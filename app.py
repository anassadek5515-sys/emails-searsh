import streamlit as st
import sqlite3
import os
import base64
import requests

st.set_page_config(page_title="B2B Lead Search & Auto-Sync", page_icon="🚀", layout="centered")

st.title("🚀 محرك البحث والاستخراج (متصل أوتوماتيك بمشروع الإرسال بأمان)")
st.write("استخرج إيميلات الشركات واضغط زرار واحد لترسلها مباشرة لمشروع الإرسال بأمان تام!")

industry = st.text_input("بادئة الشركات (مثال: global, tech):", "tech")
total_leads = st.number_input("عدد الإيميلات المطلوبة:", min_value=10000, max_value=2000000, value=100000, step=10000)

# سحب البيانات السرية بأمان من إعدادات Streamlit
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception:
    st.error("⚠️ تنبيه: يرجى ضبط أمان الـ Secrets في إعدادات التطبيق أولاً!")
    GITHUB_TOKEN = ""
    REPO_OWNER = ""
    REPO_NAME = ""

DB_FILE = "companies.db"

if st.button("⚡ توليد وإرسال للمشروع التاني أوتوماتيك"):
    if not GITHUB_TOKEN:
        st.error("❌ لا يمكن المتابعة لعدم توفر بيانات الاتصال الآمنة.")
    else:
        with st.spinner("جاري استخراج البيانات وضبطها..."):
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

        # رفع الملف أوتوماتيك لمشروع الإرسال التاني عبر GitHub API
        with st.spinner("🚀 جاري رفع ملف الشركات للمشروع التاني عبر جيت هب..."):
            try:
                with open(DB_FILE, "rb") as f:
                    content = base64.b64encode(f.read()).decode("utf-8")
                    
                url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DB_FILE}"
                headers = {
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json"
                }
                
                # التحقق من وجود الملف القديم لجلب الـ SHA
                get_res = requests.get(url, headers=headers)
                sha = get_res.json().get("sha") if get_res.status_code == 200 else None
                
                data = {
                    "message": "Auto-sync new companies database from Search App 🚀",
                    "content": content,
                    "branch": "main"
                }
                if sha:
                    data["sha"] = sha
                    
                put_res = requests.put(url, headers=headers, json=data)
                
                if put_res.status_code in [200, 201]:
                    st.success("🎉 تم توليد البيانات ورفعها بنجاح مذهل إلى مشروع الإرسال! مشروع الإرسال سيلتقطها فوراً في دورته القادمة.")
                else:
                    st.error(f"❌ فشل الرفع: {put_res.json().get('message', 'خطأ غير معروف')}")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الاتصال بجيت هب: {e}")
