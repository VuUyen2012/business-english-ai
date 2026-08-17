import streamlit as st
import requests
import json
import re
import os
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 0. PERSISTENT STORAGE (SAVE / LOAD SYSTEM)
# ==========================================
SAVE_FILE = "apex_app_save_data.json"

def load_saved_data_dict(data_dict):
    """Cập nhật dữ liệu từ dictionary vào session_state."""
    for key, value in data_dict.items():
        st.session_state[key] = value

def load_saved_data():
    """Tải dữ liệu đã lưu từ file JSON cục bộ vào session_state."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                saved_state = json.load(f)
                load_saved_data_dict(saved_state)
            return True
        except Exception as e:
            st.error(f"Error loading saved data: {e}")
            return False
    return False

def get_exportable_state():
    """Trích xuất dữ liệu cần thiết để lưu trữ."""
    data_to_save = {}
    for key, val in st.session_state.items():
        if key.startswith("FormSubmitter:") or key in ["data_loaded"]:
            continue
        if isinstance(val, (bytes, bytearray)):
            continue
        try:
            json.dumps(val)
            data_to_save[key] = val
        except (TypeError, OverflowError):
            continue
    return data_to_save

def save_data_to_file():
    """Lưu toàn bộ session_state hợp lệ vào file JSON."""
    try:
        data_to_save = get_exportable_state()
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# ==========================================
# 1. PAGE CONFIG & FULL CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Apex English - 30-Day Executive Coaching",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "data_loaded" not in st.session_state:
    load_saved_data()
    st.session_state["data_loaded"] = True

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #fff1f2 !important;
        color: #0f172a !important;
    }

    *, p, span, h1, h2, h3, h4, h5, h6, li, label, div {
        color: #0f172a !important;
    }

    div[data-testid="stJson"], 
    div[data-testid="stJson"] *, 
    pre, code, 
    [data-testid="stMarkdownContainer"] code,
    .stCodeBlock,
    [data-baseweb="tree-node"] {
        background-color: #ffe4e6 !important;
        color: #0f172a !important;
        border: 1px solid #fda4af !important;
        border-radius: 8px !important;
        font-family: 'Inter', monospace !important;
        font-weight: 600 !important;
    }

    input, textarea, select, 
    [data-baseweb="input"],
    [data-baseweb="input"] input, 
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"],
    [data-baseweb="select"] * {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1.5px solid #fda4af !important;
        border-radius: 6px !important;
        font-size: 15px !important;
    }
    
    ::placeholder {
        color: #9f1239 !important;
        opacity: 0.6 !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] {
        border-right: 2px solid #fecdd3 !important;
    }

    div[data-baseweb="tab"] div { 
        color: #881337 !important; 
        font-weight: 600 !important; 
    }
    div[data-baseweb="tab"][aria-selected="true"] div { 
        color: #e11d48 !important; 
        font-weight: 700 !important; 
        border-bottom: 3px solid #e11d48 !important;
    }

    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #fecdd3 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(225, 29, 72, 0.05);
    }
    .apex-card * { color: #0f172a !important; }
    
    .correct-card { 
        background-color: #f0fdf4 !important; 
        border-left: 5px solid #16a34a !important; 
        padding: 18px; 
        margin-top: 10px; 
        border-radius: 8px;
    }
    .correct-card * { color: #0f172a !important; }
    
    .wrong-card { 
        background-color: #fff1f2 !important; 
        border-left: 5px solid #e11d48 !important; 
        padding: 18px; 
        margin-top: 10px; 
        border-radius: 8px;
    }
    .wrong-card * { color: #0f172a !important; }

    .hint-card {
        background-color: #ffffff !important;
        border: 1.5px solid #fda4af !important;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .hint-card * { color: #0f172a !important; }

    .hero-banner {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .hero-banner h2, .hero-banner p, .hero-banner b {
        color: #ffffff !important;
    }

    .stButton>button, 
    .stButton>button *,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] > button * {
        background: linear-gradient(135deg, #e11d48 0%, #f43f5e 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(225,29,72,0.2) !important;
    }
    .stButton>button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #be123c 0%, #e11d48 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

if "error_log" not in st.session_state:
    st.session_state["error_log"] = []

# ==========================================
# 2. AUDIO PLAYER & HELPER FUNCTIONS
# ==========================================
def play_audio(text):
    safe_text = json.dumps(text)
    html_code = f"""
    <div style="margin: 5px 0;">
        <button onclick='speakText()' style="
            background-color: #e11d48;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;">
            🔊 Play Audio (Native Voice)
        </button>
    </div>
    <script>
        function speakText() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance({safe_text});
            msg.lang = 'en-US';
            msg.rate = 0.9;
            window.speechSynthesis.speak(msg);
        }}
    </script>
    """
    components.html(html_code, height=45)

def render_formatted_theory(theory_data):
    """Render lý thuyết đẹp mắt, tránh bị lồng dính raw JSON."""
    if isinstance(theory_data, str):
        st.markdown(theory_data)
    elif isinstance(theory_data, dict):
        for key, value in theory_data.items():
            title = key.replace('_', ' ').title()
            st.markdown(f"#### 📌 **{title}**")
            if isinstance(value, dict):
                for sub_k, sub_v in value.items():
                    sub_title = sub_k.replace('_', ' ').title()
                    if isinstance(sub_v, list):
                        st.markdown(f"**{sub_title}:**")
                        for item in sub_v:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{sub_title}:** {sub_v}")
            elif isinstance(value, list):
                for item in value:
                    st.markdown(f"- {item}")
            else:
                st.write(value)
            st.write("")
    else:
        st.write(str(theory_data))

def render_feedback_section(feedback_data):
    """Render phần nhận xét bài viết/nói theo chuẩn Markdown sạch."""
    if isinstance(feedback_data, dict):
        for key, val in feedback_data.items():
            header_title = key.replace('_', ' ').title()
            st.markdown(f"**• {header_title}:**")
            if isinstance(val, list):
                for item in val:
                    st.markdown(f"  - {item}")
            else:
                st.markdown(f"  {val}")
    elif isinstance(feedback_data, list):
        for item in feedback_data:
            st.markdown(f"- {item}")
    else:
        st.markdown(str(feedback_data))

# ==========================================
# 3. SIDEBAR & GROQ AI ENGINE
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 **Apex English Coach**")
    st.caption("30-DAY EXECUTIVE CURRICULUM")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    
    st.markdown("### 💾 **Save & Progress**")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save Progress", use_container_width=True):
            if save_data_to_file():
                st.toast("✅ Saved progress to disk!", icon="💾")
    with col_s2:
        if st.button("🔄 Reload Saved", use_container_width=True):
            if load_saved_data():
                st.toast("🔄 Reloaded saved data!", icon="✅")
                st.rerun()

    export_json = json.dumps(get_exportable_state(), ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Backup (.json)",
        data=export_json,
        file_name="apex_progress_backup.json",
        mime="application/json",
        use_container_width=True
    )

    uploaded_file = st.file_uploader("📤 Restore Backup (.json):", type=["json"])
    if uploaded_file is not None:
        try:
            uploaded_data = json.load(uploaded_file)
            load_saved_data_dict(uploaded_data)
            st.success("Uploaded & Restored!")
        except Exception as e:
            st.error(f"Restore failed: {e}")

    st.divider()
    app_mode = st.radio("Navigation", [
        "1. Comprehensive Diagnostic Assessment",
        "2. 30-Day Executive Curriculum",
        "3. Error Log & Remind Review"
    ])
    
    st.divider()
    current_level = st.selectbox("Current Level:", ["B2 Intermediate"])
    target_level = st.selectbox("Target Level:", ["C1 Advanced", "C2 Executive Mastery"])

SYSTEM_PROMPT = "You are an elite C-suite Executive English Coach. All teaching materials, explanations, questions, and feedback MUST be strictly in 100% ENGLISH. Outputs MUST strictly be valid JSON."

def generate_ai_response(prompt_input, seed_key=None):
    if not api_key:
        st.error("API Key missing! Please enter your Groq API Key in the sidebar.")
        return None
    
    clean_key = re.sub(r'[^\x00-\x7F]+', '', str(api_key)).strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
    
    seed_value = None
    if seed_key:
        seed_value = int(hashlib.md5(seed_key.encode('utf-8')).hexdigest(), 16) % (2**31)

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_input}
        ],
        "temperature": 0.1 if seed_key else 0.2,
        "response_format": {"type": "json_object"}
    }
    if seed_value is not None:
        payload["seed"] = seed_value

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def extract_json(raw_text):
    if not raw_text: return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', json_str)
        return json_str
    return raw_text.strip()

def get_or_generate_data(session_key, prompt_text, seed_key=None):
    if session_key not in st.session_state or not st.session_state[session_key]:
        with st.spinner("Loading executive curriculum module..."):
            raw = generate_ai_response(prompt_text, seed_key=seed_key)
            clean = extract_json(raw)
            if clean:
                try:
                    st.session_state[session_key] = json.loads(clean, strict=False)
                    save_data_to_file()
                except Exception as e:
                    st.error(f"Data Parsing Error: {e}")
    return st.session_state.get(session_key, None)

# ==========================================
# 4. EVALUATION & QUIZ SYSTEM
# ==========================================
def evaluate_answer(user_selection, raw_correct, options):
    if user_selection is None:
        return False, str(raw_correct) if raw_correct is not None else "N/A"

    u_sel_str = str(user_selection).strip().lower()
    
    if raw_correct is None or raw_correct == "None":
        if options and len(options) > 0:
            raw_correct = options[0]
        else:
            return False, "N/A"

    c_ans_str = str(raw_correct).strip().lower()

    if u_sel_str == c_ans_str:
        return True, str(user_selection)

    if options and isinstance(options, list):
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            if 1 <= idx <= len(options):
                if u_sel_str == str(options[idx - 1]).strip().lower():
                    return True, options[idx - 1]
            if 0 <= idx < len(options):
                if u_sel_str == str(options[idx]).strip().lower():
                    return True, options[idx]

        letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        if c_ans_str in letter_map and letter_map[c_ans_str] < len(options):
            if u_sel_str == str(options[letter_map[c_ans_str]]).strip().lower():
                return True, options[letter_map[c_ans_str]]

        for opt in options:
            if str(opt).strip().lower() == c_ans_str:
                if u_sel_str == str(opt).strip().lower():
                    return True, opt

    correct_display = raw_correct
    if options and isinstance(options, list):
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            if 1 <= idx <= len(options): correct_display = options[idx - 1]
            elif 0 <= idx < len(options): correct_display = options[idx]
        elif c_ans_str in {'a', 'b', 'c', 'd', 'e'}:
            correct_display = options[{'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}[c_ans_str]]

    return False, str(correct_display)

def render_quiz_system(tab_key, prompt_text, btn_label, skill_name, seed_key=None):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        get_or_generate_data(f"{tab_key}_data", prompt_text, seed_key=seed_key)

    data = st.session_state.get(f"{tab_key}_data")
    if data:
        if "lesson_theory" in data:
            st.markdown('<div class="hint-card">', unsafe_allow_html=True)
            st.markdown("### 📖 English Grammar Focus & Business Usage Rule")
            render_formatted_theory(data["lesson_theory"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        passage = data.get("passage", "")
        if passage:
            st.markdown('<div class="apex-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Case Reading / Transcript Passage")
            st.write(passage)
            if skill_name == "Listening":
                st.markdown("**🔊 Audio Briefing:**")
                play_audio(passage)
            st.markdown('</div>', unsafe_allow_html=True)

        questions = data.get("questions", [])
        if questions:
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Question {idx}: {q.get('question')}**")
                opts = q.get('options', [])
                key_input = f"q_{tab_key}_{idx}"
                
                if key_input not in st.session_state:
                    st.session_state[key_input] = opts[0] if opts else ""

                if opts and len(opts) > 0:
                    current_val = st.session_state[key_input]
                    opt_idx = opts.index(current_val) if current_val in opts else 0
                    st.radio("Select Option:", opts, index=opt_idx, key=key_input)
                else:
                    st.text_input("Your Answer:", value=st.session_state.get(key_input, ""), key=key_input)
                st.write("---")
            
            if st.button("Submit & Evaluate Answers", key=f"sub_{tab_key}", use_container_width=True):
                user_answers = {}
                for idx, q in enumerate(questions, 1):
                    q_id = str(q.get('id', idx))
                    key_input = f"q_{tab_key}_{idx}"
                    user_answers[q_id] = st.session_state.get(key_input)
                
                st.session_state[f"{tab_key}_sub"] = True
                st.session_state[f"{tab_key}_user_ans"] = user_answers
                save_data_to_file()

        if st.session_state.get(f"{tab_key}_sub", False):
            user_ans = st.session_state.get(f"{tab_key}_user_ans", {})
            score = 0
            st.markdown("### 📊 Executive Assessment Results")
            
            for idx, q in enumerate(questions, 1):
                q_id = str(q.get('id', idx))
                ans = user_ans.get(q_id)
                raw_correct = q.get('answer') or q.get('correct_answer')
                opts = q.get('options', [])
                
                is_correct, display_correct = evaluate_answer(ans, raw_correct, opts)
                
                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Selected: <b>{ans}</b></div>', unsafe_allow_html=True)
                else:
                    exp = q.get("explanation", "Review key business concepts for this section.")
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{ans if ans else "Not Selected"}</b> | Correct: <b>{display_correct}</b><br>💡 <i>Explanation: {exp}</i></div>', unsafe_allow_html=True)
                    
                    log_item = {
                        "skill": skill_name,
                        "question": q.get('question'),
                        "your_answer": ans,
                        "correct_answer": display_correct,
                        "explanation": exp
                    }
                    if log_item not in st.session_state["error_log"]:
                        st.session_state["error_log"].append(log_item)
            save_data_to_file()
            st.success(f"🏆 Overall Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 5. MAIN CURRICULUM & SKILLS MODULES
# ==========================================
if not api_key:
    st.warning("⚠️ Please input your Groq API Key in the sidebar to activate the program.")
else:
    if app_mode == "1. Comprehensive Diagnostic Assessment":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Comprehensive Diagnostic Assessment</h2>
            <p style='margin:5px 0 0 0;'>Multi-Skill Entry Evaluation: Grammar, Reading, Listening & Executive Scenario.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pdia = """Generate a FULL comprehensive entry assessment test covering 4 skills: 
        1. Grammar & Vocabulary (3 Multiple Choice Questions), 
        2. Reading Comprehension (Short passage with 3 Multiple Choice Questions), 
        3. Listening Skills (Transcript with 2 Multiple Choice Questions),
        4. Business Communication Scenario (2 Fill-in-the-blank or Choice Questions).
        Return JSON with key 'questions' containing an array of 10 objects: 'id', 'question', 'options', 'answer', 'explanation'."""
        
        render_quiz_system("diagnostic", pdia, "Start Comprehensive Assessment", "Diagnostic", seed_key="diagnostic_test_full_v2")

    elif app_mode == "2. 30-Day Executive Curriculum":
        st.markdown(f"""
        <div class="hero-banner">
            <h2 style='margin:0;'>30-Day Executive Business English Curriculum</h2>
            <p style='margin:5px 0 0 0;'>Current Level: <b>{current_level}</b> ➔ Target Level: <b>{target_level}</b></p>
        </div>
        """, unsafe_allow_html=True)

        day_selected = st.slider("Select Training Day (1 - 30):", 1, 30, 1)
        
        topics = [
            "Corporate Strategy & Vision", "Supply Chain Optimization", "M&A Negotiations", 
            "Financial Risk Management", "Executive Leadership", "Cross-Border Partnerships",
            "Crisis Communication", "Digital Transformation", "Market Entry Expansion",
            "Investor Relations", "ESG & Corporate Sustainability", "Brand Positioning",
            "Talent Acquisition & Retention", "Change Management", "Product Productization",
            "Data-Driven Decision Making", "Contractual Disputes", "C-Suite Presentation",
            "International Trade Compliance", "Customer Lifetime Value", "Public Relations Strategy",
            "Capital Raising & Pitching", "Operations Efficiency", "Agile Project Management",
            "Executive Compensation", "Corporate Restructuring", "Cybersecurity Strategy",
            "Global Macroeconomics", "Stakeholder Alignment", "B2B Enterprise Sales"
        ]
        
        grammar_topics = [
            "Present Perfect vs. Past Simple in Performance Reporting",
            "Conditionals (If / Unless / Provided that) for Strategic Risk Analysis",
            "Inversion for Executive Emphasis & Persuasive Presentations",
            "Parallel Structure & Paired Conjunctions (Neither/Nor, Either/Or) in Decision Making",
            "Passive Voice & Nominalization in Formal Business Documentation",
            "Modal Verbs of Obligation & Necessity (Must, Should, Ought to) in Compliance",
            "Subjunctive Mood & Formal Proposals (I recommend that he be...)",
            "Relative Clauses for Clear Business Context & Stakeholder Mapping",
            "Reported Speech in Corporate Communications & M&A Debriefs",
            "Gerunds vs. Infinitives after Executive Verbs (Propose, Consider, Refuse)"
        ]
        
        day_topic = topics[(day_selected - 1) % len(topics)]
        day_grammar = grammar_topics[(day_selected - 1) % len(grammar_topics)]
        
        st.markdown(f"## 📅 Day {day_selected}: **{day_topic}**")
        st.caption(f"🎯 Target Grammar Concept: **{day_grammar}**")

        tab_v, tab_p, tab_g, tab_r, tab_l, tab_w, tab_s, tab_t = st.tabs([
            "🔤 Vocabulary & Games", "🗣️ Pronunciation", "📐 Grammar Rules", 
            "📖 Reading", "🎧 Listening Briefing", "✍️ Detailed Writing Scenario", "💬 Data-Driven Speaking",
            "🌐 Translation Practice"
        ])

        # --- 1. VOCABULARY & GAMES ---
        with tab_v:
            st.markdown(f"### 🔤 10 Core Executive Vocabulary Words: {day_topic}")
            pv = f"Generate 10 C-suite Business English words for Day {day_selected} Topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with key 'words' as array of 10 objects: 'word', 'ipa', 'english_def', 'synonyms', 'example'."
            v_data_dict = get_or_generate_data(f"v_data_full_{day_selected}", pv, seed_key=f"vocab_day_{day_selected}")
            
            if v_data_dict and "words" in v_data_dict:
                words = v_data_dict["words"]
                for idx, w in enumerate(words, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4 style="color:#e11d48 !important; margin:0;">{idx}. {w.get('word')} <span style="font-size:14px; color:#9f1239 !important;">/{w.get('ipa')}/</span></h4>
                        <p style="margin:4px 0;"><b>Definition:</b> {w.get('english_def')}</p>
                        <p style="margin:4px 0;"><b>Synonyms:</b> <code style="background-color:#ffe4e6 !important; color:#0f172a !important;">{w.get('synonyms')}</code></p>
                        <p style="margin:4px 0; font-style:italic;"><b>Executive Example:</b> "{w.get('example')}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(w.get('word', ''))

            st.divider()
            st.markdown("### 🎮 Interactive Vocabulary Games")
            game_type = st.radio("Select Game Mode:", ["Game 1: Fill in Missing Letters", "Game 2: Definition Matching Quiz"], key=f"gt_{day_selected}")
            
            pgame = f"Generate 5 business vocabulary game questions for topic '{day_topic}'. ALL text MUST be in ENGLISH. For Game 1 return 'fill_words' array of objects ('word', 'hint_english'). For Game 2 return 'mcq_words' array of objects ('word', 'options', 'correct_option'). Return JSON with keys 'fill_words' and 'mcq_words'."
            g_data = get_or_generate_data(f"g_data_{day_selected}", pgame, seed_key=f"game_day_{day_selected}") or {}

            if game_type == "Game 1: Fill in Missing Letters":
                fill_list = g_data.get("fill_words", [])
                if fill_list:
                    for idx, gw in enumerate(fill_list, 1):
                        w_str = gw.get('word', '')
                        f_char = w_str[0] if w_str else 'A'
                        st.markdown(f"**Question {idx}:** English Clue: *{gw.get('hint_english')}*")
                        key_g1_in = f"g1_in_{day_selected}_{idx}"
                        if key_g1_in not in st.session_state:
                            st.session_state[key_g1_in] = ""

                        st.text_input(
                            f"Word starting with '{f_char}...':", 
                            value=st.session_state[key_g1_in], 
                            key=key_g1_in
                        )
                    
                    if st.button("Check Game 1 Answers", key=f"btn_g1_check_{day_selected}", use_container_width=True):
                        u_g1_ans = {}
                        for idx in range(1, len(fill_list) + 1):
                            key_g1_in = f"g1_in_{day_selected}_{idx}"
                            u_g1_ans[idx] = st.session_state.get(key_g1_in, "")
                        
                        st.session_state[f"g1_sub_{day_selected}"] = True
                        st.session_state[f"g1_ans_{day_selected}"] = u_g1_ans
                        save_data_to_file()

                    if st.session_state.get(f"g1_sub_{day_selected}", False):
                        g1_score = 0
                        ans_map = st.session_state.get(f"g1_ans_{day_selected}", {})
                        st.markdown("#### 📊 Game 1 Evaluation Results")
                        for idx, gw in enumerate(fill_list, 1):
                            u_val = str(ans_map.get(idx, '')).strip().lower()
                            c_val = str(gw.get('word', '')).strip().lower()
                            if u_val == c_val and u_val != "":
                                g1_score += 1
                                st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Word: <b>{gw.get("word")}</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Your answer: <b>{u_val if u_val else "None"}</b> | Correct answer: <b>{gw.get("word")}</b></div>', unsafe_allow_html=True)
                        st.info(f"🏆 Game 1 Final Score: {g1_score}/{len(fill_list)}")

            elif game_type == "Game 2: Definition Matching Quiz":
                mcq_list = g_data.get("mcq_words", [])
                if mcq_list:
                    for idx, mw in enumerate(mcq_list, 1):
                        st.markdown(f"**Question {idx}: What is the exact meaning of '{mw.get('word')}'?**")
                        key_g2_in = f"g2_in_{day_selected}_{idx}"
                        opts = mw.get('options', [])
                        if key_g2_in not in st.session_state:
                            st.session_state[key_g2_in] = opts[0] if opts else ""

                        curr_val = st.session_state[key_g2_in]
                        opt_idx = opts.index(curr_val) if curr_val in opts else 0
                        st.radio("Select Option:", opts, index=opt_idx, key=key_g2_in)
                        st.write("---")
                    
                    if st.button("Check Game 2 Answers", key=f"btn_g2_check_{day_selected}", use_container_width=True):
                        u_g2_ans = {}
                        for idx in range(1, len(mcq_list) + 1):
                            key_g2_in = f"g2_in_{day_selected}_{idx}"
                            u_g2_ans[idx] = st.session_state.get(key_g2_in)
                        
                        st.session_state[f"g2_sub_{day_selected}"] = True
                        st.session_state[f"g2_ans_{day_selected}"] = u_g2_ans
                        save_data_to_file()

                    if st.session_state.get(f"g2_sub_{day_selected}", False):
                        g2_score = 0
                        ans_map = st.session_state.get(f"g2_ans_{day_selected}", {})
                        st.markdown("#### 📊 Game 2 Evaluation Results")
                        for idx, mw in enumerate(mcq_list, 1):
                            u_v = ans_map.get(idx)
                            c_v = mw.get('correct_option')
                            is_c, disp = evaluate_answer(u_v, c_v, mw.get('options', []))
                            if is_c:
                                g2_score += 1
                                st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> 👉 <b>{u_v}</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{u_v if u_v else "None"}</b> | Correct: <b>{disp}</b></div>', unsafe_allow_html=True)
                        st.info(f"🏆 Game 2 Final Score: {g2_score}/{len(mcq_list)}")

        # --- 2. PRONUNCIATION ---
        with tab_p:
            st.markdown(f"### 🎙️ Passage Pronunciation Practice ({day_topic})")
            pp = f"Generate 5 short executive speech passages (2-3 sentences each) on Topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON object with key 'passages' containing an array of 5 strings."
            p_dict = get_or_generate_data(f"p_passages_dict_{day_selected}", pp, seed_key=f"pron_passages_{day_selected}")
            
            p_list = p_dict.get("passages", []) if p_dict else []
            for idx, text_p in enumerate(p_list, 1):
                st.markdown(f"""
                <div class="apex-card">
                    <h4>Passage {idx}:</h4>
                    <p style="font-size:16px;">{text_p}</p>
                </div>
                """, unsafe_allow_html=True)
                play_audio(text_p)

                # --- INTEGRATED PRONUNCIATION EVALUATION & CORRECTION ---
                st.markdown(f"**🗣️ Pronunciation Self-Assessment & Recording Input (Passage {idx}):**")
                user_speech_input = st.text_area(
                    f"Type or voice-transcribe what you pronounced for Passage {idx}:",
                    key=f"pron_input_{day_selected}_{idx}",
                    placeholder="Read the text above out loud using voice typing or paste your transcript here..."
                )

                if st.button(f"Evaluate & Correct Pronunciation (Passage {idx})", key=f"btn_eval_pron_{day_selected}_{idx}"):
                    if not user_speech_input.strip():
                        st.warning("Please provide your spoken transcript or audio input text to evaluate.")
                    else:
                        with st.spinner(f"Analyzing pronunciation accuracy, stress, and intonation for Passage {idx}..."):
                            pron_prompt = f"""You are an expert Executive English Pronunciation Coach. 
