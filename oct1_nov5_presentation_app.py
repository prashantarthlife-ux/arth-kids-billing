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

def _safe_dataframe(df: pd.DataFrame, **kwargs):
    if df is None or df.empty:
        st.dataframe(pd.DataFrame(), **kwargs)
        return
    clean_df = df.copy()
    for col in clean_df.columns:
        s = clean_df[col]
        if pd.api.types.is_numeric_dtype(s):
            num_s = pd.to_numeric(s, errors="coerce").replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
            if (num_s.abs() > 9e15).any():
                clean_df[col] = num_s.apply(lambda v: f"{int(round(v))}" if float(v).is_integer() else f"{v:.2f}")
            else:
                clean_df[col] = num_s
        elif pd.api.types.is_datetime64_any_dtype(s):
            clean_df[col] = s.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
        else:
            clean_df[col] = s.apply(lambda v: "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v))
    st.dataframe(clean_df, **kwargs)

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
            Revenue_
