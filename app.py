import streamlit as st
import sqlite3
import os
import base64
import requests

# إعدادات صفحة الموقع
st.set_page_config(page_title="B2B Lead Search & Auto-Sync", page_icon="🚀", layout="centered")

st.title("🚀 محرك البحث والاستخراج (متصل أوتوماتيك بمشروع الإرسال)")
st.write("استخرج إيميلات الشركات واضغط زرار واحد لترسلها مباشرة لمشروع الإرسال `Sell-saas` بدون أي نقل يدوي!")

industry = st.text_input("بادئة الشركات (مثال: global, tech):", "tech")
total_leads = st.number_input(
    "عدد الإيميلات المطلوبة (يُفضل 50,000 للتجربة السريعة):", 
    min_value=1000, 
    max_value=2000000, 
    value=50000, 
    step=5000
)

# سحب بيانات الأمان السرية بأمان من إعدادات Streamlit Secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception:
    st.error("⚠️ تنبيه: يرجى ضبط أمان الـ Secrets في إعدادات التطبيق (GITHUB_TOKEN, REPO_OWNER, REPO_NAME) أولاً!")
    GITHUB_TOKEN = ""
    REPO_OWNER = ""
    REPO_NAME = ""

DB_FILE = "companies.db"

if st.button("⚡ توليد وإرسال للمشروع التاني أوتوماتيك"):
    if not GITHUB_TOKEN:
        st.error("❌ لا يمكن المتابعة لعدم توفر بيانات الاتصال الآمنة في الـ Secrets.")
    else:
        # 1. مرحلة التوليد وبناء قاعدة البيانات SQLite
        with st.spinner("جاري استخراج البيانات وضبط قاعدة البيانات المحلية..."):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT,
                    email TEXT UNIQUE,
                    status TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON emails(email);")
            
            tlds = [".com", ".net", ".org", ".co", ".io"]
            prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team"]
            
            batch = []
            count = 0
            counter = 1
            
            while count < total_leads:
                for tld in tlds:
                    for prefix in prefixes:
                        if count >= total_leads:
                            break
                        domain = f"{industry}{counter}{tld}"
                        email = f"{prefix}@{domain}"
                        batch.append((domain, email, "Ready"))
                        count += 1
                    counter += 1
                    
                    if len(batch) >= 10000:
                        cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch)
                        conn.commit()
                        batch = []
                        
            if batch:
                cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch)
                conn.commit()
                
            conn.close()

        # 2. فحص حجم الملف (لتفادي قيود جيت هب 25 ميجابايت)
        file_size_mb = os.path.getsize(DB_FILE) / (1024 * 1024)
        st.info(f"📦 حجم قاعدة البيانات التي تم توليدها: **{file_size_mb:.2f} MB**")

        if file_size_mb > 25:
            st.warning("⚠️ الملف يتجاوز 25 ميجابايت (الحد الأقصى المسموح به للـ API). يرجى تقليل عدد الإيميلات للدفعة الواحدة.")
        else:
            # 3. مرحلة الرفع الأوتوماتيكي عبر GitHub API
            with st.spinner("🚀 جاري رفع ملف الشركات لمستودع الإرسال Sell-saas عبر جيت هب..."):
                try:
                    with open(DB_FILE, "rb") as f:
                        content = base64.b64encode(f.read()).decode("utf-8")
                        
                    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DB_FILE}"
                    headers = {
                        "Authorization": f"Bearer {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github+json"
                    }
                    
                    # جلب الـ SHA للملف القديم (مطلوب من جيت هب لتحديث الملفات الموجودة)
                    get_res = requests.get(url, headers=headers)
                    sha = None
                    if get_res.status_code == 200:
                        sha = get_res.json().get("sha")
                    
                    data = {
                        "message": "Auto-sync new companies database from Search App 🚀",
                        "content": content,
                        "branch": "main"  # تأكد أن الفرع الأساسي عندك هو main أو أبدله بـ master
                    }
                    if sha:
                        data["sha"] = sha
                        
                    # إرسال طلب التحديث (PUT)
                    put_res = requests.put(url, headers=headers, json=data)
                    
                    if put_res.status_code in [200, 201]:
                        st.success("🎉 تم توليد البيانات ورفعها بنجاح مذهل إلى مستودع الإرسال `Sell-saas`! مشروع الإرسال سيلتقطها فوراً.")
                    else:
                        st.error(f"❌ فشل الرفع من جيت هب (كود: {put_res.status_code}): {put_res.json().get('message', 'خطأ غير معروف')}")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بالشبكة: {e}")
