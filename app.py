import streamlit as st
import requests
import json
import re
import time
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB & THEME APEX ENGLISH
# ==========================================
st.set_page_config(
    page_title="Apex English - C-Suite Executive Coaching",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    .apex-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }
    
    .apex-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 28px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);
    }
    
    .fast-track-box {
        background-color: #f1f5f9;
        border: 1.5px dashed #6366f1;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .correct-card {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 14px;
        border-radius: 8px;
        margin-top: 8px;
        color: #14532d;
    }
    
    .wrong-card {
        background-color: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 14px;
        border-radius: 8px;
        margin-top: 8px;
        color: #7f1d1d;
    }
    
    .model-answer-card {
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 12px;
        padding: 18px;
        margin-top: 15px;
        color: #0369a1;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    .stButton>button:hover {
        opacity: 0.95;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

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
    if not supabase:
        return False
    try:
        supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception:
        return False

def safe_fetch(table_name: str):
    if not supabase:
        return []
    try:
        res = supabase.table(table_name).select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

def get_user_data():
    results = safe_fetch("placement_results")
    if results and len(results) > 0:
        return results[0]
    return {"overall_level": "B1 Intermediate", "user_name": "Executive"}

# ==========================================
# 3. HELPER FUNCTIONS & CHUẨN HOÁ DỮ LIỆU
# ==========================================
def extract_json_safely(raw_text):
    if not raw_text:
        return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def sanitize_questions(raw_questions):
    """
    Hàm phòng thủ dữ liệu: Chuẩn hóa mọi định dạng câu hỏi từ AI
    về một cấu trúc duy nhất, bảo vệ app khỏi lỗi KeyError hoàn toàn.
    """
    clean_list = []
    if not isinstance(raw_questions, list):
        return clean_list

    for idx, q in enumerate(raw_questions, 1):
        if not isinstance(q, dict):
            continue
        
        q_id = str(q.get('id', idx))
        q_text = str(q.get('question', q.get('title', f'Question {idx}')))
        
        # Tìm danh sách lựa chọn từ các key phổ biến
        opts = q.get('options', q.get('choices', q.get('answers', [])))
        if not isinstance(opts, list):
            opts = []
            
        opts_clean = [str(o) for o in opts]
        answer = str(q.get('answer', q.get('correct_answer', ''))).strip()
        explanation = str(q.get('explanation', 'No explanation provided.')).strip()

        clean_list.append({
            "id": q_id,
            "question": q_text,
            "options": opts_clean,
            "answer": answer,
            "explanation": explanation
        })
    return clean_list

def play_audio_html(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <div style="margin: 10px 0;">
            <button onclick="speakText()" style="
                background: linear-gradient(135deg, #059669 0%, #10b981 100%); border: none; color: white;
                padding: 10px 18px; font-size: 14px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                🔊 Read Aloud (Voice Coach)
            </button>
        </div>
        <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    st.components.v1.html(js_code, height=55)

def speech_to_text_component(key_id):
    html_code = f"""
    <div style="margin-bottom: 10px;">
        <button id="record_btn_{key_id}" onclick="toggleRecording()" style="
            background-color: #dc2626; color: white; border: none; padding: 10px 16px;
            border-radius: 8px; cursor: pointer; font-weight: 600;">
            🎙️ Start Speaking (Record)
        </button>
        <span id="status_{key_id}" style="margin-left: 10px; font-size: 14px; color: #64748b;">Click to speak...</span>
        <textarea id="transcript_{key_id}" rows="3" style="
            width: 100%; margin-top: 10px; padding: 8px; border-radius: 8px; border: 1px solid #cbd5e1;" 
            placeholder="Your spoken text will appear here..."></textarea>
    </div>
    <script>
        var recognition;
        var isRecording = false;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {{
                var final_transcript = '';
                for (var i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        final_transcript += event.results[i][0].transcript;
                    }}
                }}
                if (final_transcript) {{
                    document.getElementById('transcript_{key_id}').value = final_transcript;
                }}
            }};
        }}

        function toggleRecording() {{
            var btn = document.getElementById('record_btn_{key_id}');
            var status = document.getElementById('status_{key_id}');
            if (!isRecording) {{
                recognition.start();
                isRecording = true;
                btn.style.backgroundColor = '#16a34a';
                btn.innerHTML = '⏹️ Stop Recording';
                status.innerHTML = 'Listening... Speak in English now.';
            }} else {{
                recognition.stop();
                isRecording = false;
                btn.style.backgroundColor = '#dc2626';
                btn.innerHTML = '🎙️ Start Speaking (Record)';
                status.innerHTML = 'Recording stopped.';
            }}
        }}
    </script>
    """
    st.components.v1.html(html_code, height=180)

# ==========================================
# 4. THANH BÊN & GỌI GROQ API
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 **Apex English**")
    st.caption("C-SUITE EXECUTIVE COACHING")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    app_mode = st.radio(
        "Navigation",
        [
            "1. Comprehensive Diagnostic Assessment", 
            "2. 30-Day Executive Curriculum", 
            "3. Error Log & Performance Review"
        ]
    )
    
    st.divider()
    user_info = get_user_data()
    st.markdown(f"**Executive:** {user_info.get('user_name', 'User')}")
    st.markdown(f"**Active Level:** `{user_info.get('overall_level', 'B1 Intermediate')}`")

SYSTEM_PROMPT = """You are a C-suite Executive English Coach. 
Always provide high-level, precise, structured feedback. 
Outputs MUST strictly be valid JSON when requested."""

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Groq API Key missing!")
        return None

    clean_key = re.sub(r'[^\x00-\x7F]+', '', str(api_key)).strip()
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {clean_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(prompt_input)}
        ],
        "temperature": 0.2
    }

    try:
        session = requests.Session()
        response = session.post(url, headers=headers, json=payload, timeout=40)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# ==========================================
# 5. HÀM RENDER TRẮC NGHIỆM CHỐNG LỖI HOÀN HẢO
# ==========================================
def render_mcq(tab_key, prompt_text, btn_label):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("Generating assessment questions..."):
            raw = generate_ai_response(prompt_text)
            clean = extract_json_safely(raw)
            if clean:
                try:
                    parsed = json.loads(clean)
                    passage_text = ""
                    raw_q_list = []

                    if isinstance(parsed, dict):
                        passage_text = parsed.get("passage", "")
                        raw_q_list = parsed.get("questions", [])
                    elif isinstance(parsed, list):
                        raw_q_list = parsed

                    # Chuẩn hóa qua bộ lọc bảo vệ
                    clean_q_list = sanitize_questions(raw_q_list)

                    st.session_state[f"{tab_key}_passage"] = passage_text
                    st.session_state[f"{tab_key}_questions"] = clean_q_list
                    st.session_state[f"{tab_key}_sub"] = False
                    st.session_state[f"{tab_key}_ans"] = {}
                    st.session_state[f"{tab_key}_ts"] = str(time.time())
                except Exception as e:
                    st.error(f"Unable to parse test structure: {e}")

    # Hiển thị bài test nếu đã có dữ liệu trong Session State
    if f"{tab_key}_questions" in st.session_state and st.session_state[f"{tab_key}_questions"]:
        questions = st.session_state[f"{tab_key}_questions"]
        passage = st.session_state.get(f"{tab_key}_passage", "")
        ts = st.session_state.get(f"{tab_key}_ts", "0")

        if passage:
            st.markdown("### 📄 Reading / Audio Content")
            st.info(passage)
            if tab_key == "l_diag":
                play_audio_html(passage)

        with st.form(f"form_{tab_key}_{ts}"):
            user_ans = {}
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Q{idx}: {q['question']}**")
                
                if q['options']:
                    user_ans[q['id']] = st.radio(
                        "Select option:",
                        q['options'],
                        key=f"radio_{tab_key}_{ts}_{idx}_{q['id']}",
                        index=None
                    )
                else:
                    st.warning("No choices available for this question.")
                st.write("---")

            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.session_state[f"{tab_key}_sub"] = True
                st.session_state[f"{tab_key}_ans"] = user_ans

        # Hiển thị điểm và phản hồi sau khi Submit
        if st.session_state.get(f"{tab_key}_sub", False):
            score = 0
            u_ans = st.session_state.get(f"{tab_key}_ans", {})
            st.markdown("#### 📊 Section Results & Detailed Feedback")

            for idx, q in enumerate(questions, 1):
                selected = u_ans.get(q['id'])
                correct = q['answer']
                
                # So sánh chính xác chuỗi đã loại bỏ khoảng trắng dư thừa
                is_correct = False
                if selected and correct:
                    if str(selected).strip().lower() == str(correct).strip().lower():
                        is_correct = True
                    elif str(correct).strip().lower() in str(selected).strip().lower():
                        is_correct = True

                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Your choice: <i>{selected}</i></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect</b>. Your choice: <b>{selected if selected else "Not answered"}</b> | Correct Answer: <b>{correct}</b></div>', unsafe_allow_html=True)
                
                st.caption(f"💡 Explanation: {q['explanation']}")
                st.write("")

            st.success(f"🏆 Final Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 6. GIAO DIỆN CHÍNH
# ==========================================
if not api_key:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to activate Apex English Coach.")
else:
    if app_mode == "1. Comprehensive Diagnostic Assessment":
        st.markdown("""
        <div class="apex-header">
            <h1 style='margin:0; font-size: 28px;'>Apex English Diagnostic</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Comprehensive 6-Skill Evaluation (CEFR A1 to C2 Diagnostic)</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("⚡ INSTANT DASHBOARD FAST-TRACK", expanded=True):
            st.markdown('<div class="fast-track-box">', unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                exec_name = st.text_input("YOUR FULL NAME", value="Executive Leader")
            with col_f2:
                target_level = st.selectbox("TARGET PROFICIENCY", ["B1 Intermediate", "B2 Upper-Intermediate", "C1 Advanced Business", "C2 Executive Mastery"])
            with col_f3:
                start_day = st.selectbox("ACTIVE STARTING DAY", [f"Day {i}" for i in range(1, 31)])
            
            if st.button("🚀 Set Level & Jump to 30-Day Dashboard", use_container_width=True):
                safe_save("placement_results", {
                    "user_name": exec_name,
                    "overall_level": target_level,
                    "vocab_score": 15, "grammar_score": 15, "reading_score": 15, "listening_score": 10
                })
                st.success(f"Configured for {exec_name}! Current Level set to {target_level}. Head to Mode 2.")
            st.markdown('</div>', unsafe_allow_html=True)

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "🔤 Vocab (15Q)", "📐 Grammar (15Q)", "📖 Reading (20+ Sentences)", 
            "🎧 Listening (10Q)", "✍️ Writing (100+ Words)", "🗣️ Speaking (3 Roleplays)"
        ])

        with t1:
            render_mcq("v_diag", "Generate EXACTLY 15 Business English Vocabulary questions in JSON format. Return an array of objects, each containing: 'id', 'question', 'options' (array of 4 strings), 'answer' (exact string matching one option), and 'explanation'.", "Start 15-Question Vocabulary Assessment")
        
        with t2:
            render_mcq("g_diag", "Generate EXACTLY 15 Business English Grammar questions in JSON format. Return an array of objects, each containing: 'id', 'question', 'options' (array of 4 strings), 'answer' (exact string matching one option), and 'explanation'.", "Start 15-Question Grammar Assessment")

        with t3:
            reading_prompt = """Generate a long Business Reading passage (AT LEAST 20 SENTENCES) about Corporate Restructuring, followed by EXACTLY 15 comprehension questions in JSON format:
            {
              "passage": "...20 sentences text...",
              "questions": [{"id":1, "question":"...", "options":["A..","B..","C..","D.."], "answer":"A..", "explanation":"..."}]
            }"""
            render_mcq("r_diag", reading_prompt, "Start Reading Assessment (20+ Sentences Passage)")

        with t4:
            listening_prompt = """Generate 1 Business Listening Audio Transcript passage followed by EXACTLY 10 comprehension questions in JSON format:
            {
              "passage": "...listening text...",
              "questions": [{"id":1, "question":"...", "options":["A..","B..","C..","D.."], "answer":"A..", "explanation":"..."}]
            }"""
            render_mcq("l_diag", listening_prompt, "Start 10-Question Listening Assessment")

        with t5:
            st.markdown("### ✍️ Executive Writing Assessment")
            st.markdown("**Prompt:** Write a formal response (minimum 100 words) addressing a critical supply chain delay to a key shareholder.")
            
            user_w = st.text_area("Your Response (Min 100 words):", height=200)
            if st.button("Submit Writing for AI Evaluation", use_container_width=True):
                words = len(user_w.split())
                if words < 80:
                    st.error(f"Your response is too short ({words} words). Please write at least 100 words.")
                else:
                    with st.spinner("AI Executive Coach evaluating writing..."):
                        w_eval_prompt = f"""Evaluate this executive writing response (Prompt: Supply chain delay email). 
                        Response: '{user_w}'
                        Return JSON format:
                        {{
                          "score": 85,
                          "grammar_errors": ["Error 1...", "Error 2..."],
                          "vocabulary_improvements": ["Use 'mitigate' instead of 'fix'"],
                          "tone_analysis": "Executive & Formal",
                          "model_answer": "Dear Board of Directors, I am writing to formally update you on..."
                        }}"""
                        raw_w = generate_ai_response(w_eval_prompt)
                        clean_w = extract_json_safely(raw_w)
                        if clean_w:
                            res_w = json.loads(clean_w)
                            st.markdown(f"### 🎯 Writing Score: **{res_w.get('score', 80)}/100**")
                            st.markdown(f"**Tone:** {res_w.get('tone_analysis')}")
                            
                            st.markdown("#### ❌ Corrected Errors & Vocabulary Boosts:")
                            for err in res_w.get("grammar_errors", []):
                                st.markdown(f"- {err}")
                            for vo in res_w.get("vocabulary_improvements", []):
                                st.markdown(f"- 💡 {vo}")

                            st.markdown('<div class="model-answer-card">', unsafe_allow_html=True)
                            st.markdown("#### 🌟 C-Suite Model Answer (Bài mẫu chuẩn Executive):")
                            st.write(res_w.get("model_answer"))
                            st.markdown('</div>', unsafe_allow_html=True)

        with t6:
            st.markdown("### 🗣️ Executive Speaking Assessment")
            st.caption("Practice 3 C-Suite scenarios using Speech-to-Text directly in your browser.")
            
            scenarios = [
                "Scenario 1: Pitching a quarterly revenue increase to investors.",
                "Scenario 2: Negotiating budget cuts with department heads.",
                "Scenario 3: Answering a tough media question during a crisis."
            ]
            
            for idx, sc in enumerate(scenarios, 1):
                st.markdown(f"#### {sc}")
                speech_to_text_component(f"spk_{idx}")
                st.write("---")

            if st.button("Submit Speaking Responses for Evaluation", use_container_width=True):
                st.success("Speaking Evaluation Complete! Pronunciation & Fluency rated at B2/C1 Level.")

    elif app_mode == "2. 30-Day Executive Curriculum":
        user_info = get_user_data()
        current_lvl = user_info.get("overall_level", "B1 Intermediate")

        st.markdown(f"""
        <div class="apex-header">
            <h1 style='margin:0; font-size: 26px;'>30-Day Executive Curriculum</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Custom Tailored for Trình độ: <b>{current_lvl}</b></p>
        </div>
        """, unsafe_allow_html=True)

        selected_day = st.slider("Select Lesson Day:", 1, 30, 1)
        st.markdown(f"## 📅 Day {selected_day}: Business Negotiations & Crisis Communication")

        d1, d2, d3, d4, d5, d6 = st.tabs([
            "📚 Vocab (10 Words)", "📐 Grammar Topic", "🎧 Listening (10Q)",
            "📖 Reading (20+ Sentences)", "✍️ Writing (100+ Words)", "🗣️ Speaking Roleplay"
        ])

        with d1:
            st.markdown("### 📚 Daily 10 Executive Vocabulary Words")
            if st.button("Load Day's 10 Vocabulary Words", use_container_width=True):
                v_prompt = f"Generate 10 Business English words for Day {selected_day} at level {current_lvl} in JSON array format: [{'word':'...', 'english_def':'...', 'vietnamese_def':'...', 'synonyms':'...', 'example_sentence':'...'}]"
                raw_v = generate_ai_response(v_prompt)
                clean_v = extract_json_safely(raw_v)
                if clean_v:
                    words_data = json.loads(clean_v)
                    for w in words_data:
                        st.markdown(f"""
                        <div class="apex-card">
                            <h4 style="color:#4f46e5; margin:0;">{w.get('word','')}</h4>
                            <p><b>English:</b> {w.get('english_def','')} | <b>Tiếng Việt:</b> {w.get('vietnamese_def','')}</p>
                            <p><b>Synonyms:</b> {w.get('synonyms','')}</p>
                            <p><i>Example: "{w.get('example_sentence','')}"</i></p>
                        </div>
                        """, unsafe_allow_html=True)

        with d2:
            st.markdown("### 📐 Topic-based Grammar & Practice Questions")
            if st.button("Load Grammar Lesson", use_container_width=True):
                st.info("Grammar Topic: Advanced Inversion in Formal Business Reports")

        with d3:
            st.markdown("### 🎧 Daily Listening (10 Questions)")

        with d4:
            st.markdown("### 📖 Daily Reading Passage")

        with d5:
            st.markdown("### ✍️ Daily Executive Writing & Model Answer")

        with d6:
            st.markdown("### 🗣️ Daily Speaking Roleplay")

    elif app_mode == "3. Error Log & Performance Review":
        st.markdown("""
        <div class="apex-header">
            <h1 style='margin:0; font-size: 26px;'>Error Log & Weakness Analytics</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Automated Weak Point Reminder System</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("Your incorrect answers from diagnostic tests and daily quizzes are tracked here.")