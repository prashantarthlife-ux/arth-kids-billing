import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & CLEAN SECTION-WISE STYLING
# ==============================================================================
st.set_page_config(
    page_title="Arth life Daily Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background-color: #F1F5F9;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

.block-container {
    padding-top: 1.0rem !important;
    padding-bottom: 2.2rem !important;
    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

.main-banner {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}
.main-h1 {
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
    margin: 0;
}
.main-sub {
    font-size: 12.5px;
    color: #64748B;
    margin-top: 3px;
}

.sec-bar {
    font-size: 14.5px;
    font-weight: 800;
    color: #0F172A;
    margin: 18px 0 8px 2px;
    padding-left: 10px;
    border-left: 4px solid #4F46E5;
}

/* KPI Cards */
.kpi-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid var(--accent, #4F46E5);
    border-radius: 14px 14px 4px 4px;
    padding: 14px 16px 10px 16px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
.kpi-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}
.kpi-lbl {
    font-size: 11px;
    font-weight: 800;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.kpi-pill-pos {
    background: #ECFDF5;
    color: #059669;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}
.kpi-pill-neg {
    background: #FFF1F2;
    color: #E11D48;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}
.kpi-pill-neu {
    background: #F1F5F9;
    color: #475569;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}
.kpi-main-num {
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
    margin: 8px 0 6px 0;
    line-height: 1.05;
}
.kpi-foot {
    font-size: 11.5px;
    font-weight: 600;
    color: #334155;
    border-top: 1px dashed #E2E8F0;
    padding-top: 6px;
}

.viz-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px 14px 10px 14px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    margin-bottom: 14px;
}
.viz-heading {
    text-align: center;
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
}
.viz-info {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 7px 10px;
    margin-top: 6px;
    font-size: 12px;
    color: #334155;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOADING & HELPERS
# ==============================================================================
DEFAULT_PATH = r"C:\Users\yasha\OneDrive\Desktop\New folder (4)\New folder (4)\New folder\PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx"

@st.cache_data
def load_model(file_source):
    xls = pd.ExcelFile(file_source)
    orders = pd.read_excel(xls, sheet_name="Dim_Orders")
    disp = pd.read_excel(xls, sheet_name="Fact_Dispatches")
    rev = pd.read_excel(xls, sheet_name="Fact_Reverse_Logistics") if "Fact_Reverse_Logistics" in xls.sheet_names else pd.DataFrame()

    orders["Order_Date_dt"] = pd.to_datetime(orders["Order_Date"], dayfirst=True, errors="coerce")
    for c in ["Order_Total", "Order_Subtotal", "Discount", "Shipping", "Total_Line_Items"]:
        if c in orders.columns:
            orders[c] = pd.to_numeric(orders[c], errors="coerce").fillna(0)

    disp["Dispatch_Date_dt"] = pd.to_datetime(disp["Dispatch_Date"], dayfirst=True, errors="coerce")
    disp["Amount"] = pd.to_numeric(disp.get("Amount", 0), errors="coerce").fillna(0)
    disp["Is_Delivered"] = disp.get("Is_Delivered", False).fillna(False).astype(bool)
    disp["Is_RTO"] = disp.get("Is_RTO", False).fillna(False).astype(bool)

    if not rev.empty and "Pickup_Date" in rev.columns:
        rev["Pickup_Date_dt"] = pd.to_datetime(rev["Pickup_Date"], dayfirst=True, errors="coerce")
        rev["Amount"] = pd.to_numeric(rev.get("Amount", 0), errors="coerce").fillna(0)

    return orders, disp, rev

def make_sparkline(x_labels, y_vals, line_color="#4F46E5"):
    fig = go.Figure(go.Scatter(
        x=x_labels, y=y_vals,
        mode="lines+markers",
        line=dict(color=line_color, width=2.3, shape="spline"),
        marker=dict(size=5, color=line_color),
        text=[str(v) for v in y_vals],
        hovertemplate="%{x}: <b>%{text}</b><extra></extra>"
    ))
    fig.update_layout(
        height=42,
        margin=dict(l=4, r=4, t=4, b=2),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

def fmt_pill(diff_val, prev_val):
    if prev_val > 0:
        pct = diff_val / prev_val * 100.0
        cls = "kpi-pill-pos" if diff_val >= 0 else "kpi-pill-neg"
        return f'<span class="{cls}">{diff_val:+d} ({pct:+.1f}%)</span>'
    if diff_val != 0:
        cls = "kpi-pill-pos" if diff_val > 0 else "kpi-pill-neg"
        return f'<span class="{cls}">{diff_val:+d}</span>'
    return '<span class="kpi-pill-neu">0 (0.0%)</span>'

# Sidebar Controls
with st.sidebar:
    st.markdown("### 📅 Arth life Controls")
    uploaded = st.file_uploader("Upload Model Excel (.xlsx)", type=["xlsx"])
    local_matches = [f for f in os.listdir(".") if f.endswith(".xlsx") and "Dimensional_Model" in f] if os.path.exists(".") else []
    source = uploaded if uploaded is not None else (DEFAULT_PATH if os.path.exists(DEFAULT_PATH) else (local_matches[0] if local_matches else None))

    if source is None:
        st.warning("कृपया `PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx` अपलोड करा.")
        st.stop()

    df_orders, df_disp, df_rev = load_model(source)

    valid_dates = df_orders["Order_Date_dt"].dropna()
    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()
    default_target = datetime.date(2026, 11, 22)
    init_date = default_target if min_d <= default_target <= max_d else max_d

# ==============================================================================
# 2B. TOP BANNER + PARTICULAR DATE & REGION CONTROLS
# ==============================================================================
all_regions = sorted(df_orders["Customer_Region"].dropna().unique().tolist())

b1, b2, b3 = st.columns([1.45, 1.05, 1.25])
with b1:
    st.markdown("""
    <div class="main-banner">
        <div class="main-h1">Arth life Daily Analysis</div>
        <div class="main-sub">Particular Date KPIs + Automatic Rolling 7-Day Section-wise Analysis</div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    selected_date = st.date_input(
        "📅 Select Particular Date (Auto 7 Days)",
        value=init_date,
        min_value=min_d,
        max_value=max_d,
        key="arth_daily_date"
    )

with b3:
    sel_regions = st.multiselect(
        "🌍 Region Filter",
        options=all_regions,
        default=all_regions,
        key="arth_daily_regions"
    )

if not sel_regions:
    sel_regions = all_regions

start_7d = selected_date - datetime.timedelta(days=6)
dates_7d = [start_7d + datetime.timedelta(days=i) for i in range(7)]

with st.sidebar:
    st.divider()
    st.markdown(f"**Selected Date:** `{selected_date.strftime('%d %b %Y')}`")
    st.markdown(f"**7-Day Window:** `{start_7d.strftime('%d %b')}` – `{selected_date.strftime('%d %b %Y')}`")

# ==============================================================================
# 3. METRICS COMPUTATION
# ==============================================================================
f_orders = df_orders[df_orders["Customer_Region"].isin(sel_regions)].copy()
f_orders["_ord_d"] = f_orders["Order_Date_dt"].dt.date
f_orders["_ym"] = f_orders["Order_Date_dt"].dt.to_period("M").astype(str)

fin_low = f_orders["Financial_Status"].fillna("").astype(str).str.strip().str.lower()
valid_orders = f_orders[~fin_low.isin(["voided", "cancelled"])].copy()

# DAX-aligned orders (excludes voided, cancelled, refunded)
fin_low_dax = f_orders["Financial_Status"].fillna("").astype(str).str.strip().str.lower()
dax_orders = f_orders[~fin_low_dax.isin(["voided", "cancelled", "refunded"])].copy()

f_disp = df_disp[df_disp["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))].copy()
f_disp["_disp_d"] = f_disp["Dispatch_Date_dt"].dt.date
stat_str = f_disp["Shipment_Status"].fillna("").astype(str).str.strip()
valid_disp = f_disp[~stat_str.isin(["CANCELLED", "Stop Booking/Delivery"])].copy()

if not df_rev.empty and "Base_Order_ID" in df_rev.columns:
    f_rev = df_rev[df_rev["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))].copy()
    f_rev["_rev_d"] = f_rev["Pickup_Date_dt"].dt.date if "Pickup_Date_dt" in f_rev.columns else pd.NaT
else:
    f_rev = pd.DataFrame(columns=["Base_Order_ID", "_rev_d"])

prev_date = selected_date - datetime.timedelta(days=1)

# Unfulfilled Orders. logic:
# LatestMonthYear = MAX(Year_Month) across orders (up to selected_date if filtered, else max in Dim_Orders)
latest_ym_val = f_orders[f_orders["_ord_d"] <= selected_date]["_ym"].dropna().max()
if pd.isna(latest_ym_val) or not latest_ym_val:
    latest_ym_val = f_orders["_ym"].dropna().max()

ful_str_dax = dax_orders["Fulfillment_Status"].fillna("").astype(str).str.strip()
latest_month_unful_df = dax_orders[
    (dax_orders["_ym"] == latest_ym_val) &
    (ful_str_dax.loc[dax_orders.index] == "Unfulfilled")
].copy()
latest_month_unful_cnt = int(len(latest_month_unful_df))

day_ord = valid_orders[valid_orders["_ord_d"] == selected_date]
ord_day_cnt = len(set(day_ord["Base_Order_ID"].dropna().astype(str)))
ord_prev_cnt = len(set(valid_orders[valid_orders["_ord_d"] == prev_date]["Base_Order_ID"].dropna().astype(str)))
ord_diff = ord_day_cnt - ord_prev_cnt
day_rev_amt = float(day_ord["Order_Total"].sum())
day_aov_amt = day_rev_amt / ord_day_cnt if ord_day_cnt > 0 else 0.0

pre_day_cnt = len(set(
    day_ord[
        day_ord["Financial_Status"].fillna("").astype(str).str.strip().str.lower().isin(["paid", "authorized"])
    ]["Base_Order_ID"].dropna().astype(str)
))
cod_day_cnt = max(0, ord_day_cnt - pre_day_cnt)

ful_low = valid_orders["Fulfillment_Status"].fillna("").astype(str).str.strip().str.lower()
ful_day_cnt = len(set(
    valid_orders[
        (valid_orders["_ord_d"] == selected_date) &
        (ful_low == "fulfilled")
    ]["Base_Order_ID"].dropna().astype(str)
))

unful_day_cnt = len(set(
    valid_orders[
        (valid_orders["_ord_d"] == selected_date) &
        (~ful_low.isin(["fulfilled", "shipped"]))
    ]["Base_Order_ID"].dropna().astype(str)
))
unful_prev_cnt = len(set(
    valid_orders[
        (valid_orders["_ord_d"] == prev_date) &
        (~ful_low.isin(["fulfilled", "shipped"]))
    ]["Base_Order_ID"].dropna().astype(str)
))
unful_diff = unful_day_cnt - unful_prev_cnt

disp_day_cnt = len(set(valid_disp[valid_disp["_disp_d"] == selected_date]["Base_Order_ID"].dropna().astype(str)))
disp_prev_cnt = len(set(valid_disp[valid_disp["_disp_d"] == prev_date]["Base_Order_ID"].dropna().astype(str)))
disp_diff = disp_day_cnt - disp_prev_cnt

disp_up_to_eff = set(valid_disp[valid_disp["_disp_d"] <= selected_date]["Base_Order_ID"].dropna().astype(str))
rto_mask = (
    f_disp["Is_RTO"].astype(bool) |
    stat_str.isin(["RETURNED_TO_ORIGIN", "RETURNING_TO_ORIGIN", "RTO Delivered", "Set RTO"])
)

rows_7d = []
for d_k in dates_7d:
    odf_k = valid_orders[valid_orders["_ord_d"] == d_k]
    oids_k = set(odf_k["Base_Order_ID"].dropna().astype(str))
    ord_k = len(oids_k)
    rev_k = float(odf_k["Order_Total"].sum())
    aov_k = rev_k / ord_k if ord_k > 0 else 0.0

    pre_k = len(set(
        odf_k[
            odf_k["Financial_Status"].fillna("").astype(str).str.strip().str.lower().isin(["paid", "authorized"])
        ]["Base_Order_ID"].dropna().astype(str)
    ))
    cod_k = max(0, ord_k - pre_k)

    ddf_k = valid_disp[valid_disp["_disp_d"] == d_k]
    dp_k = len(set(ddf_k["Base_Order_ID"].dropna().astype(str)))
    delh_k = int((ddf_k["Dispatch_Category"] == "Delhivery").sum()) if "Dispatch_Category" in ddf_k.columns else 0
    dtdc_k = int((ddf_k["Dispatch_Category"] == "DTDC").sum()) if "Dispatch_Category" in ddf_k.columns else 0

    undisp_k = len(oids_k - disp_up_to_eff)
    ful_k = len(set(
        odf_k[
            odf_k["Fulfillment_Status"].fillna("").astype(str).str.strip().str.lower().isin(["fulfilled", "shipped"])
        ]["Base_Order_ID"].dropna().astype(str)
    ))
    unful_k = len(set(
        odf_k[
            ~odf_k["Fulfillment_Status"].fillna("").astype(str).str.strip().str.lower().isin(["fulfilled", "shipped"])
        ]["Base_Order_ID"].dropna().astype(str)
    ))

    rto_k = int(f_disp[(f_disp["_disp_d"] == d_k) & rto_mask]["Base_Order_ID"].nunique())
    ex_k = int(f_rev[f_rev["_rev_d"] == d_k]["Base_Order_ID"].nunique()) if (not f_rev.empty and "_rev_d" in f_rev.columns) else 0

    rows_7d.append({
        "Date": d_k.strftime("%d %b"),
        "Orders": ord_k,
        "Prepaid": pre_k,
        "COD": cod_k,
        "Revenue": rev_k,
        "AOV": aov_k,
        "Dispatched": dp_k,
        "Delhivery": delh_k,
        "DTDC": dtdc_k,
        "Undispatched": undisp_k,
        "Fulfilled": ful_k,
        "Unfulfilled": unful_k,
        "RTO": rto_k,
        "Exchange": ex_k
    })
df_7d = pd.DataFrame(rows_7d)

# ==============================================================================
# 4. TOP 4 KPI CARDS (PARTICULAR DATE + LATEST MONTH UNFULFILLED + SPARKLINES)
# ==============================================================================
c_k1, c_k2, c_k3, c_k4 = st.columns(4)

with c_k1:
    st.markdown(f"""
    <div class="kpi-box" style="--accent:#4F46E5;">
        <div class="kpi-head"><span class="kpi-lbl">Orders Created ({selected_date.strftime('%d %b')})</span>{fmt_pill(ord_diff, ord_prev_cnt)}</div>
        <div class="kpi-main-num">{ord_day_cnt:,}</div>
        <div class="kpi-foot">Prepaid: <b>{pre_day_cnt:,}</b> | COD: <b>{cod_day_cnt:,}</b> · Rev: <b>₹{day_rev_amt:,.0f}</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(make_sparkline(df_7d["Date"], df_7d["Orders"], "#4F46E5"), use_container_width=True)

with c_k2:
    st.markdown(f"""
    <div class="kpi-box" style="--accent:#E11D48;">
        <div class="kpi-head"><span class="kpi-lbl">Unfulfilled Orders ({latest_ym_val})</span><span class="kpi-pill-neg">Latest Month</span></div>
        <div class="kpi-main-num">{latest_month_unful_cnt:,}</div>
        <div class="kpi-foot">Year_Month: <b>{latest_ym_val}</b> • Status: Unfulfilled</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(make_sparkline(df_7d["Date"], df_7d["Unfulfilled"], "#E11D48"), use_container_width=True)

with c_k3:
    val_ful_disp = f"{ful_day_cnt:,}" if ful_day_cnt > 0 else "—"
    st.markdown(f"""
    <div class="kpi-box" style="--accent:#7C3AED;">
        <div class="kpi-head"><span class="kpi-lbl">Day Wise Fulfilled</span><span class="kpi-pill-neu">AOV: ₹{day_aov_amt:,.0f}</span></div>
        <div class="kpi-main-num">{val_ful_disp}</div>
        <div class="kpi-foot">Fulfilled on {selected_date.strftime('%d %b')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(make_sparkline(df_7d["Date"], df_7d["Fulfilled"], "#7C3AED"), use_container_width=True)

with c_k4:
    st.markdown(f"""
    <div class="kpi-box" style="--accent:#F59E0B;">
        <div class="kpi-head"><span class="kpi-lbl">Day Wise Unfulfilled</span>{fmt_pill(unful_diff, unful_prev_cnt)}</div>
        <div class="kpi-main-num">{unful_day_cnt:,}</div>
        <div class="kpi-foot">Prev Day ({prev_date.strftime('%d %b')}): <b>{unful_prev_cnt:,}</b> Unfulfilled</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(make_sparkline(df_7d["Date"], df_7d["Unfulfilled"], "#F59E0B"), use_container_width=True)

# ==============================================================================
# 5. SECTION-WISE CHARTS & INFORMATIVE NOTES (AUTO 7 DAYS)
# ==============================================================================
tot_7d_ord = int(df_7d["Orders"].sum())
tot_7d_pre = int(df_7d["Prepaid"].sum())
tot_7d_cod = int(df_7d["COD"].sum())
tot_7d_rev = float(df_7d["Revenue"].sum())
avg_7d_aov = tot_7d_rev / tot_7d_ord if tot_7d_ord > 0 else 0.0
tot_7d_undisp = int(df_7d["Undispatched"].sum())
tot_7d_ful = int(df_7d["Fulfilled"].sum())
tot_7d_disp = int(df_7d["Dispatched"].sum())
tot_7d_delh = int(df_7d["Delhivery"].sum())
tot_7d_dtdc = int(df_7d["DTDC"].sum())
tot_7d_rto = int(df_7d["RTO"].sum())
tot_7d_ex = int(df_7d["Exchange"].sum())

# SECTION 1: ORDERS, REVENUE & DISPATCH CORE
st.markdown('<div class="sec-bar">Section 1 — Orders Created, Revenue/AOV & Daily Dispatches (7 Days)</div>', unsafe_allow_html=True)
s1_l, s1_r = st.columns([1.05, 1.0])

with s1_l:
    st.markdown('<div class="viz-card"><div class="viz-heading">Order Created by Prepaid or COD</div>', unsafe_allow_html=True)
    fig_oc = go.Figure()
    fig_oc.add_trace(go.Bar(
        x=df_7d["Date"], y=df_7d["Prepaid"], name="Prepaid Orders",
        marker=dict(color="#4F46E5", cornerradius=4), text=df_7d["Prepaid"], textposition="inside",
        textfont=dict(color="#FFFFFF", size=10.5)
    ))
    fig_oc.add_trace(go.Bar(
        x=df_7d["Date"], y=df_7d["COD"], name="COD Orders",
        marker=dict(color="#06B6D4", cornerradius=4), text=df_7d["COD"], textposition="inside",
        textfont=dict(color="#0F172A", size=10.5)
    ))
    fig_oc.add_trace(go.Scatter(
        x=df_7d["Date"], y=df_7d["Orders"], name="Total Orders",
        mode="lines+text", line=dict(color="rgba(0,0,0,0)"),
        text=[f"<b>{v}</b>" for v in df_7d["Orders"]],
        textposition="top center", textfont=dict(size=11.5, color="#1E1B4B")
    ))
    fig_oc.update_layout(
        barmode="stack", height=270,
        margin=dict(l=8, r=8, t=26, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["Orders"].max(), 1) * 1.28], showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_oc, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>7D Orders:</b> Total <b>{tot_7d_ord:,}</b> orders (Prepaid: <b>{tot_7d_pre:,}</b> | COD: <b>{tot_7d_cod:,}</b>) · Avg <b>{tot_7d_ord/7:.1f}/day</b>.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="viz-card"><div class="viz-heading">Daily Order Revenue (₹) & Average Order Value (AOV)</div>', unsafe_allow_html=True)
    fig_rev = make_subplots(specs=[[{"secondary_y": True}]])
    fig_rev.add_trace(go.Bar(
        x=df_7d["Date"], y=df_7d["Revenue"], name="Revenue (₹)",
        marker=dict(color="#6366F1", cornerradius=5),
        text=[f"₹{v/1000:.1f}k" for v in df_7d["Revenue"]],
        textposition="outside", textfont=dict(size=10, color="#312E81")
    ), secondary_y=False)
    fig_rev.add_trace(go.Scatter(
        x=df_7d["Date"], y=df_7d["AOV"], name="AOV (₹)",
        mode="lines+markers", line=dict(color="#F59E0B", width=2.5, shape="spline"),
        marker=dict(size=7, color="#F59E0B")
    ), secondary_y=True)
    fig_rev.update_layout(
        height=240, margin=dict(l=8, r=8, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_rev.update_yaxes(range=[0, max(df_7d["Revenue"].max(), 1) * 1.28], showgrid=True, gridcolor="#F1F5F9", secondary_y=False)
    fig_rev.update_yaxes(range=[0, max(df_7d["AOV"].max(), 1) * 1.35], showgrid=False, secondary_y=True)
    st.plotly_chart(fig_rev, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>7D Revenue:</b> Gross <b>₹{tot_7d_rev:,.0f}</b> · 7-Day Avg AOV: <b>₹{avg_7d_aov:,.0f}</b>.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s1_r:
    st.markdown(f"""
    <div class="kpi-box" style="--accent:#10B981;">
        <div class="kpi-head"><span class="kpi-lbl">Total Dispatched Output ({selected_date.strftime('%d %b')})</span>{fmt_pill(disp_diff, disp_prev_cnt)}</div>
        <div class="kpi-main-num">{disp_day_cnt:,}</div>
        <div class="kpi-foot">Prev Day ({prev_date.strftime('%d %b')}): <b>{disp_prev_cnt:,}</b> Dispatched</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(make_sparkline(df_7d["Date"], df_7d["Dispatched"], "#10B981"), use_container_width=True)

    st.markdown('<div class="viz-card"><div class="viz-heading">Dispatched Orders (7 Days)</div>', unsafe_allow_html=True)
    fig_dp = go.Figure(go.Bar(
        x=df_7d["Date"], y=df_7d["Dispatched"],
        marker=dict(color="#10B981", cornerradius=5),
        text=[f"<b>{v}</b>" for v in df_7d["Dispatched"]],
        textposition="outside", textfont=dict(color="#065F46", size=11)
    ))
    fig_dp.update_layout(
        height=230, margin=dict(l=8, r=8, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["Dispatched"].max(), 1) * 1.28], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_dp, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>Dispatch Summary:</b> Total <b>{tot_7d_disp:,}</b> dispatches in 7 days · Peak: <b>{int(df_7d["Dispatched"].max()):,}</b> · Avg: <b>{tot_7d_disp/7:.1f}/day</b>.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="viz-card"><div class="viz-heading">Carrier-wise Daily Dispatch (Delhivery vs DTDC)</div>', unsafe_allow_html=True)
    fig_car = go.Figure()
    fig_car.add_trace(go.Bar(
        x=df_7d["Date"], y=df_7d["Delhivery"], name="Delhivery",
        marker=dict(color="#0EA5E9", cornerradius=4), text=df_7d["Delhivery"], textposition="inside"
    ))
    fig_car.add_trace(go.Bar(
        x=df_7d["Date"], y=df_7d["DTDC"], name="DTDC",
        marker=dict(color="#8B5CF6", cornerradius=4), text=df_7d["DTDC"], textposition="inside"
    ))
    fig_car.update_layout(
        barmode="stack", height=215, margin=dict(l=8, r=8, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_car, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>7D Carrier Parcels:</b> Delhivery: <b>{tot_7d_delh:,}</b> | DTDC: <b>{tot_7d_dtdc:,}</b>.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# SECTION 2: UNDISPATCHED ORDERS (7D), FULFILLED, DAILY RTO & DAILY EXCHANGE
st.markdown('<div class="sec-bar">Section 2 — Undispatched Orders, Fulfilled, Daily RTO & Exchange (7 Days)</div>', unsafe_allow_html=True)
s2_1, s2_2, s2_3, s2_4 = st.columns(4)

with s2_1:
    st.markdown('<div class="viz-card"><div class="viz-heading">Undispatched Orders (7D)</div>', unsafe_allow_html=True)
    fig_bl = go.Figure(go.Bar(
        x=df_7d["Date"], y=df_7d["Undispatched"],
        marker=dict(color="#F43F5E", cornerradius=5),
        text=[f"<b>{v}</b>" for v in df_7d["Undispatched"]],
        textposition="outside", textfont=dict(color="#9F1239", size=10.5)
    ))
    fig_bl.update_layout(
        height=210, margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["Undispatched"].max(), 1) * 1.32], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_bl, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>Total Undispatched (7D):</b> <b>{tot_7d_undisp:,}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s2_2:
    st.markdown('<div class="viz-card"><div class="viz-heading">Daily Fulfilled (7D)</div>', unsafe_allow_html=True)
    fig_fl = go.Figure(go.Scatter(
        x=df_7d["Date"], y=df_7d["Fulfilled"],
        mode="lines+markers+text", fill="tozeroy",
        fillcolor="rgba(139, 92, 246, 0.16)",
        line=dict(color="#7C3AED", width=2.5, shape="spline"),
        marker=dict(size=6, color="#FFFFFF", line=dict(color="#7C3AED", width=2)),
        text=[f"<b>{v}</b>" for v in df_7d["Fulfilled"]],
        textposition="top center", textfont=dict(color="#5B21B6", size=10.5)
    ))
    fig_fl.update_layout(
        height=210, margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["Fulfilled"].max(), 1) * 1.35], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_fl, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>Total Fulfilled:</b> <b>{tot_7d_ful:,}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s2_3:
    st.markdown('<div class="viz-card"><div class="viz-heading">Daily RTO (7D)</div>', unsafe_allow_html=True)
    fig_rto = go.Figure(go.Bar(
        x=df_7d["Date"], y=df_7d["RTO"],
        marker=dict(color="#EF4444", cornerradius=5),
        text=[f"<b>{v}</b>" for v in df_7d["RTO"]],
        textposition="outside", textfont=dict(color="#991B1B", size=10.5)
    ))
    fig_rto.update_layout(
        height=210, margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["RTO"].max(), 1) * 1.35], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_rto, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>7D RTO Count:</b> <b>{tot_7d_rto:,}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s2_4:
    st.markdown('<div class="viz-card"><div class="viz-heading">Daily Exchange (7D)</div>', unsafe_allow_html=True)
    fig_ex = go.Figure(go.Bar(
        x=df_7d["Date"], y=df_7d["Exchange"],
        marker=dict(color="#8B5CF6", cornerradius=5),
        text=[f"<b>{v}</b>" for v in df_7d["Exchange"]],
        textposition="outside", textfont=dict(color="#5B21B6", size=10.5)
    ))
    fig_ex.update_layout(
        height=210, margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(df_7d["Exchange"].max(), 1) * 1.35], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_ex, use_container_width=True)
    st.markdown(f'<div class="viz-info"><b>7D Exchange Pickups:</b> <b>{tot_7d_ex:,}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# SECTION 3: RTO MOM, STATES DISPATCHED & ACTIONABLE PENDING LIST
st.markdown('<div class="sec-bar">Section 3 — MOM RTO, State Dispatch & Actionable Unfulfilled Orders</div>', unsafe_allow_html=True)
s3_1, s3_2, s3_3 = st.columns([0.85, 0.85, 1.45])

with s3_1:
    st.markdown('<div class="viz-card"><div class="viz-heading">RTO Count Analysis MOM</div>', unsafe_allow_html=True)
    rto_m = f_disp[
        f_disp["Is_RTO"].astype(bool) |
        stat_str.isin(["RETURNED_TO_ORIGIN", "RETURNING_TO_ORIGIN", "RTO Delivered", "Set RTO"])
    ].copy()
    rto_m = rto_m[rto_m["Dispatch_Date_dt"].dt.date <= selected_date]
    rto_m["YM"] = rto_m["Dispatch_Date_dt"].dt.to_period("M")
    mom_s = rto_m.groupby("YM")["Base_Order_ID"].nunique().tail(5)
    m_lbls = [p.strftime("%b") for p in mom_s.index]
    m_vals = mom_s.values
    indigo_shades = ["#818CF8", "#6366F1", "#4F46E5", "#312E81", "#A5B4FC"][:len(m_vals)]
    fig_mom = go.Figure(go.Bar(
        x=m_lbls, y=m_vals, marker=dict(color=indigo_shades, cornerradius=5),
        text=[f"<b>{v}</b>" for v in m_vals], textposition="outside", textfont=dict(size=10.5)
    ))
    fig_mom.update_layout(
        height=240, margin=dict(l=5, r=5, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, max(list(m_vals) + [1]) * 1.28], showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_mom, use_container_width=True)
    peak_m_txt = f"{m_lbls[int(np.argmax(m_vals))]} ({int(np.max(m_vals)):,})" if len(m_vals) > 0 else "N/A"
    st.markdown(f'<div class="viz-info"><b>Peak Month:</b> <b>{peak_m_txt}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s3_2:
    st.markdown(f'<div class="viz-card"><div class="viz-heading">States Dispatched ({selected_date.strftime("%d %b")})</div>', unsafe_allow_html=True)
    d_sel_disp = f_disp[f_disp["_disp_d"] == selected_date].copy()
    st_col = "Customer_State" if "Customer_State" in d_sel_disp.columns else None
    if st_col and not d_sel_disp.empty:
        st_vc = d_sel_disp[st_col].fillna("Unknown").replace("", "Unknown").value_counts().head(7)
        jewel_palette = ["#4F46E5", "#06B6D4", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#3B82F6"]
        fig_st = go.Figure(go.Pie(
            labels=st_vc.index, values=st_vc.values, hole=0.56,
            marker=dict(colors=jewel_palette[:len(st_vc)], line=dict(color="#FFFFFF", width=2)),
            textinfo="label+value"
        ))
        fig_st.add_annotation(text=f"<b>{disp_day_cnt}</b>", x=0.5, y=0.5, font_size=14, showarrow=False)
        fig_st.update_layout(
            height=240, margin=dict(l=5, r=5, t=15, b=5),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )
        st.plotly_chart(fig_st, use_container_width=True)
        top_st_txt = f"{st_vc.index[0]} ({int(st_vc.iloc[0])})"
        st.markdown(f'<div class="viz-info"><b>Top State:</b> <b>{top_st_txt}</b></div>', unsafe_allow_html=True)
    else:
        st.info("No dispatches on selected date.")
        st.markdown('<div class="viz-info"><b>Top State:</b> None on selected date</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s3_3:
    st.markdown(f'<div class="viz-card"><div class="viz-heading">Actionable Unfulfilled Orders ({latest_ym_val}: {latest_month_unful_cnt})</div>', unsafe_allow_html=True)
    show_cols = [c for c in ["Base_Order_ID", "Order_Date", "Customer_Name", "Financial_Status", "Fulfillment_Status", "Order_Total", "Order_Notes"] if c in latest_month_unful_df.columns]
    pending_view = latest_month_unful_df[show_cols].sort_values(by="Order_Date", ascending=False)
    st.dataframe(pending_view, use_container_width=True, height=235, hide_index=True)
    st.download_button(
        label="⬇️ Download Unfulfilled Orders CSV",
        data=pending_view.to_csv(index=False).encode("utf-8"),
        file_name=f"unfulfilled_{latest_ym_val}_{selected_date.strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)