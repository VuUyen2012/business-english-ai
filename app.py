import streamlit as st
import requests
import json
import re
import time
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & OVERRIDE ALL DARK/BLACK ELEMENTS
# ==========================================
st.set_page_config(
    page_title="Apex English - 30-Day Executive Coaching",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force hoàn toàn nền Trắng / Hồng nhạt & Chữ Đen trên TẤT CẢ các component (Kể cả JSON/Code viewer)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. Global Reset & Background (Nền hồng phấn nhạt) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #fff1f2 !important; /* Hồng nhạt */
        color: #0f172a !important; /* Chữ đen đậm */
    }

    /* 2. ÉP TẤT CẢ CHỮ VỀ MÀU ĐEN / TỐI */
    *, p, span, h1, h2, h3, h4, h5, h6, li, label, div {
        color: #0f172a !important;
    }

    /* 3. TRIỆT BỎ NỀN ĐEN Ở JSON VIEWER & CODE BLOCKS */
    div[data-testid="stJson"], 
    div[data-testid="stJson"] *, 
    pre, code, 
    [data-testid="stMarkdownContainer"] code,
    .stCodeBlock,
    [data-baseweb="tree-node"] {
        background-color: #ffe4e6 !important; /* Nền hồng pastel nhạt */
        color: #0f172a !important; /* Chữ đen/đỏ đô đậm */
        border: 1px solid #fda4af !important;
        border-radius: 8px !important;
        font-family: 'Inter', monospace !important;
        font-weight: 600 !important;
    }

    /* 4. Fix các Input, Textarea, Selectbox (Tránh bị đen/tối) */
    input, textarea, select, 
    [data-baseweb="input"],
    [data-baseweb="input"] input, 
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"],
    [data-baseweb="select"] * {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #fda4af !important;
        border-radius: 6px !important;
    }
    
    ::placeholder {
        color: #9f1239 !important;
        opacity: 0.6 !important;
    }

    /* 5. Sidebar (Nền trắng, viền hồng nhạt) */
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] {
        border-right: 2px solid #fecdd3 !important;
    }

    /* 6. Tabs (Nhãn tab hồng đậm/đỏ) */
    div[data-baseweb="tab"] div { 
        color: #881337 !important; 
        font-weight: 600 !important; 
    }
    div[data-baseweb="tab"][aria-selected="true"] div { 
        color: #e11d48 !important; 
        font-weight: 700 !important; 
        border-bottom: 3px solid #e11d48 !important;
    }

    /* 7. Custom Cards (Chắc chắn Nền Trắng/Hồng - Chữ Đen) */
    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #fecdd3 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
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

    /* 8. Hero Banner (Nền Hồng Đậm - Chữ Trắng Tương Phản) */
    .hero-banner {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .hero-banner h2, .hero-banner p, .hero-banner b {
        color: #ffffff !important;
    }

    /* 9. Nút bấm Button */
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

# Hàm render nội dung Lý thuyết/Theory dạng Markdown
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
# 4. EVALUATION & QUIZ SYSTEM
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
            render_formatted_theory(data["lesson_theory"])
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
                        <p style="margin:4px 0;"><b>Synonyms:</b> <code style="background-color:#ffe4e6 !important; color:#0f172a !important;">{w.get('synonyms')}</code></p>
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

        # --- 6. WRITING & EVALUATION ---
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

            st.markdown(f"#### 📝 Draft Your Executive Writing Response (Target Grammar: *{day_grammar}*)")
            user_writing = st.text_area("Type your C-suite proposal / email response here:", height=220, key=f"txt_w_{day_selected}")

            if user_writing:
                word_count = len(user_writing.split())
                st.caption(f"📊 Current Word Count: **{word_count} words** (Recommended: 100+ words)")

            if st.button("Evaluate Writing & Detailed Line-by-Line Corrections", key=f"btn_w_eval_{day_selected}", use_container_width=True):
                if not user_writing or len(user_writing.strip()) < 15:
                    st.warning("⚠️ Please draft a substantial writing response (at least 15 words) before submitting for evaluation.")
                else:
                    with st.spinner("AI Executive Coach is identifying specific mistakes, revising line-by-line, and evaluating C-suite tone..."):
                        p_w_eval = f"""
                        Perform an in-depth line-by-line correction and C-suite assessment of the following user submission.
                        ALL feedback MUST be strictly in 100% ENGLISH.
                        
                        Scenario context: {scenario_disp}
                        Target Grammar focus: {day_grammar}
                        User Submission: "{user_writing}"

                        Return a JSON object with keys:
                        - 'overall_score': (integer from 0 to 100)
                        - 'executive_summary': (short overall critique)
                        - 'grammar_vocabulary_score': (score out of 100 and brief comments)
                        - 'structure_cohesion_score': (score out of 100 and brief comments)
                        - 'tone_style_score': (score out of 100 and brief comments)
                        - 'line_corrections': (array of objects for EVERY error/suboptimal phrasing in the user text:
                            [
                              {{
                                "original_phrase": "exact word or phrase from user text",
                                "corrected_phrase": "corrected version",
                                "error_type": "Grammar / Word Choice / Tone / Punctuation",
                                "explanation": "Detailed explanation of why it was wrong and the rule behind the fix."
                              }}
                            ]
                          )
                        - 'suggested_rewrite': (a polished, high-level executive C1/C2 model answer based on the user's ideas)
                        - 'actionable_improvements': (array of strings with specific actionable strategic writing advice)
                        """
                        raw_we = generate_ai_response(p_w_eval)
                        clean_we = extract_json(raw_we)
                        if clean_we:
                            try:
                                st.session_state[f"w_eval_res_{day_selected}"] = json.loads(clean_we)
                            except Exception as e:
                                st.error(f"Error parsing evaluation response: {e}")

            if f"w_eval_res_{day_selected}" in st.session_state:
                w_res = st.session_state[f"w_eval_res_{day_selected}"]
                st.divider()
                st.markdown("### 📊 Executive Writing Feedback & Scoring Dashboard")
                
                score_val = w_res.get('overall_score', 0)
                st.success(f"🏆 **Overall Writing Score: {score_val} / 100**")
                
                st.markdown(f'<div class="hint-card"><b>Executive Critique:</b> {w_res.get("executive_summary")}</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="apex-card">
                        <h5>📐 Grammar & Vocab</h5>
                        <p>{w_res.get('grammar_vocabulary_score')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="apex-card">
                        <h5>🧩 Structure & Logic</h5>
                        <p>{w_res.get('structure_cohesion_score')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="apex-card">
                        <h5>💼 C-Suite Tone</h5>
                        <p>{w_res.get('tone_style_score')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### 🛠️ Detailed Line-by-Line Corrections (Specific Error Analysis)")
                corrections = w_res.get("line_corrections", [])
                
                if not corrections or len(corrections) == 0:
                    st.info("🎉 Excellent work! No significant grammatical errors or tone issues were detected in your text.")
                else:
                    for idx, err in enumerate(corrections, 1):
                        st.markdown(f"""
                        <div class="wrong-card">
                            <span style="background-color:#e11d48; color:white !important; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:12px;">Issue #{idx} - {err.get('error_type', 'Correction')}</span><br><br>
                            ❌ <b>Original Text:</b> <span style="text-decoration: line-through; color:#be123c !important;">"{err.get('original_phrase')}"</span><br>
                            ✅ <b>Correction:</b> <b style="color:#16a34a !important;">"{err.get('corrected_phrase')}"</b><br>
                            💡 <b>Why & How to Fix:</b> {err.get('explanation')}
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="correct-card" style="margin-top:20px;">
                    <h4 style="color:#16a34a !important; margin-top:0;">✨ Optimized Executive C-Suite Version (Model Answer):</h4>
                    <p style="font-size:15px; font-style:italic;">"{w_res.get('suggested_rewrite')}"</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### 🎯 Key Actionable Recommendations:")
                tips = w_res.get('actionable_improvements', [])
                if isinstance(tips, list):
                    for tip in tips:
                        st.markdown(f"- {tip}")
                else:
                    st.write(f"- {tips}")

        # --- 7. SPEAKING (CẬP NHẬT HOÀN CHỈNH TÍNH NĂNG SPEAKING & SPEECH-TO-TEXT & CHẤM ĐIỂM) ---
        with tab_s:
            st.markdown(f"### 💬 Data-Driven Speaking Briefing: {day_topic}")
            st.caption(f"🎯 Targeted Grammar Focus: **{day_grammar}**")

            # 1. TẠO CHỦ ĐỀ VÀ TÌNH HUỐNG NÓI (SPEAKING PROMPT / SCENARIO)
            if f"s_prompt_{day_selected}" not in st.session_state:
                if st.button("Generate Executive Speaking Prompt & Questions", key=f"btn_s_gen_{day_selected}", use_container_width=True):
                    with st.spinner("Preparing executive board presentation challenge in English..."):
                        p_s_gen = f"""
                        Generate an executive-level C-Suite Speaking Briefing for Day {day_selected} Topic '{day_topic}'.
                        Grammar focus: '{day_grammar}'.
                        ALL text MUST be strictly in 100% ENGLISH.
                        
                        Return JSON object with keys:
                        - 'presentation_context': (A realistic corporate briefing/board meeting scenario, 2-3 sentences)
                        - 'key_questions': (An array of 3 strategic questions the executive must answer aloud)
                        - 'expected_key_terms': (An array of 5 C-suite key vocabulary terms to use in the speech)
                        """
                        raw_sp = generate_ai_response(p_s_gen)
                        clean_sp = extract_json(raw_sp)
                        if clean_sp:
                            try:
                                st.session_state[f"s_prompt_{day_selected}"] = json.loads(clean_sp)
                            except Exception as e:
                                st.error(f"Error loading speaking prompt: {e}")

            s_data = st.session_state.get(f"s_prompt_{day_selected}", None)

            if s_data:
                st.markdown(f"""
                <div class="apex-card">
                    <h4 style="color:#e11d48 !important; margin-top:0;">📋 Executive Board Presentation Scenario</h4>
                    <p style="font-size:15px;">{s_data.get('presentation_context')}</p>
                    <hr style="margin:12px 0; border:0; border-top:1px solid #fecdd3;">
                    <b>🎯 Strategic Questions to Address:</b>
                """, unsafe_allow_html=True)

                for q_idx, q_item in enumerate(s_data.get('key_questions', []), 1):
                    st.markdown(f"- **Q{q_idx}:** {q_item}")

                st.markdown("<br><b>💡 Recommended Key Vocabulary:</b>", unsafe_allow_html=True)
                st.markdown(", ".join([f"`{term}`" for term in s_data.get('expected_key_terms', [])]))
                st.markdown("</div>", unsafe_allow_html=True)

                st.divider()

                # 2. BỘ THU ÂM (AUDIO RECORDING) & THỦ CÔNG / TỰ ĐỘNG STT
                st.markdown("#### 🎙️ Record Your Executive Response & Speech-to-Text")
                col_rec, col_stt = st.columns([1, 1])

                with col_rec:
                    st.markdown("**1. Record Audio Response:**")
                    speaking_audio = st.audio_input("Record your answer:", key=f"aud_speaking_{day_selected}")
                    if speaking_audio:
                        st.success("✅ Audio recorded successfully!")

                with col_stt:
                    st.markdown("**2. Transcribed Speech Text (STT):**")
                    st.caption("Review or adjust your transcribed response below before AI scoring:")
                    user_stt_text = st.text_area(
                        "Transcript of your spoken response:",
                        placeholder="Type or paste your transcribed speech here if audio isn't transcribed automatically...",
                        height=120,
                        key=f"txt_stt_{day_selected}"
                    )

                # 3. CHẤM ĐIỂM SPEAKING & ĐÁNH GIÁ CHI TIẾT (EVALUATION & SCORING)
                if st.button("Evaluate Executive Speaking & Deliver Feedback", key=f"btn_s_eval_{day_selected}", use_container_width=True):
                    if not user_stt_text or len(user_stt_text.strip()) < 10:
                        st.warning("⚠️ Please provide a transcript or text of your spoken response (at least 10 words) to evaluate.")
                    else:
                        with st.spinner("AI Coach is analyzing fluency, C-suite tone, structure, and grammar..."):
                            p_s_eval = f"""
                            Perform a rigorous C-suite Executive Speaking Evaluation on the following speech transcript.
                            ALL output MUST be strictly in 100% ENGLISH.

                            Scenario context: {s_data.get('presentation_context')}
                            Target Grammar focus: {day_grammar}
                            Expected Key Terms: {", ".join(s_data.get('expected_key_terms', []))}
                            User Spoken Transcript: "{user_stt_text}"

                            Return JSON with keys:
                            - 'overall_score': (integer 0 to 100)
                            - 'fluency_delivery_score': (score out of 100 with brief notes)
                            - 'vocabulary_precision_score': (score out of 100 with brief notes)
                            - 'grammar_accuracy_score': (score out of 100 with brief notes)
                            - 'executive_impact_score': (score out of 100 with brief notes)
                            - 'strengths': (array of strings highlighting strong points)
                            - 'key_improvements': (array of strings with specific actionable suggestions)
                            - 'model_speech': (A highly refined, C-level executive polished response)
                            """
                            raw_se = generate_ai_response(p_s_eval)
                            clean_se = extract_json(raw_se)
                            if clean_se:
                                try:
                                    st.session_state[f"s_eval_res_{day_selected}"] = json.loads(clean_se)
                                except Exception as e:
                                    st.error(f"Error parsing speaking evaluation: {e}")

                if f"s_eval_res_{day_selected}" in st.session_state:
                    se_res = st.session_state[f"s_eval_res_{day_selected}"]
                    st.divider()
                    st.markdown("### 📊 Executive Speaking Performance Scorecard")

                    st.success(f"🏆 **Overall Speaking Score: {se_res.get('overall_score', 0)} / 100**")

                    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
                    with s_col1:
                        st.markdown(f"""
                        <div class="apex-card">
                            <h5>🗣️ Delivery</h5>
                            <p>{se_res.get('fluency_delivery_score')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with s_col2:
                        st.markdown(f"""
                        <div class="apex-card">
                            <h5>📚 Vocabulary</h5>
                            <p>{se_res.get('vocabulary_precision_score')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with s_col3:
                        st.markdown(f"""
                        <div class="apex-card">
                            <h5>📐 Grammar</h5>
                            <p>{se_res.get('grammar_accuracy_score')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with s_col4:
                        st.markdown(f"""
                        <div class="apex-card">
                            <h5>💼 Impact</h5>
                            <p>{se_res.get('executive_impact_score')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("#### 💪 Key Strengths:")
                    for st_item in se_res.get("strengths", []):
                        st.markdown(f"- ✅ {st_item}")

                    st.markdown("#### 🎯 Areas for Improvement:")
                    for imp_item in se_res.get("key_improvements", []):
                        st.markdown(f"- ⚠️ {imp_item}")

                    st.markdown(f"""
                    <div class="correct-card" style="margin-top:15px;">
                        <h4 style="color:#16a34a !important; margin-top:0;">🌟 Benchmark C-Suite Model Delivery:</h4>
                        <p style="font-size:15px; font-style:italic;">"{se_res.get('model_speech')}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(se_res.get('model_speech', ''))
            else:
                st.info("Click **'Generate Executive Speaking Prompt & Questions'** above to initialize today's speaking scenario.")

    elif app_mode == "1. Comprehensive Diagnostic Assessment":
        st.markdown("### 📋 Diagnostic Assessment Mode")
        st.write("Complete this assessment to determine your baseline proficiency.")

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("### 📑 Executive Error Log & Space Repetition Review")
        if not st.session_state["error_log"]:
            st.info("🎉 No incorrect answers logged yet. Keep practicing!")
        else:
            for idx, err in enumerate(st.session_state["error_log"], 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <b>[{err.get('skill')}] Entry #{idx}:</b> {err.get('question')}<br>
                    ❌ <b>Your Selection:</b> {err.get('your_answer')}<br>
                    ✅ <b>Correct Answer:</b> {err.get('correct_answer')}<br>
                    💡 <b>Explanation:</b> {err.get('explanation')}
                </div>
                """, unsafe_allow_html=True)