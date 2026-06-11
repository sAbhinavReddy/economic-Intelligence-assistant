import streamlit as st
from services.utils import safe_load_json


def render_analysis():
    st.title('🔍 News Analysis')
    st.markdown('Search and explore Indian economic news articles with AI-powered analysis.')
    
    analyzed_news = safe_load_json('data/analyzed_news.json')
    
    if not analyzed_news:
        st.warning('📭 No analyzed news found.')
        st.info('Click **Refresh News and Analysis** in the sidebar to collect and analyze the latest news.')
        return
    
    # Get unique categories and sources
    categories = sorted({article.get('category', 'Other') for article in analyzed_news})
    sources = sorted({article.get('source', 'Unknown') for article in analyzed_news})
    
    # Filters
    st.subheader('🔎 Filter Articles')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_category = st.multiselect(
            'Category:',
            ['All'] + categories,
            default=['All'],
            key='analysis_category'
        )
    
    with col2:
        selected_source = st.multiselect(
            'Source:',
            ['All'] + sources,
            default=['All'],
            key='analysis_source'
        )
    
    with col3:
        sentiment_options = ['All'] + ['Positive', 'Neutral', 'Negative']
        selected_sentiment = st.multiselect(
            'Sentiment:',
            sentiment_options,
            default=['All'],
            key='analysis_sentiment'
        )
    
    # Search text
    search_text = st.text_input(
        '🔍 Search in headlines or analysis:',
        placeholder='e.g., inflation, RBI, jobs...',
        key='analysis_search'
    )
    
    st.markdown('---')
    
    # Apply filters
    filtered = analyzed_news
    
    if 'All' not in selected_category:
        filtered = [a for a in filtered if a.get('category') in selected_category]
    
    if 'All' not in selected_source:
        filtered = [a for a in filtered if a.get('source') in selected_source]
    
    if 'All' not in selected_sentiment:
        filtered = [a for a in filtered if a.get('sentiment') in selected_sentiment]
    
    if search_text:
        search_lower = search_text.lower()
        filtered = [
            a for a in filtered
            if search_lower in a.get('title', '').lower()
            or search_lower in a.get('what_happened', '').lower()
            or search_lower in a.get('possible_impact', '').lower()
        ]
    
    # Sort by date (newest first)
    filtered = sorted(filtered, key=lambda x: x.get('published_date', ''), reverse=True)
    
    st.write(f'Found **{len(filtered)}** matching articles')
    
    if not filtered:
        st.info('No articles match your filters. Try adjusting your selection.')
        return
    
    # Display articles as cards
    for idx, article in enumerate(filtered):
        with st.container():
            with st.expander(f"📰 {article.get('title', 'Untitled')}", expanded=False):
                
                # Metadata row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"🏢 **Source:** {article.get('source', 'Unknown')}")
                with col2:
                    st.caption(f"📂 **Category:** {article.get('category', 'Unknown')}")
                with col3:
                    st.caption(f"📅 **Date:** {article.get('published_date', 'Unknown')}")
                with col4:
                    st.caption(f"💭 **Sentiment:** {article.get('sentiment', 'Neutral')}")
                
                st.markdown('---')
                
                # Analysis sections
                col1, col2 = st.columns(2)
                
                with col1:
                    what = article.get('what_happened', '')
                    if what:
                        st.markdown('**🔹 What Happened**')
                        st.write(what)
                
                with col2:
                    why = article.get('why_it_happened', '')
                    if why:
                        st.markdown('**🔹 Why It Happened**')
                        st.write(why)
                
                # Impact
                impact = article.get('possible_impact', '')
                if impact:
                    st.markdown('**🔹 Possible Impact**')
                    st.write(impact)
                
                # Link to original
                st.markdown('---')
                url = article.get('url', '#')
                st.markdown(f'[🔗 Read original article]({url})')