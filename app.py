import json
import os
import random
import tempfile
import requests
import streamlit as st

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & ÉP CHỮ ĐEN - NỀN HỒNG/TRẮNG
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
    /* Nền ứng dụng chính màu hồng nhạt */
    .main { 
        background-color: #FFF5F5 !important; 
    }
    
    /* Thẻ nội dung màu trắng - Ép màu chữ đen hoàn toàn (#1A202C) */
    .card-box {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
        border: 1px solid #FEB2B2;
        margin-bottom: 20px;
    }
    
    /* Ép tất cả thành phần văn bản bên trong card-box luôn hiển thị chữ đen */
    .card-box *, .card-box h1, .card-box h2, .card-box h3, .card-box h4, 
    .card-box p, .card-box span, .card-box div, .card-box b, .card-box i, .card-box li {
        color: #1A202C !important;
    }

    /* Đèn báo trạng thái */
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

    /* Styling nút bấm */
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
# 3. XỬ LÝ GROQ API (SỬA LỖI MODEL 400)
# ==========================================
def call_groq_llm(prompt, api_key, system_instruction=None):
    if not api_key:
        st.error("Vui lòng nhập Groq API Key ở Sidebar bên trái!")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

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

    audio_value = st.audio_input(
        "Nhấn nút Micro bên dưới để ghi âm bài đọc:",
        key=f"rec_{context_label}_{hash(reference_text)}",
    )

    if audio_value is not None:
        audio_bytes = audio_value.read()

        st.markdown("#### 🔊 Nghe lại bản ghi âm của bạn:")
        st.audio(audio_bytes, format="audio/wav")

        if st.button(
            "🎯 Phân Tích & Chấm Điểm Ngữ Điệu / Phát Âm",
            key=f"btn_eval_{context_label}_{hash(reference_text)}",
        ):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key ở Sidebar!")
            else:
                with st.spinner("Đang nhận diện giọng nói (Whisper Large V3)..."):
                    transcription = transcribe_audio_groq(
                        audio_bytes, st.session_state.groq_api_key
                    )

                if transcription:
                    st.info(f'📝 **Văn bản nhận diện được:** "{transcription}"')
                    with st.spinner("AI đang phân tích ngữ điệu, trọng âm và độ trôi chảy..."):
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
# 5. DỮ LIỆU BÀI HỌC CURRICULUM (10 TỪ VỰNG / BÀI)
# ==========================================
CURRICULUM = {
    1: {
        "title": "Day 1: Corporate Strategy & Vision",
        "grammar_concept": "Present Perfect vs. Past Simple in Performance Reporting",
        "vocab": [
            {"word": "Synergy", "pos": "noun", "meaning": "Sự cộng hưởng", "example": "Cross-departmental synergy boosted overall efficiency."},
            {"word": "Benchmark", "pos": "noun", "meaning": "Tiêu chuẩn đánh giá", "example": "We set new industry benchmarks this quarter."},
            {"word": "Streamline", "pos": "verb", "meaning": "Tối ưu hóa quy trình", "example": "The team streamlined operations to cut costs."},
            {"word": "Leverage", "pos": "verb", "meaning": "Tận dụng nguồn lực", "example": "We must leverage customer data for growth."},
            {"word": "Pivot", "pos": "verb", "meaning": "Chuyển hướng chiến lược", "example": "The startup pivoted to a B2B business model."},
            {"word": "Milestone", "pos": "noun", "meaning": "Cột mốc quan trọng", "example": "Reaching 1M users was a critical milestone."},
            {"word": "Optimization", "pos": "noun", "meaning": "Sự tối ưu hóa", "example": "Workflow optimization reduced project delays."},
            {"word": "Feasibility", "pos": "noun", "meaning": "Tính khả thi", "example": "We conducted a feasibility study before launching."},
            {"word": "Deliverable", "pos": "noun", "meaning": "Sản phẩm bàn giao", "example": "All key deliverables were submitted on schedule."},
            {"word": "Scalability", "pos": "noun", "meaning": "Khả năng mở rộng", "example": "Cloud architecture ensures system scalability."}
        ],
        "pronunciation": {
            "focus": "Linking Words & Intonation in Executive Summaries",
            "target_sentence": "Our strategic initiatives have significantly increased revenue over the past fiscal year."
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
                "What did the board approve last year?"
            ]
        },
        "listening": "Listen to the CEO's quarterly briefing on strategic growth targets.",
        "writing_prompt": "Draft a brief 120-word executive summary evaluating your department's past performance.",
        "speaking_prompt": "Deliver a 2-minute oral presentation outlining your company's core strategic vision."
    }
}

