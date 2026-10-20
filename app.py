import streamlit as st
import pandas as pd
import sqlite3
import time
import os

st.set_page_config(page_title="B2B Massive Lead Generator (SQLite Engine)", page_icon="🚀", layout="wide")

st.title("🚀 منصة صيد وتوليد العملاء (إصدار قواعد البيانات الخفيفة للملايين)")
st.write("أدخل الدومينات أو اشرع في التوليد الضخمي، وسيقوم النظام بتخزين ملايين الإيميلات في قاعدة بيانات محلية خفيفة للغاية تمنع ثقل المتصفح.")

# زر أو مساحة لإدخال النطاقات
domains_input = st.text_area(
    "أدخل النطاقات المستهدفة (كل نطاق في سطر، يمكنك لصق آلاف الدومينات هنا):",
    "gymshark.com\nallbirds.com\nfashionnova.com\nkyliecosmetics.com\nblendjet.com\nruggable.com"
)

prefixes_option = st.selectbox(
    "اختر نطاق صيغ الإيميلات المستهدفة لكل شركة:",
    [
        "الأساسية (support, contact, hello, sales, info)",
        "الموسعة (support, contact, hello, sales, info, founders, team, admin, media, press, jobs, hr)",
        "الشاملة لكل الاحتمالات (أكثر من 15 صيغة لكل شركة)"
    ]
)

DB_FILE = "companies.db"

if st.button("🔥 توليد وبناء قاعدة البيانات الضخمة (الملايين)"):
    if not domains_input:
        st.warning("⚠️ برجاء إدخال نطاق واحد على الأقل.")
    else:
        with st.spinner("⏳ جاري توليد وحفظ ملايين البيانات في قاعدة البيانات المحلية بكفاءة فائقة..."):
            start_t = time.time()
            domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
            
            # تحديد الصيغ
            if "الأساسية" in prefixes_option:
                prefixes = ["support", "contact", "hello", "sales", "info"]
            elif "الموسعة" in prefixes_option:
                prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team", "admin", "media", "press", "jobs", "hr"]
            else:
                prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team", "admin", "media", "press", "jobs", "hr", "billing", "partners", "legal", "marketing", "ceo"]
            
            # إنشاء قاعدة بيانات SQLite خفيفة
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE) # إعادة ضبط لقاعدة جديدة نظيفة
                
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # إنشاء الجدول مع فهرسة سريعة للبحث (Indexing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT,
                    email TEXT UNIQUE,
                    status TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON emails(email);")
            
            # الإدخال على دفعات (Batch Insert) لسرعة البرق وتوفير الذاكرة
            batch_data = []
            total_inserted = 0
            
            for domain in domains:
                for prefix in prefixes:
                    email = f"{prefix}@{domain}"
                    batch_data.append((domain, email, "Ready for Outreach"))
                    
                    # تفريغ الدفعة كل 10,000 سجل للحفاظ على خفة الرامات
                    if len(batch_data) >= 10000:
                        cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch_data)
                        conn.commit()
                        total_inserted += len(batch_data)
                        batch_data = []
            
            # إدخال المتبقي
            if batch_data:
                cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch_data)
                conn.commit()
                total_inserted += len(batch_data)
            
            # جلب عينة صغيرة للعرض البصري فقط (أول 100 سجل) بدون ثقل
            cursor.execute("SELECT domain, email, status FROM emails LIMIT 100")
            sample_rows = cursor.fetchall()
            
            conn.close()
            elapsed = time.time() - start_t
            
            st.success(f"🎉 تم بنجاح! تم توليد وتخزين {total_inserted:,} إيميل مستهدف داخل قاعدة البيانات الخفيفة في {elapsed:.2f} ثانية.")
            
            # عرض عينة مصغرة سريعة للمستخدم
            st.write("📋 **عينة من الإيميلات المولدة:**")
            df_sample = pd.DataFrame(sample_rows, columns=["Company Domain", "Target Email", "Status"])
            st.dataframe(df_sample, use_container_width=True)
            
            # زر تحميل قاعدة البيانات الخفيفة جاهزة (`companies.db`) لتشغيلها مباشرة مع worker.py
            with open(DB_FILE, "rb") as f:
                db_bytes = f.read()
                
            st.download_button(
                label=f"📥 تحميل قاعدة البيانات الخفيفة الكاملة (companies.db)",
                data=db_bytes,
                file_name="companies.db",
                mime="application/x-sqlite3",
            )
