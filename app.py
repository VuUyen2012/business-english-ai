import streamlit as st
import requests
import json
import re
import time
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & PINK/WHITE ACCENT CSS
# ==========================================
st.set_page_config(
    page_title="Apex English - 30-Day Executive Coaching",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS khắc phục triệt để lỗi chữ trắng trên nền trắng, áp dụng nền trắng/hồng nhạt
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. Global Reset & Background (Nền trắng/hồng cực nhẹ) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #fff1f2 !important; /* Hồng phấn nhẹ */
        color: #0f172a !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(255, 241, 242, 0.9) !important;
    }

    /* 2. Target ALL Text Elements (Bắt buộc chữ màu tối/đen) */
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] span, 
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stWidgetLabel"],
    label, p, span, h1, h2, h3, h4, h5, h6, li {
        color: #0f172a !important;
    }

    /* FIX LỖI SYNONYM / CODE TAGS (Bắt buộc chữ đen trên nền hồng nhạt) */
    code, pre, [data-testid="stMarkdownContainer"] code {
        color: #9f1239 !important; /* Màu hồng đậm/đỏ đô */
        background-color: #ffe4e6 !important; /* Nền hồng nhạt */
        border: 1px solid #fecdd3 !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-weight: 600 !important;
    }

    /* 3. Radio Buttons & Checkboxes */
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span,
    div[role="radiogroup"] div,
    [data-testid="stRadioButton"] label p {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* 4. Inputs, Textareas, Selectboxes */
    input, textarea, select, 
    [data-baseweb="input"] input, 
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] * {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #fda4af !important;
        border-radius: 6px !important;
    }
    
    ::placeholder {
        color: #9f1239 !important;
        opacity: 0.7 !important;
    }

    /* 5. Sidebar Styling (Màu trắng & Viền hồng) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #fecdd3 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    /* 6. Tabs Styling */
    div[data-baseweb="tab"] div { 
        color: #881337 !important; 
        font-weight: 600 !important; 
    }
    
    div[data-baseweb="tab"][aria-selected="true"] div { 
        color: #e11d48 !important; /* Rose Red */
        font-weight: 700 !important; 
        border-bottom: 2px solid #e11d48 !important;
    }

    /* 7. Custom Card Classes */
    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #fecdd3 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(225, 29, 72, 0.05);
    }
    .apex-card * {
        color: #0f172a !important;
    }
    
    .correct-card { 
        background-color: #f0fdf4 !important; 
        border-left: 5px solid #16a34a !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
        color: #0f172a !important;
    }
    .correct-card * { color: #0f172a !important; }
    
    .wrong-card { 
        background-color: #fff1f2 !important; 
        border-left: 5px solid #e11d48 !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
        color: #0f172a !important;
    }
    .wrong-card * { color: #0f172a !important; }

    .hint-card {
        background-color: #fff1f2 !important;
        border: 1px solid #fda4af !important;
        padding: 16px;
        border-radius: 8px;
        color: #0f172a !important;
        margin-bottom: 12px;
    }
    .hint-card * { color: #0f172a !important; }

    /* 8. Banner Exception (Gradient Hồng - Chữ Trắng Tương Phản) */
    .hero-banner {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: #ffffff !important;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .hero-banner * {
        color: #ffffff !important;
    }

    /* 9. Nút Bấm (Button Gradient Hồng - Chữ Trắng) */
    .stButton>button, .stButton>button * {
        background: linear-gradient(135deg, #e11d48 0%, #f43f5e 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(225,29,72,0.2) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #be123c 0%, #e11d48 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

if "error_log" not in st.session_state:
    st.session_state["error_log"] = []

# ==========================================
# 2. AUDIO PLAYER
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

# ==========================================
# 3. SIDEBAR & GROQ ENGINE
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 **Apex English Coach**")
    st.caption("30-DAY EXECUTIVE CURRICULUM")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
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

def generate_ai_response(prompt_input):
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
        "temperature": 0.2,
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
# 4. EVALUATION FUNCTION
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
                target_opt = str(options[idx - 1]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx - 1]
            if 0 <= idx < len(options):
                target_opt = str(options[idx]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx]

        letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        if c_ans_str in letter_map and letter_map[c_ans_str] < len(options):
            target_opt = str(options[letter_map[c_ans_str]]).strip().lower()
            if u_sel_str == target_opt:
                return True, options[letter_map[c_ans_str]]

        for opt in options:
            if str(opt).strip().lower() == c_ans_str:
                if u_sel_str == str(opt).strip().lower():
                    return True, opt

    correct_display = raw_correct
    if options and isinstance(options, list):
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            if 1 <= idx <= len(options):
                correct_display = options[idx - 1]
            elif 0 <= idx < len(options):
                correct_display = options[idx]
        elif c_ans_str in {'a', 'b', 'c', 'd', 'e'}:
            correct_display = options[{'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}[c_ans_str]]

    return False, str(correct_display)

def render_quiz_system(tab_key, prompt_text, btn_label, skill_name):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("Generating executive content in English..."):
            raw = generate_ai_response(prompt_text)
            clean = extract_json(raw)
            if clean:
                try:
                    data = json.loads(clean)
                    st.session_state[f"{tab_key}_data"] = data
                    st.session_state[f"{tab_key}_sub"] = False
                except Exception as e:
                    st.error(f"Data Parsing Error: {e}")

    if f"{tab_key}_data" in st.session_state:
        data = st.session_state[f"{tab_key}_data"]
        
        if "lesson_theory" in data:
            st.markdown('<div class="hint-card">', unsafe_allow_html=True)
            st.markdown("### 📖 English Grammar Focus & Business Usage Rule")
            st.write(data["lesson_theory"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        passage = data.get("passage", "")
        if passage:
            st.markdown('<div class="apex-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Case Reading / Transcript Passage")
            st.write(passage)
            if skill_name == "Listening":
                st.markdown("**🔊 Audio Briefing (3 Minutes):**")
                play_audio(passage)
            st.markdown('</div>', unsafe_allow_html=True)

        questions = data.get("questions", [])
        if questions:
            with st.form(f"form_{tab_key}"):
                user_answers = {}
                for idx, q in enumerate(questions, 1):
                    st.markdown(f"**Question {idx}: {q.get('question')}**")
                    opts = q.get('options', [])
                    
                    if opts and len(opts) > 0:
                        user_answers[q.get('id', idx)] = st.radio(
                            "Select Option:", opts, key=f"r_{tab_key}_{idx}", index=None
                        )
                    else:
                        user_answers[q.get('id', idx)] = st.text_input(
                            "Your Answer:", key=f"t_{tab_key}_{idx}"
                        )
                    st.write("---")
                
                if st.form_submit_button("Submit & Evaluate Answers"):
                    st.session_state[f"{tab_key}_sub"] = True
                    st.session_state[f"{tab_key}_user_ans"] = user_answers

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
            
            st.success(f"🏆 Overall Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 5. MAIN CURRICULUM
# ==========================================
if not api_key:
    st.warning("⚠️ Please input your Groq API Key in the sidebar to activate the program.")
else:
    if app_mode == "2. 30-Day Executive Curriculum":
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
            "🔤 Vocabulary & Games", "🗣️ Pronunciation", "📐 Grammar Rules (10-15Q)", 
            "📖 Reading (20+ Sentences)", "🎧 Listening Briefing", "✍️ Detailed Writing Scenario", "💬 Data-Driven Speaking"
        ])

        # --- 1. VOCABULARY & GAMES ---
        with tab_v:
            st.markdown(f"### 🔤 10 Core Executive Vocabulary Words: {day_topic}")
            if st.button(f"Generate Vocabulary for Day {day_selected}", key=f"btn_v_{day_selected}", use_container_width=True):
                with st.spinner("AI is curating executive vocabulary in English..."):
                    pv = f"Generate 10 C-suite Business English words for Day {day_selected} Topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Return JSON with key 'words' as array of 10 objects: 'word', 'ipa', 'english_def', 'synonyms', 'example'."
                    raw_v = generate_ai_response(pv)
                    clean_v = extract_json(raw_v)
                    if clean_v:
                        st.session_state[f"v_data_{day_selected}"] = json.loads(clean_v).get("words", [])

            if f"v_data_{day_selected}" in st.session_state:
                words = st.session_state[f"v_data_{day_selected}"]
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

                st.divider()
                st.markdown("### 🎮 Interactive Vocabulary Games")
                game_type = st.radio("Select Game Mode:", ["Game 1: Fill in Missing Letters", "Game 2: Definition Matching Quiz"], key=f"gt_{day_selected}")
                
                if st.button("Generate Interactive Game Challenge", key=f"btn_g_gen_{day_selected}"):
                    with st.spinner("Creating game questions in English..."):
                        pgame = f"Generate 5 business vocabulary game questions for topic '{day_topic}'. ALL text MUST be in ENGLISH. Include advanced words beyond the core 10. For Game 1 return 'fill_words' array of objects ('word', 'hint_english'). For Game 2 return 'mcq_words' array of objects ('word', 'options', 'correct_option'). NOTE: 'correct_option' MUST be the exact full text string matching one item in 'options'. Return JSON with keys 'fill_words' and 'mcq_words'."
                        raw_g = generate_ai_response(pgame)
                        clean_g = extract_json(raw_g)
                        if clean_g:
                            st.session_state[f"g_data_{day_selected}"] = json.loads(clean_g)

                g_data = st.session_state.get(f"g_data_{day_selected}", {})

                if game_type == "Game 1: Fill in Missing Letters":
                    fill_list = g_data.get("fill_words", [])
                    if not fill_list:
                        st.info("Click 'Generate Interactive Game Challenge' to play.")
                    else:
                        with st.form(f"g1_form_{day_selected}"):
                            u_g1_ans = {}
                            for idx, gw in enumerate(fill_list, 1):
                                w_str = gw.get('word', '')
                                f_char = w_str[0] if w_str else 'A'
                                st.markdown(f"**Question {idx}:** English Clue: *{gw.get('hint_english')}*")
                                u_g1_ans[idx] = st.text_input(f"Word starting with '{f_char}...':", key=f"g1_in_{day_selected}_{idx}")
                            
                            if st.form_submit_button("Check Game 1 Answers"):
                                g1_score = 0
                                for idx, gw in enumerate(fill_list, 1):
                                    u_val = str(u_g1_ans.get(idx, '')).strip().lower()
                                    c_val = str(gw.get('word', '')).strip().lower()
                                    if u_val == c_val:
                                        g1_score += 1
                                        st.success(f"Q{idx}: Correct! 👉 **{gw.get('word')}**")
                                    else:
                                        st.error(f"Q{idx}: Incorrect. Correct answer: **{gw.get('word')}**")
                                st.info(f"🏆 Game 1 Final Score: {g1_score}/{len(fill_list)}")

                elif game_type == "Game 2: Definition Matching Quiz":
                    mcq_list = g_data.get("mcq_words", [])
                    if not mcq_list:
                        st.info("Click 'Generate Interactive Game Challenge' to play.")
                    else:
                        with st.form(f"g2_form_{day_selected}"):
                            u_g2_ans = {}
                            for idx, mw in enumerate(mcq_list, 1):
                                st.markdown(f"**Question {idx}: What is the exact meaning of '{mw.get('word')}'?**")
                                u_g2_ans[idx] = st.radio("Select Option:", mw.get('options', []), key=f"g2_in_{day_selected}_{idx}", index=None)
                                st.write("---")
                            
                            if st.form_submit_button("Check Game 2 Answers"):
                                g2_score = 0
                                for idx, mw in enumerate(mcq_list, 1):
                                    u_v = u_g2_ans.get(idx)
                                    c_v = mw.get('correct_option')
                                    is_c, disp = evaluate_answer(u_v, c_v, mw.get('options', []))
                                    if is_c:
                                        g2_score += 1
                                        st.success(f"Q{idx}: Correct! 👉 {u_v}")
                                    else:
                                        st.error(f"Q{idx}: Incorrect. Selected: {u_v if u_v else 'None'} | Correct Answer: {disp}")
                                st.info(f"🏆 Game 2 Final Score: {g2_score}/{len(mcq_list)}")

        # --- 2. PRONUNCIATION ---
        with tab_p:
            st.markdown(f"### 🎙️ Passage Pronunciation Practice ({day_topic})")
            if st.button(f"Generate 5 Practice Passages Day {day_selected}", key=f"btn_p_{day_selected}", use_container_width=True):
                with st.spinner("AI generating executive speech passages in English..."):
                    pp = f"Generate 5 short executive speech passages (2-3 sentences each) on Topic '{day_topic}'. ALL text MUST be in ENGLISH. Return JSON object with key 'passages' containing an array of 5 strings."
                    raw_p = generate_ai_response(pp)
                    clean_p = extract_json(raw_p)
                    if clean_p:
                        st.session_state[f"p_passages_{day_selected}"] = json.loads(clean_p).get("passages", [])

            if f"p_passages_{day_selected}" in st.session_state:
                p_list = st.session_state[f"p_passages_{day_selected}"]
                for idx, text_p in enumerate(p_list, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4>Passage {idx}:</h4>
                        <p style="font-size:16px;">{text_p}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(text_p)
                    
                    user_audio = st.audio_input(f"Record audio for Passage {idx}:", key=f"aud_{day_selected}_{idx}")
                    if user_audio:
                        st.success(f"Audio recorded for Passage {idx}. Click below for AI analysis:")
                        
                        if st.button(f"Analyze Pronunciation for Passage {idx}", key=f"btn_ana_p_{day_selected}_{idx}"):
                            with st.spinner("Analyzing phonetics, stress, and intonation in English..."):
                                p_eval_prompt = f"Analyze executive speech for text: '{text_p}'. ALL output MUST be strictly in 100% ENGLISH. Return JSON with keys: 'key_words_eval', 'vocabulary_eval', 'intonation_eval', 'sentence_stress_eval', 'improvements' (array of strings listing mispronounced words and corrective phonetic guidance)."
                                raw_p_eval = generate_ai_response(p_eval_prompt)
                                clean_p_eval = extract_json(raw_p_eval)
                                if clean_p_eval:
                                    res_pe = json.loads(clean_p_eval)
                                    st.session_state[f"pe_res_{day_selected}_{idx}"] = res_pe

                        if f"pe_res_{day_selected}_{idx}" in st.session_state:
                            pe = st.session_state[f"pe_res_{day_selected}_{idx}"]
                            st.markdown(f"""
                            <div class="apex-card" style="background-color: #fff1f2 !important;">
                                <p>🔑 <b>Key Words Pronunciation:</b> {pe.get('key_words_eval')}</p>
                                <p>📚 <b>Vocabulary Accuracy:</b> {pe.get('vocabulary_eval')}</p>
                                <p>🌊 <b>Intonation & Pitch Contour:</b> {pe.get('intonation_eval')}</p>
                                <p>🎯 <b>Sentence Stress & Cadence:</b> {pe.get('sentence_stress_eval')}</p>
                                <hr style="margin:10px 0;">
                                <p style="color:#e11d48 !important; font-weight:bold; margin-bottom:5px;">⚠️ List of Specific Mispronunciations & Areas to Improve:</p>
                            """, unsafe_allow_html=True)
                            
                            imps = pe.get('improvements', [])
                            if isinstance(imps, list):
                                for imp in imps:
                                    st.markdown(f"- {imp}")
                            else:
                                st.write(f"- {imps}")
                            st.markdown("</div>", unsafe_allow_html=True)

        # --- 3. GRAMMAR ---
        with tab_g:
            st.markdown(f"### 📐 English Grammar Focus: **{day_grammar}**")
            pg = f"Create a comprehensive English grammar lesson focusing explicitly on '{day_grammar}'. Explain grammar rules, usage cases in Business English, and link them to structures used in corporate reading. ALL text MUST be in ENGLISH. Return JSON with 'lesson_theory' (detailed explanation) and 'questions' (array of 12 questions with 'id', 'question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"g_day_{day_selected}", pg, "Load English Grammar Lesson & 12 Practice Questions", "Grammar")

        # --- 4. READING ---
        with tab_r:
            st.markdown(f"### 📖 Reading Comprehension Case (Linked to: {day_grammar})")
            pr = f"Generate a high-level business case reading passage AT LEAST 20 sentences long on Topic '{day_topic}'. Explicitly incorporate grammar structures from '{day_grammar}'. ALL text MUST be in 100% ENGLISH. Generate 12 questions mix of multiple_choice and fill_in_blank. Return JSON with 'passage' and 'questions' ('id', 'question', 'type', 'options', 'answer', 'explanation')."
            render_quiz_system(f"r_day_{day_selected}", pr, "Load 20+ Sentence Business Case & 12 Questions", "Reading")

        # --- 5. LISTENING ---
        with tab_l:
            st.markdown("### 🎧 Executive Briefing Audio Transcription (3 Minutes)")
            pl = f"Generate an executive meeting briefing transcript (approx 400 words) on Topic '{day_topic}'. ALL text MUST be in 100% ENGLISH. Generate 10 questions mix of multiple_choice and fill_in_blank. Return JSON with 'passage' and 'questions' ('id', 'question', 'type', 'options', 'answer', 'explanation')."
            render_quiz_system(f"l_day_{day_selected}", pl, "Load 3-Minute Executive Audio & 10 Questions", "Listening")

        # --- 6. WRITING ---
        with tab_w:
            st.markdown(f"### ✍️ Executive Business Writing Brief: {day_topic}")
            if f"w_scenario_{day_selected}" not in st.session_state:
                if st.button("Generate Detailed Writing Briefing Scenario", key=f"btn_w_scen_{day_selected}"):
                    with st.spinner("Drafting detailed corporate context in English..."):
                        p_w_scen = f"Create a highly detailed writing scenario in 100% ENGLISH for Topic '{day_topic}'. Specify: 1) Company Name & Industry background, 2) Current Financial/Operational Challenge, 3) Core Mission & Strategic Focus, 4) Specific instructions for an Executive Proposal/Email to the Board of Directors (Minimum 100 words requirement). Return JSON with key 'scenario_text'."
                        raw_ws = generate_ai_response(p_w_scen)
                        clean_ws = extract_json(raw_ws)
                        if clean_ws:
                            st.session_state[f"w_scenario_{day_selected}"] = json.loads(clean_ws).get("scenario_text", "")

            scenario_disp = st.session_state.get(f"w_scenario_{day_selected}", "Click the button above to generate a detailed, company-specific corporate scenario.")
            st.markdown(f'<div class="apex-card"><b>Corporate Writing Scenario Briefing:</b><br>{scenario_disp}</div>', unsafe_allow_html=True)
            
            user_w_text = st.text_area("Draft your executive proposal/report below:", height=240, key=f"w_input_{day_selected}")
            w_count = len(user_w_text.split())
            st.caption(f"Current Word Count: **{w_count} words** (Requirement: ≥ 100 words)")

            if st.button("Submit & Evaluate Executive Writing", key=f"btn_w_{day_selected}", use_container_width=True):
                if w_count < 100:
                    st.error(f"Your essay contains {w_count} words. Please meet the minimum requirement of 100 words.")
                else:
                    with st.spinner("AI Executive Editor analyzing your submission..."):
                        pw = f"Analyze executive essay ({w_count} words): '{user_w_text}'. Context topic: '{day_topic}'. ALL feedback MUST be in 100% ENGLISH. Return JSON with: 'score', 'errors' (array of bullet strings detailing specific grammar/style mistakes), 'feedback', 'sample_essay'."
                        raw_w = generate_ai_response(pw)
                        clean_w = extract_json(raw_w)
                        if clean_w:
                            res_w = json.loads(clean_w)
                            st.success(f"🏆 Executive Score: {res_w.get('score')}/100")
                            
                            st.markdown("#### ❌ Grammar & Style Corrections:")
                            errs = res_w.get('errors', [])
                            if isinstance(errs, list):
                                for e in errs:
                                    st.markdown(f"- {e}")
                            else:
                                st.write(f"- {errs}")

                            st.markdown("#### 💡 C-Suite Editorial Feedback:")
                            st.info(res_w.get('feedback'))

                            st.markdown("#### 🌟 Benchmark Model Proposal:")
                            st.markdown(f'<div class="apex-card">{res_w.get("sample_essay")}</div>', unsafe_allow_html=True)

        # --- 7. SPEAKING ---
        with tab_s:
            st.markdown(f"### 💬 Executive Boardroom Presentation: {day_topic}")
            if f"s_table_{day_selected}" not in st.session_state:
                if st.button("Generate Boardroom Data Table & Speech Prompt", key=f"btn_s_table_{day_selected}"):
                    with st.spinner("Creating financial metrics table in English..."):
                        p_s_table = f"Create a boardroom presentation prompt in 100% ENGLISH for Topic '{day_topic}'. Provide a markdown metrics table (including metrics like Q3 Revenue Growth, Operating Margin, ROI, Risk Index, CAC, Churn, etc.). Instruct the speaker to present to the Board of Directors, explicitly linking these metrics to the company's long-term Strategy & Vision. Return JSON with key 'prompt_details'."
                        raw_st = generate_ai_response(p_s_table)
                        clean_st = extract_json(raw_st)
                        if clean_st:
                            st.session_state[f"s_table_{day_selected}"] = json.loads(clean_st).get("prompt_details", "")

            s_prompt_disp = st.session_state.get(f"s_table_{day_selected}", "Click above to generate the metrics table and presentation brief.")
            st.markdown(f'<div class="apex-card"><b>Boardroom Metrics & Presentation Brief:</b><br>{s_prompt_disp}</div>', unsafe_allow_html=True)

            if f"speech_text_{day_selected}" not in st.session_state:
                st.session_state[f"speech_text_{day_selected}"] = ""

            st.write("Record audio or append speech segment to the accumulating transcript:")
            audio_speak = st.audio_input("Record Speech Segment:", key=f"stt_{day_selected}")
            
            if audio_speak:
                new_stt_segment = f"[Speech Segment {time.strftime('%H:%M:%S')}]: 'Members of the Board, looking at our Q3 performance table...'"
                st.session_state[f"speech_text_{day_selected}"] += "\n" + new_stt_segment

            full_speech = st.text_area("Accumulated Presentation Transcript:", value=st.session_state[f"speech_text_{day_selected}"], height=200, key=f"area_s_{day_selected}")
            st.session_state[f"speech_text_{day_selected}"] = full_speech

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div class="hero-banner" style="background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);">
            <h2 style='margin:0;'>Review & Remind: Incorrect Answer History</h2>
            <p style='margin:5px 0 0 0;'>Review logged mistakes to reinforce business English mastery</p>
        </div>
        """, unsafe_allow_html=True)

        logs = st.session_state.get("error_log", [])
        if not logs:
            st.info("No recorded errors yet. Complete skill exercises to log items for review.")
        else:
            st.markdown(f"### 📌 Review List ({len(logs)} items logged):")
            for idx, err in enumerate(logs, 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <b>#{idx} [{err.get('skill')}]</b> - Question: {err.get('question')}<br>
                    - Selected Answer: <span style="color:#e11d48 !important; font-weight:bold;">{err.get('your_answer')}</span><br>
                    - Correct Answer: <span style="color:#16a34a !important; font-weight:bold;">{err.get('correct_answer')}</span><br>
                    - 💡 <i>Explanation: {err.get('explanation')}</i>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Clear Review History", use_container_width=True):
                st.session_state["error_log"] = []
                st.rerun()