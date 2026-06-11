import streamlit as st
from services.news_collector import NewsCollector
from services.analyzer import NewsAnalyzer
from services.rag import RAGService
from services.utils import save_last_updated
from pages.Home import render_home
from pages.Analysis import render_analysis
from pages.Dashboard import render_dashboard
from pages.Assistant import render_assistant

st.set_page_config(
    page_title='India Economic Intelligence Platform',
    page_icon='🇮🇳',
    layout='wide'
)

st.sidebar.title('🇮🇳 India Economic Intelligence')
page = st.sidebar.radio(
    'Navigation',
    ['Home', 'News Analysis', 'Economic Insights', 'Assistant'],
    index=0
)

st.sidebar.markdown('---')
with st.sidebar:
    if st.button('🔄 Refresh News', use_container_width=True):
        with st.status('Updating news database...', expanded=True) as status:
            st.write('📡 Fetching News...')
            collector = NewsCollector()
            raw_articles = collector.collect_all()
            st.write(f'✅ Fetched {len(raw_articles)} articles')
            
            st.write('🔍 Analyzing Articles...')
            analyzer = NewsAnalyzer()
            analyzer.analyze_articles(raw_articles)
            st.write('✅ Analysis complete')
            
            st.write('🗄️ Updating Knowledge Base...')
            rag = RAGService()
            result = rag.build_collection()
            st.write(f'✅ {result.get("message", "Knowledge base updated")}')
            
            save_last_updated()
            
            status.update(
                label='✅ Complete!',
                state='complete'
            )
        
        st.success('News refreshed successfully. Navigate to other pages to see updates.')
        st.session_state.pop('daily_summary', None)

st.sidebar.markdown('---')
st.sidebar.write(
    'Making Indian economic news understandable for everyone.'
)

if page == 'Home':
    render_home()
elif page == 'News Analysis':
    render_analysis()
elif page == 'Economic Insights':
    render_dashboard()
elif page == 'Assistant':
    render_assistant()