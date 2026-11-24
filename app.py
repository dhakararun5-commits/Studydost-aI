import streamlit as st

st.set_page_config(
    page_title="StudyDost",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp { background: #f7f9fc; }
.stButton>button {
  background:#1a73e8; color:white; border:0; border-radius:10px;
  min-height:2.7rem; font-weight:600;
}
[data-testid="stSidebar"] { background:#eef3fb; }
</style>
""", unsafe_allow_html=True)

# StudyDost is a manual, no-AI study organiser.
# Notes, chapters and question banks are kept in the current Streamlit session.
BOARDS = ["CBSE", "MP Board"]
CLASSES = [f"Class {n}" for n in range(1, 13)]

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "study_data" not in st.session_state:
    st.session_state.study_data = {}
if "study_time" not in st.session_state:
    st.session_state.study_time = "2 घंटे"
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

def current_key():
    return (st.session_state.board, st.session_state.school_class)

def get_class_data():
    return st.session_state.study_data.setdefault(
        current_key(), {"subjects": {}, "timetable": ""}
    )

def get_subject_data(subject):
    return get_class_data()["subjects"].setdefault(
        subject, {"chapters": {}, "questions": []}
    )

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#1a73e8'>🎓 StudyDost</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>आपका अपना Study Planner</p>", unsafe_allow_html=True)
    with st.form("login"):
        name = st.text_input("आपका नाम")
        submitted = st.form_submit_button("शुरू करें 🚀", use_container_width=True)
        if submitted:
            if name.strip():
                st.session_state.user_name = name.strip()
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("कृपया अपना नाम लिखें।")
    st.caption("यह ऐप बिना AI और बिना API key के काम करता है।")
    st.stop()

with st.sidebar:
    st.markdown(f"### नमस्ते, {st.session_state.user_name} 👋")
    st.selectbox("Board चुनें", BOARDS, key="board")
    st.selectbox("Class चुनें", CLASSES, key="school_class")
    menu = st.radio(
        "मेनू",
        ["🏠 होम", "📚 विषय और चैप्टर", "📝 नोट्स", "✅ MCQ टेस्ट", "⏰ टाइमटेबल"],
        label_visibility="collapsed",
    )
    if st.button("लॉगआउट", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🎓 StudyDost")
st.caption(f"{st.session_state.board} • {st.session_state.school_class}")

class_data = get_class_data()
subjects = list(class_data["subjects"].keys())

if menu == "🏠 होम":
    st.subheader(f"नमस्ते {st.session_state.user_name}!")
    st.write("पढ़ाई को व्यवस्थित करने के लिए StudyDost इस्तेमाल करें।")
    c1, c2 = st.columns(2)
    c1.metric("जोड़े गए विषय", len(subjects))
    chapter_count = sum(len(v["chapters"]) for v in class_data["subjects"].values())
    c2.metric("जोड़े गए चैप्टर", chapter_count)
    st.info("शुरू करने के लिए साइडबार से Board और Class चुनें, फिर विषय और चैप्टर जोड़ें।")
    st.warning("नोट: इस संस्करण में पाठ्यपुस्तक की पूरी आधिकारिक सामग्री पहले से शामिल नहीं है। अपने स्कूल/किताब के अनुसार सामग्री जोड़ें।")

elif menu == "📚 विषय और चैप्टर":
    st.subheader("विषय और चैप्टर")
    with st.form("add_subject"):
        subject = st.text_input("विषय का नाम (जैसे Maths, Science, Hindi)")
        add_subject = st.form_submit_button("विषय जोड़ें")
        if add_subject:
            if subject.strip():
                get_subject_data(subject.strip())
                st.success(f"{subject.strip()} जोड़ दिया गया।")
                st.rerun()
            else:
                st.error("विषय का नाम लिखें।")

    if subjects:
        selected_subject = st.selectbox("विषय चुनें", subjects, key="chapter_subject")
        with st.form("add_chapter"):
            chapter = st.text_input("चैप्टर का नाम")
            chapter_note = st.text_area("चैप्टर का छोटा विवरण (वैकल्पिक)")
            save_chapter = st.form_submit_button("चैप्टर सेव करें")
            if save_chapter:
                if chapter.strip():
                    get_subject_data(selected_subject)["chapters"][chapter.strip()] = chapter_note.strip()
                    st.success("चैप्टर सेव हो गया।")
                    st.rerun()
                else:
                    st.error("चैप्टर का नाम लिखें।")
        st.markdown("#### सेव किए गए चैप्टर")
        for ch, desc in get_subject_data(selected_subject)["chapters"].items():
            with st.expander(ch):
                st.write(desc if desc else "अभी कोई विवरण नहीं जोड़ा गया।")
    else:
        st.info("पहले अपना पहला विषय जोड़ें।")

elif menu == "📝 नोट्स":
    st.subheader("अपने नोट्स")
    if not subjects:
        st.info("पहले 'विषय और चैप्टर' में विषय जोड़ें।")
    else:
        selected_subject = st.selectbox("विषय", subjects, key="notes_subject")
        chapter_names = list(get_subject_data(selected_subject)["chapters"].keys())
        if chapter_names:
            selected_chapter = st.selectbox("चैप्टर", chapter_names)
            existing = get_subject_data(selected_subject)["chapters"].get(selected_chapter, "")
            note = st.text_area("नोट्स / महत्वपूर्ण प्रश्न-उत्तर", value=existing, height=220)
            if st.button("नोट्स सेव करें", use_container_width=True):
                get_subject_data(selected_subject)["chapters"][selected_chapter] = note
                st.success("नोट्स सेव हो गए।")
        else:
            st.info("इस विषय में पहले चैप्टर जोड़ें।")

elif menu == "✅ MCQ टेस्ट":
    st.subheader("अपना MCQ प्रश्न बैंक बनाएं")
    if not subjects:
        st.info("पहले विषय जोड़ें।")
    else:
        selected_subject = st.selectbox("विषय", subjects, key="quiz_subject")
        qdata = get_subject_data(selected_subject)
        with st.expander("नया MCQ प्रश्न जोड़ें", expanded=True):
            with st.form("add_mcq"):
                question = st.text_input("प्रश्न")
                options = [st.text_input(f"विकल्प {letter}") for letter in ["A", "B", "C", "D"]]
                correct = st.selectbox("सही उत्तर", ["A", "B", "C", "D"])
                explanation = st.text_input("समाधान / व्याख्या (वैकल्पिक)")
                add_q = st.form_submit_button("प्रश्न सेव करें")
                if add_q:
                    if question.strip() and all(x.strip() for x in options):
                        qdata["questions"].append({
                            "question": question.strip(),
                            "options": [x.strip() for x in options],
                            "answer": ["A", "B", "C", "D"].index(correct),
                            "explanation": explanation.strip(),
                        })
                        st.success("प्रश्न सेव हो गया।")
                        st.rerun()
                    else:
                        st.error("प्रश्न और चारों विकल्प भरें।")

        if qdata["questions"]:
            st.markdown(f"#### {selected_subject} — {len(qdata['questions'])} प्रश्न")
            with st.form("take_quiz"):
                answers = []
                for i, q in enumerate(qdata["questions"]):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    answers.append(st.radio(
                        "उत्तर चुनें", q["options"], key=f"answer_{current_key()}_{selected_subject}_{i}",
                        index=None, label_visibility="collapsed"
                    ))
                submitted = st.form_submit_button("उत्तर जाँचें")
            if submitted:
                score = sum(
                    1 for i, q in enumerate(qdata["questions"])
                    if answers[i] == q["options"][q["answer"]]
                )
                st.session_state.quiz_result = (score, len(qdata["questions"]))
                st.success(f"आपका स्कोर: {score}/{len(qdata['questions'])}")
                for i, q in enumerate(qdata["questions"]):
                    st.write(f"Q{i+1}: सही उत्तर — {q['options'][q['answer']]}")
                    if q["explanation"]:
                        st.caption(q["explanation"])
        else:
            st.info("अभी प्रश्न नहीं हैं। ऊपर से अपने MCQ जोड़ें।")

elif menu == "⏰ टाइमटेबल":
    st.subheader("आपका पढ़ाई टाइमटेबल")
    st.session_state.study_time = st.text_input("रोज़ पढ़ाई का लक्ष्य", st.session_state.study_time)
    timetable = st.text_area(
        "अपना टाइमटेबल लिखें",
        value=class_data.get("timetable", ""),
        height=220,
        placeholder="उदाहरण:\n4:00–5:00 Maths\n5:00–5:30 Break\n5:30–6:30 Science",
    )
    if st.button("टाइमटेबल सेव करें", use_container_width=True):
        class_data["timetable"] = timetable
        st.success("टाइमटेबल सेव हो गया।")

st.divider()
st.caption("StudyDost • No AI • No API key required")
