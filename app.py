import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from gtts import gTTS
import io

# ==========================================
# 1. CẤU HÌNH TRANG WEB & GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Business English AI Master",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# 2. KHỞI TẠO VÀ BẢO VỆ KẾT NỐI SUPABASE
# ==========================================
supabase_url = st.secrets.get("SUPABASE_URL", "")
supabase_key = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối Supabase: {e}")

# Hàm đọc lỗi an toàn từ Supabase
def safe_fetch_errors():
    if not supabase:
        return []
    try:
        res = supabase.table("error_logs").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        return []

# Hàm lưu lỗi an toàn vào Supabase
def safe_save_error(skill, lesson, original_text, corrected_text, reason):
    if not supabase:
        return False
    try:
        supabase.table("error_logs").insert({
            "skill": skill,
            "lesson": lesson,
            "original": original_text,
            "corrected": corrected_text,
            "reason": reason
        }).execute()
        return True
    except Exception as e:
        return False

# ==========================================
# 3. HÀM CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI (TTS)
# ==========================================
def text_to_speech_audio(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception:
        return None

# ==========================================
# 4. QUẢN LÝ LỊCH SỬ HỌC TẬP (SESSION STATE)
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 5. thanh BÊN (SIDEBAR) & CẤU HÌNH API
# ==========================================
with st.sidebar:
    st.title("⚙️ Cấu Hình Hệ Thống")
    
    # Lấy API key từ Secrets hoặc nhập tay
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key:", value=default_gemini_key, type="password")
    
    st.divider()
    st.title("🎯 Lộ Trình Học Tập")
    
    app_mode = st.radio(
        "Chọn chế độ học:",
        ["1. Đánh giá đầu vào (Placement Test)", "2. Giáo trình 30 Ngày (Business English)", "3. Review Sổ Tay Lỗi Sai"]
    )
    
    st.divider()
    st.subheader("📊 Trạng Thái Kết Nối")
    if supabase:
        st.success("Database Supabase: Kết nối an toàn")
    else:
        st.warning("Database Supabase: Chưa cấu hình (Chạy chế độ Offline)")

# ==========================================
# 6. KHỞI TẠO BỘ NÃO GEMINI AI
# ==========================================
SYSTEM_PROMPT = """
Bạn là một Giảng viên Chuyên gia Business English Cao cấp.
Nhiệm vụ của bạn là dẫn dắt học viên theo chuẩn khung Châu Âu (CEFR).

Quy tắc bắt buộc:
1. Khi học viên làm bài Đọc/Nghe/Từ vựng/Ngữ pháp: Hãy chấm điểm chính xác số câu đúng/sai, giải thích chi tiết lý do.
2. Với bài Writing (>=100 từ): Chấm điểm theo tiêu chí Task Achievement, Grammar, Vocabulary, Coherence. Chỉ rõ từng lỗi sai (Original -> Correction -> Reason) và bắt buộc đưa ra 1 bài mẫu (Model Answer) đạt chuẩn Executive.
3. Với bài Speaking: Phân tích phát âm, ngữ pháp, ngữ điệu và độ chuyên nghiệp (Business Tone).
4. Luôn tuân thủ số lượng câu hỏi và độ dài yêu cầu trong từng phân môn.
"""

if not api_key:
    st.info("👋 Vui lòng nhập Google Gemini API Key ở thanh bên trái để kích hoạt trợ lý AI.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

    # ==========================================
    # PHẦN 1: ĐÁNH GIÁ ĐẦU VÀO (PLACEMENT TEST)
    # ==========================================
    if app_mode == "1. Đánh giá đầu vào (Placement Test)":
        st.title("📋 Bài Kiểm Tra Đánh Giá Đầu Vào Comprehensive")
        st.write("Hoàn thành bài kiểm tra dưới đây để AI phân tích trình độ và tối ưu lộ trình 30 ngày tới.")

        test_tab1, test_tab2, test_tab3, test_tab4, test_tab5, test_tab6 = st.tabs([
            "1. Từ vựng (15 Qs)", "2. Ngữ pháp (15 Qs)", "3. Đọc hiểu (15 Qs)", 
            "4. Nghe hiểu (10 Qs)", "5. Viết (>=100 từ)", "6. Nói (3 Topics)"
        ])

        with test_tab1:
            st.subheader("Từ vựng Thương mại (15 câu hỏi)")
            if st.button("Tạo đề kiểm tra Từ vựng", key="gen_vocab_test"):
                with st.spinner("AI đang tạo 15 câu hỏi từ vựng..."):
                    prompt = "Tạo 15 câu hỏi trắc nghiệm từ vựng Business English (mức độ từ A2 đến C1) kèm đáp án ẩn bên dưới."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        with test_tab2:
            st.subheader("Ngữ pháp Thương mại (15 câu hỏi)")
            if st.button("Tạo đề kiểm tra Ngữ pháp", key="gen_gram_test"):
                with st.spinner("AI đang tạo 15 câu hỏi ngữ pháp..."):
                    prompt = "Tạo 15 câu hỏi trắc nghiệm Ngữ pháp Business English kèm đáp án ẩn bên dưới."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        with test_tab3:
            st.subheader("Kỹ năng Đọc hiểu (Reading)")
            st.caption("Đoạn văn dài ít nhất 20 câu + 15 câu hỏi trắc nghiệm")
            if st.button("Tạo bài Reading Đánh giá", key="gen_read_test"):
                with st.spinner("AI đang viết đoạn văn 20 câu và tạo 15 câu hỏi..."):
                    prompt = "Viết 1 đoạn văn chủ đề Business Strategy dài ÍT NHẤT 20 CÂU tiếng Anh. Phía dưới đưa ra 15 câu hỏi đọc hiểu trắc nghiệm."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        with test_tab4:
            st.subheader("Kỹ năng Nghe (Listening)")
            if st.button("Tạo bài Listening & Audio", key="gen_listen_test"):
                with st.spinner("AI đang tạo kịch bản nghe và File Âm thanh..."):
                    script_prompt = "Viết 1 đoạn hội thoại đàm phán hợp đồng tiếng Anh (khoảng 15-20 câu). Bắt đầu bằng chữ [SCRIPT]."
                    res = model.generate_content(script_prompt)
                    st.markdown(res.text)
                    
                    # Phát âm đoạn văn
                    audio_fp = text_to_speech_audio(res.text)
                    if audio_fp:
                        st.audio(audio_fp, format="audio/mp3")
                    
                    st.markdown("---")
                    st.markdown("**10 Câu hỏi Nghe hiểu:**")
                    qs_prompt = f"Dựa vào đoạn văn sau, hãy tạo 10 câu hỏi nghe hiểu trắc nghiệm:\n{res.text}"
                    st.markdown(model.generate_content(qs_prompt).text)

        with test_tab5:
            st.subheader("Kỹ năng Viết (Writing)")
            st.markdown("**Đề bài:** Write a business proposal or response email (at least 100 words) addressing a customer complaint regarding a delayed shipment.")
            user_essay = st.text_area("Nhập bài viết của bạn (Tối thiểu 100 từ):", height=200)
            if st.button("Chấm điểm bài Viết", key="score_writing_test"):
                if len(user_essay.split()) < 100:
                    st.warning("Bài viết của bạn chưa đủ 100 từ. Vui lòng viết thêm!")
                else:
                    with st.spinner("AI đang phân tích và chấm điểm bài viết..."):
                        prompt = f"Hãy chấm điểm chi tiết bài viết sau (chỉ rõ lỗi sai, sửa lỗi, cho điểm theo CEFR và viết 1 bài mẫu chuẩn >=150 từ):\n\n{user_essay}"
                        res = model.generate_content(prompt)
                        st.markdown(res.text)

        with test_tab6:
            st.subheader("Kỹ năng Nói (Speaking - 3 Topics)")
            st.markdown("""
            1. **Topic 1:** Introduce yourself and your professional background.
            2. **Topic 2:** Describe a challenging project you managed at work.
            3. **Topic 3:** Pitch a new product idea to a potential investor.
            """)
            
            st.write("🎙️ **Ghi âm câu trả lời của bạn:**")
            audio_val = st.audio_input("Nói vào micro để AI phân tích:")
            
            if audio_val and st.button("Đánh giá bài nói"):
                with st.spinner("AI đang lắng nghe và phân tích bài nói..."):
                    audio_bytes = audio_val.read()
                    prompt = "Hãy chuyển giọng nói này thành văn bản (Speech-to-Text), sau đó nhận xét ngữ pháp, phát âm và Business Tone."
                    response = model.generate_content([
                        {"mime_type": "audio/wav", "data": audio_bytes},
                        prompt
                    ])
                    st.markdown(response.text)

    # ==========================================
    # PHẦN 2: GIÁO TRÌNH 30 NGÀY (BUSINESS ENGLISH)
    # ==========================================
    elif app_mode == "2. Giáo trình 30 Ngày (Business English)":
        st.title("📚 Giáo Trình Cố Định 30 Ngày - Next Level Master")
        
        day_selected = st.slider("Chọn ngày học (Day 1 - Day 30):", 1, 30, 1)
        st.header(f"📌 Bài Học Day {day_selected}")

        skill_tab1, skill_tab2, skill_tab3, skill_tab4, skill_tab5, skill_tab6 = st.tabs([
            "📖 Từ vựng (10 từ)", "📝 Ngữ pháp", "🎧 Nghe (10 Qs)", 
            "📚 Đọc (20 câu, 15 Qs)", "✍️ Viết (>=100 từ)", "🎙️ Nói (Speech-to-Text)"
        ])

        # 1. Từ vựng Day X
        with skill_tab1:
            st.subheader(f"10 Từ Vựng Thương Mại - Day {day_selected}")
            if st.button("Tải danh sách 10 từ vựng", key="btn_vocab_day"):
                with st.spinner("Đang tải từ vựng..."):
                    prompt = f"Soạn 10 từ vựng Business English chuyên sâu cho Day {day_selected}. Định dạng bảng gồm: Từ tiếng Anh | Giải nghĩa tiếng Anh | Giải nghĩa tiếng Việt | Từ đồng nghĩa (Synonyms) | Ví dụ câu."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        # 2. Ngữ pháp Day X
        with skill_tab2:
            st.subheader("Chủ đề Ngữ pháp & Bài tập Đánh giá (10-15 câu)")
            if st.button("Tải lý thuyết & Bài tập Ngữ pháp", key="btn_gram_day"):
                with st.spinner("Đang biên soạn lý thuyết và câu hỏi..."):
                    prompt = f"Dạy 1 chủ đề Ngữ pháp Business English nâng cao cho Day {day_selected}. Sau đó đưa ra 12 câu hỏi trắc nghiệm/điền từ để đánh giá kèm đáp án giải thích."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        # 3. Nghe Day X
        with skill_tab3:
            st.subheader("Bài tập Nghe hiểu (10 câu hỏi)")
            if st.button("Tạo bài nghe Day này", key="btn_listen_day"):
                with st.spinner("Đang tạo bài nghe audio..."):
                    p_script = f"Soạn 1 bài nói/hội thoại tiếng Anh chủ đề Công sở Day {day_selected} (khoảng 15 câu)."
                    script_text = model.generate_content(p_script).text
                    st.markdown(script_text)
                    
                    audio_fp = text_to_speech_audio(script_text)
                    if audio_fp:
                        st.audio(audio_fp, format="audio/mp3")
                    
                    p_qs = f"Dựa vào bài nghe trên, tạo 10 câu hỏi trắc nghiệm nghe hiểu:\n{script_text}"
                    st.markdown(model.generate_content(p_qs).text)

        # 4. Đọc hiểu Day X
        with skill_tab4:
            st.subheader("Bài Đọc hiểu (Đoạn văn >= 20 câu + 15 câu hỏi)")
            if st.button("Tải bài Đọc Day này", key="btn_read_day"):
                with st.spinner("Đang khởi tạo đoạn văn 20 câu..."):
                    prompt = f"Viết 1 bài báo Business/Kinh tế tiếng Anh dài ÍT NHẤT 20 CÂU cho Day {day_selected}. Phía dưới tạo 15 câu hỏi trắc nghiệm kiểm tra độ hiểu bài."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)

        # 5. Viết Day X
        with skill_tab5:
            st.subheader("Bài tập Viết Business (>= 100 từ)")
            st.info(f"Chủ đề Viết Day {day_selected}: Write an official memo or email to your team regarding strategic goals for Q3.")
            daily_essay = st.text_area("Bài làm của bạn:", height=180, key="daily_writing_input")
            
            if st.button("Nộp bài & Chấm điểm Viết", key="btn_score_daily_write"):
                if len(daily_essay.split()) < 100:
                    st.warning("Bài viết chưa đủ 100 từ. Vui lòng bổ sung!")
                else:
                    with st.spinner("AI đang chấm điểm và đề xuất bài mẫu..."):
                        prompt = f"Chấm điểm bài viết Day {day_selected}:\n{daily_essay}\n\nYêu cầu: Sửa từng lỗi sai (Original -> Corrected -> Reason), Chấm điểm, và Viết 1 bài mẫu (Model Answer) xuất sắc."
                        res = model.generate_content(prompt)
                        st.markdown(res.text)
                        
                        # Lưu gợi ý lỗi vào Supabase nếu có
                        safe_save_error("Writing", f"Day {day_selected}", "Xem chi tiết bài viết", "Đã phân tích", "Lỗi ngữ pháp & Văn phong")

        # 6. Nói Day X
        with skill_tab6:
            st.subheader("Luyện Nói Tương Tác (Speaking Roleplay)")
            st.write(f"💬 **Chủ đề hội thoại Day {day_selected}:** Executive Meeting Discussion")
            
            audio_daily = st.audio_input("Nói câu trả lời của bạn:")
            if audio_daily and st.button("Phân tích phát âm & Ngữ điệu"):
                with st.spinner("AI đang phân tích file ghi âm..."):
                    audio_bytes = audio_daily.read()
                    prompt = "Chuyển giọng nói này thành text, phân tích lỗi phát âm, ngữ pháp và gợi ý cách nói chuyên nghiệp hơn."
                    res = model.generate_content([
                        {"mime_type": "audio/wav", "data": audio_bytes},
                        prompt
                    ])
                    st.markdown(res.text)

    # ==========================================
    # PHẦN 3: REVIEW SỔ TAY LỖI SAI (MEMORIZATION)
    # ==========================================
    elif app_mode == "3. Review Sổ Tay Lỗi Sai":
        st.title("📚 Sổ Tay Lỗi Sai & Remind Lịch Sử")
        st.caption("Danh sách các lỗi sai đã lưu từ Supabase giúp bạn ôn tập để không lặp lại.")

        errors = safe_fetch_errors()
        
        if not errors:
            st.info("Chưa có lỗi sai nào được lưu vào Supabase Database.")
        else:
            for idx, err in enumerate(errors):
                with st.expander(f"❌ Lỗi {idx+1} [{err.get('skill', 'General')}] - {err.get('lesson', '')}"):
                    st.write(f"**Nội dung:** {err.get('original', '')}")
                    st.write(f"**Sửa chuẩn:** {err.get('corrected', '')}")
                    st.write(f"**Lý do sai:** {err.get('reason', '')}")
                    st.caption(f"Thời gian lưu: {err.get('created_at', '')}")

        st.divider()
        st.subheader("💡 AI Ôn Tập Lỗi Sai Tự Động")
        if st.button("Tạo bài tập Ôn lại các lỗi hay sai"):
            with st.spinner("AI đang tổng hợp các lỗi từ database để tạo bài tập ôn lại..."):
                prompt = f"Dựa vào danh sách lỗi sai sau, hãy tạo 5 câu hỏi trắc nghiệm để học viên tự kiểm tra lại kiến thức:\n{errors}"
                res = model.generate_content(prompt)
                st.markdown(res.text)