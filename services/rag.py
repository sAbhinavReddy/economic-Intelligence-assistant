import os
from pathlib import Path
from typing import List, Tuple
import re
import chromadb
from sentence_transformers import SentenceTransformer
from services.utils import safe_load_json


class RAGService:
    def __init__(self, db_path='./vector_db', collection_name='india_economic_news'):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.embedder = None
        
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        except Exception:
            self.client = None
            self.collection = None

    def is_available(self) -> bool:
        """Check if the vector database is available."""
        return self.collection is not None and self.embedder is not None

    def is_collection_empty(self) -> bool:
        """Check if the vector collection is empty."""
        if not self.is_available():
            return True
        try:
            return self.collection.count() == 0
        except Exception:
            return True

    def get_collection_size(self) -> int:
        """Get the size of the vector collection."""
        if not self.is_available():
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0

    def build_collection(self):
        """Build or rebuild the vector collection from analyzed news."""
        documents = safe_load_json('data/analyzed_news.json')
        if not documents:
            return {'success': False, 'message': 'No analyzed news available to index. Refresh news first.'}
        
        if not self.is_available():
            return {'success': False, 'message': 'Vector database is not available. Check your setup.'}

        try:
            # Clear existing collection
            self.collection.delete(where={})
        except Exception:
            pass

        ids = []
        texts = []
        metadatas = []

        for index, article in enumerate(documents):
            # Build a rich searchable document that includes all analysis fields
            doc_text = ' '.join([
                article.get('title', ''),
                article.get('description', ''),
                article.get('what_happened', ''),
                article.get('why_it_happened', ''),
                article.get('possible_impact', ''),
                article.get('category', ''),
            ])
            
            ids.append(article.get('url', f'article-{index}'))
            texts.append(doc_text)
            # Store ALL structured fields as metadata for retrieval
            metadatas.append({
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'category': article.get('category', ''),
                'published_date': article.get('published_date', ''),
                'url': article.get('url', ''),
                'what_happened': article.get('what_happened', ''),
                'why_it_happened': article.get('why_it_happened', ''),
                'possible_impact': article.get('possible_impact', ''),
                'sentiment': article.get('sentiment', 'Neutral'),
                'description': article.get('description', ''),
            })

        if ids:
            try:
                embeddings = self.embedder.encode(texts, convert_to_numpy=True)
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=texts
                )
                return {'success': True, 'message': f'Indexed {len(ids)} articles successfully.'}
            except Exception as e:
                return {'success': False, 'message': f'Failed to build index: {str(e)}'}

        return {'success': False, 'message': 'No articles found to index.'}

    def query(self, question: str, top_k: int = 5) -> Tuple[List[dict], str]:
        """Query the vector database for relevant articles.
        
        Returns:
            Tuple of (list of articles with full metadata, error message or empty string)
        """
        if not self.is_available():
            return [], 'Vector database is not available.'
        
        if self.is_collection_empty():
            return [], 'No news indexed yet. Refresh news first.'
        
        try:
            result = self.collection.query(
                query_texts=[question],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            documents = result.get('documents', [[]])[0]
            metadatas = result.get('metadatas', [[]])[0]

            # Extract simple keywords from the question (lowercased words, drop short/common words)
            stopwords = {
                'the', 'and', 'for', 'with', 'that', 'this', 'from', 'what', 'when', 'where',
                'which', 'your', 'about', 'have', 'has', 'are', 'is', 'in', 'on', 'to', 'of',
                'a', 'an', 'by', 'as', 'it', 'be', 'or'
            }
            question_tokens = [t for t in re.findall(r"\w+", question.lower()) if len(t) > 2 and t not in stopwords]

            # Build rich article objects with ALL analysis fields from metadata
            articles = []
            for doc, meta in zip(documents, metadatas):
                doc_text = (doc or '').lower()
                matched = []
                matched_snippet = ''
                for tok in question_tokens:
                    if tok in doc_text and tok not in matched:
                        matched.append(tok)
                        # capture a small snippet around the first match
                        idx = doc_text.find(tok)
                        start = max(0, idx - 60)
                        end = min(len(doc_text), idx + 60)
                        matched_snippet = (doc or '')[start:end].strip()

                articles.append({
                    'title': meta.get('title', 'Untitled'),
                    'source': meta.get('source', 'Unknown'),
                    'category': meta.get('category', 'Unknown'),
                    'published_date': meta.get('published_date', ''),
                    'url': meta.get('url', ''),
                    'what_happened': meta.get('what_happened', ''),
                    'why_it_happened': meta.get('why_it_happened', ''),
                    'possible_impact': meta.get('possible_impact', ''),
                    'sentiment': meta.get('sentiment', 'Neutral'),
                    'description': meta.get('description', ''),
                    'matched_keywords': matched,
                    'matched_snippet': matched_snippet,
                })

            return articles, ''
        except Exception as error:
            print(f'RAG query error: {error}')
            return [], 'Unable to search the news database. Please try again.'