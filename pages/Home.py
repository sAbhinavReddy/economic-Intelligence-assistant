import streamlit as st
from services.utils import safe_load_json, get_last_updated, get_trending_topics, translate_text, translate_articles_list
from services.openrouter_summary_generator import OpenRouterSummaryGenerator
from collections import Counter


def render_home():
    lang = st.session_state.get('language', 'English')
    
    texts = {
        "English": {
            "title": "# 🇮🇳 India Economic Intelligence Platform",
            "subtitle": "Your AI-powered guide to understanding India's economy — explained in simple language.",
            "no_news": "📭 No news available yet.",
            "no_news_info": "Click **Refresh News and Analysis** in the sidebar to collect and analyze the latest Indian economic news.",
            "summary_title": "⏱️ Today's Economy In 30 Seconds",
            "retry": "🔄 Retry",
            "generating": "Generating AI summary...",
            "api_key_err": "• Please enter your API Key in the sidebar to generate the Cloud AI summary.",
            "rag_disabled": "• Daily AI Summary is disabled in Pure RAG mode. Select 'Local AI' or 'Cloud AI' in the sidebar to enable.",
            "summary_err": "• Unable to generate summary at this time. (Error: {err})",
            "stats_articles": "📰 Articles Processed",
            "stats_sources": "📡 Sources Used",
            "stats_cats": "📂 Categories",
            "stats_updated": "🕐 Last Updated",
            "trending": "🔥 Trending Topics",
            "major_events": "📌 Latest Major Events",
            "news_by_cat": "📂 News by Category",
            "showing_cat": "📰 **Showing Latest News in {cat}**",
            "recent_headlines": "📋 Recent Headlines",
            "show_all": "Show all headlines",
            "footer": "🇮🇳 India Economic Intelligence Platform — Making Indian economic news understandable for everyone."
        },
        "Hindi": {
            "title": "# 🇮🇳 भारत आर्थिक खुफिया मंच",
            "subtitle": "भारत की अर्थव्यवस्था को समझने के लिए आपका AI-संचालित मार्गदर्शक — सरल भाषा में समझाया गया।",
            "no_news": "📭 अभी तक कोई समाचार उपलब्ध नहीं है।",
            "no_news_info": "नवीनतम भारतीय आर्थिक समाचार एकत्र करने और विश्लेषण करने के लिए साइडबार में **समाचार और विश्लेषण रीफ्रेश करें** पर क्लिक करें।",
            "summary_title": "⏱️ 30 सेकंड में आज की अर्थव्यवस्था",
            "retry": "🔄 पुनः प्रयास करें",
            "generating": "AI सारांश उत्पन्न किया जा रहा है...",
            "api_key_err": "• क्लाउड AI सारांश उत्पन्न करने के लिए कृपया साइडबार में अपनी API कुंजी दर्ज करें।",
            "rag_disabled": "• प्योर RAG मोड में दैनिक AI सारांश अक्षम है। सक्षम करने के लिए साइडबार में 'Local AI' या 'Cloud AI' चुनें।",
            "summary_err": "• इस समय सारांश उत्पन्न करने में असमर्थ। (त्रुटि: {err})",
            "stats_articles": "📰 संसाधित लेख",
            "stats_sources": "📡 प्रयुक्त स्रोत",
            "stats_cats": "📂 श्रेणियाँ",
            "stats_updated": "🕐 अंतिम अद्यतन",
            "trending": "🔥 ट्रेंडिंग टॉपिक्स",
            "major_events": "📌 नवीनतम प्रमुख घटनाएँ",
            "news_by_cat": "📂 श्रेणी के अनुसार समाचार",
            "showing_cat": "📰 **{cat} में नवीनतम समाचार दिखा रहा है**",
            "recent_headlines": "📋 हाल की सुर्खियाँ",
            "show_all": "सभी सुर्खियाँ दिखाएं",
            "footer": "🇮🇳 भारत आर्थिक खुफिया मंच — भारतीय आर्थिक समाचारों को सभी के लिए समझने योग्य बनाना।"
        },
        "Telugu": {
            "title": "# 🇮🇳 భారత ఆర్థిక ఇంటెలిజెన్స్ ప్లాట్‌ఫారమ్",
            "subtitle": "భారతదేశ ఆర్థిక వ్యవస్థను అర్థం చేసుకోవడానికి మీ AI-శక్తితో కూడిన గైడ్ — సరళమైన భాషలో వివరించబడింది.",
            "no_news": "📭 ఇంకా ఎలాంటి వార్తలు అందుబాటులో లేవు.",
            "no_news_info": "తాజా భారతీయ ఆర్థిక వార్తలను సేకరించడానికి మరియు విశ్లేషించడానికి సైడ్‌బార్‌లో **వార్తలు మరియు విశ్లేషణను రిఫ్రెష్ చేయండి** క్లిక్ చేయండి.",
            "summary_title": "⏱️ 30 సెకన్లలో నేటి ఆర్థిక వ్యవస్థ",
            "retry": "🔄 మళ్లీ ప్రయత్నించండి",
            "generating": "AI సారాంశం రూపొందించబడుతోంది...",
            "api_key_err": "• క్లౌడ్ AI సారాంశాన్ని రూపొందించడానికి దయచేసి సైడ్‌బార్‌లో మీ API కీని నమోదు చేయండి.",
            "rag_disabled": "• ప్యూర్ RAG మోడ్‌లో రోజువారీ AI సారాంశం నిలిపివేయబడింది. ప్రారంభించడానికి సైడ్‌బార్‌లో 'Local AI' లేదా 'Cloud AI'ని ఎంచుకోండి.",
            "summary_err": "• ఈ సమయంలో సారాంశాన్ని రూపొందించడం సాధ్యపడలేదు. (లోపం: {err})",
            "stats_articles": "📰 ప్రాసెస్ చేయబడిన కథనాలు",
            "stats_sources": "📡 ఉపయోగించిన మూలాలు",
            "stats_cats": "📂 వర్గాలు",
            "stats_updated": "🕐 చివరిగా నవీకరించబడినది",
            "trending": "🔥 ట్రెండింగ్ అంశాలు",
            "major_events": "📌 తాజా ప్రధాన సంఘటనలు",
            "news_by_cat": "📂 వర్గం వారీగా వార్తలు",
            "showing_cat": "📰 **{cat}లో తాజా వార్తలను చూపుతోంది**",
            "recent_headlines": "📋 ఇటీవలి ముఖ్యాంశాలు",
            "show_all": "అన్ని ముఖ్యాంశాలను చూపించు",
            "footer": "🇮🇳 భారత ఆర్థిక ఇంటెలిజెన్స్ ప్లాట్‌ఫారమ్ — భారతీయ ఆర్థిక వార్తలను ప్రతి ఒక్కరికీ అర్థమయ్యేలా చేయడం."
        }
    }
    t = texts.get(lang, texts["English"])

    st.markdown(t["title"])
    st.markdown(t["subtitle"])
    
    analyzed_news = safe_load_json('data/analyzed_news.json')
    raw_news = safe_load_json('data/raw_news.json')
    
    if not analyzed_news:
        st.warning(t["no_news"])
        st.info(t["no_news_info"])
        return
    
    # --- Today's Economy In 30 Seconds ---
    with st.container():
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.subheader(t["summary_title"])
        with col2:
            if st.button(t["retry"], help="Retry generating the AI summary"):
                st.session_state.pop('daily_summary', None)
                st.rerun()
                
        if 'daily_summary' not in st.session_state:
            with st.spinner(t["generating"]):
                try:
                    ai_mode = st.session_state.get('ai_mode', 'Pure RAG (No AI)')
                    if ai_mode == 'Cloud AI (BYOK)':
                        import os
                        if not os.environ.get('OPENROUTER_API_KEY'):
                            st.session_state.daily_summary = t["api_key_err"]
                        else:
                            summary_generator = OpenRouterSummaryGenerator()
                            st.session_state.daily_summary = summary_generator.generate_daily_summary(analyzed_news[:30], language=lang)
                    elif ai_mode == 'Local AI (Ollama)':
                        from services.ollama_assistant import OllamaAssistant
                        assistant = OllamaAssistant(model=st.session_state.get('ollama_model', 'qwen2.5:0.5b'))
                        st.session_state.daily_summary = assistant.generate_daily_summary(analyzed_news[:10], language=lang)
                    else:
                        st.session_state.daily_summary = t["rag_disabled"]
                except Exception as e:
                    st.session_state.daily_summary = t["summary_err"].format(err=str(e))
        
        st.info(st.session_state.daily_summary)
    
    st.markdown("---")
    
    # --- Stats Row ---
    col1, col2, col3, col4 = st.columns(4)
    
    sources = set(a.get('source', 'Unknown') for a in analyzed_news)
    categories = set(a.get('category', 'Other') for a in analyzed_news)
    
    with col1:
        st.metric(t["stats_articles"], len(analyzed_news))
    with col2:
        st.metric(t["stats_sources"], len(sources))
    with col3:
        st.metric(t["stats_cats"], len(categories))
    with col4:
        last_updated = get_last_updated()
        st.metric(t["stats_updated"], last_updated)
    
    st.markdown("---")
    
    # --- Trending Topics ---
    trending = get_trending_topics(analyzed_news, top_n=8)
    if trending:
        if lang != 'English':
            trending = [translate_text(t, lang) for t in trending]
        st.subheader(t["trending"])
        cols = st.columns(4)
        for i, topic in enumerate(trending):
            with cols[i % 4]:
                st.markdown(f"<div style='background:#1e1e1e; padding:8px 12px; border-radius:8px; text-align:center; margin:4px 0; font-size:14px;'>{topic}</div>", unsafe_allow_html=True)
        st.markdown("")
    
    st.markdown("---")
    
    # --- Latest Major Events ---
    st.subheader(t["major_events"])
    
    recent = sorted(
        analyzed_news,
        key=lambda x: x.get('published_date', ''),
        reverse=True
    )[:6]
    
    recent = translate_articles_list(recent, lang)
    
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
    st.subheader(t["news_by_cat"])
    
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
            cat_display = translate_text(cat, lang) if lang != 'English' else cat
            if st.button(f"{icon} {cat_display} ({count})", key=f"home_cat_btn_{cat}", use_container_width=True):
                # Toggle category display
                if st.session_state.selected_home_category == cat:
                    st.session_state.selected_home_category = None
                else:
                    st.session_state.selected_home_category = cat
                    
    if st.session_state.selected_home_category:
        selected_cat = st.session_state.selected_home_category
        st.info(t["showing_cat"].format(cat=translate_text(selected_cat, lang)))
        
        cat_news = [a for a in analyzed_news if a.get('category', 'Other') == selected_cat]
        cat_news_display = sorted(cat_news, key=lambda x: x.get('published_date', ''), reverse=True)[:10]
        cat_news_display = translate_articles_list(cat_news_display, lang)
        for article in cat_news_display:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown')
            date = article.get('published_date', '')
            st.markdown(f"- [{title}]({url}) — *{source}*, {date}")
    
    st.markdown("---")
    
    # --- Recent Headlines ---
    st.subheader(t["recent_headlines"])
    
    with st.expander(t["show_all"], expanded=False):
        headlines_display = sorted(analyzed_news, key=lambda x: x.get('published_date', ''), reverse=True)[:20]
        headlines_display = translate_articles_list(headlines_display, lang)
        for article in headlines_display:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown')
            date = article.get('published_date', '')
            st.markdown(f"- [{title}]({url}) — *{source}*, {date}")
    
    st.markdown("---")
    st.caption(t["footer"])