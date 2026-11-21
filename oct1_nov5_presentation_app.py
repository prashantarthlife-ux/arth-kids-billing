import os
import base64
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & EXECUTIVE SAAS STYLING
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

/* Login Card Styling */
.login-wrap {
    max-width: 440px;
    margin: 56px auto 18px auto;
    background: #FFFFFF;
    border-radius: 24px;
    padding: 34px 32px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
    border: 1px solid #E6EAF2;
    text-align: center;
}
.login-badge {
    width: 72px;
    height: 72px;
    margin: 0 auto 14px auto;
    border-radius: 50%;
    background: linear-gradient(135deg, #312E81 0%, #7C3AED 100%);
    color: #FFFFFF;
    font-size: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 22px rgba(124, 58, 237, 0.25);
}
.login-title { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0; }
.login-sub   { font-size: 13px; color: #64748B; margin-top: 5px; margin-bottom: 12px; }

/* Executive Banner */
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
    gap: 16px;
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
    white-space: nowrap;
}

/* Section Headers */
.sec-header-rto {
    background: linear-gradient(90deg, #FFF1F2 0%, #FFFFFF 100%);
    border-left: 5px solid #EF4444;
    border-radius: 14px;
    padding: 14px 20px;
    margin-top: 14px;
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
    margin-top: 22px;
    margin-bottom: 14px;
    border-top: 1px solid #EDE9FE;
    border-right: 1px solid #EDE9FE;
    border-bottom: 1px solid #EDE9FE;
}
.sec-title { font-size: 18px; font-weight: 800; color: #0F172A; margin: 0; }
.sec-sub   { font-size: 12.5px; color: #64748B; margin-top: 2px; }

/* KPI Cards with Larger, Crisp Icons */
.kpi-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    border: 1px solid #E6EAF2;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(15, 23, 42, 0.10); }
.kpi-lbl  { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.45px; }
.kpi-val  { font-size: 22px; font-weight: 800; color: #0F172A; margin: 5px 0; letter-spacing: -0.5px; }
.kpi-tag  { display: inline-block; font-size: 11px; font-weight: 700; padding: 3.5px 10px; border-radius: 999px; }
.kpi-ico  {
    width: 54px;
    height: 54px;
    min-width: 54px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    line-height: 1;
    box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.05);
}

/* Mini Sub-KPI Cards inside Sections */
.sub-kpi {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 14px 18px;
    border: 1px solid #E6EAF2;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.sub-kpi-lbl { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; }
.sub-kpi-val { font-size: 21px; font-weight: 800; color: #0F172A; margin-top: 2px; }
.sub-kpi-ico { width: 46px; height: 46px; border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 24px; }

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
# 2. LOGO LOADER (logo.jpeg FIRST + FALLBACKS)
# ==============================================================================
LOGO_CANDIDATES = [
    "logo.jpeg",
    "Arth_life_Loge.jpeg",
    "Arth_life_Logo.jpeg",
    "arth_life_loge.jpeg",
    "logo.jpg",
    "logo.png",
]

def _get_logo_data_uri():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        script_dir,
        os.path.join(script_dir, "data"),
        os.path.join(script_dir, "assets"),
        os.getcwd(),
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.getcwd(), "assets"),
    ]
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            for cand in LOGO_CANDIDATES:
                fp = os.path.abspath(os.path.join(folder, cand))
                if os.path.isfile(fp):
                    ext = os.path.splitext(fp)[1].lower().lstrip(".")
                    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'png'}"
                    try:
                        with open(fp, "rb") as img_f:
                            b64 = base64.b64encode(img_f.read()).decode("utf-8")
                        return f"data:{mime};base64,{b64}"
                    except Exception:
                        continue
    return None

LOGO_URI = _get_logo_data_uri()
LOGO_LOGIN_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    f'style="width:82px;height:82px;border-radius:50%;object-fit:cover;margin:0 auto 12px auto;display:block;box-shadow:0 8px 20px rgba(15,23,42,0.14);border:2px solid #E2E8F0;" />'
    if LOGO_URI else '<div class="login-badge">👗</div>'
)
LOGO_BANNER_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    f'style="width:58px;height:58px;min-width:58px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.45);box-shadow:0 6px 16px rgba(0,0,0,0.22);" />'
    if LOGO_URI else ''
)

# ==============================================================================
# 3. SECURE LOGIN GATE (USER ID & PASSWORD)
# ==============================================================================
def _get_credentials():
    try:
        if "auth" in st.secrets:
            return str(st.secrets["auth"].get("username", "arthlife")), str(st.secrets["auth"].get("password", "Arth@2026"))
    except Exception:
        pass
    return "arthlife", "Arth@2026"

VALID_USER, VALID_PASS = _get_credentials()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(f"""
    <div class="login-wrap">
        {LOGO_LOGIN_HTML}
        <div class="login-title">ARTH LIFE Kids Fashion</div>
        <div class="login-sub">Executive Shopify Analytics Portal — Please Sign In</div>
    </div>
    """, unsafe_allow_html=True)

    _, mid_col, _ = st.columns([1.15, 1, 1.15])
    with mid_col:
        with st.form("login_form", clear_on_submit=False):
            in_user = st.text_input("👤 User ID", placeholder="Enter User ID")
            in_pass = st.text_input("🔑 Password", type="password", placeholder="Enter Password")
            submitted = st.form_submit_button("🔓 Sign In to Dashboard", use_container_width=True)
            if submitted:
                if in_user.strip() == VALID_USER and in_pass == VALID_PASS:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID किंवा Password. कृपया पुन्हा प्रयत्न करा.")
        st.caption("Tip: Streamlit Cloud `Secrets` मध्ये `[auth]` सेट करून तुम्ही तुमचा स्वतःचा ID व Password बदलू शकता.")
    st.stop()

# ==============================================================================
# 4. DATA LOADING & PREPROCESSING
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

def _find_col(df: pd.DataFrame, candidates: list):
    if df is None or df.empty:
        return None
    col_map = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in col_map:
            return col_map[key]
    return None

@st.cache_data(show_spinner=False)
def load_model(file_source):
    xls = pd.ExcelFile(file_source)
    orders_sheet = "Dim_Orders (2)" if "Dim_Orders (2)" in xls.sheet_names else "Dim_Orders"
    disp_sheet = "Fact_Dispatches (2)" if "Fact_Dispatches (2)" in xls.sheet_names else "Fact_Dispatches"
    rev_sheet = (
        "Fact_Reverse_Logistics (2)" if "Fact_Reverse_Logistics (2)" in xls.sheet_names
        else ("Fact_Reverse_Logistics" if "Fact_Reverse_Logistics" in xls.sheet_names else None)
    )

    orders = pd.read_excel(xls, sheet_name=orders_sheet)
    disp = pd.read_excel(xls, sheet_name=disp_sheet)
    rev = pd.read_excel(xls, sheet_name=rev_sheet) if rev_sheet else pd.DataFrame()

    orders["Order_Date_dt"] = pd.to_datetime(orders["Order_Date"], format="mixed", dayfirst=True, errors="coerce")
    for c in ["Order_Total", "Order_Subtotal", "Discount", "Shipping", "Total_Line_Items"]:
        if c in orders.columns:
            cleaned_s = orders[c].astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False).str.strip()
            orders[c] = pd.to_numeric(cleaned_s, errors="coerce").fillna(0.0)

    pm = orders["Payment_Method"].fillna("Unknown").astype(str) if "Payment_Method" in orders.columns else pd.Series(["Unknown"] * len(orders))
    orders["Payment_Category"] = np.where(
        pm.str.lower().str.contains("cod|cash on delivery"), "COD",
        np.where(pm.str.lower().str.contains("razorpay|upi|card|wallet|prepaid"), "Prepaid (Razorpay)",
        np.where(pm.str.lower().str.contains("manual"), "Manual", "Other / Blank"))
    )

    if "Dispatch_Date" in disp.columns:
        disp["Dispatch_Date_dt"] = pd.to_datetime(disp["Dispatch_Date"], dayfirst=True, errors="coerce")
    disp["Amount"] = pd.to_numeric(disp.get("Amount", 0), errors="coerce").fillna(0.0)
    disp["Is_Delivered"] = disp.get("Is_Delivered", False).astype(bool)
    disp["Is_RTO"] = disp.get("Is_RTO", False).astype(bool)

    return orders, disp, rev

