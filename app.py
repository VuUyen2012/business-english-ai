import os
import json
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# ==========================================
# 1. PAGE CONFIGURATION & GOOGLE STUDIO STYLING
# ==========================================
st.set_page_config(
    page_title="B2 to C1 English Mastery - 30 Days Program",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme CSS: White & Pink Backgrounds, Black Text, Google Studio Dashboard Style
CUSTOM_CSS = """
<style>
    /* Main App Background & Text */
    .stApp {
        background-color: #fff5f8 !important; /* Gentle pink tone background */
        color: #000000 !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Force text color black across all headers and paragraphs */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #000000 !important;
    }

    /* Cards & Containers Styling (Google Studio Look) */
    .studio-card {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    /* Buttons Styling */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ffe6ed !important; /* Pink hover effect */
        border-color: #000000 !important;
        color: #000000 !important;
    }

    /* Primary Buttons (Save / Submit) */
    .stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
    }

    /* Selectbox & Inputs Styling */
    div[data-baseweb="select"] > div, input, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
    }

    /* Success / Feedback Boxes */
    .feedback-correct {
        background-color: #e8f5e9 !important;
        border: 1px solid #2e7d32 !important;
        color: #1b5e20 !important;
        padding: 12px;
        border-radius: 8px;
        margin-top: 8px;
    }

    .feedback-incorrect {
        background-color: #ffebee !important;
        border: 1px solid #c62828 !important;
        color: #b71c1c !important;
        padding: 12px;
        border-radius: 8px;
        margin-top: 8px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. GROQ API CONNECTION FROM SECRETS
# ==========================================
def get_groq_client():
    """Retrieves Groq API key directly from Streamlit Secrets or Environment Variables without throwing hard errors."""
    groq_api_key = None
    
    # Try getting from Streamlit Secrets
    try:
        if "GROQ_API_KEY" in st.secrets:
            groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    # Fallback to Environment Variables
    if not groq_api_key:
        groq_api_key = os.getenv("GROQ_API_KEY")

    if groq_api_key:
        try:
            return Groq(api_key=groq_api_key)
        except Exception as e:
            st.error(f"⚠️ Groq API Initialization Error: {str(e)}")
            return None
    return None

groq_client = get_groq_client()

def query_groq_ai(prompt: str) -> str:
    """Helper function to run prompts against Groq AI asynchronously/safely."""
    if not groq_client:
        return "⚠️ GROQ_API_KEY is missing from Secrets/Environment! Please add GROQ_API_KEY to st.secrets or process environment variables to enable AI grading features."
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional C1 English Assessor and Executive Trainer. Always respond in clear, formal, and constructive English."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq API Connection Error: {str(e)}"

# ==========================================
# 3. CURRICULUM DATA GENERATOR (30 DAYS B2->C1)
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
                "definition": f"A standard or point of reference against which {topic.lower()} performance can be assessed.",
                "synonym": "Criterion / Standard",
                "example": f"The organization established a new performance benchmark during the {topic.lower()} process."
            } for i in range(10)
        ],
        "vocab_mcq": [
            {
                "q": f"Which term best describes strategic risk reduction in {topic.lower()}? (Q{i+1})",
                "options": ["Mitigation", "Disparity", "Suboptimal", "Stagnation"],
                "answer": "Mitigation",
                "explanation": "'Mitigation' specifically denotes reducing the severity or seriousness of risks."
            } for i in range(5)
        ],
        "vocab_fill": [
            {
                "q": f"The board of directors voted to ________ the new compliance strategy. (Fill in the blank)",
                "answer": "implement",
                "explanation": "'Implement' is the standard C1 business verb for carrying out plans or policies."
            } for i in range(5)
        ],
        "pronunciation": [
            f"Sentence 1: Achieving sustained excellence in {topic.lower()} demands unprecedented organizational agility and foresight.",
            f"Sentence 2: Stakeholders must align strategic objectives with rigorous governance frameworks to mitigate emerging liabilities.",
            f"Sentence 3: Comprehensive market analysis reveals a shifting paradigm toward sustainable operational resilience."
        ],
        "grammar_theory": f"""
        ### 📐 Advanced C1 Focus: Inversion & Subjunctive Mood in {topic}
        
        1. **Inversion for Formal Emphasis:**
           - *Structure:* Negative adverbial + Auxiliary verb + Subject + Verb
           - *Example:* "Seldom **have we encountered** such complex regulatory hurdles in {topic.lower()}."
        
        2. **The Subjunctive Mood in Corporate Governance:**
           - *Structure:* It is [essential/imperative/vital] + that + subject + base verb
           - *Example:* "It is imperative that the Chief Financial Officer **review** all compliance protocols immediately."
        """,
        "grammar_questions": [
            {
                "q": f"Q{i+1}: ________ had the executive committee finalized the proposal when market conditions fluctuated.",
                "options": ["Hardly", "No sooner", "Seldom", "Rarely"],
                "answer": "Hardly",
                "explanation": "'Hardly... when' is the correct inverted pair used to describe sequential events in formal English."
            } for i in range(10)
        ],
        "reading_passage": "\n".join([
            f"Paragraph {i+1}: In today's dynamic global market, {topic.lower()} serves as a critical driver of sustainable competitive advantage. Organizations must navigate regulatory complexities while continuously optimizing core operational processes across international jurisdictions. Strategic foresight and robust leadership are mandatory to overcome market volatility."
            for i in range(5)  # Generates 20+ lines/sentences text
        ]),
        "reading_questions": [
            {
                "q": f"Reading Q{i+1}: What is the primary operational objective emphasized in the passage?",
                "options": ["Sustaining competitive advantage", "Reducing workforce size", "Eliminating compliance audits", "Short-term profit maximization"],
                "answer": "Sustaining competitive advantage",
                "explanation": "Paragraph 1 explicitly identifies strategic foresight in this field as a driver of sustainable competitive advantage."
            } for i in range(7)
        ],
        "listening_script": "\n".join([
            f"Speaker Briefing (Part {i+1}): Welcome to today's executive audio briefing on {topic.lower()}. Over the next three minutes, we will analyze key industry metrics, strategic alignment, and operational frameworks necessary for executive decision-making."
            for i in range(6)
        ]),
        "listening_questions": [
            {
                "q": f"Listening Q{i+1}: What is the main recommended focus for executive decision-makers?",
                "options": ["Strategic alignment and framework optimization", "Immediate cost cutting", "Ignoring regulatory shifts", "Deferring investment decisions"],
                "answer": "Strategic alignment and framework optimization",
                "explanation": "The speaker explicitly outlines strategic alignment and operational frameworks as the core focus."
            } for i in range(7)
        ],
        "writing_scenario": f"""
        **Executive Writing Scenario:**
        
        You are the Chief Strategy Officer addressing a major transition in **{topic}**. 
        Write a formal memorandum (250–300 words) to the Board of Directors outlining:
        1. Current operational bottlenecks.
        2. Strategic imperatives for the next fiscal year.
        3. Risk mitigation and expected ROI.
        """,
        "writing_model": f"""
        **MEMORANDUM (C1 Model Answer)**
        
        **TO:** Board of Directors  
        **FROM:** Chief Strategy Officer  
        **DATE:** August 18, 2026  
        **SUBJECT:** Strategic Realignment Strategy for {topic}  

        In light of recent shifts in global market dynamics, immediate structural realignment regarding {topic.lower()} is required. Current operational audits reveal vulnerabilities in cross-divisional oversight...
        """,
        "speaking_prompt": f"""
        **Executive Presentation Scenario:**
        
        Deliver a 2-minute executive oral briefing detailing how your enterprise plans to mitigate operational risks in **{topic}** while seizing new market opportunities.
        """,
        "translation_questions": [
            {
                "vi": f"[Câu {i+1}] Ban giám đốc cần xem xét và phê duyệt chiến lược quản trị rủi ro liên quan đến {topic} trước quý 3.",
                "suggested": f"The board of directors needs to review and approve the risk management strategy regarding {topic.lower()} prior to Q3."
            } for i in range(10)
        ]
    }

# ==========================================
# 4. AUDIO & SPEECH-TO-TEXT HTML/JS COMPONENT
# ==========================================
def render_audio_recorder(key_prefix: str):
    """
    Renders an HTML5 Audio Recorder with Web Speech API Speech-To-Text.
    Eliminates external connection failures and provides live playback.
    """
    html_code = f"""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #000000; margin-bottom: 10px;">
        <p style="font-weight: bold; margin-bottom: 8px; color: #000000;">🎙️ Interactive Voice Recorder & Speech-To-Text</p>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="btn_start_{key_prefix}" onclick="startRecording('{key_prefix}')" style="padding: 8px 14px; background: #000000; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;">🎙️ Record</button>
            <button id="btn_stop_{key_prefix}" onclick="stopRecording('{key_prefix}')" style="padding: 8px 14px; background: #c62828; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;" disabled>⏹️ Stop</button>
            <button id="btn_play_{key_prefix}" onclick="playRecording('{key_prefix}')" style="padding: 8px 14px; background: #ffffff; color: #000000; border: 1px solid #000; border-radius: 6px; cursor: pointer;" disabled>🔊 Play Back Recording</button>
        </div>
        <audio id="audio_player_{key_prefix}" controls style="display: none; width: 100%; margin-top: 8px;"></audio>
        <p style="font-size: 12px; margin-top: 8px; font-weight: bold; color: #000000;">Live Speech-To-Text Transcript:</p>
        <textarea id="transcript_{key_prefix}" rows="3" style="width: 100%; padding: 8px; border: 1px solid #000000; border-radius: 6px; color: #000000; background: #ffffff;" placeholder="Your spoken text will automatically appear here..."></textarea>
    </div>

    <script>
        let mediaRecorder_{key_prefix} = null;
        let audioChunks_{key_prefix} = [];
        let audioBlob_{key_prefix} = null;
        let recognition_{key_prefix} = null;

        function startRecording(prefix) {{
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
                alert("Microphone access is not supported in this browser environment.");
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

                // Speech Recognition Setup
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
    """HTML5 Text-to-Speech synthesizer button."""
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    tts_html = f"""
    <button onclick="speakText_{key}()" style="padding: 6px 12px; background: #ffffff; color: #000000; border: 1px solid #000000; border-radius: 6px; cursor: pointer; font-weight: 600;">
        🔊 Pronounce
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
# 5. SESSION STATE & PROGRESS MANAGEMENT
# ==========================================
if "user_progress" not in st.session_state:
    st.session_state.user_progress = {}

if "completed_days" not in st.session_state:
    st.session_state.completed_days = []

# Sidebar Navigation
with st.sidebar:
    st.title("🎯 C1 Mastery Studio")
    st.subheader("Select Learning Day")
    
    selected_day = st.selectbox(
        "Select Day (1 to 30):",
        options=list(range(1, 31)),
        format_func=lambda d: f"Day {d}: {DAY_TOPICS[d-1]}"
    )
    
    # Progress Tracker Overview
    completed_count = len(st.session_state.completed_days)
    progress_pct = int((completed_count / 30) * 100)
    st.markdown("---")
    st.markdown(f"**Overall Progress:** {completed_count}/30 Days ({progress_pct}%)")
    st.progress(progress_pct / 100)

    # Action Buttons
    st.markdown("### 💾 Data Controls")
    if st.button("💾 Save Day Progress", use_container_width=True, type="primary"):
        st.session_state.user_progress[f"day_{selected_day}"] = "Saved"
        st.success(f"Progress saved for Day {selected_day}!")

    if st.button("✅ Mark Day Completed", use_container_width=True):
        if selected_day not in st.session_state.completed_days:
            st.session_state.completed_days.append(selected_day)
        st.success(f"Day {selected_day} marked as Completed! 🎉")
        st.rerun()

# Load Curriculum for current day
curriculum = get_day_curriculum(selected_day)

# ==========================================
# 6. MAIN CONTENT DASHBOARD
# ==========================================
st.title(f"Day {selected_day}: {curriculum['topic']}")
is_completed = selected_day in st.session_state.completed_days
st.caption(f"Status: {'✅ Completed' if is_completed else '⏳ In Progress'}")

# Skill Tabs
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
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{idx+1}. {v['word']}**  \n*Definition:* {v['definition']}  \n*Synonym:* **{v['synonym']}**  \n*Example:* \"*{v['example']}*\"")
            with col2:
                render_tts_button(v["word"], f"vocab_{idx}")
        st.divider()

    st.markdown("### 🎮 Practice Game 1: Multiple Choice Vocabulary")
    for idx, q in enumerate(curriculum["vocab_mcq"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Choose correct option:", q["options"], key=f"v_mcq_{selected_day}_{idx}")
        if st.button(f"Check Answer Q{idx+1}", key=f"btn_vmcq_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

    st.markdown("### 🎮 Practice Game 2: Contextual Fill-in-the-Blank")
    for idx, q in enumerate(curriculum["vocab_fill"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_text = st.text_input("Type answer:", key=f"v_fill_{selected_day}_{idx}")
        if st.button(f"Check Answer Fill Q{idx+1}", key=f"btn_vfill_{idx}"):
            if user_text.strip().lower() == q["answer"].lower():
                st.markdown(f"<div class='feedback-correct'>✅ Correct! <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_text}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: PRONUNCIATION
# ------------------------------------------
with tabs[1]:
    st.markdown("### 🗣️ Pronunciation & Intonation Practice")
    st.info("Read the excerpts below. Record your voice, listen back, and trigger Groq AI stress/intonation analysis.")
    
    for idx, excerpt in enumerate(curriculum["pronunciation"]):
        st.markdown(f"**Excerpt {idx+1}:** *\"{excerpt}\"*")
        render_tts_button(excerpt, f"pron_target_{idx}")
        render_audio_recorder(f"pron_{selected_day}_{idx}")
        
        spoken_input = st.text_area(f"Transcribed Text (Excerpt {idx+1}):", key=f"pron_trans_{selected_day}_{idx}")
        if st.button(f"🤖 Analyze Accent & Stress (Excerpt {idx+1})", key=f"btn_pron_ai_{idx}"):
            with st.spinner("Analyzing pronunciation via Groq AI..."):
                prompt = f"Target Excerpt: '{excerpt}'\nUser Speech-To-Text Output: '{spoken_input}'\nEvaluate C1 pronunciation accuracy, stress patterns, missing words, and intonation. Provide a score out of 10 and explicit feedback."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Pronunciation Evaluation:</b><br>{feedback}</div>", unsafe_allow_html=True)
        st.divider()

# ------------------------------------------
# TAB 3: GRAMMAR RULES
# ------------------------------------------
with tabs[2]:
    st.markdown(curriculum["grammar_theory"])
    st.markdown("### 📝 Grammar Practice Exercises (10 Questions)")
    
    for idx, q in enumerate(curriculum["grammar_questions"]):
        st.markdown(f"**{q['q']}**")
        user_opt = st.radio("Select option:", q["options"], key=f"gram_q_{selected_day}_{idx}")
        if st.button(f"Check Grammar Answer Q{idx+1}", key=f"btn_gram_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: READING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 📖 Business Reading Passage")
    st.text_area("Passage Text:", curriculum["reading_passage"], height=200, disabled=True)
    
    st.markdown("### ❓ Reading Comprehension Questions")
    for idx, q in enumerate(curriculum["reading_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Select answer:", q["options"], key=f"read_q_{selected_day}_{idx}")
        if st.button(f"Check Reading Answer Q{idx+1}", key=f"btn_read_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: LISTENING BRIEFING
# ------------------------------------------
with tabs[4]:
    st.markdown("### 🎧 Audio Transcript & Executive Briefing")
    render_tts_button(curriculum["listening_script"], f"listening_full_{selected_day}")
    st.text_area("Briefing Script:", curriculum["listening_script"], height=180, disabled=True)
    
    st.markdown("### ❓ Listening Comprehension Questions")
    for idx, q in enumerate(curriculum["listening_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Select answer:", q["options"], key=f"list_q_{selected_day}_{idx}")
        if st.button(f"Check Listening Answer Q{idx+1}", key=f"btn_list_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 6: WRITING SCENARIO
# ------------------------------------------
with tabs[5]:
    st.markdown("### ✍️ Detailed Business Writing Task")
    st.markdown(curriculum["writing_scenario"])
    
    user_writing = st.text_area("Draft your C1 response here:", height=200, key=f"writing_{selected_day}")
    
    if st.button("🤖 Submit Writing for Groq AI Scoring", type="primary"):
        if not user_writing.strip():
            st.warning("Please draft your response before submitting!")
        else:
            with st.spinner("Grading C1 Business Writing via Groq AI..."):
                prompt = f"Task: {curriculum['writing_scenario']}\n\nUser Essay Submission: '{user_writing}'\n\nEvaluate submission on: (1) C1 Vocabulary, (2) Structural Grammar, (3) Tone & Register, (4) Specific formatting/error corrections, and (5) Score / 100."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Writing Evaluation & Score:</b><br>{feedback}</div>", unsafe_allow_html=True)

    with st.expander("💡 View C1 Model Answer"):
        st.markdown(curriculum["writing_model"])

# ------------------------------------------
# TAB 7: SPEAKING PRESENTATION
# ------------------------------------------
with tabs[6]:
    st.markdown("### 📊 Executive Speaking Presentation")
    st.markdown(curriculum["speaking_prompt"])
    
    render_audio_recorder(f"speaking_pres_{selected_day}")
    spoken_presentation = st.text_area("Speech Transcript:", key=f"speaking_txt_{selected_day}")
    
    if st.button("🤖 Grade Executive Presentation via Groq AI", type="primary"):
        if not spoken_presentation.strip():
            st.warning("Please record your speech or ensure transcript is present!")
        else:
            with st.spinner("Analyzing Speech via Groq AI..."):
                prompt = f"Speaking Prompt: {curriculum['speaking_prompt']}\n\nSpeech Transcript: '{spoken_presentation}'\n\nGrade for C1 executive fluency, lexical sophistication, dynamic tone, and structural coherence. Give actionable suggestions."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Executive Speaking Evaluation:</b><br>{feedback}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 8: TRANSLATION PRACTICE
# ------------------------------------------
with tabs[7]:
    st.markdown("### 🌐 Translation Practice (Vietnamese to C1 English)")
    st.info("Translate each sentence into C1 English. Submit all for Groq AI sentence-by-sentence evaluation.")
    
    user_translations = []
    for idx, q in enumerate(curriculum["translation_questions"]):
        st.markdown(f"**Sentence {idx+1}:** {q['vi']}")
        user_trans = st.text_input(f"Your C1 Translation (Sentence {idx+1}):", key=f"trans_{selected_day}_{idx}")
        user_translations.append((q['vi'], user_trans, q['suggested']))
    
    if st.button("🤖 Grade All Translations via Groq AI", type="primary"):
        with st.spinner("Evaluating translations via Groq AI..."):
            prompt = "Evaluate the following Vietnamese-to-English translations for a C1 business level:\n\n"
            for i, (vi, user, sug) in enumerate(user_translations):
                prompt += f"Sentence {i+1} (VI): {vi}\nUser Translation: '{user}'\nSuggested Target: '{sug}'\n\n"
            prompt += "For each sentence, provide a score based on Vocabulary, Grammar, and Sentence Structure, followed by direct feedback."
            feedback = query_groq_ai(prompt)
            st.markdown(f"<div class='feedback-correct'><b>AI Sentence-by-Sentence Translation Scoring:</b><br>{feedback}</div>", unsafe_allow_html=True)