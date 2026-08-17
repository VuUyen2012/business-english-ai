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

    audio {
        width: 100% !important;
        border-radius: 8px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
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
# 2. AUDIO PLAYER & SINGLE RECORD EVALUATOR
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

def transcribe_audio_groq(audio_bytes, filename="speech.wav"):
    """Gửi file âm thanh lên Groq Whisper API để chuyển giọng nói thành văn bản."""
    if not api_key:
        return None
    clean_key = re.sub(r'[^\x00-\x7F]+', '', str(api_key)).strip()
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {clean_key}"}
    files = {"file": (filename, audio_bytes, "audio/wav")}
    data = {"model": "whisper-large-v3", "language": "en"}
    try:
        res = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        if res.status_code == 200:
            return res.json().get("text", "")
        else:
            st.error(f"Whisper API Error ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        st.error(f"Whisper API Connection Error: {e}")
        return None

def record_and_evaluate_speech(original_text, unique_id):
    """Recorder duy nhất: Cho phép Ghi âm, Nghe lại trực tiếp và Chấm điểm chi tiết qua AI."""
    st.markdown("**🎙️ Native Audio Recorder & AI Pronunciation Evaluator**")
    audio_val = st.audio_input("Record speech for evaluation", key=f"rec_native_{unique_id}")
    
    if audio_val is not None:
        st.audio(audio_val, format="audio/wav")
        st.success("✅ Recorded successfully! Click play above to re-listen to your voice.")
        
        if st.button("🤖 Evaluate Audio Recording via Groq Whisper AI", key=f"btn_eval_audio_{unique_id}", use_container_width=True):
            with st.spinner("Analyzing pronunciation, stress, intonation & fluency via Whisper AI..."):
                audio_bytes = audio_val.read()
                transcription = transcribe_audio_groq(audio_bytes)
                if transcription:
                    peval_audio = f"""You are an expert Executive English Pronunciation Coach. 
                    Target Text: "{original_text}"
                    Speech Transcribed by AI: "{transcription}"
                    
                    Evaluate the user's pronunciation, intonation, and accuracy.
                    Return JSON object with keys:
                    'transcribed_text': str,
                    'pronunciation_score': int (0-100),
                    'mispronounced_words': list of strings,
                    'intonation_feedback': list of detailed feedback points regarding stress, pace, and rhythm,
                    'overall_advice': str.
                    ALL text MUST be in ENGLISH."""
                    
                    raw_eval = generate_ai_response(peval_audio)
                    clean_eval = extract_json(raw_eval)
                    if clean_eval:
                        try:
                            eval_dict = json.loads(clean_eval, strict=False)
                            st.session_state[f"res_audio_eval_{unique_id}"] = eval_dict
                            save_data_to_file()
                        except Exception as e:
                            st.error(f"Evaluation Parsing Error: {e}")

        eval_res = st.session_state.get(f"res_audio_eval_{unique_id}")
        if isinstance(eval_res, dict):
            score = eval_res.get("pronunciation_score", 0)
            st.markdown(f"""
            <div class="apex-card">
                <h4>📊 Pronunciation Analysis & Feedback</h4>
                <p><b>Transcribed Text:</b> "<i>{eval_res.get('transcribed_text')}</i>"</p>
                <p><b>Pronunciation & Clarity Score:</b> <span style="font-size:18px; font-weight:700; color:{'#16a34a' if score>=80 else '#d97706' if score>=60 else '#e11d48'}">{score}/100</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            mis_words = eval_res.get("mispronounced_words", [])
            if mis_words:
                st.markdown(f'<div class="wrong-card">❌ <b>Mispronounced / Omitted Words:</b> {", ".join(mis_words)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="correct-card">✅ <b>All target words pronounced accurately!</b></div>', unsafe_allow_html=True)
                
            st.markdown('<div class="hint-card">', unsafe_allow_html=True)
            st.markdown("<b>🎙️ Stress & Intonation Guidance:</b>")
            render_feedback_section(eval_res.get("intonation_feedback", []))
            st.markdown(f"<b>💡 Coaching Tip:</b> {eval_res.get('overall_advice', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

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
# 3. SIDEBAR & GROQ AI ENGINE WITH FALLBACK
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

    # Đã cập nhật danh sách model Groq mới nhất, khắc phục lỗi llama-3.1-70b-versatile bị ngắt dịch vụ
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]

    last_err_msg = ""
    for model_name in candidate_models:
        payload = {
            "model": model_name,
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
            elif res.status_code in (400, 404) or "decommissioned" in res.text or "model_not_found" in res.text:
                last_err_msg = f"Model {model_name} unavailable, trying alternative model..."
                continue
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
                return None
        except Exception as e:
            last_err_msg = f"Connection Error: {e}"
            break
            
    st.error(f"Groq API Error: {last_err_msg}")
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
                    parsed = json.loads(clean, strict=False)
                    if isinstance(parsed, dict):
                        st.session_state[session_key] = parsed
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
    if isinstance(data, dict):
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
        if isinstance(questions, list) and len(questions) > 0:
            for idx, q in enumerate(questions, 1):
                if not isinstance(q, dict): continue
                st.markdown(f"**Question {idx}: {q.get('question')}**")
                opts = q.get('options', [])
                key_input = f"q_{tab_key}_{idx}"
                
                if key_input not in st.session_state:
                    st.session_state[key_input] = opts[0] if (isinstance(opts, list) and len(opts) > 0) else ""

                if isinstance(opts, list) and len(opts) > 0:
                    current_val = st.session_state[key_input]
                    opt_idx = opts.index(current_val) if current_val in opts else 0
                    st.radio("Select Option:", opts, index=opt_idx, key=key_input)
                else:
                    st.text_input("Your Answer:", value=st.session_state.get(key_input, ""), key=key_input)
                st.write("---")
            
            if st.button("Submit & Evaluate Answers", key=f"sub_{tab_key}", use_container_width=True):
                user_answers = {}
                for idx, q in enumerate(questions, 1):
                    if not isinstance(q, dict): continue
                    q_id = str(q.get('id', idx))
                    key_input = f"q_{tab_key}_{idx}"
                    user_answers[q_id] = st.session_state.get(key_input)
                
                st.session_state[f"{tab_key}_sub"] = True
                st.session_state[f"{tab_key}_user_ans"] = user_answers
                save_data_to_file()

        if st.session_state.get(f"{tab_key}_sub", False) and isinstance(questions, list):
            user_ans = st.session_state.get(f"{tab_key}_user_ans", {})
            score = 0
            st.markdown("### 📊 Executive Assessment Results")
            
            for idx, q in enumerate(questions, 1):
                if not isinstance(q, dict): continue
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
            
            if isinstance(v_data_dict, dict) and "words" in v_data_dict and isinstance(v_data_dict["words"], list):
                words = v_data_dict["words"]
                for idx, w in enumerate(words, 1):
                    if not isinstance(w, dict): continue
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
                fill_list = g_data.get("fill_words", []) if isinstance(g_data, dict) else []
                if isinstance(fill_list, list) and len(fill_list) > 0:
                    for idx, gw in enumerate(fill_list, 1):
                        if not isinstance(gw, dict): continue
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
                            if not isinstance(gw, dict): continue
                            u_val = str(ans_map.get(idx, '')).strip().lower()
                            c_val = str(gw.get('word', '')).strip().lower()
                            if u_val == c_val and u_val != "":
                                g1_score += 1
                                st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Word: <b>{gw.get("word")}</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Your answer: <b>{u_val if u_val else "None"}</b> | Correct answer: <b>{gw.get("word")}</b></div>', unsafe_allow_html=True)
                        st.info(f"🏆 Game 1 Final Score: {g1_score}/{len(fill_list)}")

            elif game_type == "Game 2: Definition Matching Quiz":
                mcq_list = g_data.get("mcq_words", []) if isinstance(g_data, dict) else []
                if isinstance(mcq_list, list) and len(mcq_list) > 0:
                    for idx, mw in enumerate(mcq_list, 1):
                        if not isinstance(mw, dict): continue
                        st.markdown(f"**Question {idx}: What is the exact meaning of '{mw.get('word')}'?**")
                        key_g2_in = f"g2_in_{day_selected}_{idx}"
                        opts = mw.get('options', [])
                        if not isinstance(opts, list): opts = []
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
                            if not isinstance(mw, dict): continue
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
            
            p_list = p_dict.get("passages", []) if isinstance(p_dict, dict) else []
            if isinstance(p_list, list):
                for idx, text_p in enumerate(p_list, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4>Passage {idx}:</h4>
                        <p style="font-size:16px;">{text_p}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(text_p)
                    record_and_evaluate_speech(text_p, f"day_{day_selected}_p_{idx}")

        # --- 3. GRAMMAR RULES ---
        with tab_g:
            st.markdown(f"### 📐 Grammar Focus: {day_grammar}")
            pgram = f"""Generate an in-depth C1/C2 executive grammar lesson for '{day_grammar}' applied to '{day_topic}'. 
            Include:
            1. 'lesson_theory': Object with 'explanation', 'business_rules', 'c_suite_examples'.
            2. 'questions': Array of 5 Multiple Choice Questions testing this grammar rule. Each question must have 'id', 'question', 'options', 'answer', 'explanation'.
            ALL text MUST be in 100% ENGLISH. Return JSON object."""
            
            render_quiz_system(f"grammar_{day_selected}", pgram, "Load Grammar Masterclass", "Grammar", seed_key=f"grammar_d{day_selected}")

        # --- 4. READING ---
        with tab_r:
            st.markdown(f"### 📖 Case Study Reading: {day_topic}")
            pread = f"""Generate an executive business case study passage (250-300 words) on '{day_topic}'.
            Include 'passage' text and 'questions' array of 4 Multiple Choice Questions ('id', 'question', 'options', 'answer', 'explanation').
            ALL text MUST be in 100% ENGLISH. Return JSON object."""
            
            render_quiz_system(f"reading_{day_selected}", pread, "Load Case Reading", "Reading", seed_key=f"read_d{day_selected}")

        # --- 5. LISTENING BRIEFING ---
        with tab_l:
            st.markdown(f"### 🎧 C-Suite Audio Briefing: {day_topic}")
            plist = f"""Generate a C-suite executive briefing transcript ('passage', 150-200 words) on '{day_topic}'.
            Include 'questions' array of 4 Multiple Choice Questions ('id', 'question', 'options', 'answer', 'explanation').
            ALL text MUST be in 100% ENGLISH. Return JSON object."""
            
            render_quiz_system(f"listening_{day_selected}", plist, "Load Audio Briefing", "Listening", seed_key=f"listen_d{day_selected}")

        # --- 6. DETAILED WRITING SCENARIO ---
        with tab_w:
            st.markdown(f"### ✍️ Executive Writing Scenario: {day_topic}")
            pwrit = f"""Generate a detailed executive writing scenario for '{day_topic}'.
            Return JSON object with key 'writing_prompt' containing: 'scenario_background', 'task_instruction', 'target_vocabulary_to_use', 'key_metrics_to_include'."""
            
            w_data = get_or_generate_data(f"w_prompt_{day_selected}", pwrit, seed_key=f"write_d{day_selected}")
            
            if isinstance(w_data, dict) and "writing_prompt" in w_data and isinstance(w_data["writing_prompt"], dict):
                wp = w_data["writing_prompt"]
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown("#### 📄 Executive Business Scenario")
                st.write(wp.get("scenario_background", ""))
                st.markdown("**🎯 Task Instruction:**")
                st.write(wp.get("task_instruction", ""))
                st.markdown(f"**💡 Target Keywords:** `{wp.get('target_vocabulary_to_use', '')}`")
                st.markdown('</div>', unsafe_allow_html=True)

            user_writing_key = f"user_w_text_{day_selected}"
            if user_writing_key not in st.session_state:
                st.session_state[user_writing_key] = ""

            user_text = st.text_area("Write your executive response below:", value=st.session_state[user_writing_key], height=220, key=user_writing_key)

            if st.button("Submit Executive Writing for AI Evaluation", key=f"btn_eval_w_{day_selected}", use_container_width=True):
                if len(user_text.strip()) < 30:
                    st.warning("Please enter a more detailed writing response (minimum 30 words) for AI evaluation.")
                else:
                    peval = f"""Evaluate this executive writing response based on C-suite standards.
                    Topic: '{day_topic}'
                    Grammar Target: '{day_grammar}'
                    User Response: "{user_text}"
                    Return JSON object with keys:
                    'overall_score' (out of 100),
                    'grammar_feedback' (list of detailed points),
                    'vocabulary_tone_feedback' (list of detailed points),
                    'executive_rewrite' (polished version of user response).
                    ALL text MUST be in ENGLISH."""
                    
                    eval_res = generate_ai_response(peval)
                    clean_eval = extract_json(eval_res)
                    if clean_eval:
                        try:
                            st.session_state[f"w_eval_res_{day_selected}"] = json.loads(clean_eval, strict=False)
                            save_data_to_file()
                        except Exception as e:
                            st.error(f"Evaluation Parsing Error: {e}")

            w_eval_data = st.session_state.get(f"w_eval_res_{day_selected}")
            if isinstance(w_eval_data, dict):
                st.markdown("### 📊 Executive AI Writing Evaluation")
                score = w_eval_data.get("overall_score", 0)
                st.metric("Writing Mastery Score", f"{score}/100")
                
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown("#### 🔍 Detailed Feedback")
                st.markdown("**Grammar & Syntax:**")
                render_feedback_section(w_eval_data.get("grammar_feedback", []))
                st.markdown("**Tone & C-Suite Vocabulary:**")
                render_feedback_section(w_eval_data.get("vocabulary_tone_feedback", []))
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="correct-card">', unsafe_allow_html=True)
                st.markdown("#### ✨ Polished Executive Rewrite")
                st.write(w_eval_data.get("executive_rewrite", ""))
                st.markdown("</div>", unsafe_allow_html=True)

        # --- 7. DATA-DRIVEN SPEAKING ---
        with tab_s:
            st.markdown(f"### 💬 Data-Driven Executive Speaking: {day_topic}")
            pspeak = f"""Generate a C-suite presentation challenge for '{day_topic}'.
            Return JSON object with key 'speaking_prompt':
            'presentation_context', 'key_data_points', 'questions_to_address'."""
            
            s_data = get_or_generate_data(f"s_prompt_{day_selected}", pspeak, seed_key=f"speak_d{day_selected}")
            
            if isinstance(s_data, dict) and "speaking_prompt" in s_data and isinstance(s_data["speaking_prompt"], dict):
                sp = s_data["speaking_prompt"]
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown("#### 📈 Strategic Context & Key Metrics")
                st.write(sp.get("presentation_context", ""))
                st.markdown("**📊 Key Data Points to Present:**")
                st.write(sp.get("key_data_points", ""))
                st.markdown("**🎯 Strategic Questions to Answer:**")
                st.write(sp.get("questions_to_address", ""))
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("#### 🎙️ Practice Speaking Aloud & Live Audio Recording")
            record_and_evaluate_speech(
                f"Regarding {day_topic}, we must align our strategic execution with key data metrics to drive long-term value.", 
                f"day_{day_selected}_speaking_main"
            )

            user_speak_key = f"user_s_text_{day_selected}"
            if user_speak_key not in st.session_state:
                st.session_state[user_speak_key] = ""

            s_text = st.text_area("Or type your speech response for AI analysis:", value=st.session_state[user_speak_key], height=180, key=user_speak_key)

            if st.button("Evaluate Presentation Response", key=f"btn_eval_s_{day_selected}", use_container_width=True):
                if len(s_text.strip()) < 20:
                    st.warning("Please provide a speech response (minimum 20 words) for evaluation.")
                else:
                    pseval = f"""Evaluate this executive speech presentation response.
                    Topic: '{day_topic}'
                    User Response: "{s_text}"
                    Return JSON object with keys:
                    'clarity_impact_score' (out of 100),
                    'persuasiveness_feedback' (list of points),
                    'vocabulary_enhancements' (list of points),
                    'model_c_suite_delivery' (sample text).
                    ALL text MUST be in ENGLISH."""
                    
                    seval_res = generate_ai_response(pseval)
                    clean_seval = extract_json(seval_res)
                    if clean_seval:
                        try:
                            st.session_state[f"s_eval_res_{day_selected}"] = json.loads(clean_seval, strict=False)
                            save_data_to_file()
                        except Exception as e:
                            st.error(f"Speech Analysis Error: {e}")

            s_eval_data = st.session_state.get(f"s_eval_res_{day_selected}")
            if isinstance(s_eval_data, dict):
                st.markdown("### 📊 Presentation Feedback & AI Score")
                st.metric("Clarity & Impact Score", f"{s_eval_data.get('clarity_impact_score', 0)}/100")
                
                st.markdown('<div class="apex-card">', unsafe_allow_html=True)
                st.markdown("#### 💡 Structural & Persuasiveness Feedback")
                render_feedback_section(s_eval_data.get("persuasiveness_feedback", []))
                st.markdown("#### 🔤 Vocabulary & Phrase Upgrades")
                render_feedback_section(s_eval_data.get("vocabulary_enhancements", []))
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="correct-card">', unsafe_allow_html=True)
                st.markdown("#### 🏆 Model C-Suite Delivery Transcript")
                model_deliv = s_eval_data.get("model_c_suite_delivery", "")
                st.write(model_deliv)
                play_audio(model_deliv)
                st.markdown('</div>', unsafe_allow_html=True)

        # --- 8. TRANSLATION PRACTICE ---
        with tab_t:
            st.markdown(f"### 🌐 Executive Translation Practice: {day_topic}")
            ptrans = f"""Generate 4 challenging executive sentences on '{day_topic}' for English translation practice.
            Return JSON object with key 'translations' as array of 4 objects:
            'id', 'source_sentence_en', 'suggested_c_suite_translation', 'key_vocabulary_notes'."""
            
            t_data = get_or_generate_data(f"t_prompt_{day_selected}", ptrans, seed_key=f"trans_d{day_selected}")
            
            if isinstance(t_data, dict) and "translations" in t_data and isinstance(t_data["translations"], list):
                t_list = t_data["translations"]
                for idx, item in enumerate(t_list, 1):
                    if not isinstance(item, dict): continue
                    st.markdown(f'<div class="apex-card">', unsafe_allow_html=True)
                    st.markdown(f"**Sentence {idx}:** {item.get('source_sentence_en')}")
                    play_audio(item.get('source_sentence_en', ''))
                    
                    key_t_in = f"t_user_in_{day_selected}_{idx}"
                    if key_t_in not in st.session_state:
                        st.session_state[key_t_in] = ""
                    
                    st.text_input("Type your paraphrased/translated executive English version:", value=st.session_state[key_t_in], key=key_t_in)
                    st.markdown('</div>', unsafe_allow_html=True)

                if st.button("Submit & Reveal Benchmark Translations", key=f"btn_t_sub_{day_selected}", use_container_width=True):
                    st.session_state[f"t_sub_{day_selected}"] = True
                    save_data_to_file()

                if st.session_state.get(f"t_sub_{day_selected}", False):
                    st.markdown("### 📊 Benchmark C-Suite Reference Translations")
                    for idx, item in enumerate(t_list, 1):
                        if not isinstance(item, dict): continue
                        user_ans = st.session_state.get(f"t_user_in_{day_selected}_{idx}", "")
                        st.markdown(f'<div class="correct-card">', unsafe_allow_html=True)
                        st.markdown(f"**Sentence {idx} Reference Solution:**")
                        st.markdown(f"• **Your Version:** {user_ans if user_ans else 'Not provided'}")
                        st.markdown(f"• **Suggested C-Suite Version:** {item.get('suggested_c_suite_translation')}")
                        st.markdown(f"• **Key Vocabulary Notes:** {item.get('key_vocabulary_notes')}")
                        st.markdown('</div>', unsafe_allow_html=True)

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div class="hero-banner">
            <h2 style='margin:0;'>Error Log & Remind Review</h2>
            <p style='margin:5px 0 0 0;'>Review all missed questions from Diagnostic & Curriculum Quizzes.</p>
        </div>
        """, unsafe_allow_html=True)

        err_list = st.session_state.get("error_log", [])
        if not err_list:
            st.success("🎉 Outstanding job! Your error log is empty. No missed questions recorded.")
        else:
            st.write(f"Total Missed Items Recorded: **{len(err_list)}**")
            if st.button("🗑️ Clear Error Log History", use_container_width=True):
                st.session_state["error_log"] = []
                save_data_to_file()
                st.rerun()

            st.write("---")
            for idx, err in enumerate(err_list, 1):
                if not isinstance(err, dict): continue
                st.markdown(f'<div class="wrong-card">', unsafe_allow_html=True)
                st.markdown(f"#### Error #{idx} [{err.get('skill', 'General')}]")
                st.markdown(f"**Question:** {err.get('question')}")
                st.markdown(f"• **Your Answer:** <span style='color:#e11d48;'><b>{err.get('your_answer')}</b></span>", unsafe_allow_html=True)
                st.markdown(f"• **Correct Answer:** <span style='color:#16a34a;'><b>{err.get('correct_answer')}</b></span>", unsafe_allow_html=True)
                st.markdown(f"• **Explanation:** <i>{err.get('explanation')}</i>")
                st.markdown('</div>', unsafe_allow_html=True)