import json
import os
import tempfile
import requests
import streamlit as st

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & ÉP MÀU CHỮ ĐEN
# ==========================================
st.set_page_config(
    page_title="IELTS Speaking & Business English 30D",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Nền ứng dụng chính */
    .main { 
        background-color: #FFF5F5 !important; 
    }
    
    /* Khung thẻ thông tin: Nền trắng, Chữ đen bắt buộc */
    .card-box {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
        border: 1px solid #FEB2B2;
        margin-bottom: 20px;
    }
    
    /* Khóa tất cả font chữ bên trong card-box thành màu đen đậm */
    .card-box *, .card-box h1, .card-box h2, .card-box h3, .card-box h4, 
    .card-box p, .card-box span, .card-box div, .card-box b, .card-box i {
        color: #1A202C !important;
    }

    /* Nút bấm */
    .stButton>button {
        background-color: #E53E3E !important; 
        color: #FFFFFF !important;
        border-radius: 8px; 
        border: none;
        padding: 8px 16px; 
        font-weight: bold; 
        width: 100%;
    }
    .stButton>button:hover { 
        background-color: #C53030 !important; 
        color: #FFFFFF !important; 
    }

    /* Badge trạng thái */
    .badge-pink {
        background-color: #FED7D7 !important; 
        color: #9B2C2C !important;
        padding: 4px 12px; 
        border-radius: 16px; 
        font-weight: bold;
    }
    .badge-green {
        background-color: #C6F6D5 !important; 
        color: #22543D !important;
        padding: 4px 12px; 
        border-radius: 16px; 
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. LƯU TRỮ TIẾN ĐỘ HỌC TỰ ĐỘNG
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
        "user_notes": st.session_state.get("user_notes", {}),
        "api_key": st.session_state.get("groq_api_key", ""),
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")


saved_data = load_saved_data()
if "completed_days" not in st.session_state:
    st.session_state.completed_days = set(saved_data.get("completed_days", []))
if "user_notes" not in st.session_state:
    st.session_state.user_notes = saved_data.get("user_notes", {})
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = saved_data.get("api_key", "")


# ==========================================
# 3. XỬ LÝ GROQ API (KHẮC PHỦC LỖI MODEL 400)
# ==========================================
def call_groq_llm(prompt, api_key, system_instruction=None):
    """Tự động chuyển đổi giữa các Model ACTIVE mới nhất của Groq để sửa lỗi 400."""
    if not api_key:
        st.error("Vui lòng nhập Groq API Key ở Sidebar bên trái!")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Danh sách Model ACTIVE chuẩn nhất của Groq
    active_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]

    if not system_instruction:
        system_instruction = "You are an expert Business English coach and IELTS examiner. Provide clear, well-structured Vietnamese analysis."

    last_error = ""
    for model in active_models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                last_error = f"Model {model} - HTTP {res.status_code}: {res.text}"
        except Exception as e:
            last_error = str(e)

    st.error(f"Groq API Error: {last_error}")
    return None


def transcribe_audio_groq(audio_bytes, api_key):
    """Chuyển âm thanh thu âm thành văn bản qua Whisper Large V3."""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:
        with open(tmp_path, "rb") as f:
            files = {
                "file": ("recording.wav", f, "audio/wav"),
                "model": (None, "whisper-large-v3"),
                "response_format": (None, "json"),
                "language": (None, "en"),
            }
            res = requests.post(url, headers=headers, files=files, timeout=40)

        if res.status_code == 200:
            return res.json().get("text", "")
        else:
            st.error(f"Lỗi Whisper Transcription ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        st.error(f"Lỗi xử lý file âm thanh: {e}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==========================================
# 4. MODULE PRONUNCIATION & INTONATION
# ==========================================
def record_and_evaluate_speech(reference_text, context_label="Pronunciation"):
    st.subheader(f"🎙️ Ghi Âm & Chấm Điểm Giọng Nói ({context_label})")

    # Native Streamlit Audio Input Widget
    audio_value = st.audio_input(
        "Nhấn nút Micro bên dưới để ghi âm bài đọc:",
        key=f"rec_{context_label}_{hash(reference_text)}",
    )

    if audio_value is not None:
        audio_bytes = audio_value.read()

        # Phát lại audio trực tiếp
        st.markdown("#### 🔊 Nghe lại bản ghi âm của bạn:")
        st.audio(audio_bytes, format="audio/wav")

        if st.button(
            "🎯 Phân Tích & Chấm Điểm Ngữ Điệu / Phát Âm",
            key=f"btn_eval_{context_label}_{hash(reference_text)}",
        ):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key ở Sidebar!")
            else:
                with st.spinner(
                    "Đang nhận diện giọng nói (Whisper Large V3)..."
                ):
                    transcription = transcribe_audio_groq(
                        audio_bytes, st.session_state.groq_api_key
                    )

                if transcription:
                    st.info(f'📝 **Văn bản nhận diện được:** "{transcription}"')
                    with st.spinner(
                        "AI đang phân tích ngữ điệu, trọng âm và độ trôi chảy..."
                    ):
                        eval_prompt = f"""
                        Phân tích bài phát âm và ngữ điệu câu tiếng Anh của học viên:
                        - Câu gốc chuẩn (Reference): "{reference_text}"
                        - Giọng đọc thực tế (Transcription): "{transcription}"

                        Trình bày đánh giá bằng Tiếng Việt đầy đủ các mục:
                        ### 1. 🎯 Điểm Tổng Quan (Thang điểm 10)
                        Đánh giá độ trôi chảy (Fluency) và mức độ chính xác so với câu gốc.

                        ### 2. 🔤 Phát Âm & Âm Cuối (Phonetics & Ending Sounds)
                        - Chỉ ra từ đọc chuẩn, từ đọc sai hoặc bị nuốt âm.
                        - Kiểm tra kỹ các âm cuối (Ending sounds) như /s/, /z/, /t/, /d/, /ed/.

                        ### 3. 🎵 Trọng Âm & Ngữ Điệu (Sentence Stress & Pitch Contour)
                        - **Trọng âm câu**: Học viên đã nhấn đúng vào các từ mang thông tin chính (Nouns, Verbs, Adjectives) chưa?
                        - **Ngữ điệu (Intonation)**: Hướng dẫn chi tiết đoạn cần Lên giọng (Rising pitch) và Xuống giọng (Falling pitch).
                        - **Nhịp điệu & Ngắt nghỉ (Rhythm & Pausing)**: Độ tự nhiên của nhịp nói.

                        ### 4. 💡 Hướng Dẫn Khắc Phục Triệt Để
                        2-3 bước ngắn gọn để sửa phát âm và nói nhấn nhá tự nhiên hơn.
                        """
                        feedback = call_groq_llm(
                            eval_prompt, st.session_state.groq_api_key
                        )
                        if feedback:
                            st.markdown("### 📊 Kết Quả Đánh Giá Chi Tiết")
                            st.markdown(
                                f"<div class='card-box'>{feedback}</div>",
                                unsafe_allow_html=True,
                            )


# ==========================================
# 5. DỮ LIỆU CURRICULUM BÀI HỌC
# ==========================================
CURRICULUM = {
    1: {
        "title": "Day 1: Corporate Strategy & Vision",
        "grammar_concept": "Present Perfect vs. Past Simple in Performance Reporting",
        "vocab": [
            {
                "word": "Synergy",
                "pos": "noun",
                "meaning": "Sự cộng hưởng",
                "example": "Cross-departmental synergy boosted overall efficiency.",
            },
            {
                "word": "Benchmark",
                "pos": "noun",
                "meaning": "Tiêu chuẩn đánh giá",
                "example": "We set new industry benchmarks this quarter.",
            },
            {
                "word": "Streamline",
                "pos": "verb",
                "meaning": "Tối ưu hóa quy trình",
                "example": "The team streamlined operations to cut costs.",
            },
        ],
        "pronunciation": {
            "focus": "Linking Words & Intonation in Executive Summaries",
            "target_sentence": "Our strategic initiatives have significantly increased revenue over the past fiscal year.",
        },
        "grammar_theory": """
        **Present Perfect**: Dùng khi báo cáo kết quả kéo dài đến hiện tại (*Revenue has grown by 15% this year*).  
        **Past Simple**: Dùng cho hành động đã hoàn tất trong quá khứ (*We launched the product in 2023*).
        """,
        "reading": {
            "title": "Annual Executive Strategy Review",
            "text": "Over the past three years, our corporation has expanded into five international markets. Last year, the executive board approved a major digital transformation roadmap.",
            "questions": [
                "How many international markets has the corporation expanded into?",
                "What did the board approve last year?",
            ],
        },
        "listening": "Listen to the CEO's quarterly briefing on strategic growth targets.",
        "writing_prompt": "Draft a brief 120-word executive summary evaluating your department's past performance.",
        "speaking_prompt": "Deliver a 2-minute oral presentation outlining your company's core strategic vision.",
        "translation": "Doanh nghiệp của chúng tôi đã mở rộng quy mô đáng kể trong quý vừa qua.",
    }
}

for d in range(2, 31):
    CURRICULUM[d] = {
        "title": f"Day {d}: Business Execution & Growth Focus {d}",
        "grammar_concept": f"Advanced Business Grammar Rules Unit {d}",
        "vocab": [
            {
                "word": f"Optimization_{d}",
                "pos": "noun",
                "meaning": "Sự tối ưu hóa",
                "example": f"Focusing on workflow optimization during day {d}.",
            },
            {
                "word": f"Leverage_{d}",
                "pos": "verb",
                "meaning": "Tận dụng nguồn lực",
                "example": f"Leveraging market data for strategy {d}.",
            },
        ],
        "pronunciation": {
            "focus": f"Pitch Modulation & Sentence Intonation Day {d}",
            "target_sentence": f"Delivering persuasive executive presentations requires precise intonation and confident delivery.",
        },
        "grammar_theory": f"Detailed grammar guidelines and professional writing structures for Unit {d}.",
        "reading": {
            "title": f"Market Analysis Report {d}",
            "text": f"Strategic planning and clear internal communication drive sustainable performance growth across departments in unit {d}.",
            "questions": [
                f"What drives sustainable corporate growth in unit {d}?"
            ],
        },
        "listening": f"Listen to senior executives discussing performance metrics for Unit {d}.",
        "writing_prompt": f"Write a professional business update covering core objectives for Day {d}.",
        "speaking_prompt": f"Present a concise progress report regarding key deliverables of Unit {d}.",
        "translation": f"Chiến lược kinh doanh hiệu quả mang lại sự tăng trưởng bền vững.",
    }


# ==========================================
# 6. GIAO DIỆN CHÍNH & TABS KỸ NĂNG
# ==========================================
def main():
    st.sidebar.title("🎓 English Mastery 30D")
    st.sidebar.caption("IELTS Speaking & Business Coach")

    api_key_input = st.sidebar.text_input(
        "Nhập Groq API Key:",
        value=st.session_state.groq_api_key,
        type="password",
    )
    if api_key_input != st.session_state.groq_api_key:
        st.session_state.groq_api_key = api_key_input
        save_data_to_file()

    st.sidebar.divider()

    completed_count = len(st.session_state.completed_days)
    st.sidebar.write(
        f"**Tiến độ:** {completed_count}/30 Ngày ({int(completed_count/30*100)}%)"
    )
    st.sidebar.progress(completed_count / 30.0)

    st.sidebar.divider()

    selected_day = st.sidebar.selectbox(
        "Chọn ngày học:",
        options=list(range(1, 31)),
        format_func=lambda x: f"Day {x}: {CURRICULUM[x]['title']}",
    )

    day_data = CURRICULUM[selected_day]

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"📅 {day_data['title']}")
        st.caption(f"🎯 Target Grammar Concept: {day_data['grammar_concept']}")
    with col2:
        is_completed = selected_day in st.session_state.completed_days
        if is_completed:
            st.markdown(
                "<span class='badge-green'>Trạng thái: Hoàn thành</span>",
                unsafe_allow_html=True,
            )
            if st.button("Hủy đánh dấu"):
                st.session_state.completed_days.remove(selected_day)
                save_data_to_file()
                st.rerun()
        else:
            st.markdown(
                "<span class='badge-pink'>Trạng thái: Đang học</span>",
                unsafe_allow_html=True,
            )
            if st.button("Đánh dấu Hoàn thành"):
                st.session_state.completed_days.add(selected_day)
                save_data_to_file()
                st.rerun()

    st.divider()

    # 7 Tabs kỹ năng chính (Đã bỏ tab Assessment)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔤 Vocabulary & Games",
        "🗣️ Pronunciation",
        "📐 Grammar Rules",
        "📖 Reading",
        "🎧 Listening Briefing",
        "✍️ Detailed Writing Scenario",
        "📊 Speaking Presentation",
    ])

    # 1. Vocabulary
    with tab1:
        st.subheader("📚 Key Vocabulary")
        for v in day_data["vocab"]:
            st.markdown(
                f"""
            <div class='card-box'>
                <h4><b>{v['word']}</b> <i>({v['pos']})</i></h4>
                <p><b>Ý nghĩa:</b> {v['meaning']}</p>
                <p><b>Ví dụ:</b> <i>"{v['example']}"</i></p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # 2. Pronunciation
    with tab2:
        st.subheader("🗣️ Pronunciation & Sentence Intonation")
        st.write(f"**Focus Area:** {day_data['pronunciation']['focus']}")
        st.info(
            f"**Target Sentence:** \"{day_data['pronunciation']['target_sentence']}\""
        )
        record_and_evaluate_speech(
            day_data["pronunciation"]["target_sentence"],
            context_label="Pronunciation",
        )

    # 3. Grammar Rules
    with tab3:
        st.subheader(f"📐 Grammar Focus: {day_data['grammar_concept']}")
        st.markdown(
            f"<div class='card-box'>{day_data['grammar_theory']}</div>",
            unsafe_allow_html=True,
        )

        if st.button("Load Grammar Masterclass"):
            with st.spinner("AI đang khởi tạo bài giảng Grammar Masterclass..."):
                masterclass_prompt = f"""
                Hãy đóng vai chuyên gia ngữ pháp Tiếng Anh thương mại.
                Tạo một bài giảng "Grammar Masterclass" chuyên sâu về chủ đề: "{day_data['grammar_concept']}".
                Gồm:
                1. Phân tích cấu trúc chuyên sâu & Lỗi sai phổ biến.
                2. 3 Ví dụ thực tế trong báo cáo doanh nghiệp.
                3. Bài tập ứng dụng nhanh có giải thích chi tiết.
                """
                response = call_groq_llm(
                    masterclass_prompt, st.session_state.groq_api_key
                )
                if response:
                    st.markdown("### 🎓 Grammar Masterclass Detailed Lesson")
                    st.markdown(
                        f"<div class='card-box'>{response}</div>",
                        unsafe_allow_html=True,
                    )

    # 4. Reading
    with tab4:
        st.subheader(f"📖 {day_data['reading']['title']}")
        st.write(day_data["reading"]["text"])
        st.markdown("#### Comprehension Questions:")
        for q in day_data["reading"]["questions"]:
            st.write(f"- {q}")

    # 5. Listening Briefing
    with tab5:
        st.subheader("🎧 Listening Briefing")
        st.write(day_data["listening"])

    # 6. Detailed Writing Scenario
    with tab6:
        st.subheader("✍️ Detailed Writing Scenario")
        st.write(f"**Nhiệm vụ:** {day_data['writing_prompt']}")

        user_writing = st.text_area(
            "Nhập văn bản bài viết của bạn tại đây:", height=150
        )
        if st.button("Chấm Điểm Bài Viết"):
            if not user_writing.strip():
                st.warning("Vui lòng nhập nội dung bài viết trước!")
            else:
                with st.spinner("AI đang chấm điểm ngữ pháp & từ vựng..."):
                    eval_writing_prompt = f"""
                    Chấm điểm bài viết Business English / IELTS Writing sau:
                    Bài làm: "{user_writing}"

                    Yêu cầu phản hồi bằng Tiếng Việt:
                    1. Điểm Grammar & Vocabulary (Thang điểm 10).
                    2. Chỉ ra các lỗi sai ngữ pháp, chọn từ chưa chuẩn.
                    3. Bản sửa nâng cấp chuyên nghiệp (Advanced Professional Version).
                    """
                    result = call_groq_llm(
                        eval_writing_prompt, st.session_state.groq_api_key
                    )
                    if result:
                        st.markdown("### 📊 AI Writing Feedback")
                        st.markdown(
                            f"<div class='card-box'>{result}</div>",
                            unsafe_allow_html=True,
                        )

    # 7. Speaking Presentation
    with tab7:
        st.subheader("📊 Speaking Presentation")
        st.write(f"**Chủ đề bài nói:** {day_data['speaking_prompt']}")
        record_and_evaluate_speech(
            day_data["speaking_prompt"], context_label="Speaking_Presentation"
        )


if __name__ == "__main__":
    main()