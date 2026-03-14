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

# ────────────────────────────────────────────────
# تحميل المتغيرات من .env
load_dotenv()

# المفاتيح (من .env)
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
GROK_KEY      = os.getenv("GROK_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY    = os.getenv("CLAUDE_API_KEY")

# إعدادات الإيميل (ضعها في Secrets في Streamlit أو في .env)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "alzoubio2010@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # ← حط App Password من جوجل هنا

# ────────────────────────────────────────────────
# حالة المستخدم (محلية فقط – ما بنخزن شيء على السيرفر)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.seen_privacy = False

if "سجل" not in st.session_state:
    st.session_state.سجل = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

# ────────────────────────────────────────────────
# صفحة الخصوصية (إجبارية أول مرة)
if not st.session_state.seen_privacy:
    st.title("مرحبا بك في Every Thing In Thing AI")
    st.markdown("### نحن نحافظ على خصوصيتك 100%")
    st.markdown("""
    • لا نحفظ أسئلتك أو محادثاتك على خوادمنا  
    • كل الإجابات تتم عبر نماذج AI خارجية (ChatGPT، Claude، Gemini، Grok، DeepSeek)  
    • اقتراحاتك فقط ترسل إلى إيميل المطور بشكل آمن ومشفر  
    • تسجيل الدخول اختياري تمامًا وما بنخزنش أي بيانات شخصية  
    • التطبيق آمن وموثوق، وكل شيء يتم معالجته في الوقت الفعلي
    """)
    if st.button("أوافق وأفهم – ادخل التطبيق"):
        st.session_state.seen_privacy = True
        st.rerun()
    st.stop()

# ────────────────────────────────────────────────
# تسجيل الدخول البسيط (محلي – بدون حفظ على السيرفر)
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
st.markdown("Every Thing In Thing AI هو أفضل تطبيق للمساعدة في الوظائف والدراسة في الأردن")

# ────────────────────────────────────────────────
# الداتا الكاملة (الوظائف + الجامعات + المدارس)
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
        "الكليات الطبية والصحية": "الطب البشري • طب وجراحة الأسنان • دكتور صيدلة • الصيدلة • التمريض • القبالة • العلاج الطبيعي • العلاج الوظيفي • الأطراف الصناعية • السمع والنطق • البصريات • الأشعة التشخيصية • تكنولوجيا المختبرات • الإسعاف والطوارئ • الصحة العامة • التغذية السريرية • تكنولوجيا صناعة الأسنان",
        "كليات الهندسة": "مدنية • معمارية • ميكانيكية • كهربائية • حاسوب • برمجيات • ميكاترونكس • طبية حيوية • صناعية • كيميائية • طاقة متجددة • عمارة داخلية • اتصالات • طيران • تعدين • مياه وبيئة",
        "تكنولوجيا المعلومات": "علم الحاسوب • أمن سيبراني • ذكاء اصطناعي • علم البيانات • حوسبة سحابية • روبوتات • نظم معلومات حاسوبية • نظم معلومات إدارية • برمجيات تقنية • واقع افتراضي/معزز • تطوير ألعاب • بلوكشين • وسائط متعددة",
        "الأعمال والاقتصاد": "محاسبة • إدارة أعمال • تمويل ومصارف • تسويق رقمي • اقتصاد • إدارة مستشفيات • سلاسل توريد ولوجستيات • تجارة إلكترونية • إدارة فنادق وسياحة • محاسبة وقانون تجاري • موارد بشرية • مخاطر وتأمين",
        "الحقوق والسياسة": "قانون • علوم سياسية • علاقات دولية • دراسات استراتيجية وأمنية",
        "الفنون والتصميم": "تصميم جرافيكي • تصميم داخلي • تصميز أزياء • فنون بصرية • موسيقى • دراما • رسوم متحركة",
        "العلوم والزراعة": "رياضيات • فيزياء • كيمياء • أحياء • جيولوجيا • تكنولوجيا حيوية • إنتاج نباتي ووقاية • إنتاج حيواني • تغذية وتصنيع غذائي • طب بيطري",
        "الآداب واللغات والتربية": "عربية وآدابها • إنجليزية وترجمة • لغات حديثة • علم نفس • علم اجتماع • عمل اجتماعي • تاريخ وجغرافيا • تربية خاصة • معلم صف • رياض أطفال • إرشاد نفسي وتربوي • صحافة وإعلام رقمي"
    },
    "مدرسة": {
        "الأساسية الدنيا (1–3)": {
            "صف 1": "لغتي العربية، رياضيات، علوم، إنجليزية، تربية إسلامية، فنية، رياضية، مهارات رقمية",
            "صف 2": "لغتي العربية، رياضيات، علوم، إنجليزية، إسلامية، اجتماعية، فنية، رياضية",
            "صف 3": "لغتي العربية، رياضيات، علوم، إنجليزية، إسلامية، اجتماعية، فنية"
        },
        "الأساسية العليا (4–6)": "عربية، رياضيات، علوم، إنجليزية، إسلامية، اجتماعيات، مهارات رقمية، تربية مهنية",
        "الإعدادية (7–9)": {
            "صف 7–8": "عربية، رياضيات، علوم، إنجليزية، إسلامية، تاريخ، جغرافيا، وطنية، ثقافة مالية، مهنية، حاسوب",
            "صف 9": "كيمياء، فيزياء، أحياء، علوم أرض، رياضيات، عربية، إنجليزية، إسلامية، تاريخ، جغرافيا، ثقافة مالية"
        },
        "الثانوية (10–12)": {
            "صف 10": "فيزياء، كيمياء، أحياء، علوم أرض، رياضيات، عربية، إنجليزية، إسلامية، تاريخ، جغرافيا، مهارات مسار",
            "صف 11 علمي": "رياضيات علمي، فيزياء، كيمياء، علوم حياتية، علوم أرض، عربية مشترك، إنجليزية، إسلامية، تاريخ أردن",
            "صف 11 أدبي": "عربي تخصص، رياضيات أدبي، تاريخ عرب، جغرافيا، فلسفة، علم نفس، عربية مشترك، إنجليزية، إسلامية، تاريخ أردن",
            "صف 12 علمي": "رياضيات، فيزياء، كيمياء، علوم حياتية، عربية، إنجليزية، إسلامية، تاريخ أردن (+ مواد الحقل)",
            "صف 12 أدبي": "عربية تخصص، تاريخ عرب وعالم، جغرافيا، رياضيات أدبي، علوم إسلامية، عربية مشترك، إنجليزية، إسلامية، تاريخ أردن"
        }
    }
}

