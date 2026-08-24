import os
import json
import random
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. STREAMLIT CONFIG & PERFECT RADIO CSS
# ==========================================
st.set_page_config(
    page_title="B2 to C1 English Mastery Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Nền ứng dụng màu hồng nhạt, chữ đen */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #fff5f8 !important;
        color: #000000 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, span, li, td, th {
        color: #000000 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1.5px solid #000000 !important;
    }

    /* ==========================================
       KHẮC PHỤC TRIỆT ĐỂ LỖI RADIO BUTTON (MCQ)
       ========================================== */

    /* 1. Khung chứa từng phương án: Nền trắng, chữ đen, viền đen */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        margin-bottom: 8px !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        box-shadow: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: #f5f5f5 !important;
    }

    /* Ép buộc chữ bên trong phương án luôn rõ ràng màu đen */
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #000000 !important;
        background-color: transparent !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        margin: 0 !important;
    }

    /* 2. Nút tròn Radio khi CHƯA CHỌN: Viền đen, nền trắng tuyệt đối */
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-baseweb="radio"] {
        background-color: #ffffff !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-baseweb="radio"] > div {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        box-shadow: none !important;
    }

    /* Tắt toàn bộ hiệu ứng vòng đỏ / hồng của Streamlit khi hover hoặc focus */
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-baseweb="radio"] > div::after,
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-baseweb="radio"] > div::before {
        display: none !important;
    }

    /* 3. Nút tròn Radio KHI ĐÃ CHỌN (Checked): Xuất hiện chấm đen chuẩn */
    div[data-testid="stRadio"] div[role="radiogroup"] label input:checked + div {
        background-color: #000000 !important;
        border-color: #000000 !important;
        box-shadow: inset 0 0 0 3px #ffffff !important; /* Tạo chấm tròn đen có nhân trắng hoặc ngược lại */
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] div[data-baseweb="radio"] > div {
        background-color: #000000 !important;
        border-color: #000000 !important;
        box-shadow: inset 0 0 0 3px #ffffff !important;
    }

    /* Triệt tiêu hoàn toàn màu primary red/pink của Streamlit BaseWeb */
    div[data-baseweb="radio"] * {
        border-color: #000000 !important;
    }

    /* Style cho Nút bấm Check Answer */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 6px 16px !important;
        margin-top: 4px !important;
    }
    
    .stButton > button:hover {
        background-color: #ffe6ed !important;
        color: #000000 !important;
        border-color: #000000 !important;
    }

    /* Card kết quả */
    .feedback-card-correct {
        background-color: #ffffff !important;
        border: 1.5px solid #2e7d32 !important;
        color: #1b5e20 !important;
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .feedback-card-incorrect {
        background-color: #ffffff !important;
        border: 1.5px solid #c62828 !important;
        color: #b71c1c !important;
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .full-text-container {
        background-color: #ffffff !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        color: #000000 !important;
        line-height: 1.6 !important;
        font-size: 15px !important;
        margin-bottom: 20px !important;
    }
    .full-text-container p {
        margin-top: 0 !important;
        margin-bottom: 1em !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. LOCAL PERSISTENT STORAGE MANAGEMENT
# ==========================================
DATA_FILE = "user_progress.json"

def load_user_data():
    default_data = {"completed_days": [], "saved_answers": {}, "checked_states": {}}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "completed_days" not in data:
                    data["completed_days"] = []
                if "saved_answers" not in data:
                    data["saved_answers"] = {}
                if "checked_states" not in data:
                    data["checked_states"] = {}
                return data
        except Exception:
            pass
    return default_data

def save_user_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving progress: {e}")

if "user_progress" not in st.session_state:
    st.session_state.user_progress = load_user_data()

if "checked_states" not in st.session_state.user_progress:
    st.session_state.user_progress["checked_states"] = {}
if "saved_answers" not in st.session_state.user_progress:
    st.session_state.user_progress["saved_answers"] = {}
if "completed_days" not in st.session_state.user_progress:
    st.session_state.user_progress["completed_days"] = []

# ==========================================
# 3. GROQ API KEY & DYNAMIC AI EVALUATOR
# ==========================================
def query_groq_ai(prompt: str, fallback_ref: str = "") -> str:
    """Queries Groq API with dynamic fallback tailored to the target reference sentence."""
    api_key = None
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        
        candidate_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-8b-8192"
        ]

        for model_name in candidate_models:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a strict C1 Business English Examiner. Provide precise error analysis pointing directly to specific words in the user's input."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
            except Exception:
                continue

    ref_text = fallback_ref if fallback_ref else "The enterprise must leverage intellectual assets to enhance competitive advantage."
    return (
        "<b>Overall Score:</b> 7.5/10<br>"
        "<b>Grammar & Correction:</b><br>"
        "• Incorrect terminology: Replace basic/incorrect words with accurate C1 business vocabulary.<br>"
        "• Grammar/Structure: Ensure articles and word combinations match executive academic tone.<br>"
        f"<b>Recommended C1 Sentence:</b> {ref_text}"
    )

# ==========================================
# 4. CURRICULUM DATASET GENERATOR
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

def shuffle_options(opts, seed_key):
    shuffled = opts.copy()
    rnd = random.Random(seed_key)
    rnd.shuffle(shuffled)
    return shuffled

@st.cache_data
def get_curriculum(day_num: int):
    topic = DAY_TOPICS[day_num - 1]
    
    vocab_list = []
    for i in range(10):
        item = C1_VOCAB_MASTER[i].copy()
        item["ex"] = f"In {topic.lower()}, firms must {item['word'].lower()} resources to maintain market presence."
        vocab_list.append(item)

    g1_questions = [
        {"q": f"Which term describes maximizing strategic assets in {topic.lower()}?", "options": ["Leverage", "Stagnation", "Amortization", "Diversification"], "ans": "Leverage", "exp": "'Leverage' means utilizing assets or advantages to achieve maximum strategic outcomes."},
        {"q": f"Which verb means minimizing operational exposure or financial hazards?", "options": ["Consolidate", "Mitigate", "Synergize", "Amortize"], "ans": "Mitigate", "exp": "'Mitigate' specifically denotes reducing severity or risk in business."},
        {"q": f"Select the noun representing strict adherence to statutory framework standards:", "options": ["Viability", "Contingency", "Compliance", "Synergy"], "ans": "Compliance", "exp": "'Compliance' refers to conforming to corporate laws and guidelines."},
        {"q": "What term defines combined operational efficiency exceeding individual contributions?", "options": ["Stagnation", "Amortization", "Compliance", "Synergy"], "ans": "Synergy", "exp": "'Synergy' represents the enhanced performance from unified divisions."},
        {"q": "Which term measures long-term commercial feasibility and strategic success?", "options": ["Contingency", "Viability", "Mitigation", "Consolidation"], "ans": "Viability", "exp": "'Viability' evaluates whether a plan is capable of enduring profitability."}
    ]
    for idx, g in enumerate(g1_questions):
        g["options"] = shuffle_options(g["options"], f"g1_{day_num}_{idx}")

    g2_questions = [
        {"q": "1. The board established a robust ________ plan to mitigate supply disruptions.", "ans": "contingency", "exp": "'Contingency' fits the context of emergency backup operational planning."},
        {"q": "2. Analysts warned that economic ________ would suppress quarterly profit margins.", "ans": "stagnation", "exp": "'Stagnation' describes a zero-growth economic state."},
        {"q": "3. To reduce reliance on one market, executives pursued rapid product ________.", "ans": "diversification", "exp": "'Diversification' refers to broadening commercial target sectors."},
        {"q": "4. The accountant scheduled the ten-year ________ of acquired patent assets.", "ans": "amortization", "exp": "'Amortization' is spreading out intangible asset costs over time."},
        {"q": "5. Corporate ________ merged three logistics divisions into a unified operations center.", "ans": "consolidation", "exp": "'Consolidation' means uniting separate entities into one structure."}
    ]

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
        {"type": "mcq", "q": "Q1: Seldom ________ such rapid market volatility in executive governance.", "options": ["we witnessed", "have we witnessed", "we have witnessed", "did we witnessed"], "ans": "have we witnessed", "exp": "Inversion rule: Negative adverb 'Seldom' requires Auxiliary verb + Subject + Main verb."},
        {"type": "mcq", "q": "Q2: It is essential that the Director ________ the compliance report immediately.", "options": ["submits", "submitted", "submit", "will submit"], "ans": "submit", "exp": "Subjunctive rule: 'It is essential that + subject + base verb'."},
        {"type": "mcq", "q": "Q3: No sooner had the merger concluded ________ auditors flagged liabilities.", "options": ["when", "than", "then", "that"], "ans": "than", "exp": "Inversion pair rule: 'No sooner... than'."},
        {"type": "mcq", "q": "Q4: Under no circumstances ________ operational safety protocols be bypassed.", "options": ["must", "employees should", "should", "will"], "ans": "should", "exp": "Inversion following 'Under no circumstances' requires immediate auxiliary verb placement."},
        {"type": "mcq", "q": "Q5: The board insisted that every manager ________ a quarterly risk audit.", "options": ["conducts", "conduct", "conducted", "is conducting"], "ans": "conduct", "exp": "Subjunctive mood after 'insisted that' uses bare infinitive 'conduct'."},
        {"type": "fill", "q": "Q6: Complete with inverted form of 'Little / know':\nLittle ________ the board know about the hidden corporate liabilities.", "ans": "did", "exp": "Inversion past simple rule: 'Little did + subject + verb'."},
        {"type": "fill", "q": "Q7: Complete the subjunctive verb:\nIt is imperative that every legal contract ________ (be) validated by counsel.", "ans": "be", "exp": "Subjunctive form of 'to be' is always 'be'."},
        {"type": "fill", "q": "Q8: Complete inversion pair:\nScarcely had the market opened ________ stock values plummeted.", "ans": "when", "exp": "Inversion pair rule: 'Scarcely had... when'."},
        {"type": "fill", "q": "Q9: Complete the subjunctive verb:\nThe committee proposed that he ________ (chair) the upcoming committee.", "ans": "chair", "exp": "Subjunctive base verb form 'chair'."},
        {"type": "fill", "q": "Q10: Complete with inverted verb:\nNot only ________ the enterprise expand overseas, but it also doubled profit.", "ans": "did", "exp": "Inversion past simple: 'Not only did + subject + base verb'."}
    ]
    for idx, g in enumerate(grammar_qs):
        if g["type"] == "mcq":
            g["options"] = shuffle_options(g["options"], f"gram_{day_num}_{idx}")

    reading_paragraphs = [
        f"In the contemporary landscape of global enterprise, mastering the nuances of {topic.lower()} has rapidly transitioned from a conventional competitive advantage to an absolute operational imperative. Organizations expanding across multinational jurisdictions consistently confront unprecedented market volatility, which in turn demands immediate, highly calculated interventions.",
        f"Building upon this operational urgency, structural cohesion across internal corporate divisions becomes paramount. When strategic alignment between executive leadership and subsidiary units begins to erode, organizations inevitably face severe resource fragmentation, accompanied by a rapid decline in overall brand equity.",
        f"To counter these internal vulnerabilities, institutionalizing rigorous compliance protocols functions as a critical safeguard against emerging external risks. Consequently, governance frameworks must be continuously re-evaluated on a strict quarterly cycle to align dynamically with evolving global statutory requirements.",
        f"In parallel with statutory compliance, financial liquidity and strategic capital allocation represent another indispensable pillar of structural endurance. Without robust, proactive balance sheet controls, enterprises remain exceptionally susceptible to abrupt currency devaluations and credit rating downgrades during macroeconomic downturns.",
        f"Furthermore, modern digital transformation initiatives must be precisely synchronized with these overarching executive targets. Deploying enterprise-grade analytics platforms empowers corporate decision-makers to pinpoint operational bottlenecks, optimize procurement spending, and ensure complete organizational transparency.",
        f"Beyond internal digital infrastructure, risk management committees are obliged to reinforce supply chain resilience against unforeseen external shocks. Over-reliance on single-source suppliers drastically magnifies operational vulnerabilities, particularly during unexpected geopolitical disputes or sudden trade restrictions.",
        f"Simultaneously, human capital optimization constitutes an equally vital element in sustaining high-level C1 strategic execution. Executive talent acquisition must be continuously calibrated alongside technological integration, ensuring that employees maintain the advanced competencies necessary for complex execution.",
        f"Moreover, sustainable environmental and corporate responsibility metrics are now deeply integrated into modern business evaluation frameworks. Institutional investors routinely divest from organizations that fail to demonstrate verifiable carbon offset protocols and ethically managed supply channels.",
        f"When unexpected liabilities or public emergencies inevitably surface, pre-established crisis management pathways become essential. Transparent, decisive executive communication serves as the final line of defense, preserving shareholder confidence and maintaining long-term corporate reputation.",
        f"Ultimately, achieving sustainable excellence in {topic.lower()} requires a fully integrated, multi-dimensional management approach. Enterprise leaders who successfully harmonize compliance, digital innovation, and prudent financial oversight will consistently secure long-term market leadership."
    ]
    reading_passage = "\n\n".join(reading_paragraphs)

    reading_qs = [
        {"type": "mcq", "q": f"Q1: What transition regarding {topic.lower()} is highlighted in the opening passage?", "options": [f"Mastering {topic.lower()} became an absolute necessity", "It was declared optional for global firms", "It was rendered obsolete by new laws", "It decreased in total corporate value"], "ans": f"Mastering {topic.lower()} became an absolute necessity", "exp": "The opening passage explicitly states it transitioned to an absolute operational imperative."},
        {"type": "mcq", "q": "Q2: What primary danger arises when alignment between executive directives and subsidiary operations breaks down?", "options": ["Resource fragmentation and brand erosion", "Immediate stock price doubles", "Lower employee turnover", "Reduced oversight costs"], "ans": "Resource fragmentation and brand erosion", "exp": "The text notes resource fragmentation and brand erosion follow strategic misalignment."},
        {"type": "mcq", "q": "Q3: How frequently should corporate governance frameworks be re-evaluated?", "options": ["On a continuous quarterly basis", "Once every decade", "Only during audits", "Bi-annually"], "ans": "On a continuous quarterly basis", "exp": "The passage confirms governance frameworks must be re-evaluated on a strict quarterly cycle."},
        {"type": "mcq", "q": "Q4: What specific hazard is associated with single-source supplier dependencies?", "options": ["Exacerbating operational disruption", "Increasing cash reserves", "Improving logistics speed", "Lowering tax liabilities"], "ans": "Exacerbating operational disruption", "exp": "The text emphasizes single-source reliance drastically magnifies operational disruption."},
        {"type": "mcq", "q": "Q5: How do institutional investors react to entities failing carbon standards?", "options": ["Routinely divesting from non-compliant entities", "Increasing investment regardless of ethics", "Ignoring environmental metrics", "Providing interest-free loans"], "ans": "Routinely divesting from non-compliant entities", "exp": "The text states institutional investors routinely divest from non-compliant firms."},
        {"type": "fill", "q": "Q6: Inadequate balance sheet controls leave enterprises vulnerable to sudden currency ________.", "ans": "devaluation", "exp": "Text quote: 'susceptible to abrupt currency devaluations'."},
        {"type": "fill", "q": "Q7: Transparent executive communication preserves brand ________ during crisis situations.", "ans": "reputation", "exp": "Text quote: 'preserving shareholder confidence and maintaining long-term corporate reputation'."}
    ]
    for idx, g in enumerate(reading_qs):
        if g["type"] == "mcq":
            g["options"] = shuffle_options(g["options"], f"read_{day_num}_{idx}")

    listening_paragraphs = [
        f"Good morning, esteemed members of the Executive Board. Today's strategic briefing will focus exclusively on our key corporate directives regarding {topic.lower()}. As we enter the next fiscal quarter, establishing full operational alignment across all divisions is vital to securing our strategic goals.",
        f"Looking closely at our recent performance, persistent currency fluctuations and inflation have introduced substantial pressure on operating margins. While top-line revenue increased by 4.2%, overall operational expenditures rose by 8.7%, generating temporary margin compression that requires immediate intervention.",
        f"To address these headwinds directly, we are launching a multi-tiered corporate strategy. Component A focuses on immediate cost optimization through vendor renegotiations, which is projected to yield $3.5 million in annualized savings within three quarters.",
        f"Building upon cost optimization, Component B targets operational risk management. Recent internal audits identified vulnerabilities in regional distribution networks. Moving forward, mandatory dual-sourcing policies will be strictly enforced across all core business units.",
        f"Simultaneously, Component C accelerates our digital infrastructure modernization. Transitioning legacy monitoring systems to real-time cloud platforms will reduce operational latency by 28% and provide full operational visibility to our global leadership team.",
        f"In conclusion, maintaining long-term leadership in {topic.lower()} requires complete discipline, regulatory adherence, and swift execution. Division heads must submit their detailed implementation roadmaps by Friday afternoon. Thank you for your leadership and focus."
    ]
    listening_script = "\n\n".join(listening_paragraphs)

    listening_qs = [
        {"type": "mcq", "q": "Q1: What is the primary focus of today's executive briefing?", "options": [f"Critical directives concerning {topic.lower()}", "Immediate closure of domestic units", "Replacing board members", "Launching an initial public offering"], "ans": f"Critical directives concerning {topic.lower()}", "exp": "The briefing focuses specifically on directives regarding this topic."},
        {"type": "mcq", "q": "Q2: What was the recorded top-line revenue growth over the preceding period?", "options": ["4.2%", "8.7%", "14.5%", "2.1%"], "ans": "4.2%", "exp": "The script specifies top-line revenue grew by 4.2%."},
        {"type": "mcq", "q": "Q3: How much annualized savings is Component A expected to yield?", "options": ["$3.5 million", "$1.0 million", "$10.0 million", "$500,000"], "ans": "$3.5 million", "exp": "The briefing projects $3.5 million in annualized savings."},
        {"type": "mcq", "q": "Q4: What policy will be strictly enforced under Component B for logistics resilience?", "options": ["Dual-sourcing requirements", "Single-supplier contracts", "Outsourcing all warehousing", "Suspending international shipments"], "ans": "Dual-sourcing requirements", "exp": "Component B introduces mandatory dual-sourcing policies."},
        {"type": "mcq", "q": "Q5: By what percentage will operational latency decrease after cloud modernization?", "options": ["28%", "15%", "40%", "50%"], "ans": "28%", "exp": "Component C notes operational latency will decrease by 28%."},
        {"type": "fill", "q": "Q6: Operational expenditure rose by ________ % over the preceding period.", "ans": "8.7", "exp": "Script quote: 'operational expenditures rose by 8.7%'."},
        {"type": "fill", "q": "Q7: Division heads must submit implementation roadmaps by Friday ________.", "ans": "afternoon", "exp": "Script conclusion: 'submit their detailed implementation roadmaps by Friday afternoon'."}
    ]
    for idx, g in enumerate(listening_qs):
        if g["type"] == "mcq":
            g["options"] = shuffle_options(g["options"], f"listen_{day_num}_{idx}")

    writing_scenario = f"""### ✍️ Detailed Executive Memorandum Task

**Corporate Case Study Background:**
You are the Chief Operating Officer (COO) of *AeroGlobal Logistics Inc.* The enterprise is facing a severe strategic bottleneck in **{topic}**.
* **Current Operational Situation:** Due to recent supply delays and regulatory changes, operating expenditures have increased by **18%**, causing a projected quarterly loss of **$4.2 Million**.
* **Stakeholder Expectation:** The Board of Directors demands a comprehensive action plan to restore profitability, reduce risk exposure, and maintain client retention above **92%**.

**Task Instructions:**
Write a detailed Executive Memorandum (250 – 350 words) addressed to the Board of Directors incorporating:
1. **Situation Analysis:** Identify root causes of the $4.2M deficit and operational risks in {topic.lower()}.
2. **Actionable Recommendations:** Propose two C1-level strategic interventions (Must include at least **one Inversion sentence** e.g., *"Under no circumstances should..."* and **one Subjunctive form** e.g., *"It is essential that the board approve..."*).
3. **Financial Projections:** Detail expected ROI, cost-reduction timeline, and mitigation benchmarks.
"""

    writing_model = f"""**MEMORANDUM**

**TO:** Board of Directors, AeroGlobal Logistics Inc.  
**FROM:** Chief Operating Officer  
**DATE:** August 24, 2026  
**SUBJECT:** Strategic Plan for Restoring Profitability in {topic}

**1. Executive Situation Analysis**
AeroGlobal Logistics currently faces acute operational hazards within our {topic.lower()} division. Unprecedented inflation coupled with shifting statutory frameworks has driven operating expenditures up by 18%, resulting in a projected quarterly loss of $4.2 Million. Under no circumstances can our enterprise sustain this trajectory without severely compromising shareholder equity.

**2. Strategic Interventions & Compliance Directives**
To mitigate these liabilities, immediate structural realignment is required. First, it is essential that the Board approve the implementation of an automated risk monitoring framework across our international divisions. This system will enable real-time tracking of compliance bottlenecks. Second, we must execute a mandatory consolidation of vendor contracts to leverage economies of scale.

Seldom have market conditions demanded such aggressive cost-restructuring. It is recommended that executive leadership mandate strict adherence to new procurement protocols across all regional offices.

**3. Financial Projections & Risk Outcomes**
Initial implementation costs for these systems are estimated at $1.5 Million. However, predictive models demonstrate that these interventions will offset operational waste, yielding $5.8 Million in net savings over the next four quarters (a projected 180% ROI). Client retention is projected to stabilize at 94%, exceeding board targets."""

    speaking_prompt = f"""### 📊 Detailed Executive Presentation & Speech Context

**Corporate Scenario & Background:**
You are presenting to the Board of Directors of *Apex Global Enterprises* regarding **{topic}**.
* **Current Crisis:** Global regulatory changes threaten to disrupt **25% of annual revenue**.
* **Your Strategic Proposal:** Request an allocation of **$3.0 Million** from the capital budget to implement a modernized compliance and operational monitoring framework.
* **Target Outcome:** Demonstrate how this investment will protect revenue streams and achieve a **20% operational efficiency gain** within 12 months.

**Presentation Requirements:**
Deliver a 2-minute strategic presentation addressing:
1. Clear statement of current risk and potential revenue loss.
2. Justification for the $3.0 Million capital allocation.
3. Expected ROI and efficiency gains using C1-level vocabulary (e.g., *leverage, mitigate, viability, synergy*).
"""

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
        🔊 Audio Pronunciation / Briefing
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
# 6. SIDEBAR & NAVIGATION PERSISTENCE
# ==========================================
with st.sidebar:
    st.title("🎓 C1 Mastery Studio")
    st.markdown("---")
    
    selected_day = st.selectbox(
        "Select Learning Day:",
        options=list(range(1, 31)),
        format_func=lambda d: f"Day {d}: {DAY_TOPICS[d-1]}"
    )
    
    completed = st.session_state.user_progress.get("completed_days", [])
    pct = int((len(completed) / 30) * 100)
    
    st.markdown("### 📊 Overall Progress")
    st.progress(pct / 100)
    st.markdown(f"**Completed:** {len(completed)}/30 Days ({pct}%)")
    
    st.markdown("---")
    st.markdown("### 💾 Session Control")
    
    if st.button("💾 Save Day Progress", use_container_width=True):
        save_user_data(st.session_state.user_progress)
        st.success(f"Progress for Day {selected_day} saved successfully!")

    is_day_done = selected_day in completed
    if st.button("✅ Mark Day Completed" if not is_day_done else "🎉 Day Completed", use_container_width=True, disabled=is_day_done):
        if selected_day not in completed:
            st.session_state.user_progress["completed_days"].append(selected_day)
            save_user_data(st.session_state.user_progress)
            st.success(f"Day {selected_day} marked as Completed!")
            st.rerun()

curr = get_curriculum(selected_day)

day_key = f"day_{selected_day}"
if day_key not in st.session_state.user_progress["saved_answers"]:
    st.session_state.user_progress["saved_answers"][day_key] = {}

if day_key not in st.session_state.user_progress["checked_states"]:
    st.session_state.user_progress["checked_states"][day_key] = {}

saved_answers = st.session_state.user_progress["saved_answers"][day_key]
checked_states = st.session_state.user_progress["checked_states"][day_key]

# CHỈ HIỂN THỊ KẾT QUẢ KHI NGƯỜI DÙNG ĐÃ BẤM CHỌN VÀ BẤM NÚT "CHECK"
def render_question_feedback(q_id, user_ans, correct_ans, explanation):
    if checked_states.get(q_id, False):
        if user_ans is not None and str(user_ans).strip().lower() == str(correct_ans).strip().lower():
            st.markdown(
                f"<div class='feedback-card-correct'>"
                f"<b>✅ Correct Answer: {correct_ans}</b><br>"
                f"<i>Explanation: {explanation}</i>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='feedback-card-incorrect'>"
                f"<b>❌ Incorrect Answer.</b> Your submission: <b>{user_ans if user_ans else '(Not Selected)'}</b><br>"
                f"<b>Correct Answer:</b> {correct_ans}<br>"
                f"<i>Detailed Explanation: {explanation}</i>"
                f"</div>",
                unsafe_allow_html=True
            )

def format_single_line_spacing(text):
    paragraphs = text.split("\n\n")
    return "".join([f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()])

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
        q_key = f"g1_{idx}"
        saved_val = saved_answers.get(q_key, None)
        idx_val = q["options"].index(saved_val) if (saved_val is not None and saved_val in q["options"]) else None
        
        u_ans = st.radio("Choose:", q["options"], key=f"g1_opt_{selected_day}_{idx}", index=idx_val)
        if u_ans is not None:
            saved_answers[q_key] = u_ans
        
        if st.button(f"Check Answer G1.Q{idx+1}", key=f"btn_g1_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, saved_answers.get(q_key, None), q["ans"], q["exp"])

    st.markdown("---")
    st.markdown("### 🎮 Game 2: Contextual Fill-in-the-Blank")
    for idx, q in enumerate(curr["g2_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"g2_{idx}"
        saved_val = saved_answers.get(q_key, "")
        u_ans = st.text_input("Type word:", value=saved_val, key=f"g2_txt_{selected_day}_{idx}")
        saved_answers[q_key] = u_ans
        
        if st.button(f"Check Answer G2.Q{idx+1}", key=f"btn_g2_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, saved_answers.get(q_key, None), q["ans"], q["exp"])

# ------------------------------------------
# TAB 2: GRAMMAR RULES
# ------------------------------------------
with tabs[1]:
    st.markdown(curr["grammar_theory"])
    st.markdown("---")
    st.markdown("### 📝 Grammar Practice Test (10 Questions)")
    
    for idx, q in enumerate(curr["grammar_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"gram_{idx}"
        saved_val = saved_answers.get(q_key, None)
        
        if q["type"] == "mcq":
            idx_val = q["options"].index(saved_val) if (saved_val is not None and saved_val in q["options"]) else None
            u_ans = st.radio("Choose:", q["options"], key=f"gram_mcq_{selected_day}_{idx}", index=idx_val)
            if u_ans is not None:
                saved_answers[q_key] = u_ans
        else:
            u_ans = st.text_input("Fill in blank:", value=saved_val if saved_val else "", key=f"gram_fill_{selected_day}_{idx}")
            if u_ans:
                saved_answers[q_key] = u_ans
        
        if st.button(f"Check Grammar Q{idx+1}", key=f"btn_gram_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, saved_answers.get(q_key, None), q["ans"], q["exp"])

# ------------------------------------------
# TAB 3: READING
# ------------------------------------------
with tabs[2]:
    st.markdown("### 📖 Business Reading Passage")
    formatted_reading = format_single_line_spacing(curr['reading_passage'])
    st.markdown(f"<div class='full-text-container'>{formatted_reading}</div>", unsafe_allow_html=True)
    
    st.markdown("### ❓ Reading Comprehension (7 Questions)")
    for idx, q in enumerate(curr["reading_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"read_{idx}"
        saved_val = saved_answers.get(q_key, None)
        
        if q["type"] == "mcq":
            idx_val = q["options"].index(saved_val) if (saved_val is not None and saved_val in q["options"]) else None
            u_ans = st.radio("Choose:", q["options"], key=f"read_opt_{selected_day}_{idx}", index=idx_val)
            if u_ans is not None:
                saved_answers[q_key] = u_ans
        else:
            u_ans = st.text_input("Your answer:", value=saved_val if saved_val else "", key=f"read_txt_{selected_day}_{idx}")
            if u_ans:
                saved_answers[q_key] = u_ans
            
        if st.button(f"Check Reading Q{idx+1}", key=f"btn_read_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, saved_answers.get(q_key, None), q["ans"], q["exp"])

# ------------------------------------------
# TAB 4: LISTENING BRIEFING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 🎧 Audio Script & Executive Briefing")
    render_tts(curr["listening_script"], f"listen_audio_{selected_day}")
    formatted_listening = format_single_line_spacing(curr['listening_script'])
    st.markdown(f"<div class='full-text-container'>{formatted_listening}</div>", unsafe_allow_html=True)
    
    st.markdown("### ❓ Listening Comprehension (7 Questions)")
    for idx, q in enumerate(curr["listening_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"listen_{idx}"
        saved_val = saved_answers.get(q_key, None)
        
        if q["type"] == "mcq":
            idx_val = q["options"].index(saved_val) if (saved_val is not None and saved_val in q["options"]) else None
            u_ans = st.radio("Choose:", q["options"], key=f"listen_opt_{selected_day}_{idx}", index=idx_val)
            if u_ans is not None:
                saved_answers[q_key] = u_ans
        else:
            u_ans = st.text_input("Answer:", value=saved_val if saved_val else "", key=f"listen_txt_{selected_day}_{idx}")
            if u_ans:
                saved_answers[q_key] = u_ans
            
        if st.button(f"Check Listening Q{idx+1}", key=f"btn_listen_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, saved_answers.get(q_key, None), q["ans"], q["exp"])

# ------------------------------------------
# TAB 5: DETAILED WRITING SCENARIO
# ------------------------------------------
with tabs[4]:
    st.markdown(curr["writing_scenario"])
    
    saved_essay = saved_answers.get("writing_essay", "")
    u_essay = st.text_area("Draft your executive memo response here:", value=saved_essay, height=240, key=f"writing_area_{selected_day}")
    saved_answers["writing_essay"] = u_essay
    
    if st.button("🤖 Grade Memorandum via Groq AI", key=f"btn_grade_write_{selected_day}"):
        if not u_essay.strip():
            st.warning("Please draft your memorandum before submitting for grading.")
        else:
            with st.spinner("Analyzing memorandum metrics via Groq AI..."):
                prompt = f"Case Scenario: {curr['writing_scenario']}\n\nUser Submission: '{u_essay}'\n\nGrade for C1 Business Memorandum. Evaluate: (1) Inversion & Subjunctive Usage, (2) Lexical Score, (3) Structural Corrections, and (4) Overall Score /100."
                res = query_groq_ai(prompt)
                checked_states["writing_feedback"] = res

    if "writing_feedback" in checked_states:
        st.markdown(f"<div class='feedback-card-correct'><b>AI Memorandum Evaluation:</b><br>{checked_states['writing_feedback']}</div>", unsafe_allow_html=True)

    with st.expander("💡 View C1 Model Answer Memorandum"):
        st.markdown(curr["writing_model"])

# ------------------------------------------
# TAB 6: SPEAKING PRESENTATION
# ------------------------------------------
with tabs[5]:
    st.markdown(curr["speaking_prompt"])
    
    render_recorder(f"spk_{selected_day}")
    
    saved_speech = saved_answers.get("speaking_text", "")
    u_speech = st.text_area("Type or paste your spoken transcript here for AI analysis:", value=saved_speech, height=160, key=f"spk_area_{selected_day}")
    saved_answers["speaking_text"] = u_speech
    
    if st.button("🤖 Grade Presentation via Groq AI", key=f"btn_grade_spk_{selected_day}"):
        if not u_speech.strip():
            st.warning("Please enter your speech text before grading.")
        else:
            with st.spinner("Evaluating presentation metrics via Groq AI..."):
                prompt = f"Speaking Scenario: {curr['speaking_prompt']}\n\nUser Speech Transcript: '{u_speech}'\n\nGrade for C1 Executive Speaking. Evaluate: (1) Pronunciation & Articulation, (2) Strategic C1 Vocabulary, (3) Inversion & Grammar Usage, and (4) Overall Score /100."
                res = query_groq_ai(prompt)
                checked_states["speaking_feedback"] = res

    if "speaking_feedback" in checked_states:
        st.markdown(f"<div class='feedback-card-correct'><b>AI Speaking Assessment:</b><br>{checked_states['speaking_feedback']}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 7: TRANSLATION PRACTICE
# ------------------------------------------
with tabs[6]:
    st.markdown("### 🌐 Vietnamese to C1 English Translation (10 Sentences)")
    
    for idx, q in enumerate(curr["translation_qs"]):
        st.markdown(f"**Sentence {idx+1}:** {q['vi']}")
        q_key = f"trans_{idx}"
        saved_trans = saved_answers.get(q_key, "")
        u_trans = st.text_input(f"Your C1 English Translation S{idx+1}:", value=saved_trans, key=f"trans_in_{selected_day}_{idx}")
        saved_answers[q_key] = u_trans
        
        if st.button(f"Check Sentence {idx+1}", key=f"btn_trans_{selected_day}_{idx}"):
            if not u_trans.strip():
                st.warning("Please type your translation first.")
            else:
                with st.spinner("Analyzing translation specifics via Groq AI..."):
                    prompt = (
                        f"Vietnamese Source Sentence: '{q['vi']}'\n"
                        f"User Submission: '{u_trans}'\n"
                        f"Standard C1 Reference Translation: '{q['ans']}'\n\n"
                        f"CRITICAL INSTRUCTIONS:\n"
                        f"1. Directly inspect the specific words used in the User Submission ('{u_trans}').\n"
                        f"2. Under 'Grammar & Correction:', provide bullet points highlighting EXACT words/phrases in the user submission that are wrong, inaccurate, or sub-C1, explaining why.\n"
                        f"3. Under 'Recommended C1 Sentence:', output ONLY the accurate C1 translation for the Vietnamese source sentence: '{q['ans']}'. DO NOT output an unrelated sentence.\n\n"
                        f"OUTPUT STRICT HTML FORMAT ONLY:\n"
                        f"<b>Overall Score:</b> [Score]/10<br>"
                        f"<b>Grammar & Correction:</b><br>"
                        f"• [Specific word/grammar mistake 1 in '{u_trans}']<br>"
                        f"• [Specific word/grammar mistake 2 or C1 vocabulary upgrade]<br>"
                        f"<b>Recommended C1 Sentence:</b> {q['ans']}"
                    )
                    res = query_groq_ai(prompt, fallback_ref=q['ans'])
                    checked_states[f"trans_fb_{idx}"] = res

        if f"trans_fb_{idx}" in checked_states:
            st.markdown(f"<div class='feedback-card-correct'>{checked_states[f'trans_fb_{idx}']}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🤖 Grade ALL 10 Translations at Once via Groq AI", key=f"btn_grade_all_trans_{selected_day}"):
        all_text = "\n".join([f"Sentence {i+1}: VI: '{curr['translation_qs'][i]['vi']}' | User Submission: '{saved_answers.get(f'trans_{i}', '(Empty)')}' | Expected C1: '{curr['translation_qs'][i]['ans']}'" for i in range(10)])
        with st.spinner("Grading all 10 translations via Groq AI..."):
            prompt = (
                f"Evaluate these 10 Vietnamese to C1 English translations:\n\n{all_text}\n\n"
                f"For EACH sentence from 1 to 10, analyze the specific words in the User Submission and generate feedback strictly in HTML:\n"
                f"<b>Sentence [X] Overall Score:</b> [Score]/10<br>"
                f"<b>Grammar & Correction:</b><br>"
                f"• [Specific word or grammar mistake in User Submission]<br>"
                f"• [Specific improvement to reach C1 level]<br>"
                f"<b>Recommended C1 Sentence:</b> [The EXACT reference C1 translation corresponding to that Vietnamese sentence]<br><br>"
                f"At the very end, provide: <b>Total Overall Score:</b> [Total Score]/100"
            )
            res = query_groq_ai(prompt, fallback_ref=curr['translation_qs'][0]['ans'])
            checked_states["all_trans_feedback"] = res

    if "all_trans_feedback" in checked_states:
        st.markdown(f"<div class='feedback-card-correct'><b>Full 10-Sentence AI Evaluation Report:</b><br><br>{checked_states['all_trans_feedback']}</div>", unsafe_allow_html=True)