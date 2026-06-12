import streamlit as st
from services.rag import RAGService
from services.pure_rag_assistant import PureRAGAssistant


def init_session_state():
    """Initialize session state variables for conversation memory."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'rag_service' not in st.session_state:
        st.session_state.rag_service = RAGService()


def render_assistant():
    init_session_state()
    lang = st.session_state.get('language', 'English')
    
    texts = {
        "English": {
            "title": "🤖 Ask About India's Economy",
            "subtitle": "Get simple, accurate answers about Indian economic news — ask anything!",
            "suggested": "💡 Try asking these questions",
            "building": "⏳ **Note:** The knowledge base is currently being built in the background. You can ask questions once it completes!",
            "no_news": "📭 No news has been indexed yet.",
            "start": "To start using the assistant:\n1. Click **Refresh News and Analysis** in the sidebar\n2. Wait for news collection and analysis to complete\n3. Come back here and ask your questions",
            "based_on": "📚 Based on {size} analyzed news articles",
            "your_question": "Your question:",
            "placeholder": "e.g., What are the latest developments in India's banking sector?",
            "ask": "🔍 Ask",
            "conversation": "💬 Conversation",
            "searching": "🔍 Searching relevant articles...",
            "generating": "🤖 Generating answer...",
            "error_api": "Please enter your API Key in the sidebar AI Settings.",
            "caption_cloud": "✓ Answer generated using Cloud AI (BYOK).",
            "caption_local": "✓ Answer generated using Local Ollama",
            "caption_rag": "✓ Answer retrieved directly from the knowledge base (Pure RAG).",
            "view_source": "📄 View Source Articles",
            "clear": "🗑️ Clear Conversation",
            "knowledge": "⚙️ Knowledge Base",
            "rebuild": "🔄 Rebuild Knowledge Base",
            "building_index": "Building index from latest analyzed news...",
            "try_asking": "Try asking a question now.",
            "stats": "📊 Show Stats",
            "indexed": "Indexed Articles",
            "db_loc": "Database Location",
            "status": "Status",
            "ready": "Ready",
            "empty": "Empty",
            "no_articles": "No relevant articles found. Try a different question."
        },
        "Hindi": {
            "title": "🤖 भारत की अर्थव्यवस्था के बारे में पूछें",
            "subtitle": "भारतीय आर्थिक समाचारों के बारे में सरल, सटीक उत्तर प्राप्त करें — कुछ भी पूछें!",
            "suggested": "💡 ये प्रश्न पूछने का प्रयास करें",
            "building": "⏳ **नोट:** ज्ञानकोष वर्तमान में पृष्ठभूमि में बनाया जा रहा है। पूरा होने पर आप प्रश्न पूछ सकते हैं!",
            "no_news": "📭 अभी तक कोई समाचार अनुक्रमित नहीं किया गया है।",
            "start": "सहायक का उपयोग शुरू करने के लिए:\n1. साइडबार में **समाचार और विश्लेषण रीफ्रेश करें** पर क्लिक करें\n2. समाचार संग्रह और विश्लेषण पूरा होने की प्रतीक्षा करें\n3. यहां वापस आएं और अपने प्रश्न पूछें",
            "based_on": "📚 {size} विश्लेषित समाचार लेखों पर आधारित",
            "your_question": "आपका प्रश्न:",
            "placeholder": "उदा., भारत के बैंकिंग क्षेत्र में नवीनतम घटनाक्रम क्या हैं?",
            "ask": "🔍 पूछें",
            "conversation": "💬 बातचीत",
            "searching": "🔍 प्रासंगिक लेख खोजे जा रहे हैं...",
            "generating": "🤖 उत्तर उत्पन्न किया जा रहा है...",
            "error_api": "कृपया साइडबार AI सेटिंग्स में अपनी API कुंजी दर्ज करें।",
            "caption_cloud": "✓ क्लाउड एआई (BYOK) का उपयोग करके उत्पन्न उत्तर।",
            "caption_local": "✓ स्थानीय ओलामा का उपयोग करके उत्पन्न उत्तर",
            "caption_rag": "✓ सीधे ज्ञानकोष (प्योर RAG) से प्राप्त उत्तर।",
            "view_source": "📄 स्रोत लेख देखें",
            "clear": "🗑️ बातचीत साफ़ करें",
            "knowledge": "⚙️ ज्ञानकोष",
            "rebuild": "🔄 ज्ञानकोष का पुनर्निर्माण करें",
            "building_index": "नवीनतम विश्लेषित समाचारों से अनुक्रमणिका बनाई जा रही है...",
            "try_asking": "अब एक प्रश्न पूछने का प्रयास करें।",
            "stats": "📊 आँकड़े दिखाएं",
            "indexed": "अनुक्रमित लेख",
            "db_loc": "डेटाबेस स्थान",
            "status": "स्थिति",
            "ready": "तैयार",
            "empty": "खाली",
            "no_articles": "कोई प्रासंगिक लेख नहीं मिला। कोई अन्य प्रश्न आज़माएँ।"
        },
        "Telugu": {
            "title": "🤖 భారత ఆర్థిక వ్యవస్థ గురించి అడగండి",
            "subtitle": "భారతీయ ఆర్థిక వార్తల గురించి సరళమైన, ఖచ్చితమైన సమాధానాలను పొందండి — దేనినైనా అడగండి!",
            "suggested": "💡 ఈ ప్రశ్నలు అడగడానికి ప్రయత్నించండి",
            "building": "⏳ **గమనిక:** నాలెడ్జ్ బేస్ ప్రస్తుతం బ్యాక్‌గ్రౌండ్‌లో నిర్మించబడుతోంది. ఇది పూర్తయిన తర్వాత మీరు ప్రశ్నలు అడగవచ్చు!",
            "no_news": "📭 ఇంకా ఎలాంటి వార్తలు ఇండెక్స్ చేయబడలేదు.",
            "start": "సహాయకుడిని ఉపయోగించడం ప్రారంభించడానికి:\n1. సైడ్‌బార్‌లో **వార్తలు మరియు విశ్లేషణను రిఫ్రెష్ చేయండి** క్లిక్ చేయండి\n2. వార్తల సేకరణ మరియు విశ్లేషణ పూర్తయ్యే వరకు వేచి ఉండండి\n3. ఇక్కడికి తిరిగి వచ్చి మీ ప్రశ్నలను అడగండి",
            "based_on": "📚 {size} విశ్లేషించబడిన వార్తా కథనాల ఆధారంగా",
            "your_question": "మీ ప్రశ్న:",
            "placeholder": "ఉదా., భారతదేశ బ్యాంకింగ్ రంగంలో తాజా పరిణామాలు ఏమిటి?",
            "ask": "🔍 అడగండి",
            "conversation": "💬 సంభాషణ",
            "searching": "🔍 సంబంధిత కథనాల కోసం వెతుకుతోంది...",
            "generating": "🤖 సమాధానం రూపొందించబడుతోంది...",
            "error_api": "దయచేసి సైడ్‌బార్ AI సెట్టింగ్‌లలో మీ API కీని నమోదు చేయండి.",
            "caption_cloud": "✓ క్లౌడ్ AI (BYOK) ఉపయోగించి రూపొందించబడిన సమాధానం.",
            "caption_local": "✓ స్థానిక ఒలామాను ఉపయోగించి రూపొందించబడిన సమాధానం",
            "caption_rag": "✓ నాలెడ్జ్ బేస్ (ప్యూర్ RAG) నుండి నేరుగా పొందబడిన సమాధానం.",
            "view_source": "📄 మూల కథనాలను వీక్షించండి",
            "clear": "🗑️ సంభాషణను క్లియర్ చేయండి",
            "knowledge": "⚙️ నాలెడ్జ్ బేస్",
            "rebuild": "🔄 నాలెడ్జ్ బేస్‌ను పునర్నిర్మించండి",
            "building_index": "తాజా విశ్లేషించబడిన వార్తల నుండి సూచికను నిర్మిస్తోంది...",
            "try_asking": "ఇప్పుడు ఒక ప్రశ్న అడగడానికి ప్రయత్నించండి.",
            "stats": "📊 గణాంకాలను చూపించు",
            "indexed": "సూచిక చేయబడిన కథనాలు",
            "db_loc": "డేటాబేస్ స్థానం",
            "status": "స్థితి",
            "ready": "సిద్ధంగా ఉంది",
            "empty": "ఖాళీ",
            "no_articles": "సంబంధిత కథనాలు ఏవీ కనుగొనబడలేదు. వేరొక ప్రశ్నను ప్రయత్నించండి."
        }
    }
    
    t = texts.get(lang, texts["English"])
    
    st.title(t["title"])
    st.markdown(t["subtitle"])
    
    # --- Suggested Prompts ---
    st.subheader(t["suggested"])
    
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
        if st.session_state.get('bg_status', {}).get('running'):
            st.info(t["building"])
        else:
            st.warning(t["no_news"])
            st.markdown(t["start"])
        return
    
    collection_size = rag.get_collection_size()
    st.caption(t["based_on"].format(size=collection_size))
    
    st.markdown('---')
    
    # --- Question input ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        default_question = clicked_question if clicked_question else ''
        question = st.text_input(
            t["your_question"],
            placeholder=t["placeholder"],
            value=default_question,
            key='assistant_question'
        )
    
    with col2:
        ask_button = st.button(t["ask"], use_container_width=True)
    
    should_process = (ask_button or clicked_question is not None) and len(question.strip()) > 0
    
    st.markdown('---')
    
    # --- Display chat history ---
    if st.session_state.chat_history:
        st.subheader(t["conversation"])
        for q, a in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant"):
                st.markdown(a)
    
    # --- Process question ---
    if should_process:
        results = []
        with st.spinner(t["searching"]):
            results, error = rag.query(question, top_k=5)
        
        if error:
            st.warning(f"📭 {error}")
            st.info(t["start"])
            return
        
        if not results:
            st.warning(t["no_articles"])
            return
        
        # Generate answer using selected AI Mode
        with st.spinner(t["generating"]):
            try:
                ai_mode = st.session_state.get('ai_mode', 'Pure RAG (No AI)')
                
                if ai_mode == 'Cloud AI (BYOK)':
                    import os
                    from services.gemini_chat_assistant import GeminiChatAssistant
                    if not os.environ.get('GEMINI_API_KEY'):
                        st.error(t["error_api"])
                        return
                    assistant = GeminiChatAssistant()
                    answer = assistant.generate_answer(question, results, language=lang)
                    caption = t["caption_cloud"]
                elif ai_mode == 'Local AI (Ollama)':
                    from services.ollama_assistant import OllamaAssistant
                    assistant = OllamaAssistant(model=st.session_state.get('ollama_model', 'qwen2.5:0.5b'))
                    answer = assistant.generate_answer(question, results, language=lang)
                    caption = f'{t["caption_local"]} ({st.session_state.get("ollama_model", "qwen2.5:0.5b")}).'
                else:
                    from services.pure_rag_assistant import PureRAGAssistant
                    assistant = PureRAGAssistant()
                    answer = assistant.generate_answer(question, results, language=lang)
                    caption = t["caption_rag"]
                
                # Store in chat history
                st.session_state.chat_history.append((question, answer))
                
                # Display the new answer
                with st.chat_message("user"):
                    st.write(question)
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                # Show source articles in expander
                with st.expander(t["view_source"], expanded=False):
                    for i, article in enumerate(results, 1):
                        title = article.get('title', 'Untitled')
                        category = article.get('category', 'Unknown')
                        what_happened = article.get('what_happened', '')
                        
                        if lang != 'English':
                            from services.utils import translate_text
                            title = translate_text(title, lang)
                            category = translate_text(category, lang)
                            what_happened = translate_text(what_happened, lang)
                            
                        st.markdown(f"**{i}. {title}**")
                        st.caption(
                            f"Source: {article.get('source', 'Unknown')} | "
                            f"Category: {category} | "
                            f"Date: {article.get('published_date', 'Unknown')}"
                        )
                        if what_happened:
                            st.write(what_happened[:200] + ('...' if len(what_happened) > 200 else ''))
                        st.markdown('---')
                
                # Show citation info
                st.caption(caption)
            
            except Exception as e:
                st.error(f'Assistant encountered an error: {str(e)}')
    
    st.markdown('---')
    
    # --- Clear history button ---
    if st.session_state.chat_history:
        if st.button(t["clear"], use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # --- Vector DB Management ---
    st.subheader(t["knowledge"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(t["rebuild"], use_container_width=True):
            with st.spinner(t["building_index"]):
                result = rag.build_collection()
                if result.get('success'):
                    st.success(f"✅ {result['message']}")
                    st.info(t["try_asking"])
                else:
                    st.warning(result.get('message', 'Unable to rebuild knowledge base.'))
    
    with col2:
        if st.button(t["stats"], use_container_width=True):
            stats = {
                t["indexed"]: rag.get_collection_size(),
                t["db_loc"]: './vector_db',
                t["status"]: t["ready"] if not rag.is_collection_empty() else t["empty"]
            }
            for key, value in stats.items():
                st.write(f"**{key}:** {value}")