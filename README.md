# Economic Intelligence Platform (India)

This project is a Streamlit application that collects, analyzes, and visualizes Indian economic news. It includes AI-assisted analysis using Gemini and a RAG-based search assistant for exploring economic trends.

## Key Features

- 🇮🇳 Collects India-focused economic news from multiple sources (NewsAPI, Google News, Moneycontrol, RBI)
- 🤖 Uses Gemini LLM for intelligent analysis with automatic rule-based fallback
- 📊 Analyzes articles into: What Happened, Why It Happened, Possible Impact
- 📈 Simplified 9-category system: Economy, Banking & Finance, Jobs & Employment, Government Policies, Business & Companies, Technology & Startups, Global Events, Markets, Other
- 🔍 RAG-powered chat assistant powered by Gemini for answering questions about Indian economic news
- � Stores raw articles and analyzed news with sentiment analysis
- 📊 Interactive Streamlit UI with Home, Analysis, Dashboard, and Assistant pages
- ⚡ ChromaDB with Sentence Transformers for fast semantic search

## Getting Started

### 1. Create the virtual environment

```bash
python -m venv venv
```

### 2. Activate the environment

Windows:

```powershell
venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your API keys:

```env
NEWS_API_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 5. Run the application

```bash
streamlit run app.py
```

## Usage

- **Home**: View latest news with analysis, filter by category
- **Analysis**: Filter articles by category, source, or sentiment; search and inspect details
- **Dashboard**: Explore interactive visualizations of news trends and sentiment
- **Assistant**: Ask questions about Indian economic news; get answers powered by OpenRouter

## Project Structure

```
economic-intelligence-platform/
├── app.py                          # Main Streamlit app
├── pages/
│   ├── Home.py                     # News overview with article cards
│   ├── Analysis.py                 # Searchable article analysis
│   ├── Dashboard.py                # Interactive visualizations
│   └── Assistant.py                # RAG-based Q&A assistant
├── services/
│   ├── news_collector.py           # Fetches from multiple news sources
│   ├── analyzer.py                 # Gemini-powered analysis engine
│   ├── openrouter_chat_assistant.py  # OpenRouter RAG assistant
│   ├── openrouter_summary_generator.py # OpenRouter summary generator
│   ├── rag.py                      # ChromaDB RAG implementation
│   └── utils.py                    # Common utilities
├── data/
│   ├── raw_news.json               # Collected articles
│   └── analyzed_news.json          # Analyzed articles with insights
├── vector_db/                      # ChromaDB embeddings
├── specs/                          # Architecture and design docs
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .env                            # API keys (gitignored)
```

### Repository Health Files

These files help keep the project maintainable, secure, and contributor-friendly. Add any that apply to your project:

- `.gitignore` — Prevents secrets/build artifacts from being committed
- `.editorconfig` — Enforces consistent code style across editors
- `CHANGELOG.md` — Documents release history
- `SECURITY.md` — Responsible disclosure policy
- `CODE_OF_CONDUCT.md` — Community standards
- `.env.example` — Shows required env vars without exposing values
- `Dockerfile` — Containerization readiness
- `.dockerignore` — Keeps Docker images lean and safe

## News Analysis Fields

Each analyzed article contains:
- **title**: Article headline
- **source**: News source
- **published_date**: Publication date
- **category**: One of 9 categories
- **what_happened**: Simple explanation of the event
- **why_it_happened**: Context and reasons
- **possible_impact**: Implications for people and businesses
- **sentiment**: Positive, Negative, or Neutral

## Key Technologies

- **Framework**: Streamlit (web UI)
- **LLMs**: Gemini (for data analysis) and OpenRouter (for chat and summaries)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB (PersistentClient)
- **Data Format**: JSON
- **Visualization**: Plotly

## News Sources

- **NewsAPI**: India business news
- **Google News**: India economy RSS feed
- **Moneycontrol**: Indian business RSS
- **RBI**: Reserve Bank press releases

## Error Handling

- No Python tracebacks are shown to users
- Friendly error messages guide users to refresh or rebuild indexes
- Automatic fallback to rule-based analysis if Gemini is unavailable

## Troubleshooting

- **Missing news data**: Click **Refresh News and Analysis** in the sidebar
- **Vector DB issues**: Click **Rebuild Index** on the Assistant page
- **No RAG results**: Vector database may be empty; run Refresh News first
- **API connection errors**: Check internet connection and API key validity

## Notes

- The application uses Gemini for AI analysis by default; other providers can be added.
- Sentiment analysis is: Positive, Negative, or Neutral
- Articles are automatically deduplicated by URL and title
- ChromaDB stores embeddings locally in ./vector_db
