import streamlit as st
import requests
import json
import time
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

def get_user_current_level():
    results = safe_fetch("placement_results")
    if results and len(results) > 0:
        latest = results[0]
        return latest.get("overall_level", "B1 Intermediate")
    return "Chưa kiểm tra (Mặc định: B1 Intermediate)"

# ==========================================
# 3. HÀM PHÁT ÂM TIẾNG ANH (BROWSER SPEECH API)
# ==========================================
def play_audio_html(text_to_speak):
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
    current_lvl = get_user_current_level()
    if supabase:
        st.success("Supabase: Đã kết nối")
    else:
        st.warning("Supabase: Chưa kết nối (Chạy tạm thời)")
    st.info(f"🎯 **Level CEFR Hiện Tại:**\n\n### `{current_lvl}`")

# ==========================================
# 5. CẤU HÌNH AI THUẦN REST HTTP (CHỐNG CRASH / 404 / 429)
# ==========================================
SYSTEM_PROMPT = """
Bạn là Giảng viên Chuyên gia Business English Cao cấp.
Quy tắc giảng dạy:
1. Luôn chấm điểm chính xác các kỹ năng theo tiêu chí CEFR (A2, B1, B2, C1, C2).
2. Khi cá nhân hóa bài học, hãy bám sát chính xác trình độ mục tiêu của học viên.
3. Khi học viên làm bài Viết (>=100 từ): Hãy sửa lỗi theo chuẩn: [Câu gốc] -> [Câu sửa] -> [Lý do] và BẮT BUỘC cung cấp 1 bài mẫu (Model Answer) chuyên nghiệp đúng trình độ.
"""

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Chưa nhập Gemini API Key!")
        return None

    # Chuyển đổi dữ liệu sang text đơn giản
    if isinstance(prompt_input, str):
        prompt_text = prompt_input
    elif isinstance(prompt_input, list):
        prompt_text = " ".join([str(x) for x in prompt_input if isinstance(x, str)])
    else:
        prompt_text = str(prompt_input)

    full_text = f"{SYSTEM_PROMPT}\n\nYêu cầu: {prompt_text}"

    # Danh sách endpoint chạy thử lần lượt nếu bị 404
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    ]

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": full_text}]
        }]
    }

    for url in endpoints:
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            elif res.status_code == 429:
                st.error("⏳ API Key Free bị vượt giới hạn lượt gọi (Quota). Vui lòng đợi 30 giây rồi bấm lại!")
                return None
            elif res.status_code == 404:
                continue # Thử endpoint tiếp theo trong danh sách
            else:
                st.error(f"Lỗi API ({res.status_code}): {res.text}")
                return None
        except Exception as err:
            st.error(f"Lỗi kết nối mạng: {str(err)}")
            return None

    st.error("Không thể kết nối đến bất kỳ Model Gemini nào với API Key hiện tại. Vui lòng kiểm tra lại Key trên Google AI Studio.")
    return None

# ==========================================
# 6. GIAO DIỆN CHÍNH
# ==========================================
if not api_key:
    st.warning("⚠️ Vui lòng cấu hình Gemini API Key ở thanh bên (Sidebar) để bắt đầu!")