# ────────────────────────────────────────────────
# إرسال السؤال لكل النماذج
def send_to_all(query):
    system = "أجب بدقة ووضوح، خطوة بخطوة، بالعربية الفصحى أو العامية حسب السياق."

    answers = []

    if OPENAI_KEY:
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":system},{"role":"user","content":query}])
            answers.append(r.choices[0].message.content.strip())
        except Exception:
            pass

    if GROK_KEY:
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions", json={"model":"grok-beta","messages":[{"role":"user","content":query}]}, headers={"Authorization": f"Bearer {GROK_KEY}"})
            r.raise_for_status()
            answers.append(r.json()["choices"][0]["message"]["content"].strip())
        except Exception:
            pass

    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            r = model.generate_content(system + "\n" + query)
            answers.append(r.text.strip())
        except Exception:
            pass

    if DEEPSEEK_KEY:
        try:
            client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
            r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":system},{"role":"user","content":query}])
            answers.append(r.choices[0].message.content.strip())
        except Exception:
            pass

    if CLAUDE_KEY:
        try:
            client = Anthropic(api_key=CLAUDE_KEY)
            msg = client.messages.create(model="claude-3-haiku-20240307", max_tokens=1024, system=system, messages=[{"role":"user","content":query}])
            answers.append(msg.content[0].text.strip())
        except Exception:
            pass

    return answers

