import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import re
import time
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB & THEME APEX ENGLISH
# ==========================================
st.set_page_config(
    page_title="Apex English - 30-Day Business Curriculum",
    page_icon="🎓",
    layout="wide"
)

# CSS FIX THEME SÁNG/TỐI & GIAO DIỆN
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }

    div[data-baseweb="tab"] div { color: #334155 !important; font-weight: 600 !important; }
    div[data-baseweb="tab"][aria-selected="true"] div { color: #4f46e5 !important; font-weight: 700 !important; }

    div[class*="stRadio"] label, div[class*="stRadio"] label p { color: #0f172a !important; font-weight: 500 !important; }

    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        color: #0f172a !important;
    }

    .correct-card {
        background-color: #f0fdf4 !important;
        border-left: 4px solid #16a34a !important;
        padding: 12px;
        border-radius: 6px;
        margin-top: 8px;
        color: #14532d !important;
    }
    
    .wrong-card {
        background-color: #fef2f2 !important;
        border-left: 4px solid #dc2626 !important;
        padding: 12px;
        border-radius: 6px;
        margin-top: 8px;
        color: #7f1d1d !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo kho lưu trữ lỗi sai trong session state
if "wrong_answers_log" not in st.session_state:
    st.session_state["wrong_answers_log"] = []

# ==========================================
# 2. KHỞI TẠO SUPABASE AN TOÀN
# ==========================================
supabase_url = st.secrets.get("SUPABASE_URL", "")
supabase_key = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(
            re.sub(r'[^\x00-\x7F]+', '', str(supabase_url)).strip(),
            re.sub(r'[^\x00-\x7F]+', '', str(supabase_key)).strip()
        )
    except Exception:
        supabase = None

def safe_save(table_name: str, data_dict: dict):
    if not supabase: return False
    try:
        supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception: return False

def safe_fetch(table_name: str):
    if not supabase: return []
    try:
        res = supabase.table(table_name).select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception: return []

# ==========================================
# 3. HELPER FUNCTIONS & GROQ API
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 **Apex English**")
    st.caption("BUSINESS ENGLISH 30-DAY NEXT LEVEL")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    app_mode = st.radio(
        "Navigation",
        [
            "1. Comprehensive Diagnostic Assessment", 
            "2. 30-Day Executive Curriculum", 
            "3. Error Log & Review Remind"
        ]
    )

SYSTEM_PROMPT = "You are a senior Business English Coach. Always provide well-structured output. JSON responses must be strict valid JSON."

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Groq API Key is missing!")
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
        response = requests.post(url, headers=headers, json=payload, timeout=40)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def extract_json_safely(raw_text):
    if not raw_text: return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    return match.group(1).strip() if match else raw_text.strip()

def sanitize_questions(raw_questions):
    clean_list = []
    if not isinstance(raw_questions, list): return clean_list
    for idx, q in enumerate(raw_questions, 1):
        if not isinstance(q, dict): continue
        clean_list.append({
            "id": str(q.get('id', idx)),
            "question": str(q.get('question', f'Question {idx}')),
            "options": [str(o) for o in q.get('options', [])],
            "answer": str(q.get('answer', '')).strip(),
            "explanation": str(q.get('explanation', 'No explanation')).strip()
        })
    return clean_list

def render_quiz_engine(tab_key, prompt_text, btn_label):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("AI is generating questions..."):
            raw = generate_ai_response(prompt_text)
            clean = extract_json_safely(raw)
            if clean:
                try:
                    parsed = json.loads(clean)
                    passage = parsed.get("passage", "") if isinstance(parsed, dict) else ""
                    raw_q = parsed.get("questions", []) if isinstance(parsed, dict) else parsed
                    st.session_state[f"{tab_key}_passage"] = passage
                    st.session_state[f"{tab_key}_questions"] = sanitize_questions(raw_q)
                    st.session_state[f"{tab_key}_sub"] = False
                    st.session_state[f"{tab_key}_ans"] = {}
                    st.session_state[f"{tab_key}_ts"] = str(time.time())
                except Exception as e:
                    st.error(f"Format parsing error: {e}")

    if f"{tab_key}_questions" in st.session_state and st.session_state[f"{tab_key}_questions"]:
        questions = st.session_state[f"{tab_key}_questions"]
        passage = st.session_state.get(f"{tab_key}_passage", "")
        ts = st.session_state.get(f"{tab_key}_ts", "0")

        if passage:
            st.markdown("#### 📄 Passage / Content")
            st.info(passage)
            # Tự động tạo âm thanh AI đọc cho bài Listening
            if "listen" in tab_key:
                tts_code = f"""
                <script>
                function playTTS() {{
                    var msg = new SpeechSynthesisUtterance({json.dumps(passage)});
                    msg.lang = 'en-US';
                    window.speechSynthesis.speak(msg);
                }}
                </script>
                <button onclick="playTTS()" style="background:#10b981; color:white; border:none; padding:10px 18px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    🔊 Play AI Audio Reading (Listening)
                </button>
                """
                components.html(tts_code, height=50)

        with st.form(f"form_{tab_key}_{ts}"):
            user_ans = {}
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Q{idx}: {q['question']}**")
                if q['options']:
                    user_ans[q['id']] = st.radio("Choose:", q['options'], key=f"r_{tab_key}_{ts}_{idx}_{q['id']}", index=None)
                st.write("---")

            if st.form_submit_button("Submit Answers"):
                st.session_state[f"{tab_key}_sub"] = True
                st.session_state[f"{tab_key}_ans"] = user_ans

        if st.session_state.get(f"{tab_key}_sub", False):
            score = 0
            u_ans = st.session_state.get(f"{tab_key}_ans", {})
            st.markdown("#### 📊 Evaluation & Detailed Feedback")

            for idx, q in enumerate(questions, 1):
                selected = u_ans.get(q['id'])
                correct = q['answer']
                is_correct = False
                if selected and correct and (str(selected).strip().lower() == str(correct).strip().lower() or str(correct).strip().lower() in str(selected).strip().lower()):
                    is_correct = True

                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Your answer: <i>{selected}</i></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect</b>. Selected: <b>{selected if selected else "No answer"}</b> | Correct: <b>{correct}</b></div>', unsafe_allow_html=True)
                    # Lưu lại câu sai vào nhật ký review
                    st.session_state["wrong_answers_log"].append({
                        "category": tab_key,
                        "question": q['question'],
                        "your_answer": selected,
                        "correct_answer": correct,
                        "explanation": q['explanation']
                    })
                st.caption(f"💡 Explanation: {q['explanation']}")

            st.success(f"🏆 Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 4. CHƯƠNG TRÌNH HỌC 30 NGÀY B1 BUSINESS
# ==========================================
if app_mode == "2. 30-Day Executive Curriculum":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
        <h2 style='margin:0; color:white;'>30-Day Business English (Level B1 -> Next Level)</h2>
        <p style='margin:5px 0 0 0; opacity:0.9;'>Full 6 Skills Syllabus with Score Assessment & Error Reminder</p>
    </div>
    """, unsafe_allow_html=True)

    day = st.slider("Select Day (1 to 30):", 1, 30, 1)
    st.markdown(f"### 📅 Curriculum Day {day}")

    t_vocab, t_gram, t_read, t_list, t_write, t_speak = st.tabs([
        "📚 Vocab (10 Words)", 
        "📐 Grammar", 
        "📖 Reading (20 Sentences & 15Q)", 
        "🎧 Listening (AI Audio & 10Q)", 
        "✍️ Writing (>=100 words)", 
        "🗣️ Speaking (STT Voice)"
    ])

    # 1. TỪ VỰNG (10 TỪ/NGÀY)
    with t_vocab:
        st.markdown("#### 📚 10 Business Words for Today")
        if st.button(f"Load Day {day} Vocabulary (10 Words)", key=f"btn_v_{day}", use_container_width=True):
            with st.spinner("Generating 10 Business words..."):
                v_prompt = f"Generate EXACTLY 10 Business English vocabulary words for Level B1 on Day {day}. Return JSON format with key 'words' containing an array of objects. Each object MUST have: 'word', 'english_def', 'vietnamese_def', 'synonyms', 'example_sentence'."
                raw = generate_ai_response(v_prompt)
                clean = extract_json_safely(raw)
                if clean:
                    try:
                        st.session_state[f"v_words_{day}"] = json.loads(clean).get("words", [])
                    except Exception as e: st.error(f"Error: {e}")

        if f"v_words_{day}" in st.session_state:
            for w in st.session_state[f"v_words_{day}"]:
                st.markdown(f"""
                <div class="apex-card">
                    <h4 style="color:#4f46e5; margin:0;">{w.get('word')}</h4>
                    <p><b>English:</b> {w.get('english_def')} | <b>Tiếng Việt:</b> {w.get('vietnamese_def')}</p>
                    <p><b>Synonyms:</b> {w.get('synonyms')}</p>
                    <p style="font-style: italic; color:#475569;">Example: "{w.get('example_sentence')}"</p>
                </div>
                """, unsafe_allow_html=True)

    # 2. NGỮ PHÁP (LÝ THUYẾT + 10-15 CÂU HỎI)
    with t_gram:
        st.markdown("#### 📐 Topic Grammar Lesson & Assessment")
        if st.button(f"Load Day {day} Grammar Lesson", key=f"btn_g_theory_{day}", use_container_width=True):
            with st.spinner("Loading grammar theory..."):
                g_lesson_prompt = f"Provide a complete Business English Grammar Lesson for Day {day} suitable for Level B1. Return JSON with keys: 'topic_title', 'theory_content' (detailed explanation with rules and business examples)."
                raw_g = generate_ai_response(g_lesson_prompt)
                clean_g = extract_json_safely(raw_g)
                if clean_g:
                    st.session_state[f"g_theory_{day}"] = json.loads(clean_g)

        if f"g_theory_{day}" in st.session_state:
            g_data = st.session_state[f"g_theory_{day}"]
            st.markdown(f"### Lesson: {g_data.get('topic_title')}")
            st.info(g_data.get('theory_content'))

        st.divider()
        g_prompt = f"Generate 10 Grammar assessment questions for Level B1 Day {day}. Return JSON object with key 'questions' containing an array of objects: 'id', 'question', 'options' (4 items), 'answer', 'explanation'."
        render_quiz_engine(f"gram_day_{day}", g_prompt, f"Start Day {day} Grammar Quiz (10 Questions)")

    # 3. ĐỌC (ĐOẠN VĂN ÍT NHẤT 20 CÂU & 15 CÂU HỎI)
    with t_read:
        st.markdown("#### 📖 Reading Comprehension (Long Article >=20 Sentences & 15 Questions)")
        r_prompt = f"Generate a long Business Reading passage with AT LEAST 20 sentences for Level B1 Day {day}. Then generate EXACTLY 15 multiple-choice comprehension questions. Return JSON with keys: 'passage' and 'questions' (array of 15 objects with 'id', 'question', 'options', 'answer', 'explanation')."
        render_quiz_engine(f"read_day_{day}", r_prompt, f"Start Day {day} Reading Test (15 Questions)")

    # 4. NGHE (CÓ NÚT ÂM THANH AI & 10 CÂU HỎI)
    with t_list:
        st.markdown("#### 🎧 Listening Practice (AI Voice & 10 Questions)")
        l_prompt = f"Generate a Business Listening script/passage (approx 150 words) for Day {day}. Then generate 10 listening comprehension questions. Return JSON with keys: 'passage' and 'questions' (array of 10 objects with 'id', 'question', 'options', 'answer', 'explanation')."
        render_quiz_engine(f"listen_day_{day}", l_prompt, f"Start Day {day} Listening Test (10 Questions)")

    # 5. VIẾT (TỐI THIỂU 100 TỪ, CHẤM LỖI & CUNG CẤP BÀI MẪU)
    with t_write:
        st.markdown("#### ✍️ Executive Writing Assessment (Minimum 100 Words)")
        st.info(f"Task Day {day}: Write a formal email or proposal regarding project delays, mitigation plans, and budget negotiation (Minimum 100 words).")
        
        user_text = st.text_area("Your Response:", height=200, key=f"write_input_{day}")
        word_count = len(re.findall(r'\w+', user_text))
        st.caption(f"Current Word Count: **{word_count} / 100 words minimum**")

        if st.button("Submit & Grade Writing", key=f"btn_w_grade_{day}", use_container_width=True):
            if word_count < 100:
                st.error(f"Your essay is too short ({word_count} words). Please write at least 100 words to submit.")
            else:
                with st.spinner("AI is evaluating grammar errors, tone, and generating a model essay..."):
                    w_prompt = f"Evaluate this Business writing submission ({word_count} words): '{user_text}'. Return JSON with keys: 'score' (out of 100), 'grammar_errors' (list of detailed errors and corrections), 'detailed_feedback', and 'model_essay' (a high-quality professional recommended version >=120 words)."
                    raw_w = generate_ai_response(w_prompt)
                    clean_w = extract_json_safely(raw_w)
                    if clean_w:
                        w_res = json.loads(clean_w)
                        st.success(f"🏆 Overall Score: {w_res.get('score')}/100")
                        st.markdown("##### 🔍 Grammar & Style Corrections:")
                        st.warning(w_res.get('grammar_errors'))
                        st.markdown("##### 💡 Feedback & Recommendations:")
                        st.info(w_res.get('detailed_feedback'))
                        st.markdown("##### 🌟 Recommended Model Essay:")
                        st.success(w_res.get('model_essay'))

    # 6. NÓI (SPEECH-TO-TEXT TRỰC TIẾP TỪ MICRO)
    with t_speak:
        st.markdown("#### 🗣️ Interactive Speaking Practice (Speech-to-Text)")
        st.info(f"Topic Day {day}: Present your quarterly performance and key achievements to executive stakeholders.")
        
        st.markdown("##### Click microphone to record your speech:")
        stt_code = """
        <script>
        var recognition;
        function startDictation() {
            if (window.hasOwnProperty('webkitSpeechRecognition')) {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = "en-US";
                recognition.start();
                document.getElementById('status').innerText = "🎙️ Listening... Speak now!";
                recognition.onresult = function(e) {
                    document.getElementById('speechText').value = e.results[0][0].transcript;
                    document.getElementById('status').innerText = "✅ Speech Captured!";
                    recognition.stop();
                };
                recognition.onerror = function(e) {
                    document.getElementById('status').innerText = "Error: " + e.error;
                    recognition.stop();
                }
            } else {
                alert("Web Speech API is not supported in this browser. Use Chrome/Edge.");
            }
        }
        </script>
        <div style="padding:10px; background:#ffffff; border-radius:10px; border:1px solid #cbd5e1;">
            <button onclick="startDictation()" style="background:#4f46e5; color:white; border:none; padding:12px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">
                🎙️ Start Microphone (Speech-to-Text)
            </button>
            <p id="status" style="margin-top:8px; font-weight:bold; color:#4f46e5;"></p>
            <textarea id="speechText" style="width:100%; height:90px; margin-top:8px; border-radius:6px; padding:8px;" placeholder="Transcribed text will appear here..."></textarea>
        </div>
        """
        components.html(stt_code, height=220)
        
        spk_manual = st.text_area("Or paste/review your transcribed speech text here for AI scoring:", height=100, key=f"spk_txt_{day}")
        if st.button("Evaluate Speaking Fluency & Grammar", key=f"btn_spk_eval_{day}", use_container_width=True):
            if spk_manual:
                with st.spinner("Evaluating speech text..."):
                    spk_eval_prompt = f"Evaluate this spoken dialogue response: '{spk_manual}'. Return JSON with keys: 'fluency_score' (out of 100), 'pronunciation_notes', 'grammar_corrections', 'better_expression'."
                    raw_spk = generate_ai_response(spk_eval_prompt)
                    clean_spk = extract_json_safely(raw_spk)
                    if clean_spk:
                        spk_res = json.loads(clean_spk)
                        st.success(f"Fluency Score: {spk_res.get('fluency_score')}/100")
                        st.markdown(f"**Grammar & Vocabulary Fixes:** {spk_res.get('grammar_corrections')}")
                        st.markdown(f"**Better Executive Expression:** {spk_res.get('better_expression')}")

# ==========================================
# 5. MỤC REVIEW & REMIND (NHẬT KÝ LỖI SAI)
# ==========================================
elif app_mode == "3. Error Log & Review Remind":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
        <h2 style='margin:0; color:white;'>Error Log & Review Remind</h2>
        <p style='margin:5px 0 0 0; opacity:0.9;'>Reminding frequently missed questions & weak skill areas</p>
    </div>
    """, unsafe_allow_html=True)

    wrong_log = st.session_state.get("wrong_answers_log", [])
    if wrong_log:
        st.markdown(f"### ⚠️ You have **{len(wrong_log)}** recorded incorrect answers to review:")
        for idx, item in enumerate(wrong_log, 1):
            st.markdown(f"""
            <div class="wrong-card">
                <p><b>#{idx} Category:</b> <code>{item.get('category')}</code></p>
                <p><b>Question:</b> {item.get('question')}</p>
                <p><b>Your Answer:</b> <span style="color:#dc2626;">{item.get('your_answer')}</span> | <b>Correct Answer:</b> <span style="color:#16a34a;">{item.get('correct_answer')}</span></p>
                <p><b>Explanation:</b> {item.get('explanation')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🎉 Great job! No errors recorded in your session yet. Complete the quizzes to populate your review log.")

elif app_mode == "1. Comprehensive Diagnostic Assessment":
    st.markdown("### 📊 Diagnostic Assessment Section")
    st.info("Use Navigation tab 2 to access the complete 30-Day Curriculum.")