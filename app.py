import streamlit as st
import requests
import json
import time
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB
# ==========================================
st.set_page_config(
    page_title="Business English Master AI",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# 2. KHỞI TẠO BẢO VỆ KẾT NỐI SUPABASE
# ==========================================
supabase_url = st.secrets.get("SUPABASE_URL", "")
supabase_key = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
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

def get_user_current_level():
    results = safe_fetch("placement_results")
    if results and len(results) > 0:
        latest = results[0]
        return latest.get("overall_level", "B1 Intermediate")
    return "Chưa kiểm tra (Mặc định: B1 Intermediate)"

# ==========================================
# 3. HÀM PHÁT ÂM TIẾNG ANH (BROWSER SPEECH API)
# ==========================================
def play_audio_html(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <div style="margin: 10px 0;">
            <button onclick="speakText()" style="
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;">
                🔊 Play Audio
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

# ==========================================
# 4. THANH BÊN (SIDEBAR) & CẤU HÌNH
# ==========================================
with st.sidebar:
    st.title("⚙️ System Config")
    
    # Ưu tiên lấy Key từ Secrets
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    st.title("🎯 Navigation")
    
    app_mode = st.radio(
        "Choose Mode:",
        [
            "1. Comprehensive Placement Test", 
            "2. 30-Day Business English Curriculum", 
            "3. Review Error Log & History"
        ]
    )
    
    st.divider()
    st.subheader("📊 Database Status")
    current_lvl = get_user_current_level()
    if supabase:
        st.success("Supabase: Connected")
    else:
        st.warning("Supabase: Disconnected")
    st.info(f"🎯 **Current CEFR Level:**\n\n### `{current_lvl}`")

# ==========================================
# 5. CẤU HÌNH AI QUA GROQ API (Llama-3.3-70b)
# ==========================================
SYSTEM_PROMPT = """
You are a Senior Business English AI Instructor.
Guidelines:
1. All generated questions, passages, options, and explanations must be 100% in professional English.
2. Evaluate responses strictly according to CEFR standards (A2, B1, B2, C1, C2).
3. Ensure user-friendly formatting with clear structural boundaries.
"""

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Groq API Key missing! Check Secrets configuration.")
        return None

    if isinstance(prompt_input, str):
        prompt_text = prompt_input
    elif isinstance(prompt_input, list):
        prompt_text = " ".join([str(x) for x in prompt_input if isinstance(x, str)])
    else:
        prompt_text = str(prompt_input)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        elif response.status_code == 401:
            st.error("❌ Invalid Groq API Key.")
            return None
        elif response.status_code == 429:
            st.error("⏳ Rate limit reached. Please wait a few seconds and try again!")
            return None
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None

    except Exception as e:
        st.error(f"Network Connection Error: {str(e)}")
        return None

# ==========================================
# 6. GIAO DIỆN CHÍNH (UI INTERACTIVE)
# ==========================================
if not api_key:
    st.warning("⚠️ Please configure your Groq API Key in Streamlit Secrets to start!")
else:
    # PHẦN 1: PLACEMENT TEST (100% Tiếng Anh & Interactive)
    if app_mode == "1. Comprehensive Placement Test":
        st.title("📋 Comprehensive Placement Test")
        
        current_lvl = get_user_current_level()
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-bottom: 20px;">
            <h4 style="margin:0; color: #1E88E5;">🏆 Current CEFR Level: <b>{current_lvl}</b></h4>
            <p style="margin:5px 0 0 0; font-size: 14px; color: #555;">This placement result is used to personalize your 30-day Business English roadmap.</p>
        </div>
        """, unsafe_allow_html=True)

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "1. Vocabulary (15 Qs)", "2. Grammar (15 Qs)", "3. Reading (20 Qs)", 
            "4. Listening (10 Qs)", "5. Writing & CEFR", "6. Speaking (3 Topics)"
        ])

        # HÀM BỔ TRỢ RENDER INTERACTIVE QUIZ HÓA JSON
        def render_interactive_quiz(tab_key, prompt_json, button_label):
            if st.button(button_label, key=f"btn_gen_{tab_key}"):
                with st.spinner("Generating 100% English quiz data..."):
                    res_raw = generate_ai_response(prompt_json)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("```"): clean_json = clean_json[3:]
                            if clean_json.endswith("```"): clean_json = clean_json[:-3]
                            
                            st.session_state[f"{tab_key}_quiz_data"] = json.loads(clean_json.strip())
                            st.session_state[f"{tab_key}_user_answers"] = {}
                            st.session_state[f"{tab_key}_submitted"] = False
                        except Exception as e:
                            st.error(f"Error parsing quiz format. Please try again! ({str(e)})")

            if f"{tab_key}_quiz_data" in st.session_state and st.session_state[f"{tab_key}_quiz_data"]:
                quiz_data = st.session_state[f"{tab_key}_quiz_data"]
                
                with st.form(f"{tab_key}_quiz_form"):
                    user_answers = {}
                    for item in quiz_data:
                        st.markdown(f"**Question {item['id']}:** {item['question']}")
                        user_answers[item['id']] = st.radio(
                            label=f"Answer Q{item['id']}:",
                            options=item["options"],
                            key=f"{tab_key}_q_{item['id']}",
                            label_visibility="collapsed"
                        )
                        st.divider()

                    submitted = st.form_submit_button("📩 Submit & Grade Test")

                if submitted:
                    st.session_state[f"{tab_key}_submitted"] = True
                    st.session_state[f"{tab_key}_user_answers"] = user_answers

                if st.session_state.get(f"{tab_key}_submitted", False):
                    score = 0
                    u_ans = st.session_state[f"{tab_key}_user_answers"]
                    
                    st.markdown("### 📊 Test Results")
                    for item in quiz_data:
                        q_id = item['id']
                        selected = u_ans.get(q_id)
                        correct = item['answer']
                        
                        if selected == correct:
                            score += 1
                            st.success(f"**Q{q_id}: Correct!** ({selected})")
                        else:
                            st.error(f"**Q{q_id}: Incorrect.** Your answer: {selected} | **Correct Answer:** {correct}")
                        
                        st.info(f"💡 *Explanation:* {item['explanation']}")
                        st.write("---")

                    final_percentage = round((score / len(quiz_data)) * 100, 1)
                    st.balloons()
                    st.markdown(f"## 🏆 Final Score: **{score}/{len(quiz_data)}** ({final_percentage}%)")

        # 1. VOCABULARY TAB
        with t1:
            st.subheader("Vocabulary Assessment (15 Questions)")
            prompt_vocab = """
            Generate a 15-question Business English Vocabulary quiz (CEFR A2-C1).
            Return ONLY a valid JSON array without any markdown code blocks or preamble:
            [
              {
                "id": 1,
                "question": "Choose the word that best completes the sentence: 'We plan to _______ our new product line next quarter.'",
                "options": ["A) launch", "B) delay", "C) suspend", "D) dismiss"],
                "answer": "A) launch",
                "explanation": "'Launch' means to introduce a new product or project to the market."
              }
            ]
            """
            render_interactive_quiz("vocab", prompt_vocab, "Start Vocabulary Test")

        # 2. GRAMMAR TAB
        with t2:
            st.subheader("Grammar Assessment (15 Questions)")
            prompt_gram = """
            Generate a 15-question Business English Grammar quiz (CEFR A2-C1 focusing on tenses, conditionals, passive voice, and formal register).
            Return ONLY a valid JSON array without markdown blocks:
            [
              {
                "id": 1,
                "question": "Identify the correct structure: 'If we _______ the budget earlier, we would have avoided the project delay.'",
                "options": ["A) approved", "B) had approved", "C) have approved", "D) approve"],
                "answer": "B) had approved",
                "explanation": "Third conditional requires 'had + past participle' in the if-clause to talk about past unreal situations."
              }
            ]
            """
            render_interactive_quiz("grammar", prompt_gram, "Start Grammar Test")

        # 3. READING TAB
        with t3:
            st.subheader("Reading Comprehension Assessment")
            if st.button("Generate Reading Passage & Quiz", key="btn_p_read"):
                with st.spinner("Generating reading passage and comprehension questions..."):
                    prompt_read = """
                    Write a formal Business Strategy passage (250-300 words). Below it, create 5 multiple choice comprehension questions.
                    Return ONLY a JSON object formatted strictly like this:
                    {
                      "passage": "Full English passage text here...",
                      "questions": [
                        {
                          "id": 1,
                          "question": "What is the primary objective of the corporate restructuring mentioned in the passage?",
                          "options": ["A) To reduce market share", "B) To optimize operational efficiency", "C) To fire staff", "D) To close international branches"],
                          "answer": "B) To optimize operational efficiency",
                          "explanation": "Paragraph 2 states that restructuring aims to streamline workflows and reduce redundant costs."
                        }
                      ]
                    }
                    """
                    res_raw = generate_ai_response(prompt_read)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("```"): clean_json = clean_json[3:]
                            if clean_json.endswith("```"): clean_json = clean_json[:-3]
                            
                            st.session_state["reading_data"] = json.loads(clean_json.strip())
                            st.session_state["reading_submitted"] = False
                        except Exception as e:
                            st.error(f"Error parsing reading data. Please try again! ({str(e)})")

            if "reading_data" in st.session_state and st.session_state["reading_data"]:
                r_data = st.session_state["reading_data"]
                st.markdown("### 📖 Reading Passage")
                st.info(r_data["passage"])
                
                with st.form("reading_quiz_form"):
                    u_answers = {}
                    for item in r_data["questions"]:
                        st.markdown(f"**Question {item['id']}:** {item['question']}")
                        u_answers[item['id']] = st.radio(
                            label=f"Answer Q{item['id']}:",
                            options=item["options"],
                            key=f"read_q_{item['id']}",
                            label_visibility="collapsed"
                        )
                        st.divider()

                    if st.form_submit_button("Submit Reading Test"):
                        st.session_state["reading_submitted"] = True
                        st.session_state["reading_user_answers"] = u_answers

                if st.session_state.get("reading_submitted", False):
                    score = 0
                    u_ans = st.session_state["reading_user_answers"]
                    for item in r_data["questions"]:
                        q_id = item['id']
                        selected = u_ans.get(q_id)
                        correct = item['answer']
                        if selected == correct:
                            score += 1
                            st.success(f"**Q{q_id}: Correct!** ({selected})")
                        else:
                            st.error(f"**Q{q_id}: Incorrect.** Your answer: {selected} | **Correct:** {correct}")
                        st.info(f"💡 *Explanation:* {item['explanation']}")
                        st.write("---")
                    st.balloons()
                    st.markdown(f"## 🏆 Score: **{score}/{len(r_data['questions'])}**")

        # 4. LISTENING TAB
        with t4:
            st.subheader("Listening Comprehension Assessment")
            if st.button("Generate Audio Transcript & Questions", key="btn_p_listen"):
                with st.spinner("Generating audio script..."):
                    prompt_listen = """
                    Create a formal Business Meeting Dialogue between two managers (150-200 words).
                    Return ONLY a JSON object strictly like this:
                    {
                      "transcript": "Full dialogue text here...",
                      "questions": [
                        {
                          "id": 1,
                          "question": "What main disagreement occurred during the contract negotiation?",
                          "options": ["A) Payment terms", "B) Office location", "C) Hiring policy", "D) Dress code"],
                          "answer": "A) Payment terms",
                          "explanation": "Speaker A explicitly mentions that a 90-day payment cycle is unacceptable."
                        }
                      ]
                    }
                    """
                    res_raw = generate_ai_response(prompt_listen)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("