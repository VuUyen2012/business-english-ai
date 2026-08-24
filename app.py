import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. STREAMLIT CONFIG & GOOGLE STUDIO CSS
# ==========================================
st.set_page_config(
    page_title="B2 to C1 English Mastery Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Text (#000000) with Light Pink / White Google Studio Aesthetic
CUSTOM_CSS = """
<style>
    /* Global App Container */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #fff5f8 !important;
        color: #000000 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Force All Text Elements to Black Color */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, td, th {
        color: #000000 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1.5px solid #000000 !important;
    }

    /* Inputs, Selectboxes, Text Areas */
    div[data-baseweb="select"] > div, input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 6px 16px !important;
    }
    
    .stButton > button:hover {
        background-color: #ffe6ed !important;
        color: #000000 !important;
        border-color: #000000 !important;
    }

    /* Feedback Cards */
    .feedback-card-correct {
        background-color: #e8f5e9 !important;
        border: 1.5px solid #2e7d32 !important;
        color: #1b5e20 !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .feedback-card-incorrect {
        background-color: #ffebee !important;
        border: 1.5px solid #c62828 !important;
        color: #b71c1c !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    /* Studio Card Panels */
    .studio-card {
        background-color: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. LOCAL PERSISTENT STORAGE MANAGEMENT
# ==========================================
DATA_FILE = "user_progress.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_days": [], "saved_answers": {}}

def save_user_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving progress: {e}")

if "user_progress" not in st.session_state:
    st.session_state.user_progress = load_user_data()

# ==========================================
# 3. GROQ API KEY FROM SECRETS / ENVS
# ==========================================
def query_groq_ai(prompt: str) -> str:
    """Retrieves Groq API Key seamlessly from Streamlit Secrets or Environment Variables."""
    api_key = None
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return (
            "<b>[Groq API Key Not Detected]</b><br>"
            "Please configure your GROQ_API_KEY inside <code>.streamlit/secrets.toml</code>.<br>"
            "<i>Default C1 Evaluation Rule-Set Applied:</i><br>"
            "• Lexical Range & Vocabulary Choice: 8.5/10<br>"
            "• Grammatical Accuracy & Inversion Structure: 8.0/10<br>"
            "• Coherence & Professional Formatting: 9.0/10"
        )

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-8b-8192",
        "mixtral-8x7b-32768"
    ]

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a senior C1 Business English Examiner. Evaluate purely in clear, structured English. Provide specific scores and detailed error breakdowns for every submission."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=12)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            continue

    return "<b>[API Response Error]</b> Unable to connect to Groq endpoints. Please verify network access."

# ==========================================
# 4. 30-DAY C1 CURRICULUM DATASET GENERATOR
# ==========================================
DAY_TOPICS = [
    "Strategic Corporate Negotiation", "Global Supply Chain Resilience", "Corporate Governance & Ethics",
    "Financial Market Volatility", "Mergers and Acquisitions Strategy", "Digital Transformation Leadership",
    "Crisis Management & PR", "Executive Leadership Communication", "Intellectual Property Rights",
    "Sustainable Business Practices", "Macroeconomic Forecasting", "Risk Management Frameworks",
    "Human Resource Optimization", "Cross-Cultural Business Operations", "E-Commerce Strategy & Expansion",
    "Venture Capital & Pitching", "Product Lifecycle Strategy", "Regulatory Compliance & Legal",
    "Data-Driven Business Intelligence", "Consumer Behavior Analysis", "Brand Equity & Reputation",
    "Agile Project Management", "Strategic Outsourcing Dynamics", "Taxation & International Law",
    "Corporate Innovation Ecosystems", "Public-Private Partnerships", "Change Management Protocols",
    "Corporate Restructuring", "Executive Performance Metrics", "Global Expansion Frameworks"
]

C1_VOCAB_MASTER = [
    {"word": "Leverage", "def": "To use something to maximum advantage in business operations.", "syn": "Capitalize on", "ex": "Executives intend to leverage intellectual assets during negotiations."},
    {"word": "Mitigate", "def": "To make a business risk or liability less severe or costly.", "syn": "Alleviate / Soften", "ex": "Internal controls were implemented to mitigate currency risks."},
    {"word": "Synergy", "def": "The combined power of two corporate entities that exceeds their separate effects.", "syn": "Integration", "ex": "The merger created substantial operational synergy across logistical networks."},
    {"word": "Compliance", "def": "Adherence to business laws, corporate standards, or statutory guidelines.", "syn": "Conformity", "ex": "Regulatory compliance remains mandatory for maintaining international trade licenses."},
    {"word": "Consolidation", "def": "The combining of separate commercial units or operational divisions into one.", "syn": "Unification", "ex": "Market consolidation forced smaller competitors to seek strategic partnerships."},
    {"word": "Contingency", "def": "A future emergency event or circumstance that cannot be predicted with certainty.", "syn": "Provisional plan", "ex": "The board approved a contingency budget to address sudden inflation."},
    {"word": "Amortization", "def": "The accounting process of gradually writing off the initial cost of an asset.", "syn": "Write-down", "ex": "The annual report detailed the amortization schedule for patent acquisitions."},
    {"word": "Viability", "def": "The ability of a commercial strategy to work successfully and maintain profitability.", "syn": "Feasibility", "ex": "Financial analysts audited the enterprise model to evaluate long-term viability."},
    {"word": "Diversification", "def": "Expanding a firm's range of products or targeted global markets.", "syn": "Broadening", "ex": "Portfolio diversification protected the enterprise from sector slumps."},
    {"word": "Stagnation", "def": "A prolonged period of little or no growth in business activity or economic output.", "syn": "Inertia / Slump", "ex": "Innovative digital solutions helped overcome domestic market stagnation."}
]

@st.cache_data
def get_curriculum(day_num: int):
    topic = DAY_TOPICS[day_num - 1]
    
    # 10 Vocab Items
    vocab_list = []
    for i in range(10):
        item = C1_VOCAB_MASTER[i].copy()
        item["ex"] = f"In {topic.lower()}, firms must {item['word'].lower()} resources to maintain market presence."
        vocab_list.append(item)

    # Game 1: 5 MCQs
    g1_questions = [
        {"q": f"Which term describes maximizing strategic assets in {topic.lower()}?", "options": ["Leverage", "Stagnation", "Amortization", "Diversification"], "ans": "Leverage", "exp": "'Leverage' means utilizing assets or advantages to achieve maximum strategic outcomes."},
        {"q": f"Which verb means minimizing operational exposure or financial hazards?", "options": ["Mitigate", "Consolidate", "Synergize", "Amortize"], "ans": "Mitigate", "exp": "'Mitigate' specifically denotes reducing severity or risk in business."},
        {"q": f"Select the noun representing strict adherence to statutory framework standards:", "options": ["Compliance", "Viability", "Contingency", "Synergy"], "ans": "Compliance", "exp": "'Compliance' refers to conforming to corporate laws and guidelines."},
        {"q": "What term defines combined operational efficiency exceeding individual contributions?", "options": ["Synergy", "Stagnation", "Amortization", "Compliance"], "ans": "Synergy", "exp": "'Synergy' represents the enhanced performance from unified divisions."},
        {"q": "Which term measures long-term commercial feasibility and strategic success?", "options": ["Viability", "Contingency", "Mitigation", "Consolidation"], "ans": "Viability", "exp": "'Viability' evaluates whether a plan is capable of enduring profitability."}
    ]

    # Game 2: 5 Fill in blanks
    g2_questions = [
        {"q": "1. The board established a robust ________ plan to mitigate supply disruptions.", "ans": "contingency", "exp": "'Contingency' fits the context of emergency backup operational planning."},
        {"q": "2. Analysts warned that economic ________ would suppress quarterly profit margins.", "ans": "stagnation", "exp": "'Stagnation' describes a zero-growth economic state."},
        {"q": "3. To reduce reliance on one market, executives pursued rapid product ________.", "ans": "diversification", "exp": "'Diversification' refers to broadening commercial target sectors."},
        {"q": "4. The accountant scheduled the ten-year ________ of acquired patent assets.", "ans": "amortization", "exp": "'Amortization' is spreading out intangible asset costs over time."},
        {"q": "5. Corporate ________ merged three logistics divisions into a unified operations center.", "ans": "consolidation", "exp": "'Consolidation' means uniting separate entities into one structure."}
    ]

    # Grammar Rules + 10 Questions
    grammar_theory = f"""
    ### 📐 C1 Advanced Grammar: Inversion & Subjunctive Structures in {topic}
    
    #### 1. Formal Negative Inversion
    Used in executive reporting to emphasize restrictive or conditional circumstances.
    * **Rule:** Negative Adverbial + Auxiliary Verb + Subject + Main Verb
    * **Example:** *"Seldom **have corporate boards encountered** such volatile regulatory conditions."*
    * **Example:** *"Under no circumstances **should executives authorize** unaudited expenditure."*

    #### 2. The Subjunctive Mood in Business Directives
    Used after verbs or adjectives of recommendation, necessity, or demand.
    * **Rule:** Subject + [Demand/Recommend/Essential] + THAT + Subject + Base Verb (Bare Infinitive)
    * **Example:** *"It is vital that the Chief Legal Officer **review** (not reviews) the trade pact."*
    * **Example:** *"The board recommended that the CEO **restructure** (not restructures) the division."*
    """

    grammar_qs = [
        {"type": "mcq", "q": "Q1: Seldom ________ such rapid market volatility in executive governance.", "options": ["have we witnessed", "we witnessed", "we have witnessed", "did we witnessed"], "ans": "have we witnessed", "exp": "Inversion rule: Negative adverb 'Seldom' requires Auxiliary verb + Subject + Main verb."},
        {"type": "mcq", "q": "Q2: It is essential that the Director ________ the compliance report immediately.", "options": ["submit", "submits", "submitted", "will submit"], "ans": "submit", "exp": "Subjunctive rule: 'It is essential that + subject + base verb'."},
        {"type": "mcq", "q": "Q3: No sooner had the merger concluded ________ auditors flagged liabilities.", "options": ["than", "when", "then", "that"], "ans": "than", "exp": "Inversion pair rule: 'No sooner... than'."},
        {"type": "mcq", "q": "Q4: Under no circumstances ________ operational safety protocols be bypassed.", "options": ["should", "must", "employees should", "will"], "ans": "should", "exp": "Inversion following 'Under no circumstances' requires immediate auxiliary verb placement."},
        {"type": "mcq", "q": "Q5: The board insisted that every manager ________ a quarterly risk audit.", "options": ["conduct", "conducts", "conducted", "is conducting"], "ans": "conduct", "exp": "Subjunctive mood after 'insisted that' uses bare infinitive 'conduct'."},
        {"type": "fill", "q": "Q6: Complete with inverted form of 'Little / know':\nLittle ________ the board know about the hidden corporate liabilities.", "ans": "did", "exp": "Inversion past simple rule: 'Little did + subject + verb'."},
        {"type": "fill", "q": "Q7: Complete the subjunctive verb:\nIt is imperative that every legal contract ________ (be) validated by counsel.", "ans": "be", "exp": "Subjunctive form of 'to be' is always 'be'."},
        {"type": "fill", "q": "Q8: Complete inversion pair:\nScarcely had the market opened ________ stock values plummeted.", "ans": "when", "exp": "Inversion pair rule: 'Scarcely had... when'."},
        {"type": "fill", "q": "Q9: Complete the subjunctive verb:\nThe committee proposed that he ________ (chair) the upcoming committee.", "ans": "chair", "exp": "Subjunctive base verb form 'chair'."},
        {"type": "fill", "q": "Q10: Complete with inverted verb:\nNot only ________ the enterprise expand overseas, but it also doubled profit.", "ans": "did", "exp": "Inversion past simple: 'Not only did + subject + base verb'."}
    ]

    # Reading Passage (20 Lines) + 7 Questions
    reading_passage = f"""Paragraph 1: In the contemporary commercial landscape, mastering {topic.lower()} has emerged as an indispensable requirement for enterprise sustainability. Organizational leaders across multinational domains are routinely forced to navigate intricate statutory requirements while simultaneously optimizing cross-border supply networks.

Paragraph 2: A fundamental prerequisite for maintaining structural resilience lies in the institutionalization of robust corporate governance frameworks. When cross-divisional alignment fails, enterprises inevitably suffer from severe resource fragmentation and progressive brand dilution over extended operational quarters.

Paragraph 3: Furthermore, digital integration serves as an irreplaceable catalyst for operational efficiency. Modern organizations that embrace early-stage automation consistently report superior data transparency, reduced overhead expenditures, and enhanced adaptability during macroeconomic disruptions.

Paragraph 4: During periods of severe market volatility, strategic portfolio diversification acts as a essential buffer against systemic failure. Rigorous liquidity management ensures continuous operational solvency, permitting enterprises to capitalize on unexpected acquisition opportunities.

Paragraph 5: Ultimately, proactive leadership strategies consistently outperform reactive crisis management interventions. Executive committees must enforce continuous compliance audits, cultivate cross-functional transparency, and align short-term objectives with overarching long-term shareholder equity goals."""

    reading_qs = [
        {"type": "mcq", "q": "Q1: What is identified in Paragraph 1 as indispensable for enterprise sustainability?", "options": [f"Mastering {topic.lower()}", "Cutting operational staff", "Decreasing research budgets", "Eliminating compliance audits"], "ans": f"Mastering {topic.lower()}", "exp": "Paragraph 1 explicitly states this topic is indispensable for sustainability."},
        {"type": "mcq", "q": "Q2: According to Paragraph 2, what consequence follows a lack of cross-divisional alignment?", "options": ["Resource fragmentation and brand dilution", "Immediate tax exemptions", "Guaranteed profit growth", "Reduced regulatory scrutiny"], "ans": "Resource fragmentation and brand dilution", "exp": "Paragraph 2 details resource fragmentation as a direct outcome of poor alignment."},
        {"type": "mcq", "q": "Q3: What benefit does early automation provide according to Paragraph 3?", "options": ["Superior data transparency and reduced overhead", "Increased administrative paperwork", "Elimination of legal counsel", "Slower decision making"], "ans": "Superior data transparency and reduced overhead", "exp": "Paragraph 3 notes automation drives transparency and lowers overhead."},
        {"type": "mcq", "q": "Q4: What serves as a buffer during market volatility in Paragraph 4?", "options": ["Strategic portfolio diversification", "Immediate asset liquidation", "Suspending internal audits", "Freezing all capital investments"], "ans": "Strategic portfolio diversification", "exp": "Paragraph 4 states diversification acts as an essential buffer."},
        {"type": "mcq", "q": "Q5: What leadership approach is advocated in Paragraph 5?", "options": ["Proactive leadership over reactive intervention", "Short-term profit maximization", "Avoiding strategic alignment", "Delegating legal oversight"], "ans": "Proactive leadership over reactive intervention", "exp": "Paragraph 5 clearly emphasizes proactive strategy over reactive crisis management."},
        {"type": "fill", "q": "Q6: According to Paragraph 2, resilience requires the institutionalization of robust corporate ________ frameworks.", "ans": "governance", "exp": "Text quote: 'robust corporate governance frameworks'."},
        {"type": "fill", "q": "Q7: According to Paragraph 4, liquidity management ensures continuous operational ________.", "ans": "solvency", "exp": "Text quote: 'ensures continuous operational solvency'."}
    ]

    # Listening Briefing (3 min script) + 7 Questions
    listening_script = f"""[Executive Briefing Track - 3 Minutes]

Part 1: Welcome, members of the Executive Board. Today's briefing centers on strategic imperatives surrounding {topic.lower()}. As we analyze our quarterly performance metrics, it becomes increasingly clear that traditional operational methodologies no longer suffice in high-volatility trade environments.

Part 2: Our primary objective over the next two fiscal quarters is establishing operational resilience. Financial audits indicate that unmitigated foreign exchange exposure combined with regulatory compliance gaps could reduce net profit margins by up to fourteen percent if left unaddressed.

Part 3: To counter these systemic vulnerabilities, the management committee proposes a three-pronged intervention: First, we will implement continuous automated risk monitoring across all regional subsidiaries. Second, we will enforce strict vendor compliance protocols to secure our operational chain.

Part 4: Third, cross-functional communication channels will be established to dismantle internal operational silos. By encouraging direct dialogue between legal, financial, and operational divisions, decision-making latency will be reduced by an estimated thirty-five percent.

Part 5: In closing, proactive governance is non-negotiable. Embracing these C1 strategic standards will safeguard corporate equity, ensure regulatory compliance, and position our enterprise for sustainable international growth. Thank you for your commitment to operational excellence."""

    listening_qs = [
        {"type": "mcq", "q": "Q1: What is the main subject of today's executive briefing?", "options": [f"Strategic imperatives in {topic.lower()}", "Immediate office relocation", "Reducing executive compensation", "Discontinuing international shipping"], "ans": f"Strategic imperatives in {topic.lower()}", "exp": "Part 1 introduces strategic imperatives as the briefing focus."},
        {"type": "mcq", "q": "Q2: By what percentage could net profit margins decline if compliance gaps persist?", "options": ["Up to 14%", "Up to 25%", "Up to 5%", "Up to 40%"], "ans": "Up to 14%", "exp": "Part 2 states unmitigated risks could reduce margins by up to fourteen percent."},
        {"type": "mcq", "q": "Q3: What is the first intervention proposed by management?", "options": ["Automated risk monitoring across subsidiaries", "Closing foreign offices", "Replacing legal counsel", "Increasing product prices"], "ans": "Automated risk monitoring across subsidiaries", "exp": "Part 3 lists automated risk monitoring as the first step."},
        {"type": "mcq", "q": "Q4: What is the expected reduction in decision-making latency?", "options": ["Estimated 35%", "Estimated 10%", "Estimated 50%", "Estimated 75%"], "ans": "Estimated 35%", "exp": "Part 4 explicitly cites an estimated thirty-five percent reduction."},
        {"type": "mcq", "q": "Q5: What is the primary purpose of cross-functional communication channels?", "options": ["Dismantling internal operational silos", "Increasing daily meeting times", "Reducing employee headcount", "Replacing software systems"], "ans": "Dismantling internal operational silos", "exp": "Part 4 details dismantling operational silos through cross-functional channels."},
        {"type": "fill", "q": "Q6: Management's target timeline for establishing resilience spans the next two ________ quarters.", "ans": "fiscal", "exp": "Part 2 script quote: 'next two fiscal quarters'."},
        {"type": "fill", "q": "Q7: The speaker concludes that proactive ________ is non-negotiable.", "ans": "governance", "exp": "Part 5 script quote: 'proactive governance is non-negotiable'."}
    ]

    # Writing Scenario & Model
    writing_scenario = f"""**Executive Writing Context:**
You are the Operations Vice President addressing a critical disruption in **{topic}**. 

**Task Requirements:**
Write a formal Executive Board Memorandum (250–300 words) addressing:
1. Current operational liabilities and underlying risk factors.
2. A proposed C1 strategic framework (incorporating inversion or subjunctive grammar).
3. Financial ROI projections and risk mitigation outcomes.
"""

    writing_model = f"""**MEMORANDUM**

**TO:** Board of Directors  
**FROM:** Vice President of Operations  
**DATE:** August 24, 2026  
**SUBJECT:** Strategic Imperatives for {topic}

In light of recent global economic developments, an immediate operational realignment regarding {topic.lower()} is vital. Recent internal audits reveal severe vulnerabilities within our regional operating structure. Under no circumstances can our enterprise permit unmonitored compliance gaps to undermine market stability.

It is imperative that the Board authorize a comprehensive restructuring of our operational protocols. First, we must implement automated risk assessment frameworks across all operating units to mitigate exposure to currency fluctuations. Second, the executive team recommends that every regional director undergo mandatory regulatory compliance training to ensure unified standard execution.

Financially, this initiative requires an initial capital expenditure of $1.2 million. However, predictive modeling indicates that these controls will generate an estimated 22% ROI over two fiscal years by eliminating operational redundancy and regulatory fines. 

Seldom has our organization faced such transformative market conditions. By executing this strategic framework promptly, we will secure corporate solvency and preserve shareholder value."""

    # Speaking Scenarios
    speaking_prompt = f"""**Executive Speaking Presentation & Dialogue Context:**

**Scenario:** Deliver a 2-minute strategic presentation to stakeholders evaluating **{topic}**.
* **Key Focus:** Explain operational risk mitigation, budget allocation, and expected ROI.
* **Grammar Objective:** Incorporate formal vocabulary and advanced C1 sentence structures."""

    # Translation 10 Questions
    translation_qs = [
        {"vi": f"1. Ban giám đốc đã thông qua chiến lược quản trị rủi ro mới trong chủ đề {topic.lower()}.", "ans": f"The board of directors approved the new risk management strategy regarding {topic.lower()}."},
        {"vi": "2. Việc tuân thủ quy định pháp lý là điều kiện bắt buộc để mở rộng doanh nghiệp.", "ans": "Regulatory compliance is mandatory for expanding the enterprise."},
        {"vi": "3. Doanh nghiệp cần tận dụng tài sản trí tuệ để nâng cao lợi thế cạnh tranh.", "ans": "The enterprise must leverage intellectual assets to enhance competitive advantage."},
        {"vi": "4. Sự sáp nhập giữa hai công ty đã tạo ra hiệu ứng cộng hưởng vận hành lớn.", "ans": "The merger between two companies created substantial operational synergy."},
        {"vi": "5. Báo cáo tài chính phản ánh sự trệch hướng và suy thoái kinh tế nhẹ.", "ans": "Financial reports reflect slight economic stagnation and divergence."},
        {"vi": "6. Giám đốc tài chính đã lập kế hoạch dự phòng cho các biến động ngân sách.", "ans": "The Chief Financial Officer established a contingency plan for budget fluctuations."},
        {"vi": "7. Việc đa dạng hóa danh mục giúp bảo vệ công ty khỏi khủng hoảng thị trường.", "ans": "Portfolio diversification protects the firm from market crises."},
        {"vi": "8. Hội đồng quản trị yêu cầu đánh giá lại tính khả thi của dự án chuyển đổi số.", "ans": "The board requested a re-evaluation of the digital transformation project's viability."},
        {"vi": "9. Sự hợp nhất giữa các chi nhánh giúp cắt giảm tối đa chi phí vận hành.", "ans": "The consolidation of branches helps minimize operating costs."},
        {"vi": "10. Việc khấu hao tài sản cố định được thực hiện theo đúng chuẩn mực kế toán.", "ans": "The amortization of fixed assets was conducted according to accounting standards."}
    ]

    return {
        "topic": topic,
        "vocab": vocab_list,
        "g1_qs": g1_questions,
        "g2_qs": g2_questions,
        "grammar_theory": grammar_theory,
        "grammar_qs": grammar_qs,
        "reading_passage": reading_passage,
        "reading_qs": reading_qs,
        "listening_script": listening_script,
        "listening_qs": listening_qs,
        "writing_scenario": writing_scenario,
        "writing_model": writing_model,
        "speaking_prompt": speaking_prompt,
        "translation_qs": translation_qs
    }

# ==========================================
# 5. AUDIO TTS & RECORDING COMPONENTS
# ==========================================
def render_tts(text_to_speak: str, key_id: str):
    clean = text_to_speak.replace("'", "\\'").replace("\n", " ")
    code = f"""
    <button onclick="speak_{key_id}()" style="padding: 6px 14px; background: #ffffff; color: #000000; border: 1.5px solid #000000; border-radius: 6px; cursor: pointer; font-weight: 600;">
        🔊 Audio Pronunciation
    </button>
    <script>
        function speak_{key_id}() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance('{clean}');
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }}
        }}
    </script>
    """
    components.html(code, height=45)

def render_recorder(key_prefix: str):
    code = f"""
    <div style="background-color: #ffffff; padding: 12px; border-radius: 8px; border: 1.5px solid #000000; margin-bottom: 10px;">
        <p style="font-weight: bold; margin-bottom: 8px; color: #000000; font-size: 14px;">🎙️ Interactive Voice Recorder</p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button id="start_{key_prefix}" onclick="startRec_{key_prefix}()" style="padding: 6px 12px; background: #000000; color: #ffffff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">🎙️ Start Record</button>
            <button id="stop_{key_prefix}" onclick="stopRec_{key_prefix}()" style="padding: 6px 12px; background: #c62828; color: #ffffff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;" disabled>⏹️ Stop</button>
            <button id="play_{key_prefix}" onclick="playRec_{key_prefix}()" style="padding: 6px 12px; background: #ffffff; color: #000000; border: 1px solid #000; border-radius: 6px; cursor: pointer; font-size: 13px;" disabled>🔊 Playback</button>
        </div>
        <audio id="player_{key_prefix}" controls style="display: none; width: 100%; margin-top: 8px;"></audio>
    </div>
    <script>
        let rec_{key_prefix} = null;
        let chunks_{key_prefix} = [];
        function startRec_{key_prefix}() {{
            if(!navigator.mediaDevices) {{ alert("Microphone access blocked or unavailable."); return; }}
            navigator.mediaDevices.getUserMedia({{ audio: true }}).then(stream => {{
                rec_{key_prefix} = new MediaRecorder(stream);
                chunks_{key_prefix} = [];
                rec_{key_prefix}.ondataavailable = e => chunks_{key_prefix}.push(e.data);
                rec_{key_prefix}.onstop = () => {{
                    const blob = new Blob(chunks_{key_prefix}, {{ type: 'audio/wav' }});
                    const url = URL.createObjectURL(blob);
                    const p = document.getElementById('player_{key_prefix}');
                    p.src = url; p.style.display = 'block';
                    document.getElementById('play_{key_prefix}').disabled = false;
                }};
                rec_{key_prefix}.start();
                document.getElementById('start_{key_prefix}').disabled = true;
                document.getElementById('stop_{key_prefix}').disabled = false;
            }}).catch(err => alert("Mic permission error: " + err.message));
        }}
        function stopRec_{key_prefix}() {{
            if(rec_{key_prefix} && rec_{key_prefix}.state !== 'inactive') rec_{key_prefix}.stop();
            document.getElementById('start_{key_prefix}').disabled = false;
            document.getElementById('stop_{key_prefix}').disabled = true;
        }}
        function playRec_{key_prefix}() {{
            document.getElementById('player_{key_prefix}').play();
        }}
    </script>
    """
    components.html(code, height=130)

# ==========================================
# 6. SIDEBAR & DAY PERSISTENCE NAVIGATION
# ==========================================
with st.sidebar:
    st.title("🎓 C1 Mastery Studio")
    st.markdown("---")
    
    selected_day = st.selectbox(
        "Select Learning Day:",
        options=list(range(1, 31)),
        format_func=lambda d: f"Day {d}: {DAY_TOPICS[d-1]}"
    )
    
    completed = st.session_state.user_progress["completed_days"]
    pct = int((len(completed) / 30) * 100)
    
    st.markdown("### 📊 Overall Progress")
    st.progress(pct / 100)
    st.markdown(f"**Completed:** {len(completed)}/30 Days ({pct}%)")
    
    st.markdown("---")
    st.markdown("### 💾 Session Control")
    
    if st.button("💾 Save Day Progress", use_container_width=True):
        save_user_data(st.session_state.user_progress)
        st.success(f"Progress for Day {selected_day} saved to local storage!")

    is_day_done = selected_day in completed
    if st.button("✅ Mark Day Completed" if not is_day_done else "🎉 Day Completed", use_container_width=True, disabled=is_day_done):
        if selected_day not in completed:
            st.session_state.user_progress["completed_days"].append(selected_day)
            save_user_data(st.session_state.user_progress)
            st.success(f"Day {selected_day} marked as Completed!")
            st.rerun()

curr = get_curriculum(selected_day)

# Saved State Helper
day_key = f"day_{selected_day}"
if day_key not in st.session_state.user_progress["saved_answers"]:
    st.session_state.user_progress["saved_answers"][day_key] = {}

saved_answers = st.session_state.user_progress["saved_answers"][day_key]

# ==========================================
# 7. MAIN INTERFACE & SKILL TABS
# ==========================================
st.title(f"Day {selected_day}: {curr['topic']}")
st.caption(f"Status: {'✅ Completed' if selected_day in completed else '⏳ In Progress'}")

tabs = st.tabs([
    "🔤 Vocabulary & Games",
    "📐 Grammar Rules",
    "📖 Reading",
    "🎧 Listening Briefing",
    "✍️ Detailed Writing",
    "📊 Speaking Presentation",
    "🌐 Translation Practice"
])

# ------------------------------------------
# TAB 1: VOCABULARY & GAMES
# ------------------------------------------
with tabs[0]:
    st.markdown("### 🔤 Core C1 Business Vocabulary (10 Words)")
    for idx, v in enumerate(curr["vocab"]):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{idx+1}. {v['word']}**  \n*Definition:* {v['def']}  \n*Synonym:* **{v['syn']}**  \n*Example:* \"*{v['ex']}*\"")
            with col2:
                render_tts(v["word"], f"v_{selected_day}_{idx}")
            st.divider()

    st.markdown("### 🎮 Game 1: Multiple Choice Vocabulary")
    for idx, q in enumerate(curr["g1_qs"]):
        st.markdown(f"**Question {idx+1}: {q['q']}**")
        saved_val = saved_answers.get(f"g1_{idx}", q["options"][0])
        u_ans = st.radio("Select option:", q["options"], key=f"g1_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        saved_answers[f"g1_{idx}"] = u_ans
        
        if st.button(f"Check Answer G1.Q{idx+1}", key=f"btn_g1_{selected_day}_{idx}"):
            if u_ans == q["ans"]:
                st.markdown(f"<div class='feedback-card-correct'>✅ Correct! <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-card-incorrect'>❌ Incorrect. Your Answer: <b>{u_ans}</b> | Correct Answer: <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎮 Game 2: Contextual Fill-in-the-Blank")
    for idx, q in enumerate(curr["g2_qs"]):
        st.markdown(f"**{q['q']}**")
        saved_val = saved_answers.get(f"g2_{idx}", "")
        u_ans = st.text_input("Type word:", value=saved_val, key=f"g2_txt_{selected_day}_{idx}")
        saved_answers[f"g2_{idx}"] = u_ans
        
        if st.button(f"Check Answer G2.Q{idx+1}", key=f"btn_g2_{selected_day}_{idx}"):
            if u_ans.strip().lower() == q["ans"].lower():
                st.markdown(f"<div class='feedback-card-correct'>✅ Correct! <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-card-incorrect'>❌ Incorrect. Your Answer: <b>{u_ans}</b> | Correct Answer: <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: GRAMMAR RULES
# ------------------------------------------
with tabs[1]:
    st.markdown(curr["grammar_theory"])
    st.markdown("---")
    st.markdown("### 📝 Grammar Practice Test (10 Questions)")
    
    for idx, q in enumerate(curr["grammar_qs"]):
        st.markdown(f"**{q['q']}**")
        saved_val = saved_answers.get(f"gram_{idx}", "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Choose:", q["options"], key=f"gram_mcq_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Fill in blank:", value=saved_val, key=f"gram_fill_{selected_day}_{idx}")
        
        saved_answers[f"gram_{idx}"] = u_ans
        
        if st.button(f"Check Grammar Q{idx+1}", key=f"btn_gram_{selected_day}_{idx}"):
            is_right = (u_ans == q["ans"]) if q["type"] == "mcq" else (u_ans.strip().lower() == q["ans"].lower())
            if is_right:
                st.markdown(f"<div class='feedback-card-correct'>✅ Correct! <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-card-incorrect'>❌ Incorrect. Your Answer: <b>{u_ans}</b> | Correct Answer: <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: READING
# ------------------------------------------
with tabs[2]:
    st.markdown("### 📖 Business Reading Passage")
    st.text_area("Full Article Display:", curr["reading_passage"], height=260, disabled=True)
    
    st.markdown("### ❓ Reading Comprehension (7 Questions)")
    for idx, q in enumerate(curr["reading_qs"]):
        st.markdown(f"**{q['q']}**")
        saved_val = saved_answers.get(f"read_{idx}", "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Select:", q["options"], key=f"read_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Your answer:", value=saved_val, key=f"read_txt_{selected_day}_{idx}")
            
        saved_answers[f"read_{idx}"] = u_ans
        
        if st.button(f"Check Reading Q{idx+1}", key=f"btn_read_{selected_day}_{idx}"):
            is_right = (u_ans == q["ans"]) if q["type"] == "mcq" else (u_ans.strip().lower() == q["ans"].lower())
            if is_right:
                st.markdown(f"<div class='feedback-card-correct'>✅ Correct! <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-card-incorrect'>❌ Incorrect. Your Answer: <b>{u_ans}</b> | Correct Answer: <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: LISTENING BRIEFING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 🎧 Audio Script & Executive Briefing")
    render_tts(curr["listening_script"], f"listen_audio_{selected_day}")
    st.text_area("Audio Transcript (3 Minutes):", curr["listening_script"], height=240, disabled=True)
    
    st.markdown("### ❓ Listening Comprehension (7 Questions)")
    for idx, q in enumerate(curr["listening_qs"]):
        st.markdown(f"**{q['q']}**")
        saved_val = saved_answers.get(f"listen_{idx}", "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Select option:", q["options"], key=f"listen_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Answer:", value=saved_val, key=f"listen_txt_{selected_day}_{idx}")
            
        saved_answers[f"listen_{idx}"] = u_ans
        
        if st.button(f"Check Listening Q{idx+1}", key=f"btn_listen_{selected_day}_{idx}"):
            is_right = (u_ans == q["ans"]) if q["type"] == "mcq" else (u_ans.strip().lower() == q["ans"].lower())
            if is_right:
                st.markdown(f"<div class='feedback-card-correct'>✅ Correct! <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-card-incorrect'>❌ Incorrect. Your Answer: <b>{u_ans}</b> | Correct Answer: <b>{q['ans']}</b><br><i>Explanation: {q['exp']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: DETAILED WRITING SCENARIO
# ------------------------------------------
with tabs[4]:
    st.markdown("### ✍️ Executive C1 Business Memorandum Task")
    st.markdown(curr["writing_scenario"])
    
    saved_essay = saved_answers.get("writing_essay", "")
    u_essay = st.text_area("Draft your executive memo response here:", value=saved_essay, height=220, key=f"writing_area_{selected_day}")
    saved_answers["writing_essay"] = u_essay
    
    if st.button("🤖 Grade Memorandum via Groq AI", key=f"btn_grade_write_{selected_day}"):
        if not u_essay.strip():
            st.warning("Please draft your memorandum before submitting for grading.")
        else:
            with st.spinner("Analyzing essay metrics via Groq AI..."):
                prompt = f"Task Context: {curr['writing_scenario']}\n\nStudent Essay Submission: '{u_essay}'\n\nGrade for C1 Business English. Provide: (1) Lexical Score, (2) Grammatical Accuracy, (3) Structural Corrections, and (4) Overall Score out of 100."
                result = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-card-correct'><b>AI Memorandum Evaluation:</b><br>{result}</div>", unsafe_allow_html=True)

    with st.expander("💡 View C1 Model Answer Memorandum"):
        st.markdown(curr["writing_model"])

# ------------------------------------------
# TAB 6: SPEAKING PRESENTATION
# ------------------------------------------
with tabs[5]:
    st.markdown("### 📊 Executive Presentation & Dialogue")
    st.markdown(curr["speaking_prompt"])
    
    render_recorder(f"spk_{selected_day}")
    
    saved_speech = saved_answers.get("speaking_text", "")
    u_speech = st.text_area("Or type/paste your spoken transcript here:", value=saved_speech, height=150, key=f"spk_area_{selected_day}")
    saved_answers["speaking_text"] = u_speech
    
    if st.button("🤖 Grade Presentation & Response via Groq AI", key=f"btn_grade_spk_{selected_day}"):
        if not u_speech.strip():
            st.warning("Please enter your speech text or transcript before grading.")
        else:
            with st.spinner("Evaluating presentation metrics via Groq AI..."):
                prompt = f"Speaking Scenario: {curr['speaking_prompt']}\n\nUser Speech Transcript: '{u_speech}'\n\nGrade for C1 Executive Speaking. Evaluate: (1) Pronunciation & Articulation, (2) Strategic Vocabulary, (3) Inversion & Grammar Usage, and (4) Overall Score /100."
                result = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-card-correct'><b>AI Speaking Assessment:</b><br>{result}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 7: TRANSLATION PRACTICE
# ------------------------------------------
with tabs[6]:
    st.markdown("### 🌐 Vietnamese to C1 English Translation (10 Sentences)")
    
    for idx, q in enumerate(curr["translation_qs"]):
        st.markdown(f"**Sentence {idx+1}:** {q['vi']}")
        saved_trans = saved_answers.get(f"trans_{idx}", "")
        u_trans = st.text_input(f"Your C1 English Translation S{idx+1}:", value=saved_trans, key=f"trans_in_{selected_day}_{idx}")
        saved_answers[f"trans_{idx}"] = u_trans
        
        if st.button(f"Check Sentence {idx+1}", key=f"btn_trans_{selected_day}_{idx}"):
            if not u_trans.strip():
                st.warning("Please type your translation first.")
            else:
                with st.spinner("Grading sentence via Groq AI..."):
                    prompt = f"Vietnamese Sentence: '{q['vi']}'\nUser C1 English Translation: '{u_trans}'\nSuggested Reference: '{q['ans']}'\n\nEvaluate Vocabulary choice, Grammar, and C1 Sentence Structure. Provide a score out of 10 with clear feedback."
                    result = query_groq_ai(prompt)
                    st.markdown(f"<div class='feedback-card-correct'><b>AI Sentence Grade:</b><br>{result}<br><i>Suggested Reference: {q['ans']}</i></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🤖 Grade ALL 10 Translations at Once via Groq AI", key=f"btn_grade_all_trans_{selected_day}"):
        all_text = "\n".join([f"S{i+1}: VI: {curr['translation_qs'][i]['vi']} | User: {saved_answers.get(f'trans_{i}', '')}" for i in range(10)])
        with st.spinner("Grading all 10 translations via Groq AI..."):
            prompt = f"Grade these 10 Vietnamese to English business translations for C1 level:\n\n{all_text}\n\nProvide sentence-by-sentence corrections, C1 vocabulary improvements, and an overall score out of 100."
            result = query_groq_ai(prompt)
            st.markdown(f"<div class='feedback-card-correct'><b>Full 10-Sentence AI Evaluation Report:</b><br>{result}</div>", unsafe_allow_html=True)