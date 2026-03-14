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
from PIL import Image
import pytesseract
from fpdf import FPDF

load_dotenv()

# ────────────────────────────────────────────────
# المفاتيح (من .env)
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
GROK_KEY      = os.getenv("GROK_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY    = os.getenv("CLAUDE_KEY")

# إعدادات الإيميل (ضعها في Secrets في Streamlit)
EMAIL_ADDRESS = "alzoubio2010@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # ← حط App Password من جوجل هنا

# ────────────────────────────────────────────────
# حالة المستخدم (محلية فقط)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.seen_privacy = False

if "سجل" not in st.session_state:
    st.session_state.سجل = []

# ────────────────────────────────────────────────
# صفحة الخصوصية
if not st.session_state.seen_privacy:
    st.title("مرحبا بك في Every Thing In Thing AI")
    st.markdown("### نحن نحافظ على خصوصيتك 100%")
    st.markdown("""
    • لا نحفظ أسئلتك أو محادثاتك على خوادمنا  
    • كل الإجابات تتم عبر نماذج AI خارجية  
    • اقتراحاتك فقط ترسل إلى إيميل المطور بشكل آمن ومشفر  
    • تسجيل الدخول اختياري تمامًا  
    • التطبيق آمن وموثوق
    """)
    if st.button("أوافق وأفهم – ادخل التطبيق"):
        st.session_state.seen_privacy = True
        st.rerun()
    st.stop()

# ────────────────────────────────────────────────
# تسجيل الدخول البسيط
if not st.session_state.logged_in:
    st.title("تسجيل الدخول")
    st.markdown("سجل دخول عشان تحصل على تجربة مخصصة (اختياري تمامًا)")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("اسم المستخدم أو الإيميل")
        password = st.text_input("كلمة السر", type="password")
    with col2:
        if st.button("دخول"):
            if username.strip() and password.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.success(f"مرحبا {username.strip()}!")
                st.rerun()
            else:
                st.error("املأ الاسم وكلمة السر")
        if st.button("دخول كزائر"):
            st.session_state.logged_in = True
            st.session_state.username = "زائر"
            st.rerun()
    st.stop()

# ────────────────────────────────────────────────
# الواجهة الرئيسية بعد الدخول
st.title(f"مرحبا {st.session_state.username} في Every Thing In Thing AI")
st.markdown("### Every Thing In Thing AI - تطبيق للوظائف والجامعة والمدرسة")

# ────────────────────────────────────────────────
# الداتا (أضفت القطاعات والوظائف الأردنية)
DATA = {
    "موظف": {
        "تكنولوجيا المعلومات": [
            "مطور برامج / Full-Stack",
            "مطور تطبيقات موبايل",
            "أخصائي أمن سيبراني",
            "مصمم UI/UX"
        ],
        "الهندسة والإنشاءات": [
            "مهندس معماري",
            "مهندس مدني/إنشائي",
            "مهندس ميكانيكي",
            "مهندس كهربائي",
            "مدير مشاريع"
        ],
        "الطب والصحة": [
            "صيدلي",
            "ممرض/ممرضة"
        ],
        "التعليم": [
            "معلم مدرسة",
            "أستاذ جامعي"
        ],
        "المبيعات والخدمات": [
            "مندوب مبيعات",
            "أخصائي تسويق رقمي"
        ],
        "المالية": ["محاسب"],
        "القطاع الحكومي": ["موظف وزارة/بلدية"],
        "التصنيع": ["مهندس إنتاج/فني"],
        "السياحة والفنادق": ["مدير فندق/مسؤول حجوزات"],
        "الإدارة والموارد البشرية": ["مدير موارد بشرية"]
    },
    "جامعة": {
        "الكليات الطبية والصحية": "الطب البشري • طب وجراحة الأسنان • الصيدلة • التمريض • العلاج الطبيعي • العلاج الوظيفي",
        "كليات الهندسة": "مدنية • معمارية • ميكانيكية • كهربائية • حاسوب • برمجيات",
        "تكنولوجيا المعلومات": "علم الحاسوب • أمن سيبراني • ذكاء اصطناعي • علم البيانات",
        "الأعمال والاقتصاد": "محاسبة • إدارة أعمال • تمويل • تسويق رقمي",
        "الحقوق والسياسة": "قانون • علوم سياسية • علاقات دولية",
        "الفنون والتصميم": "تصميم جرافيكي • تصميم داخلي • فنون بصرية",
        "العلوم والزراعة": "رياضيات • فيزياء • كيمياء • أحياء",
        "الآداب واللغات والتربية": "عربية • إنجليزية • لغات حديثة • علم نفس"
    },
    "مدرسة": {
        "الأساسية الدنيا (1–3)": {
            "صف 1": "لغتي العربية، رياضيات، علوم، إنجليزية، تربية إسلامية",
            "صف 2": "لغتي العربية، رياضيات، علوم، إنجليزية، إسلامية",
            "صف 3": "لغتي العربية، رياضيات، علوم، إنجليزية، إسلامية"
        },
        "الأساسية العليا (4–6)": "عربية، رياضيات، علوم، إنجليزية",
        "الإعدادية (7–9)": {
            "صف 7–8": "عربية، رياضيات، علوم، إنجليزية، إسلامية، تاريخ",
            "صف 9": "كيمياء، فيزياء، أحياء، علوم أرض"
        },
        "الثانوية (10–12)": {
            "صف 10": "فيزياء، كيمياء، أحياء، علوم أرض",
            "صف 11 علمي": "رياضيات، فيزياء، كيمياء، علوم حياتية",
            "صف 11 أدبي": "عربي، رياضيات، تاريخ، جغرافيا",
            "صف 12 علمي": "رياضيات، فيزياء، كيمياء، علوم حياتية",
            "صف 12 أدبي": "عربية، تاريخ، جغرافيا، رياضيات، علوم إسلامية"
        }
    }
}

# ────────────────────────────────────────────────
# دوال الذكاء الاصطناعي (مثل السابق)
def send_to_all(query):
    system = "أجب بدقة ووضوح، خطوة بخطوة، بالعربية الفصحى أو العامية حسب السياق."
    answers = []

    if OPENAI_KEY:
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":system},{"role":"user","content":query}]
            )
            answers.append(r.choices[0].message.content.strip())
        except: pass

    if GROK_KEY:
        try:
            r = requests.post(
                "https://api.x.ai/v1/chat/completions",
                json={"model":"grok-beta","messages":[{"role":"user","content":query}]},
                headers={"Authorization": f"Bearer {GROK_KEY}"}
            )
            r.raise_for_status()
            answers.append(r.json()["choices"][0]["message"]["content"].strip())
        except: pass

    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            r = model.generate_content(system + "\n" + query)
            answers.append(r.text.strip())
        except: pass

    if DEEPSEEK_KEY:
        try:
            client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
            r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":system},{"role":"user","content":query}])
            answers.append(r.choices[0].message.content.strip())
        except: pass

    if CLAUDE_KEY:
        try:
            client = Anthropic(api_key=CLAUDE_KEY)
            msg = client.messages.create(model="claude-3-haiku-20240307", max_tokens=1024, system=system, messages=[{"role":"user","content":query}])
            answers.append(msg.content[0].text.strip())
        except: pass

    return answers

