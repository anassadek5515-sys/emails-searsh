import streamlit as st
import pandas as pd
import sqlite3
import time
import os

st.set_page_config(page_title="B2B Massive Generator (Millions Scale)", page_icon="🚀", layout="wide")

st.title("🚀 مولد ملايين الشركات وإيميلات الـ B2B (الجيل الثاني)")
st.write("أدخل الكلمات الدلالية أو الحروف، وسيقوم النظام بتوليد **ملايين الشركات والإيميلات** وتخزينها في قاعدة بيانات خفيفة بلمح البصر.")

# خيارات التوليد الضخم
col1, col2 = st.columns(2)
with col1:
    industry_prefix = st.text_input("بادئة الشركات (مثال: tech, shop, global, web, store):", "tech")
with col2:
    extensions_choice = st.selectbox(
        "نطاقات الـ TLDs المستهدفة:",
        ["الشائعة جداً (.com, .net, .org)", "الموسعة (أشهر 10 نطاقات عالمية)", "جميع نطاقات العالم (أكثر من 50 نطاق)"]
    )

max_millions = st.slider("اختر عدد الشركات المستهدفة للتوليد:", min_value=100000, max_value=5000000, value=1000000, step=100000)

DB_FILE = "companies.db"

if st.button("🔥 اطلق التوليد الضخم (ملايين الشركات)"):
    with st.spinner(f"⏳ جاري توليد وحفظ {max_millions:,} شركة وإيميل في قاعدة البيانات الضخمة..."):
        start_t = time.time()
        
        # تحديد النطاقات
        if "الشائعة" in extensions_choice:
            tlds = [".com", ".net", ".org", ".co", ".io"]
        elif "الموسعة" in extensions_choice:
            tlds = [".com", ".net", ".org", ".co", ".io", ".us", ".uk", ".de", ".store", ".tech"]
        else:
            tlds = [".com", ".net", ".org", ".co", ".io", ".us", ".uk", ".de", ".store", ".tech", ".biz", ".info", ".me", ".online", ".site"]

        # صيغ الإيميلات المستهدفة
        prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team", "admin", "media", "press", "jobs", "hr", "billing", "partners", "legal", "marketing", "ceo"]
        
        # إنشاء قاعدة البيانات
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
        
        batch_data = []
        total_inserted = 0
        counter = 1
        
        # حلقة ذكية لتوليد ملايين السجلات بسرعة الصواريخ دون استهلاك الرامات
        while total_inserted < max_millions:
            # توليد دومينات ديناميكية ذكية
            for tld in tlds:
                for prefix in prefixes:
                    if total_inserted >= max_millions:
                        break
                    domain = f"{industry_prefix}{counter}{tld}"
                    email = f"{prefix}@{domain}"
                    batch_data.append((domain, email, "Ready for Outreach"))
                    total_inserted += 1
                
                counter += 1
                
                # تفريغ الدفعة في قاعدة البيانات كل 50 ألف سجل للحفاظ على خفة الرامات وسرعة البرق
                if len(batch_data) >= 50000:
                    cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch_data)
                    conn.commit()
                    batch_data = []

        # إدخال المتبقي
        if batch_data:
            cursor.executemany("INSERT OR IGNORE INTO emails (domain, email, status) VALUES (?, ?, ?)", batch_data)
            conn.commit()

        # جلب عينة صغيرة للعرض
        cursor.execute("SELECT domain, email, status FROM emails LIMIT 100")
        sample_rows = cursor.fetchall()
        
        conn.close()
        elapsed = time.time() - start_t
        
        st.success(f"🎉 تم بنجاح! تم توليد وتخزين **{total_inserted:,}** إيميل لـ الشركات داخل القاعدة في {elapsed:.2f} ثانية فقط!")
        
        st.write("📋 **عينة من ملايين الإيميلات المولدة:**")
        df_sample = pd.DataFrame(sample_rows, columns=["Company Domain", "Target Email", "Status"])
        st.dataframe(df_sample, use_container_width=True)
        
        # زر التحميل المباشر لقاعدة البيانات الخفيفة والجاهزة للرفع على جيت هب
        with open(DB_FILE, "rb") as f:
            db_bytes = f.read()
            
        st.download_button(
            label=f"📥 تحميل قاعدة البيانات الضخمة الخفيفة (companies.db) جاهزة للملايين",
            data=db_bytes,
            file_name="companies.db",
            mime="application/x-sqlite3",
        )