# Khởi tạo 30 ngày đầy đủ 10 từ vựng mỗi ngày
for d in range(2, 31):
    CURRICULUM[d] = {
        "title": f"Day {d}: Business Execution & Growth Focus {d}",
        "grammar_concept": f"Advanced Business Grammar Rules Unit {d}",
        "vocab": [
            {"word": f"Strategy_{d}_1", "pos": "noun", "meaning": f"Chiến lược kinh doanh {d}.1", "example": f"Executing core strategy for day {d}."},
            {"word": f"Optimization_{d}_2", "pos": "noun", "meaning": f"Tối ưu hóa quy trình {d}.2", "example": f"Focusing on optimization in unit {d}."},
            {"word": f"Leverage_{d}_3", "pos": "verb", "meaning": f"Tận dụng nguồn lực {d}.3", "example": f"Leveraging key resources during unit {d}."},
            {"word": f"Benchmark_{d}_4", "pos": "noun", "meaning": f"Tiêu chuẩn chất lượng {d}.4", "example": f"Setting performance benchmarks in unit {d}."},
            {"word": f"Feasibility_{d}_5", "pos": "noun", "meaning": f"Tính khả thi dự án {d}.5", "example": f"Assessing project feasibility for unit {d}."},
            {"word": f"Deliverable_{d}_6", "pos": "noun", "meaning": f"Hạng mục bàn giao {d}.6", "example": f"Completing project deliverables in unit {d}."},
            {"word": f"Scalability_{d}_7", "pos": "noun", "meaning": f"Mở rộng quy mô {d}.7", "example": f"Ensuring business scalability in unit {d}."},
            {"word": f"Consolidate_{d}_8", "pos": "verb", "meaning": f"Củng cố thị phần {d}.8", "example": f"Consolidating market presence during day {d}."},
            {"word": f"Diversify_{d}_9", "pos": "verb", "meaning": f"Đa dạng hóa danh mục {d}.9", "example": f"Diversifying investment options in unit {d}."},
            {"word": f"Retention_{d}_10", "pos": "noun", "meaning": f"Duy trì khách hàng {d}.10", "example": f"Improving customer retention rate for unit {d}."}
        ],
        "pronunciation": {
            "focus": f"Pitch Modulation & Sentence Intonation Day {d}",
            "target_sentence": f"Delivering persuasive executive presentations requires precise intonation and confident delivery."
        },
        "grammar_theory": f"Detailed grammar guidelines and professional writing structures for Unit {d}.",
        "reading": {
            "title": f"Market Analysis Report {d}",
            "text": f"Strategic planning and clear internal communication drive sustainable performance growth across departments in unit {d}.",
            "questions": [f"What drives sustainable corporate growth in unit {d}?"]
        },
        "listening": f"Listen to senior executives discussing performance metrics for Unit {d}.",
        "writing_prompt": f"Write a professional business update covering core objectives for Day {d}.",
        "speaking_prompt": f"Present a concise progress report regarding key deliverables of Unit {d}."
    }


