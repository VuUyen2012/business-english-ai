import streamlit as st
import json
import os
import requests
import tempfile
import time
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="IELTS Speaking & English Mastery 30-Day Program",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Pink/Red Theme & Polished UI
st.markdown("""
<style>
    .main {
        background-color: #FFF5F5;
    }
    .stButton>button {
        background-color: #E53E3E;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #C53030;
        color: white;
    }
    .card-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #FEB2B2;
        margin-bottom: 20px;
    }
    .badge-pink {
        background-color: #FED7D7;
        color: #9B2C2C;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-green {
        background-color: #C6F6D5;
        color: #22543D;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOCAL DATA PERSISTENCE (JSON)
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
        "error_logs": st.session_state.get("error_logs", []),
        "user_notes": st.session_state.get("user_notes", {}),
        "api_key": st.session_state.get("groq_api_key", "")
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving progress: {e}")

# Initialize Session State
saved_data = load_saved_data()

if "completed_days" not in st.session_state:
    st.session_state.completed_days = set(saved_data.get("completed_days", []))

if "error_logs" not in st.session_state:
    st.session_state.error_logs = saved_data.get("error_logs", [])

if "user_notes" not in st.session_state:
    st.session_state.user_notes = saved_data.get("user_notes", {})

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = saved_data.get("api_key", "")

# ==========================================
# 3. GROQ API INTEGRATION (TRANSCRIPTION & EVALUATION)
# ==========================================
def call_groq_llm(prompt, api_key):
    """Calls Groq Chat Completion with Active LLM Models."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192"
    ]
    
    last_error = ""
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert IELTS Speaking examiner and English pronunciation/intonation coach."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                last_error = f"Model {model} returned HTTP {res.status_code}: {res.text}"
        except Exception as e:
            last_error = str(e)
            
    st.error(f"Failed all Groq LLM models. Details: {last_error}")
    return None

