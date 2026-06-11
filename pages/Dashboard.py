import streamlit as st
import plotly.express as px
import pandas as pd
from services.utils import safe_load_json
from datetime import datetime
from collections import Counter


def render_dashboard():
    st.title('📊 Easy Economic Overview')
    st.markdown('A simple, visual summary of how the Indian economy is doing based on the latest news.')
    
    analyzed_news = safe_load_json('data/analyzed_news.json')
    
    if not analyzed_news:
        st.warning('📭 No analyzed news data found.')
        st.info('Click **Refresh News and Analysis** in the sidebar to collect and analyze news.')
        return
    
    # --- Overview Metrics ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('📰 Total Articles Read', len(analyzed_news))
    
    with col2:
        positive = len([a for a in analyzed_news if a.get('sentiment') == 'Positive'])
        st.metric('📈 Positive News', positive)
    
    with col3:
        negative = len([a for a in analyzed_news if a.get('sentiment') == 'Negative'])
        st.metric('📉 Negative News', negative)
    
    st.markdown('---')
    
    # --- Side-by-Side Donut Charts ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('📂 Topics in the News')
        category_counts = Counter(a.get('category', 'Other') for a in analyzed_news)
        category_df = pd.DataFrame([{'Category': cat, 'Count': count} for cat, count in category_counts.most_common()])
        if not category_df.empty:
            fig1 = px.pie(category_df, values='Count', names='Category', hole=0.4)
            fig1.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        st.subheader('💭 Overall Outlook')
        sentiment_counts = Counter(a.get('sentiment', 'Neutral') for a in analyzed_news)
        sentiment_df = pd.DataFrame([{'Sentiment': sent, 'Count': count} for sent, count in sentiment_counts.items()])
        if not sentiment_df.empty:
            fig2 = px.pie(sentiment_df, values='Count', names='Sentiment', hole=0.4, 
                          color='Sentiment', color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#3498db', 'Negative': '#e74c3c'})
            fig2.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown('---')
    
    # --- Outlook by Sector ---
    st.subheader('📊 Are different sectors doing well or badly?')
    category_sentiment = [{'Category': a.get('category', 'Other'), 'Sentiment': a.get('sentiment', 'Neutral')} for a in analyzed_news]
    if category_sentiment:
        cat_sent_df = pd.DataFrame(category_sentiment)
        fig3 = px.histogram(
            cat_sent_df, x='Category', color='Sentiment',
            color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#3498db', 'Negative': '#e74c3c'},
            barmode='group',
            labels={'Category': 'Sector', 'count': 'Number of Articles'}
        )
        fig3.update_layout(height=400, xaxis_title="", yaxis_title="Number of Articles")
        st.plotly_chart(fig3, use_container_width=True)
        
    st.markdown('---')
    
    # --- Recent Headlines ---
    st.subheader('📌 Recent Headlines at a Glance')
    
    recent = sorted(
        analyzed_news,
        key=lambda x: x.get('published_date', ''),
        reverse=True
    )[:10]
    
    event_data = []
    for article in recent:
        title = article.get('title', 'Untitled')
        event_data.append({
            'Headline': title[:80] + '...' if len(title) > 80 else title,
            'Category': article.get('category', 'Other'),
            'Outlook': article.get('sentiment', 'Neutral')
        })
    
    if event_data:
        event_df = pd.DataFrame(event_data)
        st.dataframe(event_df, use_container_width=True, hide_index=True)