# ==========================================
# 6. GIAO DIỆN CHÍNH VÀ CÁC TABS KỸ NĂNG
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
    st.sidebar.write(f"**Tiến độ:** {completed_count}/30 Ngày ({int(completed_count/30*100)}%)")
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
            st.markdown("<span class='badge-green'>Trạng thái: Hoàn thành</span>", unsafe_allow_html=True)
            if st.button("Hủy đánh dấu"):
                st.session_state.completed_days.remove(selected_day)
                save_data_to_file()
                st.rerun()
        else:
            st.markdown("<span class='badge-pink'>Trạng thái: Đang học</span>", unsafe_allow_html=True)
            if st.button("Đánh dấu Hoàn thành"):
                st.session_state.completed_days.add(selected_day)
                save_data_to_file()
                st.rerun()

    st.divider()

    # 7 Tab kỹ năng chính (Đã bỏ hoàn toàn Tab Assessment)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔤 Vocabulary & Games",
        "🗣️ Pronunciation",
        "📐 Grammar Rules",
        "📖 Reading",
        "🎧 Listening Briefing",
        "✍️ Detailed Writing Scenario",
        "📊 Speaking Presentation",
    ])

    # ------------------------------------------
    # TAB 1: VOCABULARY & 2 INTERACTIVE GAMES
    # ------------------------------------------
    with tab1:
        st.subheader("📚 10 Key Vocabulary Words")
        
        # Hiển thị danh sách 10 từ vựng
        cols = st.columns(2)
        for idx, v in enumerate(day_data["vocab"]):
            col = cols[idx % 2]
            with col:
                st.markdown(
                    f"""
                    <div class='card-box'>
                        <h4><b>{idx+1}. {v['word']}</b> <i>({v['pos']})</i></h4>
                        <p><b>Ý nghĩa:</b> {v['meaning']}</p>
                        <p><b>Ví dụ:</b> <i>"{v['example']}"</i></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()
        st.subheader("🎮 Vocabulary Practice Games")

        # Game 1: Multiple Choice Flashcard Quiz
        st.markdown("### 🕹️ Game 1: Quick Meaning Quiz (Trắc nghiệm Từ vựng)")
        vocab_list = day_data["vocab"]
        
        quiz_word = vocab_list[st.session_state.get(f"q_idx_{selected_day}", 0) % len(vocab_list)]
        correct_meaning = quiz_word["meaning"]
        
        # Tạo danh sách phương án lựa chọn
        options = [correct_meaning]
        other_meanings = [v["meaning"] for v in vocab_list if v["meaning"] != correct_meaning]
        options.extend(random.sample(other_meanings, min(3, len(other_meanings))))
        random.shuffle(options)

        st.markdown(f"**Từ vựng cần chọn nghĩa đúng:** `<h3 style='display:inline; color:#E53E3E;'>{quiz_word['word']}</h3>`", unsafe_allow_html=True)
        user_choice = st.radio("Chọn nghĩa đúng:", options, key=f"radio_g1_{selected_day}_{quiz_word['word']}")
        
        if st.button("Kiểm Tra Đáp Án Game 1", key=f"btn_g1_{selected_day}"):
            if user_choice == correct_meaning:
                st.success("🎉 Chính xác! Bạn đã nhớ đúng nghĩa của từ này.")
                st.session_state[f"q_idx_{selected_day}"] = st.session_state.get(f"q_idx_{selected_day}", 0) + 1
            else:
                st.error(f"❌ Chưa đúng rồi! Đáp án chính xác là: **{correct_meaning}**")

        st.divider()

        # Game 2: Fill-in-the-Blank Sentence Application
        st.markdown("### 🧩 Game 2: Context Fill-in-the-Blank (Ghép Từ Vào Câu)")
        fill_item = vocab_list[(st.session_state.get(f"q_idx_{selected_day}", 0) + 1) % len(vocab_list)]
        masked_sentence = fill_item["example"].replace(fill_item["word"], "________")
        
        st.markdown(f"**Điền từ còn thiếu vào câu:** *\"{masked_sentence}\"*")
        user_input_word = st.text_input("Nhập từ tiếng Anh thích hợp:", key=f"input_g2_{selected_day}")
        
        if st.button("Kiểm Tra Đáp Án Game 2", key=f"btn_g2_{selected_day}"):
            if user_input_word.strip().lower() == fill_item["word"].lower():
                st.success(f"🎉 Xuất sắc! Từ điền chính xác là **{fill_item['word']}**.")
            else:
                st.error(f"❌ Rất tiếc! Đáp án chuẩn xác là: **{fill_item['word']}**")

    # ------------------------------------------
    # TAB 2: PRONUNCIATION & INTONATION
    # ------------------------------------------
    with tab2:
        st.subheader("🗣️ Pronunciation & Sentence Intonation")
        st.write(f"**Focus Area:** {day_data['pronunciation']['focus']}")
        st.info(f"**Target Sentence:** \"{day_data['pronunciation']['target_sentence']}\"")
        record_and_evaluate_speech(
            day_data["pronunciation"]["target_sentence"],
            context_label="Pronunciation",
        )

    # ------------------------------------------
    # TAB 3: GRAMMAR RULES & MASTERCLASS
    # ------------------------------------------
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

    # ------------------------------------------
    # TAB 4: READING COMPREHENSION
    # ------------------------------------------
    with tab4:
        st.subheader(f"📖 {day_data['reading']['title']}")
        st.write(day_data["reading"]["text"])
        st.markdown("#### Comprehension Questions:")
        for q in day_data["reading"]["questions"]:
            st.write(f"- {q}")

    # ------------------------------------------
    # TAB 5: LISTENING BRIEFING
    # ------------------------------------------
    with tab5:
        st.subheader("🎧 Listening Briefing")
        st.write(day_data["listening"])

    # ------------------------------------------
    # TAB 6: DETAILED WRITING SCENARIO
    # ------------------------------------------
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

    # ------------------------------------------
    # TAB 7: SPEAKING PRESENTATION
    # ------------------------------------------
    with tab7:
        st.subheader("📊 Speaking Presentation")
        st.write(f"**Chủ đề bài nói:** {day_data['speaking_prompt']}")
        record_and_evaluate_speech(
            day_data["speaking_prompt"], context_label="Speaking_Presentation"
        )


if __name__ == "__main__":
    main()