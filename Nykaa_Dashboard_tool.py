import os
import glob
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
    page_title="ARTH LIFE Kids Fashion — Nykaa Analysis",
    page_icon="💄",
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
    background: linear-gradient(135deg, #DB2777 0%, #7C3AED 100%);
    color: #FFFFFF;
    font-size: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 22px rgba(219, 39, 119, 0.25);
}
.login-title { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0; }
.login-sub   { font-size: 13px; color: #64748B; margin-top: 5px; margin-bottom: 12px; }

.exec-banner {
    background: linear-gradient(135deg, #0F172A 0%, #9D174D 55%, #7C3AED 100%);
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
.exec-sub   { font-size: 13.5px; opacity: 0.88; margin-top: 5px; }
.exec-pill  {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.30);
    padding: 9px 18px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
    white-space: nowrap;
}

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
    background: linear-gradient(90deg, #FDF2F8 0%, #FFFFFF 100%);
    border-left: 5px solid #DB2777;
    border-radius: 14px;
    padding: 14px 20px;
    margin-top: 22px;
    margin-bottom: 14px;
    border-top: 1px solid #FCE7F3;
    border-right: 1px solid #FCE7F3;
    border-bottom: 1px solid #FCE7F3;
}
.sec-title { font-size: 18px; font-weight: 800; color: #0F172A; margin: 0; }
.sec-sub   { font-size: 12.5px; color: #64748B; margin-top: 2px; }

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

.card-box {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    border: 1px solid #E6EAF2;
    margin-bottom: 18px;
}
.card-title { font-size: 15.5px; font-weight: 700; color: #0F172A; margin-bottom: 12px; }

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
    if LOGO_URI else '<div class="login-badge">💄</div>'
)
LOGO_BANNER_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    f'style="width:58px;height:58px;min-width:58px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.45);box-shadow:0 6px 16px rgba(0,0,0,0.22);" />'
    if LOGO_URI else ''
)

# ==============================================================================
# 3. SECURE LOGIN GATE
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
        <div class="login-sub">Nykaa Seller Analytics Portal — Please Sign In</div>
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
# 4. NYKAA DATA DISCOVERY & PREPROCESSING
# ==============================================================================
NYKAA_DEFAULT_NAME = "OrderExport (16).xls"

def _find_nykaa_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        script_dir,
        os.path.join(script_dir, "data"),
        os.path.join(script_dir, "nykaa"),
        os.getcwd(),
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.getcwd(), "nykaa"),
    ]
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            exact = os.path.abspath(os.path.join(folder, NYKAA_DEFAULT_NAME))
            if os.path.isfile(exact):
                return exact
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            for pat in ["*OrderExport*.xls*", "*nykaa*.xls*", "*nykaa*.csv", "*.xls*"]:
                matches = sorted(glob.glob(os.path.join(folder, pat)))
                if matches:
                    return os.path.abspath(matches[0])
    return None

def _to_num(s: pd.Series) -> pd.Series:
    cleaned = s.astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)

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
def load_nykaa_data(file_src):
    if isinstance(file_src, str):
        low = file_src.lower()
        if low.endswith(".csv"):
            df = pd.read_csv(file_src, low_memory=False)
        else:
            xls = pd.ExcelFile(file_src)
            sheet = "Export" if "Export" in xls.sheet_names else xls.sheet_names[0]
            df = pd.read_excel(xls, sheet_name=sheet)
    else:
        low = file_src.name.lower()
        if low.endswith(".csv"):
            df = pd.read_csv(file_src, low_memory=False)
        else:
            xls = pd.ExcelFile(file_src)
            sheet = "Export" if "Export" in xls.sheet_names else xls.sheet_names[0]
            df = pd.read_excel(xls, sheet_name=sheet)

    df = df.drop_duplicates().copy()

    df["Order_Date_dt"] = pd.to_datetime(df.get("Order Date", pd.Series(dtype=str)), format="mixed", errors="coerce")
    if hasattr(df["Order_Date_dt"].dt, "tz") and df["Order_Date_dt"].dt.tz is not None:
        df["Order_Date_dt"] = df["Order_Date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["Order_Create_Date"] = df["Order_Date_dt"].dt.date

    df["Ship_By_dt"] = pd.to_datetime(df.get("Ship by Date", pd.Series(dtype=str)), format="mixed", errors="coerce")
    if hasattr(df["Ship_By_dt"].dt, "tz") and df["Ship_By_dt"].dt.tz is not None:
        df["Ship_By_dt"] = df["Ship_By_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)

    for c in ["Qty", "Unit Price", "Line Amount"]:
        df[c] = _to_num(df[c]) if c in df.columns else 0.0

    df["Order_Key"] = df.get("Web Order No", pd.Series(df.index.astype(str))).fillna("").astype(str).str.strip()
    df["Status_Clean"] = df.get("Status", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip()
    df["Status_Lower"] = df["Status_Clean"].str.lower()

    df["Order_Type_Clean"] = df.get("Order Type", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip()
    df["SKU_Code_Clean"] = df.get("SKU Code", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip()
    df["SKU_Name_Clean"] = df.get("SKU Name", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip()
    df["Customer_Clean"] = df.get("Customer Name", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip()

    return df

# Sidebar
with st.sidebar:
    if LOGO_URI:
        sb_c1, sb_c2 = st.columns([1, 3.2])
        with sb_c1:
            st.image(LOGO_URI, width=44)
        with sb_c2:
            st.markdown("### ARTH LIFE")
    else:
        st.markdown("### 💄 ARTH LIFE Nykaa")
    st.caption("Nykaa Kids Fashion Analytics")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    st.divider()

    repo_file = _find_nykaa_file()
    if repo_file:
        st.success(f"✅ Repo Nykaa file loaded: `{os.path.basename(repo_file)}`")

    with st.expander("📤 Upload Nykaa Export File"):
        uploaded_file = st.file_uploader("Upload OrderExport (.xls / .xlsx / .csv)", type=["xls", "xlsx", "csv"])

    source = uploaded_file if uploaded_file is not None else repo_file

    if source is None:
        st.warning("कृपया GitHub रिपॉझिटरीमध्ये `OrderExport (16).xls` ठेवा किंवा वरून अपलोड करा.")
        st.stop()

    df_all = load_nykaa_data(source)

    valid_dates = df_all["Order_Date_dt"].dropna()
    if valid_dates.empty:
        st.error("'Order Date' मध्ये वैध तारखा सापडल्या नाहीत.")
        st.stop()

    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()

    st.markdown("#### 📅 Quick Date Preset")
    preset = st.selectbox(
        "Select Preset",
        ["All Available Dates", "01 Jul – 31 Oct 2026", "01 Oct – 27 Oct 2026", "Custom Dates"],
        index=0
    )

    if preset == "01 Jul – 31 Oct 2026":
        init_start = min(max(datetime.date(2026, 7, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 10, 31), max_d), min_d)
    elif preset == "01 Oct – 27 Oct 2026":
        init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 10, 27), max_d), min_d)
    else:
        init_start, init_end = min_d, max_d

    all_otypes = sorted(df_all["Order_Type_Clean"].unique().tolist())
    sel_otypes = st.multiselect("💳 Filter Order Type (COD / Prepaid)", all_otypes, default=all_otypes)

    all_statuses = sorted(df_all["Status_Clean"].unique().tolist())
    sel_statuses = st.multiselect("📦 Filter Status", all_statuses, default=all_statuses)

# ==============================================================================
# 5. TOP BANNER & UNIFIED DATE SELECTION BAR
# ==============================================================================
ds_col1, ds_col2, ds_col3 = st.columns([1, 1, 2.2])
with ds_col1:
    start_date = st.date_input("📅 Start Date", value=init_start, min_value=min_d, max_value=max_d, key="nykaa_start_date")
with ds_col2:
    end_date = st.date_input("📅 End Date", value=init_end, min_value=min_d, max_value=max_d, key="nykaa_end_date")
with ds_col3:
    st.markdown(
        f"<div style='padding-top:28px; font-size:13px; color:#475569;'>"
        f"<b>Orders Window (Order Date):</b> {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')} "
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
            <div class="exec-title">ARTH LIFE Kids Fashion — Nykaa Analysis</div>
            <div class="exec-sub">Unique Web Orders, Line Amount Revenue, Delivered, RTO Delivered, Customer Returns & Cancelled</div>
        </div>
    </div>
    <div class="exec-pill">📅 Orders: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. FILTER BY SELECTED ORDER DATE, ORDER TYPE & STATUS (SINGLE PASS)
# ==============================================================================
p_df = df_all[
    (df_all["Order_Date_dt"].dt.date >= start_date) &
    (df_all["Order_Date_dt"].dt.date <= end_date) &
    (df_all["Order_Type_Clean"].isin(sel_otypes)) &
    (df_all["Status_Clean"].isin(sel_statuses))
].copy()

if p_df.empty:
    st.info(f"निवडलेल्या तारीख रेंजमध्ये ({start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}) कोणतेही Nykaa ऑर्डर्स सापडले नाहीत.")
    st.stop()

# ==============================================================================
# 7. KPI CALCULATIONS (UNIQUE WEB ORDER NO & LINE AMOUNT)
# ==============================================================================
tot_ord = int(p_df["Order_Key"].nunique())
tot_rows = len(p_df)
tot_qty = int(p_df["Qty"].sum())

non_canc_df = p_df[p_df["Status_Lower"] != "cancelled"].copy()
canc_df = p_df[p_df["Status_Lower"] == "cancelled"].copy()
deliv_df = p_df[p_df["Status_Lower"] == "delivered"].copy()
shipped_df = p_df[p_df["Status_Lower"] == "shipped"].copy()
rto_df = p_df[p_df["Status_Lower"].str.contains("rto", na=False)].copy()
ret_df = p_df[(~p_df["Status_Lower"].str.contains("rto", na=False)) & (p_df["Status_Lower"].str.contains("return", na=False))].copy()

deliv_cnt = int(deliv_df["Order_Key"].nunique()) if not deliv_df.empty else 0
shipped_cnt = int(shipped_df["Order_Key"].nunique()) if not shipped_df.empty else 0
rto_cnt = int(rto_df["Order_Key"].nunique()) if not rto_df.empty else 0
ret_cnt = int(ret_df["Order_Key"].nunique()) if not ret_df.empty else 0
canc_cnt = int(canc_df["Order_Key"].nunique()) if not canc_df.empty else 0

gross_rev = float(non_canc_df["Line Amount"].sum()) if not non_canc_df.empty else 0.0
rto_amt = float(rto_df["Line Amount"].sum()) if not rto_df.empty else 0.0
ret_amt = float(ret_df["Line Amount"].sum()) if not ret_df.empty else 0.0
canc_amt = float(canc_df["Line Amount"].sum()) if not canc_df.empty else 0.0
net_rev = max(gross_rev - rto_amt - ret_amt, 0.0)

aov = gross_rev / max(int(non_canc_df["Order_Key"].nunique()), 1) if not non_canc_df.empty else 0.0
ret_rto_total_cnt = rto_cnt + ret_cnt
ret_rto_pct = (ret_rto_total_cnt / max(tot_ord, 1) * 100) if tot_ord > 0 else 0.0

# Row 1: 5 Core KPIs
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Unique Orders</div>
            <div class="kpi-val">{tot_ord:,}</div>
            <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_qty:,} Qty ({tot_rows} Rows)</span>
        </div>
        <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Gross Revenue (Excl. Canc)</div>
            <div class="kpi-val">₹{gross_rev:,.2f}</div>
            <span class="kpi-tag" style="background:#FDF2F8; color:#BE185D;">AOV: ₹{aov:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#FDF2F8;">💰</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Net Revenue</div>
            <div class="kpi-val">₹{net_rev:,.2f}</div>
            <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Excl. RTO & Return</span>
        </div>
        <div class="kpi-ico" style="background:#ECFDF5;">📈</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Delivered Orders</div>
            <div class="kpi-val">{deliv_cnt:,}</div>
            <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Shipped: {shipped_cnt:,}</span>
        </div>
        <div class="kpi-ico" style="background:#ECFDF5;">🚚</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">RTO + Customer Return</div>
            <div class="kpi-val">{ret_rto_total_cnt:,} ({ret_rto_pct:.1f}%)</div>
            <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO {rto_cnt:,} | Ret {ret_cnt:,}</span>
        </div>
        <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 8. PRESENTATION TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview & Daily Trend",
    "↩️ RTO, Returns & Cancelled",
    "👗 Top SKUs & Payment Mix",
    "📋 Orders Table & Download"
])

with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
        st.markdown('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Revenue Trend (Excl. Cancelled)</div>', unsafe_allow_html=True)
        nc_u = non_canc_df.copy()
        nc_u["Order_Date_Only"] = nc_u["Order_Date_dt"].dt.date
        daily = nc_u.groupby("Order_Date_Only").agg(
            Orders=("Order_Key", "nunique"),
            Revenue=("Line Amount", "sum")
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
            height=400, margin=dict(l=15, r=15, t=40, b=60),
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
        st.markdown('<div class="card-box"><div class="card-title">🍩 Status Breakdown (Unique Orders)</div>', unsafe_allow_html=True)
        st_tbl = p_df.groupby("Status_Clean").agg(
            Unique_Orders=("Order_Key", "nunique"),
            Qty=("Qty", "sum"),
            Line_Amount_INR=("Line Amount", "sum")
        ).reset_index().sort_values("Unique_Orders", ascending=False)
        st_tbl["Line_Amount_INR"] = st_tbl["Line_Amount_INR"].round(2)

        fig_donut = go.Figure(go.Pie(
            labels=st_tbl["Status_Clean"], values=st_tbl["Unique_Orders"], hole=0.58,
            textinfo="percent", textposition="inside",
            marker=dict(colors=["#10B981", "#F59E0B", "#EF4444", "#94A3B8", "#0EA5E9"], line=dict(color="#FFFFFF", width=2.5)),
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>"
        ))
        fig_donut.update_layout(
            height=400, margin=dict(l=15, r=15, t=20, b=65),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
            annotations=[dict(text=f"<b>{tot_ord:,}</b><br>Orders", x=0.5, y=0.5, font_size=13, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="sec-header-rto">
        <div class="sec-title">↩️ RTO Delivered, Customer Returns & Cancelled Summary</div>
        <div class="sec-sub">Unique Order Counts & Line Amount Impact</div>
    </div>
    """, unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    r1.metric("RTO Delivered Orders", f"{rto_cnt:,}", f"₹{rto_amt:,.2f}")
    r2.metric("Customer Returned Orders", f"{ret_cnt:,}", f"₹{ret_amt:,.2f}")
    r3.metric("Cancelled Orders", f"{canc_cnt:,}", f"₹{canc_amt:,.2f}")

    st.markdown('<div class="card-box"><div class="card-title">📋 Status-Wise Summary Table</div>', unsafe_allow_html=True)
    _safe_dataframe(st_tbl, use_container_width=True, height=240, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    t1, t2 = st.columns([1.3, 1])
    with t1:
        st.markdown('<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by Revenue (Excl. Cancelled)</div>', unsafe_allow_html=True)
        top_sku = non_canc_df.groupby(["SKU_Code_Clean", "SKU_Name_Clean"])["Line Amount"].sum().sort_values(ascending=False).head(7)
        if not top_sku.empty:
            mv = top_sku.max()
            for rank, ((skuc, skun), amt) in enumerate(top_sku.items(), start=1):
                pct = amt / mv * 100
                short_n = f"{skuc} — {skun[:42]}..." if len(skun) > 42 else f"{skuc} — {skun}"
                st.markdown(f"""<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{short_n}</span><span style="color:#DB2777;">₹{amt:,.0f}</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="card-box"><div class="card-title">💳 Order Type (COD vs Prepaid)</div>', unsafe_allow_html=True)
        ot_tbl = p_df.groupby("Order_Type_Clean").agg(
            Unique_Orders=("Order_Key", "nunique"),
            Line_Amount_INR=("Line Amount", "sum")
        ).reset_index()
        ot_tbl["Line_Amount_INR"] = ot_tbl["Line_Amount_INR"].round(2)
        _safe_dataframe(ot_tbl, use_container_width=True, height=220, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown(f"#### 📋 Filtered Nykaa Orders ({tot_ord:,} Unique Orders / {tot_rows:,} Rows)")
    tbl_cols = [c for c in ["Web Order No", "Order_Create_Date", "Order Date", "Customer Name", "SKU Code", "SKU Name", "Order Type", "Qty", "Unit Price", "Line Amount", "Status", "Ship by Date"] if c in p_df.columns]
    _safe_dataframe(p_df[tbl_cols], use_container_width=True, height=360, hide_index=True)
    st.download_button("⬇️ Download Nykaa Orders CSV", p_df[tbl_cols].to_csv(index=False).encode("utf-8"), f"nykaa_analysis_{start_date}_{end_date}.csv", "text/csv")