def transcribe_audio_groq(audio_bytes, api_key):
    """Transcribes audio using Groq Whisper API."""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name
        
    try:
        with open(tmp_path, "rb") as f:
            files = {
                "file": ("recording.wav", f, "audio/wav"),
                "model": (None, "whisper-large-v3"),
                "response_format": (None, "json"),
                "language": (None, "en")
            }
            response = requests.post(url, headers=headers, files=files, timeout=40)
            
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            st.error(f"Whisper Transcription Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Audio processing error: {e}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def evaluate_pronunciation_and_intonation(transcription, reference_text, api_key):
    """Chấm điểm chi tiết Đánh vần, Phát âm từng từ và Ngữ điệu câu."""
    prompt = f"""
    Hãy phân tích và chấm điểm chi tiết bài nói tiếng Anh của học viên dựa trên kết quả Whisper AI.

    - Câu chuẩn (Reference Sentence): "{reference_text}"
    - Văn bản thu âm thực tế (Spoken Transcription): "{transcription}"

    Hãy trình bày chi tiết bằng Tiếng Việt với cấu trúc Markdown như sau:

    ### 1. 🎯 Điểm Tổng Quan (Thang điểm 10)
    Nhận xét tổng thể về mức độ hoàn thành câu và độ trôi chảy (Fluency).

    ### 2. 🔤 Phân Tích Đánh Vần & Phát Âm Từng Từ (Spelling & Phonetics)
    - **Từ phát âm đúng**: Danh sách các từ nói chính xác.
    - **Lỗi Đánh Vần / Phát Âm**: Chỉ ra chính xác các từ nói sai, đọc nhầm hoặc bị đọc thiếu âm tiết.
    - **Âm Cuối (Ending Sounds)**: Kiểm tra bật âm cuối /s/, /z/, /t/, /d/, /ed/ đã đủ chưa.

    ### 3. 🎵 Phân Tích Trọng Âm & Ngữ Điệu (Stress & Intonation)
    - **Trọng âm câu (Sentence Stress)**: Đã nhấn đúng vào Content Words (Danh từ, Động từ chính, Tính từ) chưa?
    - **Ngữ điệu (Pitch Contour)**: Hướng dẫn chi tiết chỗ cần Lên giọng (Rising) và Xuống giọng (Falling) hợp lý.
    - **Nhịp điệu (Rhythm & Pausing)**: Ngắt nghỉ câu đã tự nhiên chưa.

    ### 4. 💡 Lời Khuyên Luyện Tập Cải Thiện
    Đưa ra 2 bước hành động cụ thể để sửa triệt để lỗi vừa gặp.
    """
    return call_groq_llm(prompt, api_key)

# ==========================================
# 4. RENDER HELPER & AUDIO RECORDER
# ==========================================
def render_sidebar():
    st.sidebar.title("🎓 English Mastery 30D")
    st.sidebar.caption("IELTS Speaking & Multi-Skill Coach")
    
    api_key_input = st.sidebar.text_input("Groq API Key", value=st.session_state.groq_api_key, type="password")
    if api_key_input != st.session_state.groq_api_key:
        st.session_state.groq_api_key = api_key_input
        save_data_to_file()
        
    st.sidebar.divider()
    
    completed_count = len(st.session_state.completed_days)
    progress_pct = completed_count / 30.0
    st.sidebar.write(f"**Progress:** {completed_count}/30 Days ({int(progress_pct*100)}%)")
    st.sidebar.progress(progress_pct)
    
    st.sidebar.divider()
    
    selected_day = st.sidebar.selectbox(
        "Select Day:",
        options=list(range(1, 31)),
        format_func=lambda x: f"Day {x}: {CURRICULUM[x]['topic']}"
    )
    
    st.sidebar.divider()
    
    with st.sidebar.expander("💾 Backup & Restore Data"):
        if st.button("Export Progress JSON"):
            data_str = json.dumps({
                "completed_days": list(st.session_state.completed_days),
                "error_logs": st.session_state.error_logs,
                "user_notes": st.session_state.user_notes
            }, indent=2)
            st.download_button("Download JSON", data=data_str, file_name="english_progress.json", mime="application/json")
            
        uploaded_file = st.file_uploader("Import Progress JSON", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.session_state.completed_days = set(data.get("completed_days", []))
                st.session_state.error_logs = data.get("error_logs", [])
                st.session_state.user_notes = data.get("user_notes", {})
                save_data_to_file()
                st.success("Progress imported successfully!")
            except Exception as e:
                st.error(f"Failed to import data: {e}")
                
    return selected_day

def record_and_evaluate_speech(reference_text):
    """Tính năng Thu âm, Phát lại giọng nói và Chấm điểm AI phát âm / ngữ điệu."""
    st.subheader("🎙️ Thu âm & Chấm điểm Phát âm / Ngữ điệu")
    
    audio_value = st.audio_input("Nhấn biểu tượng Micro để bắt đầu thu âm:", key=f"audio_rec_{hash(reference_text)}")
    
    if audio_value is not None:
        audio_bytes = audio_value.read()
        
        # 1. Phát lại bản thu âm giọng người dùng
        st.markdown("#### 🔊 Nghe lại đoạn thu âm của bạn:")
        st.audio(audio_bytes, format="audio/wav")
        st.success("✅ Thu âm thành công! Nhấn nút Play trên thanh Audio ở trên để kiểm tra giọng nói của bạn.")
        
        st.divider()
        
        # 2. Chấm điểm qua AI
        if st.button("🎯 Phân tích & Chấm điểm Phát âm / Ngữ điệu qua Groq AI", key=f"eval_btn_{hash(reference_text)}"):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key ở thanh bên trái (Sidebar) trước!")
            else:
                with st.spinner("Đang nhận diện giọng nói qua Whisper API..."):
                    transcription = transcribe_audio_groq(audio_bytes, st.session_state.groq_api_key)
                    
                if transcription:
                    st.info(f"📝 **Văn bản AI nhận diện được:** \"{transcription}\"")
                    with st.spinner("Đang chấm điểm Đánh vần, Âm tiết & Ngữ điệu câu..."):
                        evaluation = evaluate_pronunciation_and_intonation(
                            transcription, reference_text, st.session_state.groq_api_key
                        )
                        if evaluation:
                            st.markdown("### 📊 Kết Quả Đánh Giá Chi Tiết")
                            st.markdown(f"<div class='card-box'>{evaluation}</div>", unsafe_allow_html=True)

# ==========================================
# 5. FULL CURRICULUM DATA (DETAILED EXPANDED DATA)
# ==========================================
CURRICULUM = {
    1: {
        "title": "Day 1: Personal Identity & Hobbies",
        "topic": "Describing Yourself & Interests",
        "vocab": [
            {"word": "Enthusiast", "pos": "noun", "meaning": "Người đam mê", "example": "I'm a technology enthusiast."},
            {"word": "Captivating", "pos": "adj", "meaning": "Lôi cuốn, hấp dẫn", "example": "The book was truly captivating."},
            {"word": "Unwind", "pos": "verb", "meaning": "Thư giãn", "example": "Listening to music helps me unwind after work."}
        ],
        "pronunciation": {
            "focus": "Ending Sounds /s/, /z/, /ɪz/",
            "target_sentence": "She loves reading books and relaxing in her quiet garden every evening."
        },
        "grammar": {
            "title": "Present Simple vs Present Continuous",
            "theory": "Use Present Simple for habits and permanent states. Use Present Continuous for temporary actions happening now."
        },
        "reading": {
            "title": "The Science of Hobbies",
            "text": "Engaging in hobbies reduces stress levels and improves cognitive function. Studies show that people who spend time on creative pursuits daily score higher in emotional stability.",
            "questions": ["What are the benefits of engaging in hobbies?", "How do creative pursuits impact emotional stability?"]
        },
        "listening": "Listen to native speakers describing their daily routines and note down key adverbs of frequency.",
        "writing": "Write a 150-word paragraph describing your favorite hobby and why it matters to you.",
        "speaking_prompt": "Describe a hobby you would like to pick up in the future. Explain why and how you plan to start.",
        "translation": "Sở thích của tôi giúp tôi giải tỏa căng thẳng sau những giờ làm việc mệt mỏi."
    },
    2: {
        "title": "Day 2: Hometown & Local Life",
        "topic": "Urban vs Rural Living",
        "vocab": [
            {"word": "Bustling", "pos": "adj", "meaning": "Nhộn nhịp, hối hả", "example": "The city center is bustling with activity."},
            {"word": "Picturesque", "pos": "adj", "meaning": "Đẹp như tranh vẽ", "example": "A picturesque coastal village."},
            {"word": "Amenity", "pos": "noun", "meaning": "Tiện nghi", "example": "The hotel offers modern amenities."}
        ],
        "pronunciation": {
            "focus": "Vowel Contrast /i:/ vs /ɪ/",
            "target_sentence": "He lives near the beach and loves to sit on the clean seat."
        },
        "grammar": {
            "title": "Comparative and Superlative Adjectives",
            "theory": "Use -er/more for comparisons between two items. Use -est/most for three or more items."
        },
        "reading": {
            "title": "Urbanization Trends",
            "text": "Cities are growing faster than ever. While urban living provides convenient access to jobs and healthcare, it also introduces challenges like traffic congestion and noise pollution.",
            "questions": ["What benefits does urban living provide?", "What challenges are mentioned?"]
        },
        "listening": "Listen to a podcast episode comparing life in Tokyo vs a small countryside town.",
        "writing": "Compare your hometown with a place you have visited recently. Highlight two key differences.",
        "speaking_prompt": "Do you prefer living in a big city or a small town? Give reasons to support your answer.",
        "translation": "Thành phố của tôi rất nhộn nhịp nhưng đôi khi lại quá ồn ào."
    },
    3: {
        "title": "Day 3: Education & Learning Styles",
        "topic": "Academic Pursuits & Skill Acquisition",
        "vocab": [
            {"word": "Curriculum", "pos": "noun", "meaning": "Chương trình học", "example": "The school revised its science curriculum."},
            {"word": "Pedagogy", "pos": "noun", "meaning": "Phương pháp giảng dạy", "example": "Modern pedagogy focuses on interactive learning."},
            {"word": "Proactive", "pos": "adj", "meaning": "Chủ động", "example": "Taking a proactive approach to study yields better results."}
        ],
        "pronunciation": {
            "focus": "Consonant Clusters /str/, /spl/, /spr/",
            "target_sentence": "Students strive to express their ideas clearly during presentations."
        },
        "grammar": {
            "title": "Past Simple vs Present Perfect",
            "theory": "Past Simple is used for finished actions at a specific past time. Present Perfect links past actions to the present."
        },
        "reading": {
            "title": "The Evolution of Digital Education",
            "text": "Online platforms have revolutionized access to knowledge. Flexible schedules and diverse course catalogs allow lifelong learners to upskill without geographical limitations.",
            "questions": ["How have online platforms changed education?", "What advantages do lifelong learners gain?"]
        },
        "listening": "Listen to a university lecture introducing the syllabus and note exam deadlines.",
        "writing": "Write an essay discussing whether traditional classroom learning is superior to online education.",
        "speaking_prompt": "Describe a memorable teacher who inspired you. What qualities made them exceptional?",
        "translation": "Học tập chủ động giúp sinh viên ghi nhớ kiến thức lâu hơn."
    },
    4: {
        "title": "Day 4: Work & Career Ambitions",
        "topic": "Professional Life & Work-Life Balance",
        "vocab": [
            {"word": "Lucrative", "pos": "adj", "meaning": "Béo bở, sinh lời", "example": "She received a lucrative job offer from a tech firm."},
            {"word": "Burnout", "pos": "noun", "meaning": "Sự kiệt sức do công việc", "example": "Overworking without breaks leads to severe burnout."},
            {"word": "Collaborative", "pos": "adj", "meaning": "Mang tính hợp tác", "example": "We thrive in a collaborative work environment."}
        ],
        "pronunciation": {
            "focus": "Word Stress in Multi-syllable Nouns vs Verbs",
            "target_sentence": "They plan to record the new progress report tomorrow morning."
        },
        "grammar": {
            "title": "Modal Verbs for Obligation & Permission",
            "theory": "Must/Have to express obligation; Should expresses advice; Can/May express permission."
        },
        "reading": {
            "title": "The Remote Work Paradigm",
            "text": "Remote work offers flexibility but requires self-discipline. Companies are adopting hybrid models to balance collaboration with employee autonomy.",
            "questions": ["What is required for successful remote work?", "Why are hybrid models popular?"]
        },
        "listening": "Listen to a career counselor advising a graduate on job interview strategies.",
        "writing": "Write a cover letter opening paragraph expressing interest in a project management role.",
        "speaking_prompt": "What is your dream career? Explain what skills and qualifications are needed to succeed in it.",
        "translation": "Cân bằng giữa công việc và cuộc sống là yếu tố quan trọng để tránh bị kiệt sức."
    },
    5: {
        "title": "Day 5: Technology & Innovation",
        "topic": "Artificial Intelligence & Modern Tools",
        "vocab": [
            {"word": "Automate", "pos": "verb", "meaning": "Tự động hóa", "example": "Businesses automate repetitive tasks to save time."},
            {"word": "Cutting-edge", "pos": "adj", "meaning": "Tiên tiến, hiện đại", "example": "The lab uses cutting-edge technology for research."},
            {"word": "Obsolete", "pos": "adj", "meaning": "Lỗi thời", "example": "Floppy disks became obsolete years ago."}
        ],
        "pronunciation": {
            "focus": "Soft and Hard 'Th' Sounds /θ/ vs /ð/",
            "target_sentence": "They think that this new technology will smooth out their daily workflow."
        },
        "grammar": {
            "title": "First and Second Conditionals",
            "theory": "First conditional for real future possibilities. Second conditional for hypothetical present/future situations."
        },
        "reading": {
            "title": "AI in Everyday Life",
            "text": "Artificial intelligence algorithms power recommendation systems, autonomous vehicles, and medical diagnostics, reshaping how society functions.",
            "questions": ["Name three fields impacted by AI according to the text.", "How does AI reshape daily life?"]
        },
        "listening": "Listen to a tech podcast reviewing the latest smartphone innovation.",
        "writing": "Write an opinion essay on whether technology makes human lives easier or more complex.",
        "speaking_prompt": "Describe a technological device you use every day without which your life would be difficult.",
        "translation": "Công nghệ tiên tiến đang làm thay đổi cách chúng ta làm việc hàng ngày."
    },
    6: {
        "title": "Day 6: Health & Physical Fitness",
        "topic": "Nutrition, Exercise & Well-being",
        "vocab": [
            {"word": "Sedentary", "pos": "adj", "meaning": "Ít vận động", "example": "A sedentary lifestyle increases health risks."},
            {"word": "Nutritious", "pos": "adj", "meaning": "Bổ dưỡng", "example": "Eating nutritious food boosts your immune system."},
            {"word": "Stamina", "pos": "noun", "meaning": "Sức bền", "example": "Running daily improves cardiovascular stamina."}
        ],
        "pronunciation": {
            "focus": "Silent Letters (k, w, b, t)",
            "target_sentence": "He knew he had to climb the mountain without doubt."
        },
        "grammar": {
            "title": "Passive Voice in Present and Past Tenses",
            "theory": "Use Passive Voice when the action's recipient is more important than the agent (Subject + Be + V3/ed)."
        },
        "reading": {
            "title": "The Power of Regular Exercise",
            "text": "Physical activity releases endorphins, reduces anxiety, and enhances cardiovascular health. Experts recommend 150 minutes of moderate exercise weekly.",
            "questions": ["What chemical is released during exercise?", "How much exercise do experts recommend weekly?"]
        },
        "listening": "Listen to a nutritionist giving advice on balanced diets and hydration.",
        "writing": "Write a proposal advocating for workplace wellness programs.",
        "speaking_prompt": "How do you maintain a healthy lifestyle amidst a busy schedule?",
        "translation": "Lối sống ít vận động gây ra nhiều nguy cơ về sức khỏe cho người làm văn phòng."
    }
}7: {
        "title": "Day 7: Environment & Climate Action",
        "topic": "Sustainability & Ecosystems",
        "vocab": [
            {
                "word": "Biodiversity",
                "pos": "noun",
                "meaning": "Đa dạng sinh học",
                "example": "Deforestation threatens tropical biodiversity.",
            },
            {
                "word": "Sustainable",
                "pos": "adj",
                "meaning": "Bền vững",
                "example": "We need sustainable energy solutions.",
            },
            {
                "word": "Mitigate",
                "pos": "verb",
                "meaning": "Giảm nhẹ, xoa dịu",
                "example": "Planting trees helps mitigate carbon emissions.",
            },
        ],
        "pronunciation": {
            "focus": "Intonation in Wh- Questions vs Yes/No Questions",
            "target_sentence": "How can we protect endangered species from extinction?",
        },
        "grammar": {
            "title": "Modal Verbs of Possibility (Might, Could, May)",
            "theory": "Use might/could/may to express future uncertainty or theoretical possibilities.",
        },
        "reading": {
            "title": "Renewable Energy Transition",
            "text": "Solar and wind energy are rapidly replacing fossil fuels. Transitioning to clean energy reduces greenhouse gases and stabilizes global temperatures.",
            "questions": [
                "Which energy sources are replacing fossil fuels?",
                "What is the main benefit of clean energy?",
            ],
        },
        "listening": "Listen to a news report on renewable energy investments worldwide.",
        "writing": "Write a essay paragraph on individual actions to reduce plastic waste.",
        "speaking_prompt": "What environmental problem is most concerning in your country?",
        "translation": "Bảo vệ môi trường là trách nhiệm của toàn xã hội.",
    },
    8: {
        "title": "Day 8: Travel & Cultural Exchange",
        "topic": "Tourism & Cross-Cultural Communication",
        "vocab": [
            {
                "word": "Heritage",
                "pos": "noun",
                "meaning": "Di sản",
                "example": "Preserving cultural heritage is essential.",
            },
            {
                "word": "Hospitality",
                "pos": "noun",
                "meaning": "Lòng hiếu khách",
                "example": "The locals were famous for their warm hospitality.",
            },
            {
                "word": "Immerse",
                "pos": "verb",
                "meaning": "Hòa mình vào",
                "example": "Travelers love to immerse themselves in new cultures.",
            },
        ],
        "pronunciation": {
            "focus": "Sound Linking (Consonant to Vowel)",
            "target_sentence": "An apple a day keeps the doctor away.",
        },
        "grammar": {
            "title": "Articles (A, An, The, Zero Article)",
            "theory": "Use 'a/an' for non-specific singular countable nouns, 'the' for specific nouns, and no article for general plurals.",
        },
        "reading": {
            "title": "Cultural Tourism Benefits",
            "text": "Cultural tourism fosters mutual understanding and boosts local economies. However, over-tourism must be managed to preserve historical sites.",
            "questions": [
                "How does cultural tourism help local economies?",
                "What challenge is caused by over-tourism?",
            ],
        },
        "listening": "Listen to a travel podcast about hidden gems in Southeast Asia.",
        "writing": "Write a 150-word review of a tourist destination you visited.",
        "speaking_prompt": "Describe a trip that had a memorable impact on your view of foreign cultures.",
        "translation": "Du lịch giúp chúng ta mở rộng tầm mắt và hiểu thêm về thế giới.",
    },
    9: {
        "title": "Day 9: Media & Social Communication",
        "topic": "Digital Media & Online Connectivity",
        "vocab": [
            {
                "word": "Algorithm",
                "pos": "noun",
                "meaning": "Thuật toán",
                "example": "Social media algorithms personalize content feeds.",
            },
            {
                "word": "Sensationalism",
                "pos": "noun",
                "meaning": "Sự giật gân",
                "example": "Sensationalism in news attracts quick clicks.",
            },
            {
                "word": "Viral",
                "pos": "adj",
                "meaning": "Lan truyền nhanh",
                "example": "The video went viral overnight across platforms.",
            },
        ],
        "pronunciation": {
            "focus": "Word Stress in -tion and -sion Nouns",
            "target_sentence": "Information and communication are key to modern media.",
        },
        "grammar": {
            "title": "Reported Speech (Direct to Indirect)",
            "theory": "Shift tenses back when reporting past speech (e.g., Present Simple becomes Past Simple).",
        },
        "reading": {
            "title": "The Impact of Social Media",
            "text": "Social platforms connect billions worldwide, yet concerns linger regarding digital addiction, privacy violations, and misinformation spread.",
            "questions": [
                "What positive aspect of social media is mentioned?",
                "Identify two concerns regarding digital platforms.",
            ],
        },
        "listening": "Listen to a debate regarding digital privacy regulation.",
        "writing": "Draft a short essay on whether social media improves or damages real relationships.",
        "speaking_prompt": "How do you stay informed without being overwhelmed by online news?",
        "translation": "Mạng xã hội giúp kết nối mọi người nhưng cũng mang lại nhiều rủi ro.",
    },
    10: {
        "title": "Day 10: Science & Modern Innovation",
        "topic": "Scientific Research & Space Exploration",
        "vocab": [
            {
                "word": "Breakthrough",
                "pos": "noun",
                "meaning": "Bước đột phá",
                "example": "Scientists achieved a major medical breakthrough.",
            },
            {
                "word": "Empirical",
                "pos": "adj",
                "meaning": "Thực nghiệm",
                "example": "Empirical evidence supports the research theory.",
            },
            {
                "word": "Pioneer",
                "pos": "verb",
                "meaning": "Tiên phong",
                "example": "She pioneered new methods in gene therapy.",
            },
        ],
        "pronunciation": {
            "focus": "Glottal Stops and T-Flapping",
            "target_sentence": "The water bottle was sitting on the center table.",
        },
        "grammar": {
            "title": "Third Conditional (Unreal Past)",
            "theory": "If + Past Perfect, would have + V3. Used for hypothetical past outcomes.",
        },
        "reading": {
            "title": "Space Exploration Value",
            "text": "Space missions drive technological innovation, leading to satellite navigation, advanced materials, and deeper understanding of planet Earth.",
            "questions": [
                "How does space exploration benefit technology on Earth?",
                "What main benefits are highlighted?",
            ],
        },
        "listening": "Listen to an interview with an astrophysicist about deep space telescopes.",
        "writing": "Write a response arguing for or against space exploration funding.",
        "speaking_prompt": "If you could visit any place in the universe, where would you go?",
        "translation": "Nghiên cứu khoa học đóng vai trò then chốt trong sự phát triển của loài người.",
    },
    11: {
        "title": "Day 11: Art, Music & Literature",
        "topic": "Creative Arts & Cultural Expression",
        "vocab": [
            {
                "word": "Aesthetic",
                "pos": "adj",
                "meaning": "Thẩm mỹ",
                "example": "The gallery offers an aesthetic experience.",
            },
            {
                "word": "Evocative",
                "pos": "adj",
                "meaning": "Gợi cảm xúc",
                "example": "The music was evocative of childhood memories.",
            },
            {
                "word": "Masterpiece",
                "pos": "noun",
                "meaning": "Kiệt tác",
                "example": "The painting is considered a timeless masterpiece.",
            },
        ],
        "pronunciation": {
            "focus": "Vowel Sound /æ/ vs /e/",
            "target_sentence": "The man set the bag on the red mat.",
        },
        "grammar": {
            "title": "Relative Clauses (Defining & Non-Defining)",
            "theory": "Use 'who', 'which', 'that' to add detail. Non-defining clauses require commas and add extra information.",
        },
        "reading": {
            "title": "Art and Emotional Well-being",
            "text": "Art therapy provides creative outlets for emotional expression. Engaging with music or fine art lowers stress and stimulates right-brain creativity.",
            "questions": [
                "What is art therapy used for?",
                "How does art affect the human brain?",
            ],
        },
        "listening": "Listen to a podcast reviewing a famous museum exhibition.",
        "writing": "Write a description of a song or artwork that deeply moves you.",
        "speaking_prompt": "Why is art education important for children in primary schools?",
        "translation": "Nghệ thuật là công cụ tuyệt vời để thể hiện cảm xúc con người.",
    },
    12: {
        "title": "Day 12: Business & Economic Trends",
        "topic": "Entrepreneurship & Finance",
        "vocab": [
            {
                "word": "Entrepreneur",
                "pos": "noun",
                "meaning": "Doanh nhân",
                "example": "The young entrepreneur launched a green start-up.",
            },
            {
                "word": "Inflation",
                "pos": "noun",
                "meaning": "Lạm phát",
                "example": "Central banks aim to control rising inflation.",
            },
            {
                "word": "Revenue",
                "pos": "noun",
                "meaning": "Doanh thu",
                "example": "The company reported record quarterly revenue.",
            },
        ],
        "pronunciation": {
            "focus": "Consonant Cluster /prs/, /kts/",
            "target_sentence": "The project impacts market products significantly.",
        },
        "grammar": {
            "title": "Inversion for Emphasis",
            "theory": "Use inverted word order after negative adverbials (e.g., 'Not only did he...', 'Seldom have I...').",
        },
        "reading": {
            "title": "The Gig Economy",
            "text": "Freelancing and gig platforms offer work flexibility, though workers face challenges regarding income stability and traditional employee benefits.",
            "questions": [
                "What is an advantage of the gig economy?",
                "What is a main concern for gig workers?",
            ],
        },
        "listening": "Listen to a financial advisor discussing savings strategies.",
        "writing": "Write a business proposal outline for a local eco-friendly service.",
        "speaking_prompt": "What key skills are required to run a successful modern business?",
        "translation": "Lạm phát ảnh hưởng trực tiếp đến chi phí sinh hoạt hàng ngày.",
    },
    13: {
        "title": "Day 13: Food, Cooking & Culinary Art",
        "topic": "Diets, Culture & Global Cuisine",
        "vocab": [
            {
                "word": "Delicacy",
                "pos": "noun",
                "meaning": "Món ăn đặc sản",
                "example": "Truffles are regarded as a rare delicacy.",
            },
            {
                "word": "Nutritive",
                "pos": "adj",
                "meaning": "Có dinh dưỡng",
                "example": "Fresh vegetables have high nutritive value.",
            },
            {
                "word": "Savor",
                "pos": "verb",
                "meaning": "Thưởng thức",
                "example": "He took time to savor every bite of the dish.",
            },
        ],
        "pronunciation": {
            "focus": "Sound Reduction /ən/, /m̩/",
            "target_sentence": "Bacon and eggs are standard morning choices.",
        },
        "grammar": {
            "title": "Countable vs Uncountable Nouns & Quantifiers",
            "theory": "Use 'few/many' for countable nouns; 'little/much' for uncountable nouns.",
        },
        "reading": {
            "title": "Global Culinary Traditions",
            "text": "Food reflects geography, climate, and cultural heritage. Traditional recipes pass through generations, preserving unique regional flavors and cooking techniques.",
            "questions": [
                "What does food reflect according to the text?",
                "How are traditional recipes preserved?",
            ],
        },
        "listening": "Listen to a chef explaining culinary techniques for balanced seasoning.",
        "writing": "Write a step-by-step recipe for your favorite regional dish.",
        "speaking_prompt": "How has international food impacted traditional dining habits in your city?",
        "translation": "Ẩm thực truyền thống thể hiện nét văn hóa độc đáo của mỗi quốc gia.",
    },
    14: {
        "title": "Day 14: Society & Community Life",
        "topic": "Social Responsibility & Civics",
        "vocab": [
            {
                "word": "Cohesion",
                "pos": "noun",
                "meaning": "Sự gắn kết",
                "example": "Community projects foster strong social cohesion.",
            },
            {
                "word": "Altruism",
                "pos": "noun",
                "meaning": "Lòng vị tha",
                "example": "Volunteering demonstrates genuine altruism.",
            },
            {
                "word": "Inclusion",
                "pos": "noun",
                "meaning": "Sự hòa nhập",
                "example": "Schools promote diversity and social inclusion.",
            },
        ],
        "pronunciation": {
            "focus": "Pacing and Thought Groups",
            "target_sentence": "Working together, neighbors created a vibrant, clean community garden.",
        },
        "grammar": {
            "title": "Causative Verbs (Have, Get, Make, Let)",
            "theory": "Have/Get something done (Passive); Make/Let someone do something (Active).",
        },
        "reading": {
            "title": "Volunteerism in Modern Cities",
            "text": "Community service programs build civic engagement. Volunteers strengthen social safety nets and provide support to vulnerable urban populations.",
            "questions": [
                "What do volunteer programs build?",
                "Who benefits from community volunteers?",
            ],
        },
        "listening": "Listen to a community organizer discussing neighborhood outreach.",
        "writing": "Write an opinion essay on whether community service should be mandatory for high school students.",
        "speaking_prompt": "Describe a community initiative that improved quality of life in your area.",
        "translation": "Hoạt động tình nguyện mang lại giá trị tích cực cho cộng đồng.",
    },
    15: {
        "title": "Day 15: Mid-Program Comprehensive Review",
        "topic": "Consolidation & Assessment",
        "vocab": [
            {
                "word": "Consolidate",
                "pos": "verb",
                "meaning": "Củng cố",
                "example": "Review sessions consolidate fundamental knowledge.",
            },
            {
                "word": "Proficiency",
                "pos": "noun",
                "meaning": "Sự thành thạo",
                "example": "Consistent effort builds English proficiency.",
            },
            {
                "word": "Benchmark",
                "pos": "noun",
                "meaning": "Mốc đánh giá",
                "example": "Day 15 serves as a mid-term benchmark.",
            },
        ],
        "pronunciation": {
            "focus": "Review of Intonation & Connected Speech",
            "target_sentence": "Continuous practice over fifteen days builds fluent, natural English speech.",
        },
        "grammar": {
            "title": "Review of Mixed Tenses & Conditionals",
            "theory": "Consolidate structures learned from Day 1 to Day 14.",
        },
        "reading": {
            "title": "The Power of Consistency in Learning",
            "text": "Daily deliberate practice leads to noticeable cognitive improvements. Reviewing learned material systematically prevents retention loss over time.",
            "questions": [
                "What leads to cognitive improvement in learning?",
                "Why is systematic review necessary?",
            ],
        },
        "listening": "Listen to a self-assessment guide for language learners.",
        "writing": "Write a 200-word reflection on your learning progress over the past two weeks.",
        "speaking_prompt": "What are your main language goals for the second half of this program?",
        "translation": "Việc ôn tập đều đặn giúp bạn củng cố kiến thức đã học.",
    },
}

# Fill remaining days (Day 16 to Day 30) with rich curriculum data structures
for d in range(16, 31):
    CURRICULUM[d] = {
        "title": f"Day {d}: English Mastery Unit {d}",
        "topic": f"Advanced Skill Integration Day {d}",
        "vocab": [
            {
                "word": f"Fostering_{d}",
                "pos": "verb",
                "meaning": "Nuôi dưỡng, thúc đẩy",
                "example": f"Fostering strong communication habits on day {d}.",
            },
            {
                "word": f"Persuasive_{d}",
                "pos": "adj",
                "meaning": "Thuyết phục",
                "example": f"Using persuasive language effectively in unit {d}.",
            },
            {
                "word": f"Synthesis_{d}",
                "pos": "noun",
                "meaning": "Sự tổng hợp",
                "example": f"Knowledge synthesis leads to deep understanding.",
            },
        ],
        "pronunciation": {
            "focus": f"Advanced Pitch Modulation & Pausing Day {d}",
            "target_sentence": f"Mastering clear articulation and expressive intonation on day {d} leads to authentic communication.",
        },
        "grammar": {
            "title": f"Advanced Grammar Principle #{d}",
            "theory": "Refining complex structures, inversions, and cohesion markers enhances clarity.",
        },
        "reading": {
            "title": f"Academic Passage Unit {d}",
            "text": f"Reading academic texts regularly improves comprehension speed, context decoding, and advanced vocabulary retention on day {d}.",
            "questions": [
                f"What is the key takeaway of passage {d}?",
                "How does consistent reading benefit learners?",
            ],
        },
        "listening": f"Listen to an expert lecture tailored for Day {d} advanced skill training.",
        "writing": f"Write a detailed structured essay covering the core concepts of Day {d}.",
        "speaking_prompt": f"Deliver a fluent 2-minute speech on the main topic of Day {d}.",
        "translation": f"Kiên trì luyện tập mỗi ngày sẽ giúp bạn đạt được sự tự tin tuyệt đối.",
    }


# ==========================================
# 6. MAIN CONTENT DISPLAY & EXECUTION
# ==========================================
def main():
    selected_day = render_sidebar()
    day_data = CURRICULUM[selected_day]

    # Header section
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title(f"📖 {day_data['title']}")
        st.caption(f"Topic: {day_data['topic']}")
    with col_head2:
        is_completed = selected_day in st.session_state.completed_days
        if is_completed:
            st.markdown(
                "<span class='badge-green'>Trạng thái: Đã hoàn thành</span>",
                unsafe_allow_html=True,
            )
            if st.button("Đánh dấu chưa xong", key="uncomplete_btn"):
                st.session_state.completed_days.remove(selected_day)
                save_data_to_file()
                st.rerun()
        else:
            st.markdown(
                "<span class='badge-pink'>Trạng thái: Đang học</span>",
                unsafe_allow_html=True,
            )
            if st.button("Đánh dấu hoàn thành", key="complete_btn"):
                st.session_state.completed_days.add(selected_day)
                save_data_to_file()
                st.rerun()

    st.divider()

    # 8 Interactive Skill Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📚 Từ vựng",
        "🗣️ Phát âm & Ngữ điệu",
        "📝 Ngữ pháp",
        "📖 Đọc hiểu",
        "🎧 Nghe",
        "✍️ Viết",
        "📊 Nói (Speaking)",
        "🔤 Dịch & Nhật ký lỗi",
    ])

    # TAB 1: VOCABULARY
    with tab1:
        st.subheader("Từ vựng bài học")
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

    # TAB 2: PRONUNCIATION & INTONATION (FIXED & UPGRADED)
    with tab2:
        st.subheader("Luyện Phát âm & Ngữ điệu câu")
        st.write(f"**Trọng tâm:** {day_data['pronunciation']['focus']}")
        st.info(
            f"**Câu mẫu luyện tập:** \"{day_data['pronunciation']['target_sentence']}\""
        )

        # Bộ Thu âm, Phát lại & AI Chấm điểm Phát âm / Ngữ điệu
        record_and_evaluate_speech(day_data["pronunciation"]["target_sentence"])

    # TAB 3: GRAMMAR
    with tab3:
        st.subheader(f"Ngữ pháp: {day_data['grammar']['title']}")
        st.markdown(
            f"<div class='card-box'>{day_data['grammar']['theory']}</div>",
            unsafe_allow_html=True,
        )

    # TAB 4: READING
    with tab4:
        st.subheader(f"Bài đọc: {day_data['reading']['title']}")
        st.write(day_data["reading"]["text"])
        st.markdown("#### Câu hỏi đọc hiểu:")
        for idx, q in enumerate(day_data["reading"]["questions"], 1):
            st.write(f"**Q{idx}:** {q}")

    # TAB 5: LISTENING
    with tab5:
        st.subheader("Bài tập Nghe")
        st.write(day_data["listening"])

    # TAB 6: WRITING
    with tab6:
        st.subheader("Bài tập Viết")
        st.write(day_data["writing"])
        user_writing = st.text_area(
            "Nhập bài viết của bạn tại đây:", height=150, key=f"write_{selected_day}"
        )
        if st.button("Gửi bài viết để AI chấm điểm", key=f"eval_write_{selected_day}"):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key ở Sidebar!")
            elif not user_writing.strip():
                st.warning("Vui lòng nhập bài viết trước khi bấm chấm!")
            else:
                with st.spinner("AI đang chấm điểm bài viết..."):
                    prompt = f"Hãy nhận xét và sửa lỗi chi tiết cho bài viết tiếng Anh sau:\n\n{user_writing}"
                    feedback = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if feedback:
                        st.markdown("### 📊 Đánh giá bài viết từ AI")
                        st.markdown(
                            f"<div class='card-box'>{feedback}</div>",
                            unsafe_allow_html=True,
                        )

    # TAB 7: SPEAKING
    with tab7:
        st.subheader("Luyện Nói IELTS Speaking")
        st.write(f"**Chủ đề bài nói:** {day_data['speaking_prompt']}")

        # Bộ Thu âm, Phát lại & AI Chấm điểm bài nói IELTS
        record_and_evaluate_speech(day_data["speaking_prompt"])

    # TAB 8: TRANSLATION & ERROR LOG
    with tab8:
        st.subheader("Thử thách Dịch thuật")
        st.write(f"**Dịch câu sau sang tiếng Anh:** {day_data['translation']}")

        user_trans = st.text_input("Nhập bản dịch của bạn:", key=f"trans_{selected_day}")
        if st.button("Kiểm tra bản dịch", key=f"check_trans_{selected_day}"):
            if not st.session_state.groq_api_key:
                st.error("Vui lòng nhập Groq API Key ở Sidebar!")
            elif not user_trans.strip():
                st.warning("Vui lòng nhập bản dịch trước!")
            else:
                with st.spinner("AI đang kiểm tra bản dịch..."):
                    prompt = f"Hãy đánh giá bản dịch tiếng Anh này.\n- Câu gốc tiếng Việt: '{day_data['translation']}'\n- Bản dịch của học viên: '{user_trans}'\nĐưa ra câu dịch chuẩn và sửa lỗi ngữ pháp/từ vựng nếu có."
                    eval_trans = call_groq_llm(prompt, st.session_state.groq_api_key)
                    if eval_trans:
                        st.markdown(
                            f"<div class='card-box'>{eval_trans}</div>",
                            unsafe_allow_html=True,
                        )

        st.divider()

        # Nhật ký lưu lỗi cá nhân (User Error Log)
        st.subheader("📓 Nhật ký ghi chú & Lưu lỗi cá nhân")
        note_input = st.text_area(
            "Ghi lại các từ vựng hoặc lỗi phát âm cần xem lại hôm nay:",
            value=st.session_state.user_notes.get(str(selected_day), ""),
            key=f"note_area_{selected_day}",
        )
        if st.button("Lưu ghi chú", key=f"save_note_{selected_day}"):
            st.session_state.user_notes[str(selected_day)] = note_input
            save_data_to_file()
            st.success("Đã lưu ghi chú thành công!")


if __name__ == "__main__":
    main()