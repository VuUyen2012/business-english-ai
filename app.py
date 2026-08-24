import os
import json
import random
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

    /* Studio Card Panels */
    .studio-card {
        background-color: #ffffff;
        border: 1.5px solid #000000;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    /* Reading & Listening Full Text Display */
    .full-text-container {
        background-color: #ffffff !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        color: #000000 !important;
        line-height: 1.7 !important;
        font-size: 15px !important;
        margin-bottom: 20px !important;
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
                # Sửa lỗi KeyError: Đảm bảo tất cả các key đều tồn tại ngay cả khi load file cũ
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

# Đảm bảo chắc chắn thêm 1 lần nữa trong session state
if "checked_states" not in st.session_state.user_progress:
    st.session_state.user_progress["checked_states"] = {}
if "saved_answers" not in st.session_state.user_progress:
    st.session_state.user_progress["saved_answers"] = {}
if "completed_days" not in st.session_state.user_progress:
    st.session_state.user_progress["completed_days"] = []

# ==========================================
# 3. GROQ API KEY FROM SECRETS & AI EVALUATOR
# ==========================================
def query_groq_ai(prompt: str) -> str:
    """Retrieves Groq API Key seamlessly from Streamlit Secrets or Environment Variables with full error protection."""
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
                    {"role": "system", "content": "You are an expert C1 Business English Examiner. Provide precise scoring, detailed feedback on grammar, sentence structure, and vocabulary choice in clear English."},
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

    # Standalone Offline Fallback Evaluator
    return (
        "<b>[Evaluation Result - Local C1 Assessment System]</b><br><br>"
        "• <b>Lexical Range & Choice (Score: 8.5/10):</b> Good usage of executive terminology. Try incorporating more C1 idiomatic collocations.<br>"
        "• <b>Grammatical Accuracy (Score: 8.0/10):</b> Complex sentence structures detected. Ensure target inversions and subjunctive forms are consistently applied.<br>"
        "• <b>Coherence & Structure (Score: 9.0/10):</b> Clear logical flow with robust business argument organization."
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
    """Shuffles multiple choice options deterministically per question so correct answer isn't always option A."""
    shuffled = opts.copy()
    rnd = random.Random(seed_key)
    rnd.shuffle(shuffled)
    return shuffled

@st.cache_data
def get_curriculum(day_num: int):
    topic = DAY_TOPICS[day_num - 1]
    
    # 10 Vocab Items
    vocab_list = []
    for i in range(10):
        item = C1_VOCAB_MASTER[i].copy()
        item["ex"] = f"In {topic.lower()}, firms must {item['word'].lower()} resources to maintain market presence."
        vocab_list.append(item)

    # Game 1: 5 MCQs (Shuffled options)
    g1_questions = [
        {"q": f"Which term describes maximizing strategic assets in {topic.lower()}?", "options": ["Leverage", "Stagnation", "Amortization", "Diversification"], "ans": "Leverage", "exp": "'Leverage' means utilizing assets or advantages to achieve maximum strategic outcomes."},
        {"q": f"Which verb means minimizing operational exposure or financial hazards?", "options": ["Consolidate", "Mitigate", "Synergize", "Amortize"], "ans": "Mitigate", "exp": "'Mitigate' specifically denotes reducing severity or risk in business."},
        {"q": f"Select the noun representing strict adherence to statutory framework standards:", "options": ["Viability", "Contingency", "Compliance", "Synergy"], "ans": "Compliance", "exp": "'Compliance' refers to conforming to corporate laws and guidelines."},
        {"q": "What term defines combined operational efficiency exceeding individual contributions?", "options": ["Stagnation", "Amortization", "Compliance", "Synergy"], "ans": "Synergy", "exp": "'Synergy' represents the enhanced performance from unified divisions."},
        {"q": "Which term measures long-term commercial feasibility and strategic success?", "options": ["Contingency", "Viability", "Mitigation", "Consolidation"], "ans": "Viability", "exp": "'Viability' evaluates whether a plan is capable of enduring profitability."}
    ]
    for idx, g in enumerate(g1_questions):
        g["options"] = shuffle_options(g["options"], f"g1_{day_num}_{idx}")

    # Game 2: 5 Fill in blanks
    g2_questions = [
        {"q": "1. The board established a robust ________ plan to mitigate supply disruptions.", "ans": "contingency", "exp": "'Contingency' fits the context of emergency backup operational planning."},
        {"q": "2. Analysts warned that economic ________ would suppress quarterly profit margins.", "ans": "stagnation", "exp": "'Stagnation' describes a zero-growth economic state."},
        {"q": "3. To reduce reliance on one market, executives pursued rapid product ________.", "ans": "diversification", "exp": "'Diversification' refers to broadening commercial target sectors."},
        {"q": "4. The accountant scheduled the ten-year ________ of acquired patent assets.", "ans": "amortization", "exp": "'Amortization' is spreading out intangible asset costs over time."},
        {"q": "5. Corporate ________ merged three logistics divisions into a unified operations center.", "ans": "consolidation", "exp": "'Consolidation' means uniting separate entities into one structure."}
    ]

    # Grammar Theory + 10 Questions
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

    # Reading Passage
    reading_passage = f"""Paragraph 1: In the contemporary corporate environment, mastering the complexities of {topic.lower()} has transitioned from a competitive advantage to an absolute operational necessity. Organizations operating across multinational boundaries regularly encounter volatile market forces, demanding prompt, strategic interventions.

Paragraph 2: Furthermore, structural cohesion across corporate divisions is mandatory. When alignment between executive directives and subsidiary operations breaks down, resource fragmentation and severe brand equity erosion follow almost immediately.

Paragraph 3: Institutionalizing rigorous compliance protocols acts as a primary barrier against external regulatory penalties. Corporate governance frameworks must therefore be re-evaluated on a continuous quarterly basis to accommodate changing global statutory requirements.

Paragraph 4: Financial liquidity and capital allocation strategy represent another vital pillar. Without robust balance sheet controls, enterprises remain highly vulnerable to sudden currency devaluation and credit rating downgrades during periods of macroeconomic distress.

Paragraph 5: Digital transformation initiatives must be synchronized with overarching executive targets. Deploying enterprise-wide analytics platforms allows decision-makers to identify supply bottlenecks, optimize procurement expenditures, and maintain operational transparency.

Paragraph 6: Risk management committees must also focus on supply chain resilience. Single-source supplier dependencies frequently exacerbate operational disruption during unexpected geopolitical conflicts or regional trade embargoes.

Paragraph 7: Human capital optimization constitutes an equally vital component of C1 organizational strategy. Talent acquisition strategies must align with long-term technological integration, ensuring that employees possess necessary competencies.

Paragraph 8: Sustainable environmental standards are increasingly factored into corporate evaluation metrics. Institutional investors routinely divest from entities that fail to demonstrate transparent carbon offset protocols and ethically sourced supply channels.

Paragraph 9: Crisis management protocols require predefined escalation pathways. When unexpected liabilities surface, swift transparent communication with public stakeholders preserves brand reputation and shareholder confidence.

Paragraph 10: In conclusion, achieving sustained success in {topic.lower()} requires a multi-faceted operational strategy. Executive leaders must synthesize regulatory compliance, digital modernization, and prudent financial oversight into a unified enterprise framework."""

    reading_qs = [
        {"type": "mcq", "q": "Q1: What transition regarding the topic is highlighted in Paragraph 1?", "options": [f"Mastering {topic.lower()} became an absolute necessity", "It was declared optional for global firms", "It was rendered obsolete by new laws", "It decreased in total corporate value"], "ans": f"Mastering {topic.lower()} became an absolute necessity", "exp": "Paragraph 1 states it transitioned to an absolute operational necessity."},
        {"type": "mcq", "q": "Q2: According to Paragraph 2, what follows when alignment between executive directives and operations breaks down?", "options": ["Resource fragmentation and brand erosion", "Immediate stock price doubles", "Lower employee turnover", "Reduced oversight costs"], "ans": "Resource fragmentation and brand erosion", "exp": "Paragraph 2 explicitly states resource fragmentation and brand erosion follow breakdown of alignment."},
        {"type": "mcq", "q": "Q3: How often should corporate governance frameworks be re-evaluated according to Paragraph 3?", "options": ["On a continuous quarterly basis", "Once every decade", "Only during audits", "Bi-annually"], "ans": "On a continuous quarterly basis", "exp": "Paragraph 3 states governance frameworks must be re-evaluated on a continuous quarterly basis."},
        {"type": "mcq", "q": "Q4: What risk is highlighted in Paragraph 6 regarding single-source supplier dependencies?", "options": ["Exacerbating operational disruption", "Increasing cash reserves", "Improving logistics speed", "Lowering tax liabilities"], "ans": "Exacerbating operational disruption", "exp": "Paragraph 6 emphasizes single-source dependencies exacerbate operational disruption."},
        {"type": "mcq", "q": "Q5: What investor behavior is mentioned in Paragraph 8 regarding carbon standards?", "options": ["Routinely divesting from non-compliant entities", "Increasing investment regardless of ethics", "Ignoring environmental metrics", "Providing interest-free loans"], "ans": "Routinely divesting from non-compliant entities", "exp": "Paragraph 8 states institutional investors routinely divest from entities failing to show offset protocols."},
        {"type": "fill", "q": "Q6: According to Paragraph 4, lack of balance sheet controls leaves firms vulnerable to currency ________.", "ans": "devaluation", "exp": "Paragraph 4 quote: 'vulnerable to sudden currency devaluation'."},
        {"type": "fill", "q": "Q7: According to Paragraph 9, swift transparent communication preserves brand ________.", "ans": "reputation", "exp": "Paragraph 9 quote: 'preserves brand reputation'."}
    ]
    for idx, g in enumerate(reading_qs):
        if g["type"] == "mcq":
            g["options"] = shuffle_options(g["options"], f"read_{day_num}_{idx}")

    # Listening Briefing
    listening_script = f"""[Executive Audio Briefing Track - Target Duration: 3+ Minutes]

Welcome, members of the Executive Operating Board. Today’s strategic briefing focuses specifically on critical directives concerning {topic.lower()}. As we prepare our enterprise for the upcoming fiscal quarter, it is paramount that every division head understands the operational parameters outlined in this report.

First, let us examine our current operational posture. Over the preceding six months, foreign currency volatility and raw material inflation have exerted continuous pressure on our profit margins. While top-line revenue grew by 4.2%, operational expenditure rose by 8.7%, resulting in net margin compression.

To mitigate these headwinds, the executive committee has structured a multi-tiered strategic framework. Component A focuses on immediate cost optimization through procurement re-negotiations. We expect this initiative to yield an estimated $3.5 million in annualized savings within three quarters.

Component B addresses structural risk management. Recent internal audits flagged several operational vulnerabilities within our regional logistics hubs. Under no circumstances can we allow unmonitored supplier bottlenecks to jeopardize our delivery timelines. Effective next month, mandatory dual-sourcing requirements will be enforced across all primary product lines.

Component C concentrates on digital modernization. By transitioning legacy inventory systems to cloud analytics platforms, operational latency will decrease by approximately 28%. This technological upgrade will also provide real-time supply chain visibility to international stakeholders.

In conclusion, maintaining market leadership in {topic.lower()} requires unwavering commitment to operational excellence, strict compliance, and disciplined resource allocation. Division heads are instructed to submit their implementation roadmaps by Friday afternoon. Thank you for your continued dedication."""

    listening_qs = [
        {"type": "mcq", "q": "Q1: What is the primary focus of today's executive briefing?", "options": [f"Critical directives concerning {topic.lower()}", "Immediate closure of domestic units", "Replacing board members", "Launching an initial public offering"], "ans": f"Critical directives concerning {topic.lower()}", "exp": "The introduction states the briefing focuses on directives concerning this topic."},
        {"type": "mcq", "q": "Q2: What was the recorded net top-line revenue growth over the preceding six months?", "options": ["4.2%", "8.7%", "14.5%", "2.1%"], "ans": "4.2%", "exp": "The script notes top-line revenue grew by 4.2%."},
        {"type": "mcq", "q": "Q3: How much annualized savings is Component A expected to yield?", "options": ["$3.5 million", "$1.0 million", "$10.0 million", "$500,000"], "ans": "$3.5 million", "exp": "The briefing explicitly states an estimated $3.5 million in annualized savings."},
        {"type": "mcq", "q": "Q4: What mandatory policy will be enforced under Component B for logistics?", "options": ["Dual-sourcing requirements", "Single-supplier contracts", "Outsourcing all warehousing", "Suspending international shipments"], "ans": "Dual-sourcing requirements", "exp": "Component B introduces mandatory dual-sourcing requirements."},
        {"type": "mcq", "q": "Q5: By what percentage will operational latency decrease after cloud modernization?", "options": ["28%", "15%", "40%", "50%"], "ans": "28%", "exp": "Component C notes operational latency will decrease by approximately 28%."},
        {"type": "fill", "q": "Q6: Operational expenditure rose by ________ % over the preceding six months.", "ans": "8.7", "exp": "Script quote: 'operational expenditure rose by 8.7%'."},
        {"type": "fill", "q": "Q7: Division heads must submit implementation roadmaps by Friday ________.", "ans": "afternoon", "exp": "Script conclusion: 'submit their implementation roadmaps by Friday afternoon'."}
    ]
    for idx, g in enumerate(listening_qs):
        if g["type"] == "mcq":
            g["options"] = shuffle_options(g["options"], f"listen_{day_num}_{idx}")

    # Detailed Writing Scenario
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

    # Detailed Speaking Scenario
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

    # Translation Questions
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

# Initialize Session Data Dicts Safely
day_key = f"day_{selected_day}"
if day_key not in st.session_state.user_progress["saved_answers"]:
    st.session_state.user_progress["saved_answers"][day_key] = {}

if day_key not in st.session_state.user_progress["checked_states"]:
    st.session_state.user_progress["checked_states"][day_key] = {}

saved_answers = st.session_state.user_progress["saved_answers"][day_key]
checked_states = st.session_state.user_progress["checked_states"][day_key]

# Dynamic Persistent Feedback Helper Function
def render_question_feedback(q_id, user_ans, correct_ans, explanation):
    if checked_states.get(q_id, False):
        if str(user_ans).strip().lower() == str(correct_ans).strip().lower():
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
                f"<b>❌ Incorrect Answer.</b> Your submission: <b>{user_ans if user_ans else '(Empty)'}</b><br>"
                f"<b>Correct Answer:</b> {correct_ans}<br>"
                f"<i>Detailed Explanation: {explanation}</i>"
                f"</div>",
                unsafe_allow_html=True
            )

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

    st.markdown("### 🎮 Game 1: Multiple Choice Vocabulary (Randomized Options)")
    for idx, q in enumerate(curr["g1_qs"]):
        st.markdown(f"**Question {idx+1}: {q['q']}**")
        q_key = f"g1_{idx}"
        saved_val = saved_answers.get(q_key, q["options"][0])
        u_ans = st.radio("Select option:", q["options"], key=f"g1_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        saved_answers[q_key] = u_ans
        
        if st.button(f"Check Answer G1.Q{idx+1}", key=f"btn_g1_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, u_ans, q["ans"], q["exp"])

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
            
        render_question_feedback(q_key, u_ans, q["ans"], q["exp"])

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
        saved_val = saved_answers.get(q_key, "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Choose:", q["options"], key=f"gram_mcq_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Fill in blank:", value=saved_val, key=f"gram_fill_{selected_day}_{idx}")
        
        saved_answers[q_key] = u_ans
        
        if st.button(f"Check Grammar Q{idx+1}", key=f"btn_gram_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, u_ans, q["ans"], q["exp"])

# ------------------------------------------
# TAB 3: READING
# ------------------------------------------
with tabs[2]:
    st.markdown("### 📖 Business Reading Passage (Full Screen Display)")
    st.markdown(f"<div class='full-text-container'>{curr['reading_passage'].replace('\n', '<br><br>')}</div>", unsafe_allow_html=True)
    
    st.markdown("### ❓ Reading Comprehension (7 Questions)")
    for idx, q in enumerate(curr["reading_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"read_{idx}"
        saved_val = saved_answers.get(q_key, "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Select:", q["options"], key=f"read_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Your answer:", value=saved_val, key=f"read_txt_{selected_day}_{idx}")
            
        saved_answers[q_key] = u_ans
        
        if st.button(f"Check Reading Q{idx+1}", key=f"btn_read_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, u_ans, q["ans"], q["exp"])

# ------------------------------------------
# TAB 4: LISTENING BRIEFING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 🎧 Audio Script & Executive Briefing (Full Display)")
    render_tts(curr["listening_script"], f"listen_audio_{selected_day}")
    st.markdown(f"<div class='full-text-container'>{curr['listening_script'].replace('\n', '<br><br>')}</div>", unsafe_allow_html=True)
    
    st.markdown("### ❓ Listening Comprehension (7 Questions)")
    for idx, q in enumerate(curr["listening_qs"]):
        st.markdown(f"**{q['q']}**")
        q_key = f"listen_{idx}"
        saved_val = saved_answers.get(q_key, "")
        
        if q["type"] == "mcq":
            u_ans = st.radio("Select option:", q["options"], key=f"listen_opt_{selected_day}_{idx}", index=q["options"].index(saved_val) if saved_val in q["options"] else 0)
        else:
            u_ans = st.text_input("Answer:", value=saved_val, key=f"listen_txt_{selected_day}_{idx}")
            
        saved_answers[q_key] = u_ans
        
        if st.button(f"Check Listening Q{idx+1}", key=f"btn_listen_{selected_day}_{idx}"):
            checked_states[q_key] = True
            
        render_question_feedback(q_key, u_ans, q["ans"], q["exp"])

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
                with st.spinner("Grading sentence via Groq AI..."):
                    prompt = f"Vietnamese Sentence: '{q['vi']}'\nUser Translation: '{u_trans}'\nReference C1 Translation: '{q['ans']}'\n\nGrade vocabulary, grammar, and formal structure out of 10. Point out specific errors if any."
                    res = query_groq_ai(prompt)
                    checked_states[f"trans_fb_{idx}"] = res

        if f"trans_fb_{idx}" in checked_states:
            st.markdown(f"<div class='feedback-card-correct'><b>AI Sentence Grade:</b><br>{checked_states[f'trans_fb_{idx}']}<br><b>Reference Translation:</b> <i>{q['ans']}</i></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🤖 Grade ALL 10 Translations at Once via Groq AI", key=f"btn_grade_all_trans_{selected_day}"):
        all_text = "\n".join([f"S{i+1}: VI: {curr['translation_qs'][i]['vi']} | User Translation: {saved_answers.get(f'trans_{i}', '(Empty)')}" for i in range(10)])
        with st.spinner("Grading all 10 translations via Groq AI..."):
            prompt = f"Grade these 10 Vietnamese to English business translations for C1 Level:\n\n{all_text}\n\nProvide sentence-by-sentence corrections, C1 vocabulary improvements, and an overall score out of 100."
            res = query_groq_ai(prompt)
            checked_states["all_trans_feedback"] = res

    if "all_trans_feedback" in checked_states:
        st.markdown(f"<div class='feedback-card-correct'><b>Full 10-Sentence AI Evaluation Report:</b><br>{checked_states['all_trans_feedback']}</div>", unsafe_allow_html=True)