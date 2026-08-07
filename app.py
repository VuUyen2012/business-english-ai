import requests
import json

def generate_ai_response(contents):
    if not api_key:
        st.error("Chưa nhập Gemini API Key!")
        return None

    # Chuẩn hóa dữ liệu đầu vào
    if isinstance(contents, str):
        prompt_text = contents
    elif isinstance(contents, list):
        # Trường hợp truyền audio hoặc nhiều văn bản
        prompt_text = " ".join([str(item) for item in contents if isinstance(item, str)])
    else:
        prompt_text = str(contents)

    # Sử dụng endpoint v1 ổn định thay vì v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nYêu cầu: {prompt_text}"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()

        if response.status_code == 200:
            try:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                st.error("Dữ liệu phản hồi từ AI không đúng định dạng.")
                return None
        elif response.status_code == 429:
            st.error("⏳ API Key Free bị vượt giới hạn lượt gọi (Quota limit). Vui lòng đợi 30s.")
            return None
        elif response.status_code == 404:
            # Fallback sang model gemini-pro nếu 1.5-flash không khả dụng với Key của bạn
            url_fallback = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            res_fb = requests.post(url_fallback, headers=headers, json=payload, timeout=30)
            if res_fb.status_code == 200:
                return res_fb.json()['candidates'][0]['content']['parts'][0]['text']
            st.error(f"Lỗi API 404: Key của bạn không có quyền truy cập mô hình này. Lỗi từ Google: {res_data.get('error', {}).get('message')}")
            return None
        else:
            msg = res_data.get('error', {}).get('message', 'Lỗi không xác định')
            st.error(f"Lỗi API ({response.status_code}): {msg}")
            return None

    except Exception as e:
        st.error(f"Lỗi kết nối mạng: {str(e)}")
        return None