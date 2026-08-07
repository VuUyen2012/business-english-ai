import streamlit as st
import requests
import json
import re
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB & CUSTOM STYLING (UI/UX)
# ==========================================
st.set_page_config(
    page_title="Business English Master - TOEIC Standard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS nâng cấp giao diện ứng dụng
st.markdown("""
<style>
    /* Tổng thể nền và font */
    .main {
        background-color: #0e1117;
    }
    
    /* Style cho Card câu hỏi */
    .question-card {
        background-color: #1e2638;
        border: 1px solid #2e3a52;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Badge hiển thị trình độ */
    .level-badge {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }

    /* Hiển thị kết quả & giải thích */
    .correct-box {
        background-color: #1c3b2b;
        border-left: 5px solid #2e7d32;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        color: #81c784;
    }
    
    .wrong-box {
        background-color: #3e1f24;
        border-left: 5px solid #c62828;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        color: #ef9a9a;
    }
    
    .explanation-box {
        background-color: #262f40;
        padding: 10px 14px;
        border-radius: 6px;
        margin-top: 6px;
        font-size: 0.9em;
        color: #d1d5db;
    }

    /* Tùy chỉnh Nút bấm */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO SUPABASE
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

def safe_fetch(table_name: str):
    if not supabase:
        return []
    try:
        res = supabase.table(table_name).select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

def get_user_current_level():
    results = safe_fetch("placement_results")
    if results and len(results) > 0:
        return results[0].get("overall_level", "B1 Intermediate")
    return "B1 Intermediate"

# ==========================================
# 3. HÀM XỬ LÝ AN TOÀN (TTS & REGEX JSON)
# ==========================================
def play_audio_html(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <div style="margin: 10px 0;">
            <button onclick="speakText()" style="
                background-color: #2563eb; border: none; color: white;
                padding: 10px 20px; font-size: 15px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                🔊 Play Audio Passage
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
    st.components.v1.html(js_code, height=60)

def extract_json_safely(raw_text):
    if not raw_text:
        return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

# ==========================================
# 4. THANH BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/learning.png", width=64)
    st.title("Business English AI")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    app_mode = st.radio(
        "🎯 Core Navigation",
        [
            "1. TOEIC Placement Test", 
            "2. 30-Day Business Curriculum", 
            "3. Error Log & Analytics"
        ]
    )
    
    st.divider()
    current_lvl = get_user_current_level()
    st.markdown(f'<div class="level-badge">Current Level: {current_lvl}</div>', unsafe_allow_html=True)
    if supabase:
        st.caption("🟢 Supabase Connected")
    else:
        st.caption("🔴 Supabase Disconnected")

# ==========================================
# 5. GỌI GROQ API
# ==========================================
SYSTEM_PROMPT = """You are an expert TOEIC Business English Test Creator. 
Always generate high-quality questions following standard TOEIC formats. 
Outputs MUST strictly be valid JSON."""

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
        response = session.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# ==========================================
# 6. GIAO DIỆN CHÍNH (TOEIC STANDARD)
# ==========================================
if not api_key:
    st.warning("⚠️ Please configure your Groq API Key in the sidebar to start learning!")
else:
    if app_mode == "1. TOEIC Placement Test":
        st.title("📋 Comprehensive Placement Test (TOEIC Standard)")
        st.caption("Evaluates Vocabulary, Grammar, Reading, Listening, and Writing for Business English.")

        t1, t2, t3, t4, t5 = st.tabs([
            "🔤 Vocabulary", "📐 Grammar", "📖 Reading", "🎧 Listening", "✍️ Writing"
        ])

        # Hàm render câu hỏi trắc nghiệm chuẩn TOEIC (4 lựa chọn + Giải thích)
        def render_mcq_module(tab_key, prompt_req, btn_text):
            if st.button(btn_text, key=f"btn_{tab_key}", use_container_width=True):
                with st.spinner("Generating TOEIC standard questions..."):
                    raw = generate_ai_response(prompt_req)
                    clean = extract_json_safely(raw)
                    if clean:
                        try:
                            st.session_state[f"{tab_key}_data"] = json.loads(clean)
                            st.session_state[f"{tab_key}_sub"] = False
                        except Exception as e:
                            st.error(f"Format error: {str(e)}")

            if f"{tab_key}_data" in st.session_state:
                data = st.session_state[f"{tab_key}_data"]
                
                # Nếu là bài Listening, phát Audio đoạn văn bản
                if tab_key == "listening" and "passage" in data:
                    st.subheader("🎧 Audio Transcript")
                    play_audio_html(data["passage"])
                    st.markdown(f"> *\"{data['passage']}\"*")
                    questions = data.get("questions", [])
                elif tab_key == "reading" and "passage" in data:
                    st.subheader("📄 Reading Passage")
                    st.info(data["passage"])
                    questions = data.get("questions", [])
                else:
                    questions = data if isinstance(data, list) else data.get("questions", [])

                with st.form(f"form_{tab_key}"):
                    user_answers = {}
                    for idx, q in enumerate(questions, 1):
                        st.markdown(f"**Q{idx}: {q['question']}**")
                        user_answers[q['id']] = st.radio(
                            "Select correct option:",
                            q['options'],
                            key=f"{tab_key}_{q['id']}",
                            index=None
                        )
                        st.write("---")

                    submitted = st.form_submit_button("Submit Answers")
                    if submitted:
                        st.session_state[f"{tab_key}_sub"] = True
                        st.session_state[f"{tab_key}_ans"] = user_answers

                # HIỂN THỊ KẾT QUẢ VÀ GIẢI THÍCH CHI TIẾT SỬA LỖI
                if st.session_state.get(f"{tab_key}_sub", False):
                    score = 0
                    user_ans = st.session_state[f"{tab_key}_ans"]
                    
                    st.subheader("📊 Detailed Results & Explanations")
                    for idx, q in enumerate(questions, 1):
                        selected = user_ans.get(q['id'])
                        correct = q['answer']
                        is_correct = (selected == correct)
                        
                        if is_correct:
                            score += 1
                            st.markdown(f"""
                            <div class="correct-box">
                                <b>Q{idx}: Correct! ✅</b><br>
                                Your Answer: {selected}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="wrong-box">
                                <b>Q{idx}: Incorrect ❌</b><br>
                                Your Answer: {selected if selected else 'Not answered'}<br>
                                <b>Correct Answer:</b> {correct}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="explanation-box">
                            💡 <b>Explanation:</b> {q.get('explanation', 'No detailed explanation provided.')}
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("")

                    st.success(f"🏆 Final Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

        with t1:
            vocab_prompt = """Generate 5 Business English Vocabulary questions in strict JSON format. 
            Each question MUST have EXACTLY 4 options (A, B, C, D).
            JSON Structure:
            [
              {
                "id": 1,
                "question": "The company decided to _______ its manufacturing operations overseas.",
                "options": ["A. relocate", "B. relational", "C. relative", "D. relationship"],
                "answer": "A. relocate",
                "explanation": "'Relocate' is a verb meaning to move to a new location, fitting the context of business operations."
              }
            ]"""
            render_mcq_module("vocab", vocab_prompt, "🚀 Start Vocabulary Test (TOEIC Part 5)")

        with t2:
            grammar_prompt = """Generate 5 Business English Grammar questions in strict JSON format. 
            Each question MUST have EXACTLY 4 options (A, B, C, D).
            JSON Structure:
            [
              {
                "id": 1,
                "question": "If Mr. Smith _______ the contract yesterday, we would have started the project.",
                "options": ["A. signed", "B. had signed", "C. signs", "D. signing"],
                "answer": "B. had signed",
                "explanation": "This is a Third Conditional sentence referring to an unreal past action."
              }
            ]"""
            render_mcq_module("grammar", grammar_prompt, "🚀 Start Grammar Test (TOEIC Part 5)")

        with t3:
            reading_prompt = """Generate 1 short Business Reading passage with 3 comprehension questions in JSON format.
            JSON Structure:
            {
              "passage": "To all staff: The annual financial audit will take place next Monday...",
              "questions": [
                {
                  "id": 1,
                  "question": "What is the main purpose of this memo?",
                  "options": ["A. To announce an audit", "B. To fire staff", "C. To order supplies", "D. To change hours"],
                  "answer": "A. To announce an audit",
                  "explanation": "The memo clearly states that the annual audit will take place next Monday."
                }
              ]
            }"""
            render_mcq_module("reading", reading_prompt, "🚀 Start Reading Comprehension (TOEIC Part 6/7)")

        with t4:
            listening_prompt = """Generate 1 short Business Listening script passage with 3 questions in JSON format.
            JSON Structure:
            {
              "passage": "Welcome to today's quarterly sales meeting. I am pleased to report a 15% increase in revenue...",
              "questions": [
                {
                  "id": 1,
                  "question": "What was the revenue increase reported?",
                  "options": ["A. 5%", "B. 10%", "C. 15%", "D. 20%"],
                  "answer": "C. 15%",
                  "explanation": "The speaker mentions a 15% increase in revenue."
                }
              ]
            }"""
            render_mcq_module("listening", listening_prompt, "🚀 Start Listening Test (Audio-based)")

        with t5:
            st.subheader("✍️ TOEIC Writing: Business Email Response")
            st.info("Task: Respond to an incoming client email. AI will grade your tone, vocabulary, and grammar.")
            
            sample_email = "Dear Support, We received our shipment of office chairs, but 3 items were damaged. We need urgent replacements before Friday's conference."
            st.code(sample_email, language="text")
            
            user_writing = st.text_area("Write your reply email here (minimum 50 words):", height=150)
            if st.button("Submit Writing for AI Grading", use_container_width=True):
                if len(user_writing.split()) < 20:
                    st.warning("Please write a longer response to get accurate AI evaluation.")
                else:
                    with st.spinner("AI evaluating your business writing..."):
                        eval_prompt = f"Grade this business email response to: '{sample_email}'. Student Response: '{user_writing}'. Provide Score (out of 100), Strengths, Weaknesses, and an Improved Version."
                        result = generate_ai_response(eval_prompt)
                        st.markdown("### 📊 AI Writing Feedback")
                        st.write(result)

    elif app_mode == "2. 30-Day Business Curriculum":
        st.title("📚 30-Day Business English Curriculum")
        day = st.slider("Select Curriculum Day", 1, 30, 1)
        st.info(f"Currently displaying lesson roadmap for Day {day}")

    elif app_mode == "3. Error Log & Analytics":
        st.title("📜 Error Log & Learning Analytics")
        st.write("Review all your previous incorrect answers and practice weak areas.")