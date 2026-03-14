import streamlit as st
import os
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import concurrent.futures
from dotenv import load_dotenv
import requests

load_dotenv()

# المفاتيح مخفية تمامًا (تجي من .env فقط)
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
GROK_KEY      = os.getenv("GROK_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_KEY    = os.getenv("CLAUDE_API_KEY")

# حفظ السجل (الهيستوري)
if "سجل" not in st.session_state:
    st.session_state.سجل = []

# ====================== البيانات الكاملة (مرجع داخلي) ======================
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
        "الفنون والتصميم": "تصميم جرافيكي • تصميم داخلي • تصميم أزياء • فنون بصرية • موسيقى • دراما • رسوم متحركة",
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

# ====================== إرسال السؤال لكل النماذج (مخفي تمامًا) ======================
def send_to_all(query):
    system = "أجب بدقة ووضوح، خطوة بخطوة."

    answers = []

    # ChatGPT (OpenAI)
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":system},{"role":"user","content":query}])
            answers.append(r.choices[0].message.content.strip())
        except: pass

    # Grok (xAI)
    if grok_key:
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions", json={"model":"grok-beta","messages":[{"role":"user","content":query}]}, headers={"Authorization": f"Bearer {grok_key}"})
            r.raise_for_status()
            answers.append(r.json()["choices"][0]["message"]["content"].strip())
        except: pass

    # Gemini
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            r = model.generate_content(system + "\n" + query)
            answers.append(r.text.strip())
        except: pass

    # DeepSeek
    if deepseek_key:
        try:
            client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
            r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":system},{"role":"user","content":query}])
            answers.append(r.choices[0].message.content.strip())
        except: pass

    # Claude
    if claude_key:
        try:
            client = Anthropic(api_key=claude_key)
            msg = client.messages.create(model="claude-3-haiku-20240307", max_tokens=1024, system=system, messages=[{"role":"user","content":query}])
            answers.append(msg.content[0].text.strip())
        except: pass

    return answers

# ====================== دمج الإجابات بـ Grok (مخفي) ======================
def merge_answers(answers):
    if not grok_key or not answers:
        return "\n\n".join(answers) if answers else "جاري الحل..."

    prompt = f"""ادمج الإجابات التالية بطريقتين واضحتين:
**الطريقة 1 (البسيطة والسهلة):** إجابة قصيرة، سريعة الفهم، تركز على الأساسيات فقط، بالعامية الأردنية، صحيحة 100%.
**الطريقة 2 (التفصيلية):** إجابة كاملة، دقيقة 100%، مرتبة بعناوين فرعية ونقاط، تشمل كل التفاصيل المهمة.

الإجابات:
{chr(10).join([f"[{i+1}] {ans}" for i, ans in enumerate(answers)])}"""

    try:
        r = requests.post("https://api.x.ai/v1/chat/completions", 
                          json={"model":"grok-beta","messages":[{"role":"user","content":prompt}]},
                          headers={"Authorization": f"Bearer {grok_key}"})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return "\n\n".join(answers) + "\n\n(الإجابات الخام)"

# ====================== الواجهة النظيفة (لا أي تلميح للمستخدم) ======================
st.title("NASHMI")

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

st.caption("© 2026")