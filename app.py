def clean_json_response(raw_text):
    """Xử lý chuỗi AI trả về thành JSON sạch không dùng ký tự backtick trực tiếp"""
    if not raw_text:
        return None
    text = raw_text.strip()
    
    # Loại bỏ prefix markdown nếu có
    if text.lower().startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
        
    # Loại bỏ suffix markdown nếu có
    if text.endswith("```"):
        text = text[:-3]
        
    return text.strip()