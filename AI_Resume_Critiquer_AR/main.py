import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", layout="centered")

st.title("ناقد السيرة الذاتية بالذكاء الاصطناعي")
st.markdown("ارفع سيرتك الذاتية واحصل على ملاحظات مدعومة بالذكاء الاصطناعي مُصممة خصيصًا لتناسب احتياجاتك!")

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_flie = st.file_uploader("ارفع سيرتك الذاتية (بصيغة PDF أو TXT)", type=["pdf", "txt"])
job_role = st.text_input("أدخل الوظيفة التي تستهدفها (اختياري)")

analyze = st.button("تحليل السيرة الذاتية")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_flie.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_flie:
    try:
        file_content = extract_text_from_file(uploaded_flie)

        if not file_content.strip():
            st.error("File does not have any contnet ...")
            st.stop()

        prompt = f""" الرجاء تحليل هذه السيرة الذاتية وتقديم ملاحظات بنّاءة.
    ركّز على الجوانب التالية:
    1. وضوح المحتوى وقوة التأثير
    2. عرض المهارات
    3. وصف الخبرات
    4. تحسينات محددة لوظيفة {job_role if job_role else 'طلبات التوظيف العامة'}

    محتوى السيرة الذاتية:
    {file_content}

    الرجاء تقديم التحليل بصيغة واضحة ومنظمة مع توصيات محددة."""
    
        client = OpenAI(api_key=OPEN_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content" : "أنت خبير في مراجعة السير الذاتية ولديك سنوات من الخبرة في الموارد البشرية والتوظيف."},
                {"role" : "user", "content" : prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occured: {str(e)}")

