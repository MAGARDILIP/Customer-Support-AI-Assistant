"""
Order Lookup Page — Direct order search and refund eligibility checking.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.utils.api_client import lookup_order, search_orders_by_email, check_refund

st.set_page_config(page_title="Order Lookup - ShopEase", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .order-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .order-header h2 { color: white !important; margin: 0; }
    .order-header p { color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem; }

    .order-card {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .status-delivered { color: #38a169; font-weight: 600; }
    .status-shipped { color: #d69e2e; font-weight: 600; }
    .status-pending { color: #718096; font-weight: 600; }
    .status-cancelled { color: #e53e3e; font-weight: 600; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="order-header">
    <h2>🔍 Order Lookup</h2>
    <p>Search orders by order number, email, or check refund eligibility</p>
</div>
""", unsafe_allow_html=True)

# --- Search Tabs ---
tab1, tab2, tab3 = st.tabs(["📦 By Order Number", "📧 By Email", "💰 Refund Check"])

# --- Tab 1: Order Number ---
with tab1:
    st.markdown("### Search by Order Number")
    col1, col2 = st.columns([3, 1])
    with col1:
        order_num = st.text_input(
            "Enter Order Number",
            placeholder="e.g., ORD-1023",
            key="order_num_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 Search", key="search_order", type="primary", use_container_width=True)

    if search_btn and order_num:
        with st.spinner("Looking up order..."):
            result = lookup_order(order_num)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        elif "order" in result:
            order = result["order"]
            st.success(f"✅ Order found: **{order['order_number']}**")

            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                status = order.get("status", "Unknown")
                status_emoji = {"Delivered": "✅", "Shipped": "📦", "Pending": "⏳", "Processing": "⚙️", "Cancelled": "❌"}
                st.metric("Status", f"{status_emoji.get(status, '❓')} {status}")
            with col_b:
                st.metric("Total", f"${order.get('total_price', 0):.2f}")
            with col_c:
                st.metric("Product", order.get("product_name", "N/A"))
            with col_d:
                st.metric("Quantity", order.get("quantity", 0))

            with st.expander("📋 Full Order Details"):
                st.json(order)

# --- Tab 2: Email Search ---
with tab2:
    st.markdown("### Search by Customer Email")
    col1, col2 = st.columns([3, 1])
    with col1:
        email = st.text_input(
            "Enter Customer Email",
            placeholder="e.g., john@example.com",
            key="email_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        email_btn = st.button("🔍 Search", key="search_email", type="primary", use_container_width=True)

    if email_btn and email:
        with st.spinner("Searching orders..."):
            result = search_orders_by_email(email)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        elif "orders" in result:
            customer = result.get("customer", {})
            orders = result["orders"]

            st.success(f"✅ Found {len(orders)} orders for **{customer.get('name', email)}**")

            for order in orders:
                with st.expander(f"📦 {order['order_number']} — {order.get('status', 'N/A')} — ${order.get('total_price', 0):.2f}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Product:** {order.get('product_name', 'N/A')}")
                        st.markdown(f"**Quantity:** {order.get('quantity', 0)}")
                        st.markdown(f"**Order Date:** {order.get('order_date', 'N/A')}")
                    with col_b:
                        st.markdown(f"**Status:** {order.get('status', 'N/A')}")
                        st.markdown(f"**Tracking:** {order.get('tracking_number', 'N/A')}")
                        st.markdown(f"**Delivery:** {order.get('delivery_date', 'N/A')}")

# --- Tab 3: Refund Check ---
with tab3:
    st.markdown("### Check Refund Eligibility")
    col1, col2 = st.columns([3, 1])
    with col1:
        refund_order = st.text_input(
            "Enter Order Number to Check",
            placeholder="e.g., ORD-1023",
            key="refund_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        refund_btn = st.button("💰 Check", key="check_refund", type="primary", use_container_width=True)

    if refund_btn and refund_order:
        with st.spinner("Checking eligibility..."):
            result = check_refund(refund_order)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            eligible = result.get("eligible", False)
            order = result.get("order", {})

            if eligible:
                st.success(f"✅ **ELIGIBLE FOR REFUND**")
                st.metric("Refund Amount", f"${result.get('refund_amount', 0):.2f}")
                st.info("To proceed, the customer should ship the item back in original packaging.")
            else:
                st.error(f"❌ **NOT ELIGIBLE FOR REFUND**")
                reasons = result.get("reasons", [])
                for reason in reasons:
                    st.warning(f"⚠️ {reason}")

                existing = result.get("existing_refund")
                if existing:
                    st.info(f"📌 Existing refund: {existing.get('status', 'N/A')} — ${existing.get('refund_amount', 0):.2f}")

            with st.expander("📋 Order Details"):
                st.json(order)

# --- Quick Help ---
st.markdown("---")
st.markdown("### 💡 Available Order Numbers for Testing")
st.info("Try order numbers from **ORD-1000** to **ORD-1079** (80 sample orders in the database)")
