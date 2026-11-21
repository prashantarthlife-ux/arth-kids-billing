import os
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & EXECUTIVE SAAS STYLING (SIDEBAR VISIBLE)
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
.stApp { background-color: #F5F7FB; }

/* Keep Header & Sidebar '>' button visible; hide only menu/footer/toolbar */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

.block-container {
    padding-top: 1.4rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E8ECF4;
}

/* Executive Banner */
.exec-banner {
    background: linear-gradient(135deg, #1E293B 0%, #312E81 60%, #6D28D9 100%);
    border-radius: 20px;
    padding: 24px 28px;
    color: #FFFFFF;
    margin-bottom: 20px;
    box-shadow: 0 12px 28px rgba(30, 41, 59, 0.16);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.exec-title { font-size: 24px; font-weight: 800; letter-spacing: -0.4px; margin: 0; }
.exec-sub   { font-size: 13.5px; opacity: 0.85; margin-top: 4px; }
.exec-pill  {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.28);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
}

/* KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    border: 1px solid #E8ECF4;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08); }
.kpi-lbl  { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.4px; }
.kpi-val  { font-size: 22px; font-weight: 800; color: #0F172A; margin: 4px 0; letter-spacing: -0.5px; }
.kpi-tag  { display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; }
.kpi-ico  { width: 42px; height: 42px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 20px; }

/* White Chart Containers */
.card-box {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    border: 1px solid #E8ECF4;
    margin-bottom: 18px;
}
.card-title { font-size: 15.5px; font-weight: 700; color: #0F172A; margin-bottom: 12px; }

/* Progress Rows for Top Products */
.prod-row { margin-bottom: 13px; }
.prod-meta { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #1E293B; margin-bottom: 5px; }
.prod-track { width: 100%; height: 9px; background: #F1F5F9; border-radius: 999px; overflow: hidden; }
.prod-fill  { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%); }

/* Insight Callout */
.insight-box {
    background: #FFFBEB;
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    color: #78350F;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOADING & PREPROCESSING (AUTO-LOADS EXCEL FROM GITHUB REPO)
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
# 3. TOP BANNER & UNIFIED DATE SELECTION BAR (SINGLE SOURCE OF TRUTH)
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
        <div class="exec-sub">Order-to-Delivery, Gross & Net Revenue, Discount, Shipping, RTO & Exchange Review</div>
    </div>
    <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. FILTER & COMPUTE ACCURATE METRICS (SINGLE PASS BY ORDER CREATED DATE)
# ==============================================================================
p_orders = df_orders[
    (df_orders["Order_Date_dt"].dt.date >= start_date) &
    (df_orders["Order_Date_dt"].dt.date <= end_date) &
    (df_orders["Customer_Region"].isin(sel_regions))
].copy()

period_ids = set(p_orders["Base_Order_ID"].dropna())

p_disp = df_disp[df_disp["Base_Order_ID"].isin(period_ids)].copy()

if not p_disp.empty:
    p_disp = p_disp.merge(
        p_orders[["Base_Order_ID", "Order_Date", "Order_Date_dt", "Payment_Category", "Order_Total", "Order_Notes", "Customer_Name"]],
        on="Base_Order_ID", how="left"
    )
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

p_rev = df_rev[df_rev["Base_Order_ID"].isin(period_ids)].copy() if not df_rev.empty else pd.DataFrame()

# ==============================================================================
# 5. EXECUTIVE KPI CARDS (UNIQUE COUNTS & FINANCIAL METRICS)
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

if not p_rev.empty and "Base_Order_ID" in p_rev.columns:
    exch_cnt = int(p_rev["Base_Order_ID"].nunique())
else:
    exch_cnt = len(p_rev)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Orders</div>
            <div class="kpi-val">{tot_ord:,}</div>
            <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{int(p_orders['Total_Line_Items'].sum()) if tot_ord>0 else 0:,} Items</span>
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
            <div class="kpi-lbl">Unique RTO / Exch</div>
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
# 6. EXECUTIVE PRESENTATION TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview & Funnel",
    "↩️ RTO & Exchange Status Analysis",
    "👗 Products, Age Groups & Regions",
    "📋 Actionable Tables (RTO Hub Pending, In-Transit & Unshipped)"
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

with tab2:
    st.markdown(f"""
    <div class="insight-box">
        💡 <b>Selected Created Orders Window ({start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}):</b>
        Unique RTO Orders = <b>{rto_cnt:,}</b> (Pending to Hub = <b>{rto_hub_orders:,}</b> unique orders / <b>{rto_hub_parcels:,}</b> parcels) ·
        Unique Exchanges (<code>Fact_Reverse_Logistics</code>) = <b>{exch_cnt:,}</b> · RTO Value = <b>₹{rto_rev:,.2f}</b>.
    </div>
    """, unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 RTO & Exchange Status Breakdown (Donut Chart)</div>', unsafe_allow_html=True)
        rto_sub = p_disp[p_disp["Is_RTO"] & (~p_disp["Base_Order_ID"].isin(del_oids))].copy() if not p_disp.empty else pd.DataFrame()
        rto_received_cnt = int(rto_sub[~rto_sub["RTO_Pending_Hub"]]["Base_Order_ID"].nunique()) if not rto_sub.empty else 0
        rto_pending_cnt = int(rto_sub[rto_sub["RTO_Pending_Hub"]]["Base_Order_ID"].nunique()) if not rto_sub.empty else 0

        donut_items = []
        if rto_pending_cnt > 0:
            donut_items.append(("RTO — Pending to Hub (Unique)", rto_pending_cnt))
        if rto_received_cnt > 0:
            donut_items.append(("RTO — Received at Hub (Unique)", rto_received_cnt))

        if not p_rev.empty:
            p_rev_u = p_rev.drop_duplicates(subset=["Base_Order_ID"]) if "Base_Order_ID" in p_rev.columns else p_rev
            status_col = next((c for c in ["Return_Status", "Exchange_Status", "Status", "Shipment_Status", "Reason"] if c in p_rev_u.columns), None)
            if status_col:
                rev_vc = p_rev_u[status_col].fillna("Exchange (Recorded)").astype(str).str.strip()
                rev_vc = rev_vc.replace("", "Exchange (Recorded)").value_counts()
                for st_name, cnt in rev_vc.items():
                    donut_items.append((f"Exchange — {st_name}", int(cnt)))
            else:
                donut_items.append(("Exchange / Reverse Logistics (Unique)", len(p_rev_u)))

        if donut_items:
            dn_df = pd.DataFrame(donut_items, columns=["Status", "Count"])
            donut_colors = ["#EA580C", "#EF4444", "#8B5CF6", "#0EA5E9", "#10B981", "#F59E0B", "#EC4899"]
            fig_donut = go.Figure(go.Pie(
                labels=dn_df["Status"],
                values=dn_df["Count"],
                hole=0.55,
                textinfo="label+value+percent",
                textposition="outside",
                marker=dict(colors=donut_colors[:len(dn_df)], line=dict(color="#FFFFFF", width=2)),
                hovertemplate="<b>%{label}</b><br>Unique Count: %{value:,}<br>Share: %{percent}<extra></extra>"
            ))
            fig_donut.update_layout(
                height=380,
                margin=dict(l=20, r=20, t=25, b=25),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{dn_df['Count'].sum():,}</b><br>Unique", x=0.5, y=0.5, font_size=15, showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("निवडलेल्या तारीख रेंजमध्ये कोणतेही RTO किंवा Exchange रेकॉर्ड्स नाहीत.")
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="card-box"><div class="card-title">↩️ Monthly Unique RTO & Exchange Count</div>', unsafe_allow_html=True)
        if not rto_sub.empty and "Order_Date_dt" in rto_sub.columns:
            rto_sub["Month_Lbl"] = rto_sub["Order_Date_dt"].dt.to_period("M").astype(str)
            m_rto = rto_sub.groupby("Month_Lbl")["Base_Order_ID"].nunique().reset_index(name="RTO_Orders")
        else:
            m_rto = pd.DataFrame({"Month_Lbl": [start_date.strftime("%Y-%m")], "RTO_Orders": [0]})

        if not p_rev.empty:
            rev_merged = p_rev.merge(p_orders_uniq[["Base_Order_ID", "Order_Date_dt"]], on="Base_Order_ID", how="left")
            if "Order_Date_dt" in rev_merged.columns and rev_merged["Order_Date_dt"].notna().any():
                rev_merged["Month_Lbl"] = rev_merged["Order_Date_dt"].dt.to_period("M").astype(str)
                m_exch = rev_merged.groupby("Month_Lbl")["Base_Order_ID"].nunique().reset_index(name="Exchange_Count")
            else:
                m_exch = pd.DataFrame({"Month_Lbl": [start_date.strftime("%Y-%m")], "Exchange_Count": [exch_cnt]})
        else:
            m_exch = pd.DataFrame({"Month_Lbl": m_rto["Month_Lbl"].tolist(), "Exchange_Count": [0] * len(m_rto)})

        me_df = pd.merge(m_rto, m_exch, on="Month_Lbl", how="outer").fillna(0).sort_values("Month_Lbl")
        me_df["RTO_Orders"] = me_df["RTO_Orders"].astype(int)
        me_df["Exchange_Count"] = me_df["Exchange_Count"].astype(int)

        fig_me = go.Figure()
        fig_me.add_trace(go.Bar(x=me_df["Month_Lbl"], y=me_df["RTO_Orders"], name="Unique RTO Orders", marker=dict(color="#EF4444", cornerradius=8), text=me_df["RTO_Orders"], textposition="outside"))
        fig_me.add_trace(go.Bar(x=me_df["Month_Lbl"], y=me_df["Exchange_Count"], name="Unique Exchanges", marker=dict(color="#8B5CF6", cornerradius=8), text=me_df["Exchange_Count"], textposition="outside"))
        max_me_y = max(me_df["RTO_Orders"].max(), me_df["Exchange_Count"].max(), 1) * 1.25
        fig_me.update_layout(barmode="group", height=380, margin=dict(l=10, r=10, t=30, b=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, max_me_y], showgrid=True, gridcolor="#F1F5F9", title="Unique Count"), legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1))
        st.plotly_chart(fig_me, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown('<div class="card-box"><div class="card-title">💳 COD vs Prepaid — Unique Orders</div>', unsafe_allow_html=True)
        if not p_disp.empty:
            pay_agg = p_disp.groupby("Payment_Category").agg(Parcels=("Base_Order_ID", "nunique"), Delivered=("True_Delivered", "sum"), RTO=("Is_RTO", "sum")).reset_index()
            pay_agg["Del_Pct"] = (pay_agg["Delivered"] / pay_agg["Parcels"].replace(0, 1) * 100).round(1)
            pay_agg["RTO_Pct"] = (pay_agg["RTO"] / pay_agg["Parcels"].replace(0, 1) * 100).round(1)
            del_labels = [f"<b>{int(d):,}</b><br>({p:.1f}%)" for d, p in zip(pay_agg["Delivered"], pay_agg["Del_Pct"])]
            rto_labels = [f"<b>{int(r):,}</b><br>({p:.1f}%)" for r, p in zip(pay_agg["RTO"], pay_agg["RTO_Pct"])]
            fig_pay = go.Figure()
            fig_pay.add_trace(go.Bar(x=pay_agg["Payment_Category"], y=pay_agg["Delivered"], name="Delivered", marker=dict(color="#10B981", cornerradius=8), text=del_labels, textposition="outside"))
            fig_pay.add_trace(go.Bar(x=pay_agg["Payment_Category"], y=pay_agg["RTO"], name="RTO", marker=dict(color="#EF4444", cornerradius=8), text=rto_labels, textposition="outside"))
            max_pay_y = max(pay_agg["Delivered"].max(), pay_agg["RTO"].max(), 1) * 1.25
            fig_pay.update_layout(barmode="group", height=340, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max_pay_y]))
            st.plotly_chart(fig_pay, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="card-box"><div class="card-title">🚚 Carrier Performance (Delhivery vs DTDC)</div>', unsafe_allow_html=True)
        if not p_disp.empty and "Dispatch_Category" in p_disp.columns:
            carr_agg = p_disp.groupby("Dispatch_Category").agg(Parcels=("Base_Order_ID", "nunique"), Delivered=("True_Delivered", "sum"), RTO=("Is_RTO", "sum")).reset_index()
            carr_agg["Delivery %"] = (carr_agg["Delivered"] / carr_agg["Parcels"].replace(0, 1) * 100).round(1)
            carr_agg["RTO %"] = (carr_agg["RTO"] / carr_agg["Parcels"].replace(0, 1) * 100).round(1)
            carr_del_lbl = [f"<b>{p:.1f}%</b><br>({int(c):,})" for p, c in zip(carr_agg["Delivery %"], carr_agg["Delivered"])]
            carr_rto_lbl = [f"<b>{p:.1f}%</b><br>({int(c):,})" for p, c in zip(carr_agg["RTO %"], carr_agg["RTO"])]
            fig_car = go.Figure()
            fig_car.add_trace(go.Bar(x=carr_agg["Dispatch_Category"], y=carr_agg["Delivery %"], name="Delivery %", marker=dict(color="#4F46E5", cornerradius=8), text=carr_del_lbl, textposition="outside"))
            fig_car.add_trace(go.Bar(x=carr_agg["Dispatch_Category"], y=carr_agg["RTO %"], name="RTO %", marker=dict(color="#FF5C8D", cornerradius=8), text=carr_rto_lbl, textposition="outside"))
            fig_car.update_layout(barmode="group", height=340, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 118], showgrid=True, gridcolor="#F1F5F9"))
            st.plotly_chart(fig_car, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r3:
        st.markdown('<div class="card-box"><div class="card-title">🏭 RTO Pending to Hub (Unique Orders)</div>', unsafe_allow_html=True)
        if not rto_pending_hub_df.empty and "Dispatch_Category" in rto_pending_hub_df.columns:
            hub_agg = rto_pending_hub_df.groupby("Dispatch_Category").agg(Pending_Parcels=("Order_ID", "count"), Unique_Orders=("Base_Order_ID", "nunique")).reset_index()
            hub_lbl = [f"<b>{int(o):,} ord</b> ({int(p):,} pcl)" for p, o in zip(hub_agg["Pending_Parcels"], hub_agg["Unique_Orders"])]
            fig_hub = go.Figure(go.Bar(x=hub_agg["Dispatch_Category"], y=hub_agg["Unique_Orders"], name="RTO Pending Hub (Unique Orders)", marker=dict(color="#EA580C", cornerradius=8), text=hub_lbl, textposition="outside"))
            fig_hub.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, max(float(hub_agg["Unique_Orders"].max()) * 1.25, 5.0)], showgrid=True, gridcolor="#F1F5F9"))
            st.plotly_chart(fig_hub, use_container_width=True)
        else:
            st.info("No RTO shipments pending to hub in selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"#### 🔄 Exchanges (<code>Fact_Reverse_Logistics</code> — {exch_cnt:,} Unique Orders)")
    if not p_rev.empty:
        st.dataframe(p_rev, use_container_width=True, height=260, hide_index=True)
        st.download_button(
            "⬇️ Download Exchanges (Fact_Reverse_Logistics) CSV",
            p_rev.to_csv(index=False).encode("utf-8"),
            f"exchanges_fact_reverse_logistics_{start_date}_{end_date}.csv",
            "text/csv"
        )
    else:
        st.info("निवडलेल्या तारीख रेंजमधील ऑर्डर्ससाठी `Fact_Reverse_Logistics` मध्ये कोणतेही Exchange रेकॉर्ड्स नाहीत.")

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
