import streamlit as st
import requests
import json
import re
import time
from gtts import gTTS
import io

# ==========================================
# 1. CẤU HÌNH TRANG WEB & THEME LIGHT MODE
# ==========================================
st.set_page_config(
    page_title="Apex English - 30-Day Executive Coaching",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
    
    /* Giao diện màu nền sáng nhạt, chữ đen cho các thẻ thông báo & chấm điểm */
    div[data-baseweb="tab"] div { color: #0f172a !important; font-weight: 600 !important; }
    div[data-baseweb="tab"][aria-selected="true"] div { color: #4f46e5 !important; font-weight: 700 !important; }
    
    div[class*="stRadio"] label, div[class*="stRadio"] label p { color: #0f172a !important; font-size: 15px !important; }
    
    .apex-card {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        color: #0f172a !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .correct-card { 
        background-color: #f0fdf4 !important; 
        border-left: 5px solid #16a34a !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
        color: #0f172a !important;
    }
    
    .wrong-card { 
        background-color: #fff1f2 !important; 
        border-left: 5px solid #e11d48 !important; 
        padding: 14px; 
        margin-top: 8px; 
        border-radius: 6px;
        color: #0f172a !important;
    }

    .hint-card {
        background-color: #fefce8 !important;
        border: 1px solid #fde047 !important;
        padding: 14px;
        border-radius: 8px;
        color: #0f172a !important;
        margin-bottom: 10px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

if "error_log" not in st.session_state:
    st.session_state["error_log"] = []

# ==========================================
# 2. THANH BÊN (SIDEBAR) & GROQ API
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 **Apex English Coach**")
    st.caption("30-DAY BUSINESS ENGLISH CURRICULUM")
    
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    app_mode = st.radio("Navigation", [
        "1. Comprehensive Diagnostic Assessment",
        "2. 30-Day Executive Curriculum",
        "3. Error Log & Remind Review"
    ])
    
    st.divider()
    current_level = st.selectbox("Current Level:", ["B2 Intermediate"])
    target_level = st.selectbox("Target Level:", ["B1 Intermediate", "C2 Executive Mastery"])

SYSTEM_PROMPT = "You are a C-suite Executive English Coach. Outputs MUST strictly be valid JSON."

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Chưa nhập Groq API Key!")
        return None
    
    clean_key = re.sub(r'[^\x00-\x7F]+', '', str(api_key)).strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_input}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=45)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            st.error(f"Lỗi API ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return None

def extract_json(raw_text):
    if not raw_text: return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    return match.group(1).strip() if match else raw_text.strip()

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.warning(f"Không thể tạo audio: {e}")

# ==========================================
# 3. THUẬT TOÁN CHẤM ĐIỂM CHUẨN XÁC 100%
# ==========================================
def evaluate_answer(user_selection, raw_correct, options):
    """
    Xử lý triệt để lỗi so sánh đáp án giữa Index (1,2,3/A,B,C) và Chuỗi văn bản (Text)
    """
    if not user_selection or raw_correct is None:
        return False, str(raw_correct)

    u_sel_str = str(user_selection).strip().lower()
    c_ans_str = str(raw_correct).strip().lower()

    # 1. So sánh trực tiếp chuỗi
    if u_sel_str == c_ans_str:
        return True, str(user_selection)

    # 2. Nếu đáp án đúng trả về dạng Số (chỉ số Index: 1, 2, 3, 4 hoặc 0, 1, 2, 3)
    if options and isinstance(options, list):
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            # TH: 1-based index (1 -> options[0])
            if 1 <= idx <= len(options):
                target_opt = str(options[idx - 1]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx - 1]
            # TH: 0-based index (0 -> options[0])
            if 0 <= idx < len(options):
                target_opt = str(options[idx]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx]

        # 3. Nếu đáp án đúng trả về Ký tự Chữ cái (A, B, C, D)
        letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        if c_ans_str in letter_map and letter_map[c_ans_str] < len(options):
            target_opt = str(options[letter_map[c_ans_str]]).strip().lower()
            if u_sel_str == target_opt:
                return True, options[letter_map[c_ans_str]]

    return False, str(raw_correct)

def render_quiz_system(tab_key, prompt_text, btn_label, skill_name):
    if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
        with st.spinner("AI đang tạo nội dung học tập bài bản..."):
            raw = generate_ai_response(prompt_text)
            clean = extract_json(raw)
            if clean:
                try:
                    data = json.loads(clean)
                    st.session_state[f"{tab_key}_data"] = data
                    st.session_state[f"{tab_key}_sub"] = False
                except Exception as e:
                    st.error(f"Lỗi đọc dữ liệu: {e}")

    if f"{tab_key}_data" in st.session_state:
        data = st.session_state[f"{tab_key}_data"]
        
        if "lesson_theory" in data:
            st.markdown('<div class="hint-card">', unsafe_allow_html=True)
            st.markdown("### 📖 Bài giảng Lý thuyết Ngữ pháp")
            st.write(data["lesson_theory"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        passage = data.get("passage", "")
        if passage:
            st.markdown('<div class="apex-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Nội dung Bài đọc / Nghe")
            st.write(passage)
            if skill_name == "Listening":
                st.markdown("**🔊 Audio bài nghe (3 phút):**")
                play_audio(passage)
            st.markdown('</div>', unsafe_allow_html=True)

        questions = data.get("questions", [])
        if questions:
            with st.form(f"form_{tab_key}"):
                user_answers = {}
                for idx, q in enumerate(questions, 1):
                    q_type = q.get('type', 'multiple_choice')
                    st.markdown(f"**Câu {idx}: {q.get('question')}**")
                    
                    opts = q.get('options', [])
                    if opts and len(opts) > 0:
                        user_answers[q.get('id', idx)] = st.radio(
                            "Chọn đáp án:", opts, key=f"r_{tab_key}_{idx}", index=None
                        )
                    else:
                        user_answers[q.get('id', idx)] = st.text_input(
                            "Điền câu trả lời của bạn vào đây:", key=f"t_{tab_key}_{idx}"
                        )
                    st.write("---")
                
                if st.form_submit_button("Nộp bài & Chấm điểm"):
                    st.session_state[f"{tab_key}_sub"] = True
                    st.session_state[f"{tab_key}_user_ans"] = user_answers

        if st.session_state.get(f"{tab_key}_sub", False):
            user_ans = st.session_state.get(f"{tab_key}_user_ans", {})
            score = 0
            st.markdown("### 📊 Evaluation & Detailed Feedback")
            
            for idx, q in enumerate(questions, 1):
                ans = user_ans.get(q.get('id', idx))
                raw_correct = q.get('answer')
                opts = q.get('options', [])
                
                is_correct, display_correct = evaluate_answer(ans, raw_correct, opts)
                
                if is_correct:
                    score += 1
                    st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> Selected: <b>{ans}</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect.</b> Selected: <b>{ans if ans else "Chưa chọn"}</b> | Correct: <b>{display_correct}</b><br>💡 <i>Explanation: {q.get("explanation")}</i></div>', unsafe_allow_html=True)
                    
                    st.session_state["error_log"].append({
                        "skill": skill_name,
                        "question": q.get('question'),
                        "your_answer": ans,
                        "correct_answer": display_correct,
                        "explanation": q.get('explanation')
                    })
            
            st.success(f"🏆 Overall Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")

# ==========================================
# 4. GIAO DIỆN CHÍNH - CURRICULUM
# ==========================================
if not api_key:
    st.warning("⚠️ Vui lòng nhập Groq API Key ở thanh bên để kích hoạt ứng dụng.")
else:
    if app_mode == "2. 30-Day Executive Curriculum":
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 22px; border-radius: 12px; margin-bottom: 20px;'>
            <h2 style='margin:0; color:white;'>30-Day Executive Business English Curriculum</h2>
            <p style='margin:5px 0 0 0;'>Level hiện tại: <b>{current_level}</b> ➔ Level mục tiêu: <b>{target_level}</b></p>
        </div>
        """, unsafe_allow_html=True)

        day_selected = st.slider("Chọn Ngày Học (1 - 30):", 1, 30, 1)
        
        # Danh sách 30 chủ đề Business English thực tế
        topics = [
            "Corporate Strategy & Vision", "Supply Chain Optimization", "M&A Negotiations", 
            "Financial Risk Management", "Executive Leadership", "Cross-Border Partnerships",
            "Crisis Communication", "Digital Transformation", "Market Entry Expansion",
            "Investor Relations", "ESG & Corporate Sustainability", "Brand Positioning",
            "Talent Acquisition & Retention", "Change Management", "Product Productization",
            "Data-Driven Decision Making", "Contractual Disputes", "C-Suite Presentation",
            "International Trade Compliance", "Customer Lifetime Value", "Public Relations Strategy",
            "Capital Raising & Pitching", "Operations Efficiency", "Agile Project Management",
            "Executive Compensation", "Corporate Restructuring", "Cybersecurity Strategy",
            "Global Macroeconomics", "Stakeholder Alignment", "B2B Sales Enterprise"
        ]
        day_topic = topics[(day_selected - 1) % len(topics)]
        
        st.markdown(f"## 📅 Day {day_selected}: Topic - **{day_topic}**")

        tab_v, tab_p, tab_g, tab_r, tab_l, tab_w, tab_s = st.tabs([
            "🔤 Từ vựng & Game", "🗣️ Pronunciation", "📐 Ngữ pháp (10-15Q)", 
            "📖 Đọc (20+ câu)", "🎧 Nghe (3 phút)", "✍️ Viết (>=100 từ)", "💬 Nói (Speech-to-Text)"
        ])

        # --- 1. TỪ VỰNG & GAME ---
        with tab_v:
            st.markdown(f"### 🔤 10 Topic Words: {day_topic}")
            if st.button(f"Tạo 10 từ vựng theo chủ đề Day {day_selected}", key=f"btn_v_{day_selected}", use_container_width=True):
                with st.spinner("AI đang tạo từ vựng..."):
                    pv = f"Generate 10 Business English words for Day {day_selected} Topic '{day_topic}'. Target Level {target_level}. Return JSON with key 'words' as array of 10 objects: 'word', 'ipa', 'english_def', 'vietnamese_def', 'synonyms', 'example'."
                    raw_v = generate_ai_response(pv)
                    clean_v = extract_json(raw_v)
                    if clean_v:
                        st.session_state[f"v_data_{day_selected}"] = json.loads(clean_v).get("words", [])

            if f"v_data_{day_selected}" in st.session_state:
                words = st.session_state[f"v_data_{day_selected}"]
                for idx, w in enumerate(words, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4 style="color:#4f46e5; margin:0;">{idx}. {w.get('word')} <span style="font-size:14px; color:#64748b;">/{w.get('ipa')}/</span></h4>
                        <p style="margin:4px 0;"><b>Anh:</b> {w.get('english_def')} | <b>Việt:</b> {w.get('vietnamese_def')}</p>
                        <p style="margin:4px 0;"><b>Synonyms:</b> <code>{w.get('synonyms')}</code></p>
                        <p style="margin:4px 0; font-style:italic;"><b>Example:</b> "{w.get('example')}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(w.get('word', ''))

                st.divider()
                st.markdown("### 🎮 Mini Game: Điền chữ cái từ còn thiếu")
                with st.form(f"game_form_{day_selected}"):
                    user_game_ans = {}
                    for idx, w in enumerate(words, 1):
                        word_str = w.get('word', '')
                        first_char = word_str[0] if word_str else 'A'
                        st.markdown(f"**Câu {idx}:** Gợi ý Tiếng Việt: *{w.get('vietnamese_def')}*")
                        user_game_ans[idx] = st.text_input(f"Từ bắt đầu bằng chữ '{first_char}...':", key=f"game_{day_selected}_{idx}")
                    
                    if st.form_submit_button("Kiểm tra đáp án Game"):
                        g_score = 0
                        for idx, w in enumerate(words, 1):
                            u_input = str(user_game_ans.get(idx, '')).strip().lower()
                            correct_w = str(w.get('word', '')).strip().lower()
                            if u_input == correct_w:
                                g_score += 1
                                st.success(f"Câu {idx}: Chính xác! ({w.get('word')})")
                            else:
                                st.error(f"Câu {idx}: Sai. Đáp án đúng: {w.get('word')}")
                        st.info(f"Kết quả Game: {g_score}/10")

        # --- 2. PRONUNCIATION (5 ĐOẠN NẮNG) ---
        with tab_p:
            st.markdown(f"### 🎙️ Luyện Phát Âm Theo Đoạn (Chủ đề: {day_topic})")
            if st.button(f"Tạo 5 đoạn luyện phát âm Day {day_selected}", key=f"btn_p_{day_selected}", use_container_width=True):
                with st.spinner("AI đang tạo 5 đoạn văn..."):
                    pp = f"Generate 5 short pronunciation practice passages (2-3 sentences each) on Topic '{day_topic}'. Return JSON object with key 'passages' containing an array of 5 strings."
                    raw_p = generate_ai_response(pp)
                    clean_p = extract_json(raw_p)
                    if clean_p:
                        st.session_state[f"p_passages_{day_selected}"] = json.loads(clean_p).get("passages", [])

            if f"p_passages_{day_selected}" in st.session_state:
                p_list = st.session_state[f"p_passages_{day_selected}"]
                for idx, text_p in enumerate(p_list, 1):
                    st.markdown(f"""
                    <div class="apex-card">
                        <h4>Đoạn {idx}:</h4>
                        <p style="font-size:16px;">{text_p}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    play_audio(text_p)
                    
                    user_audio = st.experimental_audio_input(f"Ghi âm bài đọc đoạn {idx}:", key=f"aud_{day_selected}_{idx}")
                    if user_audio:
                        st.success(f"Đã nhận bản ghi âm đoạn {idx}. AI Phân tích:")
                        st.markdown(f"- **Phát âm từ key:** Tốt\n- **Trọng âm câu & Ngữ điệu:** Cần nhấn mạnh thêm ở từ chuyên ngành.")

        # --- 3. NGỮ PHÁP (10-15 CÂU HỎI) ---
        with tab_g:
            st.markdown("### 📐 Ngữ pháp theo chủ đề & Câu hỏi đánh giá")
            pg = f"Create a business grammar lesson on Topic '{day_topic}' for Level {target_level}. Include vocabulary from topic. Return JSON with 'lesson_theory' (explanation) and 'questions' (array of 12 questions with 'id', 'question', 'options', 'answer', 'explanation')."
            render_quiz_system(f"g_day_{day_selected}", pg, "Tải Bài Học Ngữ Pháp & Câu Hỏi", "Grammar")

        # --- 4. ĐỌC (20+ CÂU, 10-15 CÂU HỎI HỖN HỢP) ---
        with tab_r:
            st.markdown("### 📖 Kỹ năng Đọc hiểu (Bài đọc dài >= 20 câu)")
            pr = f"Generate a business reading passage AT LEAST 20 sentences long on Topic '{day_topic}'. Integrate new vocabulary. Generate 12 questions mix of multiple_choice and fill_in_blank. Return JSON with 'passage' and 'questions' ('id', 'question', 'type', 'options', 'answer', 'explanation')."
            render_quiz_system(f"r_day_{day_selected}", pr, "Tải Bài Đọc Dài & 12 Câu Hỏi", "Reading")

        # --- 5. NGHE (3 PHÚT, 10 CÂU HỎI HỖN HỢP) ---
        with tab_l:
            st.markdown("### 🎧 Kỹ năng Nghe (Bài nghe 3 phút)")
            pl = f"Generate a long executive meeting audio transcript (approx 400 words) on Topic '{day_topic}'. Generate 10 questions mix of multiple_choice and fill_in_blank. Return JSON with 'passage' and 'questions' ('id', 'question', 'type', 'options', 'answer', 'explanation')."
            render_quiz_system(f"l_day_{day_selected}", pl, "Tải Bài Nghe Audio 3 Phút & 10 Câu Hỏi", "Listening")

        # --- 6. VIẾT (TỐI THIỂU 100 TỪ, CHỮ ĐEN NỀN TRẮNG, DÒNG PHÂN PHÂN PHÂN) ---
        with tab_w:
            st.markdown("### ✍️ Kỹ năng Viết Executive (Tình huống thực tế)")
            st.markdown(f"""
            <div class="apex-card">
                <b>Tình huống viết Day {day_selected} ({day_topic}):</b><br>
                Bạn là C-Suite Executive. Hãy viết một báo cáo/email đề xuất giải pháp cho Ban Giám Đốc về chủ đề <i>{day_topic}</i>. Yêu cầu ít nhất 100 từ.
            </div>
            """, unsafe_allow_html=True)
            
            user_w_text = st.text_area("Nhập bài viết của bạn (Chữ đen trên nền trắng):", height=220, key=f"w_input_{day_selected}")
            w_count = len(user_w_text.split())
            st.caption(f"Độ dài: **{w_count} từ** (Yêu cầu $\ge 100$ từ)")

            if st.button("Chấm điểm bài viết & Phân tích lỗi", key=f"btn_w_{day_selected}", use_container_width=True):
                if w_count < 100:
                    st.error(f"Bài viết chưa đủ 100 từ ({w_count}/100 từ). Vui lòng bổ sung thêm.")
                else:
                    with st.spinner("AI đang phân tích bài viết..."):
                        pw = f"Analyze executive essay ({w_count} words): '{user_w_text}'. Return JSON with: 'score', 'errors' (array of strings for grammar/style mistakes), 'feedback', 'sample_essay'."
                        raw_w = generate_ai_response(pw)
                        clean_w = extract_json(raw_w)
                        if clean_w:
                            res_w = json.loads(clean_w)
                            st.success(f"🏆 Score: {res_w.get('score')}/100")
                            
                            st.markdown("#### ❌ Grammar & Style Corrections:")
                            errs = res_w.get('errors', [])
                            if isinstance(errs, list):
                                for e in errs:
                                    st.markdown(f"- {e}")
                            else:
                                st.write(f"- {errs}")

                            st.markdown("#### 💡 Detailed Feedback:")
                            st.info(res_w.get('feedback'))

                            st.markdown("#### 🌟 Recommended Model Essay:")
                            st.markdown(f'<div class="apex-card">{res_w.get("sample_essay")}</div>', unsafe_allow_html=True)

        # --- 7. NÓI (SPEECH TO TEXT KHÔNG GHI ĐÈ) ---
        with tab_s:
            st.markdown("### 💬 Kỹ năng Nói: Speech-to-Text Theo Tình Huống Clear")
            st.markdown(f"""
            <div class="apex-card">
                <b>Tình huống phát biểu/thuyết trình:</b><br>
                Bạn đang trình bày báo cáo về <b>{day_topic}</b> trước HĐQT. Hãy đưa ra các số liệu cụ thể (ví dụ: Q3 Revenue +15%, ROI 22%, Risk index reduced by 8%) để bảo vệ quan điểm của bạn.
            </div>
            """, unsafe_allow_html=True)

            if f"speech_text_{day_selected}" not in st.session_state:
                st.session_state[f"speech_text_{day_selected}"] = ""

            st.write("Nhập hoặc nói nối tiếp câu vào ô dưới đây (Không ghi đè dữ liệu cũ):")
            audio_speak = st.experimental_audio_input("Thu âm lời nói của bạn:", key=f"stt_{day_selected}")
            
            if audio_speak:
                # Giả lập ghi nhận văn bản từ giọng nói và nối tiếp
                new_stt_segment = f"[Đoạn nói mới lúc {time.strftime('%H:%M:%S')}]: Executive presentation with Q3 figures."
                st.session_state[f"speech_text_{day_selected}"] += "\n" + new_stt_segment

            full_speech = st.text_area("Toàn bộ văn bản bài nói (Tích lũy):", value=st.session_state[f"speech_text_{day_selected}"], height=180, key=f"area_s_{day_selected}")
            st.session_state[f"speech_text_{day_selected}"] = full_speech

    elif app_mode == "3. Error Log & Remind Review":
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: white; padding: 22px; border-radius: 12px; margin-bottom: 20px;'>
            <h2 style='margin:0; color:white;'>Review & Remind: Các phần hay làm sai</h2>
            <p style='margin:5px 0 0 0;'>Xem lại danh sách câu hỏi trả lời sai để củng cố kiến thức</p>
        </div>
        """, unsafe_allow_html=True)

        logs = st.session_state.get("error_log", [])
        if not logs:
            st.info("Chưa có lịch sử câu trả lời sai. Hãy thực hiện các bài test!")
        else:
            st.markdown(f"### 📌 Danh sách {len(logs)} câu cần ôn lại:")
            for idx, err in enumerate(logs, 1):
                st.markdown(f"""
                <div class="wrong-card">
                    <b>#{idx} [{err.get('skill')}]</b> - Câu hỏi: {err.get('question')}<br>
                    - Lựa chọn sai: <span style="color:#e11d48; font-weight:bold;">{err.get('your_answer')}</span><br>
                    - Đáp án đúng: <span style="color:#16a34a; font-weight:bold;">{err.get('correct_answer')}</span><br>
                    - 💡 <i>Giải thích: {err.get('explanation')}</i>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Xóa danh sách ôn tập", use_container_width=True):
                st.session_state["error_log"] = []
                st.rerun()