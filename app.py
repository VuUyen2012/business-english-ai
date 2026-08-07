# ==========================================
# 6. GIAO DIỆN CHÍNH (UI/UX CHUYÊN NGHIỆP)
# ==========================================
if not api_key:
    st.warning("⚠️ Vui lòng lưu Groq API Key vào Secrets để bắt đầu sử dụng app!")
else:
    # PHẦN 1: PLACEMENT TEST (100% Tiếng Anh & Interactive)
    if app_mode == "1. Đánh giá đầu vào (Placement Test)":
        st.title("📋 Comprehensive Placement Test")
        
        current_lvl = get_user_current_level()
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-bottom: 20px;">
            <h4 style="margin:0; color: #1E88E5;">🏆 Current CEFR Level: <b>{current_lvl}</b></h4>
            <p style="margin:5px 0 0 0; font-size: 14px; color: #555;">This placement result is used to personalize your 30-day Business English roadmap.</p>
        </div>
        """, unsafe_allow_html=True)

        t1, t2, t3, t4, t5, t6 = st.tabs([
            "1. Vocabulary (15 Qs)", "2. Grammar (15 Qs)", "3. Reading (20 Qs)", 
            "4. Listening (10 Qs)", "5. Writing & CEFR", "6. Speaking (3 Topics)"
        ])

        # HÀM BỔ TRỢ RENDER INTERACTIVE QUIZ HÓA JSON
        def render_interactive_quiz(tab_key, prompt_json, button_label):
            if st.button(button_label, key=f"btn_gen_{tab_key}"):
                with st.spinner("Generating 100% English quiz data..."):
                    res_raw = generate_ai_response(prompt_json)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("```"): clean_json = clean_json[3:]
                            if clean_json.endswith("```"): clean_json = clean_json[:-3]
                            
                            st.session_state[f"{tab_key}_quiz_data"] = json.loads(clean_json.strip())
                            st.session_state[f"{tab_key}_user_answers"] = {}
                            st.session_state[f"{tab_key}_submitted"] = False
                        except Exception as e:
                            st.error(f"Error parsing quiz format. Please try again! ({str(e)})")

            if f"{tab_key}_quiz_data" in st.session_state and st.session_state[f"{tab_key}_quiz_data"]:
                quiz_data = st.session_state[f"{tab_key}_quiz_data"]
                
                with st.form(f"{tab_key}_quiz_form"):
                    user_answers = {}
                    for item in quiz_data:
                        st.markdown(f"**Question {item['id']}:** {item['question']}")
                        user_answers[item['id']] = st.radio(
                            label=f"Answer Q{item['id']}:",
                            options=item["options"],
                            key=f"{tab_key}_q_{item['id']}",
                            label_visibility="collapsed"
                        )
                        st.divider()

                    submitted = st.form_submit_button("📩 Submit & Grade Test")

                if submitted:
                    st.session_state[f"{tab_key}_submitted"] = True
                    st.session_state[f"{tab_key}_user_answers"] = user_answers

                if st.session_state.get(f"{tab_key}_submitted", False):
                    score = 0
                    u_ans = st.session_state[f"{tab_key}_user_answers"]
                    
                    st.markdown("### 📊 Test Results")
                    for item in quiz_data:
                        q_id = item['id']
                        selected = u_ans.get(q_id)
                        correct = item['answer']
                        
                        if selected == correct:
                            score += 1
                            st.success(f"**Q{q_id}: Correct!** ({selected})")
                        else:
                            st.error(f"**Q{q_id}: Incorrect.** Your answer: {selected} | **Correct Answer:** {correct}")
                        
                        st.info(f"💡 *Explanation:* {item['explanation']}")
                        st.write("---")

                    final_percentage = round((score / len(quiz_data)) * 100, 1)
                    st.balloons()
                    st.markdown(f"## 🏆 Final Score: **{score}/{len(quiz_data)}** ({final_percentage}%)")

        # 1. VOCABULARY TAB
        with t1:
            st.subheader("Vocabulary Assessment (15 Questions)")
            prompt_vocab = """
            Generate a 15-question Business English Vocabulary quiz (CEFR A2-C1).
            Return ONLY a valid JSON array without any markdown code blocks or preamble:
            [
              {
                "id": 1,
                "question": "Choose the word that best completes the sentence: 'We plan to _______ our new product line next quarter.'",
                "options": ["A) launch", "B) delay", "C) suspend", "D) dismiss"],
                "answer": "A) launch",
                "explanation": "'Launch' means to introduce a new product or project to the market."
              }
            ]
            """
            render_interactive_quiz("vocab", prompt_vocab, "Start Vocabulary Test")

        # 2. GRAMMAR TAB
        with t2:
            st.subheader("Grammar Assessment (15 Questions)")
            prompt_gram = """
            Generate a 15-question Business English Grammar quiz (CEFR A2-C1 focusing on tenses, conditionals, passive voice, and formal register).
            Return ONLY a valid JSON array without markdown blocks:
            [
              {
                "id": 1,
                "question": "Identify the correct structure: 'If we _______ the budget earlier, we would have avoided the project delay.'",
                "options": ["A) approved", "B) had approved", "C) have approved", "D) approve"],
                "answer": "B) had approved",
                "explanation": "Third conditional requires 'had + past participle' in the if-clause to talk about past unreal situations."
              }
            ]
            """
            render_interactive_quiz("grammar", prompt_gram, "Start Grammar Test")

        # 3. READING TAB
        with t3:
            st.subheader("Reading Comprehension Assessment")
            if st.button("Generate Reading Passage & Quiz", key="btn_p_read"):
                with st.spinner("Generating reading passage and comprehension questions..."):
                    prompt_read = """
                    Write a formal Business Strategy passage (250-300 words). Below it, create 5 multiple choice comprehension questions.
                    Return ONLY a JSON object formatted strictly like this:
                    {
                      "passage": "Full English passage text here...",
                      "questions": [
                        {
                          "id": 1,
                          "question": "What is the primary objective of the corporate restructuring mentioned in the passage?",
                          "options": ["A) To reduce market share", "B) To optimize operational efficiency", "C) To fire staff", "D) To close international branches"],
                          "answer": "B) To optimize operational efficiency",
                          "explanation": "Paragraph 2 states that restructuring aims to streamline workflows and reduce redundant costs."
                        }
                      ]
                    }
                    """
                    res_raw = generate_ai_response(prompt_read)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("```"): clean_json = clean_json[3:]
                            if clean_json.endswith("```"): clean_json = clean_json[:-3]
                            
                            st.session_state["reading_data"] = json.loads(clean_json.strip())
                            st.session_state["reading_submitted"] = False
                        except Exception as e:
                            st.error(f"Error parsing reading data. Please try again! ({str(e)})")

            if "reading_data" in st.session_state and st.session_state["reading_data"]:
                r_data = st.session_state["reading_data"]
                st.markdown("### 📖 Reading Passage")
                st.info(r_data["passage"])
                
                with st.form("reading_quiz_form"):
                    u_answers = {}
                    for item in r_data["questions"]:
                        st.markdown(f"**Question {item['id']}:** {item['question']}")
                        u_answers[item['id']] = st.radio(
                            label=f"Answer Q{item['id']}:",
                            options=item["options"],
                            key=f"read_q_{item['id']}",
                            label_visibility="collapsed"
                        )
                        st.divider()

                    if st.form_submit_button("Submit Reading Test"):
                        st.session_state["reading_submitted"] = True
                        st.session_state["reading_user_answers"] = u_answers

                if st.session_state.get("reading_submitted", False):
                    score = 0
                    u_ans = st.session_state["reading_user_answers"]
                    for item in r_data["questions"]:
                        q_id = item['id']
                        selected = u_ans.get(q_id)
                        correct = item['answer']
                        if selected == correct:
                            score += 1
                            st.success(f"**Q{q_id}: Correct!** ({selected})")
                        else:
                            st.error(f"**Q{q_id}: Incorrect.** Your answer: {selected} | **Correct:** {correct}")
                        st.info(f"💡 *Explanation:* {item['explanation']}")
                        st.write("---")
                    st.balloons()
                    st.markdown(f"## 🏆 Score: **{score}/{len(r_data['questions'])}**")

        # 4. LISTENING TAB
        with t4:
            st.subheader("Listening Comprehension Assessment")
            if st.button("Generate Audio Transcript & Questions", key="btn_p_listen"):
                with st.spinner("Generating audio script..."):
                    prompt_listen = """
                    Create a formal Business Meeting Dialogue between two managers (150-200 words).
                    Return ONLY a JSON object strictly like this:
                    {
                      "transcript": "Full dialogue text here...",
                      "questions": [
                        {
                          "id": 1,
                          "question": "What main disagreement occurred during the contract negotiation?",
                          "options": ["A) Payment terms", "B) Office location", "C) Hiring policy", "D) Dress code"],
                          "answer": "A) Payment terms",
                          "explanation": "Speaker A explicitly mentions that a 90-day payment cycle is unacceptable."
                        }
                      ]
                    }
                    """
                    res_raw = generate_ai_response(prompt_listen)
                    if res_raw:
                        try:
                            clean_json = res_raw.strip()
                            if clean_json.startswith("```json"): clean_json = clean_json[7:]
                            if clean_json.startswith("```"): clean_json = clean_json[3:]
                            if clean_json.endswith("```"): clean_json = clean_json[:-3]
                            
                            st.session_state["listening_data"] = json.loads(clean_json.strip())
                            st.session_state["listening_submitted"] = False
                        except Exception as e:
                            st.error(f"Error parsing listening data: {str(e)}")

            if "listening_data" in st.session_state and st.session_state["listening_data"]:
                l_data = st.session_state["listening_data"]
                st.markdown("### 🎧 Audio Script")
                play_audio_html(l_data["transcript"])
                
                with st.expander("Show Script Text (Optional)"):
                    st.write(l_data["transcript"])

                with st.form("listening_quiz_form"):
                    u_answers = {}
                    for item in l_data["questions"]:
                        st.markdown(f"**Question {item['id']}:** {item['question']}")
                        u_answers[item['id']] = st.radio(
                            label=f"Answer Q{item['id']}:",
                            options=item["options"],
                            key=f"listen_q_{item['id']}",
                            label_visibility="collapsed"
                        )
                        st.divider()

                    if st.form_submit_button("Submit Listening Test"):
                        st.session_state["listening_submitted"] = True
                        st.session_state["listening_user_answers"] = u_answers

                if st.session_state.get("listening_submitted", False):
                    score = 0
                    u_ans = st.session_state["listening_user_answers"]
                    for item in l_data["questions"]:
                        q_id = item['id']
                        selected = u_ans.get(q_id)
                        correct = item['answer']
                        if selected == correct:
                            score += 1
                            st.success(f"**Q{q_id}: Correct!** ({selected})")
                        else:
                            st.error(f"**Q{q_id}: Incorrect.** Your answer: {selected} | **Correct:** {correct}")
                        st.info(f"💡 *Explanation:* {item['explanation']}")
                        st.write("---")
                    st.balloons()
                    st.markdown(f"## 🏆 Score: **{score}/{len(l_data['questions'])}**")

        # 5. WRITING TAB
        with t5:
            st.subheader("Writing Assessment & CEFR Rating")
            st.caption("Prompt: Write a formal business email requesting a budget increase for your project (Minimum 100 words).")
            essay_text = st.text_area("Your Response:", height=200, key="p_essay", placeholder="Dear Management,...")
            
            if st.button("Evaluate Writing & Update CEFR Level", key="btn_p_score_write"):
                if len(essay_text.split()) < 100:
                    st.warning(f"Your response contains only {len(essay_text.split())} words. Please write at least 100 words.")
                else:
                    with st.spinner("Evaluating writing performance according to CEFR standards..."):
                        prompt_eval = f"""
                        Evaluate the following Business English response according to official CEFR criteria:
                        {essay_text}
                        
                        Return response in clear Markdown format with strictly this first line:
                        [LEVEL: <One / A2 Advanced B1 B2 C1 C2 Elementary Intermediate Proficient Upper-Intermediate of:>]
                        
                        Include:
                        ### 🎖️ CEFR ASSESSMENT BREAKDOWN
                        - **Overall CEFR:** [Level]
                        - **Vocabulary & Register:** [Feedback]
                        - **Grammar & Structure:** [Feedback]
                        - **Coherence & Task Fulfillment:** [Feedback]
                        
                        ### 🔍 ERROR CORRECTION & IMPROVEMENTS
                        (Original sentence -> Corrected sentence -> Detailed Explanation)
                        
                        ### ✍️ HIGH-SCORING MODEL ANSWER
                        (Provide a C1/C2 model answer for this prompt)
                        """
                        res_text = generate_ai_response(prompt_eval)
                        if res_text:
                            st.markdown(res_text)
                            detected_level = "B1 Intermediate"
                            if "[LEVEL:" in res_text:
                                try: detected_level = res_text.split("[LEVEL:")[1].split("]")[0].strip()
                                except: detected_level = "B1 Intermediate"

                            safe_save("placement_results", {"writing_feedback": res_text, "overall_level": detected_level})
                            st.balloons()
                            st.success(f"🎉 CEFR LEVEL UPDATED: **{detected_level}**!")

        # 6. SPEAKING TAB
        with t6:
            st.subheader("Speaking Assessment (3 Business Topics)")
            st.caption("Topic: Describe a challenging negotiation or business problem you solved recently.")
            spoken_text = st.text_area("Type or paste your spoken transcript below:", height=150, placeholder="In my previous role, I encountered a situation where...")
            if st.button("Evaluate Speaking Submission", key="btn_p_score_speak"):
                if spoken_text:
                    with st.spinner("Analyzing fluency, vocabulary, and grammar..."):
                        res_text = generate_ai_response(f"Evaluate this spoken Business English transcript based on CEFR fluency, vocabulary, and grammar standards:\n{spoken_text}")
                        if res_text:
                            st.markdown(res_text)

    # PHẦN 2 & 3 GIỮ NGUYÊN NHƯ B