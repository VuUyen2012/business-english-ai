def evaluate_answer(user_selection, raw_correct, options):
    if user_selection is None or raw_correct is None:
        return False, str(raw_correct)

    u_sel_str = str(user_selection).strip().lower()
    c_ans_str = str(raw_correct).strip().lower()

    # 1. So sánh trực tiếp chuỗi văn bản
    if u_sel_str == c_ans_str:
        return True, str(user_selection)

    if options and isinstance(options, list):
        # 2. Xử lý trường hợp correct_option là chỉ số số (0-indexed hoặc 1-indexed)
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            # 1-indexed
            if 1 <= idx <= len(options):
                target_opt = str(options[idx - 1]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx - 1]
            # 0-indexed
            if 0 <= idx < len(options):
                target_opt = str(options[idx]).strip().lower()
                if u_sel_str == target_opt:
                    return True, options[idx]

        # 3. Xử lý trường hợp correct_option là chữ cái A, B, C, D
        letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        if c_ans_str in letter_map and letter_map[c_ans_str] < len(options):
            target_opt = str(options[letter_map[c_ans_str]]).strip().lower()
            if u_sel_str == target_opt:
                return True, options[letter_map[c_ans_str]]

        # 4. Tìm kiếm tương đối nếu chuỗi đáp án chứa text của tùy chọn
        for opt in options:
            if str(opt).strip().lower() == c_ans_str:
                if u_sel_str == str(opt).strip().lower():
                    return True, opt

    # Nếu không khớp, trả về văn bản đáp án đúng tương ứng để hiển thị UI
    correct_display = raw_correct
    if options and isinstance(options, list):
        if c_ans_str.isdigit():
            idx = int(c_ans_str)
            if 1 <= idx <= len(options):
                correct_display = options[idx - 1]
            elif 0 <= idx < len(options):
                correct_display = options[idx]
        elif c_ans_str in {'a', 'b', 'c', 'd', 'e'}:
            correct_display = options[{'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}[c_ans_str]]

    return False, str(correct_display)