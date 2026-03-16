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
from email.mime.image import MIMEImage
import base64
from io import BytesIO

load_dotenv()

# ====================== PWA - لتحويل الموقع إلى تطبيق ======================
st.set_page_config(page_title="Every Thing In Thing AI", page_icon="🚀", layout="wide")
st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#000000">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Every Thing In Thing AI">
""", unsafe_allow_html=True)

# ====================== المفاتيح ======================
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
GROK_KEY      = os.getenv("GROK_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY    = os.getenv("CLAUDE_API_KEY")
EMAIL_ADDRESS = "alzoubio2010@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ====================== حالة المستخدم ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.seen_privacy = False
if "سجل" not in st.session_state:
    st.session_state.سجل = []

# ====================== الخصوصية ======================
if not st.session_state.seen_privacy:
    st.title("مرحبا بك في Every Thing In Thing AI")
    st.markdown("### نحن نحافظ على خصوصيتك 100%")
    st.markdown("""
    • لا نحفظ أسئلتك أو محادثاتك  
    • كل الإجابات تتم عبر نماذج AI خارجية  
    • اقتراحاتك فقط ترسل للمطور بشكل آمن  
    • تسجيل الدخول اختياري تمامًا
    """)
    if st.button("أوافق وأفهم – ادخل التطبيق"):
        st.session_state.seen_privacy = True
        st.rerun()
    st.stop()

# ====================== تسجيل الدخول ======================
if not st.session_state.logged_in:
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم أو الإيميل")
    password = st.text_input("كلمة السر", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("دخول"):
            if username:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"مرحبا {username}!")
                st.rerun()
    with col2:
        if st.button("دخول كزائر"):
            st.session_state.logged_in = True
            st.session_state.username = "زائر"
            st.rerun()
    st.stop()

# ====================== الداتا الكاملة (مكتوبة كاملة بدون اختصار) ======================
DATA = {
    "موظف": {
        "تكنولوجيا المعلومات": [
            "مطور برامج / Full-Stack: تنظيم الكود والإصدارات، تأخير الـ Testing، توثيق الكود",
            "مطور تطبيقات موبايل: إدارة Version Control، تصدير التطبيق للاختبار",
            "أخصائي أمن سيبراني: توثيق التقارير الأمنية، جدول الاختبارات",
            "مصمم UI/UX: تنظيم ملفات التصميم، إعداد Prototype"
        ],
        "الهندسة والإنشاءات": [
            "مهندس معماري: تنظيم المخططات والإصدارات، إعداد العروض التقديمية",
            "مهندس مدني/إنشائي: حسابات الكميات، جدول الزيارات الخاصة",
            "مهندس ميكانيكي: تقارير الصيانة، تنظيم قطع الغيار",
            "مهندس كهربائي: تنظيم الرسومات الكهربائية، توثيق الاختبارات",
            "مدير مشاريع: تنظيم الجداول الزمنية الداخلية، توثيق التقارير"
        ],
        "الطب والصحة": [
            "صيدلي: تنظيم المخزون اليومي، تقارير الوصفات",
            "ممرض/ممرضة: جدولة المهام الشخصية، تنظيم ملفات المرضى"
        ],
        "التعليم": [
            "معلم مدرسة: تنظيم الخطط الدراسية، تصحيح وتوثيق الامتحانات",
            "أستاذ جامعي: إعداد المقررات، تنظيم جداول البحث"
        ],
        "المبيعات والخدمات": [
            "مندوب مبيعات: متابعة العروض الشخصية، تنظيم قاعدة العملاء",
            "أخصائي تسويق رقمي: تتبع أداء الحملات، تنظيم المحتوى"
        ],
        "المالية": ["محاسب: مطابقة الحسابات، تنظيم الفواتير"],
        "القطاع الحكومي": ["موظف وزارة/بلدية: تنظيم الملفات الداخلية، إعداد التقارير"],
        "التصنيع": ["مهندس إنتاج/فني: تنظيم خطوط الإنتاج، توثيق الصيانة"],
        "السياحة والفنادق": ["مدير فندق/مسؤول حجوزات: تنظيم الحجوزات، تقارير الأداء"],
        "الإدارة والموارد البشرية": ["مدير موارد بشرية: تنظيم ملفات الموظفين، جدولة التدريبات"]
    },
    "جامعة": {
        "الكليات الطبية والصحية": [
            "الطب البشري", "طب وجراحة الأسنان", "دكتور صيدلة", "الصيدلة", "التمريض", "القبالة القانونية",
            "العلاج الطبيعي", "العلاج الوظيفي", "الأطراف الصناعية والأجهزة المساعدة", "السمع والنطق",
            "البصريات", "الأشعة التشخيصية", "تكنولوجيا المختبرات الطبية", "الإسعاف والطوارئ",
            "الصحة العامة", "التغذية السريرية والحميات", "تكنولوجيا صناعة الأسنان"
        ],
        "كليات الهندسة": [
            "الهندسة المدنية", "الهندسة المعمارية", "الهندسة الميكانيكية", "الهندسة الكهربائية",
            "هندسة الحاسوب", "هندسة البرمجيات", "هندسة الميكاترونكس", "الهندسة الطبية الحيوية",
            "الهندسة الصناعية", "الهندسة الكيميائية", "هندسة الطاقة المتجددة", "هندسة العمارة الداخلية",
            "هندسة الاتصالات", "هندسة الطيران", "هندسة التعدين", "هندسة المياه والبيئة"
        ],
        "كليات تكنولوجيا المعلومات": [
            "علم الحاسوب", "الأمن السيبراني", "الذكاء الاصطناعي", "علم البيانات",
            "تكنولوجيا الحوسبة السحابية", "الروبوتات", "نظم المعلومات الحاسوبية",
            "نظم المعلومات الإدارية", "هندسة البرمجيات التقنية", "الواقع الافتراضي والمعزز",
            "تطوير الألعاب الإلكترونية", "بلوكشين", "الوسائط المتعددة"
        ],
        "كليات الأعمال والاقتصاد": [
            "المحاسبة", "إدارة الأعمال", "التمويل والمصارف", "التسويق الرقمي", "الاقتصاد",
            "إدارة المستشفيات", "إدارة سلاسل التوريد واللوجستيات", "التجارة الإلكترونية",
            "إدارة الفنادق والمنشآت السياحية", "إدارة الموارد البشرية", "إدارة المخاطر والتأمين"
        ],
        "كليات الحقوق والسياسة": [
            "القانون", "العلوم السياسية", "العلاقات الدولية والدبلوماسية", "الدراسات الاستراتيجية والأمنية"
        ],
        "كليات الفنون والتصميم": [
            "التصميم الجرافيكي", "التصميم الداخلي", "تصميم الأزياء", "الفنون البصرية",
            "الموسيقى", "الدراما", "الرسوم المتحركة"
        ],
        "كليات العلوم والزراعة": [
            "الرياضيات", "الفيزياء", "الكيمياء", "العلوم الحياتية", "الجيولوجيا",
            "التكنولوجيا الحيوية", "الإنتاج النباتي والوقاية", "الإنتاج الحيواني",
            "التغذية والتصنيع الغذائي", "الطب البيطري"
        ],
        "كليات الآداب واللغات والتربية": [
            "اللغة العربية وآدابها", "اللغة الإنجليزية وآدابها", "اللغات الحديثة",
            "علم النفس", "علم الاجتماع", "العمل الاجتماعي", "التاريخ والجغرافيا",
            "التربية الخاصة", "معلم الصف", "رياض الأطفال", "الإرشاد النفسي والتربوي",
            "الصحافة والإعلام الرقمي"
        ]
    },
    "مدرسة": {
        "الأساسية الدنيا (1-3)": {
            "صف 1": "لغتي العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، التربية الفنية، التربية الرياضية، المهارات الرقمية",
            "صف 2": "لغتي العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، التربية الاجتماعية، التربية الفنية، التربية الرياضية",
            "صف 3": "لغتي العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، التربية الاجتماعية، التربية الفنية"
        },
        "الأساسية العليا (4-6)": {
            "صف 4": "اللغة العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، الاجتماعيات، المهارات الرقمية، التربية المهنية",
            "صف 5": "اللغة العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، الاجتماعيات، المهارات الرقمية، التربية المهنية",
            "صف 6": "اللغة العربية، الرياضيات، العلوم، اللغة الإنجليزية، التربية الإسلامية، الاجتماعيات، المهارات الرقمية، التربية المهنية"
        },
        "الإعدادية (7-9)": {
            "صف 7": "العربية، الرياضيات، العلوم، الإنجليزية، التربية الإسلامية، التاريخ، الجغرافيا، الوطنية، الثقافة المالية، التربية المهنية، الحاسوب",
            "صف 8": "العربية، الرياضيات، العلوم، الإنجليزية، التربية الإسلامية، التاريخ، الجغرافيا، الوطنية، الثقافة المالية، التربية المهنية، الحاسوب",
            "صف 9": "الكيمياء، الفيزياء، الأحياء، علوم الأرض، الرياضيات، اللغة العربية، اللغة الإنجليزية، التربية الإسلامية، التاريخ، الجغرافيا، الثقافة المالية"
        },
        "الثانوية (10-12)": {
            "صف 10": "الفيزياء، الكيمياء، الأحياء، علوم الأرض، الرياضيات، اللغة العربية، اللغة الإنجليزية، التربية الإسلامية، التاريخ، الجغرافيا، مهارات المسار المهني",
            "صف 11 علمي": "رياضيات علمي، فيزياء، كيمياء، علوم حياتية، علوم أرض، لغة عربية مشترك، لغة إنجليزية، تربية إسلامية، تاريخ الأردن",
            "صف 11 أدبي": "عربي تخصص، رياضيات أدبي، تاريخ العرب، جغرافيا، فلسفة، علم نفس، لغة عربية مشترك، لغة إنجليزية، تربية إسلامية، تاريخ الأردن",
            "صف 12 علمي": "الرياضيات، الفيزياء، الكيمياء، العلوم الحياتية، اللغة العربية، اللغة الإنجليزية، التربية الإسلامية، تاريخ الأردن",
            "صف 12 أدبي": "اللغة العربية تخصص، تاريخ العرب والعالم، الجغرافيا، الرياضيات أدبي، العلوم الإسلامية، اللغة العربية مشترك، اللغة الإنجليزية، التربية الإسلامية، تاريخ الأردن"
        }
    }
}

# ====================== دالة الخبير المتخصص ======================
def get_expert_prompt(tab, selection):
    if tab == "الوظيفة":
        return f"أنت خبير متخصص في {selection} مع 20 سنة خبرة في الأردن. تعرف كل الكتب الجامعية، قوانين البلدية، الدفاع المدني والمواصفات الرسمية. حل أي مشكلة خطوة بخطوة بدقة 100% مع مراجع."
    elif tab == "الجامعة":
        return f"أنت أستاذ جامعي أردني متخصص في {selection}. تعرف كل الكتب المقررة في الجامعات الأردنية وتشرح حسب المنهاج الرسمي."
    elif tab == "المدرسة":
        return f"أنت معلم أردني متخصص في المرحلة أو المادة {selection}. تعرف الكتاب الرسمي من وزارة التربية بالضبط (طبعة 2025) وتشرح حسب المنهاج الأردني."
    return "أجب بدقة ووضوح، خطوة بخطوة."

# ====================== إرسال للـ5 نماذج + Vision ======================
def send_to_all(query, image_data=None, tab="", selection=""):
    system = get_expert_prompt(tab, selection)
    answers = []

    # OpenAI + Vision
    if OPENAI_KEY:
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            messages = [{"role": "system", "content": system}]
            content = [{"type": "text", "text": query}]
            if image_data:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
            messages.append({"role": "user", "content": content})
            r = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
            answers.append(r.choices[0].message.content.strip())
        except: pass

    # Gemini + Vision
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            content = [system + "\n" + query]
            if image_data:
                img_bytes = base64.b64decode(image_data)
                content.append({"mime_type": "image/jpeg", "data": img_bytes})
            r = model.generate_content(content)
            answers.append(r.text.strip())
        except: pass

    # Grok
    if GROK_KEY:
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions",
                              json={"model": "grok-beta", "messages": [{"role": "user", "content": query}]},
                              headers={"Authorization": f"Bearer {GROK_KEY}"})
            answers.append(r.json()["choices"][0]["message"]["content"].strip())
        except: pass

    # DeepSeek
    if DEEPSEEK_KEY:
        try:
            client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
            r = client.chat.completions.create(model="deepseek-chat",
                                               messages=[{"role": "system", "content": system},
                                                         {"role": "user", "content": query}])
            answers.append(r.choices[0].message.content.strip())
        except: pass

    # Claude
    if CLAUDE_KEY:
        try:
            client = Anthropic(api_key=CLAUDE_KEY)
            msg = client.messages.create(model="claude-3-haiku-20240307", max_tokens=1024,
                                         system=system, messages=[{"role": "user", "content": query}])
            answers.append(msg.content[0].text.strip())
        except: pass

    return answers

# ====================== دمج بـ Grok (3 نماذج) ======================
def merge_answers(answers):
    if not GROK_KEY or not answers:
        return "\n\n".join(answers) if answers else "جاري الحل..."
    prompt = f"""ادمج الإجابات الـ5 التالية وأعطني ثلاث نماذج:
