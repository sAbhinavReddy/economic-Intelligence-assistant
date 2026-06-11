import streamlit as st
from services.rag import RAGService
from services.ollama_assistant import OllamaAssistant


def init_session_state():
    """Initialize session state variables for conversation memory."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'rag_service' not in st.session_state:
        st.session_state.rag_service = RAGService()


def render_assistant():
    init_session_state()
    
    st.title('🤖 Ask About India\'s Economy')
    st.markdown('Get simple, accurate answers about Indian economic news — ask anything!')
    
    # --- Suggested Prompts ---
    st.subheader("💡 Try asking these questions")
    
    example_questions = [
        "Why is inflation rising?",
        "What did RBI announce recently?",
        "What happened in the economy today?",
        "How do fuel prices affect consumers?",
        "What's new in India's banking sector?",
        "How are jobs and employment changing?",
    ]
    
    cols = st.columns(2)
    clicked_question = None
    for i, question in enumerate(example_questions):
        with cols[i % 2]:
            if st.button(f"❓ {question}", key=f"prompt_{i}", use_container_width=True):
                clicked_question = question
    
    st.markdown("---")
    
    # --- Check if vector DB is initialized ---
    rag = st.session_state.rag_service
    
    if rag.is_collection_empty():
        st.warning('📭 No news has been indexed yet.')
        st.markdown("""
        To start using the assistant:
        1. Click **Refresh News and Analysis** in the sidebar
        2. Wait for news collection and analysis to complete
        3. Come back here and ask your questions
        """)
        return
    
    collection_size = rag.get_collection_size()
    st.caption(f'📚 Based on {collection_size} analyzed news articles')
    
    st.markdown('---')
    
    # --- Question input ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        default_question = clicked_question if clicked_question else ''
        question = st.text_input(
            'Your question:',
            placeholder='e.g., What are the latest developments in India\'s banking sector?',
            value=default_question,
            key='assistant_question'
        )
    
    with col2:
        ask_button = st.button('🔍 Ask', use_container_width=True)
    
    should_process = (ask_button or clicked_question is not None) and len(question.strip()) > 0
    
    st.markdown('---')
    
    # --- Display chat history ---
    if st.session_state.chat_history:
        st.subheader('💬 Conversation')
        for q, a in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant"):
                st.markdown(a)
    
    # --- Process question ---
    if should_process:
        results = []
        with st.spinner('🔍 Searching relevant articles...'):
            results, error = rag.query(question, top_k=5)
        
        if error:
            st.warning(f"📭 {error}")
            st.info("Try refreshing the news database first using the sidebar button.")
            return
        
        if not results:
            st.warning('No relevant articles found. Try a different question.')
            return
        
        # Generate answer using Local AI
        with st.spinner('🤖 Generating answer with Local AI...'):
            try:
                assistant = OllamaAssistant(model="qwen2.5:0.5b")
                answer = assistant.generate_answer(question, results)
                
                # Store in chat history
                st.session_state.chat_history.append((question, answer))
                
                # Display the new answer
                with st.chat_message("user"):
                    st.write(question)
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                # Show source articles in expander
                with st.expander('📄 View Source Articles', expanded=False):
                    for i, article in enumerate(results, 1):
                        st.markdown(f"**{i}. {article.get('title', 'Untitled')}**")
                        st.caption(
                            f"Source: {article.get('source', 'Unknown')} | "
                            f"Category: {article.get('category', 'Unknown')} | "
                            f"Date: {article.get('published_date', 'Unknown')}"
                        )
                        what_happened = article.get('what_happened', '')
                        if what_happened:
                            st.write(what_happened[:200] + ('...' if len(what_happened) > 200 else ''))
                        st.markdown('---')
                
                # Show citation info
                st.caption('✓ Answer generated locally using Qwen 2.5, based on analyzed Indian economic news articles.')
            
            except Exception as e:
                error_msg = str(e)
                st.error(f'Local AI service encountered an error: {error_msg}')
                st.info('Ensure Ollama is running in your terminal via `ollama run qwen2.5:0.5b`.')
    
    st.markdown('---')
    
    # --- Clear history button ---
    if st.session_state.chat_history:
        if st.button('🗑️ Clear Conversation', use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # --- Vector DB Management ---
    st.subheader('⚙️ Knowledge Base')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('🔄 Rebuild Knowledge Base', use_container_width=True):
            with st.spinner('Building index from latest analyzed news...'):
                result = rag.build_collection()
                if result.get('success'):
                    st.success(f"✅ {result['message']}")
                    st.info('Try asking a question now.')
                else:
                    st.warning(result.get('message', 'Unable to rebuild knowledge base.'))
    
    with col2:
        if st.button('📊 Show Stats', use_container_width=True):
            stats = {
                'Indexed Articles': rag.get_collection_size(),
                'Database Location': './vector_db',
                'Status': 'Ready' if not rag.is_collection_empty() else 'Empty'
            }
            for key, value in stats.items():
                st.write(f"**{key}:** {value}")