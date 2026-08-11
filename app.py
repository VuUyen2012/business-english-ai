import streamlit as st
import json
import os
import re
from groq import Groq

# -----------------------------------------------------------------------------
# 1. SETUP PAGE CONFIG & TITLE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Corporate Executive English Portal",
    page_icon="💼",
    layout="wide"
)

# Custom CSS cho giao diện chuyên nghiệp
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px;
    }
    .apex-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 C-Suite Corporate English Portal")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. GROQ API INITIALIZATION
# -----------------------------------------------------------------------------
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
if not api_key:
    # Nếu có lưu trong st.secrets hoặc os.environ
    api_key = os.environ.get("GROQ_API_KEY", "")

if not api_key:
    st.info("💡 Please enter your **Groq API Key** in the sidebar to activate the AI platform.")
    st.stop()

client = Groq(api_key=api_key)

def generate_ai_response(prompt):
    """Gửi prompt đến Groq Llama3 model và nhận phản hồi dạng string."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error communicating with AI: {str(e)}")
        return "{}"

def extract_json(raw_text):
    """Trích xuất chuỗi JSON từ kết quả AI trả về."""
    try:
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return match.group(0)
        return raw_text
    except Exception:
        return "{}"

# -----------------------------------------------------------------------------
# 3. CURRICULUM TOPICS CONFIGURATION
# -----------------------------------------------------------------------------
TOPICS = {
    "Day 1": "Cross-Border Mergers & Acquisitions (M&A) Due Diligence",
    "Day 2": "Corporate Financial Restructuring & Capital Allocation",
    "Day 3": "Supply Chain Resilience & Global Logistics Management",
    "Day 4": "Digital Transformation & Cloud Infrastructure Strategy",
    "Day 5": "Executive Leadership & Stakeholder Crisis Communication"
}

day_selected = st.sidebar.selectbox("Select Business Module:", list(TOPICS.keys()))
day_topic = TOPICS[day_selected]

st.sidebar.markdown(f"**Current Topic:**\n*{day_topic}*")

# -----------------------------------------------------------------------------
# 4. MAIN TABS
# -----------------------------------------------------------------------------
tab_v, tab_r, tab_l, tab_s, tab_w = st.tabs([
    "📚 Vocabulary & Idioms",
    "📰 Executive Reading",
    "🎧 Boardroom Listening",
    "🗣️ C-Level Speaking",
    "✍️ Executive Writing"
])

# -----------------------------------------------------------------------------
# TAB 1: VOCABULARY & IDIOMS
# -----------------------------------------------------------------------------
with tab_v:
    st.markdown(f"### 📚 Advanced Business Vocabulary & Idioms: {day_topic}")
    if f"vocab_{day_selected}" not in st.session_state:
        if st.button("Generate Executive Vocabulary", key=f"btn_v_{day_selected}"):
            with st.spinner("Generating C-suite terminology..."):
                p_vocab = f"Generate 5 advanced corporate words/phrases/idioms related to '{day_topic}'. Return JSON object with key 'vocabulary' containing an array of objects, each having: 'term', 'phonetic', 'definition' (in English), 'business_context' (example sentence)."
                raw_v = generate_ai_response(p_vocab)
                clean_v = extract_json(raw_v)
                if clean_v:
                    st.session_state[f"vocab_{day_selected}"] = json.loads(clean_v).get("vocabulary", [])

    vocab_data = st.session_state.get(f"vocab_{day_selected}", [])
    if vocab_data:
        for idx, item in enumerate(vocab_data, 1):
            st.markdown(f"""
            <div class="apex-card">
                <h4>{idx}. {item.get('term')} <small style="color: #6c757d;">[{item.get('phonetic')}]</small></h4>
                <p><b>Definition:</b> {item.get('definition')}</p>
                <p><b>Executive Context:</b> <i>"{item.get('business_context')}"</i></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Click the button above to load the business terms for this module.")

# -----------------------------------------------------------------------------
# TAB 2: EXECUTIVE READING
# -----------------------------------------------------------------------------
with tab_r:
    st.markdown(f"### 📰 C-Suite Reading Comprehension: {day_topic}")
    if f"reading_{day_selected}" not in st.session_state:
        if st.button("Generate Executive Article", key=f"btn_r_{day_selected}"):
            with st.spinner("Drafting Wall Street Journal style analysis..."):
                p_read = f"Write a 300-word executive article on '{day_topic}'. Also create 2 multiple-choice comprehension questions with 4 options each and indicate correct answer index (0-3). Return JSON with keys 'article', 'questions' (list of {{'q':..., 'options': [...], 'answer': int, 'explanation':...}})."
                raw_r = generate_ai_response(p_read)
                clean_r = extract_json(raw_r)
                if clean_r:
                    st.session_state[f"reading_{day_selected}"] = json.loads(clean_r)

    read_data = st.session_state.get(f"reading_{day_selected}", {})
    if read_data:
        st.markdown(f'<div class="apex-card">{read_data.get("article")}</div>', unsafe_allow_html=True)
        st.markdown("#### Comprehension Check:")
        
        for q_idx, q in enumerate(read_data.get("questions", []), 1):
            st.write(f"**Q{q_idx}: {q.get('q')}**")
            user_ans = st.radio(f"Select answer for Q{q_idx}:", q.get("options"), key=f"r_q_{day_selected}_{q_idx}")
            if st.button(f"Submit Q{q_idx}", key=f"btn_rq_{day_selected}_{q_idx}"):
                correct_idx = q.get("answer")
                correct_str = q.get("options")[correct_idx]
                if user_ans == correct_str:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer: {correct_str}")
                st.info(f"**Explanation:** {q.get('explanation')}")

