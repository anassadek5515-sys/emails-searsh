import streamlit as st
import sqlite3
import os
import base64
import requests
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="B2B Empire Command Center", page_icon="🚀", layout="wide")

st.title("🚀 لوحة قيادة الإمبراطورية والتحليلات الحية (B2B Command Center)")
st.write("متابعة حية لحالة الإيميلات، الردود، والتحكم الكامل في صفقاتك!")

DB_FILE = "companies.db"

# سحب بيانات الأمان من الـ Secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception:
    GITHUB_TOKEN = ""
    REPO_OWNER = ""
    REPO_NAME = ""

# دالة ذكية لرفع قاعدة البيانات المحدثة أوتوماتيك لجيت هب
def sync_db_to_github():
    if GITHUB_TOKEN and REPO_OWNER and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DB_FILE}"
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
            
            with open(DB_FILE, "rb") as f:
                content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode("utf-8")

            get_res = requests.get(url, headers=headers)
            sha = get_res.json().get("sha") if get_res.status_code == 200 else None

            data = {
                "message": "Update database from Streamlit dashboard",
                "content": encoded_content,
                "branch": "main"
            }
            if sha:
                data["sha"] = sha

            put_res = requests.put(url, headers=headers, json=data)
            return put_res.status_code in [200, 201]
        except Exception:
            return False
    return False

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
    else:
        st.sidebar.error("❌ بيانات جيت هب (Secrets) غير مُعَدة في Streamlit!")

# التحقق من وجود قاعدة البيانات والجدول وقراءتها بأمان تام
df = pd.DataFrame(columns=["id", "name", "email", "status", "reply_text"])

if os.path.exists(DB_FILE):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies';")
        table_exists = cursor.fetchone()

        if table_exists:
            df = pd.read_sql("SELECT * FROM companies", conn)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'Ready',
                    reply_text TEXT
                )
            """)
            conn.commit()
            df = pd.read_sql("SELECT * FROM companies", conn)
        conn.close()
    except Exception as e:
        st.error(f"⚠️ خطأ أثناء قراءة قاعدة البيانات: {e}")

# --- لوحة المؤشرات العليا (Metrics) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_count = len(df)
ready_count = len(df[df['status'] == 'Ready']) if not df.empty and 'status' in df.columns else 0
sent_count = len(df[df['status'] == 'Sent']) if not df.empty and 'status' in df.columns else 0
replied_count = len(df[df['status'] == 'Replied']) if not df.empty and 'status' in df.columns else 0

col1.metric("📊 إجمالي الـ Leads", f"{total_count:,}")
col2.metric("⏳ الجاهز للإرسال (Ready)", f"{ready_count:,}")
col3.metric("🚀 الإيميلات المرسلة (Sent)", f"{sent_count:,}")
col4.metric("💬 الردود والصفقات (Replied)", f"{replied_count:,}")

# --- جدول إدارة وتحديث الردود يدوياً بكل سهولة ---
st.markdown("---")
st.subheader("📋 جدول الشركات وإدارة الردود يدوياً")
if not df.empty:
    st.write("يمكنك تتبع الشركات وتحديث حالتها أو تسجيل الرد فور تلقيه في بريدك:")
    
    # عرض الجدول للتصفح
    st.dataframe(df, use_container_width=True)

    # نموذج سريع لتحديث حالة شركة معينة إلى Replied
    st.markdown("#### ✍️ تحديث حالة شركة وردت عليك:")
    with st.form("update_lead_form"):
        lead_id_to_update = st.number_input("أدخل معرف الشركة (ID المراد تحديثه):", min_value=1, step=1)
        new_reply_text = st.text_area("أدخل نص رد العميل:")
        submit_update = st.form_submit_button("💾 تحديث الحالة إلى Replied وحفظ الرد")

        if submit_update:
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE companies 
                    SET status = 'Replied', reply_text = ? 
                    WHERE id = ?
                """, (new_reply_text, lead_id_to_update))
                conn.commit()
                conn.close()
                
                # مزامنة تلقائية لجيت هب
                if sync_db_to_github():
                    st.success(f"✅ تم تحديث الشركة رقم {lead_id_to_update} بنجاح ومزامنتها مع السيرفر!")
                    st.rerun()
                else:
                    st.warning("⚠️ تم التحديث محلياً، ولكن فشلت المزامنة التلقائية مع جيت هب.")
            except Exception as ex:
                st.error(f"❌ خطأ أثناء التحديث: {ex}")
