import json
import os
import random
import tempfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIG & STYLING (GOOGLE STUDIO PINK/WHITE THEME)
# ==========================================
st.set_page_config(
    page_title="IELTS & Business English Studio B2->C1 (30 Days)",
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
        border-right: 1px solid #FED7D7 !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label {
        color: #1A202C !important;
    }

    /* Force Selectbox & Inputs to White Background & Dark Text */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stTextInput input,
    .stTextArea textarea,
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

    /* Studio Cards */
    .studio-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
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
# 3. API & DATA PERSISTENCE
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

# Auto-get API Key from secrets or input
if "groq_api_key" not in st.session_state:
    secret_key = ""
    try:
        if "GROQ_API_KEY" in st.secrets:
            secret_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    st.session_state.groq_api_key = secret_key

if "user_answers" not in st.session_state:
    st.session_state.user_answers = saved_data.get("user_answers", {})

if "audio_recordings" not in st.session_state:
    st.session_state.audio_recordings = {}

def get_user_ans(key, default=""):
    return st.session_state.user_answers.get(key, default)

def set_user_ans(key, val):
    st.session_state.user_answers[key] = val

def call_groq_llm(prompt, api_key):
    if not api_key:
        st.error("Please configure your Groq API Key in Streamlit Secrets or Sidebar!")
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
                st.error("Invalid Groq API Key! Please verify your key.")
                return None
        except Exception:
            continue
    st.error("Groq API Connection Failed.")
    return None

def transcribe_audio_groq(audio_bytes, api_key):
    if not api_key:
        st.error("Please configure your Groq API Key!")
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

# ==========================================
# 4. SPEECH EVALUATION COMPONENT
# ==========================================
def record_and_evaluate_speech(reference_text, label, context_info=""):
    st.markdown(f"**Target Text/Context:** *\"{reference_text}\"*")
    render_tts_button(reference_text, f"tts_{hash(label+reference_text)}")
    
    rec_key = f"rec_{hash(label)}"
    audio_val = st.audio_input("Click mic to record your voice:", key=rec_key)
    
    if audio_val:
        st.session_state.audio_recordings[label] = audio_val.read()
        
    if label in st.session_state.audio_recordings:
        st.markdown("**Your Recorded Audio:**")
        st.audio(st.session_state.audio_recordings[label], format="audio/wav")
        
        if st.button("🎯 Analyze Pronunciation & Intonation AI", key=f"btn_{hash(label)}"):
            with st.spinner("AI is analyzing speech..."):
                audio_bytes = st.session_state.audio_recordings[label]
                transcribed = transcribe_audio_groq(audio_bytes, st.session_state.groq_api_key)
                if transcribed:
                    st.info(f"📝 **AI Transcribed Speech:** \"{transcribed}\"")
                    prompt = f"""
                    Evaluate C1/IELTS Speaking performance strictly in English:
                    - Reference/Prompt: "{reference_text}"
                    - Context Info: "{context_info}"
                    - Student Spoke: "{transcribed}"

                    Provide structured feedback in standard English:
                    1. Overall Score (/10)
                    2. Pronunciation & Word Stress Accuracy
                    3. Sentence Intonation & Rhythm
                    4. Relevance to Context & Content Quality
                    5. Detailed Mistakes & Specific Corrections
                    """
                    feedback = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if feedback:
                        st.markdown(f"<div class='studio-card'>{feedback}</div>", unsafe_allow_html=True)

