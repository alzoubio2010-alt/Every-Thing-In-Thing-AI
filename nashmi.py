import streamlit as st
import os
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

# ────────────────────────────────────────────────
# تحميل المتغيرات من .env
load_dotenv()

OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
GROK_KEY      = os.getenv("GROK_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY    = os.getenv("CLAUDE_API_KEY")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "alzoubio2010@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ────────────────────────────────────────────────
# حالة المستخدم
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.seen_privacy = False

if "سجل" not in st.session_state:
    st.session_state.سجل = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ────────────────────────────────────────────────
# صفحة الخصوصية
if not st.session_state.seen_privacy:

    st.title("مرحبا بك في Every Thing In Thing AI")

    st.markdown("### نحن نحافظ على خصوصيتك 100%")

    st.markdown("""
• لا نحفظ أسئلتك أو محادثاتك على خوادمنا
• كل الإجابات تتم عبر نماذج AI خارجية
• اقتراحاتك فقط ترسل إلى المطور
• تسجيل الدخول اختياري
""")

    if st.button("أوافق وأفهم – ادخل التطبيق"):
        st.session_state.seen_privacy = True
        st.rerun()

    st.stop()

# ────────────────────────────────────────────────
# تسجيل دخول بسيط
if not st.session_state.logged_in:

    st.title("تسجيل الدخول")

    col1,col2 = st.columns([3,1])

    with col1:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة السر",type="password")

    with col2:

        if st.button("دخول"):

            if username and password:

                st.session_state.logged_in=True
                st.session_state.username=username
                st.rerun()

        if st.button("دخول كزائر"):

            st.session_state.logged_in=True
            st.session_state.username="زائر"
            st.rerun()

    st.stop()

# ────────────────────────────────────────────────
# واجهة التطبيق

st.title(f"مرحبا {st.session_state.username} في Every Thing In Thing AI")

st.markdown("### تطبيق شامل للدراسة والعمل والجامعة")

# ────────────────────────────────────────────────
# ارسال السؤال لكل النماذج

def send_to_all_models(query):

    answers = {}

    system="اشرح الحل خطوة خطوة وبوضوح"

    if OPENAI_KEY:
        try:
            client=OpenAI(api_key=OPENAI_KEY)
            r=client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":system},{"role":"user","content":query}]
            )
            answers["OpenAI"]=r.choices[0].message.content
        except:
            pass

    if GROK_KEY:
        try:
            r=requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization":f"Bearer {GROK_KEY}"},
                json={"model":"grok-beta","messages":[{"role":"user","content":query}]}
            )
            answers["Grok"]=r.json()["choices"][0]["message"]["content"]
        except:
            pass

    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model=genai.GenerativeModel("gemini-1.5-flash")
            r=model.generate_content(query)
            answers["Gemini"]=r.text
        except:
            pass

    if DEEPSEEK_KEY:
        try:
            client=OpenAI(api_key=DEEPSEEK_KEY,base_url="https://api.deepseek.com")
            r=client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role":"user","content":query}]
            )
            answers["DeepSeek"]=r.choices[0].message.content
        except:
            pass

    if CLAUDE_KEY:
        try:
            client=Anthropic(api_key=CLAUDE_KEY)
            msg=client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role":"user","content":query}]
            )
            answers["Claude"]=msg.content[0].text
        except:
            pass

    return answers

# ────────────────────────────────────────────────
# دمج الإجابات

def merge_with_model(text,model_name):

    prompt=f"""
ادمج هذه الإجابات في جواب واحد واضح ومنظم:
{text}
"""

    try:

        r=requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROK_KEY}"},
            json={"model":"grok-beta","messages":[{"role":"user","content":prompt}]}
        )

        return r.json()["choices"][0]["message"]["content"]

    except:

        return text

# ────────────────────────────────────────────────
# التبويبات الرئيسية

main_tab1,main_tab2,main_tab3,main_tab4,main_tab5,main_tab6,main_tab7,main_tab8 = st.tabs([
"المساعد الذكي",
"ميزات الطلاب",
"الجامعة",
"الموظفين",
"الأدوات",
"أفكار الدراسة",
"السجل",
"اقتراحات"
])

# ────────────────────────────────────────────────
# المساعد الذكي

