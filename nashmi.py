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
# تحميل المتغيرات
load_dotenv()

OPENAI_KEY=os.getenv("OPENAI_API_KEY")
GROK_KEY=os.getenv("GROK_API_KEY")
GEMINI_KEY=os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY=os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY=os.getenv("CLAUDE_API_KEY")

EMAIL_ADDRESS=os.getenv("EMAIL_ADDRESS","alzoubio2010@gmail.com")
EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD")

# ────────────────────────────────────────────────
# بيانات الوظائف والجامعة والمدرسة

DATA={
"موظف":{
"تكنولوجيا المعلومات":[
"مطور برامج",
"مطور تطبيقات موبايل",
"أخصائي أمن سيبراني",
"مصمم UI/UX"
],
"الهندسة":[
"مهندس مدني",
"مهندس معماري",
"مهندس كهرباء",
"مهندس ميكانيك"
],
"التعليم":[
"معلم مدرسة",
"أستاذ جامعي"
]
},

"جامعة":{
"كليات الهندسة":"مدنية • معمارية • ميكانيكية • كهربائية • برمجيات • ميكاترونكس",
"تكنولوجيا المعلومات":"علم الحاسوب • ذكاء اصطناعي • أمن سيبراني • علم البيانات",
"الأعمال":"محاسبة • إدارة أعمال • تسويق • اقتصاد",
"الطب":"طب بشري • طب اسنان • صيدلة • تمريض"
},

"مدرسة":{
"الأساسية الدنيا":{
"صف1":"عربي • رياضيات • علوم • انجليزي",
"صف2":"عربي • رياضيات • علوم • انجليزي",
"صف3":"عربي • رياضيات • علوم • انجليزي"
},
"الأساسية العليا":"عربي • رياضيات • علوم • انجليزي • اجتماعيات",
"الإعدادية":{
"صف7":"رياضيات • علوم • عربي • انجليزي",
"صف8":"رياضيات • علوم • عربي • انجليزي",
"صف9":"فيزياء • كيمياء • احياء • رياضيات"
},
"الثانوية":{
"صف10":"رياضيات • فيزياء • كيمياء • عربي",
"صف11 علمي":"رياضيات • فيزياء • كيمياء • احياء",
"صف11 أدبي":"تاريخ • جغرافيا • فلسفة",
"صف12 علمي":"رياضيات • فيزياء • كيمياء",
"صف12 أدبي":"تاريخ • جغرافيا"
}
}
}

# ────────────────────────────────────────────────
# حالات التطبيق

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
    st.session_state.username=None

if "سجل" not in st.session_state:
    st.session_state.سجل=[]

# ────────────────────────────────────────────────
# تسجيل الدخول

if not st.session_state.logged_in:

    st.title("تسجيل الدخول")

    user=st.text_input("اسم المستخدم")
    pwd=st.text_input("كلمة السر",type="password")

    if st.button("دخول"):

        if user and pwd:

            st.session_state.logged_in=True
            st.session_state.username=user
            st.rerun()

    if st.button("الدخول كزائر"):

        st.session_state.logged_in=True
        st.session_state.username="زائر"
        st.rerun()

    st.stop()

# ────────────────────────────────────────────────
# ارسال السؤال للنماذج

def send_to_models(query):

    answers={}

    if OPENAI_KEY:
        try:
            client=OpenAI(api_key=OPENAI_KEY)
            r=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":query}]
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
# واجهة التطبيق

st.title(f"مرحبا {st.session_state.username} في Every Thing In Thing AI")

# التبويبات

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9=st.tabs([
"المساعد الذكي",
"الوظائف",
"الجامعة",
"المدرسة",
"ميزات الطلاب",
"الموظفين",
"الأدوات",
"السجل",
"الاقتراحات"
])

# ────────────────────────────────────────────────
# المساعد الذكي

