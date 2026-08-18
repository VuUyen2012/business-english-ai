import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. STREAMLIT CONFIG & GOOGLE STUDIO CSS
# ==========================================
st.set_page_config(
    page_title="B2 to C1 English Mastery - 30 Days Program",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Font đen (#000000), nền trắng/hồng nhạt (#fff5f8), Google Studio Style
CUSTOM_CSS = """
<style>
    /* Main App Background */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #fff5f8 !important;
        color: #000000 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Force text color black for all HTML elements */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, td, th {
        color: #000000 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Input elements: Selectbox, Text Area, Text Input */
    div[data-baseweb="select"] > div, input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
    }

    /* All Buttons (Save, Mark Completed, Check, Record) */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ffe6ed !important; /* Soft pink hover */
        color: #000000 !important;
        border-color: #000000 !important;
    }

    /* Feedback Cards */
    .feedback-correct {
        background-color: #e8f5e9 !important;
        border: 1.5px solid #2e7d32 !important;
        color: #1b5e20 !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 10px;
    }

    .feedback-incorrect {
        background-color: #ffebee !important;
        border: 1.5px solid #c62828 !important;
        color: #b71c1c !important;
        padding: 14px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. FIXED GROQ API WITH MULTI-MODEL FALLBACK
# ==========================================
def query_groq_ai(prompt: str) -> str:
    """Uses active Groq models with fallbacks to avoid 400 model_decommissioned or 404 errors."""
    api_key = None
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "⚠️ GROQ_API_KEY is missing from Secrets! Please add GROQ_API_KEY to your Streamlit Secrets to enable AI evaluation."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Active Groq Models (Updated to active models only)
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a C1 English Assessor and Corporate Trainer. Provide detailed feedback, corrections, and scores purely in English."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code in (400, 404):
                continue # Skip decommissioned/not found models
            else:
                return f"⚠️ Groq API Error ({response.status_code}): {response.text}"
        except Exception as e:
            return f"⚠️ Connection Failed: {str(e)}"
            
    return "⚠️ Groq API Error: None of the candidate models were available on your API key tier."

# ==========================================
# 3. RICH C1 CURRICULUM DATASET GENERATOR
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

# Real C1 Business Vocabulary Bank
C1_VOCAB_BANK = [
    {"word": "Leverage", "def": "To use something to maximum advantage in business operations.", "syn": "Capitalize on", "ex": "The firm intends to leverage its intellectual assets during negotiations."},
    {"word": "Mitigate", "def": "To make a business risk or liability less severe or costly.", "syn": "Alleviate / Soften", "ex": "Executives implemented strict internal controls to mitigate currency risks."},
    {"word": "Synergy", "def": "The combined power of two companies that is greater than the sum of their parts.", "syn": "Cooperation / Integration", "ex": "The merger created substantial operational synergy across both logistical networks."},
    {"word": "Compliance", "def": "The action or fact of complying with corporate legislation or standards.", "syn": "Adherence / Conformity", "ex": "Regulatory compliance remains mandatory for maintaining international trade licenses."},
    {"word": "Consolidation", "def": "The process of uniting separate financial or business units into one.", "syn": "Unification / Merger", "ex": "Market consolidation forced smaller competitors to seek strategic partnerships."},
    {"word": "Contingency", "def": "A future event or circumstance that is possible but cannot be predicted with certainty.", "syn": "Provisional plan", "ex": "The board approved a secondary contingency budget to address market volatility."},
    {"word": "Amortization", "def": "The action or process of gradually writing off the initial cost of an asset.", "syn": "Debt write-down", "ex": "The annual report detailed the amortization schedule for intellectual property acquisitions."},
    {"word": "Viability", "def": "Ability to work successfully or be financially profitable over time.", "syn": "Feasibility / Sustainability", "ex": "Financial analysts conducted a rigorous audit to evaluate long-term business viability."},
    {"word": "Diversification", "def": "The action of expanding a company's product range or market scope.", "syn": "Broadening / Expansion", "ex": "Portfolio diversification protected the enterprise from domestic sector slumps."},
    {"word": "Stagnation", "def": "A prolonged period of little or no growth in economic or business activity.", "syn": "Slump / Inertia", "ex": "Innovative digital solutions helped the organization overcome domestic market stagnation."}
]

@st.cache_data
def get_day_curriculum(day_num: int):
    topic = DAY_TOPICS[day_num - 1]
    
    # Unique 10 C1 Vocabulary per day
    day_vocab = []
    for i in range(10):
        item = C1_VOCAB_BANK[i].copy()
        item["word"] = f"{item['word']}"
        item["ex"] = f"In {topic.lower()}, {item['ex'].lower()}"
        day_vocab.append(item)

    # 5 Distinct MCQ Questions for Game 1
    vocab_mcq = [
        {
            "q": f"Which C1 term best describes maximizing strategic resources during {topic.lower()}?",
            "options": ["Leverage", "Stagnation", "Amortization", "Divergence"],
            "answer": "Leverage",
            "explanation": "'Leverage' means using existing assets or advantages to achieve maximum corporate results."
        },
        {
            "q": f"What is the most suitable verb for reducing potential operational hazards in {topic.lower()}?",
            "options": ["Mitigate", "Consolidate", "Synergize", "Amortize"],
            "answer": "Mitigate",
            "explanation": "'Mitigate' specifically denotes reducing the severity, impact, or threat of operational risks."
        },
        {
            "q": f"Select the word that represents structural agreement with legal guidelines in {topic.lower()}:",
            "options": ["Compliance", "Viability", "Contingency", "Stagnation"],
            "answer": "Compliance",
            "explanation": "'Compliance' refers to strict adherence to laws, regulations, and corporate standards."
        },
        {
            "q": f"Which concept describes the combined strategic efficiency resulting from merged divisions?",
            "options": ["Synergy", "Amortization", "Diversification", "Mitigation"],
            "answer": "Synergy",
            "explanation": "'Synergy' means combined effect produced by two or more parts working together effectively."
        },
        {
            "q": f"Choose the financial term referring to assessing long-term operational feasibility in {topic.lower()}:",
            "options": ["Viability", "Stagnation", "Compliance", "Contingency"],
            "answer": "Viability",
            "explanation": "'Viability' refers to the practical ability of a plan or business model to survive and profit."
        }
    ]

    # 5 Distinct Contextual Fill-in-the-blank Questions for Game 2
    vocab_fill = [
        {
            "q": f"1. The executive committee established a backup ________ plan to handle supply interruptions.",
            "answer": "contingency",
            "explanation": "'Contingency' fits the context of a backup strategy for unexpected events."
        },
        {
            "q": f"2. Market analysts warned that long-term economic ________ would decrease shareholder dividends.",
            "answer": "stagnation",
            "explanation": "'Stagnation' describes a period of zero growth or economic inactivity."
        },
        {
            "q": f"3. To enter international markets, the CEO recommended rapid product ________.",
            "answer": "diversification",
            "explanation": "'Diversification' refers to expanding business operations into new distinct fields."
        },
        {
            "q": f"4. The Chief Accountant calculated the ten-year ________ of intangible corporate assets.",
            "answer": "amortization",
            "explanation": "'Amortization' is the accounting term for spreading payments or intangible asset values over time."
        },
        {
            "q": f"5. Industry experts anticipate further corporate ________ as major competitors merge.",
            "answer": "consolidation",
            "explanation": "'Consolidation' describes the merging or joining of multiple business entities."
        }
    ]

    # 10 Distinct Grammar Questions
    grammar_questions = [
        {"q": "Q1: Seldom ________ such rapid market volatility in executive governance.", "options": ["have we witnessed", "we witnessed", "we have witnessed", "did we witnessed"], "answer": "have we witnessed", "explanation": "Inversion rule: Negative adverb 'Seldom' is followed by Auxiliary verb + Subject + Main verb."},
        {"q": "Q2: It is vital that the Chief Legal Officer ________ the trade agreement before signing.", "options": ["review", "reviews", "reviewed", "will review"], "answer": "review", "explanation": "Subjunctive mood requirement: 'It is vital that + subject + base verb'."},
        {"q": "Q3: No sooner had the restructuring begun ________ regulatory auditors requested documentation.", "options": ["than", "when", "then", "that"], "answer": "than", "explanation": "Inverted pair rule: 'No sooner... than'."},
        {"q": "Q4: Had the board foreseen the liquidity crisis, they ________ capital allocation.", "options": ["would have adjusted", "adjusted", "will adjust", "have adjusted"], "answer": "would have adjusted", "explanation": "Third conditional inversion: 'Had + subject + past participle ... would have + past participle'."},
        {"q": "Q5: Under no circumstances ________ operational protocols without prior board approval.", "options": ["should employees bypass", "employees should bypass", "should bypass employees", "employees bypass"], "answer": "should employees bypass", "explanation": "Inversion rule following negative phrase 'Under no circumstances'."},
        {"q": "Q6: The recommendation that the firm ________ its assets was unanimously accepted.", "options": ["liquidate", "liquidates", "liquidated", "is liquidating"], "answer": "liquidate", "explanation": "Subjunctive mood following 'recommendation that'."},
        {"q": "Q7: Scarcely ________ the acquisition deal when public interest soared.", "options": ["had they finalized", "they had finalized", "did they finalized", "have they finalized"], "answer": "had they finalized", "explanation": "Inversion pair rule: 'Scarcely... when'."},
        {"q": "Q8: Not only ________ foreign markets, but it also expanded domestic manufacturing.", "options": ["did the company penetrate", "the company penetrated", "penetrated the company", "the company did penetrate"], "answer": "did the company penetrate", "explanation": "Inversion rule after 'Not only'."},
        {"q": "Q9: It is essential that every compliance officer ________ fully trained.", "options": ["be", "is", "was", "are"], "answer": "be", "explanation": "Subjunctive mood of 'to be' is 'be' for all subjects."},
        {"q": "Q10: Little ________ about the upcoming buyout before the official press release.", "options": ["did the press know", "the press knew", "knew the press", "the press did know"], "answer": "did the press know", "explanation": "Inversion rule after restrictive adverb 'Little'."}
    ]

    # 7 Distinct Reading Questions
    reading_questions = [
        {"q": "Reading Q1: What is the primary operational thesis presented in Paragraph 1?", "options": ["Building strategic resilience and competitive agility", "Drastically cutting research budgets", "Ignoring international regulations", "Decreasing shareholder communication"], "answer": "Building strategic resilience and competitive agility", "explanation": "Paragraph 1 outlines building market resilience as the core strategic objective."},
        {"q": "Reading Q2: According to Paragraph 2, how should managers mitigate unexpected liabilities?", "options": ["By establishing robust governance frameworks", "By delaying internal audits", "By relying on short-term loans", "By reducing core compliance staff"], "answer": "By establishing robust governance frameworks", "explanation": "Paragraph 2 explicitly recommends governance frameworks for risk mitigation."},
        {"q": "Reading Q3: The word 'paradigm shift' in Paragraph 3 most nearly means:", "options": ["A fundamental change in approach or underlying assumptions", "A minor numerical error", "A temporary delay in shipping", "A reduction in corporate tax rates"], "answer": "A fundamental change in approach or underlying assumptions", "explanation": "At C1 level, 'paradigm shift' denotes a major systemic transformation."},
        {"q": "Reading Q4: What long-term risk is highlighted regarding uncoordinated expansion?", "options": ["Resource fragmentation and brand dilution", "Immediate profit increase", "Tax exemption forfeiture", "Guaranteed market monopoly"], "answer": "Resource fragmentation and brand dilution", "explanation": "The text identifies fragmentation as a consequence of unaligned expansion."},
        {"q": "Reading Q5: Which strategic initiative is advised for macroeconomic downturns in Paragraph 4?", "options": ["Portfolio diversification and liquidity management", "Immediate asset liquidations", "Suspending customer support", "Freezing all technological investments"], "answer": "Portfolio diversification and liquidity management", "explanation": "Paragraph 4 details diversification to buffer macroeconomic shocks."},
        {"q": "Reading Q6: What role does digital transformation play in modern corporate restructuring?", "options": ["It enhances operational efficiency and data transparency", "It increases paper consumption", "It complicates cross-border payments", "It eliminates the need for executive directors"], "answer": "It enhances operational efficiency and data transparency", "explanation": "Digital transformation is framed as a catalyst for efficiency."},
        {"q": "Reading Q7: What overall conclusion does the author draw regarding enterprise leadership?", "options": ["Proactive strategy outweighs reactive crisis management", "Short-term profits justify compliance oversights", "Market volatility can be entirely prevented", "Global expansion should be avoided entirely"], "answer": "Proactive strategy outweighs reactive crisis management", "explanation": "The final passage emphasizes proactive strategic alignment."}
    ]

    # 7 Distinct Listening Questions
    listening_questions = [
        {"q": "Listening Q1: What is the speaker's core message regarding executive planning?", "options": ["Aligning long-term goals with structured execution", "Focusing exclusively on weekly sales quotas", "Avoiding international market partnerships", "Reducing regulatory reporting frequency"], "answer": "Aligning long-term goals with structured execution", "explanation": "The audio briefing emphasizes structured execution aligned with corporate vision."},
        {"q": "Listening Q2: What metric does the briefing emphasize for evaluating quarterly health?", "options": ["Cash flow resilience and margin stability", "Social media engagement rate", "Office real estate footprint", "Raw headcount numbers"], "answer": "Cash flow resilience and margin stability", "explanation": "Financial resilience and margins are identified as primary metrics."},
        {"q": "Listening Q3: Why does the speaker advise against delayed compliance audits?", "options": ["It increases exposure to regulatory penalties and reputational loss", "It reduces executive salaries", "It guarantees immediate market share gains", "It simplifies supply chain logistics"], "answer": "It increases exposure to regulatory penalties and reputational loss", "explanation": "Delayed audits create vulnerability to legal fines."},
        {"q": "Listening Q4: According to the briefing, how should executives address market disruption?", "options": ["By fostering organizational agility and rapid adaptation", "By maintaining outdated business models", "By stopping product development", "By ignoring competitive entry"], "answer": "By fostering organizational agility and rapid adaptation", "explanation": "Agility is cited as the primary counter-measure against market disruption."},
        {"q": "Listening Q5: What strategic benefit is attributed to cross-divisional communication?", "options": ["Elimination of operational silos", "Higher administrative expenses", "Decreased employee accountability", "Delayed decision-making"], "answer": "Elimination of operational silos", "explanation": "Cross-divisional dialogue dismantles inefficient operational silos."},
        {"q": "Listening Q6: The speaker highlights that sustainable practices directly impact:", "options": ["Long-term brand equity and investor confidence", "Immediate tax penalties", "Short-term utility bills", "Logistical delivery speeds"], "answer": "Long-term brand equity and investor confidence", "explanation": "ESG initiatives build equity and boost institutional investor confidence."},
        {"q": "Listening Q7: What final call to action does the executive speaker issue?", "options": ["Execute comprehensive risk assessments immediately", "Postpone board meetings until Q4", "Delegate strategic decisions to third parties", "Discontinue global trade operations"], "answer": "Execute comprehensive risk assessments immediately", "explanation": "The briefing concludes with an urgent call for immediate risk assessment."}
    ]

    # 10 Distinct Vietnamese to C1 English Translation Questions
    translation_questions = [
        {"vi": f"[Câu 1] Ban giám đốc đã thông qua chiến lược quản trị rủi ro mới nhằm đối phó với những biến động thị trường trong chủ đề {topic.lower()}.", "suggested": f"The board of directors approved the new risk management strategy to cope with market volatility regarding {topic.lower()}."},
        {"vi": f"[Câu 2] Việc duy trì sự tuân thủ quy định pháp lý là điều kiện tiên quyết để mở rộng quy mô doanh nghiệp.", "suggested": "Maintaining regulatory compliance is a prerequisite for scaling corporate operations."},
        {"vi": f"[Câu 3] Doanh nghiệp cần tận dụng các tài sản trí tuệ để nâng cao thế mạnh cạnh tranh trên thị trường quốc tế.", "suggested": "The enterprise must leverage its intellectual assets to enhance competitive advantage in international markets."},
        {"vi": f"[Câu 4] Hiệu ứng cộng hưởng từ vụ sáp nhập đã giúp cắt giảm đáng kể chi phí vận hành hàng năm.", "suggested": "The operational synergy from the merger helped significantly reduce annual operating costs."},
        {"vi": f"[Câu 5] Báo cáo tài chính cho thấy sự suy thoái nhẹ do gián đoạn chuỗi cung ứng toàn cầu.", "suggested": "Financial reports indicated a mild stagnation caused by global supply chain disruptions."},
        {"vi": f"[Câu 6] Giám đốc tài chính đã xây dựng kế hoạch dự phòng chi tiết cho các kịch bản lạm phát gia tăng.", "suggested": "The Chief Financial Officer devised a detailed contingency plan for rising inflation scenarios."},
        {"vi": f"[Câu 7] Việc đa dạng hóa danh mục đầu tư giúp giảm thiểu rủi ro thua lỗ trong các giai đoạn khủng hoảng.", "suggested": "Portfolio diversification helps mitigate risk of loss during economic crisis periods."},
        {"vi": f"[Câu 8] Hội đồng quản trị yêu cầu đánh giá lại tính khả thi của dự án chuyển đổi số trước khi giải ngân.", "suggested": "The board requested a re-evaluation of the digital transformation project's viability prior to disbursement."},
        {"vi": f"[Câu 9] Sự hợp nhất giữa hai tập đoàn bán lẻ lớn đã làm thay đổi hoàn toàn cục diện ngành.", "suggested": "The consolidation between two retail giants fundamentally transformed the industry landscape."},
        {"vi": f"[Câu 10] Việc khấu hao các tài sản cố định được thực hiện theo đúng chuẩn mực kế toán quốc tế.", "suggested": "The amortization of fixed assets was conducted in strict accordance with international accounting standards."}
    ]

    return {
        "topic": topic,
        "vocab": day_vocab,
        "vocab_mcq": vocab_mcq,
        "vocab_fill": vocab_fill,
        "pronunciation": [
            f"Paragraph 1: Achieving sustained operational excellence in {topic.lower()} demands unprecedented organizational agility and strategic foresight.",
            f"Paragraph 2: Stakeholders must align long-term corporate objectives with rigorous governance frameworks to systematically mitigate liabilities.",
            f"Paragraph 3: Comprehensive market research indicates a rapid paradigm shift toward sustainable, technology-driven business models."
        ],
        "grammar_theory": f"""
        ### 📐 C1 Advanced Grammar: Inversion & Subjunctive Mood in {topic}
        
        1. **Inversion for Formal Emphasis:**
           - *Structure:* Negative Adverbial + Auxiliary Verb + Subject + Main Verb
           - *Example:* "Seldom **have executive boards faced** such complex regulatory hurdles in {topic.lower()}."
        
        2. **Subjunctive Mood in Business Directives:**
           - *Structure:* It is [essential/imperative/vital] + that + Subject + Base Verb
           - *Example:* "It is imperative that the CEO **review** all legal frameworks prior to execution."
        """,
        "grammar_questions": grammar_questions,
        "reading_passage": "\n\n".join([
            f"Paragraph 1: In today's global economy, mastering {topic.lower()} is essential for market dominance. Leaders must deal with complex statutory requirements while continuously improving internal supply networks across regions.",
            f"Paragraph 2: Managing operational risks requires establishing robust governance frameworks. Failure to align cross-divisional teams usually results in resource fragmentation and severe brand dilution over time.",
            f"Paragraph 3: Furthermore, digital transformation acts as a primary catalyst for administrative efficiency. Organizations that adopt automation early experience superior data transparency and cost resilience.",
            f"Paragraph 4: During macroeconomic downturns, strategic portfolio diversification serves as a reliable buffer. Liquid asset management ensures continuous solvency during unexpected market slumps.",
            f"Paragraph 5: Ultimately, proactive enterprise leadership consistently outweighs reactive crisis intervention. Executive committees must enforce continuous compliance audits to preserve long-term shareholder confidence."
        ]),
        "reading_questions": reading_questions,
        "listening_script": "\n\n".join([
            f"Audio Briefing (Part 1): Welcome to today's executive briefing on {topic.lower()}. Over the next three minutes, we will analyze key financial metrics, regulatory standards, and operational alignment required for senior executives.",
            f"Audio Briefing (Part 2): Evaluating quarterly health demands paying close attention to cash flow resilience and profit margin stability under volatile conditions.",
            f"Audio Briefing (Part 3): Delayed compliance audits significantly increase exposure to heavy regulatory fines and severe reputational loss across operating jurisdictions.",
            f"Audio Briefing (Part 4): To counteract aggressive competitive disruption, enterprise leaders must cultivate organizational agility and ensure rapid strategy adaptation.",
            f"Audio Briefing (Part 5): Cross-divisional dialogue plays a crucial role in dismantling obsolete operational silos, leading to smoother workflow execution.",
            f"Audio Briefing (Part 6): In conclusion, committing to sustainable practices elevates long-term brand equity and strengthens institutional investor confidence."
        ]),
        "listening_questions": listening_questions,
        "writing_scenario": f"""
        **Executive Writing Scenario:**
        You are the Director of Operations addressing a strategic challenge in **{topic}**. 
        Write a formal memorandum (250–300 words) to the Board of Directors detailing:
        1. Current operational challenges.
        2. Proposed C1 strategic imperatives.
        3. Projected ROI and risk mitigation.
        """,
        "writing_model": f"""
        **MEMORANDUM (C1 Model Answer)**
        
        **TO:** Board of Directors  
        **FROM:** Director of Operations  
        **DATE:** August 18, 2026  
        **SUBJECT:** Comprehensive Strategy for {topic}  

        In light of recent market fluctuations, an immediate realignment regarding {topic.lower()} is mandatory. Operational audits reveal vulnerabilities in cross-border coordination...
        """,
        "speaking_prompt": f"""
        **Executive Presentation Scenario:**
        Deliver a 2-minute oral presentation outlining how your enterprise plans to optimize **{topic}** while managing operational exposure.
        """,
        "translation_questions": translation_questions
    }

# ==========================================
# 4. FIXED RECORDING & SPEECH-TO-TEXT COMPONENT
# ==========================================
def render_audio_recorder(key_prefix: str):
    """HTML5 Recorder + Web Speech API with real-time feedback and quick clipboard copy."""
    html_code = f"""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1.5px solid #000000; margin-bottom: 10px;">
        <p style="font-weight: bold; margin-bottom: 8px; color: #000000;">🎙️ Interactive Audio Recorder & Real-time Speech-To-Text</p>
        <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
            <button id="btn_start_{key_prefix}" onclick="startRecording('{key_prefix}')" style="padding: 8px 14px; background: #000000; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;">🎙️ Record Voice</button>
            <button id="btn_stop_{key_prefix}" onclick="stopRecording('{key_prefix}')" style="padding: 8px 14px; background: #c62828; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;" disabled>⏹️ Stop</button>
            <button id="btn_play_{key_prefix}" onclick="playRecording('{key_prefix}')" style="padding: 8px 14px; background: #ffffff; color: #000000; border: 1px solid #000; border-radius: 6px; cursor: pointer;" disabled>🔊 Play Back</button>
            <button id="btn_copy_{key_prefix}" onclick="copyText('{key_prefix}')" style="padding: 8px 14px; background: #2e7d32; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;">📋 Copy Speech Text</button>
        </div>
        <audio id="audio_player_{key_prefix}" controls style="display: none; width: 100%; margin-top: 8px;"></audio>
        <p style="font-size: 12px; margin-top: 8px; font-weight: bold; color: #000000;">Live Speech Recognition Output:</p>
        <textarea id="transcript_{key_prefix}" rows="3" style="width: 100%; padding: 8px; border: 1px solid #000000; border-radius: 6px; color: #000000; background: #ffffff;" placeholder="Click 'Record Voice' and speak clearly... Text will render here in real time."></textarea>
    </div>

    <script>
        let mediaRecorder_{key_prefix} = null;
        let audioChunks_{key_prefix} = [];
        let recognition_{key_prefix} = null;

        function startRecording(prefix) {{
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
                alert("Microphone access is not supported in this browser environment.");
                return;
            }}

            navigator.mediaDevices.getUserMedia({{ audio: true }}).then(stream => {{
                mediaRecorder_{key_prefix} = new MediaRecorder(stream);
                audioChunks_{key_prefix} = [];

                mediaRecorder_{key_prefix}.ondataavailable = event => {{
                    audioChunks_{key_prefix}.push(event.data);
                }};

                mediaRecorder_{key_prefix}.onstop = () => {{
                    const audioBlob = new Blob(audioChunks_{key_prefix}, {{ type: 'audio/wav' }});
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const player = document.getElementById('audio_player_' + prefix);
                    player.src = audioUrl;
                    player.style.display = 'block';
                    document.getElementById('btn_play_' + prefix).disabled = false;
                }};

                mediaRecorder_{key_prefix}.start();
                document.getElementById('btn_start_' + prefix).disabled = true;
                document.getElementById('btn_stop_' + prefix).disabled = false;

                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition_{key_prefix} = new SpeechRecognition();
                    recognition_{key_prefix}.continuous = true;
                    recognition_{key_prefix}.interimResults = true;
                    recognition_{key_prefix}.lang = 'en-US';

                    let finalTranscript = '';
                    recognition_{key_prefix}.onresult = (event) => {{
                        let interimTranscript = '';
                        for (let i = event.resultIndex; i < event.results.length; ++i) {{
                            if (event.results[i].isFinal) {{
                                finalTranscript += event.results[i][0].transcript + ' ';
                            }} else {{
                                interimTranscript += event.results[i][0].transcript;
                            }}
                        }}
                        const fullText = finalTranscript + interimTranscript;
                        const txtBox = document.getElementById('transcript_' + prefix);
                        txtBox.value = fullText;
                    }};
                    recognition_{key_prefix}.start();
                }}
            }}).catch(err => alert("Error accessing microphone: " + err.message));
        }}

        function stopRecording(prefix) {{
            if (mediaRecorder_{key_prefix} && mediaRecorder_{key_prefix}.state !== 'inactive') {{
                mediaRecorder_{key_prefix}.stop();
            }}
            if (recognition_{key_prefix}) {{
                recognition_{key_prefix}.stop();
            }}
            document.getElementById('btn_start_' + prefix).disabled = false;
            document.getElementById('btn_stop_' + prefix).disabled = true;
        }}

        function playRecording(prefix) {{
            const player = document.getElementById('audio_player_' + prefix);
            player.play();
        }}

        function copyText(prefix) {{
            const txt = document.getElementById('transcript_' + prefix).value;
            if(!txt) {{
                alert("No speech text available to copy yet!");
                return;
            }}
            navigator.clipboard.writeText(txt).then(() => {{
                alert("Copied transcript to clipboard! Paste it into the evaluation box below.");
            }}).catch(() => {{
                alert("Selected and ready. Press Ctrl+C to copy: " + txt);
            }});
        }}
    </script>
    """
    components.html(html_code, height=240)

def render_tts_button(text_to_speak: str, key: str):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    tts_html = f"""
    <button onclick="speakText_{key}()" style="padding: 6px 12px; background: #ffffff; color: #000000; border: 1.5px solid #000000; border-radius: 6px; cursor: pointer; font-weight: 600;">
        🔊 Pronounce Text
    </button>
    <script>
        function speakText_{key}() {{
            if ('speechSynthesis' in window) {{
                const msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }} else {{
                alert('Text-to-speech not supported.');
            }}
        }}
    </script>
    """
    components.html(tts_html, height=45)

# ==========================================
# 5. STATE & PROGRESS PERSISTENCE
# ==========================================
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

if "completed_days" not in st.session_state:
    st.session_state.completed_days = []

# Sidebar Navigation & Selection
with st.sidebar:
    st.title("🎓 C1 Mastery Studio")
    
    st.markdown("**Select Learning Day:**")
    selected_day = st.selectbox(
        "Day Selection",
        options=list(range(1, 31)),
        format_func=lambda d: f"Day {d}: {DAY_TOPICS[d-1]}"
    )
    
    # Progress Calculation
    completed_count = len(st.session_state.completed_days)
    progress_pct = int((completed_count / 30) * 100)
    st.markdown("---")
    st.markdown(f"**Overall Progress:** {completed_count}/30 Days ({progress_pct}%)")
    st.progress(progress_pct / 100)

    st.markdown("### 💾 Data Actions")
    if st.button("💾 Save Day Progress", use_container_width=True):
        st.session_state.user_data[f"day_{selected_day}_saved"] = True
        st.success(f"Progress for Day {selected_day} saved successfully!")

    if st.button("✅ Mark Day Completed", use_container_width=True):
        if selected_day not in st.session_state.completed_days:
            st.session_state.completed_days.append(selected_day)
        st.success(f"Day {selected_day} marked as Completed! 🎉")
        st.rerun()

curriculum = get_day_curriculum(selected_day)

# ==========================================
# 6. DASHBOARD & SKILL TABS
# ==========================================
st.title(f"Day {selected_day}: {curriculum['topic']}")
st.caption(f"Status: {'✅ Completed' if selected_day in st.session_state.completed_days else '⏳ In Progress'}")

tabs = st.tabs([
    "🔤 Vocab & Games",
    "🗣️ Pronunciation",
    "📐 Grammar",
    "📖 Reading",
    "🎧 Listening",
    "✍️ Writing",
    "📊 Speaking",
    "🌐 Translation"
])

# ------------------------------------------
# TAB 1: VOCABULARY & GAMES
# ------------------------------------------
with tabs[0]:
    st.markdown("### 🔤 Target Vocabulary (C1 Level - 10 Words)")
    for idx, v in enumerate(curriculum["vocab"]):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{idx+1}. {v['word']}** \n*Definition:* {v['def']}  \n*Synonym:* **{v['syn']}** \n*Example:* \"*{v['ex']}*\"")
        with col2:
            render_tts_button(v["word"], f"vocab_{idx}")
        st.divider()

    st.markdown("### 🎮 Game 1: Multiple Choice Vocabulary")
    for idx, q in enumerate(curriculum["vocab_mcq"]):
        st.markdown(f"**Question {idx+1}: {q['q']}**")
        user_opt = st.radio("Choose option:", q["options"], key=f"vmcq_{selected_day}_{idx}")
        if st.button(f"Check Answer Q{idx+1}", key=f"btn_vmcq_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

    st.markdown("### 🎮 Game 2: Contextual Fill-in-the-Blank")
    for idx, q in enumerate(curriculum["vocab_fill"]):
        st.markdown(f"**{q['q']}**")
        user_text = st.text_input("Your answer:", key=f"vfill_{selected_day}_{idx}")
        if st.button(f"Check Fill Q{idx+1}", key=f"btn_vfill_{idx}"):
            if user_text.strip().lower() == q["answer"].lower():
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_text}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: PRONUNCIATION
# ------------------------------------------
with tabs[1]:
    st.markdown("### 🗣️ Pronunciation & Intonation Practice")
    for idx, excerpt in enumerate(curriculum["pronunciation"]):
        st.markdown(f"**Excerpt {idx+1}:** *\"{excerpt}\"*")
        render_tts_button(excerpt, f"pron_target_{idx}")
        render_audio_recorder(f"pron_{selected_day}_{idx}")
        
        spoken_input = st.text_area(f"Transcribed Text for AI Evaluation (Excerpt {idx+1}):", key=f"pron_txt_{selected_day}_{idx}", placeholder="Paste copied speech text here or leave blank to evaluate against target sentence...")
        if st.button(f"🤖 Analyze Stress & Intonation (Excerpt {idx+1})", key=f"btn_pron_ai_{idx}"):
            eval_text = spoken_input.strip() if spoken_input.strip() else f"Direct voice evaluation against target: '{excerpt}'"
            with st.spinner("Analyzing pronunciation via Groq AI..."):
                prompt = f"Target Excerpt: '{excerpt}'\nUser Speech Record: '{eval_text}'\nEvaluate C1 pronunciation, stress patterns, pitch control, and intonation. Score out of 10 with clear, practical feedback."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Pronunciation Feedback:</b><br>{feedback}</div>", unsafe_allow_html=True)
        st.divider()

# ------------------------------------------
# TAB 3: GRAMMAR RULES
# ------------------------------------------
with tabs[2]:
    st.markdown(curriculum["grammar_theory"])
    st.markdown("### 📝 Grammar Exercises (10 Questions)")
    
    for idx, q in enumerate(curriculum["grammar_questions"]):
        st.markdown(f"**{q['q']}**")
        user_opt = st.radio("Choose option:", q["options"], key=f"gram_q_{selected_day}_{idx}")
        if st.button(f"Check Grammar Q{idx+1}", key=f"btn_gram_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: READING
# ------------------------------------------
with tabs[3]:
    st.markdown("### 📖 Business Reading Passage (20+ Lines)")
    st.text_area("Reading Passage:", curriculum["reading_passage"], height=220, disabled=True)
    
    st.markdown("### ❓ Reading Comprehension (7 Questions)")
    for idx, q in enumerate(curriculum["reading_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Choose answer:", q["options"], key=f"read_q_{selected_day}_{idx}")
        if st.button(f"Check Reading Q{idx+1}", key=f"btn_read_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: LISTENING BRIEFING
# ------------------------------------------
with tabs[4]:
    st.markdown("### 🎧 Audio Script & Executive Briefing")
    render_tts_button(curriculum["listening_script"], f"listening_{selected_day}")
    st.text_area("Audio Transcript:", curriculum["listening_script"], height=200, disabled=True)
    
    st.markdown("### ❓ Listening Comprehension (7 Questions)")
    for idx, q in enumerate(curriculum["listening_questions"]):
        st.markdown(f"**Q{idx+1}: {q['q']}**")
        user_opt = st.radio("Choose answer:", q["options"], key=f"list_q_{selected_day}_{idx}")
        if st.button(f"Check Listening Q{idx+1}", key=f"btn_list_{idx}"):
            if user_opt == q["answer"]:
                st.markdown(f"<div class='feedback-correct'>✅ Correct! Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-incorrect'>❌ Incorrect. Your answer: <b>{user_opt}</b> | Correct Answer: <b>{q['answer']}</b><br><i>Explanation: {q['explanation']}</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 6: WRITING SCENARIO
# ------------------------------------------
with tabs[5]:
    st.markdown("### ✍️ Detailed C1 Business Writing Scenario")
    st.markdown(curriculum["writing_scenario"])
    
    user_writing = st.text_area("Draft your essay response here:", height=220, key=f"writing_{selected_day}")
    
    if st.button("🤖 Grade C1 Essay via Groq AI"):
        if not user_writing.strip():
            st.warning("Please enter your written response first!")
        else:
            with st.spinner("Grading essay via Groq AI..."):
                prompt = f"Writing Task: {curriculum['writing_scenario']}\n\nUser Essay Submission: '{user_writing}'\n\nGrade for C1 Business English. Provide: (1) Lexical Resource Score, (2) Grammatical Accuracy, (3) Formal Format Suggestions, and (4) Overall Score /100."
                feedback = query_groq_ai(prompt)
                st.markdown(f"<div class='feedback-correct'><b>AI Writing Feedback & Score:</b><br>{feedback}</div>", unsafe_allow_html=True)

    with st.expander("💡 View C1 Model Answer"):
        st.markdown(curriculum["writing_model"])

# ------------------------------------------
# TAB 7: SPEAKING PRESENTATION
# ------------------------------------------
with tabs[6]:
    st.markdown("### 📊 Executive Speaking Presentation")
    st.markdown(curriculum["speaking_prompt"])
    
    render_audio_recorder(f"speaking_pres_{selected_day}")
    spoken_presentation = st.text_area("Presentation Transcript for AI Evaluation:", key=f"speaking_txt_{selected_day}", placeholder="Paste copied speech transcript here or leave blank to evaluate speech content directly...")
    
    if st.button("🤖 Grade Executive Presentation via Groq AI"):
        eval_spk = spoken_presentation.strip() if spoken_presentation.strip() else f"User delivered spoken presentation for topic: {curriculum['topic']}"
        with st.spinner("Evaluating presentation via Groq AI..."):
            prompt = f"Speaking Prompt: {curriculum['speaking_prompt']}\n\nSpeech Content: '{eval_spk}'\n\nGrade for executive level fluency, lexical sophistication, dynamic tone, and structural coherence. Score out of 100 with actionable feedback."
            feedback = query_groq_ai(prompt)
            st.markdown(f"<div class='feedback-correct'><b>AI Presentation Feedback:</b><br>{feedback}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 8: TRANSLATION PRACTICE
# ------------------------------------------
with tabs[7]:
    st.markdown("### 🌐 Vietnamese to C1 English Translation (10 Sentences)")
    
    user_translations = []
    for idx, q in enumerate(curriculum["translation_questions"]):
        st.markdown(f"**Sentence {idx+1}:** {q['vi']}")
        user_trans = st.text_input(f"Your C1 Translation S{idx+1}:", key=f"trans_{selected_day}_{idx}")
        user_translations.append((q['vi'], user_trans, q['suggested']))
    
    if st.button("🤖 Grade All 10 Translations via Groq AI"):
        with st.spinner("Grading translations via Groq AI..."):
            prompt = "Grade these Vietnamese to English translations for C1 Business level:\n\n"
            for i, (vi, user, sug) in enumerate(user_translations):
                prompt += f"Sentence {i+1} (VI): {vi}\nUser Answer: '{user}'\nSuggested: '{sug}'\n\n"
            prompt += "Evaluate each sentence based on Vocabulary, Grammar, and Structure, providing clear explanations."
            feedback = query_groq_ai(prompt)
            st.markdown(f"<div class='feedback-correct'><b>AI Translation Assessment:</b><br>{feedback}</div>", unsafe_allow_html=True)