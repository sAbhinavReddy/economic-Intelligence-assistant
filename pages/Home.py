import streamlit as st
from services.utils import safe_load_json, get_last_updated, get_trending_topics
from services.gemini_assistant import GeminiAssistant
from collections import Counter


def render_home():
    st.markdown("# 🇮🇳 India Economic Intelligence Platform")
    st.markdown("Your AI-powered guide to understanding India's economy — explained in simple language.")
    
    analyzed_news = safe_load_json('data/analyzed_news.json')
    raw_news = safe_load_json('data/raw_news.json')
    
    if not analyzed_news:
        st.warning("📭 No news available yet.")
        st.info("Click **Refresh News and Analysis** in the sidebar to collect and analyze the latest Indian economic news.")
        return
    
    # --- Today's Economy In 30 Seconds ---
    with st.container():
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            lang = st.session_state.get('language', 'English')
            summary_titles = {
                'English': "⏱️ Today's Economy In 30 Seconds",
                'Hindi': "⏱️ 30 सेकंड में आज की अर्थव्यवस्था",
                'Telugu': "⏱️ 30 సెకన్లలో నేటి ఆర్థిక వ్యవస్థ"
            }
            st.subheader(summary_titles.get(lang, summary_titles['English']))
        with col2:
            if st.button("🔄 Retry", help="Retry generating the AI summary"):
                st.session_state.pop('daily_summary', None)
                st.rerun()
                
        if 'daily_summary' not in st.session_state:
            with st.spinner("Generating AI summary..."):
                try:
                    assistant = GeminiAssistant()
                    summary = assistant.generate_daily_summary(analyzed_news[:30], language=lang)
                    st.session_state.daily_summary = summary
                except Exception as e:
                    st.session_state.daily_summary = f"• Unable to generate summary at this time. (Error: {str(e)})"
        
        st.info(st.session_state.daily_summary)
    
    st.markdown("---")
    
    # --- Stats Row ---
    col1, col2, col3, col4 = st.columns(4)
    
    sources = set(a.get('source', 'Unknown') for a in analyzed_news)
    categories = set(a.get('category', 'Other') for a in analyzed_news)
    
    with col1:
        st.metric("📰 Articles Processed", len(analyzed_news))
    with col2:
        st.metric("📡 Sources Used", len(sources))
    with col3:
        st.metric("📂 Categories", len(categories))
    with col4:
        last_updated = get_last_updated()
        st.metric("🕐 Last Updated", last_updated)
    
    st.markdown("---")
    
    # --- Trending Topics ---
    trending = get_trending_topics(analyzed_news, top_n=8)
    if trending:
        st.subheader("🔥 Trending Topics")
        cols = st.columns(4)
        for i, topic in enumerate(trending):
            with cols[i % 4]:
                st.markdown(f"<div style='background:#1e1e1e; padding:8px 12px; border-radius:8px; text-align:center; margin:4px 0; font-size:14px;'>{topic}</div>", unsafe_allow_html=True)
        st.markdown("")
    
    st.markdown("---")
    
    # --- Latest Major Events ---
    st.subheader("📌 Latest Major Events")
    
    recent = sorted(
        analyzed_news,
        key=lambda x: x.get('published_date', ''),
        reverse=True
    )[:6]
    
    cols = st.columns(2)
    for i, article in enumerate(recent):
        with cols[i % 2]:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            category = article.get('category', 'Other')
            source = article.get('source', 'Unknown')
            sentiment = article.get('sentiment', 'Neutral')
            
            sentiment_icon = {'Positive': '📈', 'Negative': '📉', 'Neutral': '📊'}.get(sentiment, '📊')
            
            st.markdown(f"""
            <div style='border:1px solid #333; border-radius:12px; padding:16px; margin:8px 0; background:#1a1a2e;'>
                <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div>
                        <a href="{url}" target="_blank" style='text-decoration:none; color:#4da6ff; font-weight:600; font-size:16px;'>{title[:80]}{'...' if len(title) > 80 else ''}</a>
                        <div style='margin-top:8px; font-size:13px; color:#aaa;'>
                            <span>🏢 {source}</span> | <span>📂 {category}</span> | <span>{sentiment_icon} {sentiment}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Category Distribution Cards ---
    st.subheader("📂 News by Category")
    
    category_counts = Counter(a.get('category', 'Other') for a in analyzed_news)
    cat_cols = st.columns(3)
    
    category_icons = {
        'Economy': '💹', 'Banking & Finance': '🏦', 'Jobs & Employment': '💼',
        'Government Policies': '🏛️', 'Business & Companies': '🏢', 'Technology & Startups': '💻',
        'Markets': '📊', 'Global Events': '🌍', 'Other': '📋'
    }
    
    if 'selected_home_category' not in st.session_state:
        st.session_state.selected_home_category = None

    for i, (cat, count) in enumerate(category_counts.most_common(9)):
        with cat_cols[i % 3]:
            icon = category_icons.get(cat, '📋')
            if st.button(f"{icon} {cat} ({count})", key=f"home_cat_btn_{cat}", use_container_width=True):
                # Toggle category display
                if st.session_state.selected_home_category == cat:
                    st.session_state.selected_home_category = None
                else:
                    st.session_state.selected_home_category = cat
                    
    if st.session_state.selected_home_category:
        selected_cat = st.session_state.selected_home_category
        st.info(f"📰 **Showing Latest News in {selected_cat}**")
        
        cat_news = [a for a in analyzed_news if a.get('category', 'Other') == selected_cat]
        for article in sorted(cat_news, key=lambda x: x.get('published_date', ''), reverse=True)[:10]:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown')
            date = article.get('published_date', '')
            st.markdown(f"- [{title}]({url}) — *{source}*, {date}")
    
    st.markdown("---")
    
    # --- Recent Headlines ---
    st.subheader("📋 Recent Headlines")
    
    with st.expander("Show all headlines", expanded=False):
        for article in sorted(analyzed_news, key=lambda x: x.get('published_date', ''), reverse=True)[:20]:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown')
            date = article.get('published_date', '')
            st.markdown(f"- [{title}]({url}) — *{source}*, {date}")
    
    st.markdown("---")
    st.caption("🇮🇳 India Economic Intelligence Platform — Making Indian economic news understandable for everyone.")