with main_tab1:

    st.header("مساعد الواجبات")

    question=st.text_area("اكتب السؤال")

    uploaded=st.file_uploader("او ارفع صورة السؤال")

    if st.button("حل السؤال"):

        answers=send_to_all_models(question)

        merged_results={}

        for name,ans in answers.items():

            merged_results[name]=merge_with_model(ans,name)

        st.subheader("اختر افضل دمج")

        for name,ans in merged_results.items():

            with st.expander(name):

                st.write(ans)

# ────────────────────────────────────────────────
# ميزات الطلاب

with main_tab2:

    st.header("خطة دراسة تلقائية")

    grade=st.text_input("الصف")

    subjects=st.text_input("المواد")

    exam_date=st.date_input("موعد الامتحان",value=date.today())

    if st.button("انشاء خطة دراسة"):

        q=f"اصنع جدول دراسة للصف {grade} للمواد {subjects} حتى تاريخ {exam_date}"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])


    st.header("مولد اسئلة امتحان")

    subject=st.text_input("المادة")

    if st.button("توليد اسئلة"):

        q=f"انشئ اسئلة اختبار للمادة {subject} تشمل اختيار متعدد وصح وخطأ ومقالية"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# الجامعة

with main_tab3:

    st.header("اختيار التخصص المناسب")

    avg=st.number_input("معدلك")

    interests=st.text_input("اهتماماتك")

    if st.button("اقترح تخصص"):

        q=f"معدل الطالب {avg} واهتماماته {interests} اقترح تخصص جامعي"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])


    st.header("حساب المعدل الجامعي")

    grades=st.text_area("ادخل العلامات")

    if st.button("احسب المعدل"):

        q=f"احسب المعدل لهذه العلامات {grades}"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# الموظفين

with main_tab4:

    st.header("مولد سيرة ذاتية CV")

    info=st.text_area("اكتب معلوماتك")

    if st.button("انشاء CV"):

        q=f"اصنع سيرة ذاتية احترافية من هذه المعلومات {info}"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])


    st.header("تحضير مقابلة عمل")

    job=st.text_input("الوظيفة")

    if st.button("اسئلة المقابلة"):

        q=f"اعطني اسئلة مقابلة عمل لوظيفة {job} مع افضل الاجابات"

        answers=send_to_all_models(q)

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# الادوات

with main_tab5:

    st.header("بحث داخل التطبيق")

    search=st.text_input("ابحث هنا")


    st.header("الوضع الليلي")

    dark=st.toggle("تشغيل الوضع الليلي")


    st.header("رفع صورة للسؤال")

    st.file_uploader("ارفع صورة")


    st.header("تسجيل صوتي")

    st.audio_input("اسأل بالصوت")

# ────────────────────────────────────────────────
# أفكار الدراسة

with main_tab6:

    st.header("AI يشرح مثل المعلم")

    lesson=st.text_input("اكتب الدرس")

    if st.button("اشرح"):

        answers=send_to_all_models(f"اشرح هذا الدرس خطوة خطوة {lesson}")

        st.write(list(answers.values())[0])


    st.header("توصيات يومية للدراسة")

    if st.button("اعطني نصائح اليوم"):

        answers=send_to_all_models("اعطني نصائح دراسية يومية للطلاب")

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# السجل

with main_tab7:

    st.header("السجل")

    for item in st.session_state.سجل:

        st.write(item)

# ────────────────────────────────────────────────
# الاقتراحات

with main_tab8:

    st.header("اقتراحاتك")

    suggestion=st.text_area("اكتب اقتراحك")

    if st.button("ارسال الاقتراح"):

        if suggestion:

            try:

                msg=MIMEMultipart()

                msg['From']=EMAIL_ADDRESS

                msg['To']=EMAIL_ADDRESS

                msg['Subject']=f"اقتراح من {st.session_state.username}"

                msg.attach(MIMEText(suggestion,'plain'))

                server=smtplib.SMTP('smtp.gmail.com',587)

                server.starttls()

                server.login(EMAIL_ADDRESS,EMAIL_PASSWORD)

                server.send_message(msg)

                server.quit()

                st.success("تم ارسال الاقتراح")

            except Exception as e:

                st.error(str(e))

# ────────────────────────────────────────────────

st.caption("© 2026 Every Thing In Thing AI")