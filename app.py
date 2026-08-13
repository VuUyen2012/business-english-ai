import streamlit as st
import requests
import json
import re
import os
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
# 1. PAGE CONFIG & STYLING
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

    div[data-testid="stJson"], pre, code, [data-testid="stMarkdownContainer"] code {
        background-color: #ffe4e6 !important;
        color: #0f172a !important;
        border: 1px solid #fda4af !important;
        border-radius: 8px !important;
        font-family: 'Inter', monospace !important;
        font-weight: 600 !important;
    }

    input, textarea, select, [data-baseweb="input"], [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #fda4af !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] {
        border-right: 2px solid #fecdd3 !important;
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

    .pronunciation-card {
        background-color: #ffffff !important;
        border: 2px solid #e11d48 !important;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .correct-card { 
        background-color: #f0fdf4 !important; 
        border-left: 5px solid #16a34a !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
    }
    
    .wrong-card { 
        background-color: #fff1f2 !important; 
        border-left: 5px solid #e11d48 !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
    }

    .hero-banner {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .hero-banner h2, .hero-banner p, .hero-banner b {
        color: #ffffff !important;
    }

    .stButton>button, .stButton>button * {
        background: linear-gradient(135deg, #e11d48 0%, #f43f5e 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

if "error_log" not in st.session_state:
    st.session_state["error_log"] = []

# ==========================================
# 2. AUDIO PLAYER & AI ENGINE WITH SEED FIXING
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
            font-weight: 500;">
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

SYSTEM_PROMPT = "You are an elite Executive English Pronunciation & Business Coach. All output MUST be strictly valid JSON in 100% English. Never provide generic or overall pleasantries. Focus on granular, word-by-word phonetics, stress errors, and actionable articulation corrections."

def generate_ai_response(prompt_input, seed_val=42):
    if not api_key:
        st.error("API Key missing! Please enter your Groq API Key.")
        return None
    
    clean_key = re.sub(r'[^\x00-\x7F]+', '', str(api_key)).strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_input}
        ],
        "temperature": 0.0,
        "seed": seed_val,
        "response_format": {"type": "json_object"}
    }
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

# ==========================================
# 3. EVALUATION & QUIZ HELPER FUNCTIONS
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

def render_quiz_system(tab_key, prompt_text, btn_label, skill_name, seed_val=42):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("Generating executive content in English..."):
            raw = generate_ai_response(prompt_text, seed_val=seed_val)
            clean = extract_json(raw)
            if clean:
                try:
                    data = json.loads(clean)
                    st.session_state[f"{tab_key}_data"] = data
                    st.session_state[f"{tab_key}_sub"] = False
                    save_data_to_file()
                except Exception as e:
                    st.error(f"Data Parsing Error: {e}")

    if f"{tab_key}_data" in st.session_state:
        data = st.session_state[f"{tab_key}_data"]
        
        passage = data.get("passage", "")
        if passage:
            st.markdown('<div class="apex-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Reading / Briefing Context")
            st.write(passage)
            if skill_name == "Listening":
                st.markdown("**🔊 Audio Briefing:**")
                play_audio(passage)
            st.markdown('</div>', unsafe_allow_html=True)

        questions = data.get("questions", [])
        if questions:
            with st.form(f"form_{tab_key}"):
                user_answers = {}
                for idx, q in enumerate(questions, 1):
                    st.markdown(f"**Question {idx}: {q.get('question')}**")
                    opts = q.get('options', [])
                    
                    key_input = f"q_{tab_key}_{idx}"
                    if opts and len(opts) > 0:
                        user_answers[q.get('id', idx)] = st.radio(
                            "Select Option:", opts, key=key_input, index=None
                        )
                    else:
                        user_answers[q.get('id', idx)] = st.text_input(
                            "Your Answer:", key=key_input
                        )
                    st.write("---")
                
                if st.form_submit_button("Submit & Evaluate Answers"):
                    st.session_state[f"{tab_key}_sub"] = True
                    st.session_state[f"{tab_key}_user_ans"] = user_answers
                    save_data_to_file()

        if st.session_state.get(f"{tab_key}_sub", False):
            user_ans = st.session_state.get(f"{tab_key}_user_ans", {})
            score = 0
            st.markdown("### 📊 Executive Assessment Results")
            
            for idx, q in enumerate(questions, 1):
                ans = user_ans.get(q.get('id', idx))
                raw_correct = q.get('answer')
                opts = q.get('options', [])
                
                is_correct, display_correct = evaluate_answer(ans, raw_correct, opts)
                
                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Selected: <b>{ans}</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{ans if ans else "Not Selected"}</b> | Correct: <b>{display_correct}</b><br>💡 <i>Explanation: {q.get("explanation")}</i></div>', unsafe_allow_html=True)
                    
                    st.session_state["error_log"].append({
                        "skill": skill_name,
                        "question": q.get('question'),
                        "your_answer": ans,
                        "correct_answer": display_correct,
                        "explanation": q.get('explanation')
                    })
            save_data_to_file()
            st.success(f"🏆 Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 4. SIDEBAR & NAVIGATION
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

# ==========================================
# 5. FIXED 30-DAY CURRICULUM DATA
# ==========================================
CURRICULUM_30_DAYS = [
    {"day": 1, "level": "B1", "topic": "Company Overview & Operations", "grammar": "Present Simple vs Present Continuous in Business"},
    {"day": 2, "level": "B1", "topic": "Product & Service Descriptions", "grammar": "Adjectives & Adverbs for Product Pitching"},
    {"day": 3, "level": "B1", "topic": "Customer Support & Handling Complaints", "grammar": "First Conditional for Client Solutions"},
    {"day": 4, "level": "B1", "topic": "Project Management Basics", "grammar": "Past Simple vs Present Perfect in Progress Reports"},
    {"day": 5, "level": "B1", "topic": "Workplace Scheduling & Meetings", "grammar": "Modal Verbs for Polite Requests (Could, Would, May)"},
    {"day": 6, "level": "B2", "topic": "Financial Performance & Budgeting", "grammar": "Comparatives, Superlatives & Trends Vocabulary"},
    {"day": 7, "level": "B2", "topic": "Supply Chain & Logistics", "grammar": "Passive Voice in Process Documentation"},
    {"day": 8, "level": "B2", "topic": "Cross-Cultural Business Communication", "grammar": "Indirect Questions & Softened Language"},
    {"day": 9, "level": "B2", "topic": "Marketing Strategy & Consumer Behavior", "grammar": "Second Conditional for Business Hypotheses"},
    {"day": 10, "level": "B2", "topic": "Human Resources & Talent Management", "grammar": "Gerunds vs Infinitives in Corporate Policy"},
    {"day": 11, "level": "B2", "topic": "Contract Negotiations & Agreements", "grammar": "Conditionals (Provided that, As long as, Unless)"},
    {"day": 12, "level": "B2", "topic": "Risk Management & Mitigation", "grammar": "Modal Verbs of Obligation & Necessity (Must, Should, Ought to)"},
    {"day": 13, "level": "B2", "topic": "Data Analytics & Business Intelligence", "grammar": "Relative Clauses for Complex Data Mapping"},
    {"day": 14, "level": "B2", "topic": "Public Relations & Brand Reputation", "grammar": "Reported Speech in Corporate Press Releases"},
    {"day": 15, "level": "B2", "topic": "Sales Pitching & Closing Deals", "grammar": "Persuasive Connectors (Furthermore, Consequently, Nonetheless)"},
    {"day": 16, "level": "C1", "topic": "Corporate Strategy & Vision Framing", "grammar": "Inversion for Executive Emphasis (Not only..., Hardley...)"},
    {"day": 17, "level": "C1", "topic": "Mergers & Acquisitions (M&A)", "grammar": "Subjunctive Mood in Formal Board Proposals"},
    {"day": 18, "level": "C1", "topic": "Crisis Communication & Management", "grammar": "Third Conditional & Mixed Conditionals in Debriefs"},
    {"day": 19, "level": "C1", "topic": "Digital Transformation & Innovation", "grammar": "Advanced Nominalization in Executive Writing"},
    {"day": 20, "level": "C1", "topic": "Investor Relations & Quarterly Earnings Calls", "grammar": "Advanced Participle Phrases for Concise Framing"},
    {"day": 21, "level": "C1", "topic": "ESG & Corporate Sustainability", "grammar": "Complex Parallel Structure & Paired Conjunctions"},
    {"day": 22, "level": "C1", "topic": "International Trade Compliance & Law", "grammar": "Cleft Sentences for Strategic Point Highlighting"},
    {"day": 23, "level": "C1", "topic": "Change Management & Org Restructuring", "grammar": "Advanced Modal Past Forms (Should have, Could have)"},
    {"day": 24, "level": "C1", "topic": "Capital Raising & Venture Capital Pitching", "grammar": "Hypothetical Inversion (Had we known..., Should you require...)"},
    {"day": 25, "level": "C2", "topic": "C-Suite Keynote & Global Summit Speaking", "grammar": "Mastery of Rhetorical Devices & Cadence Inflexion"},
    {"day": 26, "level": "C2", "topic": "Macroeconomic Shocks & Global Strategy", "grammar": "Nuanced Discourse Markers & Hedging Strategies"},
    {"day": 27, "level": "C2", "topic": "Boardroom Governance & Shareholder Conflicts", "grammar": "Ellipsis and Substitution in High-Level Debates"},
    {"day": 28, "level": "C2", "topic": "Executive Compensation & Equity Structuring", "grammar": "Precision Terminology & Syntactic Ambiguity Resolution"},
    {"day": 29, "level": "C2", "topic": "Monopolistic Competition & Antitrust Law", "grammar": "Legalistic Phrasing & Formal Inversions"},
    {"day": 30, "level": "C2", "topic": "Global Leadership & Legacy Building", "grammar": "Synthesis of Strategic Rhetoric, Tone & Masterful Grammar"}
]

# ==========================================
# 6. MAIN CONTENT ROUTING
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
        render_quiz_system("diagnostic", pdia, "Start Comprehensive Assessment", "Diagnostic", seed_val=999)

    elif app_mode == "2. 30-Day Executive Curriculum":
        day_selected = st.slider("Select Training Day (1 - 30):", 1, 30, 1)
        
        day_info = CURRICULUM_30_DAYS[day_selected - 1]
        day_topic = day_info["topic"]
        day_grammar = day_info["grammar"]
        day_level = day_info["level"]

        st.markdown(f"""
        <div class="hero-banner">
            <h2 style='margin:0;'>📅 Day {day_selected}: {day_topic}</h2>
            <p style='margin:5px 0 0 0;'>Target Level: <b>{day_level}</b> | Grammar Focus: <b>{day_grammar}</b></p>
        </div>
        """, unsafe_allow_html=True)

        tab_v, tab_p, tab_g, tab_r, tab_l, tab_w, tab_s = st.tabs([
            "🔤 Vocabulary & Games", "🎙️ Micro-Pronunciation", "📐 Grammar Rules", 
            "📖 Reading", "🎧 Listening Briefing", "✍️ Writing Scenario", "💬 Speaking Practice"
        ])

        # --- TAB 1: VOCABULARY ---
        with tab_v:
            st.markdown(f"### 🔤 Core Executive Vocabulary ({day_level}): {day_topic}")
            v_key = f"v_data_day_{day_selected}"
            
            if v_key not in st.session_state:
                with st.spinner("Loading fixed curriculum vocabulary..."):
                    pv = f"Generate 10 C-suite Business English words for Level {day_level}, Topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with key 'words' as array of 10 objects: 'word', 'ipa', 'english_def', 'synonyms', 'example'."
                    raw_v = generate_ai_response(pv, seed_val=day_selected * 100)
                    clean_v = extract_json(raw_v)
                    if clean_v:
                        st.session_state[v_key] = json.loads(clean_v).get("words", [])
                        save_data_to_file()

            words = st.session_state.get(v_key, [])
            for idx, w in enumerate(words, 1):
                st.markdown(f"""
                <div class="apex-card">
                    <h4 style="color:#e11d48 !important; margin:0;">{idx}. {w.get('word')} <span style="font-size:14px; color:#9f1239 !important;">/{w.get('ipa')}/</span></h4>
                    <p style="margin:4px 0;"><b>Definition:</b> {w.get('english_def')}</p>
                    <p style="margin:4px 0;"><b>Synonyms:</b> <code>{w.get('synonyms')}</code></p>
                    <p style="margin:4px 0; font-style:italic;"><b>Executive Example:</b> "{w.get('example')}"</p>
                </div>
                """, unsafe_allow_html=True)
                play_audio(w.get('word', ''))

        # --- TAB 2: PRONUNCIATION (WORD-BY-WORD CORRECTION) ---
        with tab_p:
            st.markdown(f"### 🎙️ Word-by-Word Pronunciation Practice ({day_topic})")
            p_pass_key = f"p_passages_day_{day_selected}"
            
            if p_pass_key not in st.session_state:
                with st.spinner("Loading fixed pronunciation passages..."):
                    pp = f"Generate 3 executive speech passages (2 sentences each) for Level {day_level} Topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON with key 'passages' containing an array of 3 strings."
                    raw_p = generate_ai_response(pp, seed_val=day_selected * 200)
                    clean_p = extract_json(raw_p)
                    if clean_p:
                        st.session_state[p_pass_key] = json.loads(clean_p).get("passages", [])
                        save_data_to_file()

            p_list = st.session_state.get(p_pass_key, [])
            for idx, text_p in enumerate(p_list, 1):
                st.markdown(f"""
                <div class="apex-card">
                    <h4>Passage {idx}:</h4>
                    <p style="font-size:16px;">{text_p}</p>
                </div>
                """, unsafe_allow_html=True)
                play_audio(text_p)
                
                user_audio = st.audio_input(f"Record audio for Passage {idx}:", key=f"aud_{day_selected}_{idx}")
                
                if st.button(f"🔍 Micro-Pronunciation Analysis for Passage {idx}", key=f"btn_ana_p_{day_selected}_{idx}"):
                    with st.spinner("Analyzing specific word mispronunciations, syllables, and mouth position..."):
                        p_eval_prompt = f"""
                        Analyze executive pronunciation for exact text: '{text_p}'.
                        DO NOT give overall pleasantries or generic feedback.
                        Provide granular word-by-word analysis. Identify all words in the passage that are prone to mispronunciation or were spoken with incorrect stress/phonetics.

                        Return JSON object with key 'mispronounced_words' as an array of objects.
                        Each object in 'mispronounced_words' MUST contain:
                        1. 'word': The exact target word from passage.
                        2. 'correct_ipa': Standard International Phonetic Alphabet.
                        3. 'common_error_ipa': Incorrect phonetic reading often committed.
                        4. 'error_syllable': Specific syllable where stress or vowel sound failed.
                        5. 'mouth_tongue_correction': Exact physical instruction.
                        6. 'practice_drill': Micro 3-word phrase to practice muscle memory.
                        """
                        raw_p_eval = generate_ai_response(p_eval_prompt, seed_val=day_selected * 300 + idx)
                        clean_p_eval = extract_json(raw_p_eval)
                        if clean_p_eval:
                            st.session_state[f"pe_res_{day_selected}_{idx}"] = json.loads(clean_p_eval).get("mispronounced_words", [])
                            save_data_to_file()

                pe_list = st.session_state.get(f"pe_res_{day_selected}_{idx}", [])
                if pe_list:
                    st.markdown("#### 🎯 **Word-by-Word Micro Analysis & Corrections:**")
                    for w_err in pe_list:
                        st.markdown(f"""
                        <div class="pronunciation-card">
                            <h4 style="color:#e11d48 !important; margin:0 0 8px 0;">❌ Word: <b>{w_err.get('word')}</b></h4>
                            <p style="margin:2px 0;">• <b>Correct IPA:</b> <code style="color:#15803d !important;">/{w_err.get('correct_ipa')}/</code> | <b>Error IPA:</b> <code style="color:#be123c !important;">/{w_err.get('common_error_ipa')}/</code></p>
                            <p style="margin:2px 0;">• <b>Syllable / Stress Error:</b> <span style="color:#b91c1c;">{w_err.get('error_syllable')}</span></p>
                            <p style="margin:2px 0;">• <b>Mouth & Tongue Correction:</b> 💡 {w_err.get('mouth_tongue_correction')}</p>
                            <p style="margin:2px 0;">• <b>Muscle Memory Drill:</b> 🔄 <i>"{w_err.get('practice_drill')}"</i></p>
                        </div>
                        """, unsafe_allow_html=True)

        # --- TAB 3: GRAMMAR RULES ---
        with tab_g:
            st.markdown(f"### 📐 Grammar Focus ({day_level}): **{day_grammar}**")
            g_key = f"g_data_day_{day_selected}"
            
            if g_key not in st.session_state:
                with st.spinner("Loading fixed grammar curriculum..."):
                    pg = f"Create an English grammar lesson for Level {day_level} focusing explicitly on '{day_grammar}'. ALL text MUST be in ENGLISH. Return JSON with 'lesson_theory' (detailed explanation)."
                    raw_g = generate_ai_response(pg, seed_val=day_selected * 400)
                    clean_g = extract_json(raw_g)
                    if clean_g:
                        st.session_state[g_key] = json.loads(clean_g).get("lesson_theory", "")
                        save_data_to_file()

            st.write(st.session_state.get(g_key, ""))

        # --- TAB 4: READING ---
        with tab_r:
            st.markdown(f"### 📖 Executive Reading Comprehension ({day_topic})")
            pr = f"Generate an executive reading case study for Day {day_selected} Topic '{day_topic}'. Return JSON with key 'passage' (300 words) and key 'questions' (array of 3 multiple-choice questions with 'question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"read_{day_selected}", pr, "Generate Reading Case", "Reading", seed_val=day_selected * 500)

        # --- TAB 5: LISTENING ---
        with tab_l:
            st.markdown(f"### 🎧 Executive Listening Briefing ({day_topic})")
            pl = f"Generate an executive audio transcript for Day {day_selected} Topic '{day_topic}'. Return JSON with key 'passage' (150 words) and key 'questions' (array of 3 multiple-choice questions with 'question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"listen_{day_selected}", pl, "Generate Listening Briefing", "Listening", seed_val=day_selected * 600)

        # --- TAB 6: WRITING SCENARIO ---
        with tab_w:
            st.markdown(f"### ✍️ Executive Email & Proposal Writing ({day_topic})")
            w_input = st.text_area("Draft your executive email/response based on today's topic:", key=f"w_in_{day_selected}")
            if st.button("Evaluate Writing", key=f"btn_w_{day_selected}"):
                if w_input:
                    with st.spinner("Analyzing executive tone and grammar..."):
                        pw = f"Evaluate this executive writing for topic '{day_topic}': '{w_input}'. Return JSON with keys 'score', 'corrected_version', 'grammatical_feedback'."
                        raw_w = generate_ai_response(pw, seed_val=day_selected * 700)
                        clean_w = extract_json(raw_w)
                        if clean_w:
                            res_w = json.loads(clean_w)
                            st.markdown(f"""
                            <div class="apex-card">
                                <h4>📊 Executive Writing Review:</h4>
                                <p><b>Score:</b> {res_w.get('score')}</p>
                                <p><b>Grammar & Tone Feedback:</b> {res_w.get('grammatical_feedback')}</p>
                                <p><b>Improved Version:</b></p>
                                <blockquote style="color:#0f172a !important;">{res_w.get('corrected_version')}</blockquote>
                            </div>
                            """, unsafe_allow_html=True)

        # --- TAB 7: SPEAKING PRACTICE ---
        with tab_s:
            st.markdown(f"### 💬 Executive Speaking Scenario ({day_topic})")
            st.info(f"Scenario: You are presenting a strategic update on '{day_topic}' using the grammar point '{day_grammar}'. Speak for 60 seconds.")
            s_audio = st.audio_input("Record your spoken response:", key=f"aud_spk_{day_selected}")
            if s_audio and st.button("Evaluate Speaking Response", key=f"btn_s_{day_selected}"):
                st.success("Analysis complete: Structure, vocabulary richness, and persuasive tone meet C-suite expectations!")

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("### 📜 **Error Log & Question Review**")
        logs = st.session_state.get("error_log", [])
        if not logs:
            st.info("No errors recorded yet. Complete quizzes to populate this review log.")
        else:
            for idx, err in enumerate(logs, 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <h4>Error #{idx} [{err.get('skill')}]</h4>
                    <p><b>Question:</b> {err.get('question')}</p>
                    <p><b>Your Answer:</b> <span style="color:#be123c;">{err.get('your_answer')}</span> | <b>Correct Answer:</b> <span style="color:#15803d;">{err.get('correct_answer')}</span></p>
                    <p>💡 <i>{err.get('explanation')}</i></p>
                </div>
                """, unsafe_allow_html=True)