def _make_donut_fig(labels, values, colors, center_text):
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.58,
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        marker=dict(colors=colors[:len(labels)], line=dict(color="#FFFFFF", width=2.5)),
        hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_layout(
        height=370,
        margin=dict(l=15, r=15, t=20, b=65),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.06,
            xanchor="center",
            x=0.5,
            font=dict(size=11.5, color="#1E293B")
        ),
        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=14, showarrow=False)]
    )
    return fig

# Sidebar
with st.sidebar:
    if LOGO_URI:
        sb_c1, sb_c2 = st.columns([1, 3.2])
        with sb_c1:
            st.image(LOGO_URI, width=44)
        with sb_c2:
            st.markdown("### ARTH LIFE")
    else:
        st.markdown("### 👗 ARTH LIFE Shopify")
    st.caption("Kids Fashion E-Commerce Analytics")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
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

    reg_col = _find_col(df_orders, ["Customer_Region", "Region"])
    all_regions = sorted(df_orders[reg_col].dropna().astype(str).unique().tolist()) if reg_col else ["All"]
    sel_regions = st.multiselect("🌍 Filter Region", all_regions, default=all_regions)

# ==============================================================================
# 5. TOP BANNER & UNIFIED DATE SELECTION BAR
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
    <div style="display:flex; align-items:center; gap:16px;">
        {LOGO_BANNER_HTML}
        <div>
            <div class="exec-title">ARTH LIFE Kids Fashion — Shopify Analysis</div>
            <div class="exec-sub">Pure RTO & Cancelled Exchange Returns, Financial KPIs, Region/State RTO & Day-Wise Trends</div>
        </div>
    </div>
    <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. FILTER STRICTLY BY ORDER CREATED DATE (SINGLE PASS)
# ==============================================================================
if reg_col:
    p_orders = df_orders[
        (df_orders["Order_Date_dt"].dt.date >= start_date) &
        (df_orders["Order_Date_dt"].dt.date <= end_date) &
        (df_orders[reg_col].astype(str).isin(sel_regions))
    ].copy()
else:
    p_orders = df_orders[
        (df_orders["Order_Date_dt"].dt.date >= start_date) &
        (df_orders["Order_Date_dt"].dt.date <= end_date)
    ].copy()

