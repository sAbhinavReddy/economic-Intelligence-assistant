import streamlit as st
import threading

# Try importing add_script_run_ctx to avoid missing context warnings in threads
try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx
except ImportError:
    add_script_run_ctx = None

from services.news_collector import NewsCollector
from services.analyzer import NewsAnalyzer
from services.rag import RAGService
from services.utils import save_last_updated, safe_load_json
import time
from pages.Home import render_home
from pages.Analysis import render_analysis
from pages.Dashboard import render_dashboard
from pages.Assistant import render_assistant

st.set_page_config(
    page_title='India Economic Intelligence Platform',
    page_icon='🇮🇳',
    layout='wide'
)

# --- BACKGROUND TASK SETUP ---
if 'bg_status' not in st.session_state:
    st.session_state.bg_status = {
        'running': False,
        'complete': False,
        'message': ''
    }

# --- AUTO FETCH ON FIRST LOAD ---
if 'first_load_checked' not in st.session_state:
    st.session_state.first_load_checked = True
    if not safe_load_json('data/analyzed_news.json') and not st.session_state.bg_status['running']:
        st.session_state.bg_status['message'] = 'Initial setup: Fetching news...'
        thread = threading.Thread(target=background_refresh_task, args=(st.session_state.bg_status,))
        if add_script_run_ctx:
            add_script_run_ctx(thread)
        thread.start()
        st.rerun()

def background_refresh_task(status_dict):
    status_dict['running'] = True
    status_dict['complete'] = False
    try:
        status_dict['message'] = '📡 Fetching News...'
        collector = NewsCollector()
        raw_articles = collector.collect_all()
        
        status_dict['message'] = '🔍 Analyzing Articles...'
        analyzer = NewsAnalyzer()
        analyzer.analyze_articles(raw_articles)
        
        status_dict['message'] = '🗄️ Updating Knowledge Base...'
        rag = RAGService()
        rag.build_collection()
        
        save_last_updated()
        
        status_dict['message'] = '✅ Background update complete!'
        status_dict['complete'] = True
    except Exception as e:
        status_dict['message'] = f'❌ Error: {str(e)}'
        status_dict['complete'] = True
    finally:
        status_dict['running'] = False

# --- LANGUAGE SELECTOR ---
if 'language' not in st.session_state:
    st.session_state.language = 'English'

st.sidebar.title('🌐 Language / भाषा / భాష')
selected_lang = st.sidebar.selectbox(
    'Choose Language',
    ['English', 'Hindi', 'Telugu'],
    index=['English', 'Hindi', 'Telugu'].index(st.session_state.language),
    label_visibility="collapsed"
)
if selected_lang != st.session_state.language:
    st.session_state.language = selected_lang
    st.session_state.pop('daily_summary', None)  # Force AI summary to regenerate
    st.rerun()

nav_translations = {
    'Home': {'Hindi': 'मुख्य पृष्ठ', 'Telugu': 'హోమ్', 'English': 'Home'},
    'News Analysis': {'Hindi': 'समाचार विश्लेषण', 'Telugu': 'వార్తల విశ్లేషణ', 'English': 'News Analysis'},
    'Economic Insights': {'Hindi': 'आर्थिक अंतर्दृष्टि', 'Telugu': 'ఆర్థిక అంతర్దృష్టులు', 'English': 'Economic Insights'},
    'Assistant': {'Hindi': 'सहायक', 'Telugu': 'సహాయకుడు', 'English': 'Assistant'},
    'Navigation': {'Hindi': 'नेविगेशन', 'Telugu': 'నావిగేషన్', 'English': 'Navigation'},
    'Refresh News': {'Hindi': '🔄 समाचार रीफ्रेश करें', 'Telugu': '🔄 వార్తలను రిఫ్రెష్ చేయండి', 'English': '🔄 Refresh News'},
    'Estimated Time': {'Hindi': '⏱️ अनुमानित समय: ~1-2 मिनट', 'Telugu': '⏱️ అంచనా సమయం: ~1-2 నిమిషాలు', 'English': '⏱️ Estimated time: ~1-2 mins'}
}

st.sidebar.title('🇮🇳 India Economic Intelligence')
page = st.sidebar.radio(
    nav_translations['Navigation'].get(st.session_state.language, 'Navigation'),
    ['Home', 'News Analysis', 'Economic Insights', 'Assistant'],
    format_func=lambda x: nav_translations[x].get(st.session_state.language, x)
)

st.sidebar.markdown('---')
with st.sidebar:
    bg_status = st.session_state.bg_status
    
    if bg_status['running']:
        st.info(f"🔄 **Working in background...**\n\n{bg_status['message']}")
        st.caption("Auto-updating status...")
        time.sleep(2)
        st.rerun()
            
    elif bg_status['complete']:
        if "Error" in bg_status['message']:
            st.error(bg_status['message'])
            btn_label = "Dismiss"
        else:
            st.success(bg_status['message'])
            btn_label = "Apply Updates Now"
            
        if st.button(btn_label, type="primary", use_container_width=True):
            bg_status['complete'] = False
            bg_status['message'] = ''
            st.session_state.pop('daily_summary', None)
            st.rerun()
            
    else:
        st.caption(nav_translations['Estimated Time'].get(st.session_state.language, '⏱️ Estimated time: ~1-2 mins'))
        if st.button(nav_translations['Refresh News'].get(st.session_state.language, '🔄 Refresh News'), use_container_width=True):
            thread = threading.Thread(target=background_refresh_task, args=(bg_status,))
            if add_script_run_ctx:
                add_script_run_ctx(thread)
            thread.start()
            st.rerun()

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