**1. البسيطة:** عامية أردنية سريعة الفهم.
**2. التفصيلية:** كاملة مرتبة بعناوين ونقاط.
**3. الخبير الأردني:** مع مراجع كتب وقوانين رسمية.

الإجابات:
{chr(10).join([f"[{i+1}] {ans}" for i, ans in enumerate(answers)])}"""
    try:
        r = requests.post("https://api.x.ai/v1/chat/completions",
                          json={"model": "grok-beta", "messages": [{"role": "user", "content": prompt}]},
                          headers={"Authorization": f"Bearer {GROK_KEY}"})
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return "\n\n".join(answers)

# ====================== التبويبات ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👷 الوظيفة", "🎓 الجامعة", "📚 المدرسة", "📖 السجل", "💡 اقتراحات"])

# تبويب 1 الوظيفة
with tab1:
    sector = st.selectbox("القطاع", list(DATA["موظف"].keys()))
    job = st.selectbox("الوظيفة", DATA["موظف"][sector])
    col_camera, col_text = st.columns([1, 3])
    with col_camera:
        photo = st.camera_input("📷 صور المشكلة", key="camera_job")
    with col_text:
        details = st.text_area("التفاصيل أو المشكلة", height=100)
    if st.button("🔥 حل كخبير متخصص", key="btn1"):
        with st.spinner("جاري التحليل كخبير..."):
            image_data = None
            if photo:
                buffered = BytesIO()
                photo.getvalue().save(buffered, format="JPEG")
                image_data = base64.b64encode(buffered.getvalue()).decode()
            query = details if details.strip() else "حلل الصورة"
            answers = send_to_all(query, image_data, "الوظيفة", job)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80], "جواب": final})
            st.markdown(final)

# تبويب 2 الجامعة (نفس المنطق مع expert prompt)
with tab2:
    college = st.selectbox("الكلية", list(DATA["جامعة"].keys()))
    st.write("التخصصات:", DATA["جامعة"][college])
    col_camera, col_text = st.columns([1, 3])
    with col_camera:
        photo = st.camera_input("📷 صور التخصص", key="camera_uni")
    with col_text:
        spec = st.text_input("التخصص أو السؤال")
    if st.button("شرح كخبير جامعي", key="btn2"):
        with st.spinner("جاري الحل..."):
            image_data = None
            if photo:
                buffered = BytesIO()
                photo.getvalue().save(buffered, format="JPEG")
                image_data = base64.b64encode(buffered.getvalue()).decode()
            query = spec if spec.strip() else "حلل الصورة"
            answers = send_to_all(query, image_data, "الجامعة", college)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80], "جواب": final})
            st.markdown(final)

# تبويب 3 المدرسة
with tab3:
    stage = st.selectbox("المرحلة", list(DATA["مدرسة"].keys()))
    if isinstance(DATA["مدرسة"][stage], dict):
        grade = st.selectbox("الصف", list(DATA["مدرسة"][stage].keys()))
        subject = st.text_input("المادة")
        query_base = f"صف {grade} - {subject} في {stage}"
    else:
        subject = st.text_input("المادة")
        query_base = f"{stage} - {subject}"
    col_camera, col_text = st.columns([1, 3])
    with col_camera:
        photo = st.camera_input("📷 صور الدرس", key="camera_school")
    with col_text:
        pass
    if st.button("شرح كخبير مدرسي", key="btn3"):
        with st.spinner("جاري الحل..."):
            image_data = None
            if photo:
                buffered = BytesIO()
                photo.getvalue().save(buffered, format="JPEG")
                image_data = base64.b64encode(buffered.getvalue()).decode()
            answers = send_to_all(query_base, image_data, "المدرسة", stage)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query_base[:80], "جواب": final})
            st.markdown(final)

# تبويب 4 السجل
with tab4:
    st.subheader("السجل")
    if st.session_state.سجل:
        for i, item in enumerate(reversed(st.session_state.سجل)):
            with st.expander(f"سؤال {len(st.session_state.سجل)-i}"):
                st.markdown(item["جواب"])
    else:
        st.info("السجل فارغ حاليًا")

# تبويب 5 الاقتراحات
with tab5:
    st.header("اقتراحاتك تهمنا")
    suggestion = st.text_area("اكتب اقتراحك أو تعليقك", height=160)
    uploaded_files = st.file_uploader("ارفع صور أو ملفات (أكثر من واحد)", accept_multiple_files=True,
                                      type=["jpg", "jpeg", "png", "pdf"])
    if st.button("إرسال الاقتراح"):
        if suggestion.strip() or uploaded_files:
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = EMAIL_ADDRESS
                msg['Subject'] = f"اقتراح جديد من {st.session_state.username}"
                body = f"المستخدم: {st.session_state.username}\n\nالاقتراح:\n{suggestion}"
                msg.attach(MIMEText(body, 'plain'))
                if uploaded_files:
                    for file in uploaded_files:
                        msg.attach(MIMEImage(file.getvalue()))
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()
                st.success("تم الإرسال بنجاح!")
            except Exception as e:
                st.error(f"خطأ: {str(e)}")
        else:
            st.warning("اكتب اقتراح أو ارفع ملف")

st.caption("© 2026 - Every Thing In Thing AI - تطبيق أردني كامل")