else:
    # PHẦN 1: PLACEMENT TEST
    if app_mode == "1. Đánh giá đầu vào (Placement Test)":
        st.title("📋 Bài Kiểm Tra Đánh Giá Đầu Vào Comprehensive")
        
        current_lvl = get_user_current_level()
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-bottom: 20px;">
            <h4 style="margin:0; color: #1E88E5;">🏆 Trình độ CEFR Đã Ghi Nhận: <b>{current_lvl}</b></h4>
            <p style="margin:5px 0 0 0; font-size: 14px; color: #555;">Kết quả đánh giá này được dùng để cá nhân hóa toàn bộ Giáo trình 30 ngày của bạn.</p>
        </div>
        """, unsafe_allow_html=True)

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "1. Từ vựng (15 Qs)", "2. Ngữ pháp (15 Qs)", "3. Đọc hiểu (20 câu)", 
            "4. Nghe hiểu (10 Qs)", "5. Viết & Đánh giá CEFR", "6. Nói (3 Topics)"
        ])

        with t1:
            st.subheader("Kiểm tra Từ vựng (15 câu hỏi)")
            if st.button("Tạo đề Từ vựng", key="btn_p_vocab"):
                with st.spinner("AI đang tạo đề..."):
                    res_text = generate_ai_response("Tạo 15 câu hỏi trắc nghiệm từ vựng Business English (phân bổ từ A2 đến C1) kèm đáp án ẩn bên dưới.")
                    if res_text:
                        st.markdown(res_text)

        with t2:
            st.subheader("Kiểm tra Ngữ pháp (15 câu hỏi)")
            if st.button("Tạo đề Ngữ pháp", key="btn_p_gram"):
                with st.spinner("AI đang tạo đề..."):
                    res_text = generate_ai_response("Tạo 15 câu hỏi trắc nghiệm ngữ pháp Business English kèm đáp án ẩn bên dưới.")
                    if res_text:
                        st.markdown(res_text)

        with t3:
            st.subheader("Kiểm tra Đọc hiểu (Reading)")
            if st.button("Tạo bài Đọc hiểu", key="btn_p_read"):
                with st.spinner("AI đang khởi tạo đoạn văn 20 câu..."):
                    res_text = generate_ai_response("Viết 1 đoạn văn chủ đề Business Strategy dài ÍT NHẤT 20 CÂU. Phía dưới đưa ra 15 câu hỏi trắc nghiệm đọc hiểu.")
                    if res_text:
                        st.markdown(res_text)

        with t4:
            st.subheader("Kiểm tra Nghe hiểu (Listening)")
            if st.button("Tạo bài Nghe & Audio", key="btn_p_listen"):
                with st.spinner("AI đang tạo kịch bản nghe..."):
                    script_text = generate_ai_response("Viết 1 đoạn hội thoại đàm phán hợp đồng tiếng Anh dài 15-20 câu.")
                    if script_text:
                        st.markdown(script_text)
                        play_audio_html(script_text)
                        st.markdown("---")
                        qs_text = generate_ai_response(f"Dựa vào bài nghe sau, tạo 10 câu hỏi trắc nghiệm:\n{script_text}")
                        if qs_text:
                            st.markdown(qs_text)

        with t5:
            st.subheader("Kiểm tra Viết (Writing & Chấm điểm Level CEFR)")
            essay_text = st.text_area("Nhập bài viết của bạn (Tối thiểu 100 từ):", height=200, key="p_essay")
            
            if st.button("Chấm điểm & Cập nhật Level CEFR", key="btn_p_score_write"):
                if len(essay_text.split()) < 100:
                    st.warning(f"Bài viết hiện tại mới có {len(essay_text.split())} từ. Vui lòng viết đủ 100 từ!")
                else:
                    with st.spinner("AI đang phân tích và xếp cấp độ CEFR..."):
                        prompt_eval = f"""
                        Chấm điểm bài viết sau để xác định level CEFR:
                        {essay_text}
                        
                        Yêu cầu cấu trúc phản hồi BẮT BUỘC:
                        ---
                        ### 🎖️ BẢNG TỔNG KẾT ĐÁNH GIÁ CEFR
                        - **Mức CEFR Tổng:** [Chỉ chọn 1 trong: A2 Elementary / B1 Intermediate / B2 Upper-Intermediate / C1 Advanced / C2 Proficient]
                        - **Từ vựng (Vocabulary):** [Nhận xét & Mức CEFR]
                        - **Ngữ pháp (Grammar):** [Nhận xét & Mức CEFR]
                        - **Độ mạch lạc (Coherence):** [Nhận xét & Mức CEFR]
                        ---
                        ### 🔍 CHI TIẾT LỖI SAI VÀ SỬA CÂU
                        (Sửa chi tiết từng câu sai)
                        
                        ---
                        ### ✍️ BÀI VIẾT MẪU ĐẠT CHUẨN MỤC TIÊU (MODEL ANSWER)
                        (Viết 1 bài mẫu hoàn chỉnh >=150 từ)

                        Dòng ĐẦU TIÊN của phản hồi phải ghi chính xác: [LEVEL: <Tên_Mức_CEFR>]
                        Ví dụ: [LEVEL: B2 Upper-Intermediate]
                        """
                        res_text = generate_ai_response(prompt_eval)
                        if res_text:
                            st.markdown(res_text)
                            
                            detected_level = "B1 Intermediate"
                            if "[LEVEL:" in res_text:
                                try:
                                    detected_level = res_text.split("[LEVEL:")[1].split("]")[0].strip()
                                except:
                                    detected_level = "B1 Intermediate"

                            safe_save("placement_results", {
                                "writing_feedback": res_text,
                                "overall_level": detected_level
                            })
                            st.balloons()
                            st.success(f"🎉 ĐÃ CẬP NHẬT TRÌNH ĐỘ THÀNH CÔNG: **{detected_level}**! Hãy chuyển sang Chế độ 2 để bắt đầu học.")

        with t6:
            st.subheader("Kiểm tra Nói (Speaking - 3 Topics)")
            st.info("Tính năng thu âm đang được hỗ trợ qua nhập liệu văn bản bài nói.")
            spoken_text = st.text_area("Nhập nội dung bài nói của bạn để AI chấm điểm:", height=150)
            if st.button("Chấm điểm bài Nói", key="btn_p_score_speak"):
                if spoken_text:
                    with st.spinner("AI đang phân tích bài nói..."):
                        res_text = generate_ai_response(f"Đánh giá bài nói sau về ngữ pháp, từ vựng và tiêu chuẩn CEFR:\n{spoken_text}")
                        if res_text:
                            st.markdown(res_text)

    # PHẦN 2: GIÁO TRÌNH 30 NGÀY
    elif app_mode == "2. Giáo trình 30 Ngày (Business English)":
        user_level = get_user_current_level()
        st.title("📚 Giáo Trình 30 Ngày - Business English")
        st.info(f"🎯 **Độ khó bài học hiện tại đang khóa theo trình độ:** **{user_level}**")
        
        day_selected = st.slider("Chọn ngày học:", 1, 30, 1)
        st.header(f"📌 Chi Tiết Bài Học: Day {day_selected} (Trình độ {user_level})")

        d_t1, d_t2, d_t3, d_t4, d_t5 = st.tabs([
            "📖 Từ vựng", "📝 Ngữ pháp", "🎧 Nghe", "📚 Đọc", "✍️ Viết (>=100 từ)"
        ])

        with d_t1:
            st.subheader(f"10 Từ Vựng Thương Mại (Level {user_level}) - Day {day_selected}")
            if st.button("Tải 10 từ vựng", key=f"btn_d_vocab_{day_selected}"):
                with st.spinner("Đang tải danh sách từ vựng cá nhân hóa..."):
                    prompt = f"Soạn 10 từ vựng Business English chuẩn trình độ {user_level} cho Day {day_selected}. Định dạng bảng: Từ tiếng Anh | Giải nghĩa EN | Giải nghĩa VI | Từ đồng nghĩa | Ví dụ câu thực tế."
                    res_text = generate_ai_response(prompt)
                    if res_text:
                        st.markdown(res_text)

        with d_t2:
            st.subheader(f"Ngữ pháp Thương Mại (Level {user_level})")
            if st.button("Tải bài học Ngữ pháp", key=f"btn_d_gram_{day_selected}"):
                with st.spinner("Đang tải lý thuyết..."):
                    prompt = f"Dạy 1 chủ đề Ngữ pháp Business English thiết kế riêng cho trình độ {user_level} (Day {day_selected}). Sau đó tạo 12 câu hỏi trắc nghiệm đánh giá kèm đáp án."
                    res_text = generate_ai_response(prompt)
                    if res_text:
                        st.markdown(res_text)

        with d_t3:
            st.subheader(f"Bài tập Nghe hiểu (Level {user_level})")
            if st.button("Tạo bài Nghe Day này", key=f"btn_d_listen_{day_selected}"):
                with st.spinner("Đang tạo kịch bản nghe..."):
                    prompt = f"Soạn 1 đoạn hội thoại công sở tiếng Anh chuẩn trình độ {user_level} cho Day {day_selected} (dài 15 câu)."
                    script_text = generate_ai_response(prompt)
                    if script_text:
                        st.markdown(script_text)
                        play_audio_html(script_text)

        with d_t4:
            st.subheader(f"Bài Đọc hiểu (Level {user_level} - Đoạn văn >= 20 câu)")
            if st.button("Tải bài Đọc Day này", key=f"btn_d_read_{day_selected}"):
                with st.spinner("Đang khởi tạo đoạn văn..."):
                    prompt = f"Viết 1 bài báo/văn bản Business tiếng Anh dành cho trình độ {user_level} dài ÍT NHẤT 20 CÂU cho Day {day_selected}. Phía dưới tạo 15 câu hỏi trắc nghiệm."
                    res_text = generate_ai_response(prompt)
                    if res_text:
                        st.markdown(res_text)

        with d_t5:
            st.subheader(f"Bài tập Viết Business (>= 100 từ - Tiêu chuẩn {user_level})")
            daily_essay = st.text_area("Bài làm của bạn:", height=180, key=f"daily_write_in_{day_selected}")
            
            if st.button("Chấm điểm & Nộp bài", key=f"btn_d_score_write_{day_selected}"):
                if len(daily_essay.split()) < 100:
                    st.warning("Vui lòng viết đủ tối thiểu 100 từ!")
                else:
                    with st.spinner("AI đang chấm điểm theo tiêu chí level..."):
                        prompt = f"""
                        Học viên có trình độ hiện tại là {user_level}. Hãy chấm điểm bài viết Day {day_selected}:
                        {daily_essay}
                        
                        Yêu cầu:
                        1. Nhận xét bài viết đã đạt chuẩn {user_level} chưa.
                        2. Sửa từng lỗi sai chi tiết.
                        3. Cung cấp 1 bài viết mẫu (Model Answer) đạt chuẩn mốc trình độ TIẾP THEO cao hơn 1 bậc.
                        """
                        res_text = generate_ai_response(prompt)
                        if res_text:
                            st.markdown(res_text)
                            
                            safe_save("lesson_progress", {
                                "day_number": day_selected,
                                "skill": f"Writing ({user_level})",
                                "user_submission": daily_essay,
                                "ai_feedback": res_text
                            })
                            safe_save("error_logs", {
                                "skill": "Writing",
                                "lesson": f"Day {day_selected} ({user_level})",
                                "original": daily_essay[:100] + "...",
                                "corrected": "Xem chi tiết phản hồi AI",
                                "reason": "Phân tích ngữ pháp & Business Tone"
                            })
                            st.success(f"✅ Đã lưu tiến độ Day {day_selected} vào hệ thống!")

    # PHẦN 3: LỊCH SỬ HỌC
    elif app_mode == "3. Review Sổ Tay Lỗi Sai & Lịch Sử Học":
        st.title("📚 Lịch Sử Học Tập & Sổ Tay Review Lỗi Sai")
        tab_history, tab_errors = st.tabs(["📜 Tiến Độ Bài Học 30 Ngày", "❌ Sổ Tay Lỗi Sai"])
        
        with tab_history:
            history_data = safe_fetch("lesson_progress")
            if not history_data:
                st.info("Chưa có lịch sử bài học nào được lưu.")
            else:
                for item in history_data:
                    with st.expander(f"📅 Day {item.get('day_number')} - Skill: {item.get('skill')} ({item.get('created_at', '')[:10]})"):
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
                        res_text = generate_ai_response(f"Tạo 5 câu hỏi trắc nghiệm ôn tập dựa trên danh sách lỗi sau:\n{errors}")
                        if res_text:
                            st.markdown(res_text)