# ==========================================
# 5. CURRICULUM GENERATOR (DAYS 1 TO 30)
# ==========================================
def get_curriculum_day(day_num):
    topics = [
        "Executive Corporate Strategy", "Cross-Border Negotiations", "Financial Risk Mitigation",
        "Change Management & Agility", "Brand Reputation & Crisis Management", "Digital Transformation & Cloud",
        "Supply Chain Resilience", "Mergers & Acquisitions Realignment", "ESG & Corporate Governance",
        "AI & Business Automation"
    ]
    topic = topics[(day_num - 1) % len(topics)]
    
    vocab = [
        {"word": "Consolidate", "pos": "verb", "en": "To combine into a single, stronger unit.", "syn": "Merge, Strengthen", "example": "The company plans to consolidate its position in the European market."},
        {"word": "Feasibility", "pos": "noun", "en": "The degree to which something is possible or practical.", "syn": "Viability, Practicability", "example": "We conducted a comprehensive feasibility study before launching the project."},
        {"word": "Disruption", "pos": "noun", "en": "Disturbance or problems that interrupt an event or process.", "syn": "Upheaval, Disturbance", "example": "AI technology is causing massive disruption across traditional service industries."},
        {"word": "Benchmark", "pos": "noun", "en": "A standard or point of reference against which things may be measured.", "syn": "Criterion, Yardstick", "example": "Our Q3 performance set a new benchmark for corporate productivity."},
        {"word": "Mitigate", "pos": "verb", "en": "Make less severe, serious, or painful.", "syn": "Alleviate, Moderate", "example": "Immediate steps were taken to mitigate the financial risk of the market downturn."},
        {"word": "Leverage", "pos": "verb", "en": "Use something to maximum advantage.", "syn": "Exploit, Utilize", "example": "We must leverage our brand equity to launch new digital product lines."},
        {"word": "Scalability", "pos": "noun", "en": "Ability of a computing or business system to handle growing work.", "syn": "Expandability", "example": "Cloud architecture offers incredible enterprise scalability for global operations."},
        {"word": "Pivot", "pos": "verb", "en": "Change strategic direction abruptly.", "syn": "Shift, Reorient", "example": "The startup pivoted from a consumer app to an enterprise SaaS model."},
        {"word": "Stagnation", "pos": "noun", "en": "State of not flowing, moving, or changing.", "syn": "Inaction, Standstill", "example": "Economic stagnation led to reduced venture capital investments."},
        {"word": "Unprecedented", "pos": "adj", "en": "Never done or known before.", "syn": "Unparalleled, Novel", "example": "The tech sector experienced unprecedented growth during the last decade."}
    ]

    vocab_mcq = [
        {"q": "Which word means 'to combine into a single, stronger unit'?", "options": ["Pivot", "Consolidate", "Mitigate", "Leverage"], "a": "Consolidate"},
        {"q": "Choose the synonym for 'Viability':", "options": ["Stagnation", "Feasibility", "Disruption", "Benchmark"], "a": "Feasibility"},
        {"q": "What is the best word for 'making something less severe'?", "options": ["Mitigate", "Pivot", "Scalability", "Consolidate"], "a": "Mitigate"},
        {"q": "Select the antonym of 'Continuous Growth':", "options": ["Scalability", "Benchmark", "Stagnation", "Disruption"], "a": "Stagnation"},
        {"q": "Which term refers to an established standard for comparison?", "options": ["Feasibility", "Benchmark", "Pivot", "Leverage"], "a": "Benchmark"}
    ]

    vocab_fitb = [
        {"q": "We need to _____ our resources to maximize market impact.", "a": "leverage"},
        {"q": "Cloud infrastructure ensures high operational _____.", "a": "scalability"},
        {"q": "The board decided to _____ away from declining legacy markets.", "a": "pivot"},
        {"q": "AI startup investments reached an _____ high this year.", "a": "unprecedented"},
        {"q": "Supply chain _____ forced factories to halt production.", "a": "disruption"}
    ]

    pronunciation = [
        f"Day {day_num} Focus 1: Our strategic initiatives have significantly consolidated our market position over the past fiscal year. Executive board members agreed to increase capital expenditure to expand digital infrastructure across all major operational hubs.",
        f"Day {day_num} Focus 2: To mitigate potential operational risks, leadership approved an unprecedented risk governance framework today. This multi-layered initiative systematically addresses cybersecurity vulnerabilities, compliance hurdles, and global supply chain bottlenecks.",
        f"Day {day_num} Focus 3: Leveraging digital scalability remains the primary benchmark for enterprise growth in this quarter. Companies failing to adapt their core infrastructure face severe market stagnation, declining margins, and sudden competitive obsolescence."
    ]

    grammar_theory = """
**Advanced Business Conditionals: Inversion Structure (C1 Level)**

In formal business writing and C1 level presentations, standard conditional sentences are often inverted to emphasize urgency, formality, and authority.

**1. Type 1 Conditional Inversion (Formal Future Possibilities):**
• *Standard:* If you require further clarification, please contact our legal counsel.
• *Inverted:* **Should you require further clarification,** please contact our legal counsel.

**2. Type 2 Conditional Inversion (Hypothetical Present/Future Scenarios):**
• *Standard:* If the market were to collapse, our contingency plan would take effect.
• *Inverted:* **Were the market to collapse,** our contingency plan would take effect.

**3. Type 3 Conditional Inversion (Hypothetical Past Scenarios):**
• *Standard:* If the board had approved the merger, our revenue would have doubled.
• *Inverted:* **Had the board approved the merger,** our revenue would have doubled.
"""

    grammar_mcq = [
        {"q": "_____ the executive committee mandate the budget, we will proceed immediately.", "options": ["Had", "Should", "Were", "Unless"], "a": "Should"},
        {"q": "_____ the company mitigated risks earlier, the losses would have been avoided.", "options": ["Were", "Had", "Should", "If only"], "a": "Had"},
        {"q": "_____ the price of raw materials to skyrocket, we would adjust our pricing strategy.", "options": ["Were", "Should", "Had", "If"], "a": "Were"},
        {"q": "Should you _____ any issues with compliance, notify the audit team immediately.", "options": ["encounter", "encountered", "encounters", "had encountered"], "a": "encounter"},
        {"q": "Had the CEO _____ the market trends, the product launch would not have failed.", "options": ["foreseen", "foresaw", "foresee", "foreseeing"], "a": "foreseen"}
    ]

    grammar_fitb = [
        {"q": "_____ the firm to pivot now, stakeholders might object strongly.", "a": "Were"},
        {"q": "Should you _____ additional leverage during negotiations, review clause 4.", "a": "need"},
        {"q": "_____ the board known about the disruption, they would have restructured earlier.", "a": "Had"},
        {"q": "Were we to _____ the supply chain, overhead costs would fall by 15%.", "a": "optimize"},
        {"q": "Should any partner _____ the compliance terms, the contract will terminate.", "a": "violate"}
    ]

    reading_text = f"""
1. In an era marked by unprecedented global market volatility, modern enterprise corporations face complex operational threats daily.
2. Navigating this dynamic landscape requires executive leadership to move far beyond mere baseline regulatory compliance.
3. Establishing long-term organizational sustainability demands proactive strategic planning, resource optimization, and robust agility.
4. Adopting rigorous feasibility frameworks ensures that financial capital and human resource allocations align with core strategic vision.
5. Furthermore, failure to mitigate systemic operational vulnerabilities frequently precipitates irreversible brand damage across international markets.
6. Corporate leaders must systematically analyze potential risk factors before initiating major capital expenditures or cross-border acquisitions.
7. Strategic consolidation of operational units often yields significant cost savings and structural resilience during economic downturns.
8. By consolidating redundant departments, global enterprises streamline internal communication and boost executive decision-making speed.
9. However, sudden structural changes can trigger internal resistance if organizational culture and employee alignment are neglected.
10. Therefore, effective change management communication must accompany every single strategic realignment effort across all business divisions.
11. Market disruption driven by rapid artificial intelligence adoption presents both severe operational risks and lucrative commercial horizons.
12. Corporate entities that fail to leverage technological advancements risk fast-approaching market obsolescence and severe revenue decline.
13. Setting dynamic operational benchmarks allows executives to evaluate organizational performance against top tier industry competitors.
14. These benchmarks must be updated quarterly to maintain relevance in rapidly shifting global market environments.
15. Achieving seamless global scalability requires cloud-native IT architectures capable of handling sudden spikes in consumer demand.
16. Without modern scalable infrastructure, expanding operational footprints into emerging international markets becomes prohibitively expensive.
17. Startups and established enterprise firms alike must know exactly when to pivot away from underperforming product lines.
18. A well-executed strategic pivot can reinvigorate corporate growth and open completely unexploited revenue channels.
19. Economic stagnation remains an ever-present threat for organizations that cling stubbornly to outdated operational paradigms.
20. In conclusion, sustainable commercial success belongs exclusively to businesses that embrace strategic agility, continuous innovation, and leadership excellence.
"""

    reading_mcq = [
        {"q": "According to sentence 2, what must executive leadership do in volatile markets?", "options": ["Maintain baseline compliance only", "Move far beyond baseline compliance", "Reduce operational agility", "Ignore market volatility"], "a": "Move far beyond baseline compliance"},
        {"q": "What is the primary benefit of adopting rigorous feasibility frameworks (sentence 4)?", "options": ["Guaranteed short-term profit", "Resource alignment with strategic vision", "Elimination of tax liabilities", "Automated employee hiring"], "a": "Resource alignment with strategic vision"},
        {"q": "Consolidating operational units primarily helps companies to (sentence 7):", "options": ["Increase overhead expenses", "Achieve cost savings during downturns", "Delay decision-making processes", "Replace senior board members"], "a": "Achieve cost savings during downturns"},
        {"q": "What major risk do firms face if they ignore technological advancements (sentence 12)?", "options": ["Rapid international expansion", "Market obsolescence and revenue decline", "Improved industry benchmarks", "Zero market disruption"], "a": "Market obsolescence and revenue decline"}
    ]

    reading_fitb = [
        {"q": "Economic _____ (sentence 19) remains a constant threat to static companies.", "a": "stagnation"},
        {"q": "Firms must set dynamic operational _____ (sentence 13) to evaluate performance.", "a": "benchmarks"},
        {"q": "A well-executed strategic _____ (sentence 18) can reinvigorate growth.", "a": "pivot"}
    ]

    listening_script = f"""
Good morning, members of the executive board, and welcome to our Day {day_num} strategic roadmap briefing focusing on {topic}.
Over the past four quarters, global markets have experienced unprecedented volatility, characterized by supply chain disruptions, fluctuating interest rates, and severe inflationary pressures.
Despite these macroeconomic headwinds, our enterprise has maintained remarkable structural resilience.
Through a series of aggressive risk mitigation strategies, we successfully safeguarded our core revenue streams while expanding market share in target territories.
A central driver of our recent performance has been the decision to consolidate regional operations.
By merging redundant business units into centralized hubs, we reduced operating expenses by 18% while enhancing cross-departmental collaboration.
This structural consolidation allowed us to reallocate capital into high-growth digital transformation initiatives.
Furthermore, we conducted rigorous feasibility studies prior to launching our enterprise cloud architecture.
These studies confirmed that upgrading our legacy software would dramatically enhance operational scalability.
As a result, our enterprise platform can now support a 200% increase in active users without suffering performance degradation or server downtime.
However, executive leadership must remain vigilant. Market disruption driven by AI automation is accelerating rapidly across our sector.
Competitors who fail to adapt to these technological shifts are experiencing severe market stagnation.
To maintain our competitive edge, we have outlined three strategic priorities:
First, we will continue to leverage predictive AI tools to optimize supply chain inventory management.
Second, we will establish clear performance benchmarks for all international subsidiaries.
Third, we remain prepared to pivot our market strategy rapidly should global economic conditions deteriorate.
Thank you for your continued confidence in our strategic vision.
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
**Business Context & Scenario (Day {day_num} - {topic}):**
You are the Chief Strategy Officer (CSO) at a mid-sized corporation struggling with rising operational costs (up 22% YoY) and aggressive market competition. The CEO has requested an immediate executive memo proposing a strategic pivot.

**Requirements & Expectations:**
Write an executive memo (200-250 words) addressed to the Executive Board:
1. Detail current operational challenges and financial risks.
2. Propose concrete strategic actions (e.g., consolidating units, leveraging AI, pivoting business model).
3. Outline expected benchmarks, feasibility metrics, and timeline for execution.
Use formal C1 Business English vocabulary (e.g., *mitigate, consolidate, leverage, feasibility, benchmark*).
"""

    writing_sample = f"""
**SUBJECT:** EXECUTIVE STRATEGIC REALIGNMENT & OPERATIONAL PIVOT MEMORANDUM

**TO:** Board of Directors  
**FROM:** Chief Strategy Officer  
**DATE:** October 24, 2026  

**1. Operational Assessment & Challenges** Over the preceding four quarters, our organization has faced unprecedented macroeconomic headwinds, resulting in a 22% increase in operational overhead. Current market fragmentation and aggressive competitor automation threaten our market share. Without immediate intervention, margin compression will lead to severe revenue stagnation.

**2. Proposed Strategic Realignment** To mitigate these systemic risks, executive leadership proposes a multi-phase strategic pivot focused on two primary levers:
* **Operational Consolidation:** We will consolidate four regional operational centers into two centralized digital hubs, reducing redundant administrative overhead by an estimated 18%.
* **Technological Leverage:** We will leverage enterprise AI automation to streamline supply chain logistics and customer acquisition workflows.

**3. Feasibility & Benchmarks** Preliminary feasibility studies indicate that this restructuring will require an initial capital expenditure of $1.5M, with full return on investment realized within 14 months. We will establish rigorous quarterly performance benchmarks to monitor transition efficiency and ensure seamless cross-departmental alignment. 

Prompt execution of this proposal will solidify our competitive position and secure long-term profitability.
"""

    speaking_prompt = f"Deliver a 2-minute executive presentation on '{topic}'. Detail how your company will mitigate current market disruption, leverage new technologies, and maintain operational benchmarks over the next fiscal year."

    translation_items = [
        {"id": 1, "vi": "Chúng tôi cần hợp nhất các bộ phận để cắt giảm chi phí vận hành.", "ref": "We need to consolidate departments to reduce operational expenses."},
        {"id": 2, "vi": "Báo cáo khả thi xác nhận rằng dự án mới rất đáng tin cậy.", "ref": "The feasibility report confirms that the new project is viable."},
        {"id": 3, "vi": "Sự gián đoạn công nghệ đang buộc các công ty phải thay đổi chiến lược.", "ref": "Technological disruption is forcing companies to pivot their strategies."},
        {"id": 4, "vi": "Chúng ta phải thiết lập một tiêu chuẩn mới cho chất lượng dịch vụ.", "ref": "We must establish a new benchmark for service quality."},
        {"id": 5, "vi": "Các biện pháp khắc phục rủi ro tài chính đã được phê duyệt.", "ref": "Financial risk mitigation measures have been approved."},
        {"id": 6, "vi": "Tập đoàn sẽ tận dụng trí tuệ nhân tạo để tối ưu hóa quy trình.", "ref": "The corporation will leverage artificial intelligence to optimize workflows."},
        {"id": 7, "vi": "Khả năng mở rộng của nền tảng đám mây là cực kỳ quan trọng.", "ref": "The scalability of the cloud platform is extremely crucial."},
        {"id": 8, "vi": "Họ đã chuyển hướng mô hình kinh doanh từ B2C sang B2B.", "ref": "They pivoted their business model from B2C to B2B."},
        {"id": 9, "vi": "Sự trệch hướng kinh tế đã ảnh hưởng lớn đến doanh thu quý này.", "ref": "Economic stagnation significantly impacted revenue this quarter."},
        {"id": 10, "vi": "Công ty đã đạt mức tăng trưởng chưa từng có trong lịch sử.", "ref": "The company achieved unprecedented growth in its history."}
    ]

    return {
        "topic": topic,
        "vocab": vocab,
        "vocab_mcq": vocab_mcq,
        "vocab_fitb": vocab_fitb,
        "pronunciation": pronunciation,
        "grammar_theory": grammar_theory,
        "grammar_mcq": grammar_mcq,
        "grammar_fitb": grammar_fitb,
        "reading_text": reading_text,
        "reading_mcq": reading_mcq,
        "reading_fitb": reading_fitb,
        "listening_script": listening_script,
        "listening_mcq": listening_mcq,
        "listening_fitb": listening_fitb,
        "writing_prompt": writing_prompt,
        "writing_sample": writing_sample,
        "speaking_prompt": speaking_prompt,
        "translation_items": translation_items
    }