Evaluate the user's spoken attempt against the target passage.

Target Passage: "{text_p}"
User's Spoken Attempt: "{user_speech_input}"

Provide an evaluation in JSON format containing:
1. 'overall_score': Score out of 100
2. 'phonetic_breakdown': Detailed phonetic analysis (IPA) of mispronounced/missed key executive words
3. 'pronunciation_errors': Specific word/sound errors made and how to fix them
4. 'rhythm_and_intonation': Advice on sentence stress, linking, and C-suite tone
5. 'corrected_transcript': Optimized read-along phonetic text with bold stress markers
"""
                            raw_pron_res = generate_ai_response(pron_prompt)
                            clean_pron_res = extract_json(raw_pron_res)
                            
                            if clean_pron_res:
                                try:
                                    pron_eval_data = json.loads(clean_pron_res, strict=False)
                                    st.session_state[f"pron_eval_{day_selected}_{idx}"] = pron_eval_data
                                    save_data_to_file()
                                except Exception as e:
                                    st.error(f"Evaluation Error: {e}")

                eval_result = st.session_state.get(f"pron_eval_{day_selected}_{idx}")
                if eval_result:
                    score = eval_result.get("overall_score", 0)
                    if score >= 80:
                        st.markdown(f'<div class="correct-card"><b>🏆 Overall Pronunciation Score: {score}/100</b></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="wrong-card"><b>📊 Overall Pronunciation Score: {score}/100</b></div>', unsafe_allow_html=True)
                    
                    st.markdown("#### 🎯 Phonetic & Intonation Feedback")
                    render_feedback_section(eval_result)
                    st.divider()

        # --- 3. GRAMMAR ---
        with tab_g:
            st.markdown(f"### 📐 Executive Grammar Focus: {day_grammar}")
            pg = f"""Generate an executive grammar training module on target grammar concept '{day_grammar}'. ALL content MUST be in 100% ENGLISH.
            Return JSON with keys:
            1. 'lesson_theory': {{'title': string, 'core_rule': string, 'executive_context': string, 'formula': string, 'examples': [string, string]}}
            2. 'questions': array of 5 objects ('id', 'question', 'options', 'answer', 'explanation')."""
            
            render_quiz_system(f"g_{day_selected}", pg, f"Load Grammar Module (Day {day_selected})", "Grammar", seed_key=f"grammar_module_{day_selected}")

        # --- 4. READING ---
        with tab_r:
            st.markdown(f"### 📖 Strategic Business Case Study Reading: {day_topic}")
            pr = f"""Generate a high-level C-suite business case study reading passage (300 words) on topic '{day_topic}'. ALL content MUST be in ENGLISH.
            Return JSON with keys:
            1. 'passage': full case study text
            2. 'questions': array of 5 comprehension/inference questions with keys ('id', 'question', 'options', 'answer', 'explanation')."""
            
            render_quiz_system(f"r_{day_selected}", pr, f"Load Reading Case Study (Day {day_selected})", "Reading", seed_key=f"reading_module_{day_selected}")

        # --- 5. LISTENING ---
        with tab_l:
            st.markdown(f"### 🎧 Executive Briefing Listening Simulation: {day_topic}")
            pl = f"""Generate a C-suite executive briefing transcript (250 words) on topic '{day_topic}'. ALL content MUST be in ENGLISH.
            Return JSON with keys:
            1. 'passage': full audio briefing text
            2. 'questions': array of 5 listening comprehension questions with keys ('id', 'question', 'options', 'answer', 'explanation')."""
            
            render_quiz_system(f"l_{day_selected}", pl, f"Load Listening Briefing (Day {day_selected})", "Listening", seed_key=f"listening_module_{day_selected}")

        # --- 6. WRITING ---
        with tab_w:
            st.markdown(f"### ✍️ Detailed Executive Writing Challenge: {day_topic}")
            pw_prompt = f"Generate a detailed business writing prompt for topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with keys 'scenario_title', 'business_context', 'prompt_instructions'."
            w_prompt_data = get_or_generate_data(f"w_prompt_{day_selected}", pw_prompt, seed_key=f"writing_prompt_{day_selected}") or {}
            
            if w_prompt_data:
                st.markdown(f"""
                <div class="apex-card">
                    <h4>📌 Scenario: {w_prompt_data.get('scenario_title', 'C-Suite Briefing')}</h4>
                    <p><b>Business Context:</b> {w_prompt_data.get('business_context', '')}</p>
                    <p><b>Your Task:</b> {w_prompt_data.get('prompt_instructions', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                key_w_in = f"w_input_{day_selected}"
                if key_w_in not in st.session_state:
                    st.session_state[key_w_in] = ""

                user_writing = st.text_area("Write your executive memo / response here:", value=st.session_state.get(key_w_in, ""), height=220, key=key_w_in)
                
                if st.button("Submit Writing for AI C-Suite Evaluation", key=f"btn_eval_w_{day_selected}", use_container_width=True):
                    if len(user_writing.strip()) < 20:
                        st.warning("Please provide a more detailed writing sample (at least 20 words).")
                    else:
                        with st.spinner("Evaluating writing tone, grammar, and strategic impact..."):
                            peval_w = f"""You are a C-suite Executive Coach. Evaluate this response for prompt: '{w_prompt_data.get('prompt_instructions')}'
                            User Submission: '{user_writing}'
                            ALL text MUST be in 100% ENGLISH. Return JSON with keys:
                            1. 'overall_score': number out of 100
                            2. 'executive_tone_feedback': text
                            3. 'grammar_and_syntax_corrections': array of strings
                            4. 'enhanced_c_suite_version': text rewrite."""
                            
                            w_eval_res = generate_ai_response(peval_w)
                            clean_w = extract_json(w_eval_res)
                            if clean_w:
                                try:
                                    st.session_state[f"w_eval_{day_selected}"] = json.loads(clean_w, strict=False)
                                    save_data_to_file()
                                except Exception as e:
                                    st.error(f"Writing Evaluation Error: {e}")

                w_eval = st.session_state.get(f"w_eval_{day_selected}")
                if w_eval:
                    st.markdown("### 📊 Executive Writing Feedback")
                    score = w_eval.get('overall_score', 0)
                    if score >= 80:
                        st.markdown(f'<div class="correct-card"><b>🏆 Score: {score}/100</b></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="wrong-card"><b>📊 Score: {score}/100</b></div>', unsafe_allow_html=True)
                    
                    render_feedback_section(w_eval)

        # --- 7. SPEAKING ---
        with tab_s:
            st.markdown(f"### 💬 Data-Driven Speaking & Boardroom Presentation Scenario: {day_topic}")
            ps_prompt = f"Generate a C-suite boardroom speaking challenge for topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON with keys 'scenario', 'speaking_prompt', 'key_points_to_cover'."
            s_prompt_data = get_or_generate_data(f"s_prompt_{day_selected}", ps_prompt, seed_key=f"speaking_prompt_{day_selected}") or {}

            if s_prompt_data:
                st.markdown(f"""
                <div class="apex-card">
                    <h4>🎙️ Boardroom Challenge: {s_prompt_data.get('scenario', 'Executive Address')}</h4>
                    <p><b>Prompt:</b> {s_prompt_data.get('speaking_prompt', '')}</p>
                    <p><b>Key Points to Include:</b> {s_prompt_data.get('key_points_to_cover', '')}</p>
                </div>
                """, unsafe_allow_html=True)

                key_s_in = f"s_input_{day_selected}"
                if key_s_in not in st.session_state:
                    st.session_state[key_s_in] = ""

                user_speaking = st.text_area("Paste or voice-transcribe your speech transcript here:", value=st.session_state.get(key_s_in, ""), height=180, key=key_s_in)
                
                if st.button("Submit Speaking Transcript for AI Assessment", key=f"btn_eval_s_{day_selected}", use_container_width=True):
                    if len(user_speaking.strip()) < 15:
                        st.warning("Please provide a longer speaking transcript for analysis.")
                    else:
                        with st.spinner("Evaluating speech rhetoric, fluency, and persuasion..."):
                            peval_s = f"""You are an Executive Communications Director. Evaluate this transcript for prompt: '{s_prompt_data.get('speaking_prompt')}'
                            User Transcript: '{user_speaking}'
                            ALL text MUST be in 100% ENGLISH. Return JSON with keys:
                            1. 'persuasion_score': number out of 100
                            2. 'rhetoric_and_fluency_analysis': text
                            3. 'key_improvements': array of strings
                            4. 'polished_c_suite_delivery': text rewrite."""
                            
                            s_eval_res = generate_ai_response(peval_s)
                            clean_s = extract_json(s_eval_res)
                            if clean_s:
                                try:
                                    st.session_state[f"s_eval_{day_selected}"] = json.loads(clean_s, strict=False)
                                    save_data_to_file()
                                except Exception as e:
                                    st.error(f"Speaking Evaluation Error: {e}")

                s_eval = st.session_state.get(f"s_eval_{day_selected}")
                if s_eval:
                    st.markdown("### 📊 Executive Speaking Feedback")
                    score = s_eval.get('persuasion_score', 0)
                    if score >= 80:
                        st.markdown(f'<div class="correct-card"><b>🏆 Score: {score}/100</b></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="wrong-card"><b>📊 Score: {score}/100</b></div>', unsafe_allow_html=True)
                    
                    render_feedback_section(s_eval)

        # --- 8. TRANSLATION PRACTICE ---
        with tab_t:
            st.markdown(f"### 🌐 Strategic Executive Translation Challenge: {day_topic}")
            st.caption("Translate complex executive business statements into high-impact, professional C-suite English.")
            
            pt_prompt = f"Generate 3 complex business translation sentences on topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON with key 'translation_tasks' containing array of 3 objects: 'id', 'source_context', 'target_prompt', 'ideal_c_suite_translation'."
            t_data = get_or_generate_data(f"t_data_{day_selected}", pt_prompt, seed_key=f"trans_prompt_{day_selected}") or {}
            
            t_tasks = t_data.get("translation_tasks", [])
            if t_tasks:
                for idx, task in enumerate(t_tasks, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4>Task {idx}: {task.get('source_context', '')}</h4>
                        <p><b>Prompt/Context:</b> {task.get('target_prompt', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    key_t_in = f"trans_input_{day_selected}_{idx}"
                    if key_t_in not in st.session_state:
                        st.session_state[key_t_in] = ""

                    st.text_area(f"Your C-Suite English Translation (Task {idx}):", value=st.session_state.get(key_t_in, ""), key=key_t_in, height=100)
                    st.write("---")

                if st.button("Submit & Evaluate All Translations", key=f"btn_eval_t_{day_selected}", use_container_width=True):
                    u_trans_map = {}
                    for idx in range(1, len(t_tasks) + 1):
                        key_t_in = f"trans_input_{day_selected}_{idx}"
                        u_trans_map[idx] = st.session_state.get(key_t_in, "")

                    with st.spinner("Evaluating translation precision and vocabulary appropriateness..."):
                        peval_t = f"""Evaluate these user translations against ideal executive English standards.
                        Tasks & Submissions: {json.dumps(u_trans_map)}
                        Reference Ideal Translations: {json.dumps(t_tasks)}
                        ALL feedback MUST be strictly in 100% ENGLISH. Return JSON with key 'evaluations' as an array of 3 objects corresponding to each task: ('task_id', 'accuracy_score', 'feedback', 'recommended_refinement')."""
                        
                        raw_t_eval = generate_ai_response(peval_t)
                        clean_t_eval = extract_json(raw_t_eval)
                        if clean_t_eval:
                            try:
                                st.session_state[f"t_eval_{day_selected}"] = json.loads(clean_t_eval, strict=False)
                                save_data_to_file()
                            except Exception as e:
                                st.error(f"Translation Evaluation Error: {e}")

                t_eval = st.session_state.get(f"t_eval_{day_selected}")
                if t_eval and "evaluations" in t_eval:
                    st.markdown("### 📊 Translation Assessment Results")
                    eval_list = t_eval["evaluations"]
                    for ev in eval_list:
                        tid = ev.get('task_id', 1)
                        sc = ev.get('accuracy_score', 0)
                        
                        if sc >= 80:
                            st.markdown(f'<div class="correct-card"><b>Task {tid} Score: {sc}/100</b><br>{ev.get("feedback")}<br><b>Refinement:</b> {ev.get("recommended_refinement")}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="wrong-card"><b>Task {tid} Score: {sc}/100</b><br>{ev.get("feedback")}<br><b>Refinement:</b> {ev.get("recommended_refinement")}</div>', unsafe_allow_html=True)

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Error Log & Remind Spaced Review</h2>
            <p style='margin:5px 0 0 0;'>Targeted review of past incorrect answers across all skills.</p>
        </div>
        """, unsafe_allow_html=True)

        error_log = st.session_state.get("error_log", [])
        
        if not error_log:
            st.success("🎉 Excellent! You currently have no logged errors in your review queue.")
        else:
            st.markdown(f"### 📋 Total Recorded Errors: **{len(error_log)}**")
            
            if st.button("🗑️ Clear Error Log", use_container_width=True):
                st.session_state["error_log"] = []
                save_data_to_file()
                st.toast("Error log cleared!", icon="🧹")
                st.rerun()

            for idx, err in enumerate(error_log, 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <h4>Error #{idx} [{err.get('skill', 'General')}]</h4>
                    <p><b>Question:</b> {err.get('question')}</p>
                    <p style="color:#e11d48 !important;"><b>Your Answer:</b> {err.get('your_answer')}</p>
                    <p style="color:#16a34a !important;"><b>Correct Answer:</b> {err.get('correct_answer')}</p>
                    <p>💡 <b>Explanation:</b> {err.get('explanation')}</p>
                </div>
                """, unsafe_allow_html=True)