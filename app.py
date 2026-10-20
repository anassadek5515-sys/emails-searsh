import streamlit as st
import sqlite3
import os
import base64
import requests
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="B2B Empire Command Center", page_icon="🚀", layout="wide")

st.title("🚀 لوحة قيادة الإمبراطورية والتحليلات الحية (B2B Command Center)")
st.write("متابعة حية لحالة الإيميلات، الردود، والرسومات البيانية لأداء الحملات الصاروخية!")

DB_FILE = "companies.db"

# سحب بيانات الأمان
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception:
    GITHUB_TOKEN = ""
    REPO_OWNER = ""
    REPO_NAME = ""

# زرار لتحديث وسحب أحدث حالة لقاعدة البيانات من جيت هب
if st.sidebar.button("🔄 مزامنة وجلب أحدث البيانات من السيرفر"):
    if GITHUB_TOKEN and REPO_OWNER and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DB_FILE}"
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                file_content = base64.b64decode(res.json()["content"])
                with open(DB_FILE, "wb") as f:
                    f.write(file_content)
                st.sidebar.success("✅ تم تحديث بيانات اللوحة بنجاح!")
            else:
                st.sidebar.warning("⚠️ لم يتم العثور على ملف قاعدة البيانات في المستودع بعد.")
        except Exception as e:
            st.sidebar.error(f"❌ خطأ في الجلب: {e}")

# عرض التحليلات والرسومات البيانية إذا كانت القاعدة موجودة
if os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM companies", conn)
    conn.close()

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    total_count = len(df)
    ready_count = len(df[df['status'] == 'Ready']) if 'status' in df.columns else 0
    sent_count = len(df[df['status'] == 'Sent']) if 'status' in df.columns else 0
    replied_count = len(df[df['status'] == 'Replied']) if 'status' in df.columns else 0

    col1.metric("📊 إجمالي الـ Leads", f"{total_count:,}")
    col2.metric("⏳ الجاهز للإرسال (Ready)", f"{ready_count:,}")
    col3.metric("🚀 الإيميلات المرسلة (Sent)", f"{sent_count:,}")
    col4.metric("💬 الردود والصفقات (Replied)", f"{replied_count:,}")

    st.markdown("---")
    st.subheader("📈 التحليلات البيانية لحالة الإرسال")
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
    
    st.markdown("---")
    st.subheader("💬 صندوق الردود وصياغة الصفقات الذكية")
    company_reply = st.text_area("أدخل رد الشركة هنا لنقوم بصياغة الرد المناسب وقفل الصفقة:")
    if st.button("✨ صياغة الرد الذكي للقفل"):
        if company_reply.strip():
            st.info("🤖 جارٍ تحليل الرد وصياغة أفضل استراتيجية لإغلاق الصفقة...")
            # هنا هنربط الذكاء الاصطناعي لصياغة الرد المقترح
            st.success("💡 الرد المقترح: شكراً لاهتمامكم... بناءً على طلبكم يمكننا البدء فوراً بالعرض الخاص...")
        else:
            st.warning("⚠️ يرجى إدخال رد الشركة أولاً.")

else:
    st.info("ℹ️ قاعدة البيانات غير محملة محلياً. اضغط على زر المزامنة في القائمة الجانبية لجلب البيانات وعرض الرسومات البيانية.")

st.markdown("---")
st.subheader("⚡ مولد الدفعات الجديدة والتحكم")
industry = st.text_input("بادئة الشركات (مثال: global, tech):", "tech")
total_leads = st.number_input("عدد الإيميلات المطلوبة للدفعة:", min_value=1000, max_value=2000000, value=50000, step=5000)

if st.button("🚀 توليد ورفع دفعة جديدة"):
    # [كود التوليد والرفع السابق هنا]
    pass