# -----------------------------------------------------------------------------
# TAB 3: BOARDROOM LISTENING
# -----------------------------------------------------------------------------
with tab_l:
    st.markdown(f"### 🎧 Boardroom Meeting Simulation: {day_topic}")
    if f"listening_{day_selected}" not in st.session_state:
        if st.button("Simulate Boardroom Discussion", key=f"btn_l_{day_selected}"):
            with st.spinner("Generating dialogue script..."):
                p_list = f"Create a dialogue script between CEO and CFO discussing '{day_topic}'. Include 2 comprehension questions. Return JSON with 'transcript' (string), 'questions' (array of objects)."
                raw_l = generate_ai_response(p_list)
                clean_l = extract_json(raw_l)
                if clean_l:
                    st.session_state[f"listening_{day_selected}"] = json.loads(clean_l)

    list_data = st.session_state.get(f"listening_{day_selected}", {})
    if list_data:
        st.markdown(f'<div class="apex-card"><b>Meeting Transcript:</b><br><br>{list_data.get("transcript")}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: C-LEVEL SPEAKING
# -----------------------------------------------------------------------------
with tab_s:
    st.markdown(f"### 🗣️ Executive Pitch & Q&A Simulation: {day_topic}")
    st.write("Present your strategic solution to the Board of Directors below:")
    
    user_speech = st.text_area("Enter your spoken presentation script/transcript:", height=150, key=f"speech_in_{day_selected}")
    
    if st.button("Evaluate Presentation", key=f"btn_s_{day_selected}"):
        if len(user_speech.strip()) < 20:
            st.warning("Please enter a longer script for evaluation.")
        else:
            with st.spinner("Board members evaluating presentation..."):
                p_speak = f"Evaluate executive speech: '{user_speech}' on topic '{day_topic}'. Return JSON with: 'score' (integer 0-100), 'pacing_tone_feedback', 'improved_version'."
                raw_s = generate_ai_response(p_speak)
                clean_s = extract_json(raw_s)
                if clean_s:
                    res_s = json.loads(clean_s)
                    st.metric("Executive Delivery Score", f"{res_s.get('score', 80)}/100")
                    st.write("**Feedback:**", res_s.get("pacing_tone_feedback"))
                    st.markdown(f"**Polished C-Suite Version:**\n> {res_s.get('improved_version')}")

# -----------------------------------------------------------------------------
# TAB 5: EXECUTIVE WRITING (FIXED & ENHANCED)
# -----------------------------------------------------------------------------
with tab_w:
    st.markdown(f"### ✍️ Executive Business Writing Brief: {day_topic}")
    
    # 1. Generate Corporate Scenario Brief
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
    
    # 2. Writing Input Box & Word Counter
    user_w_text = st.text_area("Draft your executive proposal/report below:", height=240, key=f"w_input_{day_selected}")
    w_count = len(user_w_text.split())
    st.caption(f"Current Word Count: **{w_count} words** (Requirement: ≥ 100 words)")

    # 3. Evaluation Button & Logic Fix
    if st.button("Submit & Evaluate Executive Writing", key=f"btn_w_{day_selected}", use_container_width=True):
        if w_count < 100:
            st.error(f"Your essay contains {w_count} words. Please meet the minimum requirement of 100 words.")
        else:
            with st.spinner("AI Executive Editor analyzing your submission..."):
                # SỬA PROMPT: Yêu cầu rõ ràng AI chấm theo thang điểm 100
                pw = f"Analyze executive essay ({w_count} words): '{user_w_text}'. Context topic: '{day_topic}'. ALL feedback MUST be in 100% ENGLISH. Evaluate on a 0-100 percentage scale for Executive Polish, Tone, Structure, and Grammar. Return JSON with: 'score' (an integer number between 0 and 100, e.g. 85), 'errors' (array of bullet strings detailing specific grammar/style mistakes), 'feedback', 'sample_essay'."
                raw_w = generate_ai_response(pw)
                clean_w = extract_json(raw_w)
                
                if clean_w:
                    res_w = json.loads(clean_w)
                    
                    # ---------------------------------------------------------
                    # TỰ ĐỘNG CHUẨN HÓA ĐIỂM (SỬA LỖI 6.5/100 -> THANG ĐIỂM 100)
                    # ---------------------------------------------------------
                    raw_score = res_w.get('score', 70)
                    try:
                        num_score = float(raw_score)
                        if num_score <= 9.0:
                            # Nếu AI trả về thang điểm IELTS 9.0, tự động quy đổi ra % (Ví dụ: 6.5 -> 72)
                            final_score = int(round((num_score / 9.0) * 100))
                        else:
                            final_score = int(round(num_score))
                    except (ValueError, TypeError):
                        final_score = 75

                    # Hiển thị điểm số đã chuẩn hóa
                    st.success(f"🏆 Executive Writing Score: {final_score}/100")
                    
                    st.markdown("#### ❌ Grammar & Style Corrections:")
                    errs = res_w.get('errors', [])
                    if isinstance(errs, list) and len(errs) > 0:
                        for e in errs:
                            st.markdown(f"- {e}")
                    elif isinstance(errs, str):
                        st.write(f"- {errs}")
                    else:
                        st.info("No major grammatical errors detected. Great job!")

                    st.markdown("#### 💡 C-Suite Editorial Feedback:")
                    st.info(res_w.get('feedback', 'Solid writing layout with professional structure.'))

                    st.markdown("#### 🌟 Benchmark Model Proposal:")
                    st.markdown(f'<div class="apex-card">{res_w.get("sample_essay")}</div>', unsafe_allow_html=True)