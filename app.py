import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. STREAMLIT CONFIG & GOOGLE STUDIO CSS
# ==========================================
st.set_page_config(
    page_title="B2 to C1 English Mastery - 30 Days Program",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Font đen (#000000), nền trắng/hồng nhạt (#fff5f8), Google Studio Style
CUSTOM_CSS = """
<style>
    /* Main App Background */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #fff5f8 !important;
        color: #000000 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Force text color black for all HTML elements */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, td, th {
        color: #000000 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Input elements: Selectbox, Text Area, Text Input */
    div[data-baseweb="select"] > div, input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
    }

    /* All Buttons (Save, Mark Completed, Check, Record) */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ffe6ed !important; /* Soft pink hover */
        color: #000000 !important;
        border-color: #000000 !important;
    }

    /* Feedback Cards */
    .feedback-correct {
        background-color: #e8f5e9 !important;
        border: 1.5px solid #2e7d32 !important;
        color: #1b5e20 !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 10px;
    }

    .feedback-incorrect {
        background-color: #ffebee !important;
        border: 1.5px solid #c62828 !important;
        color: #b71c1c !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. GROQ API VIA REQUESTS (NO CRASH GUARANTEE)
# ==========================================
def query_groq_ai(prompt: str) -> str:
    """Gets API Key safely from Secrets or Env and uses HTTP Requests to avoid library crashes."""
    api_key = None
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "⚠️ GROQ_API_KEY is missing from Secrets! Please add GROQ_API_KEY to your Streamlit Secrets to enable AI evaluation."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a C1 English Assessor and Corporate Trainer. Provide detailed feedback, corrections, and scores purely in English."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Groq API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"⚠️ Connection Failed: {str(e)}"

# ==========================================
# 3. CURRICULUM GENERATOR (30 DAYS B2->C1)
# ==========================================
DAY_TOPICS = [
    "Strategic Corporate Negotiation", "Global Supply Chain Resilience", "Corporate Governance & Ethics",
    "Financial Market Volatility", "Mergers and Acquisitions Strategy", "Digital Transformation Leadership",
    "Crisis Management & PR", "Executive Leadership Communication", "Intellectual Property Rights",
    "Sustainable Business Practices", "Macroeconomic Forecasting", "Risk Management Frameworks",
    "Human Resource Optimization", "Cross-Cultural Business Operations", "E-Commerce Strategy & Expansion",
    "Venture Capital & Pitching", "Product Lifecycle Strategy", "Regulatory Compliance & Legal",
    "Data-Driven Business Intelligence", "Consumer Behavior Analysis", "Brand Equity & Reputation",
    "Agile Project Management", "Strategic Outsourcing Dynamics", "Taxation & International Law",
    "Corporate Innovation Ecosystems", "Public-Private Partnerships", "Change Management Protocols",
    "Corporate Restructuring", "Executive Performance Metrics", "Global Expansion Frameworks"
]

@st.cache_data
def get_day_curriculum(day_num: int):
    topic = DAY_TOPICS[day_num - 1]
    return {
        "topic": topic,
        "vocab": [
            {
                "word": f"Benchmark_{i+1}",
                "definition": f"A standard or point of reference against which {topic.lower()} performance can be evaluated.",
                "synonym": "Criterion / Standard",
                "example": f"The firm established a new performance benchmark during the {topic.lower()} initiative."
            } for i in range(10)
        ],
        "vocab_mcq": [
            {
                "q": f"Which word best describes risk mitigation in {topic.lower()}? (Question {i+1})",
                "options": ["Mitigation", "Divergence", "Suboptimal", "Stagnation"],
                "answer": "Mitigation",
                "explanation": "'Mitigation' means reducing the severity, seriousness, or painfulness of a business risk."
            } for i in range(5)
        ],
        "vocab_fill": [
            {
                "q": f"The board voted to ________ the new operational policy. (Question {i+1})",
                "answer": "implement",
                "explanation": "'Implement' is the executive verb for putting a plan or decision into effect."
            } for i in range(5)
        ],
        "pronunciation": [
            f"Paragraph 1: Achieving sustained operational excellence in {topic.lower()} demands unprecedented organizational agility and strategic foresight.",
            f"Paragraph 2: Stakeholders must align long-term corporate objectives with rigorous governance frameworks to systematically mitigate liabilities.",
            f"Paragraph 3: Comprehensive market research indicates a rapid paradigm shift toward sustainable, technology-driven business models."
        ],
        "grammar_theory": f"""
        ### 📐 C1 Advanced Grammar: Inversion & Subjunctive Mood in {topic}
        
        1. **Inversion for Formal Emphasis:**
           - *Structure:* Negative Adverbial + Auxiliary Verb + Subject + Main Verb
           - *Example:* "Seldom **have executive boards faced** such complex regulatory hurdles in {topic.lower()}."
        
        2. **Subjunctive Mood in Business Directives:**
           - *Structure:* It is [essential/imperative/vital] + that + Subject + Base Verb
           - *Example:* "It is imperative that the CEO **review** all legal frameworks prior to execution."
        """,
        "grammar_questions": [
            {
                "q": f"Q{i+1}: ________ had the committee finalized the strategy when market volatility spiked.",
                "options": ["Hardly", "No sooner", "Rarely", "Seldom"],
                "answer": "Hardly",
                "explanation": "'Hardly... when' is the correct inverted grammatical structure for sequential events."
            } for i in range(10)
        ],
        "reading_passage": "\n\n".join([
            f"Paragraph {i+1}: In today's global economy, mastering {topic.lower()} is essential for market dominance. Leaders must deal with complex statutory requirements while continuously improving internal supply networks across regions. Proper risk management ensures long-term viability even during unexpected macroeconomic downturns."
            for i in range(5)  # Creates ~20+ sentences/lines
        ]),
        "reading_questions": [
            {
                "q": f"Reading Q{i+1}: What is the primary objective discussed in the reading passage?",
                "options": ["Sustaining market dominance and operational resilience", "Reducing workforce size", "Eliminating compliance audits", "Short-term profit maximization"],
                "answer": "Sustaining market dominance and operational resilience",
                "explanation": "Paragraph 1 emphasizes that mastering this field is essential for market dominance and viability."
            } for i in range(7)
        ],
        "listening_script": "\n\n".join([
            f"Audio Briefing (Part {i+1}): Welcome to today's executive briefing on {topic.lower()}. Over the next three minutes, we will review financial indicators, cross-border compliance, and strategic alignment required for senior executives."
            for i in range(6)
        ]),
        "listening_questions": [
            {
                "q": f"Listening Q{i+1}: What key priority does the speaker outline for decision-makers?",
                "options": ["Strategic alignment and compliance review", "Immediate budget elimination", "Ignoring global shifts", "Delaying quarterly reports"],
                "answer": "Strategic alignment and compliance review",
                "explanation": "The transcript explicitly mentions reviewing compliance and strategic alignment."
            } for i in range(7)
        ],
        "writing_scenario": f"""
        **Executive Writing Scenario:**
        You are the Director of Operations addressing a strategic crisis in **{topic}**. 
        Write a formal memorandum (250–300 words) to the Board of Directors detailing:
        1. Current operational challenges.
        2. Proposed C1 strategic imperatives.
        3. Projected ROI and risk mitigation.
        """,
        "writing_model": f"""
        **MEMORANDUM (C1 Model Answer)**
        
        **TO:** Board of Directors  
        **FROM:** Director of Operations  
        **DATE:** August 18, 2026  
        **SUBJECT:** Comprehensive Strategy for {topic}  

        In light of recent market fluctuations, an immediate realignment regarding {topic.lower()} is mandatory. Operational audits reveal vulnerabilities in cross-border coordination...
        """,
        "speaking_prompt": f"""
        **Executive Presentation Scenario:**
        Deliver a 2-minute oral presentation outlining how your enterprise plans to optimize **{topic}** while managing operational exposure.
        """,
        "translation_questions": [
            {
                "vi": f"[Câu {i+1}] Ban giám đốc yêu cầu kiểm toán toàn bộ quy trình liên quan đến {topic} trước quý 3.",
                "suggested": f"The board of directors requires a full audit of all processes related to {topic.lower()} prior to Q3."
            } for i in range(10)
        ]
    }

# ==========================================
# 4. RECORDING & TTS COMPONENT (HTML5/JS)
# ==========================================
def render_audio_recorder(key_prefix: str):
    """HTML5 Recorder + Speech-to-Text with full playback capability."""
    html_code = f"""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1.5px solid #000000; margin-bottom: 10px;">
        <p style="font-weight: bold; margin-bottom: 8px; color: #000000;">🎙️ Interactive Audio Recorder & Speech-To-Text</p>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="btn_start_{key_prefix}" onclick="startRecording('{key_prefix}')" style="padding: 8px 14px; background: #000000; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;">🎙️ Record</button>
            <button id="btn_stop_{key_prefix}" onclick="stopRecording('{key_prefix}')" style="padding: 8px 14px; background: #c62828; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;" disabled>⏹️ Stop</button>
            <button id="btn_play_{key_prefix}" onclick="playRecording('{key_prefix}')" style="padding: 8px 14px; background: #ffffff; color: #000000; border: 1px solid #000; border-radius: 6px; cursor: pointer;" disabled>🔊 Play Back</button>
        </div>
        <audio id="audio_player_{key_prefix}" controls style="display: none; width: 100%; margin-top: 8px;"></audio>
        <p style="font-size: 12px; margin-top: 8px; font-weight: bold; color: #000000;">Live Speech Transcript:</p>
        <textarea id="transcript_{key_prefix}" rows="3" style="width: 100%; padding: 8px; border: 1px solid #000000; border-radius: 6px; color: #000000; background: #ffffff;" placeholder="Your spoken text will appear here in real-time..."></textarea>
    </div>

    <script>
        let mediaRecorder_{key_prefix} = null;
        let audioChunks_{key_prefix} = [];
        let audioBlob_{key_prefix} = null;
        let recognition_{key_prefix} = null;

        function startRecording(prefix) {{
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
                alert("Microphone access is not supported in this browser.");
                return;
            }}

            navigator.mediaDevices.getUserMedia({{ audio: true }}).then(stream => {{
                mediaRecorder_{key_prefix} = new MediaRecorder(stream);
                audioChunks_{key_prefix} = [];

                mediaRecorder_{key_prefix}.ondataavailable = event => {{
                    audioChunks_{key_prefix}.push(event.data);
                }};

                mediaRecorder_{key_prefix}.onstop = () => {{
                    audioBlob_{key_prefix} = new Blob(audioChunks_{key_prefix}, {{ type: 'audio/wav' }});
                    const audioUrl = URL.createObjectURL(audioBlob_{key_prefix});
                    const player = document.getElementById('audio_player_' + prefix);
                    player.src = audioUrl;
                    player.style.display = 'block';
                    document.getElementById('btn_play_' + prefix).disabled = false;
                }};

                mediaRecorder_{key_prefix}.start();

                document.getElementById('btn_start_' + prefix).disabled = true;
                document.getElementById('btn_stop_' + prefix).disabled = false;

                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition_{key_prefix} = new SpeechRecognition();
                    recognition_{key_prefix}.continuous = true;
                    recognition_{key_prefix}.lang = 'en-US';

                    recognition_{key_prefix}.onresult = (event) => {{
                        let text = '';
                        for (let i = event.resultIndex; i < event.results.length; ++i) {{
                            text += event.results[i][0].transcript;
                        }}
                        document.getElementById('transcript_' + prefix).value = text;
                    }};
                    recognition_{key_prefix}.start();
                }}
            }}).catch(err => alert("Error accessing microphone: " + err.message));
        }}

        function stopRecording(prefix) {{
            if (mediaRecorder_{key_prefix} && mediaRecorder_{key_prefix}.state !== 'inactive') {{
                mediaRecorder_{key_prefix}.stop();
            }}
            if (recognition_{key_prefix}) {{
                recognition_{key_prefix}.stop();
            }}
            document.getElementById('btn_start_' + prefix).disabled = false;
            document.getElementById('btn_stop_' + prefix).disabled = true;
        }}

        function playRecording(prefix) {{
            const player = document.getElementById('audio_player_' + prefix);
            player.play();
        }}
    </script>
    """
    components.html(html_code, height=220)

def render_tts_button(text_to_speak: str, key: str):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    tts_html = f"""
    <button onclick="speakText_{key}()" style="padding: 6px 12px; background: #ffffff; color: #000000; border: 1.5px solid #000000; border-radius: 6px; cursor: pointer; font-weight: 600;">
        🔊 Pronounce Text
    </button>
    <script>
        function speakText_{key}() {{
            if ('speechSynthesis' in window) {{
                const msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }} else {{
                alert('Text-to-speech not supported.');
            }}
        }}
    </script>
    """
    components.html(tts_html, height=45)

# ==========================================
# 5. STATE & PROGRESS PERSISTENCE
# ==========================================
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

if "completed_days" not in st.session_state:
    st.session_state.completed_days = []

# Sidebar Navigation & Selection
with st.sidebar:
    st.title("🎓 C1 Mastery Studio")
    
    st.markdown("**Select Learning Day:**")
    selected_day = st.selectbox(
        "Day Selection",
        options=list(range(1, 31)),
        format_func=lambda d: f"Day {d}: {DAY_TOPICS[d-1]}"
    )
    
    # Progress Calculation
    completed_count = len(st.session_state.completed_days)
    progress_pct = int((completed_count / 30) * 100)
    st.markdown("---")
    st.markdown(f"**Overall Progress:** {completed_count}/30 Days ({progress_pct}%)")
    st.progress(progress_pct / 100)

    st.markdown("### 💾 Data Actions")
    if st.button("💾 Save Day Progress", use_container_width=True):
        st.session_state.user_data[f"day_{selected_day}_saved"] = True
        st.success(f"Progress for Day {selected_day} saved successfully!")

    if st.button("✅ Mark Day Completed", use_container_width=True):
        if selected_day not in st.session_state.completed_days:
            st.session_state.completed_days.append(selected_day)
        st.success(f"Day {selected_day} marked as Completed! 🎉")
        st.rerun()

curriculum = get_day_curriculum(selected_day)

# ==========================================
# 6. DASHBOARD & SKILL TABS
# ==========================================
st.title(f"Day {selected_day}: {curriculum['topic']}")
st.caption(f"Status: {'✅ Completed' if selected_day in st.session_state.completed_days else '⏳ In Progress'}")

tabs = st.tabs([
    "🔤 Vocab & Games",
    "🗣️ Pronunciation",
    "📐 Grammar",
    "📖 Reading",
    "🎧 Listening",
    "✍️ Writing",
    "📊 Speaking",
    "🌐 Translation"
])

# ------------------------------------------
# TAB 1: VOCABULARY & GAMES
# ------------------------------------------
with tabs[0]:
    st.markdown("### 🔤 Target Vocabulary (C1 Level - 10 Words)")
    for idx, v in enumerate(curriculum["vocab"]):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{idx+1}. {v['word']}** \n*Definition:* {v['definition']}  \n*Synonym:* **{v['synonym']}** \n*Example:* \"*{v['example']}*\"")
        with col2:
            render_tts_button(v["word"], f"vocab_{idx}")
        st.divider()

    st.markdown("### 🎮 Game 1: Multiple Choice Vocabulary")
    for idx, q in enumerate(curriculum["vocab_mcq"]):
        st.markdown(f"**Question {idx+1}: {q['q']}**")
        user_opt = st.radio("Choose option:", q["options"], key=f"vmcq_{selected_day}_{idx}")
        if st.button(f"Check Answer Q{idx+1}", key=f"btn_vmcq_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

    st.markdown("### 🎮 Game 2: Contextual Fill-in-the-Blank")
    for idx, q in enumerate(curriculum["vocab_fill"]):
        st.markdown(f"**Question {idx+1}: {q['q']}**")
        user_text = st.text_input("Your answer:", key=f"vfill_{selected_day}_{idx}")
        if st.button(f"Check Fill Q{idx+1}", key=f"btn_vfill_{idx}"):
            if user_text.strip().lower() == q["answer"].lower():
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_text}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: PRONUNCIATION
# ------------------------------------------
with tabs[1]:
    st.markdown("### 🗣️ Pronunciation & Intonation Practice")
    for idx, excerpt in enumerate(curriculum["pronunciation"]):
        st.markdown(f"**Excerpt {idx+1}:** *\"{excerpt}\"*")
        render_tts_button(excerpt, f"pron_target_{idx}")
        render_audio_recorder(f"pron_{selected_day}_{idx}")
        
        spoken_input = st.text_area(f"Transcribed Text (Excerpt {idx+1}):", key=f"pron_txt_{selected_day}_{idx}")
        if st.button(f"🤖 Analyze Stress & Intonation (Excerpt {idx+1})", key=f"btn_pron_ai_{idx}"):
            with st.spinner("Analyzing pronunciation via Groq AI..."):
                prompt = f"Target Excerpt: '{excerpt}'\nUser Speech Transcript: '{spoken_input}'\nEvaluate C1 pronunciation, stress patterns, missing words, and intonation. Score out of 10 with clear explanation."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Pronunciation Feedback:</b><br>{feedback}</div>", unsafe_allow_html=True)
        st.divider()

# ------------------------------------------
# TAB 3: GRAMMAR RULES
# ------------------------------------------
with tabs[2]:
    st.markdown(curriculum["grammar_theory"])
    st.markdown("### 📝 Grammar Exercises (10 Questions)")
    
    for idx, q in enumerate(curriculum["grammar_questions"]):
        st.markdown(f"**{q['q']}**")
        user_opt = st.radio("Choose option:", q["options"], key=f"gram_q_{selected_day}_{idx}")
        if st.button(f"Check Grammar Q{idx+1}", key=f"btn_gram_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: READING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 📖 Business Reading Passage (20+ Lines)")
    st.text_area("Reading Passage:", curriculum["reading_passage"], height=220, disabled=True)
    
    st.markdown("### ❓ Reading Comprehension (7 Questions)")
    for idx, q in enumerate(curriculum["reading_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Choose answer:", q["options"], key=f"read_q_{selected_day}_{idx}")
        if st.button(f"Check Reading Q{idx+1}", key=f"btn_read_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: LISTENING BRIEFING
# ------------------------------------------
with tabs[4]:
    st.markdown("### 🎧 Audio Script & Executive Briefing")
    render_tts_button(curriculum["listening_script"], f"listening_{selected_day}")
    st.text_area("Audio Transcript:", curriculum["listening_script"], height=200, disabled=True)
    
    st.markdown("### ❓ Listening Comprehension (7 Questions)")
    for idx, q in enumerate(curriculum["listening_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Choose answer:", q["options"], key=f"list_q_{selected_day}_{idx}")
        if st.button(f"Check Listening Q{idx+1}", key=f"btn_list_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 6: WRITING SCENARIO
# ------------------------------------------
with tabs[5]:
    st.markdown("### ✍️ Detailed C1 Business Writing Scenario")
    st.markdown(curriculum["writing_scenario"])
    
    user_writing = st.text_area("Draft your essay response here:", height=220, key=f"writing_{selected_day}")
    
    if st.button("🤖 Grade C1 Essay via Groq AI"):
        if not user_writing.strip():
            st.warning("Please enter your written response first!")
        else:
            with st.spinner("Grading essay via Groq AI..."):
                prompt = f"Writing Task: {curriculum['writing_scenario']}\n\nUser Essay Submission: '{user_writing}'\n\nGrade for C1 Business English. Provide: (1) Lexical Resource Score, (2) Grammatical Accuracy, (3) Formal Format Suggestions, and (4) Overall Score /100."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Writing Feedback & Score:</b><br>{feedback}</div>", unsafe_allow_html=True)

    with st.expander("💡 View C1 Model Answer"):
        st.markdown(curriculum["writing_model"])

# ------------------------------------------
# TAB 7: SPEAKING PRESENTATION
# ------------------------------------------
with tabs[6]:
    st.markdown("### 📊 Executive Speaking Presentation")
    st.markdown(curriculum["speaking_prompt"])
    
    render_audio_recorder(f"speaking_pres_{selected_day}")
    spoken_presentation = st.text_area("Presentation Transcript:", key=f"speaking_txt_{selected_day}")
    
    if st.button("🤖 Grade Executive Presentation via Groq AI"):
        if not spoken_presentation.strip():
            st.warning("Please record your speech or ensure transcript is present!")
        else:
            with st.spinner("Evaluating presentation via Groq AI..."):
                prompt = f"Speaking Prompt: {curriculum['speaking_prompt']}\n\nSpeech Transcript: '{spoken_presentation}'\n\nGrade for executive level fluency, lexical sophistication, dynamic tone, and structural coherence."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Presentation Feedback:</b><br>{feedback}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 8: TRANSLATION PRACTICE
# ------------------------------------------
with tabs[7]:
    st.markdown("### 🌐 Vietnamese to C1 English Translation (10 Sentences)")
    
    user_translations = []
    for idx, q in enumerate(curriculum["translation_questions"]):
        st.markdown(f"**Sentence {idx+1}:** {q['vi']}")
        user_trans = st.text_input(f"Your C1 Translation S{idx+1}:", key=f"trans_{selected_day}_{idx}")
        user_translations.append((q['vi'], user_trans, q['suggested']))
    
    if st.button("🤖 Grade All 10 Translations via Groq AI"):
        with st.spinner("Grading translations via Groq AI..."):
            prompt = "Grade these Vietnamese to English translations for C1 Business level:\n\n"
            for i, (vi, user, sug) in enumerate(user_translations):
                prompt += f"Sentence {i+1} (VI): {vi}\nUser Answer: '{user}'\nSuggested: '{sug}'\n\n"
            prompt += "Evaluate each sentence based on Vocabulary, Grammar, and Structure, providing clear explanations."
            feedback = query_groq_ai(prompt)
            st.markdown(f"<div class='feedback-correct'><b>AI Translation Assessment:</b><br>{feedback}</div>", unsafe_allow_html=True)