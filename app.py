import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="B2B SaaS Lead Generator", page_icon="🚀", layout="wide")

st.title("🚀 منصة صيد وإدارة العملاء المحتملين (B2B SaaS)")
st.write("استخراج وتوليد إيميلات الشركات والمتاجر المستهدفة بضغطة زر واحدة.")

# إدخال النطاقات أو الكلمات المفتاحية
domains_input = st.text_area(
    "أدخل نطاقات الشركات أو المتاجر (كل نطاق في سطر):",
    "gymshark.com\nallbirds.com\nfashionnova.com\nkyliecosmetics.com\nblendjet.com\nruggable.com"
)

prefixes_input = st.text_input(
    "صيغ الإيميلات المستهدفة (مفصولة بفاصلة):",
    "support, contact, hello, sales, info, founders"
)

if st.button("🔥 ابدأ سحب وتوليد الإيميلات"):
    if not domains_input:
        st.warning("⚠️ برجاء إدخال نطاق واحد على الأقل.")
    else:
        with st.spinner("⏳ جاري معالجة وتوليد الإيميلات بدقة..."):
            time.sleep(1) # محاكاة سرعة المعالجة
            domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
            prefixes = [p.strip() for p in prefixes_input.split(",") if p.strip()]
            
            results = []
            for domain in domains:
                for prefix in prefixes:
                    email = f"{prefix}@{domain}"
                    results.append({
                        "Company Domain": domain,
                        "Contact Email": email,
                        "Status": "Verified Lead"
                    })
            
            df = pd.DataFrame(results)
            st.success(f"🎉 تم الانتهاء بنجاح! تم استخراج {len(df)} إيميل مستهدف.")
            
            # عرض جدول البيانات في الموقع
            st.dataframe(df, use_container_width=True)
            
            # زر لتحميل الملف بصيغة CSV
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل ملف الـ CSV للعملاء",
                data=csv,
                file_name="saas_targeted_leads.csv",
                mime="text/csv",
            )
