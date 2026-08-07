# Helper render MCQ an toàn tuyệt đối (Chống KeyError)
        def render_mcq(tab_key, prompt_text, btn_label):
            if st.button(btn_label, key=f"btn_{tab_key}", use_container_width=True):
                with st.spinner("Generating test questions..."):
                    raw = generate_ai_response(prompt_text)
                    clean = extract_json_safely(raw)
                    if clean:
                        try:
                            parsed_data = json.loads(clean)
                            # Reset trạng thái câu hỏi và kết quả cũ
                            st.session_state[f"{tab_key}_data"] = parsed_data
                            st.session_state[f"{tab_key}_sub"] = False
                            st.session_state[f"{tab_key}_ans"] = {}
                        except Exception as e:
                            st.error(f"Format error from AI: {e}")

            if f"{tab_key}_data" in st.session_state:
                data = st.session_state[f"{tab_key}_data"]
                
                # Xử lý nếu data là Dict có chứa Passage hoặc Questions
                if isinstance(data, dict):
                    if "passage" in data:
                        st.markdown("### 📄 Content / Audio Transcript")
                        st.info(data["passage"])
                        if tab_key == "l_diag":
                            play_audio_html(data["passage"])
                    questions = data.get("questions", [])
                elif isinstance(data, list):
                    questions = data
                else:
                    questions = []

                if not questions:
                    st.warning("No questions generated. Please try clicking the button again.")
                    return

                with st.form(f"form_{tab_key}"):
                    user_ans = {}
                    for idx, q in enumerate(questions, 1):
                        # Dùng .get() an toàn, fallback nếu thiếu 'id' hoặc 'options'
                        q_id = q.get('id', idx)
                        q_text = q.get('question', f'Question {idx}')
                        q_opts = q.get('options', q.get('choices', []))
                        
                        st.markdown(f"**Q{idx}: {q_text}**")
                        
                        if q_opts:
                            user_ans[q_id] = st.radio(
                                "Select answer:", 
                                q_opts, 
                                key=f"{tab_key}_radio_{idx}_{q_id}", 
                                index=None
                            )
                        else:
                            st.error("Missing options for this question.")
                            
                        st.write("---")
                    
                    submitted = st.form_submit_button("Submit Section")
                    if submitted:
                        st.session_state[f"{tab_key}_sub"] = True
                        st.session_state[f"{tab_key}_ans"] = user_ans

                # Hiển thị kết quả & chấm điểm khi người dùng Submit
                if st.session_state.get(f"{tab_key}_sub", False):
                    score = 0
                    u_ans = st.session_state.get(f"{tab_key}_ans", {})
                    st.markdown("#### 📊 Section Results & Detailed Feedback")
                    
                    for idx, q in enumerate(questions, 1):
                        q_id = q.get('id', idx)
                        sel = u_ans.get(q_id)
                        cor = q.get('answer', '')
                        exp = q.get('explanation', 'No detailed explanation available.')
                        
                        if sel and sel == cor:
                            score += 1
                            st.markdown(f'<div class="correct-card">✅ <b>Q{idx}: Correct!</b> ({sel})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="wrong-card">❌ <b>Q{idx}: Incorrect</b>. Your Answer: <b>{sel if sel else "Not Answered"}</b> | Correct Answer: <b>{cor}</b></div>', unsafe_allow_html=True)
                        
                        st.caption(f"💡 Explanation: {exp}")
                        st.write("")
                    
                    st.success(f"🏆 Final Score: {score}/{len(questions)} ({(score/len(questions))*100:.0f}%)")
                    st.session_state[f"{tab_key}_score_val"] = score