# Exclude voided orders (`Financial_Status` == "voided") across all KPIs, charts, and tables
fin_status_col = _find_col(p_orders, ["Financial_Status"])
if fin_status_col:
    p_orders = p_orders[p_orders[fin_status_col].fillna("").astype(str).str.strip().str.lower() != "voided"].copy()

base_oid_col = _find_col(p_orders, ["Base_Order_ID", "Order_ID", "Name"])
period_ids = set(p_orders[base_oid_col].dropna()) if base_oid_col else set()

disp_base_col = _find_col(df_disp, ["Base_Order_ID", "Order_ID"])
p_disp = df_disp[df_disp[disp_base_col].isin(period_ids)].copy() if (not df_disp.empty and disp_base_col) else pd.DataFrame()

state_col_ord = _find_col(p_orders, ["Shipping_State", "State"])

if not p_disp.empty and base_oid_col:
    merge_cols = [base_oid_col, "Order_Date", "Order_Date_dt", "Payment_Category", "Order_Total"]
    for extra_c in ["Order_Notes", "Customer_Name", "Customer_Region", "Shipping_State", "State", "Shipping_City"]:
        found_ec = _find_col(p_orders, [extra_c])
        if found_ec and found_ec not in merge_cols and found_ec not in p_disp.columns:
            merge_cols.append(found_ec)
    merge_cols = [c for c in merge_cols if c in p_orders.columns]
    p_disp = p_disp.merge(
        p_orders[merge_cols].drop_duplicates(subset=[base_oid_col]),
        left_on=disp_base_col, right_on=base_oid_col, how="left"
    )

    status_col_d = _find_col(p_disp, ["Shipment_Status", "Status"])
    status_u = p_disp[status_col_d].fillna("").astype(str).str.strip().str.upper() if status_col_d else pd.Series([""] * len(p_disp))
    del_col_d = _find_col(p_disp, ["Delivered_Date"])
    has_del = (p_disp[del_col_d].notna() & (p_disp[del_col_d].astype(str).str.strip() != "")) if del_col_d else pd.Series([False] * len(p_disp))
    is_rto = p_disp["Is_RTO"].astype(bool) if "Is_RTO" in p_disp.columns else pd.Series([False] * len(p_disp))
    is_del = p_disp["Is_Delivered"].astype(bool) if "Is_Delivered" in p_disp.columns else pd.Series([False] * len(p_disp))
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
    if not p_disp.empty:
        p_disp["True_Delivered"] = False
        p_disp["True_Undelivered"] = False
        p_disp["True_In_Transit"] = False
        p_disp["True_Cancelled_Lost"] = False
        p_disp["RTO_Pending_Hub"] = False

dispatched_ids = set(p_disp[disp_base_col].dropna()) if (not p_disp.empty and disp_base_col) else set()
not_dispatched = p_orders[~p_orders[base_oid_col].isin(dispatched_ids)].copy() if base_oid_col else pd.DataFrame()

del_oids = set(p_disp[p_disp["True_Delivered"]][disp_base_col].dropna()) if (not p_disp.empty and disp_base_col) else set()
rto_all_oids = set(p_disp[p_disp["Is_RTO"]][disp_base_col].dropna()) if (not p_disp.empty and disp_base_col) else set()
rto_oids = rto_all_oids - del_oids

rto_pending_hub_df = p_disp[p_disp["RTO_Pending_Hub"]].copy() if not p_disp.empty else pd.DataFrame()
rto_pending_hub_oids = set(rto_pending_hub_df[disp_base_col].dropna()) if (not rto_pending_hub_df.empty and disp_base_col) else set()
int_oids = (set(p_disp[p_disp["True_In_Transit"]][disp_base_col].dropna()) - del_oids - rto_oids) if (not p_disp.empty and disp_base_col) else set()

rev_base_col = _find_col(df_rev, ["Base_Order_ID", "Order_ID"]) if not df_rev.empty else None
rev_order_id_col = _find_col(df_rev, ["Order_ID", "Base_Order_ID"]) if not df_rev.empty else None
rev_status_col = _find_col(df_rev, ["Reverse_Status", "Return_Status", "Exchange_Status", "Status"]) if not df_rev.empty else None

if not df_rev.empty and rev_base_col:
    p_rev_all = df_rev[df_rev[rev_base_col].isin(period_ids)].copy()
    if rev_status_col:
        rev_st_upper = p_rev_all[rev_status_col].fillna("").astype(str).str.strip().str.upper()
        p_rev_active = p_rev_all[rev_st_upper != "CANCELLED"].copy()
        p_rev_cancelled = p_rev_all[rev_st_upper == "CANCELLED"].copy()
    else:
        p_rev_active = p_rev_all.copy()
        p_rev_cancelled = pd.DataFrame(columns=p_rev_all.columns)
else:
    p_rev_all = pd.DataFrame()
    p_rev_active = pd.DataFrame()
    p_rev_cancelled = pd.DataFrame()

# ==============================================================================
# 7. KPI CALCULATIONS (PURE RTO + CANCELLED EXCHANGES = TOTAL RETURNS)
# ==============================================================================
if not p_orders.empty and base_oid_col:
    p_orders_uniq = p_orders.drop_duplicates(subset=[base_oid_col]).copy()
    tot_ord = int(p_orders[base_oid_col].nunique())
else:
    p_orders_uniq = p_orders.copy()
    tot_ord = len(p_orders)

