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
    page_title="ARTH LIFE Kids Fashion — Myntra Analysis",
    page_icon="🛍️",
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

/* Login Card */
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
    background: linear-gradient(135deg, #BE185D 0%, #7C3AED 100%);
    color: #FFFFFF;
    font-size: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 22px rgba(190, 24, 93, 0.25);
}
.login-title { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0; }
.login-sub   { font-size: 13px; color: #64748B; margin-top: 5px; margin-bottom: 12px; }

/* Executive Banner */
.exec-banner {
    background: linear-gradient(135deg, #0F172A 0%, #831843 55%, #7C3AED 100%);
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

/* KPI Cards */
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
# 2. LOGO LOADER
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
    if LOGO_URI else '<div class="login-badge">🛍️</div>'
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
        <div class="login-sub">Myntra Seller Analytics Portal — Please Sign In</div>
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
# 4. DATA DISCOVERY & PREPROCESSING (Myntra_Consolidated_Orders.xlsx + CSV)
# ==============================================================================
CONSOLIDATED_XLSX_NAME = "Myntra_Consolidated_Orders.xlsx"

def _find_myntra_sources():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        script_dir,
        os.path.join(script_dir, "data"),
        os.path.join(script_dir, "myntra"),
        os.getcwd(),
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.getcwd(), "myntra"),
    ]
    found = []
    seen = set()
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            exact_xlsx = os.path.abspath(os.path.join(folder, CONSOLIDATED_XLSX_NAME))
            if os.path.isfile(exact_xlsx) and exact_xlsx not in seen:
                seen.add(exact_xlsx)
                found.append(exact_xlsx)
    for folder in search_dirs:
        if folder and os.path.isdir(folder):
            for pat in ["*myntra*.xlsx", "part-*.csv", "*myntra*.csv"]:
                for fp in sorted(glob.glob(os.path.join(folder, pat))):
                    afp = os.path.abspath(fp)
                    if afp not in seen:
                        seen.add(afp)
                        found.append(afp)
    return found

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

def _to_num(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)

def _read_single_source(src):
    if isinstance(src, str):
        low = src.lower()
        if low.endswith(".xlsx") or low.endswith(".xls"):
            xls = pd.ExcelFile(src)
            sheet = "Myntra_All_Orders" if "Myntra_All_Orders" in xls.sheet_names else xls.sheet_names[0]
            return pd.read_excel(xls, sheet_name=sheet), os.path.basename(src)
        return pd.read_csv(src, low_memory=False), os.path.basename(src)
    else:
        low = src.name.lower()
        if low.endswith(".xlsx") or low.endswith(".xls"):
            xls = pd.ExcelFile(src)
            sheet = "Myntra_All_Orders" if "Myntra_All_Orders" in xls.sheet_names else xls.sheet_names[0]
            return pd.read_excel(xls, sheet_name=sheet), src.name
        return pd.read_csv(src, low_memory=False), src.name

def _build_combined_status(s_val, r_val):
    sl = str(s_val or "").strip().lower()
    rl = str(r_val or "").strip().lower()
    s_clean = str(s_val or "").strip()
    r_clean = str(r_val or "").strip()
    if sl == "delivered" and r_clean == "":
        return "Delivered (No Return)"
    if rl == "return_refund":
        return f"Customer Return ({s_clean or 'Unknown'})"
    if rl == "release_rto_refund":
        return f"RTO ({s_clean or 'Unknown'})"
    if rl == "exchange":
        return f"Exchange ({s_clean or 'Unknown'})"
    if r_clean != "":
        return f"{s_clean or 'Unknown'} | {r_clean}"
    return s_clean or "Unknown"

@st.cache_data(show_spinner=False)
def load_myntra_data(file_paths, uploaded_files):
    frames = []
    loaded_names = []

    if file_paths:
        for fp in file_paths:
            try:
                tmp, nm = _read_single_source(fp)
                tmp["_source_file"] = nm
                frames.append(tmp)
                loaded_names.append(nm)
            except Exception:
                continue

    if uploaded_files:
        for uf in uploaded_files:
            try:
                tmp, nm = _read_single_source(uf)
                tmp["_source_file"] = nm
                frames.append(tmp)
                loaded_names.append(nm)
            except Exception:
                continue

    if not frames:
        return pd.DataFrame(), []

    df = pd.concat(frames, ignore_index=True).drop_duplicates().copy()

    df["order_date_dt"] = pd.to_datetime(df.get("order_date", pd.Series(dtype=str)), format="mixed", errors="coerce")
    if hasattr(df["order_date_dt"].dt, "tz") and df["order_date_dt"].dt.tz is not None:
        df["order_date_dt"] = df["order_date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["Order_Create_Date"] = df["order_date_dt"].dt.date

    df["packing_date_dt"] = pd.to_datetime(df.get("packing_date", pd.Series(dtype=str)), format="mixed", errors="coerce")
    if hasattr(df["packing_date_dt"].dt, "tz") and df["packing_date_dt"].dt.tz is not None:
        df["packing_date_dt"] = df["packing_date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)

    for c in ["seller_paid_amount", "Total_Customer_Paid", "mrp", "discount_amount", "delivery_charges"]:
        df[c] = _to_num(df[c]) if c in df.columns else 0.0

    if "order_number" in df.columns and df["order_number"].notna().any():
        df["Unique_Order_Key"] = df["order_number"].astype(str).str.strip()
    elif "sale_order_code" in df.columns and df["sale_order_code"].notna().any():
        df["Unique_Order_Key"] = df["sale_order_code"].astype(str).str.strip()
    else:
        df["Unique_Order_Key"] = df.index.astype(str)

    raw_ois = df.get("order_item_status", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
    raw_rt = df.get("return_type", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
    rst_u = df.get("return_status", pd.Series(["UNKNOWN"] * len(df))).fillna("UNKNOWN").astype(str).str.strip().str.upper().replace("", "UNKNOWN")

    df["Status_Clean"] = raw_ois.str.lower()
    df["Return_Type_Clean"] = raw_rt.str.lower()
    df["Reverse_Status_Clean"] = rst_u
    df["Combined_Status"] = [_build_combined_status(a, b) for a, b in zip(raw_ois, raw_rt)]

    df["State_Clean"] = df.get("customer_state", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    df["Article_Clean"] = df.get("article_type", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    df["SKU_Clean"] = df.get("product_sku_code", pd.Series(["Unknown"] * len(df))).fillna("Unknown").astype(str).str.strip().replace("", "Unknown")

    return df, sorted(list(dict.fromkeys(loaded_names)))

with st.sidebar:
    if LOGO_URI:
        sb_c1, sb_c2 = st.columns([1, 3.2])
        with sb_c1:
            st.image(LOGO_URI, width=44)
        with sb_c2:
            st.markdown("### ARTH LIFE")
    else:
        st.markdown("### 🛍️ ARTH LIFE Myntra")
    st.caption("Myntra Kids Fashion Analytics")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    st.divider()

    repo_sources = _find_myntra_sources()
    if repo_sources:
        st.success(f"✅ Loaded {len(repo_sources)} Myntra source(s) from repo")

    with st.expander("📤 Upload Myntra_Consolidated_Orders.xlsx / CSV"):
        uploaded_files = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"], accept_multiple_files=True)

    df_all, loaded_file_names = load_myntra_data(repo_sources, uploaded_files)

    if df_all.empty:
        st.warning("कृपया GitHub रिपॉझिटरीमध्ये `Myntra_Consolidated_Orders.xlsx` ठेवा किंवा वरून अपलोड करा.")
        st.stop()

    valid_dates = df_all["order_date_dt"].dropna()
    if valid_dates.empty:
        st.error("'order_date' मध्ये वैध तारखा सापडल्या नाहीत.")
        st.stop()

    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()

    st.markdown("#### 📅 Quick Date Preset")
    preset = st.selectbox(
        "Select Preset",
        ["All Available Dates", "01 Oct – 31 Oct 2026", "01 Oct – 05 Nov 2026", "Custom Dates"],
        index=0
    )

    if preset == "01 Oct – 31 Oct 2026":
        init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 10, 31), max_d), min_d)
    elif preset == "01 Oct – 05 Nov 2026":
        init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        init_end = max(min(datetime.date(2026, 11, 5), max_d), min_d)
    else:
        init_start, init_end = min_d, max_d

    all_states = sorted(df_all["State_Clean"].unique().tolist())
    sel_states = st.multiselect("🗺️ Filter Customer State", all_states, default=all_states)

    all_comb_statuses = sorted(df_all["Combined_Status"].unique().tolist())
    sel_comb_statuses = st.multiselect("🔀 Combined Status (order_item_status + return_type)", all_comb_statuses, default=all_comb_statuses)

ds_col1, ds_col2, ds_col3 = st.columns([1, 1, 2.2])
with ds_col1:
    start_date = st.date_input("📅 Start Date", value=init_start, min_value=min_d, max_value=max_d, key="myntra_start_date")
with ds_col2:
    end_date = st.date_input("📅 End Date", value=init_end, min_value=min_d, max_value=max_d, key="myntra_end_date")
with ds_col3:
    st.markdown(
        f"<div style='padding-top:28px; font-size:13px; color:#475569;'>"
        f"<b>Orders Created Window (order_date):</b> {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')} "
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
            <div class="exec-title">ARTH LIFE Kids Fashion — Myntra Analysis</div>
            <div class="exec-sub">Total Orders Created, Dispatched, RTO, Customer Returns & Seller Paid Revenue</div>
        </div>
    </div>
    <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)

p_df = df_all[
    (df_all["order_date_dt"].dt.date >= start_date) &
    (df_all["order_date_dt"].dt.date <= end_date) &
    (df_all["State_Clean"].isin(sel_states)) &
    (df_all["Combined_Status"].isin(sel_comb_statuses))
].copy()

if p_df.empty:
    st.info(f"निवडलेल्या तारीख रेंजमध्ये ({start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}) कोणतेही Myntra ऑर्डर्स सापडले नाहीत.")
    st.stop()

tot_ord = int(p_df["Unique_Order_Key"].nunique())
tot_rows = len(p_df)

has_pack = p_df["packing_date_dt"].notna()
has_inv = (p_df["invoice_number"].fillna("").astype(str).str.strip() != "") if "invoice_number" in p_df.columns else pd.Series([False]*len(p_df))
is_disp_mask = has_pack | has_inv | p_df["Status_Clean"].isin(["delivered", "in_transit", "reverse_in_transit", "shipped"])
disp_cnt = int(p_df[is_disp_mask]["Unique_Order_Key"].nunique()) if is_disp_mask.any() else 0

rt_l_series = p_df["Return_Type_Clean"]
st_l_series = p_df["Status_Clean"]

is_rto_mask = rt_l_series.str.contains("rto", na=False) | st_l_series.str.contains("rto", na=False)
is_cust_ret_mask = (~is_rto_mask) & (~rt_l_series.str.contains("exchange", na=False)) & (
    rt_l_series.str.contains("return", na=False) | st_l_series.str.contains("reverse", na=False)
)
is_exch_mask = rt_l_series.str.contains("exchange", na=False)

rto_df = p_df[is_rto_mask].copy()
cust_ret_df = p_df[is_cust_ret_mask].copy()
exch_df = p_df[is_exch_mask].copy()

rto_cnt = int(rto_df["Unique_Order_Key"].nunique()) if not rto_df.empty else 0
cust_ret_cnt = int(cust_ret_df["Unique_Order_Key"].nunique()) if not cust_ret_df.empty else 0
exch_cnt = int(exch_df["Unique_Order_Key"].nunique()) if not exch_df.empty else 0

seller_rev = float(p_df["seller_paid_amount"].sum())
rto_seller_rev = float(rto_df["seller_paid_amount"].sum()) if not rto_df.empty else 0.0
cust_ret_seller_rev = float(cust_ret_df["seller_paid_amount"].sum()) if not cust_ret_df.empty else 0.0
net_seller_rev = max(seller_rev - rto_seller_rev - cust_ret_seller_rev, 0.0)

aov = seller_rev / tot_ord if tot_ord > 0 else 0.0
rto_pct = (rto_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
cust_ret_pct = (cust_ret_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Total Orders Created</div>
            <div class="kpi-val">{tot_ord:,}</div>
            <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_rows:,} Order Items</span>
        </div>
        <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Order Dispatched</div>
            <div class="kpi-val">{disp_cnt:,}</div>
            <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">{disp_cnt/max(tot_ord,1)*100:.1f}% Dispatched</span>
        </div>
        <div class="kpi-ico" style="background:#ECFEFF;">📦</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">RTO Count</div>
            <div class="kpi-val">{rto_cnt:,} ({rto_pct:.1f}%)</div>
            <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">₹{rto_seller_rev:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Customer Return Count</div>
            <div class="kpi-val">{cust_ret_cnt:,} ({cust_ret_pct:.1f}%)</div>
            <span class="kpi-tag" style="background:#FFF1F2; color:#BE123C;">₹{cust_ret_seller_rev:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#FFF1F2;">📥</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-lbl">Revenue (seller_paid_amount)</div>
            <div class="kpi-val">₹{seller_rev:,.2f}</div>
            <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">AOV: ₹{aov:,.0f}</span>
        </div>
        <div class="kpi-ico" style="background:#ECFDF5;">💰</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview & Combined Status",
    "↩️ RTO & Customer Returns",
    "👗 Article Types, SKUs & States",
    "📋 Orders Table & Download"
])

with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
        st.markdown('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Seller Paid Revenue Trend</div>', unsafe_allow_html=True)
        p_df["Order_Date_Only"] = p_df["order_date_dt"].dt.date
        daily = p_df.groupby("Order_Date_Only").agg(
            Orders=("Unique_Order_Key", "nunique"),
            Revenue=("seller_paid_amount", "sum")
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

        st.markdown('<div style="font-size:14px; font-weight:700; color:#0F172A; margin-top:14px; margin-bottom:8px;">🔀 Combined Status (order_item_status + return_type)</div>', unsafe_allow_html=True)
        comb_tbl = p_df.groupby("Combined_Status").agg(
            Unique_Orders=("Unique_Order_Key", "nunique"),
            Item_Rows=("Unique_Order_Key", "count"),
            Seller_Paid_INR=("seller_paid_amount", "sum")
        ).reset_index().sort_values("Unique_Orders", ascending=False)
        comb_tbl["Seller_Paid_INR"] = comb_tbl["Seller_Paid_INR"].round(2)
        _safe_dataframe(comb_tbl, use_container_width=True, height=200, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card-box"><div class="card-title">🎯 Order & Return Funnel (Unique Orders)</div>', unsafe_allow_html=True)
        funnel_labels = ["Orders Created", "Dispatched", "Customer Returns", "RTO Count", "Exchanges"]
        funnel_vals = [tot_ord, disp_cnt, cust_ret_cnt, rto_cnt, exch_cnt]
        funnel_colors = ["#4F46E5", "#0EA5E9", "#E11D48", "#EF4444", "#8B5CF6"]

        fig_fun = go.Figure(go.Bar(
            y=funnel_labels[::-1], x=funnel_vals[::-1], orientation="h",
            marker=dict(color=funnel_colors[::-1], cornerradius=8),
            text=[f"<b>{v:,}</b>" for v in funnel_vals[::-1]], textposition="outside", cliponaxis=False,
            textfont=dict(size=12, color="#0F172A")
        ))
        fig_fun.update_layout(
            height=400, margin=dict(l=10, r=60, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, range=[0, max(funnel_vals + [1]) * 1.22]),
            yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        st.plotly_chart(fig_fun, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="sec-header-rto">
        <div class="sec-title">🚚 Section 1: RTO Analysis</div>
        <div class="sec-sub">RTO Orders by Reverse Status & Top States</div>
    </div>
    """, unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 RTO Reverse Status (Donut)</div>', unsafe_allow_html=True)
        if not rto_df.empty:
            r_st = rto_df.groupby("Reverse_Status_Clean")["Unique_Order_Key"].nunique().reset_index(name="Count")
            fig_rs = go.Figure(go.Pie(
                labels=r_st["Reverse_Status_Clean"], values=r_st["Count"], hole=0.58,
                textinfo="percent", textposition="inside",
                marker=dict(colors=["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6"], line=dict(color="#FFFFFF", width=2.5))
            ))
            fig_rs.update_layout(height=340, margin=dict(l=15, r=15, t=20, b=65), paper_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5), annotations=[dict(text=f"<b>{rto_cnt:,}</b><br>RTO", x=0.5, y=0.5, font_size=13, showarrow=False)])
            st.plotly_chart(fig_rs, use_container_width=True)
        else:
            st.info("No RTO orders in selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rc2:
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Top States by RTO Count</div>', unsafe_allow_html=True)
        if not rto_df.empty:
            s_rto = rto_df.groupby("State_Clean")["Unique_Order_Key"].nunique().reset_index(name="Orders").sort_values("Orders", ascending=True).tail(8)
            fig_sr = go.Figure(go.Bar(y=s_rto["State_Clean"], x=s_rto["Orders"], orientation="h", marker=dict(color="#0284C7", cornerradius=8), text=s_rto["Orders"], textposition="outside", cliponaxis=False))
            fig_sr.update_layout(height=340, margin=dict(l=10, r=45, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(s_rto["Orders"].max()) * 1.28, 3.0)]))
            st.plotly_chart(fig_sr, use_container_width=True)
        else:
            st.info("No state RTO data.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sec-header-exch">
        <div class="sec-title">📥 Section 2: Customer Return & Exchange Analysis</div>
        <div class="sec-sub">Customer Returns (return_refund) & Exchanges</div>
    </div>
    """, unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown('<div class="card-box"><div class="card-title">🍩 Customer Return Reverse Status (Donut)</div>', unsafe_allow_html=True)
        if not cust_ret_df.empty:
            c_st = cust_ret_df.groupby("Reverse_Status_Clean")["Unique_Order_Key"].nunique().reset_index(name="Count")
            fig_cs = go.Figure(go.Pie(
                labels=c_st["Reverse_Status_Clean"], values=c_st["Count"], hole=0.58,
                textinfo="percent", textposition="inside",
                marker=dict(colors=["#E11D48", "#8B5CF6", "#10B981", "#F59E0B", "#0EA5E9"], line=dict(color="#FFFFFF", width=2.5))
            ))
            fig_cs.update_layout(height=340, margin=dict(l=15, r=15, t=20, b=65), paper_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5), annotations=[dict(text=f"<b>{cust_ret_cnt:,}</b><br>Cust Ret", x=0.5, y=0.5, font_size=13, showarrow=False)])
            st.plotly_chart(fig_cs, use_container_width=True)
        else:
            st.info("No Customer Return orders in selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="card-box"><div class="card-title">🔄 Exchanges & Net Seller Paid Summary</div>', unsafe_allow_html=True)
        st.metric("Exchange Orders (Unique)", f"{exch_cnt:,}")
        st.metric("Exchange seller_paid_amount", f"₹{float(exch_df['seller_paid_amount'].sum()) if not exch_df.empty else 0.0:,.2f}")
        st.metric("Net Seller Paid Revenue (After RTO & Cust Ret)", f"₹{net_seller_rev:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    p1, p2 = st.columns([1.2, 1])
    with p1:
        st.markdown('<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by Unique Orders</div>', unsafe_allow_html=True)
        top_sku = p_df.groupby("SKU_Clean")["Unique_Order_Key"].nunique().sort_values(ascending=False).head(7)
        if not top_sku.empty:
            mv = top_sku.max()
            for rank, (sku, cnt) in enumerate(top_sku.items(), start=1):
                pct = cnt / mv * 100
                st.markdown(f"""<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{sku}</span><span style="color:#DB2777;">{cnt:,} ord</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with p2:
        st.markdown('<div class="card-box"><div class="card-title">👗 Article Types (Unique Orders)</div>', unsafe_allow_html=True)
        art_df = p_df.groupby("Article_Clean")["Unique_Order_Key"].nunique().reset_index(name="Orders").sort_values("Orders", ascending=False)
        fig_art = go.Figure(go.Bar(x=art_df["Article_Clean"], y=art_df["Orders"], marker=dict(color="#8B5CF6", cornerradius=8), text=art_df["Orders"], textposition="outside", cliponaxis=False))
        fig_art.update_layout(height=310, margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(float(art_df["Orders"].max()) * 1.25, 3.0)]))
        st.plotly_chart(fig_art, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown(f"#### 📋 Filtered Myntra Orders ({tot_ord:,} Unique Orders / {tot_rows:,} Rows)")
    tbl_cols = [c for c in ["order_number", "sale_order_code", "Order_Create_Date", "order_date", "order_item_status", "return_type", "Combined_Status", "return_status", "product_sku_code", "article_type", "customer_state", "seller_paid_amount", "discount_amount", "delivery_charges"] if c in p_df.columns]
    _safe_dataframe(p_df[tbl_cols], use_container_width=True, height=360, hide_index=True)
    st.download_button("⬇️ Download Filtered Myntra Data CSV", p_df[tbl_cols].to_csv(index=False).encode("utf-8"), f"myntra_analysis_{start_date}_{end_date}.csv", "text/csv")