with tab1:

    st.header("مساعد الواجبات")

    question=st.text_area("اكتب السؤال او المشكلة")

    st.write("رفع صورة السؤال")
    image=st.file_uploader("اختر صورة")

    st.write("التقاط صورة بالكاميرا")
    camera=st.camera_input("التقط صورة للسؤال")

    if st.button("حل السؤال"):

        answers=send_to_models(question)

        for name,ans in answers.items():

            with st.expander(name):
                st.write(ans)

# ────────────────────────────────────────────────
# الوظائف

with tab2:

    sector=st.selectbox("القطاع",list(DATA["موظف"].keys()))

    job=st.selectbox("الوظيفة",DATA["موظف"][sector])

    details=st.text_area("اكتب المشكلة او السؤال")

    if st.button("حل المشكلة"):

        q=f"مشكلة في وظيفة {job} في قطاع {sector}: {details}"

        answers=send_to_models(q)

        for name,ans in answers.items():

            with st.expander(name):
                st.write(ans)

# ────────────────────────────────────────────────
# الجامعة

with tab3:

    college=st.selectbox("الكلية",list(DATA["جامعة"].keys()))

    st.write("التخصصات:")

    st.write(DATA["جامعة"][college])

    spec=st.text_input("السؤال عن التخصص")

    if st.button("اسأل"):

        q=f"تخصص جامعي {spec} في كلية {college}"

        answers=send_to_models(q)

        for name,ans in answers.items():

            with st.expander(name):
                st.write(ans)

# ────────────────────────────────────────────────
# المدرسة

with tab4:

    stage=st.selectbox("المرحلة",list(DATA["مدرسة"].keys()))

    if isinstance(DATA["مدرسة"][stage],dict):

        grade=st.selectbox("الصف",list(DATA["مدرسة"][stage].keys()))

        st.write("المواد:")
        st.write(DATA["مدرسة"][stage][grade])

        subject=st.text_input("المادة او السؤال")

        query=f"صف {grade} مادة {subject}"

    else:

        st.write(DATA["مدرسة"][stage])

        subject=st.text_input("المادة او السؤال")

        query=f"مرحلة {stage} مادة {subject}"

    if st.button("شرح"):

        answers=send_to_models(query)

        for name,ans in answers.items():

            with st.expander(name):
                st.write(ans)

# ────────────────────────────────────────────────
# ميزات الطلاب

with tab5:

    st.header("خطة دراسة")

    grade=st.text_input("الصف")
    subjects=st.text_input("المواد")
    exam=st.date_input("موعد الامتحان",value=date.today())

    if st.button("انشاء الخطة"):

        q=f"اصنع جدول دراسة للصف {grade} للمواد {subjects} حتى تاريخ {exam}"

        answers=send_to_models(q)

        st.write(list(answers.values())[0])

    st.header("مولد اسئلة")

    subject=st.text_input("المادة")

    if st.button("توليد"):

        q=f"انشئ اسئلة اختبار للمادة {subject}"

        answers=send_to_models(q)

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# الموظفين

with tab6:

    info=st.text_area("معلوماتك لانشاء CV")

    if st.button("انشاء CV"):

        answers=send_to_models(f"اكتب سيرة ذاتية احترافية من هذه المعلومات {info}")

        st.write(list(answers.values())[0])

# ────────────────────────────────────────────────
# الادوات

with tab7:

    st.header("بحث")

    st.text_input("ابحث داخل التطبيق")

    st.header("الوضع الليلي")

    st.toggle("تشغيل")

    st.header("تسجيل صوت")

    st.audio_input("اسأل بالصوت")

# ────────────────────────────────────────────────
# السجل

with tab8:

    st.header("السجل")

    for item in st.session_state.سجل:

        st.write(item)

# ────────────────────────────────────────────────
# الاقتراحات

with tab9:

    suggestion=st.text_area("اكتب اقتراحك")

    if st.button("ارسال الاقتراح"):

        try:

            msg=MIMEMultipart()
            msg['From']=EMAIL_ADDRESS
            msg['To']=EMAIL_ADDRESS
            msg['Subject']="اقتراح جديد"

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