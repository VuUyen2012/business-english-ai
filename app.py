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

# CSS FIX TRIỆT ĐỂ LỖI DARK MODE & MÀU CHỮ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* FIX CHỮ TAB, INPUT, RADIO, SELECTBOX */
    div[data-baseweb="tab"] div {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    div[data-baseweb="tab"][aria-selected="true"] div {
        color: #4f46e5 !important;
        font-weight: 700 !important;
    }

    div[class*="stRadio"] label, 
    div[class*="stRadio"] label p, 
    div[class*="stRadio"] div, 
    .stRadio p, .stRadio label, .stRadio span {
        color: #0f172a !important;
        font-weight: 500 !important;
        font-size: 15px !important;
    }

    .fast-track-box {
        background-color: #ffffff !important;
        border: 1.5px dashed #6366f1 !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        color: #0f172a !important;
    }

    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        color: #0f172a !important;
    }

    .stTextInput input, div[data-baseweb="select"] div {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    .correct-card {
        background-color: #f0fdf4 !important;
        border-left: 4px solid #16a34a !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 8px;
        color: #14532d !important;
    }
    
    .wrong-card {
        background-color: #fef2f2 !important;
        border-left: 4px solid #dc2626 !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 8px;
        color: #7f1d1d !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
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
# 3. HELPER FUNCTIONS
# ==========================================
def extract_json_safely(raw_text):
    if not raw_text:
        return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def sanitize_questions(raw_questions):
    clean_list = []
    if not isinstance(raw_questions, list):
        return clean_list

    for idx, q in enumerate(raw_questions, 1):
        if not isinstance(q, dict):
            continue
        
        q_id = str(q.get('id', idx))
        q_text = str(q.get('question', q.get('title', f'Question {idx}')))
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

SYSTEM_PROMPT = "You are a C-suite Executive English Coach. Always provide high-level, precise, structured feedback. Outputs MUST strictly be valid JSON."

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Groq API Key is missing!")
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
            {"role": "user", "content": prompt_input}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    try:
        session = requests.Session()
        response = session.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['choices'][0]['message']['content']
        else:
            st.error(f"Groq API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# ==========================================
# 5. HÀM RENDER TRẮC NGHIỆM
# ==========================================
def render_mcq(tab_key, prompt_text, btn_label):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("AI is generating assessment questions..."):
            raw = generate_ai_response(prompt_text)
            clean = extract_json_safely(raw)
            if clean:
                try:
                    parsed = json.loads(clean)
                    passage_text = ""
                    raw_q_list = []

                    if isinstance(parsed, dict):
                        passage_text = parsed.get("passage", "")
                        raw_q_list = parsed.get("questions", parsed.get("data", []))
                    elif isinstance(parsed, list):
                        raw_q_list = parsed

                    clean_q_list = sanitize_questions(raw_q_list)

                    st.session_state[f"{tab_key}_passage"] = passage_text
                    st.session_state[f"{tab_key}_questions"] = clean_q_list
                    st.session_state[f"{tab_key}_sub"] = False
                    st.session_state[f"{tab_key}_ans"] = {}
                    st.session_state[f"{tab_key}_ts"] = str(time.time())
                except Exception as e:
                    st.error(f"Unable to parse test structure: {e}")

    if f"{tab_key}_questions" in st.session_state and st.session_state[f"{tab_key}_questions"]:
        questions = st.session_state[f"{tab_key}_questions"]
        passage = st.session_state.get(f"{tab_key}_passage", "")
        ts = st.session_state.get(f"{tab_key}_ts", "0")

        if passage:
            st.markdown("### 📄 Content / Context")
            st.info(passage)

        with st.form(f"form_{tab_key}_{ts}"):
            user_ans = {}
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Q{idx}: {q['question']}**")
                
                if q['options']:
                    user_ans[q['id']] = st.radio(
                        "Select your answer:",
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

        if st.session_state.get(f"{tab_key}_sub", False):
            score = 0
            u_ans = st.session_state.get(f"{tab_key}_ans", {})
            st.markdown("#### 📊 Section Results & Detailed Feedback")

            for idx, q in enumerate(questions, 1):
                selected = u_ans.get(q['id'])
                correct = q['answer']
                
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
            
            safe_save("quiz_results", {
                "category": tab_key,
                "score": score,
                "total": len(questions)
            })

# ==========================================
# 6. GIAO DIỆN CHÍNH
# ==========================================
if not api_key:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to activate Apex English Coach.")
else:
    if app_mode == "1. Comprehensive Diagnostic Assessment":
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 26px; color: white;'>Apex English Diagnostic Assessment</h1>
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
                st.success(f"Configured for {exec_name}! Level set to {target_level}.")
            st.markdown('</div>', unsafe_allow_html=True)

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "🔤 Vocab (15Q)", "📐 Grammar (15Q)", "📖 Reading", 
            "🎧 Listening", "✍️ Writing", "🗣️ Speaking"
        ])

        with t1:
            vocab_prompt = "Generate 15 Business English Vocabulary questions in JSON format. Return a JSON object with a key 'questions' containing an array of objects. Each object must have: 'id', 'question', 'options' (4 strings), 'answer' (exact matching option), 'explanation'."
            render_mcq("v_diag", vocab_prompt, "Start 15-Question Vocabulary Assessment")
        
        with t2:
            grammar_prompt = "Generate 15 Executive English Grammar questions in JSON format. Return a JSON object with a key 'questions' containing an array of objects. Each object must have: 'id', 'question', 'options' (4 strings), 'answer' (exact matching option), 'explanation'."
            render_mcq("g_diag", grammar_prompt, "Start 15-Question Grammar Assessment")

        with t3:
            reading_prompt = "Generate 1 Business Reading passage followed by 5 comprehension questions in JSON format with keys: 'passage' and 'questions'."
            render_mcq("r_diag", reading_prompt, "Start Reading Assessment")

        with t4:
            listening_prompt = "Generate 1 Business Audio Transcript passage followed by 5 comprehension questions in JSON format with keys: 'passage' and 'questions'."
            render_mcq("l_diag", listening_prompt, "Start Listening Assessment")

        with t5:
            st.markdown("### ✍️ Executive Writing Assessment")
            user_w = st.text_area("Write a formal response regarding supply chain issues (Min 80 words):", height=150)
            if st.button("Submit Writing for Evaluation", use_container_width=True):
                st.success("Writing received and analyzed!")

        with t6:
            st.markdown("### 🗣️ Executive Speaking Assessment")
            st.info("Record or type your responses to C-Suite scenarios.")

    elif app_mode == "2. 30-Day Executive Curriculum":
        user_info = get_user_data()
        current_lvl = user_info.get("overall_level", "B1 Intermediate")

        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 26px; color: white;'>30-Day Executive Curriculum</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Personalized Plan for Level: <b>{current_lvl}</b></p>
        </div>
        """, unsafe_allow_html=True)

        selected_day = st.slider("Select Lesson Day:", 1, 30, 1)
        st.markdown(f"## 📅 Day {selected_day} - Executive Training ({current_lvl})")

        d1, d2, d3, d4, d5 = st.tabs([
            "📚 Daily Vocabulary (10 Words)", 
            "📐 Grammar Focus", 
            "📖 Reading Exercise", 
            "✍️ Writing Prompt", 
            "🗣️ Speaking Challenge"
        ])

        with d1:
            st.markdown(f"### 📚 10 Business Words for Day {selected_day}")
            if st.button(f"Generate Day {selected_day} Vocabulary", key="btn_v_day", use_container_width=True):
                with st.spinner("AI is generating 10 tailored business words..."):
                    v_prompt = f"Generate 10 Business English vocabulary words tailored for level {current_lvl} on Day {selected_day}. Return a JSON object with a key 'words' containing an array of objects. Each object must have: 'word', 'english_def', 'vietnamese_def', 'synonyms', 'example_sentence'."
                    raw_v = generate_ai_response(v_prompt)
                    clean_v = extract_json_safely(raw_v)
                    if clean_v:
                        try:
                            parsed_v = json.loads(clean_v)
                            words_list = parsed_v.get("words", parsed_v) if isinstance(parsed_v, dict) else parsed_v
                            st.session_state[f"day_{selected_day}_words"] = words_list
                        except Exception as e:
                            st.error(f"Data error: {e}")

            if f"day_{selected_day}_words" in st.session_state:
                for w in st.session_state[f"day_{selected_day}_words"]:
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4 style="color:#4f46e5; margin:0;">{w.get('word','')}</h4>
                        <p style="margin:5px 0;"><b>English Def:</b> {w.get('english_def','')} | <b>Tiếng Việt:</b> {w.get('vietnamese_def','')}</p>
                        <p style="margin:5px 0;"><b>Synonyms:</b> {w.get('synonyms','')}</p>
                        <p style="margin:5px 0; font-style: italic; color:#475569;">Example: "{w.get('example_sentence','')}"</p>
                    </div>
                    """, unsafe_allow_html=True)

        with d2:
            st.markdown(f"### 📐 Grammar Practice (Day {selected_day})")
            g_day_prompt = f"Generate 5 Grammar Practice questions for level {current_lvl} Day {selected_day}. Return a JSON object with key 'questions' containing an array of objects ('id', 'question', 'options', 'answer', 'explanation')."
            render_mcq(f"g_day_{selected_day}", g_day_prompt, f"Start Day {selected_day} Grammar Practice")

        with d3:
            st.markdown(f"### 📖 Business Reading Exercise (Day {selected_day})")
            r_day_prompt = f"Generate a short executive reading passage and 3 comprehension questions for level {current_lvl} Day {selected_day}. Return JSON with 'passage' and 'questions'."
            render_mcq(f"r_day_{selected_day}", r_day_prompt, f"Start Day {selected_day} Reading")

        with d4:
            st.markdown(f"### ✍️ Daily Executive Writing Prompt")
            st.info(f"Day {selected_day} Task: Write a concise executive memo summarizing key findings from a market entry report.")
            user_day_w = st.text_area("Your Draft Response:", height=150, key=f"write_day_{selected_day}")
            if st.button("Submit Writing for Feedback", key=f"btn_w_day_{selected_day}", use_container_width=True):
                if len(user_day_w.split()) < 30:
                    st.warning("Please write at least 30 words for feedback.")
                else:
                    with st.spinner("AI evaluating response..."):
                        w_eval_prompt = f"Analyze this writing draft: '{user_day_w}'. Return JSON with keys 'score' (number), 'feedback' (string), and 'improved_version' (string)."
                        raw_w_eval = generate_ai_response(w_eval_prompt)
                        clean_w_eval = extract_json_safely(raw_w_eval)
                        if clean_w_eval:
                            res_w = json.loads(clean_w_eval)
                            st.success(f"Score: {res_w.get('score', 80)}/100")
                            st.markdown(f"**Feedback:** {res_w.get('feedback', '')}")
                            st.markdown("**Improved Version:**")
                            st.info(res_w.get('improved_version', ''))

        with d5:
            st.markdown(f"### 🗣️ Speaking Challenge (Day {selected_day})")
            st.write("Practicing verbal pitch and crisis responses.")
            st.text_area("Type your verbal draft response:", height=100, key=f"spk_day_{selected_day}")
            if st.button("Submit Speaking Response", key=f"btn_spk_day_{selected_day}", use_container_width=True):
                st.success("Speaking submission logged!")

    elif app_mode == "3. Error Log & Performance Review":
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 26px; color: white;'>Error Log & Performance Review</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Tracked learning performance and historical quiz metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        quiz_history = safe_fetch("quiz_results")
        if quiz_history:
            st.markdown("### 📊 Quiz Results History")
            for item in quiz_history:
                st.markdown(f"- **Category:** `{item.get('category')}` | **Score:** {item.get('score')}/{item.get('total')}")
        else:
            st.info("No quiz history recorded yet. Complete assessments to track your metrics.")