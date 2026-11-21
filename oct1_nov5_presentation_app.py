import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & ATTRACTIVE EXECUTIVE SAAS STYLING
# ==============================================================================
st.set_page_config(
    page_title="ARTH LIFE Kids Fashion — Shopify Analysis",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp { background-color: #F4F6FB; }

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

.block-container {
    padding-top: 1.3rem !important;
    padding-bottom: 2.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E6EAF2;
}

/* Top Banner */
.exec-banner {
    background: linear-gradient(135deg, #0F172A 0%, #312E81 55%, #7C3AED 100%);
    border-radius: 22px;
    padding: 24px 30px;
    color: #FFFFFF;
    margin-bottom: 18px;
    box-shadow: 0 14px 30px rgba(30, 41, 59, 0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.exec-title { font-size: 25px; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
.exec-sub   { font-size: 13.5px; opacity: 0.86; margin-top: 5px; }
.exec-pill  {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.30);
    padding: 9px 18px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
}

/* Section Headers (RTO vs Exchange separate sections) */
.sec-header-rto {
    background: linear-gradient(90deg, #FFF1F2 0%, #FFFFFF 100%);
    border-left: 5px solid #EF4444;
    border-radius: 14px;
    padding: 14px 20px;
    margin-top: 10px;
    margin-bottom: 14px;
    border-top: 1px solid #FFE4E6;
    border-right: 1px solid #FFE4E6;
    border-bottom: 1px solid #FFE4E6;
}
.sec-header-exch {
    background: linear-gradient(90deg, #F5F3FF 0%, #FFFFFF 100%);
    border-left: 5px solid #8B5CF6;
    border-radius: 14px;
    padding: 14px 20px;
    margin-top: 18px;
    margin-bottom: 14px;
    border-top: 1px solid #EDE9FE;
    border-right: 1px solid #EDE9FE;
    border-bottom: 1px solid #EDE9FE;
}
.sec-title { font-size: 18px; font-weight: 800; color: #0F172A; margin: 0; }
.sec-sub   { font-size: 12.5px; color: #64748B; margin-top: 2px; }

/* KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 17px 19px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    border: 1px solid #E6EAF2;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08); }
.kpi-lbl  { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.4px; }
.kpi-val  { font-size: 22px; font-weight: 800; color: #0F172A; margin: 4px 0; letter-spacing: -0.5px; }
.kpi-tag  { display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; }
.kpi-ico  { width: 42px; height: 42px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 20px; }

/* Chart Cards */
.card-box {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    border: 1px solid #E6EAF2;
    margin-bottom: 18px;
}
.card-title { font-size: 15.5px; font-weight: 700; color: #0F172A; margin-bottom: 12px; }

/* Progress Rows */
.prod-row { margin-bottom: 13px; }
.prod-meta { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #1E293B; margin-bottom: 5px; }
.prod-track { width: 100%; height: 9px; background: #F1F5F9; border-radius: 999px; overflow: hidden; }
.prod-fill  { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOADING & PREPROCESSING
# ==============================================================================
DEFAULT_PATH = r"C:\Users\yasha\OneDrive\Desktop\New folder (4)\New folder (4)\New folder\PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx"
MODEL_FILENAME = "PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx"

def _find_repo_excel():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        script_dir,
        os.path.join(script_dir, "data"),
        os.path.join(script_dir, "Data"),
        os.getcwd(),
        os.path.join(os.getcwd(), "data"),
    ]
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            exact_fp = os.path.abspath(os.path.join(folder, MODEL_FILENAME))
            if os.path.isfile(exact_fp):
                return exact_fp
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            try:
                for fn in sorted(os.listdir(folder)):
                    if fn.lower().endswith(".xlsx") and "dimensional_model" in fn.lower():
                        return os.path.abspath(os.path.join(folder, fn))
            except Exception:
                continue
    if os.path.exists(DEFAULT_PATH):
        return DEFAULT_PATH
    return None

@st.cache_data(show_spinner=False)
def load_model(file_source):
    xls = pd.ExcelFile(file_source)
    orders = pd.read_excel(xls, sheet_name="Dim_Orders")
    disp = pd.read_excel(xls, sheet_name="Fact_Dispatches")
    rev = pd.read_excel(xls, sheet_name="Fact_Reverse_Logistics") if "Fact_Reverse_Logistics" in xls.sheet_names else pd.DataFrame()

    orders["Order_Date_dt"] = pd.to_datetime(orders["Order_Date"], dayfirst=True, errors="coerce")
    for c in ["Order_Total", "Order_Subtotal", "Discount", "Shipping", "Total_Line_Items"]:
        if c in orders.columns:
            orders[c] = pd.to_numeric(orders[c], errors="coerce").fillna(0.0)

    pm = orders["Payment_Method"].fillna("Unknown").astype(str)
    orders["Payment_Category"] = np.where(
        pm.str.lower().str.contains("cod|cash on delivery"), "COD",
        np.where(pm.str.lower().str.contains("razorpay|upi|card|wallet|prepaid"), "Prepaid (Razorpay)",
        np.where(pm.str.lower().str.contains("manual"), "Manual", "Other / Blank"))
    )

    disp["Dispatch_Date_dt"] = pd.to_datetime(disp["Dispatch_Date"], dayfirst=True, errors="coerce")
    disp["Amount"] = pd.to_numeric(disp.get("Amount", 0), errors="coerce").fillna(0.0)
    disp["Is_Delivered"] = disp.get("Is_Delivered", False).astype(bool)
    disp["Is_RTO"] = disp.get("Is_RTO", False).astype(bool)

    return orders, disp, rev

def _week_bucket(dt_val, start_d):
    if pd.isna(dt_val):
        return "Unknown"
    d = dt_val.date() if isinstance(dt_val, pd.Timestamp) else dt_val
    day_idx = max((d - start_d).days, 0)
    w_num = (day_idx // 7) + 1
    w_start = start_d + datetime.timedelta(days=(w_num - 1) * 7)
    w_end = min(w_start + datetime.timedelta(days=6), d + datetime.timedelta(days=6))
    return f"Week {w_num} ({w_start.strftime('%d %b')}–{w_end.strftime('%d %b')})"

# Sidebar
with st.sidebar:
    st.markdown("### 👗 ARTH LIFE Shopify")
    st.caption("Kids Fashion E-Commerce Analytics")
    st.divider()

    repo_excel = _find_repo_excel()
    if repo_excel:
        st.success(f"✅ Repo Excel loaded: `{os.path.basename(repo_excel)}`")

    with st.expander("📤 Override Excel manually (Optional)"):
        uploaded = st.file_uploader("Upload Model Excel (.xlsx)", type=["xlsx"])

    source = uploaded if uploaded is not None else repo_excel

    if source is None:
        st.warning("कृपया GitHub रिपॉझिटरीमध्ये `PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx` ठेवा किंवा वरून अपलोड करा.")
        st.stop()

    df_orders, df_disp, df_rev = load_model(source)

    valid_order_dates = df_orders["Order_Date_dt"].dropna()
    if valid_order_dates.empty:
        st.error("'Order_Date' मध्ये वैध तारखा सापडल्या नाहीत.")
        st.stop()

    min_d = valid_order_dates.min().date()
    max_d = valid_order_dates.max().date()

    st.markdown("#### 📅 Quick Date Preset")
    preset = st.selectbox(
        "Select Preset",
        ["Custom Dates", "01 Oct – 05 Nov 2026", "01 Sep – 14 Sep 2026", "All Available Dates"],
        index=0
    )

    if preset == "01 Oct – 05 Nov 2026":
        init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 11, 5), max_d), min_d)
    elif preset == "01 Sep – 14 Sep 2026":
        init_start = min(max(datetime.date(2026, 9, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 9, 14), max_d), min_d)
    elif preset == "All Available Dates":
        init_start, init_end = min_d, max_d
    else:
        init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 11, 5), max_d), min_d)

    all_regions = sorted(df_orders["Customer_Region"].dropna().unique().tolist())
    sel_regions = st.multiselect("🌍 Filter Region", all_regions, default=all_regions)

# ==============================================================================
# 3. TOP BANNER & UNIFIED DATE SELECTION BAR
# ==============================================================================
ds_col1, ds_col2, ds_col3 = st.columns([1, 1, 2.2])
with ds_col1:
    start_date = st.date_input("📅 Start Date", value=init_start, min_value=min_d, max_value=max_d, key="unified_start_date")
with ds_col2:
    end_date = st.date_input("📅 End Date", value=init_end, min_value=min_d, max_value=max_d, key="unified_end_date")
with ds_col3:
    st.markdown(
        f"<div style='padding-top:28px; font-size:13px; color:#475569;'>"
        f"<b>Orders Created Window:</b> {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')} "
        f"(Available: {min_d.strftime('%d %b %Y')} to {max_d.strftime('%d %b %Y')})</div>",
        unsafe_allow_html=True
    )

if start_date > end_date:
    st.error("❌ Start Date ही End Date पेक्षा लहान किंवा समान असावी.")
    st.stop()

st.markdown(f"""
<div class="exec-banner">
    <div>
        <div class="exec-title">👗 ARTH LIFE Kids Fashion — Shopify Analysis</div>
        <div class="exec-sub">Dedicated RTO & Exchange Sections, Order-to-Delivery Funnel, Revenue, Discount & Shipping</div>
    </div>
    <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. FILTER STRICTLY BY ORDER CREATED DATE (SINGLE PASS)
# ==============================================================================
p_orders = df_orders[
    (df_orders["Order_Date_dt"].dt.date >= start_date) &
    (df_orders["Order_Date_dt"].dt.date <= end_date) &
    (df_orders["Customer_Region"].isin(sel_regions))
].copy()

period_ids = set(p_orders["Base_Order_ID"].dropna())
p_disp = df_disp[df_disp["Base_Order_ID"].isin(period_ids)].copy()

if not p_disp.empty:
    merge_cols = ["Base_Order_ID", "Order_Date", "Order_Date_dt", "Payment_Category", "Order_Total", "Order_Notes", "Customer_Name"]
    for extra_c in ["Customer_Region", "Shipping_State", "State", "Shipping_City"]:
        if extra_c in p_orders.columns and extra_c not in p_disp.columns:
            merge_cols.append(extra_c)
    p_disp = p_disp.merge(p_orders[merge_cols].drop_duplicates(subset=["Base_Order_ID"]), on="Base_Order_ID", how="left")

    status_u = p_disp["Shipment_Status"].fillna("").astype(str).str.strip().str.upper()
    has_del = p_disp["Delivered_Date"].notna() & (p_disp["Delivered_Date"].astype(str).str.strip() != "")
    is_rto = p_disp["Is_RTO"].astype(bool)
    is_del = p_disp["Is_Delivered"].astype(bool)
    is_bad = status_u.isin(["CANCELLED", "CANCELED", "LOST"])

    p_disp["True_Delivered"] = (is_del | (status_u.isin(["SHIPPED", "PROCESSING", "OUT_FOR_DELIVERY"]) & has_del)) & (~is_rto) & (~is_bad)
    p_disp["True_Undelivered"] = (~p_disp["True_Delivered"]) & (~is_rto) & (~is_bad) & (status_u == "UNDELIVERED")
    p_disp["True_In_Transit"] = (~p_disp["True_Delivered"]) & (~is_rto) & (~is_bad) & (status_u != "UNDELIVERED")
    p_disp["True_Cancelled_Lost"] = is_bad

    received_hub_tokens = {
        "RTO DELIVERED", "RTO_DELIVERED", "DELIVERED TO HUB", "RECEIVED AT HUB",
        "RETURN DELIVERED", "RET DELIVERED", "RTO RECEIVED"
    }
    p_disp["RTO_Pending_Hub"] = is_rto & (~has_del) & (~status_u.isin(received_hub_tokens))
else:
    p_disp["True_Delivered"] = pd.Series(dtype=bool)
    p_disp["True_Undelivered"] = pd.Series(dtype=bool)
    p_disp["True_In_Transit"] = pd.Series(dtype=bool)
    p_disp["True_Cancelled_Lost"] = pd.Series(dtype=bool)
    p_disp["RTO_Pending_Hub"] = pd.Series(dtype=bool)

dispatched_ids = set(p_disp["Base_Order_ID"].dropna()) if not p_disp.empty else set()
not_dispatched = p_orders[~p_orders["Base_Order_ID"].isin(dispatched_ids)].copy()

del_oids = set(p_disp[p_disp["True_Delivered"]]["Base_Order_ID"].dropna()) if not p_disp.empty else set()
rto_oids = (set(p_disp[p_disp["Is_RTO"]]["Base_Order_ID"].dropna()) - del_oids) if not p_disp.empty else set()
rto_pending_hub_df = p_disp[p_disp["RTO_Pending_Hub"]].copy() if not p_disp.empty else pd.DataFrame()
rto_pending_hub_oids = set(rto_pending_hub_df["Base_Order_ID"].dropna()) if not rto_pending_hub_df.empty else set()
int_oids = (set(p_disp[p_disp["True_In_Transit"]]["Base_Order_ID"].dropna()) - del_oids - rto_oids) if not p_disp.empty else set()

p_rev = df_rev[df_rev["Base_Order_ID"].isin(period_ids)].copy() if (not df_rev.empty and "Base_Order_ID" in df_rev.columns) else pd.DataFrame()

# ==============================================================================
# 5. EXECUTIVE KPI CARDS
# ==============================================================================
if not p_orders.empty and "Base_Order_ID" in p_orders.columns:
    p_orders_uniq = p_orders.drop_duplicates(subset=["Base_Order_ID"]).copy()
    tot_ord = int(p_orders["Base_Order_ID"].nunique())
else:
    p_orders_uniq = p_orders.copy()
    tot_ord = len(p_orders)

gross_rev = float(p_orders_uniq["Order_Total"].sum()) if len(p_orders_uniq) > 0 else 0.0
tot_disc = float(p_orders_uniq["Discount"].sum()) if ("Discount" in p_orders_uniq.columns and len(p_orders_uniq) > 0) else 0.0
tot_ship = float(p_orders_uniq["Shipping"].sum()) if ("Shipping" in p_orders_uniq.columns and len(p_orders_uniq) > 0) else 0.0

rto_rev = float(p_orders_uniq[p_orders_uniq["Base_Order_ID"].isin(rto_oids)]["Order_Total"].sum()) if len(p_orders_uniq) > 0 else 0.0
net_rev = max(gross_rev - rto_rev - tot_ship, 0.0)
realized_deliv_rev = float(p_orders_uniq[p_orders_uniq["Base_Order_ID"].isin(del_oids)]["Order_Total"].sum()) if len(p_orders_uniq) > 0 else 0.0

aov = gross_rev / tot_ord if tot_ord > 0 else 0.0
disp_cnt = len(dispatched_ids)
deliv_cnt = len(del_oids)
deliv_pct = (deliv_cnt / disp_cnt * 100) if disp_cnt > 0 else 0.0
rto_cnt = len(rto_oids)
rto_pct = (rto_cnt / disp_cnt * 100) if disp_cnt > 0 else 0.0
rto_hub_parcels = int(p_disp["RTO_Pending_Hub"].sum()) if not p_disp.empty else 0
rto_hub_orders = len(rto_pending_hub_oids)
exch_cnt = int(p_rev["Base_Order_ID"].nunique()) if (not p_rev.empty and "Base_Order_ID" in p_rev.columns) else len(p_rev)
tot_ret_disp_cnt = rto_cnt + exch_cnt
tot_ret_disp_pct = (tot_ret_disp_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
exch_rev = float(p_orders_uniq[p_orders_uniq["Base_Order_ID"].isin(set(p_rev["Base_Order_ID"]))]["Order_Total"].sum()) if (not p_rev.empty and "Base_Order_ID" in p_rev.columns and len(p_orders_uniq) > 0) else 0.0
tot_ret_amt = rto_rev + exch_rev

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Orders</div>
            <div class="kpi-val">{tot_ord:,}</div>
            <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{int(p_orders_uniq['Total_Line_Items'].sum()) if len(p_orders_uniq)>0 else 0:,} Items</span>
        </div>
        <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Gross Revenue</div>
            <div class="kpi-val">₹{gross_rev:,.2f}</div>
            <span class="kpi-tag" style="background:#F5F3FF; color:#7C3AED;">AOV: ₹{aov:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#F5F3FF;">💰</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Net Revenue</div>
            <div class="kpi-val">₹{net_rev:,.2f}</div>
            <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Delivered: ₹{realized_deliv_rev:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#ECFDF5;">📈</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Total Discount</div>
            <div class="kpi-val">₹{tot_disc:,.2f}</div>
            <span class="kpi-tag" style="background:#FDF2F8; color:#BE185D;">{tot_disc/max(gross_rev+tot_disc,1)*100:.1f}% Disc. Share</span>
        </div>
        <div class="kpi-ico" style="background:#FDF2F8;">🏷️</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Total Shipping Cost</div>
            <div class="kpi-val">₹{tot_ship:,.2f}</div>
            <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">Avg: ₹{tot_ship/max(tot_ord,1):,.1f}/Order</span>
        </div>
        <div class="kpi-ico" style="background:#ECFEFF;">🚢</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Dispatched</div>
            <div class="kpi-val">{disp_cnt:,}</div>
            <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">{disp_cnt/max(tot_ord,1)*100:.1f}% of Orders</span>
        </div>
        <div class="kpi-ico" style="background:#ECFEFF;">📦</div>
    </div>""", unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Delivered</div>
            <div class="kpi-val">{deliv_cnt:,}</div>
            <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">▲ {deliv_pct:.1f}% Success</span>
        </div>
        <div class="kpi-ico" style="background:#ECFDF5;">🚚</div>
    </div>""", unsafe_allow_html=True)

with f3:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">RTO / Exchange Orders</div>
            <div class="kpi-val">{rto_cnt:,} / {exch_cnt:,}</div>
            <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO: {rto_pct:.1f}%</span>
        </div>
        <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
    </div>""", unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">RTO Pending Hub</div>
            <div class="kpi-val">{rto_hub_parcels:,}</div>
            <span class="kpi-tag" style="background:#FFF7ED; color:#C2410C;">{rto_hub_orders:,} Unique Orders</span>
        </div>
        <div class="kpi-ico" style="background:#FFF7ED;">🏭</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

if p_orders.empty:
    st.info(f"निवडलेल्या तारीख रेंजमध्ये ({start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}) कोणतेही ऑर्डर्स सापडले नाहीत.")
    st.stop()

# ==============================================================================
# 6. TABS — WITH SEPARATE RTO & EXCHANGE SECTIONS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview & Funnel",
    "↩️ RTO & Exchange Separate Sections",
    "👗 Products, Age Groups & Regions",
    "📋 Actionable Tables"
])

with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
        st.markdown('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Revenue Trend</div>', unsafe_allow_html=True)
        daily = p_orders_uniq.groupby("Order_Date_dt").agg(
            Orders=("Base_Order_ID", "nunique"),
            Revenue=("Order_Total", "sum")
        ).reset_index().sort_values("Order_Date_dt")
        daily["Date_Label"] = daily["Order_Date_dt"].dt.strftime("%d %b")
        daily["Rev_Lakhs"] = (daily["Revenue"] / 1e5).round(2)

        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        fig_dual.add_trace(
            go.Bar(
                x=daily["Date_Label"], y=daily["Orders"], name="Unique Orders",
                marker=dict(color="#6366F1", cornerradius=6), opacity=0.82,
                text=daily["Orders"], textposition="outside",
                textfont=dict(size=10, color="#312E81", family="Plus Jakarta Sans"),
                hovertemplate="<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>"
            ),
            secondary_y=False
        )
        fig_dual.add_trace(
            go.Scatter(
                x=daily["Date_Label"], y=daily["Rev_Lakhs"], name="Revenue (₹ Lakhs)",
                mode="lines+markers", line=dict(color="#EC4899", width=3, shape="spline"),
                marker=dict(size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")),
                hovertemplate="Revenue: ₹%{y:.2f}L<extra></extra>"
            ),
            secondary_y=True
        )
        max_ord_y = daily["Orders"].max() * 1.25 if not daily.empty else 100
        max_rev_y = daily["Rev_Lakhs"].max() * 1.25 if not daily.empty else 10
        fig_dual.update_layout(
            height=410, margin=dict(l=10, r=10, t=35, b=55),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified", bargap=0.28,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=12)),
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        fig_dual.update_xaxes(tickangle=-45, tickfont=dict(size=11, color="#475569"), nticks=18, showgrid=False)
        fig_dual.update_yaxes(title_text="Unique Orders", range=[0, max_ord_y], showgrid=True, gridcolor="#F1F5F9", zeroline=False, secondary_y=False)
        fig_dual.update_yaxes(title_text="Revenue (₹ Lakhs)", range=[0, max_rev_y], showgrid=False, zeroline=False, secondary_y=True)
        st.plotly_chart(fig_dual, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card-box"><div class="card-title">🎯 Order-to-Delivery Funnel (Unique Orders)</div>', unsafe_allow_html=True)
        funnel_labels = ["Orders Created", "Dispatched", "True Delivered", "Pure RTO", "RTO Pending Hub", "In-Transit", "Not Dispatched"]
        funnel_vals = [tot_ord, disp_cnt, deliv_cnt, rto_cnt, rto_hub_orders, len(int_oids), len(not_dispatched)]
        funnel_colors = ["#4F46E5", "#0EA5E9", "#10B981", "#EF4444", "#EA580C", "#F59E0B", "#94A3B8"]

        fig_fun = go.Figure(go.Bar(
            y=funnel_labels[::-1], x=funnel_vals[::-1], orientation="h",
            marker=dict(color=funnel_colors[::-1], cornerradius=8),
            text=[f"<b>{v:,}</b>" for v in funnel_vals[::-1]], textposition="outside",
            textfont=dict(size=12, color="#0F172A")
        ))
        fig_fun.update_layout(
            height=410, margin=dict(l=0, r=55, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, range=[0, max(funnel_vals + [1]) * 1.2]),
            yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        st.plotly_chart(fig_fun, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: SEPARATE RTO SECTION & SEPARATE EXCHANGE SECTION
# ------------------------------------------------------------------------------
with tab2:
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Returns Display", f"{tot_ret_disp_cnt:,} ({tot_ret_disp_pct:.2f}%)")
    s2.metric("Total Return Amount", f"₹{tot_ret_amt:,.2f}")
    s3.metric("Total RTO Orders", f"{rto_cnt:,}")
    s4.metric("Total Exchange Orders", f"{exch_cnt:,}")

    # ================= SECTION A: DEDICATED RTO SECTION =================
    st.markdown("""
    <div class="sec-header-rto">
        <div class="sec-title">🚚 Section 1: RTO (Return-to-Origin) Analysis</div>
        <div class="sec-sub">RTO Status Donut, State-wise / Region-wise RTO Returns & Weekly RTO Trend</div>
    </div>
    """, unsafe_allow_html=True)

    rto_df = p_disp[p_disp["Is_RTO"] & (~p_disp["Base_Order_ID"].isin(del_oids))].copy() if not p_disp.empty else pd.DataFrame()

    rto_c1, rto_c2, rto_c3 = st.columns(3)
    with rto_c1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 RTO Status Breakdown (Donut)</div>', unsafe_allow_html=True)
        if not rto_df.empty:
            st_col_rto = "Shipment_Status" if "Shipment_Status" in rto_df.columns else None
            if st_col_rto:
                rto_st_agg = rto_df.groupby(rto_df[st_col_rto].fillna("RTO").astype(str).str.strip())["Base_Order_ID"].nunique().reset_index(name="Count")
                rto_st_agg.columns = ["Status", "Count"]
            else:
                rto_st_agg = pd.DataFrame({"Status": ["RTO Pending Hub", "RTO Received Hub"], "Count": [rto_hub_orders, max(rto_cnt - rto_hub_orders, 0)]})
            rto_st_agg = rto_st_agg[rto_st_agg["Count"] > 0]
            fig_rto_donut = go.Figure(go.Pie(
                labels=rto_st_agg["Status"], values=rto_st_agg["Count"], hole=0.56,
                textinfo="label+value+percent", textposition="outside",
                marker=dict(colors=["#EF4444", "#F97316", "#F59E0B", "#DC2626", "#E11D48"], line=dict(color="#FFFFFF", width=2))
            ))
            fig_rto_donut.update_layout(
                height=340, margin=dict(l=15, r=15, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False, annotations=[dict(text=f"<b>{rto_cnt:,}</b><br>RTO", x=0.5, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig_rto_donut, use_container_width=True)
        else:
            st.info("निवडलेल्या कालावधीत RTO ऑर्डर्स नाहीत.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rto_c2:
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Region / State-wise RTO Returns</div>', unsafe_allow_html=True)
        if not rto_df.empty:
            geo_col = next((c for c in ["Shipping_State", "State", "Customer_Region", "Shipping_City"] if c in rto_df.columns), None)
            if geo_col:
                geo_rto = rto_df.groupby(rto_df[geo_col].fillna("Unknown").astype(str).str.strip())["Base_Order_ID"].nunique().reset_index(name="RTO_Orders").sort_values("RTO_Orders", ascending=True).tail(6)
                fig_geo_rto = go.Figure(go.Bar(
                    y=geo_rto[geo_col], x=geo_rto["RTO_Orders"], orientation="h",
                    marker=dict(color="#0284C7", cornerradius=8),
                    text=geo_rto["RTO_Orders"], textposition="outside"
                ))
                fig_geo_rto.update_layout(
                    height=340, margin=dict(l=0, r=35, t=15, b=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(geo_rto["RTO_Orders"].max()) * 1.25, 3.0)])
                )
                st.plotly_chart(fig_geo_rto, use_container_width=True)
        else:
            st.info("No RTO geography data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rto_c3:
        st.markdown('<div class="card-box"><div class="card-title">📆 Weekly RTO Return Analysis</div>', unsafe_allow_html=True)
        if not rto_df.empty and "Order_Date_dt" in rto_df.columns:
            rto_df["Week_Lbl"] = rto_df["Order_Date_dt"].apply(lambda d: _week_bucket(d, start_date))
            wk_rto = rto_df.groupby("Week_Lbl")["Base_Order_ID"].nunique().reset_index(name="RTO_Count")
            fig_wk_rto = go.Figure()
            fig_wk_rto.add_trace(go.Bar(
                x=wk_rto["Week_Lbl"], y=wk_rto["RTO_Count"], name="Weekly RTO",
                marker=dict(color="#FB923C", cornerradius=8),
                text=wk_rto["RTO_Count"], textposition="outside"
            ))
            fig_wk_rto.add_trace(go.Scatter(
                x=wk_rto["Week_Lbl"], y=wk_rto["RTO_Count"], name="Trend",
                mode="lines+markers", line=dict(color="#EA580C", width=2.5, shape="spline")
            ))
            fig_wk_rto.update_layout(
                height=340, margin=dict(l=10, r=10, t=20, b=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(wk_rto["RTO_Count"].max()) * 1.3, 3.0)])
            )
            st.plotly_chart(fig_wk_rto, use_container_width=True)
        else:
            st.info("No weekly RTO data.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ================= SECTION B: DEDICATED EXCHANGE SECTION =================
    st.markdown("""
    <div class="sec-header-exch">
        <div class="sec-title">🔄 Section 2: Exchange Analysis (<code>Fact_Reverse_Logistics</code>)</div>
        <div class="sec-sub">Exchanged Status Donut, Weekly Exchange Orders Analysis & Reverse Logistics Records</div>
    </div>
    """, unsafe_allow_html=True)

    ex_c1, ex_c2 = st.columns([1.05, 1.35])
    with ex_c1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 Exchanged Status (Donut Chart)</div>', unsafe_allow_html=True)
        if not p_rev.empty:
            p_rev_u = p_rev.drop_duplicates(subset=["Base_Order_ID"]) if "Base_Order_ID" in p_rev.columns else p_rev.copy()
            ex_st_col = next((c for c in ["Exchange_Status", "Return_Status", "Status", "Shipment_Status", "Reason"] if c in p_rev_u.columns), None)
            if ex_st_col:
                ex_agg = p_rev_u.groupby(p_rev_u[ex_st_col].fillna("Exchange").astype(str).str.strip()).size().reset_index(name="Count")
                ex_agg.columns = ["Status", "Count"]
            else:
                ex_agg = pd.DataFrame({"Status": ["Exchanged"], "Count": [len(p_rev_u)]})
            ex_agg = ex_agg[ex_agg["Count"] > 0]
            fig_ex_donut = go.Figure(go.Pie(
                labels=ex_agg["Status"], values=ex_agg["Count"], hole=0.56,
                textinfo="label+value+percent", textposition="outside",
                marker=dict(colors=["#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#0EA5E9", "#EC4899"], line=dict(color="#FFFFFF", width=2))
            ))
            fig_ex_donut.update_layout(
                height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False, annotations=[dict(text=f"<b>{int(ex_agg['Count'].sum()):,}</b><br>Exchange", x=0.5, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig_ex_donut, use_container_width=True)
        else:
            st.info("निवडलेल्या कालावधीत `Fact_Reverse_Logistics` मध्ये Exchange रेकॉर्ड्स नाहीत.")
        st.markdown('</div>', unsafe_allow_html=True)

    with ex_c2:
        st.markdown('<div class="card-box"><div class="card-title">📆 Weekly Exchange Orders Analysis</div>', unsafe_allow_html=True)
        if not p_rev.empty:
            rev_w = p_rev.merge(p_orders_uniq[["Base_Order_ID", "Order_Date_dt"]], on="Base_Order_ID", how="left")
            if "Order_Date_dt" in rev_w.columns and rev_w["Order_Date_dt"].notna().any():
                rev_w["Week_Lbl"] = rev_w["Order_Date_dt"].apply(lambda d: _week_bucket(d, start_date))
                wk_ex = rev_w.groupby("Week_Lbl")["Base_Order_ID"].nunique().reset_index(name="Exchange_Count")
            else:
                wk_ex = pd.DataFrame({"Week_Lbl": [f"Week 1 ({start_date.strftime('%d %b')})"], "Exchange_Count": [exch_cnt]})
            fig_wk_ex = go.Figure()
            fig_wk_ex.add_trace(go.Bar(
                x=wk_ex["Week_Lbl"], y=wk_ex["Exchange_Count"], name="Weekly Exchanges",
                marker=dict(color="#A855F7", cornerradius=8),
                text=wk_ex["Exchange_Count"], textposition="outside"
            ))
            fig_wk_ex.add_trace(go.Scatter(
                x=wk_ex["Week_Lbl"], y=wk_ex["Exchange_Count"], name="Trend",
                mode="lines+markers", line=dict(color="#7C3AED", width=2.5, shape="spline")
            ))
            fig_wk_ex.update_layout(
                height=350, margin=dict(l=10, r=10, t=20, b=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(wk_ex["Exchange_Count"].max()) * 1.3, 3.0)])
            )
            st.plotly_chart(fig_wk_ex, use_container_width=True)
        else:
            st.info("No weekly exchange data in selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"#### 🔄 Exchanges Detail (<code>Fact_Reverse_Logistics</code> — {exch_cnt:,} Unique Orders)")
    if not p_rev.empty:
        st.dataframe(p_rev, use_container_width=True, height=250, hide_index=True)
        st.download_button(
            "⬇️ Download Exchanges CSV",
            p_rev.to_csv(index=False).encode("utf-8"),
            f"exchanges_{start_date}_{end_date}.csv",
            "text/csv"
        )
    else:
        st.info("No Exchange records found for the selected created orders window.")

with tab3:
    p1, p2 = st.columns([1.2, 1])
    with p1:
        st.markdown('<div class="card-box"><div class="card-title">🏆 Top 7 Bestselling Delivered Products</div>', unsafe_allow_html=True)
        if not p_disp.empty and "Clean_Product_Name" in p_disp.columns:
            prod_s = p_disp[p_disp["True_Delivered"]]["Clean_Product_Name"].dropna().astype(str).str.strip()
            prod_s = prod_s[~prod_s.str.lower().isin(["", "nan", "none", "garment item", "manual dispatch item", "dresses", "standard"])]
            top_p = prod_s.value_counts().head(7)
            if not top_p.empty:
                mv = top_p.max()
                for rank, (name, cnt) in enumerate(top_p.items(), start=1):
                    pct = cnt / mv * 100
                    short = name if len(name) <= 44 else name[:44] + "..."
                    st.markdown(f"""<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{short}</span><span style="color:#DB2777;">{cnt:,} pcs</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with p2:
        st.markdown('<div class="card-box"><div class="card-title">👶 Top Kids Age Groups (Delivered)</div>', unsafe_allow_html=True)
        if not p_disp.empty and "Product_Age_Group" in p_disp.columns:
            age_s = p_disp[p_disp["True_Delivered"]]["Product_Age_Group"].dropna().astype(str).str.strip()
            age_s = age_s[~age_s.str.lower().isin(["", "nan", "none", "standard / free size"])]
            top_a = age_s.value_counts().head(7).reset_index()
            top_a.columns = ["Age Group", "Count"]
            if not top_a.empty:
                fig_age = go.Figure(go.Bar(x=top_a["Age Group"], y=top_a["Count"], marker=dict(color="#8B5CF6", cornerradius=8), text=top_a["Count"], textposition="outside"))
                fig_age.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True, gridcolor="#F1F5F9"))
                st.plotly_chart(fig_age, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    g1, g2 = st.columns([1, 1.3])
    with g1:
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Unique Orders by Region</div>', unsafe_allow_html=True)
        reg_agg = p_orders.groupby("Customer_Region")["Base_Order_ID"].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False)
        fig_reg = go.Figure(go.Pie(labels=reg_agg["Customer_Region"], values=reg_agg["Orders"], hole=0.52, marker=dict(colors=["#4F46E5", "#EC4899", "#10B981", "#F59E0B", "#0EA5E9", "#8B5CF6"])))
        fig_reg.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_reg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="card-box"><div class="card-title">🏙️ Top 8 Cities by Unique Orders</div>', unsafe_allow_html=True)
        city_agg = p_orders.groupby("Shipping_City")["Base_Order_ID"].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False).head(8)
        fig_city = go.Figure(go.Bar(y=city_agg["Shipping_City"][::-1], x=city_agg["Orders"][::-1], orientation="h", marker=dict(color="#0EA5E9", cornerradius=8), text=city_agg["Orders"][::-1], textposition="outside"))
        fig_city.update_layout(height=300, margin=dict(l=0, r=35, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=True, gridcolor="#F1F5F9"))
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown(f"#### 🏭 RTO Pending to Hub ({rto_hub_parcels} Parcels / {rto_hub_orders} Unique Orders)")
    hub_cols = [c for c in ["Order_ID", "Order_Date", "Dispatch_Date", "Carrier", "Tracking_Number", "Shipment_Status", "Order_Total", "Order_Notes"] if c in rto_pending_hub_df.columns]
    hub_view = rto_pending_hub_df[hub_cols] if not rto_pending_hub_df.empty else pd.DataFrame(columns=hub_cols)
    st.dataframe(hub_view, use_container_width=True, height=280, hide_index=True)
    st.download_button("⬇️ Download RTO Pending Hub CSV", hub_view.to_csv(index=False).encode("utf-8"), "rto_pending_hub.csv", "text/csv")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(f"#### 🚚 Truly In-Transit Parcels ({int(p_disp['True_In_Transit'].sum()) if not p_disp.empty else 0})")
        it_cols = [c for c in ["Order_ID", "Order_Date", "Dispatch_Date", "Carrier", "Shipment_Status", "Order_Total", "Order_Notes"] if c in p_disp.columns]
        it_view = p_disp[p_disp["True_In_Transit"]][it_cols] if not p_disp.empty else pd.DataFrame(columns=it_cols)
        st.dataframe(it_view, use_container_width=True, height=340, hide_index=True)
        st.download_button("⬇️ Download In-Transit CSV", it_view.to_csv(index=False).encode("utf-8"), "in_transit.csv", "text/csv")

    with t_col2:
        st.markdown(f"#### ⏳ Not Dispatched Orders ({len(not_dispatched)})")
        nd_cols = [c for c in ["Base_Order_ID", "Order_Date", "Financial_Status", "Fulfillment_Status", "Order_Total", "Order_Notes"] if c in not_dispatched.columns]
        nd_view = not_dispatched[nd_cols]
        st.dataframe(nd_view, use_container_width=True, height=340, hide_index=True)
        st.download_button("⬇️ Download Not-Dispatched CSV", nd_view.to_csv(index=False).encode("utf-8"), "not_dispatched.csv", "text/csv")