# ==========================================
# 6. MAIN APPLICATION LAYOUT
# ==========================================
def main():
    # Sidebar
    st.sidebar.title("🎓 IELTS & Business C1")
    st.sidebar.subheader("30-Day Executive Studio")

    # API Key check/input
    if not st.session_state.groq_api_key:
        api_input = st.sidebar.text_input("Groq API Key:", type="password", help="Enter Groq API Key if not set in secrets")
        if api_input:
            st.session_state.groq_api_key = api_input
    else:
        st.sidebar.success("🔑 API Key Active", icon="✅")

    # Select Day
    selected_day = st.sidebar.selectbox("Select Learning Day:", range(1, 31), format_func=lambda x: f"Day {x:02d}")
    day_data = get_curriculum_day(selected_day)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current Topic:**\n*{day_data['topic']}*")
    
    # Progress & Mark Completed
    if selected_day in st.session_state.completed_days:
        st.sidebar.success(f"Status: Day {selected_day} Completed!", icon="🎉")
    else:
        st.sidebar.info(f"Status: Day {selected_day} In Progress", icon="📖")

    col_save, col_mark = st.sidebar.columns(2)
    with col_save:
        if st.button("💾 Save Progress"):
            save_data_to_file()
    with col_mark:
        if st.button("✅ Complete Day"):
            st.session_state.completed_days.add(selected_day)
            save_data_to_file()
            st.rerun()

    # Main Header
    st.title(f"⚡ Day {selected_day:02d}: {day_data['topic']}")
    st.markdown("<span class='badge-b2'>LEVEL B2</span> ➔ <span class='badge-c1'>TARGET LEVEL C1</span>", unsafe_allow_html=True)
    st.write("")

    # Tabs for 8 Skills
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🔤 Vocab & Games",
        "🗣️ Pronunciation",
        "📐 Grammar Rules",
        "📖 Reading",
        "🎧 Listening",
        "✍️ Detailed Writing",
        "📊 Speaking Presentation",
        "🌐 Translation Practice"
    ])

    # 1. Vocab & Games
    with tab1:
        st.subheader("🔤 C1 Target Vocabulary (10 Words)")
        for idx, item in enumerate(day_data["vocab"]):
            with st.container():
                st.markdown(f"""
                <div class='studio-card'>
                    <h4>{idx+1}. {item['word']} <small style='font-size:14px; color:#718096;'>({item['pos']})</small></h4>
                    <p><b>English Meaning:</b> {item['en']}</p>
                    <p><b>Synonyms:</b> <code>{item['syn']}</code></p>
                    <p><b>Example:</b> <i>"{item['example']}"</i></p>
                </div>
                """, unsafe_allow_html=True)
                render_tts_button(f"{item['word']}. {item['example']}", f"v_{selected_day}_{idx}")

        st.markdown("---")
        st.subheader("🎮 Practice Games")
        
        st.markdown("#### Game 1: Multiple Choice Vocabulary")
        for idx, q_data in enumerate(day_data["vocab_mcq"]):
            k_mcq = f"v_mcq_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_mcq, "")
            user_sel = st.radio(f"Q{idx+1}: {q_data['q']}", q_data['options'], index=q_data['options'].index(curr_ans) if curr_ans in q_data['options'] else 0, key=k_mcq)
            set_user_ans(k_mcq, user_sel)
            
            if user_sel == q_data["a"]:
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            else:
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

        st.markdown("#### Game 2: Fill in the Context")
        for idx, q_data in enumerate(day_data["vocab_fitb"]):
            k_fitb = f"v_fitb_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_fitb, "")
            user_in = st.text_input(f"Q{idx+1}: {q_data['q']}", value=curr_ans, key=k_fitb)
            set_user_ans(k_fitb, user_in)
            
            if user_in.strip().lower() == q_data["a"].lower():
                st.success(f"✅ Correct! Word: {q_data['a']}")
            elif user_in.strip():
                st.error(f"❌ Incorrect. Expected Word: {q_data['a']}")

    # 2. Pronunciation
    with tab2:
        st.subheader("🗣️ Pronunciation & Intonation Training")
        for idx, text_block in enumerate(day_data["pronunciation"]):
            st.markdown(f"<div class='studio-card'><b>Passage {idx+1}:</b></div>", unsafe_allow_html=True)
            record_and_evaluate_speech(text_block, label=f"Pronunciation_Day{selected_day}_P{idx+1}")
            st.write("")

    # 3. Grammar Rules
    with tab3:
        st.subheader("📐 Grammar Rules & Structure")
        st.markdown(f"<div class='studio-card'>{day_data['grammar_theory']}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📝 Grammar Test (10 Questions)")
        
        st.markdown("##### Part 1: Multiple Choice (5 Questions)")
        for idx, q_data in enumerate(day_data["grammar_mcq"]):
            k_gmcq = f"g_mcq_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_gmcq, "")
            user_sel = st.radio(f"Q{idx+1}: {q_data['q']}", q_data['options'], index=q_data['options'].index(curr_ans) if curr_ans in q_data['options'] else 0, key=k_gmcq)
            set_user_ans(k_gmcq, user_sel)
            
            if user_sel == q_data["a"]:
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            else:
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

        st.markdown("##### Part 2: Fill in the Blank (5 Questions)")
        for idx, q_data in enumerate(day_data["grammar_fitb"]):
            k_gfitb = f"g_fitb_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_gfitb, "")
            user_in = st.text_input(f"Q{idx+6}: {q_data['q']}", value=curr_ans, key=k_gfitb)
            set_user_ans(k_gfitb, user_in)
            
            if user_in.strip().lower() == q_data["a"].lower():
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            elif user_in.strip():
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

    # 4. Reading
    with tab4:
        st.subheader("📖 Business Reading Passages (20 Sentences)")
        st.markdown(f"<div class='studio-card'><pre style='white-space: pre-wrap; font-family: Inter;'>{day_data['reading_text']}</pre></div>", unsafe_allow_html=True)
        render_tts_button(day_data['reading_text'], f"reading_{selected_day}")

        st.markdown("---")
        st.subheader("📝 Reading Comprehension (7 Questions)")
        
        for idx, q_data in enumerate(day_data["reading_mcq"]):
            k_rmcq = f"r_mcq_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_rmcq, "")
            user_sel = st.radio(f"Q{idx+1}: {q_data['q']}", q_data['options'], index=q_data['options'].index(curr_ans) if curr_ans in q_data['options'] else 0, key=k_rmcq)
            set_user_ans(k_rmcq, user_sel)
            
            if user_sel == q_data["a"]:
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            else:
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

        for idx, q_data in enumerate(day_data["reading_fitb"]):
            k_rfitb = f"r_fitb_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_rfitb, "")
            user_in = st.text_input(f"Q{idx+5}: {q_data['q']}", value=curr_ans, key=k_rfitb)
            set_user_ans(k_rfitb, user_in)
            
            if user_in.strip().lower() == q_data["a"].lower():
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            elif user_in.strip():
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

    # 5. Listening Briefing
    with tab5:
        st.subheader("🎧 Business Listening Briefing (~3 Min Script)")
        st.markdown(f"<div class='studio-card'><pre style='white-space: pre-wrap; font-family: Inter;'>{day_data['listening_script']}</pre></div>", unsafe_allow_html=True)
        render_tts_button(day_data['listening_script'], f"listening_{selected_day}")

        st.markdown("---")
        st.subheader("📝 Listening Comprehension (7 Questions)")
        
        for idx, q_data in enumerate(day_data["listening_mcq"]):
            k_lmcq = f"l_mcq_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_lmcq, "")
            user_sel = st.radio(f"Q{idx+1}: {q_data['q']}", q_data['options'], index=q_data['options'].index(curr_ans) if curr_ans in q_data['options'] else 0, key=k_lmcq)
            set_user_ans(k_lmcq, user_sel)
            
            if user_sel == q_data["a"]:
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            else:
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

        for idx, q_data in enumerate(day_data["listening_fitb"]):
            k_lfitb = f"l_fitb_{selected_day}_{idx}"
            curr_ans = get_user_ans(k_lfitb, "")
            user_in = st.text_input(f"Q{idx+5}: {q_data['q']}", value=curr_ans, key=k_lfitb)
            set_user_ans(k_lfitb, user_in)
            
            if user_in.strip().lower() == q_data["a"].lower():
                st.success(f"✅ Correct! Answer: {q_data['a']}")
            elif user_in.strip():
                st.error(f"❌ Incorrect. Correct Answer: {q_data['a']}")

    # 6. Detailed Writing
    with tab6:
        st.subheader("✍️ Detailed Writing Scenario")
        st.markdown(f"<div class='studio-card'>{day_data['writing_prompt']}</div>", unsafe_allow_html=True)
        
        k_write = f"write_{selected_day}"
        curr_write = get_user_ans(k_write, "")
        user_writing = st.text_area("Write your executive response here:", value=curr_write, height=220, key=k_write)
        set_user_ans(k_write, user_writing)
        
        if st.button("📊 Evaluate Essay & Provide Corrections", key=f"btn_write_{selected_day}"):
            if not user_writing.strip():
                st.warning("Please enter your writing response first!")
            else:
                with st.spinner("AI Examiner is evaluating writing..."):
                    prompt = f"""
                    Evaluate Business Writing Response strictly in English:
                    Prompt Scenario: {day_data['writing_prompt']}
                    Student Submission: "{user_writing}"

                    Format response cleanly:
                    1. C1 Band Score (/10)
                    2. Task Achievement & Tone Assessment
                    3. Grammar & Advanced Vocabulary Corrections (Point out exact mistakes)
                    4. Professional Upgraded C1 Revision
                    """
                    result = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if result:
                        st.markdown(f"<div class='studio-card'>{result}</div>", unsafe_allow_html=True)

        with st.expander("💡 View Model C1 Executive Response"):
            st.markdown(f"<div class='studio-card'>{day_data['writing_sample']}</div>", unsafe_allow_html=True)

    # 7. Speaking Presentation
    with tab7:
        st.subheader("📊 Speaking Presentation Scenario")
        st.markdown(f"<div class='studio-card'><b>Scenario Prompt:</b> {day_data['speaking_prompt']}</div>", unsafe_allow_html=True)
        record_and_evaluate_speech(day_data["speaking_prompt"], label=f"Speaking_Presentation_Day{selected_day}", context_info=day_data["topic"])

    # 8. Translation Practice
    with tab8:
        st.subheader("🌐 Translation Practice (10 Vietnamese Sentences -> English C1)")
        
        for idx, t_item in enumerate(day_data["translation_items"]):
            st.markdown(f"**Sentence {t_item['id']}:** {t_item['vi']}")
            k_trans = f"trans_{selected_day}_{idx}"
            curr_val = get_user_ans(k_trans, "")
            u_trans = st.text_input(f"Your English Translation for Sentence {t_item['id']}:", value=curr_val, key=k_trans)
            set_user_ans(k_trans, u_trans)
            
            if st.button(f"🎯 Evaluate Sentence {t_item['id']}", key=f"btn_trans_{selected_day}_{idx}"):
                if not u_trans.strip():
                    st.warning("Please enter translation first!")
                else:
                    with st.spinner(f"Evaluating Sentence {t_item['id']}..."):
                        prompt = f"""
                        Evaluate translation from Vietnamese to English strictly in English:
                        - Vietnamese Original: "{t_item['vi']}"
                        - Reference C1 Standard: "{t_item['ref']}"
                        - Student Translation: "{u_trans}"

                        Provide feedback:
                        1. Score (/10)
                        2. Vocabulary & Grammar Errors
                        3. Suggested C1 Professional Rephrasing
                        """
                        eval_res = call_groq_llm(prompt, st.session_state.groq_api_key)
                        if eval_res:
                            st.markdown(f"<div class='studio-card'>{eval_res}</div>", unsafe_allow_html=True)
            st.write("---")

if __name__ == "__main__":
    main()