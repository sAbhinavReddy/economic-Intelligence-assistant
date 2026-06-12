import streamlit as st
import plotly.express as px
import pandas as pd
from services.utils import safe_load_json, translate_text
from datetime import datetime
from collections import Counter


def render_dashboard():
    lang = st.session_state.get('language', 'English')
    
    texts = {
        "English": {
            "title": "📊 Easy Economic Overview",
            "subtitle": "A simple, visual summary of how the Indian economy is doing based on the latest news.",
            "no_news": "📭 No analyzed news data found.",
            "no_news_info": "Click **Refresh News and Analysis** in the sidebar to collect and analyze news.",
            "total": "📰 Total Articles Read",
            "positive": "📈 Positive News",
            "negative": "📉 Negative News",
            "topics": "📂 Topics in the News",
            "outlook": "💭 Overall Outlook",
            "sectors": "📊 Are different sectors doing well or badly?",
            "headlines": "📌 Recent Headlines at a Glance",
            "sector_label": "Sector",
            "count_label": "Number of Articles",
            "col_headline": "Headline",
            "col_category": "Category",
            "col_outlook": "Outlook",
            "untitled": "Untitled"
        },
        "Hindi": {
            "title": "📊 आसान आर्थिक अवलोकन",
            "subtitle": "नवीनतम समाचारों के आधार पर भारतीय अर्थव्यवस्था कैसा प्रदर्शन कर रही है, इसका एक सरल, दृश्य सारांश।",
            "no_news": "📭 कोई विश्लेषित समाचार डेटा नहीं मिला।",
            "no_news_info": "समाचार एकत्र करने और विश्लेषण करने के लिए साइडबार में **समाचार और विश्लेषण रीफ्रेश करें** पर क्लिक करें।",
            "total": "📰 पढ़े गए कुल लेख",
            "positive": "📈 सकारात्मक समाचार",
            "negative": "📉 नकारात्मक समाचार",
            "topics": "📂 समाचार में विषय",
            "outlook": "💭 समग्र दृष्टिकोण",
            "sectors": "📊 क्या विभिन्न क्षेत्र अच्छा या बुरा प्रदर्शन कर रहे हैं?",
            "headlines": "📌 हाल की सुर्खियाँ एक नज़र में",
            "sector_label": "क्षेत्र",
            "count_label": "लेखों की संख्या",
            "col_headline": "सुर्खी",
            "col_category": "श्रेणी",
            "col_outlook": "दृष्टिकोण",
            "untitled": "अनाम"
        },
        "Telugu": {
            "title": "📊 సులభమైన ఆర్థిక అవలోకనం",
            "subtitle": "తాజా వార్తల ఆధారంగా భారత ఆర్థిక వ్యవస్థ ఎలా ఉందో సరళమైన, దృశ్య సారాంశం.",
            "no_news": "📭 విశ్లేషించబడిన వార్తల డేటా ఏదీ కనుగొనబడలేదు.",
            "no_news_info": "వార్తలను సేకరించడానికి మరియు విశ్లేషించడానికి సైడ్‌బార్‌లో **వార్తలు మరియు విశ్లేషణను రిఫ్రెష్ చేయండి** క్లిక్ చేయండి.",
            "total": "📰 చదివిన మొత్తం కథనాలు",
            "positive": "📈 సానుకూల వార్తలు",
            "negative": "📉 ప్రతికూల వార్తలు",
            "topics": "📂 వార్తలలోని అంశాలు",
            "outlook": "💭 మొత్తం దృక్పథం",
            "sectors": "📊 వివిధ విభాగాలు బాగా పనిచేస్తున్నాయా లేదా చెడుగా పనిచేస్తున్నాయా?",
            "headlines": "📌 ఇటీవలి ముఖ్యాంశాలు ఒక చూపులో",
            "sector_label": "రంగం",
            "count_label": "కథనాల సంఖ్య",
            "col_headline": "ముఖ్యాంశం",
            "col_category": "వర్గం",
            "col_outlook": "దృక్పథం",
            "untitled": "శీర్షిక లేదు"
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
    
    # --- Overview Metrics ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(t["total"], len(analyzed_news))
    
    with col2:
        positive = len([a for a in analyzed_news if a.get('sentiment') == 'Positive'])
        st.metric(t["positive"], positive)
    
    with col3:
        negative = len([a for a in analyzed_news if a.get('sentiment') == 'Negative'])
        st.metric(t["negative"], negative)
    
    st.markdown('---')
    
    def t_label(x):
        return translate_text(x, lang) if lang != 'English' else x
    
    # --- Side-by-Side Donut Charts ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t["topics"])
        category_counts = Counter(a.get('category', 'Other') for a in analyzed_news)
        category_df = pd.DataFrame([{'Category': t_label(cat), 'Count': count} for cat, count in category_counts.most_common()])
        if not category_df.empty:
            fig1 = px.pie(category_df, values='Count', names='Category', hole=0.4)
            fig1.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        st.subheader(t["outlook"])
        sentiment_counts = Counter(a.get('sentiment', 'Neutral') for a in analyzed_news)
        sentiment_df = pd.DataFrame([{'Sentiment': t_label(sent), 'Count': count} for sent, count in sentiment_counts.items()])
        if not sentiment_df.empty:
            fig2 = px.pie(sentiment_df, values='Count', names='Sentiment', hole=0.4, 
                          color='Sentiment', color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#3498db', 'Negative': '#e74c3c'})
            fig2.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown('---')
    
    # --- Outlook by Sector ---
    st.subheader(t["sectors"])
    category_sentiment = [{'Category': t_label(a.get('category', 'Other')), 'Sentiment': t_label(a.get('sentiment', 'Neutral'))} for a in analyzed_news]
    if category_sentiment:
        cat_sent_df = pd.DataFrame(category_sentiment)
        fig3 = px.histogram(
            cat_sent_df, x='Category', color='Sentiment',
            color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#3498db', 'Negative': '#e74c3c'},
            barmode='group',
            labels={'Category': t["sector_label"], 'count': t["count_label"]}
        )
        fig3.update_layout(height=400, xaxis_title="", yaxis_title=t["count_label"])
        st.plotly_chart(fig3, use_container_width=True)
        
    st.markdown('---')
    
    # --- Recent Headlines ---
    st.subheader(t["headlines"])
    
    recent = sorted(
        analyzed_news,
        key=lambda x: x.get('published_date', ''),
        reverse=True
    )[:10]
    
    event_data = []
    for article in recent:
        title = article.get('title', t["untitled"])
        if lang != 'English':
            title = translate_text(title, lang)
        event_data.append({
            t["col_headline"]: title[:80] + '...' if len(title) > 80 else title,
            t["col_category"]: t_label(article.get('category', 'Other')),
            t["col_outlook"]: t_label(article.get('sentiment', 'Neutral'))
        })
    
    if event_data:
        event_df = pd.DataFrame(event_data)
        st.dataframe(event_df, use_container_width=True, hide_index=True)