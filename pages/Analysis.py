import streamlit as st
from services.utils import safe_load_json, translate_text, translate_articles_list


def render_analysis():
    lang = st.session_state.get('language', 'English')
    
    texts = {
        "English": {
            "title": "🔍 News Analysis",
            "subtitle": "Search and explore Indian economic news articles with AI-powered analysis.",
            "no_news": "📭 No analyzed news found.",
            "no_news_info": "Click **Refresh News and Analysis** in the sidebar to collect and analyze the latest news.",
            "filter": "🔎 Filter Articles",
            "cat_label": "Category:",
            "source_label": "Source:",
            "sentiment_label": "Sentiment:",
            "all": "All",
            "search_label": "🔍 Search in headlines or analysis:",
            "search_ph": "e.g., inflation, RBI, jobs...",
            "found": "Found **{count}** matching articles",
            "no_match": "No articles match your filters. Try adjusting your selection.",
            "source": "Source",
            "category": "Category",
            "date": "Date",
            "sentiment": "Sentiment",
            "what": "🔹 What Happened",
            "why": "🔹 Why It Happened",
            "impact": "🔹 Possible Impact",
            "read_orig": "🔗 Read original article",
            "untitled": "Untitled",
            "unknown": "Unknown"
        },
        "Hindi": {
            "title": "🔍 समाचार विश्लेषण",
            "subtitle": "AI-संचालित विश्लेषण के साथ भारतीय आर्थिक समाचार लेख खोजें और एक्सप्लोर करें।",
            "no_news": "📭 कोई विश्लेषित समाचार नहीं मिला।",
            "no_news_info": "नवीनतम समाचार एकत्र करने और विश्लेषण करने के लिए साइडबार में **समाचार और विश्लेषण रीफ्रेश करें** पर क्लिक करें।",
            "filter": "🔎 लेख फ़िल्टर करें",
            "cat_label": "श्रेणी:",
            "source_label": "स्रोत:",
            "sentiment_label": "भावना:",
            "all": "सभी",
            "search_label": "🔍 सुर्खियों या विश्लेषण में खोजें:",
            "search_ph": "उदा., मुद्रास्फीति, RBI, नौकरियां...",
            "found": "**{count}** मेल खाने वाले लेख मिले",
            "no_match": "कोई भी लेख आपके फ़िल्टर से मेल नहीं खाता। अपने चयन को समायोजित करने का प्रयास करें।",
            "source": "स्रोत",
            "category": "श्रेणी",
            "date": "दिनांक",
            "sentiment": "भावना",
            "what": "🔹 क्या हुआ",
            "why": "🔹 ऐसा क्यों हुआ",
            "impact": "🔹 संभावित प्रभाव",
            "read_orig": "🔗 मूल लेख पढ़ें",
            "untitled": "अनाम",
            "unknown": "अज्ञात"
        },
        "Telugu": {
            "title": "🔍 వార్తల విశ్లేషణ",
            "subtitle": "AI-శక్తితో కూడిన విశ్లేషణతో భారతీయ ఆర్థిక వార్తా కథనాలను శోధించండి మరియు అన్వేషించండి.",
            "no_news": "📭 విశ్లేషించబడిన వార్తలు ఏవీ కనుగొనబడలేదు.",
            "no_news_info": "తాజా వార్తలను సేకరించడానికి మరియు విశ్లేషించడానికి సైడ్‌బార్‌లో **వార్తలు మరియు విశ్లేషణను రిఫ్రెష్ చేయండి** క్లిక్ చేయండి.",
            "filter": "🔎 కథనాలను ఫిల్టర్ చేయండి",
            "cat_label": "వర్గం:",
            "source_label": "మూలం:",
            "sentiment_label": "సెంటిమెంట్:",
            "all": "అన్నీ",
            "search_label": "🔍 ముఖ్యాంశాలు లేదా విశ్లేషణలో శోధించండి:",
            "search_ph": "ఉదా., ద్రవ్యోల్బణం, RBI, ఉద్యోగాలు...",
            "found": "**{count}** సరిపోలే కథనాలు కనుగొనబడ్డాయి",
            "no_match": "మీ ఫిల్టర్‌లకు ఏ కథనాలు సరిపోలలేదు. మీ ఎంపికను సర్దుబాటు చేయడానికి ప్రయత్నించండి.",
            "source": "మూలం",
            "category": "వర్గం",
            "date": "తేదీ",
            "sentiment": "సెంటిమెంట్",
            "what": "🔹 ఏమి జరిగింది",
            "why": "🔹 ఇది ఎందుకు జరిగింది",
            "impact": "🔹 సాధ్యమయ్యే ప్రభావం",
            "read_orig": "🔗 అసలు కథనాన్ని చదవండి",
            "untitled": "శీర్షిక లేదు",
            "unknown": "తెలియదు"
        }
    }
    
    t = texts.get(lang, texts["English"])

    st.title(t["title"])
    st.markdown(t["subtitle"])
    
    analyzed_news = safe_load_json('data/analyzed_news.json')
    
    if not analyzed_news:
        st.warning(t["no_news"])
        st.info(t["no_news_info"])
        return
    
    # Get unique categories and sources
    categories = sorted({article.get('category', 'Other') for article in analyzed_news})
    sources = sorted({article.get('source', 'Unknown') for article in analyzed_news})
    
    def t_label(x):
        return translate_text(x, lang) if lang != 'English' else x
    
    # Filters
    st.subheader(t["filter"])
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_category = st.multiselect(
            t["cat_label"],
            [t["all"]] + categories,
            default=[t["all"]],
            format_func=lambda x: t["all"] if x == t["all"] else t_label(x),
            key='analysis_category'
        )
    
    with col2:
        selected_source = st.multiselect(
            t["source_label"],
            [t["all"]] + sources,
            default=[t["all"]],
            format_func=lambda x: t["all"] if x == t["all"] else t_label(x),
            key='analysis_source'
        )
    
    with col3:
        sentiment_options = [t["all"]] + ['Positive', 'Neutral', 'Negative']
        selected_sentiment = st.multiselect(
            t["sentiment_label"],
            sentiment_options,
            default=[t["all"]],
            format_func=lambda x: t["all"] if x == t["all"] else t_label(x),
            key='analysis_sentiment'
        )
    
    # Search text
    search_text = st.text_input(
        t["search_label"],
        placeholder=t["search_ph"],
        key='analysis_search'
    )
    
    st.markdown('---')
    
    # Apply filters
    filtered = analyzed_news
    
    if t["all"] not in selected_category:
        filtered = [a for a in filtered if a.get('category') in selected_category]
    
    if t["all"] not in selected_source:
        filtered = [a for a in filtered if a.get('source') in selected_source]
    
    if t["all"] not in selected_sentiment:
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
    
    st.write(t["found"].format(count=len(filtered)))
    
    if not filtered:
        st.info(t["no_match"])
        return
    
    # Display articles as cards
    for idx, article in enumerate(filtered):
        with st.container():
            with st.expander(f"📰 {article.get('title', t['untitled'])}", expanded=False):
                
                # Metadata row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"🏢 **{t['source']}** {article.get('source', t['unknown'])}")
                with col2:
                    st.caption(f"📂 **{t['category']}** {article.get('category', t['unknown'])}")
                with col3:
                    st.caption(f"📅 **{t['date']}** {article.get('published_date', t['unknown'])}")
                with col4:
                    st.caption(f"💭 **{t['sentiment']}** {article.get('sentiment', 'Neutral')}")
                
                st.markdown('---')
                
                # Analysis sections
                col1, col2 = st.columns(2)
                
                with col1:
                    what = article.get('what_happened', '')
                    if what:
                        st.markdown(f"**{t['what']}**")
                        st.write(what)
                
                with col2:
                    why = article.get('why_it_happened', '')
                    if why:
                        st.markdown(f"**{t['why']}**")
                        st.write(why)
                
                # Impact
                impact = article.get('possible_impact', '')
                if impact:
                    st.markdown(f"**{t['impact']}**")
                    st.write(impact)
                
                # Link to original
                st.markdown('---')
                url = article.get('url', '#')
                st.markdown(f"[{t['read_orig']}]({url})")