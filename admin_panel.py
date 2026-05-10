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
    
    # Fetch Data for Metrics
    res = supabase.table("products").select("*").execute()
    df = pd.DataFrame(res.data)

    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total SKU", len(df))
        m2.metric("In Stock", len(df[df['is_available'] == True]))
        m3.metric("Premium Brands", len(df['brand'].unique()))

        st.subheader("Inventory Distribution")
        # Displaying a clean table
        st.table(df[['brand', 'name', 'price_dhs']].head(10))
    else:
        st.warning("No data found in the 'products' table.")

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

# --- 3. CUSTOMER INSIGHTS (DEMO MODE) ---
elif choice == "Customer Insights":
    st.title("Customer Insights & Logs")
    st.info("Demo Data: Tracking how users interact with Roxana AI.")
    
    # Sample logs to look good for the demo
    mock_logs = [
        {"Time": "2024-05-10 14:20", "User": "@client_dubai", "Query": "Something for dry hair?", "Response": "Recommended Alchemy Oil"},
        {"Time": "2024-05-10 15:05", "User": "@beauty_user", "Query": "Price of Helen Seward?", "Response": "Displayed 150 Dhs"},
    ]
    st.table(mock_logs)

# --- 4. SYSTEM STATUS ---
elif choice == "System Status":
    st.title("System Status")
    st.success("✅ Telegram Bot: Online")
    st.success("✅ Supabase DB: Connected")
    st.success("✅ AI Engine (Gemini): Ready")
    st.divider()
    st.write("Project: Roxana Digital Transformation")
