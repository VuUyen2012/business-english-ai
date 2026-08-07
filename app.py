import streamlit as st
import requests
import json
import re
from supabase import create_client, Client

# ==========================================
# 1. CẤU HÌNH TRANG WEB (BẮT BUỘC ĐẦU FILE)
# ==========================================
st.set_page_config(
    page_title="Business English Master AI",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# 2. KHỞI TẠO SUPABASE
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
        return results[0].get("overall_level", "B1 Intermediate")
    return "B1 Intermediate"

# ==========================================
# 3. HÀM XỬ LÝ AN TOÀN (TTS & REGEX JSON)
# ==========================================
def play_audio_html(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <div style="margin: 10px 0;">
            <button onclick="speakText()" style="
                background-color: #4CAF50; border: none; color: white;
                padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer;">
                🔊 Play Audio
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

def extract_json_safely(raw_text):
    """Trích xuất JSON dùng Regex, tránh tuyệt đối lỗi chuỗi backtick"""
    if not raw_text:
        return None
    match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

# ==========================================
# 4. THANH BÊN (SIDEBAR) & KHỞI TẠO BIẾN
# ==========================================
with st.sidebar:
    st.title("⚙️ System Config")
    default_groq_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key:", value=default_groq_key, type="password")
    
    st.divider()
    st.title("🎯 Navigation")
    app_mode = st.radio(
        "Choose Mode:",
        [
            "1. Comprehensive Placement Test", 
            "2. 30-Day Business English Curriculum", 
            "3. Review Error Log & History"
        ]
    )
    
    st.divider()
    st.subheader("📊 Database Status")
    current_lvl = get_user_current_level()
    if supabase:
        st.success("Supabase: Connected")
    else:
        st.warning("Supabase: Disconnected")
    st.info(f"🎯 Current CEFR Level: {current_lvl}")

# ==========================================
# 5. GỌI GROQ API
# ==========================================
SYSTEM_PROMPT = "You are a Senior Business English AI Instructor. Answer clearly in professional English."

def generate_ai_response(prompt_input):
    if not api_key:
        st.error("Groq API Key missing!")
        return None

    url = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(prompt_input)}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error ({response.status_code})")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# ==========================================
# 6. GIAO DIỆN CHÍNH
# ==========================================
if not api_key:
    st.warning("⚠️ Please configure your Groq API Key in the sidebar or Secrets to start!")
else:
    if app_mode == "1. Comprehensive Placement Test":
        st.title("📋 Comprehensive Placement Test")
        st.info(f"Current Level: {get_user_current_level()}")

        t1, t2, t3, t4, t5 = st.tabs(["Vocabulary", "Grammar", "Reading", "Listening", "Writing"])

        def run_quiz_tab(tab_key, prompt_text, btn_label):
            if st.button(btn_label, key=f"btn_{tab_key}"):
                with st.spinner("Generating quiz..."):
                    raw = generate_ai_response(prompt_text)
                    clean = extract_json_safely(raw)
                    if clean:
                        try:
                            st.session_state[f"{tab_key}_data"] = json.loads(clean)
                            st.session_state[f"{tab_key}_sub"] = False
                        except Exception as e:
                            st.error(f"Format error: {str(e)}")

            if f"{tab_key}_data" in st.session_state:
                data = st.session_state[f"{tab_key}_data"]
                with st.form(f"form_{tab_key}"):
                    ans = {}
                    for item in data:
                        st.write(f"**Q{item['id']}:** {item['question']}")
                        ans[item['id']] = st.radio("Select answer:", item["options"], key=f"{tab_key}_{item['id']}")
                    if st.form_submit_button("Submit"):
                        st.session_state[f"{tab_key}_sub"] = True
                        st.session_state[f"{tab_key}_ans"] = ans

                if st.session_state.get(f"{tab_key}_sub", False):
                    score = 0
                    user_a = st.session_state[f"{tab_key}_ans"]
                    for item in data:
                        if user_a.get(item['id']) == item['answer']:
                            score += 1
                    st.success(f"Score: {score}/{len(data)}")

        with t1:
            run_quiz_tab("vocab", "Generate 5 Business English vocab questions in JSON array format: [{'id':1,'question':'...','options':['A...','B...'],'answer':'A...'}]", "Start Vocabulary Test")
        with t2:
            run_quiz_tab("grammar", "Generate 5 Business English grammar questions in JSON array format: [{'id':1,'question':'...','options':['A...','B...'],'answer':'A...'}]", "Start Grammar Test")
        with t3:
            st.write("Reading module active.")
        with t4:
            st.write("Listening module active.")
        with t5:
            st.write("Writing module active.")

    elif app_mode == "2. 30-Day Business English Curriculum":
        st.title("📚 30-Day Curriculum")
        day = st.slider("Select Day", 1, 30, 1)
        st.write(f"Day {day} curriculum active.")

    elif app_mode == "3. Review Error Log & History":
        st.title("📜 Learning History")
        st.write("History log active.")