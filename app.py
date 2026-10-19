import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="B2B Massive Lead Generator", page_icon="🚀", layout="wide")

st.title("🚀 منصة صيد وتوليد العملاء (إصدار الـ 100 ألف+)")
st.write("أدخل الدومينات أو ارفعها، وسيقوم النظام بتوليد القاعدة الضخمة واستخراجها في ملف CSV فوراً.")

# خيار لإدخال عدد كبير من النطاقات
domains_input = st.text_area(
    "أدخل النطاقات المستهدفة (كل نطاق في سطر، يمكنك لصق آلاف الدومينات هنا):",
    "gymshark.com\nallbirds.com\nfashionnova.com\nkyliecosmetics.com\nblendjet.com\nruggable.com"
)

# اختيار الصيغ المطلوبة
prefixes_option = st.selectbox(
    "اختر نطاق صيغ الإيميلات المستهدفة:",
    [
        "الأساسية (support, contact, hello, sales, info)",
        "الموسعة (support, contact, hello, sales, info, founders, team, admin, media, press, jobs, hr)",
        "الشاملة لكل الاحتمالات (أكثر من 15 صيغة لكل شركة)"
    ]
)

if st.button("🔥 توليد واستخراج قاعدة البيانات الضخمة"):
    if not domains_input:
        st.warning("⚠️ برجاء إدخال نطاق واحد على الأقل.")
    else:
        with st.spinner("⏳ جاري معالجة البيانات وتوليد الإيميلات بكفاءة عالية..."):
            start_t = time.time()
            domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
            
            # تحديد الصيغ بناءً على اختيار المستخدم
            if "الأساسية" in prefixes_option:
                prefixes = ["support", "contact", "hello", "sales", "info"]
            elif "الموسعة" in prefixes_option:
                prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team", "admin", "media", "press", "jobs", "hr"]
            else:
                prefixes = ["support", "contact", "hello", "sales", "info", "founders", "team", "admin", "media", "press", "jobs", "hr", "billing", "partners", "legal", "marketing", "ceo"]
            
            # توليد البيانات بطريقة سريعة جداً لا تستهلك الذاكرة
            results = []
            for domain in domains:
                for prefix in prefixes:
                    email = f"{prefix}@{domain}"
                    results.append({
                        "Company Domain": domain,
                        "Target Email": email,
                        "Status": "Ready for Outreach"
                    })
            
            df = pd.DataFrame(results)
            elapsed = time.time() - start_t
            
            st.success(f"🎉 تم بنجاح! تم توليد {len(df):,} إيميل مستهدف في {elapsed:.2f} ثانية.")
            
            # عرض عينة فقط من النتائج عشان الموقع ما يثقلش في العرض البصري
            st.write("📋 **عينة من النتائج التي تم توليدها:**")
            st.dataframe(df.head(100), use_container_width=True)
            
            # زر تحميل الملف كاملاً (حتى لو مليون سطر) بصيغة CSV
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 تحميل ملف الـ CSV كاملاً ({len(df):,} إيميل)",
                data=csv,
                file_name="massive_b2b_leads.csv",
                mime="text/csv",
            )
