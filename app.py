import os
import json
import base64
import streamlit as st
from openai import OpenAI
from PIL import Image

st.set_page_config(
    page_title="StudyDost AI",
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

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    try:
        API_KEY = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        API_KEY = None

client = OpenAI(api_key=API_KEY) if API_KEY else None
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def ask_ai(messages, temperature=0.4):
    if client is None:
        raise RuntimeError("AI API key is not configured. Set OPENAI_API_KEY on the server.")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "syllabus" not in st.session_state:
    st.session_state.syllabus = {}
if "study_time" not in st.session_state:
    st.session_state.study_time = "2 घंटे"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#1a73e8'>🎓 StudyDost AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>आपका Personal AI Study Partner</p>", unsafe_allow_html=True)
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
    st.caption("यह शुरुआती संस्करण demo login इस्तेमाल करता है; अभी कोई असली अकाउंट/पासवर्ड सिस्टम नहीं है।")
    st.stop()

with st.sidebar:
    st.markdown(f"### नमस्ते, {st.session_state.user_name} 👋")
    menu = st.radio(
        "मेनू",
        ["📖 सिलेबस और टाइमटेबल", "🤖 AI स्टडी चैट", "📸 फोटो से सवाल हल करें", "📝 क्विज़ और मॉक टेस्ट"],
        label_visibility="collapsed",
    )
    if st.button("लॉगआउट", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.chat_history = []
        st.rerun()

if not client:
    st.warning("AI फीचर चालू करने के लिए सर्वर पर OPENAI_API_KEY सेट करें। API key को Android ऐप या इस कोड में hard-code न करें।")

if menu == "📖 सिलेबस और टाइमटेबल":
    st.title("📖 सिलेबस और टाइमटेबल")
    st.session_state.study_time = st.text_input("रोज़ पढ़ाई का समय", st.session_state.study_time)
    with st.form("add_subject"):
        subject = st.text_input("विषय (जैसे Maths, Science)")
        chapters = st.text_area("चैप्टर के नाम (हर चैप्टर नई लाइन में)")
        save = st.form_submit_button("सिलेबस सेव करें")
        if save:
            if subject.strip() and chapters.strip():
                st.session_state.syllabus[subject.strip()] = chapters.strip()
                st.success(f"{subject} का सिलेबस सेव हो गया।")
            else:
                st.error("विषय और चैप्टर दोनों लिखें।")
    if st.session_state.syllabus:
        for sub, ch in st.session_state.syllabus.items():
            with st.expander(sub):
                st.write(ch)
    else:
        st.info("अभी कोई विषय नहीं जोड़ा गया है।")

elif menu == "🤖 AI स्टडी चैट":
    st.title("🤖 आपका AI स्टडी दोस्त")
    st.caption("किसी भी विषय का सवाल पूछें। AI आसान भाषा में समझाने की कोशिश करेगा।")
    if st.session_state.syllabus:
        st.caption("आपका सिलेबस: " + "; ".join(st.session_state.syllabus.keys()))
    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(content)
    prompt = st.chat_input("अपना सवाल लिखें...")
    if prompt:
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)
        context = (
            f"Student name: {st.session_state.user_name}. "
            f"Daily study time: {st.session_state.study_time}. "
            f"Syllabus: {json.dumps(st.session_state.syllabus, ensure_ascii=False)}. "
            "You are StudyDost AI, a patient school tutor. Reply in the language the student uses. "
            "Explain step by step in age-appropriate, simple language. Do not invent textbook facts."
        )
        try:
            answer = ask_ai(
                [{"role": "system", "content": context}]
                + [{"role": r, "content": c} for r, c in st.session_state.chat_history[-12:]]
            )
        except Exception as e:
            answer = f"AI से जवाब लेते समय समस्या आई: {e}"
        st.session_state.chat_history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.markdown(answer)

elif menu == "📸 फोटो से सवाल हल करें":
    st.title("📸 फोटो से सवाल हल करें")
    st.write("किताब या कॉपी के सवाल की साफ़ फोटो अपलोड करें।")
    file = st.file_uploader("फोटो चुनें", type=["jpg", "jpeg", "png"])
    if file:
        image = Image.open(file).convert("RGB")
        st.image(image, caption="अपलोड की गई फोटो", use_container_width=True)
        if st.button("🔍 सवाल समझाओ और हल करो", use_container_width=True):
            if not client:
                st.error("पहले सर्वर पर OPENAI_API_KEY सेट करें।")
            else:
                try:
                    import io
                    buf = io.BytesIO()
                    image.save(buf, format="JPEG", quality=85)
                    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
                    result = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": "You are a careful school tutor. Read the uploaded question and explain the solution step by step in simple Hindi unless the question is in English. If text is unclear, say so rather than guessing."},
                            {"role": "user", "content": [
                                {"type": "text", "text": "इस फोटो में दिए गए सवाल को पढ़कर हल करो।"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                            ]}
                        ],
                        max_tokens=1200,
                    )
                    st.markdown("### समाधान")
                    st.markdown(result.choices[0].message.content)
                except Exception as e:
                    st.error(f"फोटो समझने में समस्या आई: {e}")

elif menu == "📝 क्विज़ और मॉक टेस्ट":
    st.title("📝 क्विज़ और मॉक टेस्ट")
    if not st.session_state.syllabus:
        st.info("पहले सिलेबस सेक्शन में विषय और चैप्टर जोड़ें।")
    else:
        subject = st.selectbox("विषय चुनें", list(st.session_state.syllabus.keys()))
        count = st.selectbox("प्रश्नों की संख्या", [5, 10])
        if st.button("नया टेस्ट बनाएं 🚀", use_container_width=True):
            if not client:
                st.error("पहले सर्वर पर OPENAI_API_KEY सेट करें।")
            else:
                prompt = f"""Create {count} school-level multiple-choice questions based ONLY on these chapters:
{st.session_state.syllabus[subject]}
Return valid JSON only in this shape:
{{"questions":[{{"question":"...","options":["A...","B...","C...","D..."],"answer":0,"explanation":"..."}}]}}
The answer is the zero-based option index. Use clear language."""
                try:
                    raw = ask_ai([{"role": "user", "content": prompt}], temperature=0.2)
                    raw = raw.removeprefix("```json").removesuffix("```").strip()
                    data = json.loads(raw)
                    st.session_state.quiz_data = {"subject": subject, **data}
                    st.session_state.quiz_answers = {}
                except Exception as e:
                    st.error(f"टेस्ट बनाने में समस्या आई: {e}")
        quiz = st.session_state.quiz_data
        if quiz:
            st.subheader(f"{quiz['subject']} टेस्ट")
            with st.form("quiz_form"):
                for i, q in enumerate(quiz["questions"]):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    choice = st.radio("एक उत्तर चुनें", q["options"], key=f"q_{i}", index=None, label_visibility="collapsed")
                    st.session_state.quiz_answers[i] = choice
                submitted = st.form_submit_button("उत्तर जाँचें")
            if submitted:
                score = 0
                for i, q in enumerate(quiz["questions"]):
                    chosen = st.session_state.quiz_answers.get(i)
                    correct = q["options"][q["answer"]]
                    if chosen == correct:
                        score += 1
                        st.success(f"Q{i+1}: सही! {q['explanation']}")
                    else:
                        st.error(f"Q{i+1}: सही उत्तर — {correct}. {q['explanation']}")
                st.metric("आपका स्कोर", f"{score}/{len(quiz['questions'])}")
