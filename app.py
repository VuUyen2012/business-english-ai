import streamlit as st
import google.generativeai as genai
from supabase import create_client
from gtts import gTTS
import io

# 1. Cấu hình trang Web & Secrets
st.set_page_config(page_title="Business English AI Assistant", layout="wide")
st.title("💼 Trợ Lý Business English 4 Kỹ Năng")

# Khởi tạo API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# 2. Giáo trình cố định (Syllabus - Không tự ý đổi)
SYLLABUS = {
    "Module 1: Professional Emails": ["1.1 Cold Pitching", "1.2 Handling Escalations", "1.3 Price Negotiation"],
    "Module 2: Business Meetings": ["2.1 Leading a Meeting", "2.2 Polite Interruptions", "2.3 Action Item Alignment"],
    "Module 3: Executive Writing": ["3.1 Quarterly Status Report", "3.2 Project Proposal Pitch"]
}
# Sidebar chọn bài học cố định & Review lỗi
st.sidebar.header("📚 Giáo Trình Cố Định")
selected_module = st.sidebar.selectbox("Chọn Module", list(SYLLABUS.keys()))
selected_lesson = st.sidebar.selectbox("Chọn Bài Học", SYLLABUS[selected_module])

tab1, tab2, tab3 = st.tabs(["🎙️ Luyện Nói & Nghe", "✍️ Luyện Viết (Writing)", "📜 Nhật Ký Sửa Lỗi (Review)"])

# TAB 1: LUYỆN NÓI VÀ NGHE (SPEECH TO TEXT & TTS)
with tab1:
    st.subheader(f"Role-play Listening & Speaking: {selected_lesson}")
    audio_val = st.audio_input("Nhấn mic để nói câu trả lời của bạn:")
    
    if audio_val:
        # Gửi voice trực tiếp vào Gemini để Transcription & Phân tích
        audio_bytes = audio_val.read()
        prompt = f"Bạn là giáo viên Business English. Học viên vừa nói câu hội thoại bài {selected_lesson}. " \
                 f"Hãy transcribe chính xác giọng nói, nhận xét lỗi sai ngữ pháp/giọng văn, và đưa ra câu nói chuẩn mực hơn."
        
        response = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_bytes}])
        st.write("🤖 **Đánh giá & Phản hồi từ AI:**")
        st.write(response.text)
        
        # Chuyển phản hồi thành Giọng Nói (TTS) để luyện Nghe
        tts = gTTS(text=response.text[:200], lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
# TAB 2: LUYỆN VIẾT & SỬA LỖI TỰ ĐỘNG LƯU DATABASE
with tab2:
    st.subheader(f"Sửa Bài Viết Business Writing: {selected_lesson}")
    user_text = st.text_area("Dán bài viết/email của bạn vào đây:", height=150)
    
    if st.button("Chấm Bài & Sửa Lỗi"):
        prompt = f"Phân tích bài viết Business English này cho bài {selected_lesson}:\n{user_text}\n" \
                 f"Trả về kết quả gồm: 1. Bản sửa chuẩn (Corrected text) | 2. Giải thích lỗi sai & Từ vựng nâng cao."
        res = model.generate_content(prompt)
        st.markdown(res.text)
        
        # TỰ ĐỘNG LƯU VÀO DATABASE (Đảm bảo refresh không mất)
        supabase.table("error_logs").insert({
            "module_name": selected_lesson,
            "skill_type": "Writing",
            "user_input": user_text,
            "corrected_text": res.text[:300],
            "explanation": res.text
        }).execute()
        st.success("✅ Đã tự động lưu lỗi sai vào nhật ký học tập!")

# TAB 3: REVIEW LỊCH SỬ LỖI SAI (XEM LẠI KHI CẦN)
with tab3:
    st.subheader("📜 Danh Sách Lỗi Sai Đã Lưu Trong Quá Trình Học")
    data = supabase.table("error_logs").select("*").order("created_at", desc=True).execute()
    for item in data.data:
        with st.expander(f"Bài: {item['module_name']} | Kỹ năng: {item['skill_type']} ({item['created_at'][:10]})"):
            st.write(f"**Câu gốc của bạn:** {item['user_input']}")
            st.write(f"**AI Sửa & Giải thích:**\n{item['explanation']}")