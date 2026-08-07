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
# 2. KHỞI TẠO BẢO VỆ KẾT NỐI SUPABASE
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
# 3. HÀM PHÁT ÂM TIẾNG ANH & LÀM SẠCH JSON
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

def clean_json_response(raw_text):
    """Hàm xử lý chuỗi phản hồi từ AI thành JSON chuẩn, tránh lỗi cú pháp"""
    if not raw_text:
        return None
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("