gross_rev = float(p_orders_uniq["Order_Total"].sum()) if (len(p_orders_uniq) > 0 and "Order_Total" in p_orders_uniq.columns) else 0.0
tot_disc = float(p_orders_uniq["Discount"].sum()) if ("Discount" in p_orders_uniq.columns and len(p_orders_uniq) > 0) else 0.0
tot_ship = float(p_orders_uniq["Shipping"].sum()) if ("Shipping" in p_orders_uniq.columns and len(p_orders_uniq) > 0) else 0.0

pure_rto_cnt = len(rto_all_oids)

if not p_rev_cancelled.empty and rev_order_id_col:
    canc_exch_cnt = int(p_rev_cancelled[rev_order_id_col].nunique())
elif not p_rev_cancelled.empty and rev_base_col:
    canc_exch_cnt = int(p_rev_cancelled[rev_base_col].nunique())
else:
    canc_exch_cnt = len(p_rev_cancelled)

if not p_rev_active.empty and rev_order_id_col:
    exch_cnt = int(p_rev_active[rev_order_id_col].nunique())
else:
    exch_cnt = len(p_rev_active)

tot_ret_cnt = pure_rto_cnt + canc_exch_cnt
disp_cnt = len(dispatched_ids)
tot_ret_pct = (tot_ret_cnt / disp_cnt * 100) if disp_cnt > 0 else 0.0

rto_order_ids_set = set(rto_all_oids)
canc_exch_order_ids_set = set(p_rev_cancelled[rev_base_col].dropna()) if (not p_rev_cancelled.empty and rev_base_col) else set()
all_affected_ret_oids = rto_order_ids_set.union(canc_exch_order_ids_set)

tot_ret_amt = (
    float(p_orders_uniq[p_orders_uniq[base_oid_col].isin(all_affected_ret_oids)]["Order_Total"].sum())
    if (len(p_orders_uniq) > 0 and base_oid_col) else 0.0
)
net_rev = max(gross_rev - tot_ret_amt - tot_ship, 0.0)
realized_deliv_rev = float(p_orders_uniq[p_orders_uniq[base_oid_col].isin(del_oids)]["Order_Total"].sum()) if (len(p_orders_uniq) > 0 and base_oid_col) else 0.0

aov = gross_rev / tot_ord if tot_ord > 0 else 0.0
deliv_cnt = len(del_oids)
deliv_pct = (deliv_cnt / disp_cnt * 100) if disp_cnt > 0 else 0.0

rto_hub_parcels = int(p_disp["RTO_Pending_Hub"].sum()) if not p_disp.empty else 0
rto_hub_orders = len(rto_pending_hub_oids)

# Row 1: Financial KPIs
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Orders</div>
            <div class="kpi-val">{tot_ord:,}</div>
            <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{int(p_orders_uniq['Total_Line_Items'].sum()) if ('Total_Line_Items' in p_orders_uniq.columns and len(p_orders_uniq)>0) else 0:,} Items</span>
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

# Row 2: Operational & Return Breakdown KPIs
f1, f2, f3, f4, f5 = st.columns(5)
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
            <div class="kpi-lbl">Total Returns Display</div>
            <div class="kpi-val">{tot_ret_cnt:,} ({tot_ret_pct:.2f}%)</div>
            <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO {pure_rto_cnt:,} + Exch Canc {canc_exch_cnt:,}</span>
        </div>
        <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
    </div>""", unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Pure RTO / Exch Canc</div>
            <div class="kpi-val">{pure_rto_cnt:,} / {canc_exch_cnt:,}</div>
            <span class="kpi-tag" style="background:#FFF1F2; color:#BE123C;">Active Exch: {exch_cnt:,}</span>
        </div>
        <div class="kpi-ico" style="background:#FFF1F2;">🔄</div>
    </div>""", unsafe_allow_html=True)

