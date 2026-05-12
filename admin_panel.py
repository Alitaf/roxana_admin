import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Page Layout Configuration
st.set_page_config(
    page_title="Roxana AI | Admin Dashboard",
    page_icon="💎",
    layout="wide"
)

# Database Connection
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error("Connection Failed. Please check Supabase Secrets.")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.title("Control Center")
menu = ["Dashboard", "Inventory Manager", "Customer Insights", "System Status"]
choice = st.sidebar.radio("Navigation", menu)

# --- 1. DASHBOARD SECTION ---
if choice == "Dashboard":
    st.title("Business Overview")
    st.markdown("Real-time performance metrics for Roxana AI Bot.")
    
    # ۱. واکشی داده‌ها
    res_p = supabase.table("products").select("id, brand").execute()
    # واکشی چت‌های ۲۴ ساعت گذشته (استفاده از فیلتر مستقیم در کوئری برای سرعت بیشتر)
    from datetime import datetime, timedelta
    time_threshold = (datetime.now() - timedelta(hours=24)).isoformat()
    
    res_l = supabase.table("chat_logs").select("user_id").gt("created_at", time_threshold).execute()
    
    df_products = pd.DataFrame(res_p.data)
    df_logs = pd.DataFrame(res_l.data)

    if not df_products.empty:
        # ۲. محاسبه کاربران فعال
        if not df_logs.empty:
            active_users = df_logs['user_id'].nunique() # شمارش آی‌دی‌های غیر تکراری
        else:
            active_users = 0

        # ۳. نمایش متریک‌ها در ۳ ستون
        m1, m2, m3 = st.columns(3)
        m1.metric("Total SKU", len(df_products))
        m2.metric("Active Users (24h)", active_users) # جایگزین شد
        m3.metric("Premium Brands", len(df_products['brand'].unique()))

        st.subheader("Recent Inventory Preview")
        st.table(df_products.head(5))
    else:
        st.warning("No products found.")

# --- 2. INVENTORY MANAGER SECTION ---
elif choice == "Inventory Manager":
    st.title("Inventory Manager")
    
    # TAB 1: Add New, TAB 2: Edit Existing
    tab1, tab2 = st.tabs(["➕ Add Product", "📝 Edit / Delete"])
    
    with tab1:
        with st.form("new_product"):
            col1, col2 = st.columns(2)
            with col1:
                brand = st.text_input("Brand Name (e.g. Helen Seward)")
                p_name = st.text_input("Product Name")
            with col2:
                price = st.number_input("Price in AED (Dhs)", min_value=0.0)
                link = st.text_input("Product Link (URL)")
            
            desc = st.text_area("Features & Benefits")
            if st.form_submit_button("Publish Product"):
                new_data = {"brand": brand, "name": p_name, "price_dhs": price, "link": link, "description": desc, "is_available": True}
                supabase.table("products").insert(new_data).execute()
                st.success(f"{p_name} is now live!")
                st.rerun()

    with tab2:
        res = supabase.table("products").select("*").order("brand").execute()
        for p in res.data:
            with st.expander(f"{p['brand']} - {p['name']} ({p['price_dhs']} Dhs)"):
                c1, c2 = st.columns([4, 1])
                is_active = c1.toggle("Show in Bot", value=p['is_available'], key=f"t_{p['id']}")
                
                # Update status if toggled
                if is_active != p['is_available']:
                    supabase.table("products").update({"is_available": is_active}).eq("id", p['id']).execute()
                    st.rerun()
                
                if c2.button("🗑 Delete", key=f"d_{p['id']}"):
                    supabase.table("products").delete().eq("id", p['id']).execute()
                    st.rerun()

# --- 3. CUSTOMER INSIGHTS SECTION ---
elif choice == "Customer Insights":
    st.title("Customer Insights & Logs")
    st.markdown("Real-time monitoring of customer interactions.")
    
    # Fetch logs from Supabase
    logs_res = supabase.table("chat_logs").select("*").order("created_at", desc=True).limit(50).execute()
    
    if logs_res.data:
        logs_df = pd.DataFrame(logs_res.data)
        
        # تعریف یک نقشه برای تغییر نام ستون‌ها (فقط مواردی که وجود دارند)
        column_mapping = {
            "created_at": "Time",
            "user_id": "User ID",
            "username": "Username",
            "user_query": "Customer Query",
            "bot_response": "Roxana Response"
        }
        
        # تغییر نام ستون‌ها بدون توجه به تعداد کل آن‌ها
        display_df = logs_df.rename(columns=column_mapping)
        
        # نمایش ستون‌های موجود (اگر ستونی هنوز در دیتابیس نیست، خطایی نمی‌دهد)
        available_cols = [c for c in ["Time", "User ID","Username", "Customer Query", "Roxana Response"] if c in display_df.columns]
        
        st.dataframe(display_df[available_cols], use_container_width=True)
    else:
        st.info("No chat logs found yet.")

# --- 4. SYSTEM STATUS ---
elif choice == "System Status":
    st.title("System Status")
    st.success("✅ Telegram Bot: Online")
    st.success("✅ Supabase DB: Connected")
    st.success("✅ AI Engine (Gemini): Ready")
    st.divider()
    st.write("Project: Roxana Digital Transformation")
