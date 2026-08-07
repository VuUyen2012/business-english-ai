import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB
# ==========================================
st.set_page_config(
    page_title="Business English Master AI",
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
    except Exception:
        supabase = None

# --- HÀM TƯƠNG TÁC DATABASE AN TOÀN ---
def safe_save(table_name: str, data_dict: dict):
    if not supabase:
        return False
    try:
        supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception:
        return False

def safe_fetch(table_name: str):
    if not supabase:
        return []
    try:
        res = supabase.table(table_name).select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

# ==========================================
# 3. HÀM PHÁT ÂM TIẾNG ANH (BẰNG NATIVE BROWSER SPEECH)
# ==========================================
def play_audio_html(text_to_speak):
    """Sử dụng Web Speech API của trình duyệt - Không bao giờ lỗi thư viện"""
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <div style="margin: 10px 0;">
            <button onclick="speakText()" style="
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;">
                🔊 Phát âm Audio (Giọng đọc Trình duyệt)
            </button>
        </div>
        <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    st.components.v1.html(js_code, height=60)

# ==========================================
# 4. THANH BÊN (SIDEBAR) & CẤU HÌNH
# ==========================================
with st.sidebar:
    st.title("⚙️ Cấu Hình Hệ Thống")
    
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key:", value=default_gemini_key, type="password")
    
    st.divider()
    st.title("🎯 Điều Hướng Chức Năng")
    
    app_mode = st.radio(
        "Chọn chế độ:",
        [
            "1. Đánh giá đầu vào (Placement Test)", 
            "2. Giáo trình 30 Ngày (Business English)", 
            "3. Review Sổ Tay Lỗi Sai & Lịch Sử Học"
        ]
    )
    
    st.divider()
    st.subheader("📊 Trạng Thái Database")
    if supabase:
        st.success("Supabase: Đã kết nối (Dữ liệu được sao lưu)")
    else:
        st.warning("Supabase: Chưa kết nối (Chạy tạm thời)")

# ==========================================
# 5. CẤU HÌNH SYSTEM PROMPT & GEMINI
# ==========================================
SYSTEM_PROMPT = """
Bạn là Giảng viên Chuyên gia Business English Cao cấp.
Quy tắc giảng dạy:
1. Luôn chấm điểm chính xác các kỹ năng theo tiêu chí CEFR (A2, B1, B2, C1).
2. Khi học viên làm bài Viết (>=100 từ): Hãy sửa lỗi theo chuẩn: [Câu gốc] -> [Câu sửa] -> [Lý do] và BẮT BUỘC cung cấp 1 bài mẫu (Model Answer) chuyên nghiệp.
3. Luôn đáp ứng đủ số lượng câu hỏi và độ dài văn bản theo yêu cầu của học viên.
"""

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình Gemini API Key để sử dụng app!")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

    # ==========================================
    # PHẦN 1: ĐÁNH GIÁ ĐẦU VÀO (PLACEMENT TEST)
    # ==========================================
    if app_mode == "1. Đánh giá đầu vào (Placement Test)":
        st.title("📋 Bài Kiểm Tra Đánh Giá Đầu Vào Comprehensive")
        st.caption("Kết quả test sẽ tự động lưu vào Database để theo dõi sự tiến bộ qua thời gian.")

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "1. Từ vựng (15 Qs)", "2. Ngữ pháp (15 Qs)", "3. Đọc hiểu (20 câu)", 
            "4. Nghe hiểu (10 Qs)", "5. Viết (>=100 từ)", "6. Nói (3 Topics)"
        ])

        with t1:
            st.subheader("Kiểm tra Từ vựng (15 câu hỏi)")
            if st.button("Tạo đề Từ vựng", key="btn_p_vocab"):
                with st.spinner("AI đang tạo đề..."):
                    res = model.generate_content("Tạo 15 câu hỏi trắc nghiệm từ vựng Business English (từ A2 đến C1) kèm đáp án ẩn bên dưới.")
                    st.markdown(res.text)

        with t2:
            st.subheader("Kiểm tra Ngữ pháp (15 câu hỏi)")
            if st.button("Tạo đề Ngữ pháp", key="btn_p_gram"):
                with st.spinner("AI đang tạo đề..."):
                    res = model.generate_content("Tạo 15 câu hỏi trắc nghiệm ngữ pháp Business English kèm đáp án ẩn bên dưới.")
                    st.markdown(res.text)

        with t3:
            st.subheader("Kiểm tra Đọc hiểu (Reading)")
            if st.button("Tạo bài Đọc hiểu", key="btn_p_read"):
                with st.spinner("AI đang khởi tạo đoạn văn 20 câu và 15 câu hỏi..."):
                    res = model.generate_content("Viết 1 đoạn văn chủ đề Business Strategy dài ÍT NHẤT 20 CÂU. Phía dưới đưa ra 15 câu hỏi trắc nghiệm đọc hiểu.")
                    st.markdown(res.text)

        with t4:
            st.subheader("Kiểm tra Nghe hiểu (Listening)")
            if st.button("Tạo bài Nghe & Audio", key="btn_p_listen"):
                with st.spinner("AI đang tạo kịch bản nghe..."):
                    script_res = model.generate_content("Viết 1 đoạn hội thoại đàm phán hợp đồng tiếng Anh dài 15-20 câu.")
                    st.markdown(script_res.text)
                    play_audio_html(script_res.text)
                    st.markdown("---")
                    qs_res = model.generate_content(f"Dựa vào bài nghe sau, tạo 10 câu hỏi trắc nghiệm:\n{script_res.text}")
                    st.markdown(qs_res.text)

        with t5:
            st.subheader("Kiểm tra Viết (Writing)")
            essay_text = st.text_area("Nhập bài viết của bạn (Tối thiểu 100 từ):", height=200, key="p_essay")
            if st.button("Chấm điểm & Lưu kết quả Test Viết", key="btn_p_score_write"):
                if len(essay_text.split()) < 100:
                    st.warning(f"Bài viết hiện tại mới có {len(essay_text.split())} từ. Vui lòng viết đủ 100 từ!")
                else:
                    with st.spinner("AI đang chấm điểm chi tiết..."):
                        res = model.generate_content(f"Chấm điểm bài viết sau (chỉ rõ lỗi sai, sửa lỗi, cho điểm CEFR và viết 1 bài mẫu chuẩn >=150 từ):\n\n{essay_text}")
                        st.markdown(res.text)
                        
                        safe_save("placement_results", {
                            "writing_feedback": res.text,
                            "overall_level": "Đã đánh giá bài viết"
                        })
                        st.success("✅ Đã sao lưu kết quả đánh giá vào Database an toàn!")

        with t6:
            st.subheader("Kiểm tra Nói (Speaking - 3 Topics)")
            spoken_audio = st.audio_input("Ghi âm bài nói của bạn:")
            if spoken_audio and st.button("Chấm điểm bài Nói", key="btn_p_score_speak"):
                with st.spinner("AI đang phân tích bài nói..."):
                    audio_bytes = spoken_audio.read()
                    res = model.generate_content([
                        {"mime_type": "audio/wav", "data": audio_bytes},
                        "Chuyển giọng nói thành text, đánh giá ngữ pháp, phát âm và Business Tone."
                    ])
                    st.markdown(res.text)

    # ==========================================
    # PHẦN 2: GIÁO TRÌNH 30 NGÀY (BUSINESS ENGLISH)
    # ==========================================
    elif app_mode == "2. Giáo trình 30 Ngày (Business English)":
        st.title("📚 Giáo Trình Cố Định 30 Ngày - Business English")
        
        day_selected = st.slider("Chọn ngày học:", 1, 30, 1)
        st.header(f"📌 Chi Tiết Bài Học: Day {day_selected}")

        d_t1, d_t2, d_t3, d_t4, d_t5, d_t6 = st.tabs([
            "📖 Từ vựng", "📝 Ngữ pháp", "🎧 Nghe", 
            "📚 Đọc", "✍️ Viết (>=100 từ)", "🎙️ Nói"
        ])

        with d_t1:
            st.subheader(f"10 Từ Vựng Thương Mại - Day {day_selected}")
            if st.button("Tải 10 từ vựng", key=f"btn_d_vocab_{day_selected}"):
                with st.spinner("Đang tải danh sách từ vựng..."):
                    res = model.generate_content(f"Soạn 10 từ vựng Business English cho Day {day_selected}. Định dạng bảng: Từ tiếng Anh | Giải nghĩa EN | Giải nghĩa VI | Từ đồng nghĩa | Ví dụ câu.")
                    st.markdown(res.text)

        with d_t2:
            st.subheader("Ngữ pháp theo Chủ đề")
            if st.button("Tải bài học Ngữ pháp", key=f"btn_d_gram_{day_selected}"):
                with st.spinner("Đang tải lý thuyết..."):
                    res = model.generate_content(f"Dạy 1 chủ đề Ngữ pháp Business English cho Day {day_selected}. Sau đó tạo 12 câu hỏi trắc nghiệm đánh giá kèm đáp án.")
                    st.markdown(res.text)

        with d_t3:
            st.subheader("Bài tập Nghe hiểu")
            if st.button("Tạo bài Nghe Day này", key=f"btn_d_listen_{day_selected}"):
                with st.spinner("Đang tạo kịch bản..."):
                    script_text = model.generate_content(f"Soạn 1 đoạn hội thoại công sở tiếng Anh Day {day_selected} (15 câu).").text
                    st.markdown(script_text)
                    play_audio_html(script_text)

        with d_t4:
            st.subheader("Bài Đọc hiểu (Đoạn văn >= 20 câu)")
            if st.button("Tải bài Đọc Day này", key=f"btn_d_read_{day_selected}"):
                with st.spinner("Đang khởi tạo đoạn văn..."):
                    res = model.generate_content(f"Viết 1 bài báo Business tiếng Anh dài ÍT NHẤT 20 CÂU cho Day {day_selected}. Phía dưới tạo 15 câu hỏi trắc nghiệm.")
                    st.markdown(res.text)

        with d_t5:
            st.subheader("Bài tập Viết Business (>= 100 từ)")
            daily_essay = st.text_area("Bài làm của bạn:", height=180, key=f"daily_write_in_{day_selected}")
            
            if st.button("Chấm điểm & Nộp bài", key=f"btn_d_score_write_{day_selected}"):
                if len(daily_essay.split()) < 100:
                    st.warning("Vui lòng viết đủ tối thiểu 100 từ!")
                else:
                    with st.spinner("AI đang chấm điểm..."):
                        res = model.generate_content(f"Chấm điểm bài viết Day {day_selected}:\n{daily_essay}\n\nYêu cầu: Sửa từng lỗi sai, Chấm điểm CEFR, và Viết 1 bài mẫu xuất sắc.")
                        st.markdown(res.text)
                        
                        safe_save("lesson_progress", {
                            "day_number": day_selected,
                            "skill": "Writing",
                            "user_submission": daily_essay,
                            "ai_feedback": res.text
                        })
                        safe_save("error_logs", {
                            "skill": "Writing",
                            "lesson": f"Day {day_selected}",
                            "original": daily_essay[:100] + "...",
                            "corrected": "Xem chi tiết phản hồi AI",
                            "reason": "Phân tích ngữ pháp & Business Tone"
                        })
                        st.success(f"✅ Đã lưu tiến độ Day {day_selected} vào hệ thống!")

        with d_t6:
            st.subheader("Luyện Nói Tương Tác")
            daily_audio = st.audio_input("Ghi âm câu trả lời:")
            if daily_audio and st.button("Phân tích bài Nói", key=f"btn_d_score_speak_{day_selected}"):
                with st.spinner("AI đang phân tích..."):
                    audio_bytes = daily_audio.read()
                    res = model.generate_content([
                        {"mime_type": "audio/wav", "data": audio_bytes},
                        "Chuyển giọng nói thành text, phân tích phát âm và ngữ pháp."
                    ])
                    st.markdown(res.text)

    # ==========================================
    # PHẦN 3: REVIEW SỔ TAY LỖI SAI & LỊCH SỬ HỌC
    # ==========================================
    elif app_mode == "3. Review Sổ Tay Lỗi Sai & Lịch Sử Học":
        st.title("📚 Lịch Sử Học Tập & Sổ Tay Review Lỗi Sai")
        
        tab_history, tab_errors = st.tabs(["📜 Tiến Độ Bài Học 30 Ngày", "❌ Sổ Tay Lỗi Sai"])
        
        with tab_history:
            history_data = safe_fetch("lesson_progress")
            if not history_data:
                st.info("Chưa có lịch sử bài học nào được lưu.")
            else:
                for item in history_data:
                    with st.expander(f"📅 Day {item.get('day_number')} - Skill: {item.get('skill')} ({item.get('created_at')[:10]})"):
                        st.write("**Bài làm của bạn:**")
                        st.caption(item.get("user_submission"))
                        st.write("**Nhận xét từ AI:**")
                        st.markdown(item.get("ai_feedback"))
                        
        with tab_errors:
            errors = safe_fetch("error_logs")
            if not errors:
                st.info("Chưa có lỗi sai nào trong hệ thống.")
            else:
                for idx, err in enumerate(errors):
                    with st.expander(f"❌ Lỗi {idx+1} [{err.get('skill')}] - {err.get('lesson')}"):
                        st.write(f"**Nội dung:** {err.get('original')}")
                        st.write(f"**Sửa chuẩn:** {err.get('corrected')}")
                        st.write(f"**Lý do sai:** {err.get('reason')}")

                st.divider()
                if st.button("Tạo bài tập Ôn lại các lỗi sai"):
                    with st.spinner("AI đang tạo bài tập ôn lại..."):
                        res = model.generate_content(f"Tạo 5 câu hỏi trắc nghiệm ôn tập dựa trên danh sách lỗi sau:\n{errors}")
                        st.markdown(res.text)