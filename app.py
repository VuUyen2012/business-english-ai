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
    """Trích xuất toàn bộ dữ liệu cần thiết để lưu trữ."""
    data_to_save = {}
    for key, val in st.session_state.items():
        if key.startswith("FormSubmitter:") or key in ["data_loaded"]:
            continue
        if isinstance(val, (bytes, bytearray)):
            continue
        data_to_save[key] = val
    return data_to_save

def save_data_to_file():
    """Lưu toàn bộ session_state vào file JSON."""
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

# Tự động load dữ liệu đã lưu khi khởi chạy trang
if "data_loaded" not in st.session_state:
    load_saved_data()
    st.session_state["data_loaded"] = True

# Styling CSS
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
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
    }
    .correct-card * { color: #0f172a !important; }
    
    .wrong-card { 
        background-color: #fff1f2 !important; 
        border-left: 5px solid #e11d48 !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
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

    /* ĐỊNH DẠNG TẤT CẢ CÁC NÚT BẤM VÀ SUBMIT BUTTONS NỔI BẬT */
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
# 2. AUDIO PLAYER & HELPERS
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

# ==========================================
# 3. SIDEBAR & GROQ ENGINE
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
        st.error("API Key missing! Please enter your Groq API Key.")
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
        res = requests.post(url, headers=headers, json=payload, timeout=45)
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
    return match.group(1).strip() if match else raw_text.strip()

def get_or_generate_data(session_key, prompt_text, seed_key=None):
    if session_key not in st.session_state or not st.session_state[session_key]:
        with st.spinner("Loading executive curriculum module..."):
            raw = generate_ai_response(prompt_text, seed_key=seed_key)
            clean = extract_json(raw)
            if clean:
                try:
                    st.session_state[session_key] = json.loads(clean)
                    save_data_to_file()
                except Exception as e:
                    st.error(f"Data Parsing Error: {e}")
    return st.session_state.get(session_key, None)

# ==========================================
# 4. EVALUATION & QUIZ SYSTEM WITH PERSISTENCE
# ==========================================
def evaluate_answer(user_selection, raw_correct, options):
    if user_selection is None or raw_correct is None:
        return False, str(raw_correct)

    u_sel_str = str(user_selection).strip().lower()
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
                
                # Trực tiếp kết nối state mà không cần st.form
                if key_input not in st.session_state:
                    st.session_state[key_input] = opts[0] if opts else ""

                if opts and len(opts) > 0:
                    current_val = st.session_state[key_input]
                    opt_idx = opts.index(current_val) if current_val in opts else 0
                    st.radio("Select Option:", opts, index=opt_idx, key=key_input)
                else:
                    st.text_input("Your Answer:", key=key_input)
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
                raw_correct = q.get('answer')
                opts = q.get('options', [])
                
                is_correct, display_correct = evaluate_answer(ans, raw_correct, opts)
                
                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Selected: <b>{ans}</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{ans if ans else "Not Selected"}</b> | Correct: <b>{display_correct}</b><br>💡 <i>Explanation: {q.get("explanation")}</i></div>', unsafe_allow_html=True)
                    
                    log_item = {
                        "skill": skill_name,
                        "question": q.get('question'),
                        "your_answer": ans,
                        "correct_answer": display_correct,
                        "explanation": q.get('explanation')
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
            <p style='margin:5px 0 0 0;'>Identify your current Executive English baseline proficiency.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pdia = "Generate a full baseline Executive Assessment test. Return JSON with key 'questions' containing 10 questions across grammar, vocabulary, reading comprehension, and business scenario evaluation."
        render_quiz_system("diagnostic", pdia, "Start Comprehensive Assessment", "Diagnostic", seed_key="diagnostic_test")

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

        tab_v, tab_p, tab_g, tab_r, tab_l, tab_w, tab_s = st.tabs([
            "🔤 Vocabulary & Games", "🗣️ Pronunciation", "📐 Grammar Rules", 
            "📖 Reading", "🎧 Listening Briefing", "✍️ Detailed Writing Scenario", "💬 Data-Driven Speaking"
        ])

        # --- 1. VOCABULARY & GAMES (PERFECT PERSISTENCE FIX) ---
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
            
            pgame = f"Generate 5 business vocabulary game questions for topic '{day_topic}'. ALL text MUST be in ENGLISH. Include advanced words beyond the core 10. For Game 1 return 'fill_words' array of objects ('word', 'hint_english'). For Game 2 return 'mcq_words' array of objects ('word', 'options', 'correct_option'). NOTE: 'correct_option' MUST be the exact full text string matching one item in 'options'. Return JSON with keys 'fill_words' and 'mcq_words'."
            g_data = get_or_generate_data(f"g_data_{day_selected}", pgame, seed_key=f"game_day_{day_selected}") or {}

            # FIX GAME 1 (TỰ ĐỘNG BINDING BẰNG STATE TRỰC TIẾP, KHÔNG BỊ TRỐNG CHỮ NÀO)
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
                        
                        st.text_input(f"Word starting with '{f_char}...':", key=key_g1_in)
                    
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

            # FIX GAME 2
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
                
                user_audio = st.audio_input(f"Record audio for Passage {idx}:", key=f"aud_{day_selected}_{idx}")
                
                if st.button(f"Analyze Detailed Pronunciation for Passage {idx}", key=f"btn_ana_p_{day_selected}_{idx}"):
                    with st.spinner("Analyzing word-by-word phonetics, stress, and intonation..."):
                        p_eval_prompt = f"""
                        You are a strict C-suite Executive Phonetics Coach. Analyze spoken English for passage: '{text_p}'.
                        Do NOT give vague or generic summaries. Provide actionable, word-by-word phonetic analysis to help improve pronunciation.
                        
                        Return JSON object with keys:
                        1. 'detailed_word_errors': array of objects for specific mispronounced words, each having:
                           - 'word': the target word
                           - 'ipa_correct': correct IPA representation
                           - 'common_mistake': phonetic error or missed sound
                           - 'coaching_tip': specific mouth/tongue position fix
                        2. 'intonation_and_pitch': specific instruction on pitch, pausing, and sentence rhythm
                        3. 'sentence_stress': exact words to emphasize in this passage for executive presence
                        4. 'overall_speech_score': e.g., '85/100'
                        ALL text MUST be strictly in 100% ENGLISH.
                        """
                        raw_p_eval = generate_ai_response(p_eval_prompt)
                        clean_p_eval = extract_json(raw_p_eval)
                        if clean_p_eval:
                            st.session_state[f"pe_res_{day_selected}_{idx}"] = json.loads(clean_p_eval)
                            save_data_to_file()

                if f"pe_res_{day_selected}_{idx}" in st.session_state:
                    pe = st.session_state[f"pe_res_{day_selected}_{idx}"]
                    st.markdown(f"""
                    <div class="apex-card" style="background-color: #fff1f2 !important;">
                        <h4 style="color:#e11d48 !important;">📊 Executive Speech Diagnostics (Score: {pe.get('overall_speech_score', 'N/A')})</h4>
                        <p>🌊 <b>Intonation & Pitch Contour:</b> {pe.get('intonation_and_pitch')}</p>
                        <p>🎯 <b>Sentence Stress Guidance:</b> {pe.get('sentence_stress')}</p>
                        <hr style="margin:10px 0;">
                        <h4 style="color:#be123c !important;">⚠️ Word-by-Word Phonetic Error Analysis:</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    word_errors = pe.get('detailed_word_errors', [])
                    if word_errors:
                        for err in word_errors:
                            st.markdown(f"""
                            <div class="wrong-card">
                                <p style="margin:0;">🔴 Target Word: <b>{err.get('word')}</b> | Correct IPA: <code>/{err.get('ipa_correct')}/</code></p>
                                <p style="margin:2px 0;">❌ Error / Flaw: <i>{err.get('common_mistake')}</i></p>
                                <p style="margin:2px 0;">💡 Coaching Fix: <b>{err.get('coaching_tip')}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No specific phonetic errors detected. Great articulation!")

        # --- 3. GRAMMAR RULES ---
        with tab_g:
            st.markdown(f"### 📐 Grammar Focus: {day_grammar}")
            pg = f"Generate a detailed grammar masterclass on '{day_grammar}' for Topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with key 'lesson_theory' (structured object/markdown) and 'questions' (array of 5 multiple-choice questions with 'question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"grammar_{day_selected}", pg, f"Load Day {day_selected} Grammar Module", "Grammar", seed_key=f"grammar_module_day_{day_selected}")

        # --- 4. READING ---
        with tab_r:
            st.markdown(f"### 📖 Case Reading Comprehension ({day_topic})")
            pr = f"Generate an executive case study (250 words) on '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with 'passage' string and 'questions' array of 5 reading comprehension questions ('question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"reading_{day_selected}", pr, f"Load Day {day_selected} Reading Case Study", "Reading", seed_key=f"reading_module_day_{day_selected}")

        # --- 5. LISTENING BRIEFING ---
        with tab_l:
            st.markdown(f"### 🎧 C-Suite Audio Briefing ({day_topic})")
            pl = f"Generate a executive spoken briefing script (200 words) on '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with 'passage' string and 'questions' array of 5 listening comprehension questions ('question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"listening_{day_selected}", pl, f"Load Day {day_selected} Audio Briefing", "Listening", seed_key=f"listening_module_day_{day_selected}")

        # --- 6. WRITING SCENARIO (FULL PERSISTENCE) ---
        with tab_w:
            st.markdown(f"### ✍️ Detailed Executive Writing Scenario ({day_topic})")
            pw = f"Generate a complex executive writing scenario on '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON object with 'scenario' string and 'prompt' instruction."
            w_module = get_or_generate_data(f"w_mod_{day_selected}", pw, seed_key=f"writing_module_day_{day_selected}") or {}
            
            if w_module:
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown(f"**Scenario:** {w_module.get('scenario')}")
                st.markdown(f"**Task Instructions:** {w_module.get('prompt')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                key_write_in = f"write_in_{day_selected}"
                if key_write_in not in st.session_state:
                    st.session_state[key_write_in] = ""

                u_writing = st.text_area("Draft your executive response (Email/Memo):", key=key_write_in, height=200)

                if st.button("Evaluate Writing", key=f"btn_w_eval_{day_selected}"):
                    if u_writing.strip():
                        save_data_to_file()
                        with st.spinner("Analyzing tone, grammar, and executive vocabulary..."):
                            p_weval = f"Evaluate this executive writing response: '{u_writing}' for topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON with 'grammar_score', 'tone_feedback', 'revised_version', 'key_improvements'."
                            raw_we = generate_ai_response(p_weval)
                            clean_we = extract_json(raw_we)
                            if clean_we:
                                st.session_state[f"we_res_{day_selected}"] = json.loads(clean_we)
                                save_data_to_file()
                    else:
                        st.warning("Please draft your response before submitting.")
                
                if f"we_res_{day_selected}" in st.session_state:
                    wer = st.session_state[f"we_res_{day_selected}"]
                    st.markdown('<div class="hint-card">', unsafe_allow_html=True)
                    st.markdown(f"### 📝 Executive Writing Feedback (Score: {wer.get('grammar_score')})")
                    st.markdown(f"**Tone & Style Analysis:** {wer.get('tone_feedback')}")
                    st.markdown(f"**Key Improvements:** {wer.get('key_improvements')}")
                    st.markdown("#### ✨ Revised C-Suite Level Draft:")
                    st.code(wer.get('revised_version'))
                    st.markdown('</div>', unsafe_allow_html=True)

        # --- 7. DATA-DRIVEN SPEAKING (FULL PERSISTENCE) ---
        with tab_s:
            st.markdown(f"### 💬 Data-Driven Executive Speaking ({day_topic})")
            ps = f"Generate an executive speaking task requiring data presentation on '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON with 'chart_description', 'speaking_prompt', 'recommended_phrases'."
            s_module = get_or_generate_data(f"s_mod_{day_selected}", ps, seed_key=f"speaking_module_day_{day_selected}") or {}
            
            if s_module:
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown(f"**Data Briefing / Chart:** {s_module.get('chart_description')}")
                st.markdown(f"**Prompt:** {s_module.get('speaking_prompt')}")
                st.markdown(f"**Recommended Phrases:** {s_module.get('recommended_phrases')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                u_speech_audio = st.audio_input("Record your speech response:", key=f"spk_aud_{day_selected}")
                
                if st.button("Evaluate Speaking Response", key=f"btn_s_eval_{day_selected}"):
                    with st.spinner("Analyzing executive speaking fluency and rhetoric..."):
                        p_seval = f"Evaluate executive presentation response for '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with 'clarity_score', 'persuasiveness_feedback', 'advanced_rhetoric_tips'."
                        raw_se = generate_ai_response(p_seval)
                        clean_se = extract_json(raw_se)
                        if clean_se:
                            st.session_state[f"se_res_{day_selected}"] = json.loads(clean_se)
                            save_data_to_file()
                
                if f"se_res_{day_selected}" in st.session_state:
                    ser = st.session_state[f"se_res_{day_selected}"]
                    st.markdown('<div class="hint-card">', unsafe_allow_html=True)
                    st.markdown(f"### 🎙️ Executive Speaking Feedback (Score: {ser.get('clarity_score')})")
                    st.markdown(f"**Persuasiveness & Tone:** {ser.get('persuasiveness_feedback')}")
                    st.markdown(f"**Rhetoric & Delivery Tips:** {ser.get('advanced_rhetoric_tips')}")
                    st.markdown('</div>', unsafe_allow_html=True)

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Error Log & Adaptive Memory Review</h2>
            <p style='margin:5px 0 0 0;'>Review mis-answered questions across diagnostic & daily modules.</p>
        </div>
        """, unsafe_allow_html=True)
        
        err_log = st.session_state.get("error_log", [])
        if not err_log:
            st.success("🎉 Excellent! Your error log is empty. No mistakes logged yet.")
        else:
            st.markdown(f"### 📋 Logged Errors Count: **{len(err_log)}**")
            for idx, item in enumerate(err_log, 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <b>[{item.get('skill')}] Error #{idx}</b><br>
                    <b>Question:</b> {item.get('question')}<br>
                    ❌ <b>Your Answer:</b> {item.get('your_answer')}<br>
                    ✅ <b>Correct Answer:</b> {item.get('correct_answer')}<br>
                    💡 <i>Explanation: {item.get('explanation')}</i>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Clear Error Log", use_container_width=True):
                st.session_state["error_log"] = []
                save_data_to_file()
                st.toast("Error log cleared!", icon="🧹")
                st.rerun()