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
    """Trích xuất toàn bộ dữ liệu hợp lệ để lưu trữ JSON (tránh lỗi Unserializable)."""
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
# 2. AUDIO PLAYER & SPEECH RECORDING HELPERS
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

def render_speech_recorder_stt(key_prefix):
    """Tạo bộ thu âm Live Microphone & Speech-to-Text trực tiếp bằng JS Engine."""
    html_code = f"""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1.5px solid #fda4af; font-family: sans-serif;">
        <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
            <button id="start_btn_{key_prefix}" onclick="startDictation()" style="background-color: #e11d48; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                🎙️ Start Recording
            </button>
            <button id="stop_btn_{key_prefix}" onclick="stopDictation()" style="background-color: #475569; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold;" disabled>
                ⏹️ Stop
            </button>
            <span id="status_{key_prefix}" style="color: #be123c; font-weight: 500; font-size: 14px;">Status: Ready</span>
        </div>
        <p style="font-size: 12px; color: #64748b; margin: 0 0 5px 0;">Live Speech-to-Text Transcript (Copy below to edit if needed):</p>
        <textarea id="transcript_box_{key_prefix}" rows="4" style="width: 100%; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; font-size: 14px; box-sizing: border-box;" placeholder="Your spoken text will appear here..."></textarea>
    </div>

    <script>
        var recognition;
        function startDictation() {{
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = function() {{
                    document.getElementById('status_{key_prefix}').innerText = 'Status: Listening... Speak clearly into your mic.';
                    document.getElementById('start_btn_{key_prefix}').disabled = true;
                    document.getElementById('stop_btn_{key_prefix}').disabled = false;
                }};

                recognition.onresult = function(event) {{
                    var final_transcript = '';
                    for (var i = event.resultIndex; i < event.results.length; ++i) {{
                        if (event.results[i].isFinal) {{
                            final_transcript += event.results[i][0].transcript + ' ';
                        }}
                    }}
                    if (final_transcript) {{
                        var textarea = document.getElementById('transcript_box_{key_prefix}');
                        textarea.value += final_transcript;
                    }}
                }};

                recognition.onerror = function(event) {{
                    document.getElementById('status_{key_prefix}').innerText = 'Error: ' + event.error;
                }};

                recognition.onend = function() {{
                    document.getElementById('status_{key_prefix}').innerText = 'Status: Stopped recording.';
                    document.getElementById('start_btn_{key_prefix}').disabled = false;
                    document.getElementById('stop_btn_{key_prefix}').disabled = true;
                }};

                recognition.start();
            }} else {{
                alert('Speech Recognition is not supported in this browser. Please use Google Chrome.');
            }}
        }}

        function stopDictation() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
    """
    components.html(html_code, height=210)

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
# 4. EVALUATION & QUIZ SYSTEM WITH PERSISTENCE (SUPPORT MULTI-QUESTION TYPES)
# ==========================================
def evaluate_answer(user_selection, raw_correct, options):
    """Hàm so sánh câu trả lời thông minh, hỗ trợ cả MCQ, Fill-in-the-blank và T/F/NG."""
    if user_selection is None:
        return False, str(raw_correct)

    u_sel_str = str(user_selection).strip().lower()
    c_ans_str = str(raw_correct).strip().lower() if raw_correct is not None else ""

    # So sánh trực tiếp chuỗi đã chuẩn hóa
    if u_sel_str == c_ans_str and u_sel_str != "":
        return True, str(user_selection)

    # Nếu có danh sách tùy chọn (MCQ hoặc T/F/NG)
    if options and isinstance(options, list) and len(options) > 0:
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
    if options and isinstance(options, list) and len(options) > 0:
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            if 1 <= idx <= len(options): correct_display = options[idx - 1]
            elif 0 <= idx < len(options): correct_display = options[idx]
        elif c_ans_str in {'a', 'b', 'c', 'd', 'e'} and len(options) > {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}[c_ans_str]:
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
            st.markdown("### 📄 Case Reading / Strategic Executive Report")
            st.write(passage)
            if skill_name == "Listening":
                st.markdown("**🔊 Audio Briefing:**")
                play_audio(passage)
            st.markdown('</div>', unsafe_allow_html=True)

        questions = data.get("questions", [])
        if questions:
            for idx, q in enumerate(questions, 1):
                q_type = q.get('type', 'multiple_choice')
                q_title = f"Question {idx} [{q_type.replace('_', ' ').title()}]: {q.get('question')}"
                st.markdown(f"**{q_title}**")
                
                opts = q.get('options', [])
                key_input = f"q_{tab_key}_{idx}"
                
                # Hiển thị linh hoạt theo thể loại câu hỏi
                if opts and len(opts) > 0:
                    if key_input not in st.session_state:
                        st.session_state[key_input] = opts[0]
                    current_val = st.session_state[key_input]
                    opt_idx = opts.index(current_val) if current_val in opts else 0
                    st.radio("Select your answer:", opts, index=opt_idx, key=key_input)
                else:
                    if key_input not in st.session_state:
                        st.session_state[key_input] = ""
                    st.text_input("Type your answer:", value=st.session_state.get(key_input, ""), key=key_input)
                
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
                
                raw_correct = q.get('correct_answer') if 'correct_answer' in q else q.get('answer')
                opts = q.get('options', [])
                
                is_correct, display_correct = evaluate_answer(ans, raw_correct, opts)
                
                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Selected: <b>{ans}</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{ans if ans else "Not Selected"}</b> | Correct: <b>{display_correct}</b><br>💡 <i>Explanation: {q.get("explanation", "Review the reading passage for full context.")}</i></div>', unsafe_allow_html=True)
                    
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
    # --- MODULE 1: FULL DIAGNOSTIC ASSESSMENT ---
    if app_mode == "1. Comprehensive Diagnostic Assessment":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Comprehensive Executive Diagnostic Assessment</h2>
            <p style='margin:5px 0 0 0;'>Evaluate baseline proficiency across 4 core C-Suite Executive Skills: Grammar & Vocabulary, Reading, Writing, and Speaking.</p>
        </div>
        """, unsafe_allow_html=True)
        
        diag_tabs = st.tabs(["📝 Grammar & Vocabulary (MCQ)", "📖 Reading Comprehension", "✍️ Executive Writing Assessment", "🎙️ Executive Speaking Assessment"])
        
        # Tab 1: MCQ Grammar & Vocab
        with diag_tabs[0]:
            pdia = """Generate a full baseline Executive English Assessment test for Grammar & Vocabulary. 
            Return JSON with key 'questions' containing 10 Multiple Choice Questions. 
            Each question MUST have 'id', 'question', 'options' (array of 4 options), 'correct_answer' (exact full string of correct option), and 'explanation'."""
            render_quiz_system("diag_mcq", pdia, "Start Grammar & Vocab Assessment", "Diagnostic", seed_key="diag_mcq_test")

        # Tab 2: Diagnostic Reading Assessment (Cập nhật tiêu chuẩn độ dài & dạng câu hỏi)
        with diag_tabs[1]:
            pdia_r = """Generate an advanced C1/C2 executive reading diagnostic test.
            Return JSON with keys:
            - 'passage': A high-level strategic executive report or business case analysis of AT LEAST 20 SENTENCES long. Separate into 3-4 structured paragraphs.
            - 'questions': An array of 7 questions with multiple types:
               1. Multiple Choice Questions (type: 'multiple_choice', array of 4 options)
               2. Fill in the blank (type: 'fill_in_the_blank', options: [])
               3. True/False/Not Given (type: 'true_false_ng', options: ['True', 'False', 'Not Given'])
            Each question MUST contain: 'id', 'type', 'question', 'options', 'correct_answer' (exact full string or exact word), and 'explanation'."""
            render_quiz_system("diag_reading", pdia_r, "Start Reading Assessment", "Diagnostic Reading", seed_key="diag_read_test")

        # Tab 3: Writing Assessment
        with diag_tabs[2]:
            st.markdown("### ✍️ Baseline Executive Writing Task")
            st.markdown("""
            **Prompt:** Write a formal executive email (at least 100 words) to your Board of Directors proposing a key strategic pivot due to changing market conditions.
            """)
            diag_w_input = st.text_area("Draft your executive proposal here:", height=180, key="diag_writing_input")
            
            if st.button("Evaluate Writing Baseline", key="btn_eval_diag_writing"):
                if len(diag_w_input.strip().split()) < 30:
                    st.warning("Please enter a comprehensive response (at least 30-100 words) to evaluate.")
                else:
                    eval_p = f"""Evaluate this executive writing baseline draft:
                    "{diag_w_input}"
                    Return JSON with keys:
                    'cefr_level': estimated level (e.g., B2, C1),
                    'score': score out of 10,
                    'errors': array of objects ('original', 'corrected', 'reason'),
                    'c1_benchmark': 'A full model C1/C2 executive rewrite of the response.'"""
                    
                    with st.spinner("Analyzing executive writing baseline..."):
                        res_raw = generate_ai_response(eval_p)
                        res_json = json.loads(extract_json(res_raw))
                        
                        st.markdown(f"### 🏆 Level Assessment: **{res_json.get('cefr_level')}** (Score: {res_json.get('score')}/10)")
                        
                        st.markdown("#### ❌ Identified Errors & Corrections:")
                        for err in res_json.get('errors', []):
                            st.markdown(f"- ❌ *\"{err.get('original')}\"* ➔ ✅ **\"{err.get('corrected')}\"** ({err.get('reason')})")
                        
                        st.markdown("#### ✨ Standard C1/C2 Executive Benchmark Rewrite:")
                        st.info(res_json.get('c1_benchmark'))

        # Tab 4: Speaking Assessment
        with diag_tabs[3]:
            st.markdown("### 🎙️ Baseline Executive Speaking Task")
            st.markdown("**Prompt:** Describe a major business crisis you managed or an operational change you led. Speak clearly into your mic.")
            
            render_speech_recorder_stt("diag_spk")
            st.caption("Copy your transcript or type your spoken response into the text box below for AI evaluation:")
            spk_text = st.text_area("Your Spoken Response Text:", height=100, key="diag_spk_text_input")
            
            if st.button("Evaluate Speaking Baseline", key="btn_eval_diag_spk"):
                if not spk_text.strip():
                    st.warning("Please provide your spoken text transcript to evaluate.")
                else:
                    spk_eval_p = f"""Evaluate this spoken English transcript for an executive:
                    "{spk_text}"
                    Return JSON with keys:
                    'pronunciation_score': score out of 10,
                    'fluency_intonation_score': score out of 10,
                    'errors': array of objects ('original', 'corrected', 'explanation'),
                    'c1_speaking_benchmark': 'A high-impact executive C1 model spoken response.'"""
                    
                    with st.spinner("Evaluating speaking performance..."):
                        s_res = json.loads(extract_json(generate_ai_response(spk_eval_p)))
                        
                        col1, col2 = st.columns(2)
                        col1.metric("Pronunciation & Clarity", f"{s_res.get('pronunciation_score')}/10")
                        col2.metric("Intonation & Fluency", f"{s_res.get('fluency_intonation_score')}/10")
                        
                        st.markdown("#### 🔍 Key Speaking Errors & Adjustments:")
                        for err in s_res.get('errors', []):
                            st.markdown(f"- ❌ *\"{err.get('original')}\"* ➔ ✅ **\"{err.get('corrected')}\"** ({err.get('explanation')})")
                            
                        st.markdown("#### 🎯 Level C1 Standard Executive Response:")
                        st.success(s_res.get('c1_speaking_benchmark'))

    # --- MODULE 2: 30-DAY EXECUTIVE CURRICULUM ---
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
            "🔤 Vocabulary", "🗣️ Pronunciation", "📝 Grammar Rules", 
            "📖 Reading Mastery", "🎧 Listening", "✍️ Writing Task", "🎙️ Speaking Task"
        ])

        # --- TAB VOCABULARY ---
        with tab_v:
            p_v = f"""Generate C-Suite executive vocabulary for Day {day_selected} Topic: '{day_topic}'.
            Return JSON with key 'words' containing 5 items. Each item must have: 'word', 'phonetic', 'definition', 'c1_example', 'synonyms' (array)."""
            
            if st.button("Load Day Vocabulary", key=f"btn_v_{day_selected}"):
                get_or_generate_data(f"day_{day_selected}_vocab", p_v, seed_key=f"vocab_{day_selected}")

            v_data = st.session_state.get(f"day_{day_selected}_vocab")
            if v_data and "words" in v_data:
                for w in v_data["words"]:
                    st.markdown(f'<div class="apex-card">', unsafe_allow_html=True)
                    st.markdown(f"### 📌 **{w.get('word')}** `[{w.get('phonetic')}]`")
                    st.markdown(f"**Definition:** {w.get('definition')}")
                    st.markdown(f"**C1 Executive Example:** *\"{w.get('c1_example')}\"*")
                    st.markdown(f"**Synonyms:** {', '.join(w.get('synonyms', []))}")
                    play_audio(w.get('word'))
                    st.markdown('</div>', unsafe_allow_html=True)

        # --- TAB PRONUNCIATION ---
        with tab_p:
            p_p = f"""Generate C-Suite level pronunciation drill for Day {day_selected} topic: '{day_topic}'.
            Return JSON with keys:
            - 'key_terms': array of objects ('term', 'phonetic', 'tip')
            - 'executive_sentences': array of 3 complex executive sentences to practice intonation and connected speech."""
            
            if st.button("Load Pronunciation Guide", key=f"btn_p_{day_selected}"):
                get_or_generate_data(f"day_{day_selected}_pronunciation", p_p, seed_key=f"pron_{day_selected}")

            p_data = st.session_state.get(f"day_{day_selected}_pronunciation")
            if p_data:
                st.markdown("### 🎯 Key Executive Terminology & Pronunciation Tips")
                for item in p_data.get('key_terms', []):
                    st.markdown(f"- **{item.get('term')}** `[{item.get('phonetic')}]`: {item.get('tip')}")
                    play_audio(item.get('term'))
                
                st.divider()
                st.markdown("### 🔊 Intonation & Connected Speech Drills")
                for idx, sent in enumerate(p_data.get('executive_sentences', []), 1):
                    st.markdown(f"**{idx}.** *\"{sent}\"*")
                    play_audio(sent)

        # --- TAB GRAMMAR RULES ---
        with tab_g:
            p_g = f"""Provide detailed C1/C2 executive grammar training on: '{day_grammar}' applied to '{day_topic}'.
            Return JSON with keys:
            - 'lesson_theory': detailed breakdown of grammar rule, core formula, executive usage, common mistakes.
            - 'questions': 5 Multiple Choice Questions practicing this rule. Each question object MUST have 'id', 'question', 'options', 'correct_answer', and 'explanation'."""
            render_quiz_system(f"day_{day_selected}_grammar", p_g, "Load Grammar Lesson & Exercises", "Grammar", seed_key=f"gram_{day_selected}")

        # --- TAB READING MASTERY (CẬP NHẬT 20+ CÂU & 5-10 CÂU HỎI ĐA DẠNG) ---
        with tab_r:
            p_r = f"""Generate a comprehensive executive Reading Comprehension module for Day {day_selected} Topic: '{day_topic}'.
            Return JSON with keys:
            - 'passage': An authentic, highly detailed C-suite strategic report, board memo, or Harvard Business Review style case study. MUST BE AT LEAST 20 SENTENCES LONG (approx 400-500 words), split into 4 clear paragraphs.
            - 'questions': An array of 8 questions with multi-type varieties:
                1. Multiple Choice (type: 'multiple_choice', 4 options)
                2. Fill-in-the-blank (type: 'fill_in_the_blank', options: [])
                3. True / False / Not Given (type: 'true_false_ng', options: ['True', 'False', 'Not Given'])
                4. Vocabulary in Context (type: 'multiple_choice', 4 options)
            Each question object MUST contain: 'id', 'type', 'question', 'options', 'correct_answer' (exact full string or exact fill-in word), and 'explanation'."""
            render_quiz_system(f"day_{day_selected}_reading", p_r, "Load 20+ Sentence Reading Case & Exercises", "Reading", seed_key=f"read_{day_selected}")

        # --- TAB LISTENING ---
        with tab_l:
            p_l = f"""Generate an executive Listening comprehension module for Day {day_selected} Topic: '{day_topic}'.
            Return JSON with keys:
            - 'passage': A formal C-Suite executive oral briefing or keynote speech (around 200 words).
            - 'questions': 5 MCQ questions. Each MUST have 'id', 'question', 'options', 'correct_answer', and 'explanation'."""
            render_quiz_system(f"day_{day_selected}_listening", p_l, "Load Listening Briefing & Exercises", "Listening", seed_key=f"list_{day_selected}")

        # --- TAB WRITING TASK ---
        with tab_w:
            st.markdown(f"### ✍️ Day {day_selected} Executive Writing Challenge")
            st.markdown(f"**Topic Focus:** {day_topic} | **Grammar Target:** {day_grammar}")
            
            w_prompt_key = f"day_{day_selected}_w_prompt"
            if w_prompt_key not in st.session_state:
                p_w_gen = f"Generate 1 formal executive writing prompt (email, memo, or strategy summary) related to '{day_topic}'. Return JSON with key 'prompt'."
                raw_p = generate_ai_response(p_w_gen, seed_key=f"w_p_{day_selected}")
                st.session_state[w_prompt_key] = json.loads(extract_json(raw_p)).get('prompt', f"Write a strategic proposal on {day_topic}.")

            st.info(st.session_state[w_prompt_key])
            
            w_user_input = st.text_area("Write your executive draft here (min 80 words):", height=180, key=f"w_input_{day_selected}")
            
            if st.button("Submit Draft for C1/C2 Coaching", key=f"btn_w_eval_{day_selected}"):
                if len(w_user_input.strip().split()) < 20:
                    st.warning("Please draft a more substantial response (at least 20-80 words).")
                else:
                    eval_prompt = f"""Act as a C-suite English coach. Evaluate this writing draft:
                    Draft: "{w_user_input}"
                    Target Grammar: {day_grammar}
                    Target Topic: {day_topic}
                    
                    Return JSON with keys:
                    'cefr_level': estimated CEFR level,
                    'score': score out of 10,
                    'errors': array of objects ('original', 'corrected', 'reason'),
                    'c1_benchmark': 'A full model C1/C2 executive rewrite of the response.'"""
                    
                    with st.spinner("Analyzing executive writing..."):
                        w_res = json.loads(extract_json(generate_ai_response(eval_prompt)))
                        st.markdown(f"### 🏆 Level: **{w_res.get('cefr_level')}** (Score: {w_res.get('score')}/10)")
                        st.markdown("#### ❌ Corrections:")
                        for err in w_res.get('errors', []):
                            st.markdown(f"- ❌ *\"{err.get('original')}\"* ➔ ✅ **\"{err.get('corrected')}\"** ({err.get('reason')})")
                        st.markdown("#### ✨ C1/C2 Executive Model Benchmark:")
                        st.info(w_res.get('c1_benchmark'))

        # --- TAB SPEAKING TASK ---
        with tab_s:
            st.markdown(f"### 🎙️ Day {day_selected} Executive Speaking Challenge")
            st.markdown(f"**Topic Focus:** {day_topic}")
            
            s_prompt_key = f"day_{day_selected}_s_prompt"
            if s_prompt_key not in st.session_state:
                p_s_gen = f"Generate 1 high-impact C-suite speaking prompt related to '{day_topic}'. Return JSON with key 'prompt'."
                raw_sp = generate_ai_response(p_s_gen, seed_key=f"s_p_{day_selected}")
                st.session_state[s_prompt_key] = json.loads(extract_json(raw_sp)).get('prompt', f"Deliver a 1-minute executive statement on {day_topic}.")

            st.info(st.session_state[s_prompt_key])
            
            render_speech_recorder_stt(f"day_{day_selected}_spk")
            st.caption("Copy your transcript or type your spoken response into the text box below for AI evaluation:")
            s_user_input = st.text_area("Your Spoken Response Text:", height=100, key=f"spk_input_{day_selected}")
            
            if st.button("Evaluate Executive Speech", key=f"btn_s_eval_{day_selected}"):
                if not s_user_input.strip():
                    st.warning("Please provide your spoken text transcript to evaluate.")
                else:
                    spk_eval_prompt = f"""Evaluate this spoken English transcript for an executive speaking on '{day_topic}':
                    "{s_user_input}"
                    
                    Return JSON with keys:
                    'pronunciation_score': score out of 10,
                    'fluency_intonation_score': score out of 10,
                    'errors': array of objects ('original', 'corrected', 'explanation'),
                    'c1_speaking_benchmark': 'A high-impact executive C1 model spoken response.'"""
                    
                    with st.spinner("Analyzing speaking performance..."):
                        s_res = json.loads(extract_json(generate_ai_response(spk_eval_prompt)))
                        col1, col2 = st.columns(2)
                        col1.metric("Pronunciation & Clarity", f"{s_res.get('pronunciation_score')}/10")
                        col2.metric("Intonation & Fluency", f"{s_res.get('fluency_intonation_score')}/10")
                        
                        st.markdown("#### 🔍 Key Adjustments:")
                        for err in s_res.get('errors', []):
                            st.markdown(f"- ❌ *\"{err.get('original')}\"* ➔ ✅ **\"{err.get('corrected')}\"** ({err.get('explanation')})")
                        st.markdown("#### 🎯 C1 Standard Executive Response:")
                        st.success(s_res.get('c1_speaking_benchmark'))

    # --- MODULE 3: ERROR LOG & REMIND REVIEW ---
    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Executive Error Log & Review Center</h2>
            <p style='margin:5px 0 0 0;'>Track mistakes across exercises to review, reinforce, and solidify learning.</p>
        </div>
        """, unsafe_allow_html=True)

        err_list = st.session_state.get("error_log", [])
        
        if not err_list:
            st.success("🎉 Outstanding work! You currently have zero logged errors.")
        else:
            st.markdown(f"### 📋 Logged Errors Count: **{len(err_list)}**")
            
            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("🗑️ Clear Error Log"):
                    st.session_state["error_log"] = []
                    save_data_to_file()
                    st.rerun()

            for idx, err in enumerate(err_list, 1):
                st.markdown(f'<div class="wrong-card">', unsafe_allow_html=True)
                st.markdown(f"**Error #{idx} [{err.get('skill')}]**")
                st.markdown(f"**Question:** {err.get('question')}")
                st.markdown(f"❌ **Your Answer:** {err.get('your_answer')}")
                st.markdown(f"✅ **Correct Answer:** {err.get('correct_answer')}")
                st.markdown(f"💡 **Explanation:** {err.get('explanation')}")
                st.markdown('</div>', unsafe_allow_html=True)