with f5:
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
# 8. PRESENTATION TABS
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
        p_orders_uniq["Order_Date_Only"] = p_orders_uniq["Order_Date_dt"].dt.date
        daily = p_orders_uniq.groupby("Order_Date_Only").agg(
            Orders=(base_oid_col, "nunique"),
            Revenue=("Order_Total", "sum")
        ).reset_index().sort_values("Order_Date_Only")
        daily["Date_Label"] = pd.to_datetime(daily["Order_Date_Only"]).dt.strftime("%d %b")
        daily["Rev_Lakhs"] = (daily["Revenue"] / 1e5).round(2)
        daily["AOV"] = np.where(daily["Orders"] > 0, daily["Revenue"] / daily["Orders"], 0.0)
        daily["Custom_Hover"] = [
            f"₹{rev:,.2f} (₹{rev/1e5:.2f}L) | AOV: ₹{aov_v:,.0f}"
            for rev, aov_v in zip(daily["Revenue"], daily["AOV"])
        ]

        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        fig_dual.add_trace(
            go.Bar(
                x=daily["Date_Label"], y=daily["Orders"], name="Unique Orders",
                marker=dict(color="#6366F1", cornerradius=6), opacity=0.85,
                text=daily["Orders"], textposition="outside", cliponaxis=False,
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
                customdata=daily["Custom_Hover"],
                hovertemplate="Revenue: %{customdata}<extra></extra>"
            ),
            secondary_y=True
        )
        max_ord_y = max(float(daily["Orders"].max()) * 1.28, 5.0) if not daily.empty else 10.0
        max_rev_y = max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5) if not daily.empty else 1.0
        fig_dual.update_layout(
            height=410, margin=dict(l=15, r=15, t=40, b=60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified", bargap=0.28,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=12)),
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        fig_dual.update_xaxes(tickangle=-45, tickfont=dict(size=11, color="#475569"), nticks=18, showgrid=False)
        fig_dual.update_yaxes(title_text="Unique Orders", range=[0, max_ord_y], showgrid=True, gridcolor="#F1F5F9", zeroline=False, secondary_y=False)
        fig_dual.update_yaxes(title_text="Revenue (₹ Lakhs)", range=[0, max_rev_y], showgrid=False, zeroline=False, secondary_y=True)
        st.plotly_chart(fig_dual, use_container_width=True)
        st.markdown('<div style="font-size:13px; font-weight:700; color:#334155; margin-top:10px; margin-bottom:6px;">📋 Day-Wise Orders & Exact Revenue Verification</div>', unsafe_allow_html=True)
        d_verify = p_orders_uniq.groupby("Order_Date_Only").agg(
            Unique_Orders=(base_oid_col, "nunique"),
            Revenue_INR=("Order_Total", "sum"),
            Discount_INR=("Discount", "sum") if "Discount" in p_orders_uniq.columns else ("Order_Total", lambda s: 0.0),
            Shipping_INR=("Shipping", "sum") if "Shipping" in p_orders_uniq.columns else ("Order_Total", lambda s: 0.0),
        ).reset_index().sort_values("Order_Date_Only")
        d_verify["Date"] = pd.to_datetime(d_verify["Order_Date_Only"]).dt.strftime("%d %b %Y")
        d_verify["AOV_INR"] = np.where(d_verify["Unique_Orders"] > 0, (d_verify["Revenue_INR"] / d_verify["Unique_Orders"]).round(0), 0)
        d_verify["Revenue_INR"] = d_verify["Revenue_INR"].round(2)
        d_verify["Discount_INR"] = d_verify["Discount_INR"].round(2)
        d_verify["Shipping_INR"] = d_verify["Shipping_INR"].round(2)
        st.dataframe(
            d_verify[["Date", "Unique_Orders", "Revenue_INR", "AOV_INR", "Discount_INR", "Shipping_INR"]],
            use_container_width=True,
            height=210,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card-box"><div class="card-title">🎯 Order-to-Delivery Funnel (Unique Orders)</div>', unsafe_allow_html=True)
        funnel_labels = ["Orders Created", "Dispatched", "True Delivered", "Pure RTO Orders", "Exch Cancelled", "RTO Pending Hub", "In-Transit", "Not Dispatched"]
        funnel_vals = [tot_ord, disp_cnt, deliv_cnt, pure_rto_cnt, canc_exch_cnt, rto_hub_orders, len(int_oids), len(not_dispatched)]
        funnel_colors = ["#4F46E5", "#0EA5E9", "#10B981", "#EF4444", "#E11D48", "#EA580C", "#F59E0B", "#94A3B8"]

        fig_fun = go.Figure(go.Bar(
            y=funnel_labels[::-1], x=funnel_vals[::-1], orientation="h",
            marker=dict(color=funnel_colors[::-1], cornerradius=8),
            text=[f"<b>{v:,}</b>" for v in funnel_vals[::-1]], textposition="outside", cliponaxis=False,
            textfont=dict(size=12, color="#0F172A")
        ))
        fig_fun.update_layout(
            height=410, margin=dict(l=10, r=60, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, range=[0, max(funnel_vals + [1]) * 1.22]),
            yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        st.plotly_chart(fig_fun, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="sub-kpi">
            <div><div class="sub-kpi-lbl">Total Returns Display</div><div class="sub-kpi-val">{tot_ret_cnt:,} ({tot_ret_pct:.2f}%)</div></div>
            <div class="sub-kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="sub-kpi">
            <div><div class="sub-kpi-lbl">Total Return Amount</div><div class="sub-kpi-val">₹{tot_ret_amt:,.2f}</div></div>
            <div class="sub-kpi-ico" style="background:#FFF1F2;">💸</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="sub-kpi">
            <div><div class="sub-kpi-lbl">Pure RTO Orders</div><div class="sub-kpi-val">{pure_rto_cnt:,}</div></div>
            <div class="sub-kpi-ico" style="background:#FFEDD5;">🚚</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="sub-kpi">
            <div><div class="sub-kpi-lbl">Exchanged Cancelled</div><div class="sub-kpi-val">{canc_exch_cnt:,}</div></div>
            <div class="sub-kpi-ico" style="background:#FCE7F3;">❌</div>
        </div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="sub-kpi">
            <div><div class="sub-kpi-lbl">Active Exchange Orders</div><div class="sub-kpi-val">{exch_cnt:,}</div></div>
            <div class="sub-kpi-ico" style="background:#F3E8FF;">🔄</div>
        </div>""", unsafe_allow_html=True)

    # ================= SECTION 1: RTO ANALYSIS =================
    st.markdown(f"""
    <div class="sec-header-rto">
        <div class="sec-title">🚚 Section 1: Pure RTO Analysis (Pure RTO: {pure_rto_cnt:,} | Cancelled Exchanges: {canc_exch_cnt:,} | Total Returns: {tot_ret_cnt:,})</div>
        <div class="sec-sub">RTO Status Donut, Region & State-wise RTO Returns & Day-Wise RTO Orders Trend</div>
    </div>
    """, unsafe_allow_html=True)

    rto_df = p_disp[p_disp["Is_RTO"]].copy() if (not p_disp.empty and "Is_RTO" in p_disp.columns) else pd.DataFrame()

    rto_c1, rto_c2, rto_c3 = st.columns([1.05, 1.1, 1.35])
    with rto_c1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 RTO Status Breakdown (Donut)</div>', unsafe_allow_html=True)
        if not rto_df.empty and disp_base_col:
            st_col_rto = _find_col(rto_df, ["Shipment_Status", "Status"])
            if st_col_rto:
                rto_st_agg = rto_df.groupby(rto_df[st_col_rto].fillna("RTO").astype(str).str.strip())[disp_base_col].nunique().reset_index(name="Count")
                rto_st_agg.columns = ["Status", "Count"]
            else:
                rto_st_agg = pd.DataFrame({"Status": ["RTO Pending Hub", "RTO Received Hub"], "Count": [rto_hub_orders, max(pure_rto_cnt - rto_hub_orders, 0)]})
            rto_st_agg = rto_st_agg[rto_st_agg["Count"] > 0]
            fig_rto_donut = _make_donut_fig(
                rto_st_agg["Status"].tolist(),
                rto_st_agg["Count"].tolist(),
                ["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6", "#10B981"],
                f"<b>{pure_rto_cnt:,}</b><br>Pure RTO"
            )
            st.plotly_chart(fig_rto_donut, use_container_width=True)
        else:
            st.info("निवडलेल्या कालावधीत RTO ऑर्डर्स नाहीत.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rto_c2:
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Region & State-wise RTO Returns</div>', unsafe_allow_html=True)
        if not rto_df.empty and disp_base_col:
            r_col_d = _find_col(rto_df, ["Customer_Region", "Region"])
            s_col_d = _find_col(rto_df, ["Shipping_State", "State"])
            if r_col_d and s_col_d:
                rto_df["Region_State_Lbl"] = (
                    rto_df[r_col_d].fillna("Unknown").astype(str).str.strip()
                    + " — "
                    + rto_df[s_col_d].fillna("Unknown").astype(str).str.strip()
                )
                geo_rto = rto_df.groupby("Region_State_Lbl")[disp_base_col].nunique().reset_index(name="RTO_Orders").sort_values("RTO_Orders", ascending=True).tail(8)
                y_lbl_col = "Region_State_Lbl"
            else:
                fallback_col = r_col_d or s_col_d or _find_col(rto_df, ["Shipping_City", "City"])
                geo_rto = rto_df.groupby(rto_df[fallback_col].fillna("Unknown").astype(str).str.strip())[disp_base_col].nunique().reset_index(name="RTO_Orders").sort_values("RTO_Orders", ascending=True).tail(8)
                y_lbl_col = fallback_col

            fig_geo_rto = go.Figure(go.Bar(
                y=geo_rto[y_lbl_col], x=geo_rto["RTO_Orders"], orientation="h",
                marker=dict(color="#0284C7", cornerradius=8),
                text=geo_rto["RTO_Orders"], textposition="outside", cliponaxis=False
            ))
            fig_geo_rto.update_layout(
                height=370, margin=dict(l=10, r=45, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(geo_rto["RTO_Orders"].max()) * 1.28, 3.0)])
            )
            st.plotly_chart(fig_geo_rto, use_container_width=True)
        else:
            st.info("No RTO region/state data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rto_c3:
        st.markdown('<div class="card-box"><div class="card-title">📅 Day-Wise RTO Orders Analysis</div>', unsafe_allow_html=True)
        if not rto_df.empty and "Order_Date_dt" in rto_df.columns and disp_base_col:
            d_rto = rto_df.groupby(rto_df["Order_Date_dt"].dt.date)[disp_base_col].nunique().reset_index(name="RTO_Count").sort_values("Order_Date_dt")
            d_rto["Date_Lbl"] = pd.to_datetime(d_rto["Order_Date_dt"]).dt.strftime("%d %b")
            fig_d_rto = go.Figure()
            fig_d_rto.add_trace(go.Bar(
                x=d_rto["Date_Lbl"], y=d_rto["RTO_Count"], name="Day-Wise RTO",
                marker=dict(color="#FB923C", cornerradius=6),
                text=d_rto["RTO_Count"], textposition="outside", cliponaxis=False
            ))
            fig_d_rto.add_trace(go.Scatter(
                x=d_rto["Date_Lbl"], y=d_rto["RTO_Count"], name="Trend",
                mode="lines+markers", line=dict(color="#EA580C", width=2.5, shape="spline")
            ))
            fig_d_rto.update_layout(
                height=370, margin=dict(l=15, r=15, t=25, b=55), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(tickangle=-45, nticks=18, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(d_rto["RTO_Count"].max()) * 1.32, 3.0)])
            )
            st.plotly_chart(fig_d_rto, use_container_width=True)
        else:
            st.info("No day-wise RTO data.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ================= SECTION 2: EXCHANGE ANALYSIS (Reverse_Status) =================
    st.markdown(f"""
    <div class="sec-header-exch">
        <div class="sec-title">🔄 Section 2: Exchange Analysis (Active Exchanges: {exch_cnt:,} | Exchanged Cancelled: {canc_exch_cnt:,})</div>
        <div class="sec-sub">Exchanged Status by <code>Reverse_Status</code>, Day-Wise Exchange Orders & Reverse Logistics Table</div>
    </div>
    """, unsafe_allow_html=True)

    ex_c1, ex_c2 = st.columns([1.05, 1.45])
    with ex_c1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 Exchange Status by <code>Reverse_Status</code> (Donut)</div>', unsafe_allow_html=True)
        if not p_rev_all.empty:
            id_for_cnt = rev_order_id_col if rev_order_id_col else rev_base_col
            if rev_status_col and id_for_cnt:
                ex_st_df = p_rev_all.groupby(p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip())[id_for_cnt].nunique().reset_index(name="Count")
                ex_st_df.columns = ["Reverse_Status", "Count"]
            elif rev_status_col:
                ex_st_df = p_rev_all.groupby(p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip()).size().reset_index(name="Count")
                ex_st_df.columns = ["Reverse_Status", "Count"]
            else:
                ex_st_df = pd.DataFrame({"Reverse_Status": ["Recorded"], "Count": [len(p_rev_all)]})
            ex_st_df = ex_st_df[ex_st_df["Count"] > 0]

            fig_ex_donut = _make_donut_fig(
                ex_st_df["Reverse_Status"].tolist(),
                ex_st_df["Count"].tolist(),
                ["#10B981", "#8B5CF6", "#F59E0B", "#0EA5E9", "#EF4444", "#EC4899"],
                f"<b>{int(ex_st_df['Count'].sum()):,}</b><br>Total Exch"
            )
            st.plotly_chart(fig_ex_donut, use_container_width=True)
        else:
            st.info("निवडलेल्या कालावधीत `Fact_Reverse_Logistics` मध्ये Exchange रेकॉर्ड्स नाहीत.")
        st.markdown('</div>', unsafe_allow_html=True)

    with ex_c2:
        st.markdown('<div class="card-box"><div class="card-title">📅 Day-Wise Exchange Orders Analysis (Non-Cancelled)</div>', unsafe_allow_html=True)
        if not p_rev_active.empty and rev_base_col:
            rev_d = p_rev_active.merge(p_orders_uniq[[base_oid_col, "Order_Date_dt"]], left_on=rev_base_col, right_on=base_oid_col, how="left")
            id_for_day = rev_order_id_col if (rev_order_id_col and rev_order_id_col in rev_d.columns) else rev_base_col
            if "Order_Date_dt" in rev_d.columns and rev_d["Order_Date_dt"].notna().any():
                d_ex = rev_d.groupby(rev_d["Order_Date_dt"].dt.date)[id_for_day].nunique().reset_index(name="Exchange_Count").sort_values("Order_Date_dt")
                d_ex["Date_Lbl"] = pd.to_datetime(d_ex["Order_Date_dt"]).dt.strftime("%d %b")
                fig_d_ex = go.Figure()
                fig_d_ex.add_trace(go.Bar(
                    x=d_ex["Date_Lbl"], y=d_ex["Exchange_Count"], name="Day-Wise Exchanges",
                    marker=dict(color="#A855F7", cornerradius=6),
                    text=d_ex["Exchange_Count"], textposition="outside", cliponaxis=False
                ))
                fig_d_ex.add_trace(go.Scatter(
                    x=d_ex["Date_Lbl"], y=d_ex["Exchange_Count"], name="Trend",
                    mode="lines+markers", line=dict(color="#7C3AED", width=2.5, shape="spline")
                ))
                fig_d_ex.update_layout(
                    height=370, margin=dict(l=15, r=15, t=25, b=55), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis=dict(tickangle=-45, nticks=18, showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(d_ex["Exchange_Count"].max()) * 1.32, 3.0)])
                )
                st.plotly_chart(fig_d_ex, use_container_width=True)
            else:
                st.info("No dated exchange records in selected period.")
        else:
            st.info("No day-wise exchange data in selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"#### 🔄 Exchanges Detail (<code>Fact_Reverse_Logistics</code> — Active: {exch_cnt:,} | Cancelled: {canc_exch_cnt:,})")
    if not p_rev_all.empty:
        st.dataframe(p_rev_all, use_container_width=True, height=250, hide_index=True)
        st.download_button(
            "⬇️ Download Exchanges CSV",
            p_rev_all.to_csv(index=False).encode("utf-8"),
            f"exchanges_{start_date}_{end_date}.csv",
            "text/csv"
        )
    else:
        st.info("No Exchange records found for the selected created orders window.")

with tab3:
    p1, p2 = st.columns([1.2, 1])
    with p1:
        st.markdown('<div class="card-box"><div class="card-title">🏆 Top 7 Bestselling Delivered Products</div>', unsafe_allow_html=True)
        prod_col = _find_col(p_disp, ["Clean_Product_Name", "Product_Name", "Title"]) if not p_disp.empty else None
        if not p_disp.empty and prod_col:
            prod_s = p_disp[p_disp["True_Delivered"]][prod_col].dropna().astype(str).str.strip()
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
        age_col = _find_col(p_disp, ["Product_Age_Group", "Age_Group", "Size"]) if not p_disp.empty else None
        if not p_disp.empty and age_col:
            age_s = p_disp[p_disp["True_Delivered"]][age_col].dropna().astype(str).str.strip()
            age_s = age_s[~age_s.str.lower().isin(["", "nan", "none", "standard / free size"])]
            top_a = age_s.value_counts().head(7).reset_index()
            top_a.columns = ["Age Group", "Count"]
            if not top_a.empty:
                fig_age = go.Figure(go.Bar(
                    x=top_a["Age Group"], y=top_a["Count"],
                    marker=dict(color="#8B5CF6", cornerradius=8),
                    text=top_a["Count"], textposition="outside", cliponaxis=False
                ))
                fig_age.update_layout(height=310, margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(top_a["Count"].max()) * 1.25, 3.0)]))
                st.plotly_chart(fig_age, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    g1, g2 = st.columns([1, 1.3])
    with g1:
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Unique Orders by Region & State</div>', unsafe_allow_html=True)
        if reg_col and state_col_ord and base_oid_col:
            p_orders["Reg_St"] = p_orders[reg_col].fillna("Unknown").astype(str).str.strip() + " — " + p_orders[state_col_ord].fillna("Unknown").astype(str).str.strip()
            reg_agg = p_orders.groupby("Reg_St")[base_oid_col].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False).head(7)
            fig_reg = _make_donut_fig(
                reg_agg["Reg_St"].tolist(), reg_agg["Orders"].tolist(),
                ["#4F46E5", "#EC4899", "#10B981", "#F59E0B", "#0EA5E9", "#8B5CF6", "#F97316"],
                f"<b>{int(reg_agg['Orders'].sum()):,}</b><br>Orders"
            )
            st.plotly_chart(fig_reg, use_container_width=True)
        elif reg_col and base_oid_col:
            reg_agg = p_orders.groupby(reg_col)[base_oid_col].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False)
            fig_reg = _make_donut_fig(
                reg_agg[reg_col].tolist(), reg_agg["Orders"].tolist(),
                ["#4F46E5", "#EC4899", "#10B981", "#F59E0B", "#0EA5E9", "#8B5CF6"],
                f"<b>{int(reg_agg['Orders'].sum()):,}</b><br>Orders"
            )
            st.plotly_chart(fig_reg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="card-box"><div class="card-title">🏙️ Top 8 Cities by Unique Orders</div>', unsafe_allow_html=True)
        city_col = _find_col(p_orders, ["Shipping_City", "City"])
        if city_col and base_oid_col:
            city_agg = p_orders.groupby(city_col)[base_oid_col].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False).head(8)
            fig_city = go.Figure(go.Bar(
                y=city_agg[city_col][::-1], x=city_agg["Orders"][::-1], orientation="h",
                marker=dict(color="#0EA5E9", cornerradius=8), text=city_agg["Orders"][::-1], textposition="outside", cliponaxis=False
            ))
            fig_city.update_layout(height=370, margin=dict(l=10, r=45, t=15, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(city_agg["Orders"].max()) * 1.25, 3.0)]))
            st.plotly_chart(fig_city, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown(f"#### 🏭 RTO Pending to Hub ({rto_hub_parcels} Parcels / {rto_hub_orders} Unique Orders)")
    hub_cols = [c for c in ["Order_ID", "Base_Order_ID", "Order_Date", "Dispatch_Date", "Carrier", "Tracking_Number", "Shipment_Status", "Order_Total", "Order_Notes"] if c in rto_pending_hub_df.columns]
    hub_view = rto_pending_hub_df[hub_cols] if not rto_pending_hub_df.empty else pd.DataFrame(columns=hub_cols)
    st.dataframe(hub_view, use_container_width=True, height=280, hide_index=True)
    st.download_button("⬇️ Download RTO Pending Hub CSV", hub_view.to_csv(index=False).encode("utf-8"), "rto_pending_hub.csv", "text/csv")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(f"#### 🚚 Truly In-Transit Parcels ({int(p_disp['True_In_Transit'].sum()) if (not p_disp.empty and 'True_In_Transit' in p_disp.columns) else 0})")
        it_cols = [c for c in ["Order_ID", "Base_Order_ID", "Order_Date", "Dispatch_Date", "Carrier", "Shipment_Status", "Order_Total", "Order_Notes"] if c in p_disp.columns]
        it_view = p_disp[p_disp["True_In_Transit"]][it_cols] if (not p_disp.empty and "True_In_Transit" in p_disp.columns) else pd.DataFrame(columns=it_cols)
        st.dataframe(it_view, use_container_width=True, height=340, hide_index=True)
        st.download_button("⬇️ Download In-Transit CSV", it_view.to_csv(index=False).encode("utf-8"), "in_transit.csv", "text/csv")

    with t_col2:
        st.markdown(f"#### ⏳ Not Dispatched Orders ({len(not_dispatched)})")
        nd_cols = [c for c in [base_oid_col, "Order_Date", "Financial_Status", "Fulfillment_Status", "Order_Total", "Order_Notes"] if c and c in not_dispatched.columns]
        nd_view = not_dispatched[nd_cols] if not not_dispatched.empty else pd.DataFrame(columns=nd_cols)
        st.dataframe(nd_view, use_container_width=True, height=340, hide_index=True)
        st.download_button("⬇️ Download Not-Dispatched CSV", nd_view.to_csv(index=False).encode("utf-8"), "not_dispatched.csv", "text/csv")
