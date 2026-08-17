import json
import os
import random
import tempfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN STYLE GOOGLE AI STUDIO (FORCED BLACK TEXT)
# ==========================================
st.set_page_config(
    page_title="IELTS & Business English Studio B2->C1",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injection CSS: Ép toàn bộ ứng dụng sang chữ màu đen đậm #1A202C tuyệt đối
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Ép nền ứng dụng hồng nhạt */
    .stApp, [data-testid="stAppViewContainer"] { 
        background-color: #FFF5F5 !important; 
    }
    
    /* Ép tất cả văn bản trong ứng dụng thành màu ĐEN DẬM #1A202C */
    html, body, p, span, div, h1, h2, h3, h4, h5, h6, li, a, label, strong, b, em, i,
    [class*="css"], .stMarkdown, .stText, .stRadio label, .stCheckbox label,
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #1A202C !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Thẻ Container Google Studio Style (Nền Trắng, Chữ Đen) */
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

    /* Đổi màu chữ ô Input, Textarea & Selectbox thành Chữ Đen - Nền Trắng */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }
    
    /* Đổi màu Radio Buttons & Labels */
    div[class*="stRadio"] label p {
        color: #1A202C !important;
        font-weight: 500 !important;
    }

    /* Style cho Tabs */
    button[data-baseweb="tab"] p {
        color: #2D3748 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] p {
        color: #E53E3E !important;
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

    /* Nút bấm đỏ nổi bật */
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
# 2. BỘ PHÁT ÂM TTS (WEB SPEECH API)
# ==========================================
def render_tts_button(text, button_id):
    """Tạo nút loa phát âm trực tiếp bằng JS Web Speech API."""
    js_code = f"""
    <button onclick="playTTS('{text}')" id="btn_{button_id}" style="
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
        🔊 Nghe phát âm
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
# 3. LƯU TIẾN ĐỘ & GROQ API
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
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Lỗi lưu trữ: {e}")

saved_data = load_saved_data()
if "completed_days" not in st.session_state:
    st.session_state.completed_days = set(saved_data.get("completed_days", []))
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = saved_data.get("api_key", "")

def call_groq_llm(prompt, api_key):
    if not api_key:
        st.error("Vui lòng nhập Groq API Key ở Sidebar!")
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    active_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    
    for model in active_models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a C1 Business English & IELTS Senior Examiner. Provide exact, structured evaluations in Vietnamese."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            continue
    st.error("Kết nối Groq API thất bại. Kiểm tra Key hoặc mạng!")
    return None

def transcribe_audio_groq(audio_bytes, api_key):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
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
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return None


# ==========================================
# 4. HÀM THU ÂM VÀ CHẤM ĐIỂM GIỌNG NÓI
# ==========================================
def record_and_evaluate_speech(reference_text, label):
    st.markdown(f"**Văn bản luyện đọc:** *\"{reference_text}\"*")
    render_tts_button(reference_text, f"tts_{hash(label+reference_text)}")
    
    audio_val = st.audio_input("Nhấn nút micro để ghi âm giọng đọc:", key=f"rec_{hash(label+reference_text)}")
    if audio_val:
        audio_bytes = audio_val.read()
        st.audio(audio_bytes, format="audio/wav")
        if st.button("🎯 Phân tích Ngữ điệu & Trọng âm AI", key=f"btn_{hash(label+reference_text)}"):
            with st.spinner("AI đang chấm điểm giọng nói..."):
                transcribed = transcribe_audio_groq(audio_bytes, st.session_state.groq_api_key)
                if transcribed:
                    st.info(f"📝 **AI nghe được:** \"{transcribed}\"")
                    prompt = f"""
                    Đánh giá phát âm C1/IELTS Speaking:
                    - Văn bản gốc: "{reference_text}"
                    - Học viên nói: "{transcribed}"
                    Chấm điểm theo tiêu chí bằng tiếng Việt:
                    1. Điểm tổng quan (/10)
                    2. Trọng âm từ & Trọng âm câu (Sentence Stress)
                    3. Ngữ điệu (Rising/Falling Intonation)
                    4. Lỗi phát âm chi tiết & Cách khắc phục.
                    """
                    feedback = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if feedback:
                        st.markdown(f"<div class='studio-card'>{feedback}</div>", unsafe_allow_html=True)


# ==========================================
# 5. DỮ LIỆU BÀI HỌC B2 -> C1 (30 NGÀY MASTERY)
# ==========================================
def get_curriculum_day(day_num):
    topics = [
        "Executive Corporate Strategy", "Cross-Border Negotiations", "Financial Risk Mitigation",
        "Change Management & Agility", "Brand Reputation & Crisis", "Digital Transformation",
        "Supply Chain Optimization", "M&A Realignment", "ESG & Corporate Governance", "AI & Business Automation"
    ]
    topic = topics[(day_num - 1) % len(topics)]
    
    vocab = [
        {"word": "Consolidate", "pos": "verb", "en": "To combine into a single, stronger unit.", "vn": "Củng cố / Sáp nhập", "syn": "Merge, Strengthen", "example": "The company plans to consolidate its position in the European market."},
        {"word": "Feasibility", "pos": "noun", "en": "The degree to which something is possible.", "vn": "Tính khả thi", "syn": "Viability, Practicability", "example": "We conducted a feasibility study before launching the project."},
        {"word": "Disruption", "pos": "noun", "en": "Disturbance that alters a system.", "vn": "Sự đứt gãy / Đột phá", "syn": "Upheaval, Disturbance", "example": "AI technology is causing massive disruption in traditional industries."},
        {"word": "Benchmark", "pos": "noun", "en": "A standard against which things may be measured.", "vn": "Tiêu chuẩn đánh giá", "syn": "Criterion, Yardstick", "example": "Our Q3 performance set a new benchmark for the sector."},
        {"word": "Mitigate", "pos": "verb", "en": "Make less severe, serious, or painful.", "vn": "Giảm thiểu rủi ro", "syn": "Alleviate, Reduce", "example": "Steps were taken to mitigate the financial impact of the crisis."},
        {"word": "Leverage", "pos": "verb", "en": "Use something to maximum advantage.", "vn": "Tận dụng tối đa", "syn": "Exploit, Utilize", "example": "We must leverage our brand equity to launch new products."},
        {"word": "Scalability", "pos": "noun", "en": "Ability of a system to handle growing work.", "vn": "Khả năng mở rộng", "syn": "Expandability", "example": "Cloud architecture offers incredible business scalability."},
        {"word": "Pivot", "pos": "verb", "en": "Change strategic direction abruptly.", "vn": "Chuyển hướng chiến lược", "syn": "Shift, Reorient", "example": "The startup pivoted from B2C to an enterprise B2B model."},
        {"word": "Stagnation", "pos": "noun", "en": "State of not flowing, moving, or changing.", "vn": "Sự đình trệ / Trì trệ", "syn": "Inaction, Standstill", "example": "Economic stagnation led to reduced corporate investment."},
        {"word": "Unprecedented", "pos": "adj", "en": "Never done or known before.", "vn": "Chưa từng có tiền lệ", "syn": "Unparalleled, Novel", "example": "The sector experienced unprecedented growth during the quarter."}
    ]

    return {
        "title": f"Day {day_num}: {topic} (B2 → C1 Level)",
        "topic": topic,
        "vocab": vocab,
        "pronunciation": [
            f"Our strategic initiatives have significantly consolidated market position over the fiscal year.",
            f"To mitigate operational risks, executive leadership approved an unprecedented risk governance framework.",
            f"Leveraging digital scalability remains the primary benchmark for corporate growth in this quarter."
        ],
        "grammar": {
            "title": "Inversion in Advanced Business Conditionals (C1 Grammar)",
            "theory": """
            **Cấu trúc Đảo ngữ Điều kiện C1 trong Báo cáo & Đàm phán:**
            * *Type 1 (Should):* **Should you require further clarification,** please contact our legal counsel. (Thay cho *If you require...*)
            * *Type 2 (Were):* **Were the market to collapse,** our contingency plan would take effect. (Thay cho *If the market were to...*)
            * *Type 3 (Had):* **Had the board approved the merger,** our revenue would have doubled. (Thay cho *If the board had approved...*)
            """,
            "mcq": [
                {"q": "_____ the executive committee mandate the budget, we will proceed immediately.", "options": ["Had", "Should", "Were", "Unless"], "a": "Should"},
                {"q": "_____ the company mitigated risks earlier, the losses would have been avoided.", "options": ["Were", "Had", "Should", "If only"], "a": "Had"}
            ],
            "fitb": [
                {"q": "_____ (Were) the firm to pivot now, stakeholders might object.", "a": "Were"},
                {"q": "Should you _____ (need) additional leverage, review the clause.", "a": "need"}
            ]
        },
        "reading": {
            "title": f"Executive Summary: Navigating {topic}",
            "text": f"In an era of market volatility, corporations must move beyond mere compliance to achieve sustainable growth. Adopting robust feasibility frameworks ensures that resource allocation aligns with core objectives. Failure to mitigate systemic vulnerabilities often leads to unprecedented stagnation across operational units.",
            "mcq": [
                {"q": "What is essential for sustainable growth according to the passage?", "options": ["Simple compliance", "Robust feasibility frameworks", "Reducing resources", "Ignoring volatility"], "a": "Robust feasibility frameworks"},
                {"q": "Systemic vulnerabilities lead directly to:", "options": ["Scalability", "Stagnation", "Immediate profit", "Rebranding"], "a": "Stagnation"}
            ],
            "fitb": [
                {"q": "Companies must move beyond mere _____ to achieve long-term growth.", "a": "compliance"},
                {"q": "Unprecedented _____ occurs when vulnerabilities are left unmitigated.", "a": "stagnation"}
            ]
        },
        "listening": {
            "script": f"Welcome shareholders. Today's quarterly briefing focuses on {topic}. Despite macro economic headwinds, our strategic pivot enabled us to consolidate existing markets while achieving unprecedented scalability in logistics.",
            "mcq": [
                {"q": "What enabled the market consolidation according to the speaker?", "options": ["Macro headwinds", "Strategic pivot", "Budget cuts", "Staff reduction"], "a": "Strategic pivot"}
            ],
            "fitb": [
                {"q": "The company achieved unprecedented _____ in logistics.", "a": "scalability"}
            ]
        },
        "writing": f"Write an executive memo (150-200 words) proposing a strategic shift to mitigate risks in '{topic}'. Incorporate at least 3 C1 vocabulary words from today's lesson.",
        "speaking": f"Deliver a 2-minute pitch to board members convincing them why your department needs to pivot strategy regarding '{topic}'.",
        "translation": [
            {"vn": "1. Chúng tôi cần củng cố vị thế thị trường trước khi mở rộng quy mô.", "en": "We need to consolidate our market position before scaling up."},
            {"vn": "2. Nghiên cứu tính khả thi đã chỉ ra những rủi ro tài chính tiềm ẩn.", "en": "The feasibility study highlighted potential financial risks."},
            {"vn": "3. Doanh nghiệp phải tận dụng công nghệ AI để tối ưu hóa quy trình.", "en": "The business must leverage AI technology to optimize workflows."},
            {"vn": "4. Sự đứt gãy chuỗi cung ứng đã gây ra thiệt hại chưa từng có.", "en": "The supply chain disruption caused unprecedented damages."},
            {"vn": "5. Tiêu chuẩn đánh giá này giúp kiểm soát chất lượng dự án.", "en": "This benchmark helps control project quality."},
            {"vn": "6. Nhóm nghiên cứu đã đề xuất giải pháp giảm thiểu rủi ro vận hành.", "en": "The research team proposed solutions to mitigate operational risks."},
            {"vn": "7. Khả năng mở rộng của nền tảng này là ưu điểm cạnh tranh lớn.", "en": "The scalability of this platform is a major competitive advantage."},
            {"vn": "8. Công ty đã chuyển hướng chiến lược sang mô hình kinh doanh B2B.", "en": "The company pivoted its strategy to a B2B business model."},
            {"vn": "9. Sự trì trệ kinh tế ảnh hưởng trực tiếp đến doanh thu quý 3.", "en": "Economic stagnation directly impacted Q3 revenue."},
            {"vn": "10. Nếu ban giám đốc chấp thuận, chúng tôi sẽ triển khai kế hoạch ngay.", "en": "Should the board approve, we will implement the plan immediately."}
        ]
    }


# ==========================================
# 6. GIAO DIỆN CHÍNH & 8 TABS KỸ NĂNG
# ==========================================
def main():
    st.sidebar.title("⚡ AI English Studio")
    st.sidebar.caption("Lộ trình B2 → C1 Mastery (30 Ngày)")

    api_key_in = st.sidebar.text_input("🔑 Groq API Key:", value=st.session_state.groq_api_key, type="password")
    if api_key_in != st.session_state.groq_api_key:
        st.session_state.groq_api_key = api_key_in
        save_data_to_file()

    st.sidebar.divider()
    
    comp_len = len(st.session_state.completed_days)
    st.sidebar.write(f"**Tiến độ khóa học:** {comp_len}/30 Ngày ({int(comp_len/30*100)}%)")
    st.sidebar.progress(comp_len / 30.0)

    selected_day = st.sidebar.selectbox(
        "📅 Chọn bài học ngày:",
        options=list(range(1, 31)),
        format_func=lambda x: f"Day {x}: {get_curriculum_day(x)['title']}"
    )

    day_data = get_curriculum_day(selected_day)

    # Header Studio
    st.markdown(
        f"""
        <div class="studio-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="badge-c1">C1 LEVEL MASTERY</span>
                    <h2 style="margin-top: 8px; margin-bottom: 4px;">{day_data['title']}</h2>
                    <p style="color: #4A5568 !important; margin: 0;">Chủ đề trọng tâm: <b>{day_data['topic']}</b></p>
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
    # TAB 1: VOCABULARY & GAMES
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
                        <p style="margin-top:8px;"><b>Nghĩa EN:</b> {v['en']}</p>
                        <p><b>Nghĩa VN:</b> {v['vn']}</p>
                        <p><b>Từ đồng nghĩa:</b> <code>{v['syn']}</code></p>
                        <p><b>Ví dụ:</b> <i>"{v['example']}"</i></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                render_tts_button(v['word'], f"vocab_{selected_day}_{idx}")

        st.divider()
        st.subheader("🎮 Vocabulary Games Practice")

        # Game 1: Multiple Choice
        st.markdown("### 🕹️ Game 1: C1 Word Definition Quiz (5 Câu hỏi)")
        score_g1 = 0
        for i in range(5):
            w = day_data["vocab"][i]
            st.markdown(f"**Câu {i+1}:** Nghĩa đúng của từ **\"{w['word']}\"** là gì?")
            opts = [w['vn'], day_data["vocab"][(i+1)%10]['vn'], day_data["vocab"][(i+2)%10]['vn'], day_data["vocab"][(i+3)%10]['vn']]
            random.seed(i + selected_day)
            random.shuffle(opts)
            ans = st.radio(f"Chọn đáp án cho câu {i+1}:", opts, key=f"g1_q_{selected_day}_{i}")
            if ans == w['vn']:
                score_g1 += 1
        if st.button("Kiểm tra điểm Game 1"):
            st.success(f"🎉 Điểm Game 1 của bạn: {score_g1}/5")

        st.divider()

        # Game 2: Fill-in-the-blank
        st.markdown("### 🧩 Game 2: Context Sentence Fill-in-the-blank (5 Câu hỏi)")
        score_g2 = 0
        for i in range(5, 10):
            w = day_data["vocab"][i]
            sentence = w["example"].replace(w["word"], "________").replace(w["word"].lower(), "________")
            st.markdown(f"**Câu {i-4}:** Điền từ thích hợp: *\"{sentence}\"*")
            u_ans = st.text_input(f"Nhập từ câu {i-4}:", key=f"g2_q_{selected_day}_{i}")
            if u_ans.strip().lower() == w["word"].lower():
                score_g2 += 1
        if st.button("Kiểm tra điểm Game 2"):
            st.success(f"🎉 Điểm Game 2 của bạn: {score_g2}/5")

    # ------------------------------------------
    # TAB 2: PRONUNCIATION
    # ------------------------------------------
    with t2:
        st.subheader("🗣️ C1 Pronunciation & Intonation Drills")
        st.caption("Luyện tập 3 đoạn/câu đọc nâng cao theo chủ đề bài học. Thu âm để AI chấm trọng âm và ngữ điệu:")
        for idx, p in enumerate(day_data["pronunciation"]):
            st.markdown(f"<div class='studio-card'><h4>Đoạn {idx+1}</h4></div>", unsafe_allow_html=True)
            record_and_evaluate_speech(p, label=f"pron_tab_{selected_day}_{idx}")

    # ------------------------------------------
    # TAB 3: GRAMMAR RULES
    # ------------------------------------------
    with t3:
        st.subheader(f"📐 {day_data['grammar']['title']}")
        st.markdown(f"<div class='studio-card'>{day_data['grammar']['theory']}</div>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Kiểm tra Ngữ pháp")
        st.markdown("#### Phần 1: Trắc nghiệm Multiple Choice")
        for idx, q in enumerate(day_data["grammar"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            u_ans = st.radio(f"Đáp án Q{idx+1}:", q['options'], key=f"g_mcq_{selected_day}_{idx}")
            if u_ans == q['a']:
                st.caption("✅ Đúng!")

        st.markdown("#### Phần 2: Điền từ vào chỗ trống Fill-in-the-blank")
        for idx, q in enumerate(day_data["grammar"]["fitb"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            u_ans = st.text_input(f"Nhập từ Q{idx+1}:", key=f"g_fitb_{selected_day}_{idx}")
            if u_ans.strip().lower() == q['a'].lower():
                st.caption("✅ Chính xác!")

    # ------------------------------------------
    # TAB 4: READING
    # ------------------------------------------
    with t4:
        st.subheader(f"📖 {day_data['reading']['title']}")
        st.markdown(f"<div class='studio-card'><p style='font-size:16px; line-height:1.6;'>{day_data['reading']['text']}</p></div>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Bài tập Đọc hiểu")
        st.markdown("#### Multiple Choice Questions")
        for idx, q in enumerate(day_data["reading"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            st.radio(f"Lựa chọn Q{idx+1}:", q['options'], key=f"r_mcq_{selected_day}_{idx}")

        st.markdown("#### Fill in the blank")
        for idx, q in enumerate(day_data["reading"]["fitb"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            st.text_input(f"Nhập từ trả lời Q{idx+1}:", key=f"r_fitb_{selected_day}_{idx}")

    # ------------------------------------------
    # TAB 5: LISTENING
    # ------------------------------------------
    with t5:
        st.subheader("🎧 Business Audio Briefing Script")
        st.markdown(f"<div class='studio-card'><p style='font-size:16px; line-height:1.6;'><i>\"{day_data['listening']['script']}\"</i></p></div>", unsafe_allow_html=True)
        render_tts_button(day_data['listening']['script'], f"listen_script_{selected_day}")
        
        st.markdown("### 📝 Bài tập Nghe hiểu")
        for idx, q in enumerate(day_data["listening"]["mcq"]):
            st.write(f"**Q{idx+1}:** {q['q']}")
            st.radio(f"Đáp án Nghe Q{idx+1}:", q['options'], key=f"l_mcq_{selected_day}_{idx}")

        for idx, q in enumerate(day_data["listening"]["fitb"]):
            st.write(f"**Fill-in Q{idx+1}:** {q['q']}")
            st.text_input(f"Nhập câu trả lời Nghe Q{idx+1}:", key=f"l_fitb_{selected_day}_{idx}")

    # ------------------------------------------
    # TAB 6: WRITING
    # ------------------------------------------
    with t6:
        st.subheader("✍️ C1 Executive Writing Scenario")
        st.markdown(f"<div class='studio-card'><b>Nhiệm vụ:</b> {day_data['writing']}</div>", unsafe_allow_html=True)
        
        user_writer = st.text_area("Nhập bài viết Tiếng Anh của bạn tại đây:", height=200)
        if st.button("🚀 AI Chấm điểm & Nâng cấp bài viết C1"):
            if not user_writer.strip():
                st.warning("Vui lòng nhập bài viết trước khi chấm!")
            else:
                with st.spinner("AI Chuyên gia C1 đang thẩm định..."):
                    prompt = f"""
                    Chấm bài viết Business English C1:
                    Đề bài: "{day_data['writing']}"
                    Bài viết học viên: "{user_writer}"

                    Yêu cầu đánh giá bằng Tiếng Việt:
                    1. Điểm Task Achievement, Grammar & C1 Vocabulary (/10).
                    2. Lỗi ngữ pháp & Từ vựng chưa chuẩn C1.
                    3. Bản viết lại đẳng cấp C1 Executive (Advanced Rewritten Version).
                    """
                    res = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if res:
                        st.markdown(f"<div class='studio-card'>{res}</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 7: SPEAKING
    # ------------------------------------------
    with t7:
        st.subheader("📊 Executive Speaking Pitch")
        st.markdown(f"<div class='studio-card'><b>Chủ đề Thuyết trình:</b> {day_data['speaking']}</div>", unsafe_allow_html=True)
        record_and_evaluate_speech(day_data['speaking'], label=f"speak_pitch_{selected_day}")

    # ------------------------------------------
    # TAB 8: TRANSLATION
    # ------------------------------------------
    with t8:
        st.subheader("🌐 C1 Translation Practice (10 Câu Tiếng Việt → Tiếng Anh)")
        st.caption("Dịch 10 câu theo chủ đề sang Tiếng Anh. AI sẽ chấm điểm dựa trên Từ vựng C1, Ngữ pháp và Cấu trúc câu:")
        
        user_trans_answers = []
        for idx, t_item in enumerate(day_data["translation"]):
            st.markdown(f"**Câu {idx+1}:** {t_item['vn']}")
            ans_input = st.text_input(f"Bản dịch câu {idx+1}:", key=f"trans_{selected_day}_{idx}")
            user_trans_answers.append({"vn": t_item['vn'], "user_en": ans_input, "ref_en": t_item['en']})

        if st.button("🎯 AI Chấm Điểm Bài Dịch 10 Câu"):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key!")
            else:
                with st.spinner("AI đang chấm chi tiết 10 câu dịch..."):
                    prompt_trans = f"""
                    Chấm bài dịch 10 câu Tiếng Việt -> Tiếng Anh (Level C1 Business English):
                    Dữ liệu bài làm:
                    {json.dumps(user_trans_answers, ensure_ascii=False, indent=2)}

                    Hãy đánh giá chi tiết bằng Tiếng Việt:
                    1. Tổng điểm bài dịch (/10).
                    2. Nhận xét từng câu (Câu đúng/Chưa chuẩn, Điểm mạnh từ vựng C1).
                    3. Bảng tổng hợp Gợi ý bản dịch chuẩn C1 chuyên nghiệp nhất.
                    """
                    res_trans = call_groq_llm(prompt_trans, st.session_state.groq_api_key)
                    if res_trans:
                        st.markdown(f"<div class='studio-card'>{res_trans}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()