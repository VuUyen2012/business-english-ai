import json
import os
import random
import tempfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIG & STYLING (SỬA LỖI UI SIDEBAR & INPUTS)
# ==========================================
st.set_page_config(
    page_title="IELTS & Business English Studio B2->C1",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Background light pink */
    .stApp, [data-testid="stAppViewContainer"] { 
        background-color: #FFF5F5 !important; 
    }
    
    /* Sidebar light theme styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label {
        color: #1A202C !important;
    }

    /* Force Selectbox & Inputs to White Background & Dark Text (Fix Lỗi 1 & Lỗi 2) */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div, 
    .stTextInput input, 
    .stSelectbox div[role="combobox"] {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }

    /* Dropdown Options List Styling */
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="option"] * {
        color: #1A202C !important;
    }

    /* Force black text across app */
    html, body, p, span, div, h1, h2, h3, h4, h5, h6, li, a, label, strong, b, em, i,
    [class*="css"], .stMarkdown, .stText, .stRadio label, .stCheckbox label,
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #1A202C !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Cards */
    .studio-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    .studio-card *, .studio-card p, .studio-card span, .studio-card h1, .studio-card h2, 
    .studio-card h3, .studio-card h4, .studio-card div, .studio-card b, .studio-card i, .studio-card li {
        color: #1A202C !important;
    }

    code {
        background-color: #EDF2F7 !important;
        color: #2D3748 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }

    /* Badges */
    .badge-c1 {
        background-color: #FED7D7 !important;
        color: #9B2C2C !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .badge-b2 {
        background-color: #EBF8FF !important;
        color: #2B6CB0 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }

    /* Red Primary Buttons */
    .stButton>button {
        background-color: #E53E3E !important; 
        color: #FFFFFF !important;
        border-radius: 8px !important; 
        border: none !important;
        padding: 10px 20px !important; 
        font-weight: 600 !important; 
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button p {
        color: #FFFFFF !important;
    }
    .stButton>button:hover { 
        background-color: #C53030 !important; 
        box-shadow: 0 4px 12px rgba(229, 62, 62, 0.2) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. TTS ENGINE (WEB SPEECH API)
# ==========================================
def render_tts_button(text, button_id):
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <button onclick="playTTS('{clean_text}')" id="btn_{button_id}" style="
        background-color: #ED8936;
        color: white;
        border: none;
        padding: 6px 14px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    ">
        🔊 Listen Audio
    </button>
    <script>
    function playTTS(phrase) {{
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(phrase);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """
    components.html(js_code, height=45)

# ==========================================
# 3. SAVE PROGRESS & API SERVICES (FIX LỖI 4: LƯU DATA BÀI LÀM)
# ==========================================
DATA_FILE = "user_progress.json"

def load_saved_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data_to_file():
    data_to_save = {
        "completed_days": list(st.session_state.get("completed_days", set())),
        "api_key": st.session_state.get("groq_api_key", ""),
        "user_answers": st.session_state.get("user_answers", {}),
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        st.toast("Progress saved successfully!", icon="✅")
    except Exception as e:
        st.error(f"Save error: {e}")

saved_data = load_saved_data()

if "completed_days" not in st.session_state:
    st.session_state.completed_days = set(saved_data.get("completed_days", []))
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = saved_data.get("api_key", "")
if "user_answers" not in st.session_state:
    st.session_state.user_answers = saved_data.get("user_answers", {})
if "audio_recordings" not in st.session_state:
    st.session_state.audio_recordings = {}

def call_groq_llm(prompt, api_key):
    if not api_key:
        st.error("Please enter your Groq API Key in the Sidebar!")
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    active_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    
    for model in active_models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a C1 Business English & IELTS Senior Examiner. Provide structured evaluations strictly in English."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            elif res.status_code == 401:
                st.error("Invalid API Key! Please check your Groq API Key.")
                return None
        except Exception:
            continue
    st.error("Groq API Connection Failed. Check Key or Network!")
    return None

def transcribe_audio_groq(audio_bytes, api_key):
    if not api_key:
        st.error("Please enter your Groq API Key in the Sidebar!")
        return None
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key.strip()}"}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
        
    try:
        with open(tmp_path, "rb") as f:
            files = {
                "file": ("recording.wav", f, "audio/wav"),
                "model": (None, "whisper-large-v3"),
                "language": (None, "en")
            }
            res = requests.post(url, headers=headers, files=files, timeout=40)
        if res.status_code == 200:
            return res.json().get("text", "")
        else:
            st.error(f"Whisper API Error: {res.status_code} - {res.text}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return None

# Helper function để lưu đáp án người dùng vào session_state
def get_user_ans(key, default=""):
    return st.session_state.user_answers.get(key, default)

def set_user_ans(key, val):
    st.session_state.user_answers[key] = val

# ==========================================
# 4. SPEECH EVALUATION & AUDIO PLAYER
# ==========================================
def record_and_evaluate_speech(reference_text, label, context_info=""):
    st.markdown(f"**Target Text/Context:** *\"{reference_text}\"*")
    render_tts_button(reference_text, f"tts_{hash(label+reference_text)}")
    
    rec_key = f"rec_{hash(label)}"
    audio_val = st.audio_input("Click mic to record your voice:", key=rec_key)
    
    if audio_val:
        st.session_state.audio_recordings[label] = audio_val.read()
    
    if label in st.session_state.audio_recordings:
        st.markdown("**Your Saved Recording:**")
        st.audio(st.session_state.audio_recordings[label], format="audio/wav")
        
        if st.button("🎯 Analyze Pronunciation & Intonation AI", key=f"btn_{hash(label)}"):
            with st.spinner("AI is analyzing speech..."):
                audio_bytes = st.session_state.audio_recordings[label]
                transcribed = transcribe_audio_groq(audio_bytes, st.session_state.groq_api_key)
                if transcribed:
                    st.info(f"📝 **AI Transcribed:** \"{transcribed}\"")
                    prompt = f"""
                    Evaluate C1/IELTS Speaking performance strictly in English:
                    - Reference/Prompt: "{reference_text}"
                    - Context Info: "{context_info}"
                    - Student Spoke: "{transcribed}"
                    
                    Provide feedback in standard English using the format:
                    1. Overall Score (/10)
                    2. Pronunciation & Word Stress
                    3. Sentence Intonation & Rhythm
                    4. Relevance to Context & Content Quality
                    5. Detailed Mistakes & Improvements
                    """
                    feedback = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if feedback:
                        st.markdown(f"<div class='studio-card'>{feedback}</div>", unsafe_allow_html=True)

# ==========================================
# 5. CURRICULUM DATA
# ==========================================
def get_curriculum_day(day_num):
    topics = [
        "Executive Corporate Strategy", "Cross-Border Negotiations", "Financial Risk Mitigation",
        "Change Management & Agility", "Brand Reputation & Crisis", "Digital Transformation",
        "Supply Chain Optimization", "M&A Realignment", "ESG & Corporate Governance", "AI & Business Automation"
    ]
    topic = topics[(day_num - 1) % len(topics)]
    
    vocab = [
        {"word": "Consolidate", "pos": "verb", "en": "To combine into a single, stronger unit.", "syn": "Merge, Strengthen", "example": "The company plans to consolidate its position in the European market."},
        {"word": "Feasibility", "pos": "noun", "en": "The degree to which something is possible.", "syn": "Viability, Practicability", "example": "We conducted a feasibility study before launching the project."},
        {"word": "Disruption", "pos": "noun", "en": "Disturbance that alters a system.", "syn": "Upheaval, Disturbance", "example": "AI technology is causing massive disruption in traditional industries."},
        {"word": "Benchmark", "pos": "noun", "en": "A standard against which things may be measured.", "syn": "Criterion, Yardstick", "example": "Our Q3 performance set a new benchmark for the sector."},
        {"word": "Mitigate", "pos": "verb", "en": "Make less severe, serious, or painful.", "syn": "Alleviate, Reduce", "example": "Steps were taken to mitigate the financial impact of the crisis."},
        {"word": "Leverage", "pos": "verb", "en": "Use something to maximum advantage.", "syn": "Exploit, Utilize", "example": "We must leverage our brand equity to launch new products."},
        {"word": "Scalability", "pos": "noun", "en": "Ability of a system to handle growing work.", "syn": "Expandability", "example": "Cloud architecture offers incredible business scalability."},
        {"word": "Pivot", "pos": "verb", "en": "Change strategic direction abruptly.", "syn": "Shift, Reorient", "example": "The startup pivoted from B2C to an enterprise B2B model."},
        {"word": "Stagnation", "pos": "noun", "en": "State of not flowing, moving, or changing.", "syn": "Inaction, Standstill", "example": "Economic stagnation led to reduced corporate investment."},
        {"word": "Unprecedented", "pos": "adj", "en": "Never done or known before.", "syn": "Unparalleled, Novel", "example": "The sector experienced unprecedented growth during the quarter."}
    ]

    pronunciation = [
        "Our strategic initiatives have significantly consolidated our market position over the past fiscal year. Executive board members have agreed to increase capital expenditure to expand our infrastructure. Moving forward, this framework will guarantee operational excellence across all major regions.",
        "To mitigate operational risks, executive leadership approved an unprecedented risk governance framework yesterday. This multi-layered initiative addresses cyber security vulnerabilities, compliance hurdles, and potential supply chain bottlenecks. By doing so, we ensure long-term stability and sustained market leadership.",
        "Leveraging digital scalability remains the primary benchmark for enterprise growth in this quarter. Companies that fail to adapt their infrastructure will face severe market stagnation and revenue decline. Therefore, accelerating our cloud integration strategy is essential for immediate competitive advantage."
    ]

    grammar_theory = """
    **Advanced Business Conditionals: Inversion Structure (C1 Level)**
    <br><br>
    <b>1. Type 1 Conditional Inversion (Formal Requests / Future Possibilities):</b><br>
    • Standard: If you require further clarification, please contact our legal counsel.<br>
    • Inverted: <b>Should you require further clarification,</b> please contact our legal counsel.<br><br>
    
    <b>2. Type 2 Conditional Inversion (Hypothetical Present / Future Scenarios):</b><br>
    • Standard: If the market were to collapse, our contingency plan would take effect.<br>
    • Inverted: <b>Were the market to collapse,</b> our contingency plan would take effect.<br><br>
    
    <b>3. Type 3 Conditional Inversion (Hypothetical Past Scenarios):</b><br>
    • Standard: If the board had approved the merger, our revenue would have doubled.<br>
    • Inverted: <b>Had the board approved the merger,</b> our revenue would have doubled.<br>
    """
    
    grammar_mcq = [
        {"q": "_____ the executive committee mandate the budget, we will proceed immediately.", "options": ["Had", "Should", "Were", "Unless"], "a": "Should"},
        {"q": "_____ the company mitigated risks earlier, the losses would have been avoided.", "options": ["Were", "Had", "Should", "If only"], "a": "Had"},
        {"q": "_____ the price of raw materials to skyrocket, we would adjust our pricing strategy.", "options": ["Were", "Should", "Had", "If"], "a": "Were"},
        {"q": "Should you _____ any issues with compliance, notify the audit team.", "options": ["encounter", "encountered", "encounters", "had encountered"], "a": "encounter"},
        {"q": "Had the CEO _____ the market trends, the product launch would not have failed.", "options": ["foreseen", "foresaw", "foresee", "foreseeing"], "a": "foreseen"}
    ]
    grammar_fitb = [
        {"q": "_____ (Were) the firm to pivot now, stakeholders might object strongly.", "a": "Were"},
        {"q": "Should you _____ (need) additional leverage during negotiations, review the clause.", "a": "need"},
        {"q": "_____ (Had) the board known about the disruption, they would have restructured early.", "a": "Had"},
        {"q": "Were we to _____ (optimize) the supply chain, overhead costs would fall by 15%.", "a": "optimize"},
        {"q": "Should any partner _____ (violate) the terms, the contract will be terminated.", "a": "violate"}
    ]

    reading_text = """
1. In an era marked by unprecedented global market volatility, modern corporations face severe operational threats.
2. Navigating this complex landscape requires executive leadership to move far beyond mere baseline compliance.
3. Establishing long-term organizational sustainability demands proactive strategic planning and robust agility.
4. Adopting rigorous feasibility frameworks ensures that capital and human resource allocations align with strategic vision.
5. Furthermore, failure to mitigate systemic vulnerabilities frequently precipitates irreversible brand damage across global markets.
6. Corporate leaders must systematically analyze potential risk factors before initiating major capital expenditures.
7. Strategic consolidation of operational units often yields significant cost savings during economic downturns.
8. By consolidating redundant departments, enterprises streamline internal communication and boost decision-making speed.
9. However, sudden structural changes can trigger internal resistance if organizational culture is neglected.
10. Therefore, effective change management communication must accompany every strategic realignment effort.
11. Market disruption driven by rapid artificial intelligence adoption presents both severe risks and lucrative horizons.
12. Firms that fail to leverage technological advancements risk fast-approaching market obsolescence and revenue decline.
13. Setting dynamic operational benchmarks allows executives to evaluate performance against top industry competitors.
14. These benchmarks must be updated quarterly to maintain relevance in rapidly shifting competitive environments.
15. Achieving seamless scalability requires scalable IT architectures capable of handling sudden spikes in consumer demand.
16. Without cloud-native infrastructure, expanding into emerging international markets becomes prohibitively expensive.
17. Startups and enterprise firms alike must know exactly when to pivot away from underperforming product lines.
18. A well-executed strategic pivot can reinvigorate growth and open completely unexploited revenue channels.
19. Economic stagnation remains an ever-present threat for organizations that cling stubbornly to outdated paradigms.
20. In conclusion, sustainable success belongs exclusively to businesses that embrace agility, continuous learning, and innovation.
"""
    reading_mcq = [
        {"q": "According to sentence 2, what must executive leadership do in volatile markets?", "options": ["Maintain baseline compliance only", "Move far beyond baseline compliance", "Reduce operational agility", "Ignore market volatility"], "a": "Move far beyond baseline compliance"},
        {"q": "What is the result of adopting rigorous feasibility frameworks (sentence 4)?", "options": ["Guaranteed revenue", "Resource alignment with strategic vision", "Higher tax liabilities", "Reduced workforce"], "a": "Resource alignment with strategic vision"},
        {"q": "Consolidating operational units primarily helps companies to (sentence 7):", "options": ["Increase overhead", "Achieve cost savings during downturns", "Delay decision-making", "Replace senior management"], "a": "Achieve cost savings during downturns"},
        {"q": "What risk do firms face if they ignore technological advancements (sentence 12)?", "options": ["Rapid international expansion", "Market obsolescence and revenue decline", "Improved benchmarks", "Zero disruption"], "a": "Market obsolescence and revenue decline"}
    ]
    reading_fitb = [
        {"q": "Economic _____ (sentence 19) remains a constant threat to static companies.", "a": "stagnation"},
        {"q": "Firms must set dynamic operational _____ (sentence 13) to evaluate performance.", "a": "benchmarks"},
        {"q": "A well-executed strategic _____ (sentence 18) can reinvigorate growth.", "a": "pivot"}
    ]

    listening_script = """
Good morning, ladies and gentlemen of the board, and welcome to our annual strategic roadmap presentation. Today, I will be addressing our operational performance under topic Executive Corporate Strategy, evaluating current market challenges, and presenting our multi-phase expansion framework.

Over the past four quarters, global markets have experienced unprecedented volatility, characterized by supply chain disruptions, fluctuating interest rates, and inflationary pressures. Despite these macroeconomic headwinds, our company has maintained remarkable resilience. Through a series of aggressive risk mitigation strategies, we successfully safeguarded our core revenue streams while expanding our market share in target territories.

A central driver of our success has been the decision to consolidate our regional operations. By merging redundant business units into centralized hubs, we reduced operating expenses by 18% while enhancing cross-departmental collaboration. This structural consolidation allowed us to reallocate capital into high-growth divisions, specifically our digital transformation initiatives.

Furthermore, we conducted rigorous feasibility studies prior to launching our cloud integration architecture. These studies confirmed that upgrading our legacy software would dramatically enhance operational scalability. As a result, our enterprise platform can now support a 200% increase in active users without suffering performance degradation or server downtime.

However, we must remain vigilant. Market disruption driven by AI automation is accelerating rapidly across our sector. Competitors who fail to adapt to these technological shifts are experiencing severe stagnation. To maintain our competitive edge, executive leadership has outlined three strategic priorities for the upcoming fiscal year.

First, we will continue to leverage predictive AI tools to optimize inventory management and reduce lead times. Second, we will establish clear performance benchmarks for all international subsidiaries to ensure quality control and brand alignment. Third, we will remain prepared to pivot our strategy rapidly should geopolitical or economic conditions deteriorate.

In conclusion, our strategic fundamentals remain rock-solid. By combining disciplined financial governance with aggressive technological innovation, we are uniquely positioned to deliver long-term value to our shareholders. Thank you for your continued confidence in our executive vision.
"""
    listening_mcq = [
        {"q": "By how much did structural consolidation reduce operating expenses?", "options": ["10%", "15%", "18%", "25%"], "a": "18%"},
        {"q": "What did the feasibility studies confirm regarding cloud integration?", "options": ["It would increase costs", "It would enhance operational scalability", "It was unnecessary", "It would cause server downtime"], "a": "It would enhance operational scalability"},
        {"q": "What capacity increase can the upgraded enterprise platform support?", "options": ["50%", "100%", "150%", "200%"], "a": "200%"},
        {"q": "What threat is affecting competitors who fail to adopt AI automation?", "options": ["Severe stagnation", "Rapid overfunding", "Lack of compliance", "Immediate bankruptcy"], "a": "Severe stagnation"}
    ]
    listening_fitb = [
        {"q": "The company reallocated capital into high-growth _____ initiatives.", "a": "digital transformation"},
        {"q": "The company will continue to _____ predictive AI tools for inventory management.", "a": "leverage"},
        {"q": "Executive leadership established clear performance _____ for subsidiaries.", "a": "benchmarks"}
    ]

    writing_prompt = f"""
**Context & Current Situation:**
You are the Chief Strategy Officer (CSO) at a mid-sized fintech corporation struggling with rising operational costs (up 22% YoY) and increased market competition. The CEO has requested an immediate executive memo proposing a strategic pivot.

**Requirements & Expectation:**
Write an executive memo (200-250 words) addressed to the Board of Directors.
- Detail the current operational challenges.
- Propose 2-3 concrete strategic initiatives (e.g., resource consolidation, AI automation).
- Clearly define expected KPIs (e.g., 15% cost reduction, market share stability).
- Incorporate at least 3 C1 vocabulary words from today's lesson (e.g., consolidate, mitigate, leverage, benchmark).
"""

    speaking_prompt = f"""
**Context & Current Situation:**
You are heading the Business Development division. Your sector is currently facing severe economic stagnation and new regulatory hurdles. You are presenting at an emergency Board meeting to request a $2M budget allocation for strategic realignment.

**Requirements & Expectation:**
Deliver a 2-minute executive pitch (150-200 words) convincing the Board to approve the budget.
- Describe the current crisis/situation.
- Explain why continuing current operations is unacceptable.
- Pitch your strategic solution using at least 3 C1 words (e.g., pivot, feasibility, scalability).
- End with a strong persuasive conclusion on ROI expectations.
"""

    translation = [
        {"id": 1, "vn": "Chúng tôi cần củng cố vị thế thị trường trước khi mở rộng quy mô.", "en": "We need to consolidate our market position before scaling up."},
        {"id": 2, "vn": "Nghiên cứu tính khả thi đã chỉ ra những rủi ro tài chính tiềm ẩn.", "en": "The feasibility study highlighted potential financial risks."},
        {"id": 3, "vn": "Doanh nghiệp phải tận dụng công nghệ AI để tối ưu hóa quy trình.", "en": "The business must leverage AI technology to optimize workflows."},
        {"id": 4, "vn": "Sự đứt gãy chuỗi cung ứng đã gây ra thiệt hại chưa từng có.", "en": "The supply chain disruption caused unprecedented damages."},
        {"id": 5, "vn": "Tiêu chuẩn đánh giá này giúp kiểm soát chất lượng dự án.", "en": "This benchmark helps control project quality."},
        {"id": 6, "vn": "Nhóm nghiên cứu đã đề xuất giải pháp giảm thiểu rủi ro vận hành.", "en": "The research team proposed solutions to mitigate operational risks."},
        {"id": 7, "vn": "Khả năng mở rộng của nền tảng này là ưu điểm cạnh tranh lớn.", "en": "The scalability of this platform is a major competitive advantage."},
        {"id": 8, "vn": "Công ty đã chuyển hướng chiến lược sang mô hình kinh doanh B2B.", "en": "The company pivoted its strategy to a B2B business model."},
        {"id": 9, "vn": "Sự trì trệ kinh tế ảnh hưởng trực tiếp đến doanh thu quý 3.", "en": "Economic stagnation directly impacted Q3 revenue."},
        {"id": 10, "vn": "Nếu ban giám đốc chấp thuận, chúng tôi sẽ triển khai kế hoạch ngay.", "en": "Should the board approve, we will implement the plan immediately."}
    ]

    return {
        "title": f"Day {day_num}: {topic} (B2 → C1 Level)",
        "topic": topic,
        "vocab": vocab,
        "pronunciation": pronunciation,
        "grammar": {
            "title": "Inversion in Advanced Business Conditionals (C1 Grammar)",
            "theory": grammar_theory,
            "mcq": grammar_mcq,
            "fitb": grammar_fitb
        },
        "reading": {
            "title": f"Executive Summary: Navigating {topic}",
            "text": reading_text,
            "mcq": reading_mcq,
            "fitb": reading_fitb
        },
        "listening": {
            "script": listening_script,
            "mcq": listening_mcq,
            "fitb": listening_fitb
        },
        "writing": writing_prompt,
        "speaking": speaking_prompt,
        "translation": translation
    }

# ==========================================
# 6. MAIN APPLICATION & 8 SKILL TABS
# ==========================================
def main():
    st.sidebar.title("⚡ AI English Studio")
    st.sidebar.caption("Roadmap B2 → C1 Mastery (30 Days)")

    # Groq API Input Fix
    api_key_in = st.sidebar.text_input("🔑 Groq API Key:", value=st.session_state.groq_api_key, type="password")
    if api_key_in != st.session_state.groq_api_key:
        st.session_state.groq_api_key = api_key_in.strip()

    st.sidebar.divider()
    
    # Save Progress Button
    if st.sidebar.button("💾 SAVE PROGRESS"):
        save_data_to_file()

    st.sidebar.divider()

    comp_len = len(st.session_state.completed_days)
    st.sidebar.write(f"**Course Progress:** {comp_len}/30 Days ({int(comp_len/30*100)}%)")
    st.sidebar.progress(comp_len / 30.0)

    selected_day = st.sidebar.selectbox(
        "📅 Select Lesson Day:",
        options=list(range(1, 31)),
        format_func=lambda x: f"Day {x}: {get_curriculum_day(x)['topic']}"
    )

    if st.sidebar.checkbox("Mark Day as Completed", value=(selected_day in st.session_state.completed_days)):
        st.session_state.completed_days.add(selected_day)
    else:
        st.session_state.completed_days.discard(selected_day)

    day_data = get_curriculum_day(selected_day)

    # Main Header
    st.markdown(
        f"""
        <div class="studio-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="badge-c1">C1 LEVEL MASTERY</span>
                    <h2 style="margin-top: 8px; margin-bottom: 4px;">{day_data['title']}</h2>
                    <p style="color: #4A5568 !important; margin: 0;">Main Topic: <b>{day_data['topic']}</b></p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
        "🔤 Vocabulary & Games",
        "🗣️ Pronunciation",
        "📐 Grammar Rules",
        "📖 Reading",
        "🎧 Listening Briefing",
        "✍️ Detailed Writing",
        "📊 Speaking Pitch",
        "🌐 Translation Practice"
    ])

    # ------------------------------------------
    # TAB 1: VOCABULARY & GAMES (SỬA LỖI 3 & 4)
    # ------------------------------------------
    with t1:
        st.subheader("📚 10 C1 Vocabulary Words of the Day")
        cols = st.columns(2)
        for idx, v in enumerate(day_data["vocab"]):
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div class="studio-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0;">{idx+1}. {v['word']}</h3>
                            <span class="badge-b2">{v['pos']}</span>
                        </div>
                        <p style="margin-top:8px;"><b>Meaning (EN):</b> {v['en']}</p>
                        <p><b>Synonyms:</b> <code>{v['syn']}</code></p>
                        <p><b>Example:</b> <i>"{v['example']}"</i></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                render_tts_button(v['word'], f"vocab_{selected_day}_{idx}")

        st.divider()
        st.subheader("🎮 Vocabulary Games Practice")

        # GAME 1
        st.markdown("### 🕹️ Game 1: C1 Word Definition Quiz (5 Questions)")
        for i in range(5):
            w = day_data["vocab"][i]
            st.markdown(f"**Question {i+1}:** What is the correct definition of **\"{w['word']}\"**?")
            opts = [w['en'], day_data["vocab"][(i+1)%10]['en'], day_data["vocab"][(i+2)%10]['en'], day_data["vocab"][(i+3)%10]['en']]
            random.seed(i + selected_day)
            random.shuffle(opts)
            
            key_g1 = f"g1_q_{selected_day}_{i}"
            curr_val = get_user_ans(key_g1, opts[0])
            ans = st.radio(
                f"Select option Q{i+1}:", 
                opts, 
                index=opts.index(curr_val) if curr_val in opts else 0,
                key=key_g1
            )
            set_user_ans(key_g1, ans)

        if st.button("Check Game 1 Answers", key="btn_check_g1"):
            st.markdown("#### 📋 Detailed Results - Game 1:")
            score_g1 = 0
            for i in range(5):
                w = day_data["vocab"][i]
                u_a = get_user_ans(f"g1_q_{selected_day}_{i}")
                is_correct = (u_a == w['en'])
                if is_correct:
                    score_g1 += 1
                    st.success(f"**Question {i+1} ({w['word']}):** ✅ Correct!\n- Your Answer: {u_a}")
                else:
                    st.error(f"**Question {i+1} ({w['word']}):** ❌ Incorrect!\n- Your Answer: {u_a}\n- **Correct Answer:** {w['en']}")
            st.info(f"🏆 Total Score Game 1: {score_g1}/5")

        st.divider()

        # GAME 2
        st.markdown("### 🧩 Game 2: Context Sentence Fill-in-the-blank (5 Questions)")
        for i in range(5, 10):
            w = day_data["vocab"][i]
            sentence = w["example"].replace(w["word"], "________").replace(w["word"].lower(), "________")
            st.markdown(f"**Question {i-4}:** Fill in the blank: *\"{sentence}\"*")
            
            key_g2 = f"g2_q_{selected_day}_{i}"
            curr_val = get_user_ans(key_g2, "")
            u_ans = st.text_input(f"Enter word Q{i-4}:", value=curr_val, key=key_g2)
            set_user_ans(key_g2, u_ans)

        if st.button("Check Game 2 Answers", key="btn_check_g2"):
            st.markdown("#### 📋 Detailed Results - Game 2:")
            score_g2 = 0
            for i in range(5, 10):
                w = day_data["vocab"][i]
                u_a = get_user_ans(f"g2_q_{selected_day}_{i}")
                is_correct = (u_a.strip().lower() == w["word"].lower())
                if is_correct:
                    score_g2 += 1
                    st.success(f"**Question {i-4}:** ✅ Correct!\n- Your Answer: {u_a}")
                else:
                    st.error(f"**Question {i-4}:** ❌ Incorrect!\n- Your Answer: {u_a if u_a else '(Blank)'}\n- **Correct Answer:** {w['word']}")
            st.info(f"🏆 Total Score Game 2: {score_g2}/5")

    # ------------------------------------------
    # TAB 2: PRONUNCIATION
    # ------------------------------------------
    with t2:
        st.subheader("🗣️ C1 Pronunciation & Intonation Drills")
        st.caption("Practice 3 advanced paragraph drills. Record your audio to receive AI intonation, stress, and pronunciation scoring:")
        for idx, p in enumerate(day_data["pronunciation"]):
            st.markdown(f"<div class='studio-card'><h4>Paragraph {idx+1}</h4></div>", unsafe_allow_html=True)
            record_and_evaluate_speech(p, label=f"pron_tab_{selected_day}_{idx}")

    # ------------------------------------------
    # TAB 3: GRAMMAR RULES (SỬA LỖI 3 & 4)
    # ------------------------------------------
    with t3:
        st.subheader(f"📐 {day_data['grammar']['title']}")
        st.markdown(f"<div class='studio-card'>{day_data['grammar']['theory']}</div>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Grammar Practice Assessment (10 Questions Total)")
        st.markdown("#### Part 1: Multiple Choice Questions (5 Questions)")
        for idx, q in enumerate(day_data["grammar"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            key_g_mcq = f"g_mcq_{selected_day}_{idx}"
            curr_val = get_user_ans(key_g_mcq, q['options'][0])
            u_ans = st.radio(
                f"Select option Q{idx+1}:", 
                q['options'], 
                index=q['options'].index(curr_val) if curr_val in q['options'] else 0,
                key=key_g_mcq
            )
            set_user_ans(key_g_mcq, u_ans)

        st.markdown("#### Part 2: Fill-in-the-blank Questions (5 Questions)")
        for idx, q in enumerate(day_data["grammar"]["fitb"]):
            st.write(f"**Q{idx+6}:** {q['q']}")
            key_g_fitb = f"g_fitb_{selected_day}_{idx}"
            curr_val = get_user_ans(key_g_fitb, "")
            u_ans = st.text_input(f"Enter answer Q{idx+6}:", value=curr_val, key=key_g_fitb)
            set_user_ans(key_g_fitb, u_ans)

        if st.button("Check Grammar Answers", key="btn_check_grammar"):
            st.markdown("#### 📋 Detailed Grammar Evaluation:")
            g_score = 0
            for idx, q in enumerate(day_data["grammar"]["mcq"]):
                u_a = get_user_ans(f"g_mcq_{selected_day}_{idx}")
                if u_a == q['a']:
                    g_score += 1
                    st.success(f"**Q{idx+1}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+1}:** ❌ Incorrect! Your Answer: {u_a} | **Correct Answer:** {q['a']}")

            for idx, q in enumerate(day_data["grammar"]["fitb"]):
                u_a = get_user_ans(f"g_fitb_{selected_day}_{idx}")
                if u_a.strip().lower() == q['a'].lower():
                    g_score += 1
                    st.success(f"**Q{idx+6}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+6}:** ❌ Incorrect! Your Answer: {u_a if u_a else '(Blank)'} | **Correct Answer:** {q['a']}")
            st.info(f"🏆 Grammar Total Score: {g_score}/10")

    # ------------------------------------------
    # TAB 4: READING (SỬA LỖI 3 & 4)
    # ------------------------------------------
    with t4:
        st.subheader(f"📖 {day_data['reading']['title']}")
        st.markdown(f"<div class='studio-card'><p style='font-size:15px; line-height:1.8;'>{day_data['reading']['text']}</p></div>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Reading Comprehension (7 Questions Total)")
        st.markdown("#### Part 1: Multiple Choice Questions")
        for idx, q in enumerate(day_data["reading"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            key_r_mcq = f"r_mcq_{selected_day}_{idx}"
            curr_val = get_user_ans(key_r_mcq, q['options'][0])
            u_ans = st.radio(
                f"Select option R{idx+1}:", 
                q['options'], 
                index=q['options'].index(curr_val) if curr_val in q['options'] else 0,
                key=key_r_mcq
            )
            set_user_ans(key_r_mcq, u_ans)

        st.markdown("#### Part 2: Fill-in-the-blank Questions")
        for idx, q in enumerate(day_data["reading"]["fitb"]):
            st.write(f"**Q{idx+5}:** {q['q']}")
            key_r_fitb = f"r_fitb_{selected_day}_{idx}"
            curr_val = get_user_ans(key_r_fitb, "")
            u_ans = st.text_input(f"Enter word R{idx+5}:", value=curr_val, key=key_r_fitb)
            set_user_ans(key_r_fitb, u_ans)

        if st.button("Check Reading Answers", key="btn_check_reading"):
            st.markdown("#### 📋 Detailed Reading Evaluation:")
            r_score = 0
            for idx, q in enumerate(day_data["reading"]["mcq"]):
                u_a = get_user_ans(f"r_mcq_{selected_day}_{idx}")
                if u_a == q['a']:
                    r_score += 1
                    st.success(f"**Q{idx+1}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+1}:** ❌ Incorrect! Your Answer: {u_a} | **Correct Answer:** {q['a']}")

            for idx, q in enumerate(day_data["reading"]["fitb"]):
                u_a = get_user_ans(f"r_fitb_{selected_day}_{idx}")
                if u_a.strip().lower() == q['a'].lower():
                    r_score += 1
                    st.success(f"**Q{idx+5}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+5}:** ❌ Incorrect! Your Answer: {u_a if u_a else '(Blank)'} | **Correct Answer:** {q['a']}")
            st.info(f"🏆 Reading Total Score: {r_score}/7")

    # ------------------------------------------
    # TAB 5: LISTENING (SỬA LỖI 3 & 4)
    # ------------------------------------------
    with t5:
        st.subheader("🎧 Business Audio Briefing Script (~3 Minutes Read)")
        st.markdown(f"<div class='studio-card'><p style='font-size:15px; line-height:1.8;'><i>\"{day_data['listening']['script']}\"</i></p></div>", unsafe_allow_html=True)
        render_tts_button(day_data['listening']['script'], f"listen_script_{selected_day}")
        
        st.markdown("### 📝 Listening Comprehension Exercises (7 Questions Total)")
        st.markdown("#### Part 1: Multiple Choice Questions")
        for idx, q in enumerate(day_data["listening"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            key_l_mcq = f"l_mcq_{selected_day}_{idx}"
            curr_val = get_user_ans(key_l_mcq, q['options'][0])
            u_ans = st.radio(
                f"Select option L{idx+1}:", 
                q['options'], 
                index=q['options'].index(curr_val) if curr_val in q['options'] else 0,
                key=key_l_mcq
            )
            set_user_ans(key_l_mcq, u_ans)

        st.markdown("#### Part 2: Fill-in-the-blank Questions")
        for idx, q in enumerate(day_data["listening"]["fitb"]):
            st.write(f"**Q{idx+5}:** {q['q']}")
            key_l_fitb = f"l_fitb_{selected_day}_{idx}"
            curr_val = get_user_ans(key_l_fitb, "")
            u_ans = st.text_input(f"Enter answer L{idx+5}:", value=curr_val, key=key_l_fitb)
            set_user_ans(key_l_fitb, u_ans)

        if st.button("Check Listening Answers", key="btn_check_listening"):
            st.markdown("#### 📋 Detailed Listening Evaluation:")
            l_score = 0
            for idx, q in enumerate(day_data["listening"]["mcq"]):
                u_a = get_user_ans(f"l_mcq_{selected_day}_{idx}")
                if u_a == q['a']:
                    l_score += 1
                    st.success(f"**Q{idx+1}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+1}:** ❌ Incorrect! Your Answer: {u_a} | **Correct Answer:** {q['a']}")

            for idx, q in enumerate(day_data["listening"]["fitb"]):
                u_a = get_user_ans(f"l_fitb_{selected_day}_{idx}")
                if u_a.strip().lower() == q['a'].lower():
                    l_score += 1
                    st.success(f"**Q{idx+5}:** ✅ Correct! ({u_a})")
                else:
                    st.error(f"**Q{idx+5}:** ❌ Incorrect! Your Answer: {u_a if u_a else '(Blank)'} | **Correct Answer:** {q['a']}")
            st.info(f"🏆 Listening Total Score: {l_score}/7")

    # ------------------------------------------
    # TAB 6: WRITING
    # ------------------------------------------
    with t6:
        st.subheader("✍️ C1 Executive Writing Scenario")
        st.markdown(f"<div class='studio-card'>{day_data['writing']}</div>", unsafe_allow_html=True)
        
        key_w = f"w_essay_{selected_day}"
        curr_val = get_user_ans(key_w, "")
        user_writer = st.text_area("Write your response in English:", value=curr_val, height=220, key=key_w)
        set_user_ans(key_w, user_writer)

        if st.button("🚀 AI Evaluation & C1 Upgrade Feedback"):
            if not user_writer.strip():
                st.warning("Please enter your essay before submitting!")
            else:
                with st.spinner("C1 AI Examiner is evaluating your writing..."):
                    prompt = f"""
                    Evaluate this C1 Business English Writing Task strictly in English:
                    Task Prompt: "{day_data['writing']}"
                    Student Submission: "{user_writer}"

                    Provide structured feedback:
                    1. Band Score (/10) for Task Achievement, Vocabulary, and Grammar.
                    2. Grammar & Vocabulary Errors with explanations.
                    3. Executive C1 Rewritten Version (Polished Professional Draft).
                    """
                    res = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if res:
                        st.markdown(f"<div class='studio-card'>{res}</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 7: SPEAKING
    # ------------------------------------------
    with t7:
        st.subheader("📊 Executive Speaking Pitch")
        st.markdown(f"<div class='studio-card'>{day_data['speaking']}</div>", unsafe_allow_html=True)
        record_and_evaluate_speech(day_data['speaking'], label=f"speak_pitch_{selected_day}", context_info=day_data['speaking'])

    # ------------------------------------------
    # TAB 8: TRANSLATION (SỬA LỖI 3 & 4)
    # ------------------------------------------
    with t8:
        st.subheader("🌐 C1 Sentence-by-Sentence Translation Practice")
        st.caption("Translate each Vietnamese sentence to English below. Click evaluate per sentence for instant learning:")
        
        for idx, t_item in enumerate(day_data["translation"]):
            st.markdown(f"<div class='studio-card'><b>Sentence {t_item['id']}:</b> {t_item['vn']}</div>", unsafe_allow_html=True)
            
            key_trans = f"single_trans_{selected_day}_{idx}"
            curr_val = get_user_ans(key_trans, "")
            u_trans = st.text_input(f"Your Translation for Sentence {t_item['id']}:", value=curr_val, key=key_trans)
            set_user_ans(key_trans, u_trans)
            
            if st.button(f"🎯 Evaluate Sentence {t_item['id']}", key=f"btn_trans_{selected_day}_{idx}"):
                if not u_trans.strip():
                    st.warning("Please enter translation first!")
                else:
                    with st.spinner(f"Evaluating Sentence {t_item['id']}..."):
                        prompt_single = f"""
                        Evaluate this single sentence translation from Vietnamese to C1 English:
                        - Original VN: "{t_item['vn']}"
                        - Ideal Reference EN: "{t_item['en']}"
                        - Student Translation: "{u_trans}"

                        Provide detailed feedback strictly in English:
                        1. Score (/10)
                        2. Accuracy & C1 Vocabulary usage
                        3. Exact mistakes in student's response vs correct reference
                        4. Polished C1 Alternative
                        """
                        res_single = call_groq_llm(prompt_single, st.session_state.groq_api_key)
                        if res_single:
                            st.markdown(f"<div class='studio-card'>{res_single}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()