else:
    st.info("ℹ️ لا توجد بيانات في قاعدة البيانات حالياً. استخدم المولد أدناه لإنشاء دفعة جديدة.")

# --- صندوق الردود والشركات التي تفاعلت ---
st.markdown("---")
st.subheader("💬 صندوق الردود الواردة وصياغة صفقات البيع")

if not df.empty and 'status' in df.columns:
    replied_df = df[df['status'] == 'Replied']
    if not replied_df.empty:
        st.success(f"🎉 تم العثور على {len(replied_df)} شركة قامت بالرد!")
        for index, row in replied_df.iterrows():
            with st.expander(f"🏢 شركة: {row['name']} ({row['email']})"):
                st.write(f"**نص الرد الوارد:**")
                st.info(row['reply_text'] if row['reply_text'] else "لا يوجد نص مسجل للرد.")
    else:
        st.info("📭 لم ترد أي شركة مسجلة حتى الآن.")

# مساعد صياغة الردود الذكي
st.markdown("<br>", unsafe_allow_html=True)
company_reply_input = st.text_area("أدخل رد الشركة أو استفسارها هنا لنصيغ لك الرد الاحترافي المناسب:")
if st.button("✨ صياغة الرد الذكي لقفل الصفقة"):
    if company_reply_input.strip():
        st.info("🤖 جارٍ تحليل رد العميل وصياغة أفضل استراتيجية لبيع اشتراك الـ 200$...")
        st.success("""
        💡 **الرد المقترح لإغلاق الصفقة:**
        
        "أهلاً بحضرتك،  
        شكراً لاهتمامك بـ منصتنا. بناءً على استفسارك، نظامنا مصمم خصيصاً لتتبع المنتجات الأكثر مبيعاً وتحليل المنافسين لحظياً، مما يوفر عليكم آلاف الدولارات في تجارب الإعلانات.  
        اشتراكنا بـ 200 دولار شهرياً، ويسعدنا جداً ترتيب مكالمة سريعة لمدة 3 دقائق اليوم لنعرض لك كيف يمكننا مضاعفة مبيعات متجركم فوراً.  
        هل يناسبكم موعد غداً الساعة 2 ظهراً؟"
        """)
    else:
        st.warning("⚠️ يرجى إدخال رد الشركة أولاً.")

# --- قسم التوليد والتحكم الإضافي ---
st.markdown("---")
st.subheader("⚡ مولد الدفعات الجديدة والتحكم")
industry = st.text_input("بادئة الشركات (مثال: global, tech):", "tech")
total_leads = st.number_input("عدد الإيميلات المطلوبة للدفعة:", min_value=1, max_value=2000000, value=10, step=5)

if st.button("🚀 توليد ورفع دفعة جديدة وجدولة السيرفر"):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                status TEXT DEFAULT 'Ready',
                reply_text TEXT
            )
        """)
        
        for i in range(1, total_leads + 1):
            comp_name = f"{industry.capitalize()} Store {i}"
            comp_email = f"contact{i}@{industry.lower()}123.com"
            cursor.execute("""
                INSERT INTO companies (name, email, status) 
                VALUES (?, ?, 'Ready')
            """, (comp_name, comp_email))
            
        conn.commit()
        conn.close()
        
        st.success(f"✅ تم توليد {total_leads} شركة بنجاح في قاعدة البيانات المحلية!")

        if sync_db_to_github():
            st.success("☁️ تم رفع وتحديث قاعدة البيانات على جيت هب بنجاح تام!")
            st.rerun()
        else:
            st.warning("⚠️ تم الحفظ محلياً، ولكن فشل الرفع لجيت هب.")

    except Exception as ex:
        st.error(ferror := f"❌ حدث خطأ أثناء التوليد أو الرفع: {ex}")