# ────────────────────────────────────────────────
# دمج الإجابات بـ Grok
def merge_answers(answers):
    if not GROK_KEY or not answers:
        return "\n\n".join(answers) if answers else "جاري الحل..."

    prompt = f"""ادمج الإجابات التالية بطريقتين واضحتين:
**الطريقة 1 (البسيطة):** إجابة قصيرة، سريعة الفهم، بالعامية الأردنية.
**الطريقة 2 (التفصيلية):** إجابة كاملة، دقيقة، مرتبة بعناوين ونقاط.

الإجابات:
{chr(10).join([f"[{i+1}] {ans}" for i, ans in enumerate(answers)])}"""

    try:
        r = requests.post("https://api.x.ai/v1/chat/completions", json={"model":"grok-beta","messages":[{"role":"user","content":prompt}]}, headers={"Authorization": f"Bearer {GROK_KEY}"})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "\n\n".join(answers)

# ────────────────────────────────────────────────
# التبويبات (الآن أضفت تبويب "اقتراحات" بحيث زرّ الاقتراحات صار تبويب عادي)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["الوظيفة", "الجامعة", "المدرسة", "السجل", "اقتراحات"])

with tab1:
    sector = st.selectbox("القطاع", list(DATA["موظف"].keys()))
    job = st.selectbox("الوظيفة", DATA["موظف"][sector])
    details = st.text_area("التفاصيل أو المشكلة")
    if st.button("حل المشكلة", key="btn1"):
        with st.spinner("جاري الحل..."):
            query = f"قسم موظف - {sector} - {job}\nالتفاصيل: {details}"
            answers = send_to_all(query)
            final = merge_answers(answers)
            st.session_state.سجل.append({"سؤال": query[:80] + "...", "جواب": final})
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
            st.session_state.سجل.append({"سؤال": query[:80] + "...", "جواب": final})
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
            st.session_state.سجل.append({"سؤال": query[:80] + "...", "جواب": final})
        st.markdown(final)

with tab4:
    st.subheader("السجل")
    if st.session_state.سجل:
        for i, item in enumerate(reversed(st.session_state.سجل)):
            with st.expander(f"سؤال {len(st.session_state.سجل)-i}"):
                st.markdown(item["جواب"])
    else:
        st.info("السجل فارغ حاليًا")

with tab5:
    st.header("اقتراحاتك تهمنا")
    st.markdown("اكتب أي اقتراح أو تعليق – يوصل مباشرة للمطور")
    suggestion = st.text_area("اكتب هنا...", height=160, key="suggestion_area")

    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("إرسال الاقتراح", key="send_suggestion"):
            if suggestion.strip():
                # حفظ محلي
                st.session_state.suggestions.append({
                    "from": st.session_state.username,
                    "text": suggestion.strip()
                })

                # إرسال إيميل
                try:
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_ADDRESS
                    msg['To'] = EMAIL_ADDRESS
                    msg['Subject'] = f"اقتراح جديد من {st.session_state.username}"

                    body = f"المستخدم: {st.session_state.username}\n\nالاقتراح:\n{suggestion.strip()}"
                    msg.attach(MIMEText(body, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
                    server.starttls()
                    if not EMAIL_PASSWORD:
                        raise ValueError("لم يتم توفير كلمة سر الإيميل. ضع EMAIL_PASSWORD في المتغيرات البيئية (App Password).")
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)
                    server.quit()

                    st.success("تم إرسال اقتراحك بنجاح! شكرًا")
                    # تنظيف الحقل بعد الإرسال
                    st.session_state.suggestion_area = ""
                except Exception as e:
                    st.error(f"حصل خطأ أثناء الإرسال: {str(e)}")
            else:
                st.warning("اكتب اقتراحك أولاً")

    # عرض الاقتراحات المحفوظة محليًا (للعرض فقط، لا تُنشر)
    if st.session_state.suggestions:
        st.markdown("---")
        st.subheader("اقتراحات مرسلة محليًا (عرض مؤقت)")
        for i, s in enumerate(reversed(st.session_state.suggestions), 1):
            st.write(f"{i}. من: {s['from']}")
            st.write(s['text'])
            st.write("---")

# ────────────────────────────────────────────────
# تذييل
st.caption("© 2026 - Every Thing In Thing AI - نحن نحافظ على خصوصيتك")