def merge_answers(answers):
    if not GROK_KEY or not answers:
        return "\n\n".join(answers) if answers else "جاري الحل..."
    prompt = f"""ادمج الإجابات التالية بطريقة واضحة:
{chr(10).join([f"[{i+1}] {ans}" for i, ans in enumerate(answers)])}"""
    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            json={"model":"grok-beta","messages":[{"role":"user","content":prompt}]},
            headers={"Authorization": f"Bearer {GROK_KEY}"}
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return "\n\n".join(answers)

# ────────────────────────────────────────────────
# التبويبات الرئيسية
tab1, tab2, tab3, tab4 = st.tabs(["الوظيفة", "الجامعة", "المدرسة", "السجل"])

with tab1:
    sector = st.selectbox("القطاع", list(DATA["موظف"].keys()))
    job = st.selectbox("الوظيفة", DATA["موظف"][sector])
    details = st.text_area("التفاصيل أو المشكلة")
    if st.button("حل المشكلة", key="btn1"):
        with st.spinner("جاري الحل..."):
            query = f"قسم موظف - {sector} - {job}\nالتفاصيل: {details}"
            answers = send_to_all(query)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80]+"...", "جواب": final})
        st.markdown(final)

with tab2:
    college = st.selectbox("الكلية", list(DATA["جامعة"].keys()))
    st.write("التخصصات:", DATA["جامعة"][college])
    spec = st.text_input("التخصص أو السؤال")
    if st.button("شرح أو إجابة", key="btn2"):
        with st.spinner("جاري الحل..."):
            query = f"تخصص جامعي: {spec} في {college}"
            answers = send_to_all(query)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80]+"...", "جواب": final})
        st.markdown(final)

with tab3:
    stage = st.selectbox("المرحلة", list(DATA["مدرسة"].keys()))
    if isinstance(DATA["مدرسة"][stage], dict):
        grade = st.selectbox("الصف", list(DATA["مدرسة"][stage].keys()))
        subject = st.text_input("المادة أو الموضوع")
        query = f"صف {grade} - {subject} في {stage}"
    else:
        subject = st.text_input("المادة أو الموضوع")
        query = f"{stage} - {subject}"
    if st.button("شرح أو حل", key="btn3"):
        with st.spinner("جاري الحل..."):
            answers = send_to_all(query)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80]+"...", "جواب": final})
        st.markdown(final)

with tab4:
    st.subheader("السجل")
    if st.session_state.سجل:
        for i, item in enumerate(reversed(st.session_state.سجل)):
            with st.expander(f"سؤال {len(st.session_state.سجل)-i}"):
                st.markdown(item["جواب"])
    else:
        st.info("السجل فارغ حاليًا")

# ────────────────────────────────────────────────
# صندوق الاقتراحات في السايدبار
with st.sidebar:
    st.header("اقتراحاتك تهمنا")
    st.markdown("اكتب أي اقتراح أو تعليق – يوصل مباشرة للمطور")
    suggestion = st.text_area("اكتب هنا...", height=120)
    if st.button("إرسال الاقتراح"):
        if suggestion.strip():
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = "alzoubio2010@gmail.com"
                msg['Subject'] = f"اقتراح جديد من {st.session_state.username}"
                body = f"المستخدم: {st.session_state.username}\n\nالاقتراح:\n{suggestion}"
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()

                st.success("تم إرسال اقتراحك بنجاح! شكرًا")
            except Exception as e:
                st.error(f"حصل خطأ أثناء الإرسال: {str(e)}")
        else:
            st.warning("اكتب اقتراحك أولاً")

st.caption("© 2026 - Every Thing In Thing AI - نحن نحافظ على خصوصيتك")