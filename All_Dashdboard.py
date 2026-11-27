import base64
import datetime
import glob
import io
import os
import re
import urllib.request
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & EXECUTIVE STYLING
# ==============================================================================
st.set_page_config(
    page_title="ARTH LIFE Kids Fashion — Analytics Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _html(raw_html: str):
  """Flatten HTML lines so Markdown never treats indented tags as code blocks."""
  lines = [ln.strip() for ln in raw_html.strip().splitlines() if ln.strip()]
  st.markdown("".join(lines), unsafe_allow_html=True)


_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 45%, #F4F6FB 100%);
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

.block-container {
    padding-top: 1.0rem !important;
    padding-bottom: 2.4rem !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

/* Login Card */
.login-wrap {
    max-width: 440px;
    margin: 56px auto 18px auto;
    background: #FFFFFF;
    border-radius: 24px;
    padding: 34px 32px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
    border: 1px solid #E2E8F0;
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

/* Top Switcher Bar */
.hub-topbar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 12px 18px;
    margin-bottom: 12px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
}
.hub-brand-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}
.hub-brand-title {
    font-size: 18px;
    font-weight: 800;
    color: #0F172A;
    margin: 0;
}
.hub-brand-sub {
    font-size: 12px;
    color: #64748B;
}
.hub-status-badge {
    background: #EEF2FF;
    color: #4338CA;
    border: 1px solid #C7D2FE;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
}

/* Daily Banner & Cards */
.main-banner {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
.main-h1 { font-size: 20px; font-weight: 800; color: #0F172A; margin: 0; }
.main-sub { font-size: 12.5px; color: #64748B; margin-top: 3px; }

/* Channel Executive Banner */
.exec-banner {
    background: linear-gradient(135deg, #0F172A 0%, #312E81 55%, #7C3AED 100%);
    border-radius: 22px;
    padding: 22px 28px;
    color: #FFFFFF;
    margin-bottom: 18px;
    box-shadow: 0 14px 30px rgba(30, 41, 59, 0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}
.exec-banner.myntra { background: linear-gradient(135deg, #0F172A 0%, #831843 55%, #7C3AED 100%); }
.exec-banner.nykaa  { background: linear-gradient(135deg, #0F172A 0%, #9D174D 55%, #7C3AED 100%); }
.exec-banner-left { display: flex; align-items: center; gap: 16px; }
.exec-title { font-size: 24px; font-weight: 800; letter-spacing: -0.4px; margin: 0; color: #FFFFFF; }
.exec-sub   { font-size: 13px; opacity: 0.9; margin-top: 4px; color: #F8FAFC; }
.exec-pill  {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.30);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
}

/* Daily KPI & Section Bars */
.sec-bar {
    font-size: 14.5px;
    font-weight: 800;
    color: #0F172A;
    margin: 18px 0 8px 2px;
    padding-left: 10px;
    border-left: 4px solid #4F46E5;
}
.kpi-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid var(--accent, #4F46E5);
    border-radius: 14px 14px 4px 4px;
    padding: 14px 16px 10px 16px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
.kpi-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.kpi-lbl { font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.4px; }
.kpi-pill-pos { background: #ECFDF5; color: #059669; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-pill-neg { background: #FFF1F2; color: #E11D48; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-pill-neu { background: #F1F5F9; color: #475569; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-main-num { font-size: 28px; font-weight: 800; color: #0F172A; margin: 8px 0 6px 0; line-height: 1.05; }
.kpi-foot { font-size: 11.5px; font-weight: 600; color: #334155; border-top: 1px dashed #E2E8F0; padding-top: 6px; }

.viz-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px 14px 10px 14px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    margin-bottom: 14px;
}
.viz-heading { text-align: center; font-size: 14px; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
.viz-info {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 7px 10px;
    margin-top: 6px;
    font-size: 12px;
    color: #334155;
}

/* Channel Section Headers & KPI Cards */
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
""")

# ==============================================================================
# 2. SHARED HELPERS & LOGO LOADER
# ==============================================================================
LOGO_CANDIDATES = [
    "logo.jpeg",
    "Arth_life_Loge.jpeg",
    "Arth_life_Logo.jpeg",
    "arth_life_loge.jpeg",
    "logo.jpg",
    "logo.png",
]


def _search_dirs():
  """Return candidate directories for data files and assets."""
  script_dir = os.path.dirname(os.path.abspath(__file__))
  cwd_dir = os.getcwd()
  base_roots = [
      script_dir,
      os.path.dirname(script_dir),
      cwd_dir,
      os.path.dirname(cwd_dir),
  ]
  dirs = []
  seen = set()
  for r in base_roots:
    for sub in ["", "data", "Data", "assets", "myntra", "nykaa", "files", "uploads"]:
      cand = os.path.abspath(os.path.join(r, sub)) if sub else os.path.abspath(r)
      if cand not in seen and os.path.isdir(cand):
        seen.add(cand)
        dirs.append(cand)
  return dirs


def _norm_key(name: str) -> str:
  """Normalize filenames so punctuation and spacing differences still match."""
  stem, ext = os.path.splitext(str(name or "").lower().strip())
  stem_clean = re.sub(r"[^a-z0-9]+", "", stem)
  return f"{stem_clean}{ext}"


def _find_local_file(candidates: list, globs: list = None, keyword_tokens: list = None):
  """Locate a matching file in known folders or nearby subdirectories."""
  norm_targets = {_norm_key(c) for c in candidates}
  exact_lower = {str(c).lower().strip() for c in candidates}

  for folder in _search_dirs():
    try:
      entries = os.listdir(folder)
    except Exception:
      continue
    for fn in sorted(entries):
      fp = os.path.join(folder, fn)
      if not os.path.isfile(fp):
        continue
      low = fn.lower().strip()
      if low in exact_lower or _norm_key(fn) in norm_targets:
        return os.path.abspath(fp)

  if globs:
    for folder in _search_dirs():
      for pat in globs:
        matches = sorted(glob.glob(os.path.join(folder, pat)))
        if matches:
          return os.path.abspath(matches[0])

  roots = list(
      dict.fromkeys([
          os.path.abspath(os.path.dirname(os.path.abspath(__file__))),
          os.path.abspath(os.getcwd()),
      ])
  )
  for root in roots:
    for cur_root, _, files in os.walk(root):
      rel_depth = len(os.path.relpath(cur_root, root).split(os.sep))
      if rel_depth > 3:
        continue
      for fn in sorted(files):
        fp = os.path.join(cur_root, fn)
        low = fn.lower().strip()
        if low in exact_lower or _norm_key(fn) in norm_targets:
          return os.path.abspath(fp)
        if (
            keyword_tokens
            and any(tok in low for tok in keyword_tokens)
            and low.endswith((".xlsx", ".xls", ".csv"))
        ):
          return os.path.abspath(fp)
  return None


def _get_logo_data_uri():
  """Load brand logo as a base64 data URI if available."""
  fp = _find_local_file(LOGO_CANDIDATES)
  if fp:
    ext = os.path.splitext(fp)[1].lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'png'}"
    try:
      with open(fp, "rb") as img_f:
        b64 = base64.b64encode(img_f.read()).decode("utf-8")
      return f"data:{mime};base64,{b64}"
    except Exception:
      return None
  return None


LOGO_URI = _get_logo_data_uri()
LOGO_LOGIN_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    'style="width:82px;height:82px;border-radius:50%;object-fit:cover;margin:0'
    ' auto 12px auto;display:block;box-shadow:0 8px 20px'
    ' rgba(15,23,42,0.14);border:2px solid #E2E8F0;" />'
    if LOGO_URI
    else '<div class="login-badge">📊</div>'
)
LOGO_BANNER_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    'style="width:58px;height:58px;min-width:58px;border-radius:50%;object-fit:cover;border:2px'
    ' solid rgba(255,255,255,0.45);box-shadow:0 6px 16px rgba(0,0,0,0.22);" />'
    if LOGO_URI
    else ""
)


def _github_raw_url(filename: str):
  """Build GitHub raw URL if [github] repo settings exist in st.secrets."""
  try:
    if "github" in st.secrets:
      repo = str(st.secrets["github"].get("repo", "")).strip().strip("/")
      branch = str(st.secrets["github"].get("branch", "main")).strip()
      base_path = str(st.secrets["github"].get("path", "")).strip().strip("/")
      if repo:
        parts = [p for p in [base_path, filename] if p]
        return (
            f"https://raw.githubusercontent.com/{repo}/{branch}/"
            + "/".join(parts)
        )
  except Exception:
    pass
  return None


@st.cache_data(show_spinner=False)
def _fetch_bytes_from_url(url: str):
  """Fetch raw file bytes from a URL."""
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  with urllib.request.urlopen(req, timeout=25) as resp:
    return resp.read()


def _resolve_source(
    local_candidates: list,
    globs: list,
    github_filename: str,
    fallback_local_path: str = None,
    keyword_tokens: list = None,
    uploaded_obj=None,
):
  """Resolve file source from upload, repository/local path, or GitHub raw URL."""
  if uploaded_obj is not None:
    return uploaded_obj, f"Uploaded: {getattr(uploaded_obj, 'name', 'File')}"
  local_fp = _find_local_file(
      local_candidates, globs=globs, keyword_tokens=keyword_tokens
  )
  if local_fp:
    return local_fp, f"GitHub Repo: {os.path.basename(local_fp)}"
  if fallback_local_path and os.path.exists(fallback_local_path):
    return (
        fallback_local_path,
        f"Local Path: {os.path.basename(fallback_local_path)}",
    )
  gh_url = _github_raw_url(github_filename)
  if gh_url:
    try:
      raw_bytes = _fetch_bytes_from_url(gh_url)
      return io.BytesIO(raw_bytes), f"GitHub Raw: {github_filename}"
    except Exception:
      pass
  return None, "Not Connected"


def _find_col(df: pd.DataFrame, candidates: list):
  """Find a matching column name case-insensitively."""
  if df is None or df.empty:
    return None
  col_map = {str(c).strip().lower(): c for c in df.columns}
  for cand in candidates:
    key = cand.strip().lower()
    if key in col_map:
      return col_map[key]
  return None


def _to_num(series: pd.Series) -> pd.Series:
  """Convert currency or comma-formatted strings to float cleanly."""
  cleaned = (
      series.astype(str)
      .str.replace(",", "", regex=False)
      .str.replace("₹", "", regex=False)
      .str.strip()
  )
  return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def _safe_dataframe(df: pd.DataFrame, **kwargs):
  """Render a DataFrame safely for Streamlit without large-int or object overflow."""
  if df is None or df.empty:
    st.dataframe(pd.DataFrame(), **kwargs)
    return
  clean_df = df.copy()
  for col in clean_df.columns:
    s = clean_df[col]
    if pd.api.types.is_numeric_dtype(s):
      num_s = (
          pd.to_numeric(s, errors="coerce")
          .replace([float("inf"), float("-inf")], 0.0)
          .fillna(0.0)
      )
      if (num_s.abs() > 9e15).any():
        clean_df[col] = num_s.apply(
            lambda v: f"{int(round(v))}" if float(v).is_integer() else f"{v:.2f}"
        )
      else:
        clean_df[col] = num_s
    elif pd.api.types.is_datetime64_any_dtype(s):
      clean_df[col] = s.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
    else:
      clean_df[col] = s.apply(
          lambda v: "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
      )
  st.dataframe(clean_df, **kwargs)


def _make_donut_fig(labels, values, colors, center_text):
  """Build a styled Plotly donut chart."""
  fig = go.Figure(
      go.Pie(
          labels=labels,
          values=values,
          hole=0.58,
          textinfo="percent",
          textposition="inside",
          insidetextorientation="horizontal",
          marker=dict(
              colors=colors[: len(labels)],
              line=dict(color="#FFFFFF", width=2.5),
          ),
          hovertemplate=(
              "<b>%{label}</b><br>Orders: %{value:,}<br>Share:"
              " %{percent}<extra></extra>"
          ),
      )
  )
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
          font=dict(size=11.5, color="#1E293B"),
      ),
      annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=14, showarrow=False)],
  )
  return fig


# ==============================================================================
# 3. SECURE LOGIN GATE
# ==============================================================================
def _get_credentials():
  """Read login credentials from st.secrets with fallback defaults."""
  try:
    if "auth" in st.secrets:
      return str(st.secrets["auth"].get("username", "arthlife")), str(
          st.secrets["auth"].get("password", "Arth@2026")
      )
  except Exception:
    pass
  return "arthlife", "Arth@2026"


VALID_USER, VALID_PASS = _get_credentials()
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
  _html(f"""
    <div class="login-wrap">
        {LOGO_LOGIN_HTML}
        <div class="login-title">ARTH LIFE Kids Fashion</div>
        <div class="login-sub">Individual Channel Analytics — Please Sign In</div>
    </div>
    """)
  _, mid_col, _ = st.columns([1.15, 1, 1.15])
  with mid_col:
    with st.form("login_form", clear_on_submit=False):
      in_user = st.text_input("👤 User ID", placeholder="Enter User ID")
      in_pass = st.text_input(
          "🔑 Password", type="password", placeholder="Enter Password"
      )
      if st.form_submit_button("🔓 Sign In to Dashboard", use_container_width=True):
        if in_user.strip() == VALID_USER and in_pass == VALID_PASS:
          st.session_state["authenticated"] = True
          st.rerun()
        else:
          st.error("Invalid User ID or Password. Please try again.")
  st.stop()


# ==============================================================================
# 4. DATA LOADERS (MODEL EXCEL, MYNTRA, NYKAA)
# ==============================================================================
DEFAULT_MODEL_PATH = r"C:\Users\yasha\OneDrive\Desktop\New folder (4)\New folder (4)\New folder\PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx"
MODEL_FILENAME = "PowerBI_Dimensional_Model_Ecommerce_2.2.xlsx"
MYNTRA_CONSOLIDATED_NAME = "Myntra_Consolidated_Orders.xlsx"
NYKAA_DEFAULT_NAME = "OrderExport (16).xls"


def _read_excel_or_html_table(file_src, preferred_sheet=None):
  """Read real Excel workbooks or HTML-exported .xls files."""
  if hasattr(file_src, "seek"):
    file_src.seek(0)
  try:
    xls = pd.ExcelFile(file_src)
    sheet = (
        preferred_sheet
        if (preferred_sheet and preferred_sheet in xls.sheet_names)
        else xls.sheet_names[0]
    )
    return pd.read_excel(xls, sheet_name=sheet)
  except Exception:
    if hasattr(file_src, "seek"):
      file_src.seek(0)
      raw_bytes = file_src.read()
    else:
      with open(file_src, "rb") as f:
        raw_bytes = f.read()
    html_tables = pd.read_html(io.BytesIO(raw_bytes))
    if html_tables:
      return html_tables[0]
    raise


@st.cache_data(show_spinner=False)
def load_model_excel(file_source):
  """Load Dim_Orders, Fact_Dispatches, and Fact_Reverse_Logistics from model workbook."""
  if hasattr(file_source, "seek"):
    file_source.seek(0)
  xls = pd.ExcelFile(file_source)
  orders_sheet = (
      "Dim_Orders (2)" if "Dim_Orders (2)" in xls.sheet_names else "Dim_Orders"
  )
  disp_sheet = (
      "Fact_Dispatches (2)"
      if "Fact_Dispatches (2)" in xls.sheet_names
      else "Fact_Dispatches"
  )
  rev_sheet = (
      "Fact_Reverse_Logistics (2)"
      if "Fact_Reverse_Logistics (2)" in xls.sheet_names
      else (
          "Fact_Reverse_Logistics"
          if "Fact_Reverse_Logistics" in xls.sheet_names
          else None
      )
  )

  orders = pd.read_excel(xls, sheet_name=orders_sheet)
  disp = pd.read_excel(xls, sheet_name=disp_sheet)
  rev = pd.read_excel(xls, sheet_name=rev_sheet) if rev_sheet else pd.DataFrame()

  orders["Order_Date_dt"] = pd.to_datetime(
      orders["Order_Date"], format="mixed", dayfirst=True, errors="coerce"
  )
  for c in [
      "Order_Total",
      "Order_Subtotal",
      "Discount",
      "Shipping",
      "Total_Line_Items",
  ]:
    if c in orders.columns:
      orders[c] = _to_num(orders[c])

  pm = (
      orders["Payment_Method"].fillna("Unknown").astype(str)
      if "Payment_Method" in orders.columns
      else pd.Series(["Unknown"] * len(orders))
  )
  orders["Payment_Category"] = np.where(
      pm.str.lower().str.contains("cod|cash on delivery"),
      "COD",
      np.where(
          pm.str.lower().str.contains("razorpay|upi|card|wallet|prepaid"),
          "Prepaid (Razorpay)",
          np.where(pm.str.lower().str.contains("manual"), "Manual", "Other / Blank"),
      ),
  )

  if "Dispatch_Date" in disp.columns:
    disp["Dispatch_Date_dt"] = pd.to_datetime(
        disp["Dispatch_Date"], format="mixed", dayfirst=True, errors="coerce"
    )
  disp["Amount"] = _to_num(disp.get("Amount", 0))
  disp["Is_Delivered"] = disp.get("Is_Delivered", False).fillna(False).astype(bool)
  disp["Is_RTO"] = disp.get("Is_RTO", False).fillna(False).astype(bool)

  if not rev.empty and "Pickup_Date" in rev.columns:
    rev["Pickup_Date_dt"] = pd.to_datetime(
        rev["Pickup_Date"], format="mixed", dayfirst=True, errors="coerce"
    )
    rev["Amount"] = _to_num(rev.get("Amount", 0))

  return orders, disp, rev


def _read_single_myntra(src):
  """Read a Myntra consolidated Excel or CSV file."""
  name = (
      src
      if isinstance(src, str)
      else getattr(src, "name", MYNTRA_CONSOLIDATED_NAME)
  )
  low = str(name).lower()
  if low.endswith(".csv"):
    if hasattr(src, "seek"):
      src.seek(0)
    return pd.read_csv(src, low_memory=False), os.path.basename(str(name))
  return (
      _read_excel_or_html_table(src, preferred_sheet="Myntra_All_Orders"),
      os.path.basename(str(name)),
  )


def _build_combined_status(s_val, r_val):
  """Combine Myntra order_item_status and return_type into a readable label."""
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
def load_myntra_data(source):
  """Load and normalize Myntra order data."""
  if source is None:
    return pd.DataFrame(), []
  tmp, nm = _read_single_myntra(source)
  df = tmp.drop_duplicates().copy()

  ord_dt_col = _find_col(
      df, ["order_date", "Order Date", "order_created_date"]
  )
  pack_dt_col = _find_col(df, ["packing_date", "Packing Date", "packed_date"])

  df["order_date_dt"] = pd.to_datetime(
      df[ord_dt_col] if ord_dt_col else pd.Series(dtype=str),
      format="mixed",
      dayfirst=True,
      errors="coerce",
  )
  if (
      hasattr(df["order_date_dt"].dt, "tz")
      and df["order_date_dt"].dt.tz is not None
  ):
    df["order_date_dt"] = (
        df["order_date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    )
  df["Order_Create_Date"] = df["order_date_dt"].dt.date

  df["packing_date_dt"] = pd.to_datetime(
      df[pack_dt_col] if pack_dt_col else pd.Series(dtype=str),
      format="mixed",
      dayfirst=True,
      errors="coerce",
  )
  if (
      hasattr(df["packing_date_dt"].dt, "tz")
      and df["packing_date_dt"].dt.tz is not None
  ):
    df["packing_date_dt"] = (
        df["packing_date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    )

  for canonical, cands in [
      (
          "seller_paid_amount",
          [
              "seller_paid_amount",
              "Seller Paid Amount",
              "seller_payable_amount",
          ],
      ),
      (
          "Total_Customer_Paid",
          [
              "Total_Customer_Paid",
              "total_customer_paid",
              "customer_paid_amount",
          ],
      ),
      ("mrp", ["mrp", "MRP"]),
      ("discount_amount", ["discount_amount", "Discount Amount", "discount"]),
      (
          "delivery_charges",
          ["delivery_charges", "Delivery Charges", "shipping_fee"],
      ),
  ]:
    found_c = _find_col(df, cands)
    df[canonical] = _to_num(df[found_c]) if found_c else 0.0

  ord_num_col = _find_col(df, ["order_number", "Order Number"])
  sale_ord_col = _find_col(df, ["sale_order_code", "Sale Order Code"])
  if ord_num_col and df[ord_num_col].notna().any():
    df["Unique_Order_Key"] = df[ord_num_col].astype(str).str.strip()
  elif sale_ord_col and df[sale_ord_col].notna().any():
    df["Unique_Order_Key"] = df[sale_ord_col].astype(str).str.strip()
  else:
    df["Unique_Order_Key"] = df.index.astype(str)

  ois_col = _find_col(df, ["order_item_status", "Order Item Status", "status"])
  rt_col = _find_col(df, ["return_type", "Return Type"])
  rst_col = _find_col(df, ["return_status", "Return Status", "reverse_status"])

  raw_ois = (
      df[ois_col].fillna("").astype(str).str.strip()
      if ois_col
      else pd.Series([""] * len(df))
  )
  raw_rt = (
      df[rt_col].fillna("").astype(str).str.strip()
      if rt_col
      else pd.Series([""] * len(df))
  )
  rst_u = (
      df[rst_col]
      .fillna("UNKNOWN")
      .astype(str)
      .str.strip()
      .str.upper()
      .replace("", "UNKNOWN")
      if rst_col
      else pd.Series(["UNKNOWN"] * len(df))
  )

  df["Status_Clean"] = raw_ois.str.lower()
  df["Return_Type_Clean"] = raw_rt.str.lower()
  df["Reverse_Status_Clean"] = rst_u
  df["Combined_Status"] = [
      _build_combined_status(a, b) for a, b in zip(raw_ois, raw_rt)
  ]

  art_col = _find_col(df, ["article_type", "Article Type", "category"])
  sku_col = _find_col(
      df, ["product_sku_code", "Product SKU Code", "sku_code", "sku"]
  )

  df["Article_Clean"] = (
      df[art_col].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
      if art_col
      else pd.Series(["Unknown"] * len(df))
  )
  df["SKU_Clean"] = (
      df[sku_col].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
      if sku_col
      else pd.Series(["Unknown"] * len(df))
  )
  return df, [nm]


@st.cache_data(show_spinner=False)
def load_nykaa_data(file_src):
  """Load and normalize Nykaa export data."""
  if file_src is None:
    return pd.DataFrame()
  name = (
      file_src
      if isinstance(file_src, str)
      else getattr(file_src, "name", NYKAA_DEFAULT_NAME)
  )
  if str(name).lower().endswith(".csv"):
    if hasattr(file_src, "seek"):
      file_src.seek(0)
    df = pd.read_csv(file_src, low_memory=False)
  else:
    df = _read_excel_or_html_table(file_src, preferred_sheet="Export")

  df = df.drop_duplicates().copy()
  odate_col = _find_col(df, ["Order Date", "order_date", "Created Date"])
  df["Order_Date_dt"] = pd.to_datetime(
      df[odate_col] if odate_col else pd.Series(dtype=str),
      format="mixed",
      dayfirst=True,
      errors="coerce",
  )
  if (
      hasattr(df["Order_Date_dt"].dt, "tz")
      and df["Order_Date_dt"].dt.tz is not None
  ):
    df["Order_Date_dt"] = (
        df["Order_Date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    )
  df["Order_Create_Date"] = df["Order_Date_dt"].dt.date

  for canonical, cands in [
      ("Qty", ["Qty", "Quantity", "qty"]),
      ("Unit Price", ["Unit Price", "unit_price", "Price"]),
      ("Line Amount", ["Line Amount", "line_amount", "Total Amount", "Amount"]),
  ]:
    found_c = _find_col(df, cands)
    df[canonical] = _to_num(df[found_c]) if found_c else 0.0

  wno_col = _find_col(
      df, ["Web Order No", "web_order_no", "Order No", "Order ID"]
  )
  df["Order_Key"] = (
      df[wno_col].fillna("").astype(str).str.strip()
      if wno_col
      else pd.Series(df.index.astype(str), index=df.index)
  )

  st_col = _find_col(df, ["Status", "status", "Order Status"])
  df["Status_Clean"] = (
      df[st_col].fillna("Unknown").astype(str).str.strip()
      if st_col
      else pd.Series(["Unknown"] * len(df))
  )
  df["Status_Lower"] = df["Status_Clean"].str.lower()

  ot_col = _find_col(df, ["Order Type", "order_type", "Payment Mode"])
  df["Order_Type_Clean"] = (
      df[ot_col].fillna("Unknown").astype(str).str.strip()
      if ot_col
      else pd.Series(["Unknown"] * len(df))
  )

  skuc_col = _find_col(df, ["SKU Code", "sku_code", "SKU"])
  skun_col = _find_col(df, ["SKU Name", "sku_name", "Product Name"])
  df["SKU_Code_Clean"] = (
      df[skuc_col].fillna("Unknown").astype(str).str.strip()
      if skuc_col
      else pd.Series(["Unknown"] * len(df))
  )
  df["SKU_Name_Clean"] = (
      df[skun_col].fillna("Unknown").astype(str).str.strip()
      if skun_col
      else pd.Series(["Unknown"] * len(df))
  )
  return df


# ==============================================================================
# 5. CONNECT GITHUB FILES & INDIVIDUAL PAGE NAVIGATION
# ==============================================================================
DASHBOARD_PAGES = [
    "📊 Daily Analysis",
    "👗 Shopify Analysis",
    "🛍️ Myntra Analysis",
    "💄 Nykaa Analysis",
]

if "active_page" not in st.session_state:
  st.session_state["active_page"] = DASHBOARD_PAGES[0]

with st.sidebar:
  if LOGO_URI:
    sb1, sb2 = st.columns([1, 3.2])
    with sb1:
      st.image(LOGO_URI, width=44)
    with sb2:
      st.markdown("### ARTH LIFE")
  else:
    st.markdown("### 📊 ARTH LIFE")
  st.caption("GitHub Connected • Individual Pages")

  sb_page = st.radio(
      "🎯 Individual Dashboard Page",
      options=DASHBOARD_PAGES,
      index=DASHBOARD_PAGES.index(st.session_state["active_page"]),
      key="sidebar_page_radio",
  )
  st.session_state["active_page"] = sb_page

  if st.button("🚪 Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

  st.divider()
  st.markdown("#### 📂 Manual Override (Optional)")
  sb_up_myntra = st.file_uploader(
      "Myntra_Consolidated_Orders.xlsx",
      type=["xlsx", "xls", "csv"],
      key="sb_up_myntra",
  )
  sb_up_nykaa = st.file_uploader(
      "OrderExport (16).xls",
      type=["xls", "xlsx", "csv"],
      key="sb_up_nykaa",
  )

model_src, model_status = _resolve_source(
    [MODEL_FILENAME],
    ["*dimensional_model*.xlsx"],
    MODEL_FILENAME,
    fallback_local_path=DEFAULT_MODEL_PATH,
    keyword_tokens=["dimensional_model"],
)
myntra_src, myntra_status = _resolve_source(
    [MYNTRA_CONSOLIDATED_NAME],
    [
        "*Myntra_Consolidated*.xlsx",
        "*myntra*.xlsx",
        "part-*.csv",
        "*myntra*.csv",
    ],
    MYNTRA_CONSOLIDATED_NAME,
    keyword_tokens=["myntra"],
    uploaded_obj=sb_up_myntra,
)
nykaa_src, nykaa_status = _resolve_source(
    [NYKAA_DEFAULT_NAME],
    ["*OrderExport*.xls*", "*nykaa*.xls*", "*nykaa*.csv"],
    NYKAA_DEFAULT_NAME,
    keyword_tokens=["orderexport", "nykaa"],
    uploaded_obj=sb_up_nykaa,
)

with st.sidebar:
  st.divider()
  st.markdown("#### 🔗 Connection Status")
  st.caption(f"• Model: **{model_status}**")
  st.caption(f"• Myntra: **{myntra_status}**")
  st.caption(f"• Nykaa: **{nykaa_status}**")

_html("""
<div class="hub-topbar">
    <div class="hub-brand-row">
        <div>
            <div class="hub-brand-title">ARTH LIFE Kids Fashion — Individual Dashboard View</div>
            <div class="hub-brand-sub">Connected to Myntra_Consolidated_Orders.xlsx & OrderExport (16).xls</div>
        </div>
        <div class="hub-status-badge">🔗 GitHub Connected</div>
    </div>
</div>
""")

top_nav1, top_nav2 = st.columns([4.4, 0.6])
with top_nav1:
  chosen_page = st.radio(
      "Select Individual Dashboard",
      options=DASHBOARD_PAGES,
      index=DASHBOARD_PAGES.index(st.session_state["active_page"]),
      horizontal=True,
      label_visibility="collapsed",
      key="top_page_radio",
  )
  st.session_state["active_page"] = chosen_page
with top_nav2:
  if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()


# ==============================================================================
# 6. PAGE 1: DAILY ANALYSIS
# ==============================================================================
def render_daily_page():
  if model_src is None:
    st.warning(
        f"Model file `{MODEL_FILENAME}` was not found in GitHub or local"
        " folders."
    )
    return

  df_orders, df_disp, df_rev = load_model_excel(model_src)
  valid_dates = df_orders["Order_Date_dt"].dropna()
  if valid_dates.empty:
    st.error("No valid dates found in Order_Date.")
    return

  min_d = valid_dates.min().date()
  max_d = valid_dates.max().date()
  default_target = datetime.date(2026, 11, 22)
  init_date = default_target if min_d <= default_target <= max_d else max_d

  b1, b2 = st.columns([1.8, 1.0])
  with b1:
    _html("""
        <div class="main-banner">
            <div class="main-h1">Arth life Daily Analysis</div>
            <div class="main-sub">Particular Date KPIs + Automatic Rolling 7-Day Section-wise Analysis</div>
        </div>
        """)
  with b2:
    selected_date = st.date_input(
        "📅 Select Particular Date (Auto 7 Days)",
        value=init_date,
        min_value=min_d,
        max_value=max_d,
        key="arth_daily_date",
    )

  start_7d = selected_date - datetime.timedelta(days=6)
  dates_7d = [start_7d + datetime.timedelta(days=i) for i in range(7)]
  prev_date = selected_date - datetime.timedelta(days=1)

  f_orders = df_orders.copy()
  f_orders["_ord_d"] = f_orders["Order_Date_dt"].dt.date
  f_orders["_ym"] = f_orders["Order_Date_dt"].dt.to_period("M").astype(str)

  fin_low = (
      f_orders["Financial_Status"].fillna("").astype(str).str.strip().str.lower()
  )
  valid_orders = f_orders[~fin_low.isin(["voided", "cancelled"])].copy()
  dax_orders = f_orders[~fin_low.isin(["voided", "cancelled", "refunded"])].copy()

  f_disp = df_disp[
      df_disp["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))
  ].copy()
  f_disp["_disp_d"] = f_disp["Dispatch_Date_dt"].dt.date
  stat_str = f_disp["Shipment_Status"].fillna("").astype(str).str.strip()
  valid_disp = f_disp[
      ~stat_str.isin(["CANCELLED", "Stop Booking/Delivery"])
  ].copy()

  if not df_rev.empty and "Base_Order_ID" in df_rev.columns:
    f_rev = df_rev[
        df_rev["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))
    ].copy()
    f_rev["_rev_d"] = (
        f_rev["Pickup_Date_dt"].dt.date
        if "Pickup_Date_dt" in f_rev.columns
        else pd.NaT
    )
  else:
    f_rev = pd.DataFrame(columns=["Base_Order_ID", "_rev_d"])

  latest_ym_val = f_orders[f_orders["_ord_d"] <= selected_date]["_ym"].dropna().max()
  if pd.isna(latest_ym_val) or not latest_ym_val:
    latest_ym_val = f_orders["_ym"].dropna().max()

  ful_str_dax = dax_orders["Fulfillment_Status"].fillna("").astype(str).str.strip()
  latest_month_unful_df = dax_orders[
      (dax_orders["_ym"] == latest_ym_val)
      & (ful_str_dax.loc[dax_orders.index] == "Unfulfilled")
  ].copy()
  latest_month_unful_cnt = int(len(latest_month_unful_df))

  day_ord = valid_orders[valid_orders["_ord_d"] == selected_date]
  ord_day_cnt = len(set(day_ord["Base_Order_ID"].dropna().astype(str)))
  ord_prev_cnt = len(
      set(
          valid_orders[valid_orders["_ord_d"] == prev_date]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  ord_diff = ord_day_cnt - ord_prev_cnt
  day_rev_amt = float(day_ord["Order_Total"].sum())
  day_aov_amt = day_rev_amt / ord_day_cnt if ord_day_cnt > 0 else 0.0

  pre_day_cnt = len(
      set(
          day_ord[
              day_ord["Financial_Status"]
              .fillna("")
              .astype(str)
              .str.strip()
              .str.lower()
              .isin(["paid", "authorized"])
          ]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  cod_day_cnt = max(0, ord_day_cnt - pre_day_cnt)

  ful_low = (
      valid_orders["Fulfillment_Status"]
      .fillna("")
      .astype(str)
      .str.strip()
      .str.lower()
  )
  ful_day_cnt = len(
      set(
          valid_orders[
              (valid_orders["_ord_d"] == selected_date) & (ful_low == "fulfilled")
          ]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  unful_day_cnt = len(
      set(
          valid_orders[
              (valid_orders["_ord_d"] == selected_date)
              & (~ful_low.isin(["fulfilled", "shipped"]))
          ]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  unful_prev_cnt = len(
      set(
          valid_orders[
              (valid_orders["_ord_d"] == prev_date)
              & (~ful_low.isin(["fulfilled", "shipped"]))
          ]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  unful_diff = unful_day_cnt - unful_prev_cnt

  disp_day_cnt = len(
      set(
          valid_disp[valid_disp["_disp_d"] == selected_date]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  disp_prev_cnt = len(
      set(
          valid_disp[valid_disp["_disp_d"] == prev_date]["Base_Order_ID"]
          .dropna()
          .astype(str)
      )
  )
  disp_diff = disp_day_cnt - disp_prev_cnt

  disp_up_to_eff = set(
      valid_disp[valid_disp["_disp_d"] <= selected_date]["Base_Order_ID"]
      .dropna()
      .astype(str)
  )
  rto_mask = f_disp["Is_RTO"].astype(bool) | stat_str.isin([
      "RETURNED_TO_ORIGIN",
      "RETURNING_TO_ORIGIN",
      "RTO Delivered",
      "Set RTO",
  ])

  rows_7d = []
  for d_k in dates_7d:
    odf_k = valid_orders[valid_orders["_ord_d"] == d_k]
    oids_k = set(odf_k["Base_Order_ID"].dropna().astype(str))
    ord_k = len(oids_k)
    rev_k = float(odf_k["Order_Total"].sum())
    aov_k = rev_k / ord_k if ord_k > 0 else 0.0

    pre_k = len(
        set(
            odf_k[
                odf_k["Financial_Status"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["paid", "authorized"])
            ]["Base_Order_ID"]
            .dropna()
            .astype(str)
        )
    )
    cod_k = max(0, ord_k - pre_k)

    ddf_k = valid_disp[valid_disp["_disp_d"] == d_k]
    dp_k = len(set(ddf_k["Base_Order_ID"].dropna().astype(str)))
    delh_k = (
        int((ddf_k["Dispatch_Category"] == "Delhivery").sum())
        if "Dispatch_Category" in ddf_k.columns
        else 0
    )
    dtdc_k = (
        int((ddf_k["Dispatch_Category"] == "DTDC").sum())
        if "Dispatch_Category" in ddf_k.columns
        else 0
    )

    undisp_k = len(oids_k - disp_up_to_eff)
    ful_k = len(
        set(
            odf_k[
                odf_k["Fulfillment_Status"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["fulfilled", "shipped"])
            ]["Base_Order_ID"]
            .dropna()
            .astype(str)
        )
    )
    unful_k = len(
        set(
            odf_k[
                ~odf_k["Fulfillment_Status"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["fulfilled", "shipped"])
            ]["Base_Order_ID"]
            .dropna()
            .astype(str)
        )
    )

    rto_k = int(
        f_disp[(f_disp["_disp_d"] == d_k) & rto_mask]["Base_Order_ID"].nunique()
    )
    ex_k = (
        int(f_rev[f_rev["_rev_d"] == d_k]["Base_Order_ID"].nunique())
        if (not f_rev.empty and "_rev_d" in f_rev.columns)
        else 0
    )

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
        "Exchange": ex_k,
    })
  df_7d = pd.DataFrame(rows_7d)

  def _spark(x_labels, y_vals, line_color="#4F46E5"):
    fig = go.Figure(
        go.Scatter(
            x=x_labels,
            y=y_vals,
            mode="lines+markers",
            line=dict(color=line_color, width=2.3, shape="spline"),
            marker=dict(size=5, color=line_color),
            text=[str(v) for v in y_vals],
            hovertemplate="%{x}: <b>%{text}</b><extra></extra>",
        )
    )
    fig.update_layout(
        height=42,
        margin=dict(l=4, r=4, t=4, b=2),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

  def _pill(diff_val, prev_val):
    if prev_val > 0:
      pct = diff_val / prev_val * 100.0
      cls = "kpi-pill-pos" if diff_val >= 0 else "kpi-pill-neg"
      return f'<span class="{cls}">{diff_val:+d} ({pct:+.1f}%)</span>'
    if diff_val != 0:
      cls = "kpi-pill-pos" if diff_val > 0 else "kpi-pill-neg"
      return f'<span class="{cls}">{diff_val:+d}</span>'
    return '<span class="kpi-pill-neu">0 (0.0%)</span>'

  c_k1, c_k2, c_k3, c_k4 = st.columns(4)
  with c_k1:
    _html(f"""
        <div class="kpi-box" style="--accent:#4F46E5;">
            <div class="kpi-head"><span class="kpi-lbl">Orders Created ({selected_date.strftime('%d %b')})</span>{_pill(ord_diff, ord_prev_cnt)}</div>
            <div class="kpi-main-num">{ord_day_cnt:,}</div>
            <div class="kpi-foot">Prepaid: <b>{pre_day_cnt:,}</b> | COD: <b>{cod_day_cnt:,}</b> · Rev: <b>₹{day_rev_amt:,.0f}</b></div>
        </div>
        """)
    st.plotly_chart(
        _spark(df_7d["Date"], df_7d["Orders"], "#4F46E5"),
        use_container_width=True,
    )

  with c_k2:
    _html(f"""
        <div class="kpi-box" style="--accent:#E11D48;">
            <div class="kpi-head"><span class="kpi-lbl">Unfulfilled Orders ({latest_ym_val})</span><span class="kpi-pill-neg">Latest Month</span></div>
            <div class="kpi-main-num">{latest_month_unful_cnt:,}</div>
            <div class="kpi-foot">Year_Month: <b>{latest_ym_val}</b> • Status: Unfulfilled</div>
        </div>
        """)
    st.plotly_chart(
        _spark(df_7d["Date"], df_7d["Unfulfilled"], "#E11D48"),
        use_container_width=True,
    )

  with c_k3:
    val_ful_disp = f"{ful_day_cnt:,}" if ful_day_cnt > 0 else "—"
    _html(f"""
        <div class="kpi-box" style="--accent:#7C3AED;">
            <div class="kpi-head"><span class="kpi-lbl">Day Wise Fulfilled</span><span class="kpi-pill-neu">AOV: ₹{day_aov_amt:,.0f}</span></div>
            <div class="kpi-main-num">{val_ful_disp}</div>
            <div class="kpi-foot">Fulfilled on {selected_date.strftime('%d %b')}</div>
        </div>
        """)
    st.plotly_chart(
        _spark(df_7d["Date"], df_7d["Fulfilled"], "#7C3AED"),
        use_container_width=True,
    )

  with c_k4:
    _html(f"""
        <div class="kpi-box" style="--accent:#F59E0B;">
            <div class="kpi-head"><span class="kpi-lbl">Day Wise Unfulfilled</span>{_pill(unful_diff, unful_prev_cnt)}</div>
            <div class="kpi-main-num">{unful_day_cnt:,}</div>
            <div class="kpi-foot">Prev Day ({prev_date.strftime('%d %b')}): <b>{unful_prev_cnt:,}</b> Unfulfilled</div>
        </div>
        """)
    st.plotly_chart(
        _spark(df_7d["Date"], df_7d["Unfulfilled"], "#F59E0B"),
        use_container_width=True,
    )

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

  _html(
      '<div class="sec-bar">Section 1 — Orders Created, Revenue/AOV & Daily'
      " Dispatches (7 Days)</div>"
  )
  s1_l, s1_r = st.columns([1.05, 1.0])
  with s1_l:
    _html(
        '<div class="viz-card"><div class="viz-heading">Order Created by'
        " Prepaid or COD</div>"
    )
    fig_oc = go.Figure()
    fig_oc.add_trace(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Prepaid"],
            name="Prepaid Orders",
            marker=dict(color="#4F46E5", cornerradius=4),
            text=df_7d["Prepaid"],
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=10.5),
        )
    )
    fig_oc.add_trace(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["COD"],
            name="COD Orders",
            marker=dict(color="#06B6D4", cornerradius=4),
            text=df_7d["COD"],
            textposition="inside",
            textfont=dict(color="#0F172A", size=10.5),
        )
    )
    fig_oc.add_trace(
        go.Scatter(
            x=df_7d["Date"],
            y=df_7d["Orders"],
            name="Total Orders",
            mode="lines+text",
            line=dict(color="rgba(0,0,0,0)"),
            text=[f"<b>{v}</b>" for v in df_7d["Orders"]],
            textposition="top center",
            textfont=dict(size=11.5, color="#1E1B4B"),
        )
    )
    fig_oc.update_layout(
        barmode="stack",
        height=270,
        margin=dict(l=8, r=8, t=26, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["Orders"].max(), 1) * 1.28],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_oc, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>7D Orders:</b> Total <b>{tot_7d_ord:,}</b>'
        f" orders (Prepaid: <b>{tot_7d_pre:,}</b> | COD:"
        f" <b>{tot_7d_cod:,}</b>) · Avg"
        f" <b>{tot_7d_ord/7:.1f}/day</b>.</div></div>"
    )

    _html(
        '<div class="viz-card"><div class="viz-heading">Daily Order Revenue'
        " (₹) & Average Order Value (AOV)</div>"
    )
    fig_rev = make_subplots(specs=[[{"secondary_y": True}]])
    fig_rev.add_trace(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Revenue"],
            name="Revenue (₹)",
            marker=dict(color="#6366F1", cornerradius=5),
            text=[f"₹{v/1000:.1f}k" for v in df_7d["Revenue"]],
            textposition="outside",
            textfont=dict(size=10, color="#312E81"),
        ),
        secondary_y=False,
    )
    fig_rev.add_trace(
        go.Scatter(
            x=df_7d["Date"],
            y=df_7d["AOV"],
            name="AOV (₹)",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2.5, shape="spline"),
            marker=dict(size=7, color="#F59E0B"),
        ),
        secondary_y=True,
    )
    fig_rev.update_layout(
        height=240,
        margin=dict(l=8, r=8, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    fig_rev.update_yaxes(
        range=[0, max(df_7d["Revenue"].max(), 1) * 1.28],
        showgrid=True,
        gridcolor="#F1F5F9",
        secondary_y=False,
    )
    fig_rev.update_yaxes(
        range=[0, max(df_7d["AOV"].max(), 1) * 1.35],
        showgrid=False,
        secondary_y=True,
    )
    st.plotly_chart(fig_rev, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>7D Revenue:</b> Gross'
        f" <b>₹{tot_7d_rev:,.0f}</b> · 7-Day Avg AOV:"
        f" <b>₹{avg_7d_aov:,.0f}</b>.</div></div>"
    )

  with s1_r:
    _html(f"""
        <div class="kpi-box" style="--accent:#10B981;">
            <div class="kpi-head"><span class="kpi-lbl">Total Dispatched Output ({selected_date.strftime('%d %b')})</span>{_pill(disp_diff, disp_prev_cnt)}</div>
            <div class="kpi-main-num">{disp_day_cnt:,}</div>
            <div class="kpi-foot">Prev Day ({prev_date.strftime('%d %b')}): <b>{disp_prev_cnt:,}</b> Dispatched</div>
        </div>
        """)
    st.plotly_chart(
        _spark(df_7d["Date"], df_7d["Dispatched"], "#10B981"),
        use_container_width=True,
    )

    _html(
        '<div class="viz-card"><div class="viz-heading">Dispatched Orders (7'
        " Days)</div>"
    )
    fig_dp = go.Figure(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Dispatched"],
            marker=dict(color="#10B981", cornerradius=5),
            text=[f"<b>{v}</b>" for v in df_7d["Dispatched"]],
            textposition="outside",
            textfont=dict(color="#065F46", size=11),
        )
    )
    fig_dp.update_layout(
        height=230,
        margin=dict(l=8, r=8, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["Dispatched"].max(), 1) * 1.28],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_dp, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>Dispatch Summary:</b> Total'
        f" <b>{tot_7d_disp:,}</b> dispatches in 7 days · Peak:"
        f' <b>{int(df_7d["Dispatched"].max()):,}</b> · Avg:'
        f" <b>{tot_7d_disp/7:.1f}/day</b>.</div></div>"
    )

    _html(
        '<div class="viz-card"><div class="viz-heading">Carrier-wise Daily'
        " Dispatch (Delhivery vs DTDC)</div>"
    )
    fig_car = go.Figure()
    fig_car.add_trace(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Delhivery"],
            name="Delhivery",
            marker=dict(color="#0EA5E9", cornerradius=4),
            text=df_7d["Delhivery"],
            textposition="inside",
        )
    )
    fig_car.add_trace(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["DTDC"],
            name="DTDC",
            marker=dict(color="#8B5CF6", cornerradius=4),
            text=df_7d["DTDC"],
            textposition="inside",
        )
    )
    fig_car.update_layout(
        barmode="stack",
        height=215,
        margin=dict(l=8, r=8, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_car, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>7D Carrier Parcels:</b> Delhivery:'
        f" <b>{tot_7d_delh:,}</b> | DTDC:"
        f" <b>{tot_7d_dtdc:,}</b>.</div></div>"
    )

  _html(
      '<div class="sec-bar">Section 2 — Undispatched Orders, Fulfilled, Daily'
      " RTO & Exchange (7 Days)</div>"
  )
  s2_1, s2_2, s2_3, s2_4 = st.columns(4)
  with s2_1:
    _html(
        '<div class="viz-card"><div class="viz-heading">Undispatched Orders'
        " (7D)</div>"
    )
    fig_bl = go.Figure(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Undispatched"],
            marker=dict(color="#F43F5E", cornerradius=5),
            text=[f"<b>{v}</b>" for v in df_7d["Undispatched"]],
            textposition="outside",
            textfont=dict(color="#9F1239", size=10.5),
        )
    )
    fig_bl.update_layout(
        height=210,
        margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["Undispatched"].max(), 1) * 1.32],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_bl, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>Total Undispatched (7D):</b>'
        f" <b>{tot_7d_undisp:,}</b></div></div>"
    )

  with s2_2:
    _html(
        '<div class="viz-card"><div class="viz-heading">Daily Fulfilled'
        " (7D)</div>"
    )
    fig_fl = go.Figure(
        go.Scatter(
            x=df_7d["Date"],
            y=df_7d["Fulfilled"],
            mode="lines+markers+text",
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.16)",
            line=dict(color="#7C3AED", width=2.5, shape="spline"),
            marker=dict(
                size=6, color="#FFFFFF", line=dict(color="#7C3AED", width=2)
            ),
            text=[f"<b>{v}</b>" for v in df_7d["Fulfilled"]],
            textposition="top center",
            textfont=dict(color="#5B21B6", size=10.5),
        )
    )
    fig_fl.update_layout(
        height=210,
        margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["Fulfilled"].max(), 1) * 1.35],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_fl, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>Total Fulfilled:</b>'
        f" <b>{tot_7d_ful:,}</b></div></div>"
    )

  with s2_3:
    _html('<div class="viz-card"><div class="viz-heading">Daily RTO (7D)</div>')
    fig_rto = go.Figure(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["RTO"],
            marker=dict(color="#EF4444", cornerradius=5),
            text=[f"<b>{v}</b>" for v in df_7d["RTO"]],
            textposition="outside",
            textfont=dict(color="#991B1B", size=10.5),
        )
    )
    fig_rto.update_layout(
        height=210,
        margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["RTO"].max(), 1) * 1.35],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_rto, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>7D RTO Count:</b>'
        f" <b>{tot_7d_rto:,}</b></div></div>"
    )

  with s2_4:
    _html(
        '<div class="viz-card"><div class="viz-heading">Daily Exchange'
        " (7D)</div>"
    )
    fig_ex = go.Figure(
        go.Bar(
            x=df_7d["Date"],
            y=df_7d["Exchange"],
            marker=dict(color="#8B5CF6", cornerradius=5),
            text=[f"<b>{v}</b>" for v in df_7d["Exchange"]],
            textposition="outside",
            textfont=dict(color="#5B21B6", size=10.5),
        )
    )
    fig_ex.update_layout(
        height=210,
        margin=dict(l=5, r=5, t=22, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(df_7d["Exchange"].max(), 1) * 1.35],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_ex, use_container_width=True)
    _html(
        f'<div class="viz-info"><b>7D Exchange Pickups:</b>'
        f" <b>{tot_7d_ex:,}</b></div></div>"
    )

  _html(
      '<div class="sec-bar">Section 3 — MOM RTO & Actionable Unfulfilled'
      " Orders</div>"
  )
  s3_1, s3_2 = st.columns([1.0, 1.6])
  with s3_1:
    _html(
        '<div class="viz-card"><div class="viz-heading">RTO Count Analysis'
        " MOM</div>"
    )
    rto_m = f_disp[rto_mask].copy()
    rto_m = rto_m[rto_m["Dispatch_Date_dt"].dt.date <= selected_date]
    rto_m["YM"] = rto_m["Dispatch_Date_dt"].dt.to_period("M")
    mom_s = rto_m.groupby("YM")["Base_Order_ID"].nunique().tail(5)
    m_lbls = [p.strftime("%b") for p in mom_s.index]
    m_vals = mom_s.values
    indigo_shades = ["#818CF8", "#6366F1", "#4F46E5", "#312E81", "#A5B4FC"][
        : len(m_vals)
    ]
    fig_mom = go.Figure(
        go.Bar(
            x=m_lbls,
            y=m_vals,
            marker=dict(color=indigo_shades, cornerradius=5),
            text=[f"<b>{v}</b>" for v in m_vals],
            textposition="outside",
            textfont=dict(size=10.5),
        )
    )
    fig_mom.update_layout(
        height=240,
        margin=dict(l=5, r=5, t=24, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            range=[0, max(list(m_vals) + [1]) * 1.28],
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
    )
    st.plotly_chart(fig_mom, use_container_width=True)
    peak_m_txt = (
        f"{m_lbls[int(np.argmax(m_vals))]} ({int(np.max(m_vals)):,})"
        if len(m_vals) > 0
        else "N/A"
    )
    _html(
        f'<div class="viz-info"><b>Peak Month:</b>'
        f" <b>{peak_m_txt}</b></div></div>"
    )

  with s3_2:
    _html(
        '<div class="viz-card"><div class="viz-heading">Actionable'
        f" Unfulfilled Orders ({latest_ym_val}:"
        f" {latest_month_unful_cnt})</div>"
    )
    show_cols = [
        c
        for c in [
            "Base_Order_ID",
            "Order_Date",
            "Customer_Name",
            "Financial_Status",
            "Fulfillment_Status",
            "Order_Total",
            "Order_Notes",
        ]
        if c in latest_month_unful_df.columns
    ]
    pending_view = latest_month_unful_df.sort_values(
        by="Order_Date_dt", ascending=False
    )[show_cols]
    _safe_dataframe(
        pending_view, use_container_width=True, height=235, hide_index=True
    )
    st.download_button(
        label="⬇️ Download Unfulfilled Orders CSV",
        data=pending_view.to_csv(index=False).encode("utf-8"),
        file_name=f"unfulfilled_{latest_ym_val}_{selected_date.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="dl_daily_unful",
    )
    _html("</div>")


# ==============================================================================
# 7. PAGE 2: SHOPIFY ANALYSIS
# ==============================================================================
def render_shopify_page():
  if model_src is None:
    st.warning(
        f"Model file `{MODEL_FILENAME}` was not found in GitHub or local"
        " folders."
    )
    return

  df_orders, df_disp, df_rev = load_model_excel(model_src)
  valid_order_dates = df_orders["Order_Date_dt"].dropna()
  if valid_order_dates.empty:
    st.error("No valid dates found in Order_Date.")
    return

  min_d = valid_order_dates.min().date()
  max_d = valid_order_dates.max().date()

  f_c1, f_c2, f_c3 = st.columns([1.2, 1.0, 1.0])
  with f_c1:
    preset = st.selectbox(
        "📅 Quick Date Preset",
        [
            "Custom Dates",
            "01 Oct – 05 Nov 2026",
            "01 Sep – 14 Sep 2026",
            "All Available Dates",
        ],
        index=0,
        key="shp_preset",
    )
  if preset == "01 Sep – 14 Sep 2026":
    init_start = min(max(datetime.date(2026, 9, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 9, 14), max_d), min_d)
  elif preset == "All Available Dates":
    init_start, init_end = min_d, max_d
  else:
    init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 11, 5), max_d), min_d)

  with f_c2:
    start_date = st.date_input(
        "📅 Start Date",
        value=init_start,
        min_value=min_d,
        max_value=max_d,
        key="shp_start_date",
    )
  with f_c3:
    end_date = st.date_input(
        "📅 End Date",
        value=init_end,
        min_value=min_d,
        max_value=max_d,
        key="shp_end_date",
    )

  if start_date > end_date:
    st.error("Start Date must be on or before End Date.")
    return

  _html(f"""
    <div class="exec-banner">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Shopify Analysis</div>
                <div class="exec-sub">Pure RTO & Cancelled Exchange Returns, Financial KPIs & Day-Wise Trends</div>
            </div>
        </div>
        <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
    </div>
    """)

  p_orders = df_orders[
      (df_orders["Order_Date_dt"].dt.date >= start_date)
      & (df_orders["Order_Date_dt"].dt.date <= end_date)
  ].copy()

  fin_status_col = _find_col(p_orders, ["Financial_Status"])
  if fin_status_col:
    p_orders = p_orders[
        p_orders[fin_status_col].fillna("").astype(str).str.strip().str.lower()
        != "voided"
    ].copy()

  base_oid_col = _find_col(p_orders, ["Base_Order_ID", "Order_ID", "Name"])
  period_ids = set(p_orders[base_oid_col].dropna()) if base_oid_col else set()

  disp_base_col = _find_col(df_disp, ["Base_Order_ID", "Order_ID"])
  p_disp = (
      df_disp[df_disp[disp_base_col].isin(period_ids)].copy()
      if (not df_disp.empty and disp_base_col)
      else pd.DataFrame()
  )

  if not p_disp.empty and base_oid_col:
    merge_cols = [
        c
        for c in [
            base_oid_col,
            "Order_Date",
            "Order_Date_dt",
            "Payment_Category",
            "Order_Total",
            "Order_Notes",
            "Customer_Name",
        ]
        if c in p_orders.columns
    ]
    p_disp = p_disp.merge(
        p_orders[merge_cols].drop_duplicates(subset=[base_oid_col]),
        left_on=disp_base_col,
        right_on=base_oid_col,
        how="left",
    )

    status_col_d = _find_col(p_disp, ["Shipment_Status", "Status"])
    status_u = (
        p_disp[status_col_d].fillna("").astype(str).str.strip().str.upper()
        if status_col_d
        else pd.Series([""] * len(p_disp))
    )
    del_col_d = _find_col(p_disp, ["Delivered_Date"])
    has_del = (
        (
            p_disp[del_col_d].notna()
            & (p_disp[del_col_d].astype(str).str.strip() != "")
        )
        if del_col_d
        else pd.Series([False] * len(p_disp))
    )
    is_rto = (
        p_disp["Is_RTO"].astype(bool)
        if "Is_RTO" in p_disp.columns
        else pd.Series([False] * len(p_disp))
    )
    is_del = (
        p_disp["Is_Delivered"].astype(bool)
        if "Is_Delivered" in p_disp.columns
        else pd.Series([False] * len(p_disp))
    )
    is_bad = status_u.isin(["CANCELLED", "CANCELED", "LOST"])

    p_disp["True_Delivered"] = (
        (
            is_del
            | (
                status_u.isin(["SHIPPED", "PROCESSING", "OUT_FOR_DELIVERY"])
                & has_del
            )
        )
        & (~is_rto)
        & (~is_bad)
    )
    p_disp["True_In_Transit"] = (
        (~p_disp["True_Delivered"])
        & (~is_rto)
        & (~is_bad)
        & (status_u != "UNDELIVERED")
    )

    received_hub_tokens = {
        "RTO DELIVERED",
        "RTO_DELIVERED",
        "DELIVERED TO HUB",
        "RECEIVED AT HUB",
        "RETURN DELIVERED",
        "RET DELIVERED",
        "RTO RECEIVED",
    }
    p_disp["RTO_Pending_Hub"] = (
        is_rto & (~has_del) & (~status_u.isin(received_hub_tokens))
    )
  else:
    if not p_disp.empty:
      p_disp["True_Delivered"] = False
      p_disp["True_In_Transit"] = False
      p_disp["RTO_Pending_Hub"] = False

  dispatched_ids = (
      set(p_disp[disp_base_col].dropna())
      if (not p_disp.empty and disp_base_col)
      else set()
  )
  not_dispatched = (
      p_orders[~p_orders[base_oid_col].isin(dispatched_ids)].copy()
      if base_oid_col
      else pd.DataFrame()
  )

  del_oids = (
      set(p_disp[p_disp["True_Delivered"]][disp_base_col].dropna())
      if (not p_disp.empty and disp_base_col)
      else set()
  )
  rto_all_oids = (
      set(p_disp[p_disp["Is_RTO"]][disp_base_col].dropna())
      if (not p_disp.empty and disp_base_col)
      else set()
  )
  rto_oids = rto_all_oids - del_oids

  rto_pending_hub_df = (
      p_disp[p_disp["RTO_Pending_Hub"]].copy()
      if not p_disp.empty
      else pd.DataFrame()
  )
  rto_pending_hub_oids = (
      set(rto_pending_hub_df[disp_base_col].dropna())
      if (not rto_pending_hub_df.empty and disp_base_col)
      else set()
  )
  int_oids = (
      (
          set(p_disp[p_disp["True_In_Transit"]][disp_base_col].dropna())
          - del_oids
          - rto_oids
      )
      if (not p_disp.empty and disp_base_col)
      else set()
  )

  rev_base_col = (
      _find_col(df_rev, ["Base_Order_ID", "Order_ID"])
      if not df_rev.empty
      else None
  )
  rev_order_id_col = (
      _find_col(df_rev, ["Order_ID", "Base_Order_ID"])
      if not df_rev.empty
      else None
  )
  rev_status_col = (
      _find_col(
          df_rev, ["Reverse_Status", "Return_Status", "Exchange_Status", "Status"]
      )
      if not df_rev.empty
      else None
  )

  if not df_rev.empty and rev_base_col:
    p_rev_all = df_rev[df_rev[rev_base_col].isin(period_ids)].copy()
    if rev_status_col:
      rev_st_upper = (
          p_rev_all[rev_status_col].fillna("").astype(str).str.strip().str.upper()
      )
      p_rev_active = p_rev_all[rev_st_upper != "CANCELLED"].copy()
      p_rev_cancelled = p_rev_all[rev_st_upper == "CANCELLED"].copy()
    else:
      p_rev_active = p_rev_all.copy()
      p_rev_cancelled = pd.DataFrame(columns=p_rev_all.columns)
  else:
    p_rev_all = pd.DataFrame()
    p_rev_active = pd.DataFrame()
    p_rev_cancelled = pd.DataFrame()

  if not p_orders.empty and base_oid_col:
    p_orders_uniq = p_orders.drop_duplicates(subset=[base_oid_col]).copy()
    tot_ord = int(p_orders[base_oid_col].nunique())
  else:
    p_orders_uniq = p_orders.copy()
    tot_ord = len(p_orders)

  gross_rev = (
      float(p_orders_uniq["Order_Total"].sum())
      if (len(p_orders_uniq) > 0 and "Order_Total" in p_orders_uniq.columns)
      else 0.0
  )
  tot_disc = (
      float(p_orders_uniq["Discount"].sum())
      if ("Discount" in p_orders_uniq.columns and len(p_orders_uniq) > 0)
      else 0.0
  )
  tot_ship = (
      float(p_orders_uniq["Shipping"].sum())
      if ("Shipping" in p_orders_uniq.columns and len(p_orders_uniq) > 0)
      else 0.0
  )

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
  canc_exch_order_ids_set = (
      set(p_rev_cancelled[rev_base_col].dropna())
      if (not p_rev_cancelled.empty and rev_base_col)
      else set()
  )
  all_affected_ret_oids = rto_order_ids_set.union(canc_exch_order_ids_set)

  tot_ret_amt = (
      float(
          p_orders_uniq[p_orders_uniq[base_oid_col].isin(all_affected_ret_oids)][
              "Order_Total"
          ].sum()
      )
      if (len(p_orders_uniq) > 0 and base_oid_col)
      else 0.0
  )
  net_rev = max(gross_rev - tot_ret_amt, 0.0)
  realized_deliv_rev = (
      float(
          p_orders_uniq[p_orders_uniq[base_oid_col].isin(del_oids)][
              "Order_Total"
          ].sum()
      )
      if (len(p_orders_uniq) > 0 and base_oid_col)
      else 0.0
  )

  aov = gross_rev / tot_ord if tot_ord > 0 else 0.0
  deliv_cnt = len(del_oids)
  deliv_pct = (deliv_cnt / disp_cnt * 100) if disp_cnt > 0 else 0.0

  rto_hub_parcels = int(p_disp["RTO_Pending_Hub"].sum()) if not p_disp.empty else 0
  rto_hub_orders = len(rto_pending_hub_oids)

  k1, k2, k3, k4, k5 = st.columns(5)
  with k1:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Orders</div>
                <div class="kpi-val">{tot_ord:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{int(p_orders_uniq['Total_Line_Items'].sum()) if ('Total_Line_Items' in p_orders_uniq.columns and len(p_orders_uniq)>0) else 0:,} Items</span>
            </div>
            <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
        </div>
        """)
  with k2:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Gross Revenue</div>
                <div class="kpi-val">₹{gross_rev:,.2f}</div>
                <span class="kpi-tag" style="background:#F5F3FF; color:#7C3AED;">AOV: ₹{aov:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#F5F3FF;">💰</div>
        </div>
        """)
  with k3:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Net Revenue</div>
                <div class="kpi-val">₹{net_rev:,.2f}</div>
                <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Delivered: ₹{realized_deliv_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#ECFDF5;">📈</div>
        </div>
        """)
  with k4:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Total Discount</div>
                <div class="kpi-val">₹{tot_disc:,.2f}</div>
                <span class="kpi-tag" style="background:#FDF2F8; color:#BE185D;">{tot_disc/max(gross_rev+tot_disc,1)*100:.1f}% Disc. Share</span>
            </div>
            <div class="kpi-ico" style="background:#FDF2F8;">🏷️</div>
        </div>
        """)
  with k5:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Total Shipping Cost</div>
                <div class="kpi-val">₹{tot_ship:,.2f}</div>
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">Avg: ₹{tot_ship/max(tot_ord,1):,.1f}/Order</span>
            </div>
            <div class="kpi-ico" style="background:#ECFEFF;">🚢</div>
        </div>
        """)

  st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

  f1, f2, f3, f4, f5 = st.columns(5)
  with f1:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Dispatched</div>
                <div class="kpi-val">{disp_cnt:,}</div>
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">{disp_cnt/max(tot_ord,1)*100:.1f}% of Orders</span>
            </div>
            <div class="kpi-ico" style="background:#ECFEFF;">📦</div>
        </div>
        """)
  with f2:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Delivered</div>
                <div class="kpi-val">{deliv_cnt:,}</div>
                <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">▲ {deliv_pct:.1f}% Success</span>
            </div>
            <div class="kpi-ico" style="background:#ECFDF5;">🚚</div>
        </div>
        """)
  with f3:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Total Returns Display</div>
                <div class="kpi-val">{tot_ret_cnt:,} ({tot_ret_pct:.2f}%)</div>
                <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO {pure_rto_cnt:,} + Exch Canc {canc_exch_cnt:,}</span>
            </div>
            <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>
        """)
  with f4:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Pure RTO / Exch Canc</div>
                <div class="kpi-val">{pure_rto_cnt:,} / {canc_exch_cnt:,}</div>
                <span class="kpi-tag" style="background:#FFF1F2; color:#BE123C;">Active Exch: {exch_cnt:,}</span>
            </div>
            <div class="kpi-ico" style="background:#FFF1F2;">🔄</div>
        </div>
        """)
  with f5:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">RTO Pending Hub</div>
                <div class="kpi-val">{rto_hub_parcels:,}</div>
                <span class="kpi-tag" style="background:#FFF7ED; color:#C2410C;">{rto_hub_orders:,} Unique Orders</span>
            </div>
            <div class="kpi-ico" style="background:#FFF7ED;">🏭</div>
        </div>
        """)

  st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

  if p_orders.empty:
    st.info(
        "No orders found between"
        f" {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}."
    )
    return

  tab1, tab2, tab3, tab4 = st.tabs([
      "📈 Overview & Funnel",
      "↩️ RTO & Exchange Analysis",
      "👗 Top Products & Age Groups",
      "📋 Actionable Tables",
  ])

  with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
      _html(
          '<div class="card-box"><div class="card-title">📊 Daily Unique'
          " Orders & Revenue Trend</div>"
      )
      p_orders_uniq["Order_Date_Only"] = p_orders_uniq["Order_Date_dt"].dt.date
      daily = (
          p_orders_uniq.groupby("Order_Date_Only")
          .agg(Orders=(base_oid_col, "nunique"), Revenue=("Order_Total", "sum"))
          .reset_index()
          .sort_values("Order_Date_Only")
      )
      daily["Date_Label"] = pd.to_datetime(daily["Order_Date_Only"]).dt.strftime(
          "%d %b"
      )
      daily["Rev_Lakhs"] = (daily["Revenue"] / 1e5).round(2)
      daily["AOV"] = np.where(
          daily["Orders"] > 0, daily["Revenue"] / daily["Orders"], 0.0
      )
      daily["Custom_Hover"] = [
          f"₹{rev:,.2f} (₹{rev/1e5:.2f}L) | AOV: ₹{aov_v:,.0f}"
          for rev, aov_v in zip(daily["Revenue"], daily["AOV"])
      ]

      fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
      fig_dual.add_trace(
          go.Bar(
              x=daily["Date_Label"],
              y=daily["Orders"],
              name="Unique Orders",
              marker=dict(color="#6366F1", cornerradius=6),
              opacity=0.85,
              text=daily["Orders"],
              textposition="outside",
              cliponaxis=False,
              textfont=dict(
                  size=10, color="#312E81", family="Plus Jakarta Sans"
              ),
              hovertemplate=(
                  "<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>"
              ),
          ),
          secondary_y=False,
      )
      fig_dual.add_trace(
          go.Scatter(
              x=daily["Date_Label"],
              y=daily["Rev_Lakhs"],
              name="Revenue (₹ Lakhs)",
              mode="lines+markers",
              line=dict(color="#EC4899", width=3, shape="spline"),
              marker=dict(
                  size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")
              ),
              customdata=daily["Custom_Hover"],
              hovertemplate="Revenue: %{customdata}<extra></extra>",
          ),
          secondary_y=True,
      )
      max_ord_y = (
          max(float(daily["Orders"].max()) * 1.28, 5.0)
          if not daily.empty
          else 10.0
      )
      max_rev_y = (
          max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5)
          if not daily.empty
          else 1.0
      )
      fig_dual.update_layout(
          height=410,
          margin=dict(l=15, r=15, t=40, b=60),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          hovermode="x unified",
          bargap=0.28,
          legend=dict(
              orientation="h",
              yanchor="bottom",
              y=1.04,
              xanchor="right",
              x=1,
              font=dict(size=12),
          ),
          font=dict(family="Plus Jakarta Sans", color="#334155"),
      )
      fig_dual.update_xaxes(
          tickangle=-45,
          tickfont=dict(size=11, color="#475569"),
          nticks=18,
          showgrid=False,
      )
      fig_dual.update_yaxes(
          title_text="Unique Orders",
          range=[0, max_ord_y],
          showgrid=True,
          gridcolor="#F1F5F9",
          zeroline=False,
          secondary_y=False,
      )
      fig_dual.update_yaxes(
          title_text="Revenue (₹ Lakhs)",
          range=[0, max_rev_y],
          showgrid=False,
          zeroline=False,
          secondary_y=True,
      )
      st.plotly_chart(fig_dual, use_container_width=True)

      _html(
          '<div style="font-size:13px; font-weight:700; color:#334155;'
          ' margin-top:10px; margin-bottom:6px;">📋 Day-Wise Orders &'
          " Revenue Verification</div>"
      )
      d_verify = (
          p_orders_uniq.groupby("Order_Date_Only")
          .agg(
              Unique_Orders=(base_oid_col, "nunique"),
              Revenue_INR=("Order_Total", "sum"),
              Discount_INR=(
                  ("Discount", "sum")
                  if "Discount" in p_orders_uniq.columns
                  else ("Order_Total", lambda s: 0.0)
              ),
              Shipping_INR=(
                  ("Shipping", "sum")
                  if "Shipping" in p_orders_uniq.columns
                  else ("Order_Total", lambda s: 0.0)
              ),
          )
          .reset_index()
          .sort_values("Order_Date_Only")
      )
      d_verify["Date"] = pd.to_datetime(d_verify["Order_Date_Only"]).dt.strftime(
          "%d %b %Y"
      )
      d_verify["AOV_INR"] = np.where(
          d_verify["Unique_Orders"] > 0,
          (d_verify["Revenue_INR"] / d_verify["Unique_Orders"]).round(0),
          0,
      )
      d_verify["Revenue_INR"] = d_verify["Revenue_INR"].round(2)
      d_verify["Discount_INR"] = d_verify["Discount_INR"].round(2)
      d_verify["Shipping_INR"] = d_verify["Shipping_INR"].round(2)
      _safe_dataframe(
          d_verify[[
              "Date",
              "Unique_Orders",
              "Revenue_INR",
              "AOV_INR",
              "Discount_INR",
              "Shipping_INR",
          ]],
          use_container_width=True,
          height=210,
          hide_index=True,
      )
      _html("</div>")

    with c_right:
      _html(
          '<div class="card-box"><div class="card-title">🎯 Order-to-Delivery'
          " Funnel (Unique Orders)</div>"
      )
      funnel_labels = [
          "Orders Created",
          "Dispatched",
          "True Delivered",
          "Pure RTO Orders",
          "Exch Cancelled",
          "RTO Pending Hub",
          "In-Transit",
          "Not Dispatched",
      ]
      funnel_vals = [
          tot_ord,
          disp_cnt,
          deliv_cnt,
          pure_rto_cnt,
          canc_exch_cnt,
          rto_hub_orders,
          len(int_oids),
          len(not_dispatched),
      ]
      funnel_colors = [
          "#4F46E5",
          "#0EA5E9",
          "#10B981",
          "#EF4444",
          "#E11D48",
          "#EA580C",
          "#F59E0B",
          "#94A3B8",
      ]
      fig_fun = go.Figure(
          go.Bar(
              y=funnel_labels[::-1],
              x=funnel_vals[::-1],
              orientation="h",
              marker=dict(color=funnel_colors[::-1], cornerradius=8),
              text=[f"<b>{v:,}</b>" for v in funnel_vals[::-1]],
              textposition="outside",
              cliponaxis=False,
              textfont=dict(size=12, color="#0F172A"),
          )
      )
      fig_fun.update_layout(
          height=410,
          margin=dict(l=10, r=60, t=20, b=20),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(
              showgrid=True,
              gridcolor="#F1F5F9",
              zeroline=False,
              range=[0, max(funnel_vals + [1]) * 1.22],
          ),
          yaxis=dict(showgrid=False, tickfont=dict(size=12)),
          font=dict(family="Plus Jakarta Sans", color="#334155"),
      )
      st.plotly_chart(fig_fun, use_container_width=True)
      _html("</div>")

  with tab2:
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
      _html(
          '<div class="sub-kpi"><div><div class="sub-kpi-lbl">Total Returns'
          f' Display</div><div class="sub-kpi-val">{tot_ret_cnt:,}'
          f' ({tot_ret_pct:.2f}%)</div></div><div class="sub-kpi-ico"'
          ' style="background:#FEF2F2;">↩️</div></div>'
      )
    with m2:
      _html(
          '<div class="sub-kpi"><div><div class="sub-kpi-lbl">Total Return'
          f' Amount</div><div class="sub-kpi-val">₹{tot_ret_amt:,.2f}</div></div><div'
          ' class="sub-kpi-ico" style="background:#FFF1F2;">💸</div></div>'
      )
    with m3:
      _html(
          '<div class="sub-kpi"><div><div class="sub-kpi-lbl">Pure RTO'
          f' Orders</div><div class="sub-kpi-val">{pure_rto_cnt:,}</div></div><div'
          ' class="sub-kpi-ico" style="background:#FFEDD5;">🚚</div></div>'
      )
    with m4:
      _html(
          '<div class="sub-kpi"><div><div class="sub-kpi-lbl">Exchanged'
          f' Cancelled</div><div class="sub-kpi-val">{canc_exch_cnt:,}</div></div><div'
          ' class="sub-kpi-ico" style="background:#FCE7F3;">❌</div></div>'
      )
    with m5:
      _html(
          '<div class="sub-kpi"><div><div class="sub-kpi-lbl">Active Exchange'
          f' Orders</div><div class="sub-kpi-val">{exch_cnt:,}</div></div><div'
          ' class="sub-kpi-ico" style="background:#F3E8FF;">🔄</div></div>'
      )

    _html(f"""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: Pure RTO Analysis (Pure RTO: {pure_rto_cnt:,} | Cancelled Exchanges: {canc_exch_cnt:,} | Total Returns: {tot_ret_cnt:,})</div>
            <div class="sec-sub">RTO Status Breakdown & Day-Wise RTO Orders Trend</div>
        </div>
        """)

    rto_df = (
        p_disp[p_disp["Is_RTO"]].copy()
        if (not p_disp.empty and "Is_RTO" in p_disp.columns)
        else pd.DataFrame()
    )
    rto_c1, rto_c2 = st.columns([1.05, 1.45])
    with rto_c1:
      _html(
          '<div class="card-box"><div class="card-title">🍩 RTO Status'
          " Breakdown (Donut)</div>"
      )
      if not rto_df.empty and disp_base_col:
        st_col_rto = _find_col(rto_df, ["Shipment_Status", "Status"])
        if st_col_rto:
          rto_st_agg = (
              rto_df.groupby(
                  rto_df[st_col_rto].fillna("RTO").astype(str).str.strip()
              )[disp_base_col]
              .nunique()
              .reset_index(name="Count")
          )
          rto_st_agg.columns = ["Status", "Count"]
        else:
          rto_st_agg = pd.DataFrame({
              "Status": ["RTO Pending Hub", "RTO Received Hub"],
              "Count": [rto_hub_orders, max(pure_rto_cnt - rto_hub_orders, 0)],
          })
        rto_st_agg = rto_st_agg[rto_st_agg["Count"] > 0]
        st.plotly_chart(
            _make_donut_fig(
                rto_st_agg["Status"].tolist(),
                rto_st_agg["Count"].tolist(),
                ["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6", "#10B981"],
                f"<b>{pure_rto_cnt:,}</b><br>Pure RTO",
            ),
            use_container_width=True,
        )
      else:
        st.info("No RTO orders in selected period.")
      _html("</div>")

    with rto_c2:
      _html(
          '<div class="card-box"><div class="card-title">📅 Day-Wise RTO Orders'
          " Analysis</div>"
      )
      if (
          not rto_df.empty
          and "Order_Date_dt" in rto_df.columns
          and disp_base_col
      ):
        d_rto = (
            rto_df.groupby(rto_df["Order_Date_dt"].dt.date)[disp_base_col]
            .nunique()
            .reset_index(name="RTO_Count")
            .sort_values("Order_Date_dt")
        )
        d_rto["Date_Lbl"] = pd.to_datetime(d_rto["Order_Date_dt"]).dt.strftime(
            "%d %b"
        )
        fig_d_rto = go.Figure()
        fig_d_rto.add_trace(
            go.Bar(
                x=d_rto["Date_Lbl"],
                y=d_rto["RTO_Count"],
                name="Day-Wise RTO",
                marker=dict(color="#FB923C", cornerradius=6),
                text=d_rto["RTO_Count"],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_d_rto.add_trace(
            go.Scatter(
                x=d_rto["Date_Lbl"],
                y=d_rto["RTO_Count"],
                name="Trend",
                mode="lines+markers",
                line=dict(color="#EA580C", width=2.5, shape="spline"),
            )
        )
        fig_d_rto.update_layout(
            height=370,
            margin=dict(l=15, r=15, t=25, b=55),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(tickangle=-45, nticks=18, showgrid=False),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                range=[0, max(float(d_rto["RTO_Count"].max()) * 1.32, 3.0)],
            ),
        )
        st.plotly_chart(fig_d_rto, use_container_width=True)
      else:
        st.info("No day-wise RTO data.")
      _html("</div>")

    _html(f"""
        <div class="sec-header-exch">
            <div class="sec-title">🔄 Section 2: Exchange Analysis (Active Exchanges: {exch_cnt:,} | Exchanged Cancelled: {canc_exch_cnt:,})</div>
            <div class="sec-sub">Exchanged Status by Reverse_Status & Day-Wise Exchange Orders</div>
        </div>
        """)

    ex_c1, ex_c2 = st.columns([1.05, 1.45])
    with ex_c1:
      _html(
          '<div class="card-box"><div class="card-title">🍩 Exchange Status'
          " by Reverse_Status (Donut)</div>"
      )
      if not p_rev_all.empty:
        id_for_cnt = rev_order_id_col if rev_order_id_col else rev_base_col
        if rev_status_col and id_for_cnt:
          ex_st_df = (
              p_rev_all.groupby(
                  p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip()
              )[id_for_cnt]
              .nunique()
              .reset_index(name="Count")
          )
          ex_st_df.columns = ["Reverse_Status", "Count"]
        elif rev_status_col:
          ex_st_df = (
              p_rev_all.groupby(
                  p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip()
              )
              .size()
              .reset_index(name="Count")
          )
          ex_st_df.columns = ["Reverse_Status", "Count"]
        else:
          ex_st_df = pd.DataFrame(
              {"Reverse_Status": ["Recorded"], "Count": [len(p_rev_all)]}
          )
        ex_st_df = ex_st_df[ex_st_df["Count"] > 0]
        st.plotly_chart(
            _make_donut_fig(
                ex_st_df["Reverse_Status"].tolist(),
                ex_st_df["Count"].tolist(),
                ["#10B981", "#8B5CF6", "#F59E0B", "#0EA5E9", "#EF4444", "#EC4899"],
                f"<b>{int(ex_st_df['Count'].sum()):,}</b><br>Total Exch",
            ),
            use_container_width=True,
        )
      else:
        st.info(
            "No Exchange records in Fact_Reverse_Logistics for selected period."
        )
      _html("</div>")

    with ex_c2:
      _html(
          '<div class="card-box"><div class="card-title">📅 Day-Wise Exchange'
          " Orders Analysis (Non-Cancelled)</div>"
      )
      if not p_rev_active.empty and rev_base_col:
        rev_d = p_rev_active.merge(
            p_orders_uniq[[base_oid_col, "Order_Date_dt"]],
            left_on=rev_base_col,
            right_on=base_oid_col,
            how="left",
        )
        id_for_day = (
            rev_order_id_col
            if (rev_order_id_col and rev_order_id_col in rev_d.columns)
            else rev_base_col
        )
        if "Order_Date_dt" in rev_d.columns and rev_d["Order_Date_dt"].notna().any():
          d_ex = (
              rev_d.groupby(rev_d["Order_Date_dt"].dt.date)[id_for_day]
              .nunique()
              .reset_index(name="Exchange_Count")
              .sort_values("Order_Date_dt")
          )
          d_ex["Date_Lbl"] = pd.to_datetime(d_ex["Order_Date_dt"]).dt.strftime(
              "%d %b"
          )
          fig_d_ex = go.Figure()
          fig_d_ex.add_trace(
              go.Bar(
                  x=d_ex["Date_Lbl"],
                  y=d_ex["Exchange_Count"],
                  name="Day-Wise Exchanges",
                  marker=dict(color="#A855F7", cornerradius=6),
                  text=d_ex["Exchange_Count"],
                  textposition="outside",
                  cliponaxis=False,
              )
          )
          fig_d_ex.add_trace(
              go.Scatter(
                  x=d_ex["Date_Lbl"],
                  y=d_ex["Exchange_Count"],
                  name="Trend",
                  mode="lines+markers",
                  line=dict(color="#7C3AED", width=2.5, shape="spline"),
              )
          )
          fig_d_ex.update_layout(
              height=370,
              margin=dict(l=15, r=15, t=25, b=55),
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              showlegend=False,
              xaxis=dict(tickangle=-45, nticks=18, showgrid=False),
              yaxis=dict(
                  showgrid=True,
                  gridcolor="#F1F5F9",
                  range=[0, max(float(d_ex["Exchange_Count"].max()) * 1.32, 3.0)],
              ),
          )
          st.plotly_chart(fig_d_ex, use_container_width=True)
        else:
          st.info("No dated exchange records in selected period.")
      else:
        st.info("No day-wise exchange data in selected period.")
      _html("</div>")

    st.markdown(
        "#### 🔄 Exchanges Detail (Fact_Reverse_Logistics — Active:"
        f" {exch_cnt:,} | Cancelled: {canc_exch_cnt:,})"
    )
    if not p_rev_all.empty:
      _safe_dataframe(
          p_rev_all, use_container_width=True, height=250, hide_index=True
      )
      st.download_button(
          "⬇️ Download Exchanges CSV",
          p_rev_all.to_csv(index=False).encode("utf-8"),
          f"exchanges_{start_date}_{end_date}.csv",
          "text/csv",
          key="dl_shp_exch",
      )
    else:
      st.info(
          "No Exchange records found for the selected created orders window."
      )

  with tab3:
    p1, p2 = st.columns([1.2, 1])
    with p1:
      _html(
          '<div class="card-box"><div class="card-title">🏆 Top 7 Bestselling'
          " Delivered Products</div>"
      )
      prod_col = (
          _find_col(p_disp, ["Clean_Product_Name", "Product_Name", "Title"])
          if not p_disp.empty
          else None
      )
      if not p_disp.empty and prod_col:
        prod_s = (
            p_disp[p_disp["True_Delivered"]][prod_col]
            .dropna()
            .astype(str)
            .str.strip()
        )
        prod_s = prod_s[
            ~prod_s.str.lower().isin([
                "",
                "nan",
                "none",
                "garment item",
                "manual dispatch item",
                "dresses",
                "standard",
            ])
        ]
        top_p = prod_s.value_counts().head(7)
        if not top_p.empty:
          mv = top_p.max()
          for rank, (name, cnt) in enumerate(top_p.items(), start=1):
            pct = cnt / mv * 100
            short = name if len(name) <= 44 else name[:44] + "..."
            _html(
                f'<div class="prod-row"><div class="prod-meta"><span>#{rank}'
                f' &nbsp;{short}</span><span style="color:#DB2777;">{cnt:,}'
                ' pcs</span></div><div class="prod-track"><div'
                f' class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>'
            )
      _html("</div>")

    with p2:
      _html(
          '<div class="card-box"><div class="card-title">👶 Top Kids Age'
          " Groups (Delivered)</div>"
      )
      age_col = (
          _find_col(p_disp, ["Product_Age_Group", "Age_Group", "Size"])
          if not p_disp.empty
          else None
      )
      if not p_disp.empty and age_col:
        age_s = (
            p_disp[p_disp["True_Delivered"]][age_col]
            .dropna()
            .astype(str)
            .str.strip()
        )
        age_s = age_s[
            ~age_s.str.lower().isin(["", "nan", "none", "standard / free size"])
        ]
        top_a = age_s.value_counts().head(7).reset_index()
        top_a.columns = ["Age Group", "Count"]
        if not top_a.empty:
          fig_age = go.Figure(
              go.Bar(
                  x=top_a["Age Group"],
                  y=top_a["Count"],
                  marker=dict(color="#8B5CF6", cornerradius=8),
                  text=top_a["Count"],
                  textposition="outside",
                  cliponaxis=False,
              )
          )
          fig_age.update_layout(
              height=310,
              margin=dict(l=10, r=10, t=25, b=10),
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              yaxis=dict(
                  showgrid=True,
                  gridcolor="#F1F5F9",
                  range=[0, max(float(top_a["Count"].max()) * 1.25, 3.0)],
              ),
          )
          st.plotly_chart(fig_age, use_container_width=True)
      _html("</div>")

  with tab4:
    st.markdown(
        f"#### 🏭 RTO Pending to Hub ({rto_hub_parcels} Parcels /"
        f" {rto_hub_orders} Unique Orders)"
    )
    hub_cols = [
        c
        for c in [
            "Order_ID",
            "Base_Order_ID",
            "Order_Date",
            "Dispatch_Date",
            "Carrier",
            "Tracking_Number",
            "Shipment_Status",
            "Order_Total",
            "Order_Notes",
        ]
        if c in rto_pending_hub_df.columns
    ]
    hub_view = (
        rto_pending_hub_df[hub_cols]
        if not rto_pending_hub_df.empty
        else pd.DataFrame(columns=hub_cols)
    )
    _safe_dataframe(
        hub_view, use_container_width=True, height=280, hide_index=True
    )
    st.download_button(
        "⬇️ Download RTO Pending Hub CSV",
        hub_view.to_csv(index=False).encode("utf-8"),
        "rto_pending_hub.csv",
        "text/csv",
        key="dl_shp_hub",
    )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2)
    with t_col1:
      st.markdown(
          "#### 🚚 Truly In-Transit Parcels"
          f" ({int(p_disp['True_In_Transit'].sum()) if (not p_disp.empty and 'True_In_Transit' in p_disp.columns) else 0})"
      )
      it_cols = [
          c
          for c in [
              "Order_ID",
              "Base_Order_ID",
              "Order_Date",
              "Dispatch_Date",
              "Carrier",
              "Shipment_Status",
              "Order_Total",
              "Order_Notes",
          ]
          if c in p_disp.columns
      ]
      it_view = (
          p_disp[p_disp["True_In_Transit"]][it_cols]
          if (not p_disp.empty and "True_In_Transit" in p_disp.columns)
          else pd.DataFrame(columns=it_cols)
      )
      _safe_dataframe(
          it_view, use_container_width=True, height=340, hide_index=True
      )
      st.download_button(
          "⬇️ Download In-Transit CSV",
          it_view.to_csv(index=False).encode("utf-8"),
          "in_transit.csv",
          "text/csv",
          key="dl_shp_it",
      )

    with t_col2:
      st.markdown(f"#### ⏳ Not Dispatched Orders ({len(not_dispatched)})")
      nd_cols = [
          c
          for c in [
              base_oid_col,
              "Order_Date",
              "Financial_Status",
              "Fulfillment_Status",
              "Order_Total",
              "Order_Notes",
          ]
          if c and c in not_dispatched.columns
      ]
      nd_view = (
          not_dispatched[nd_cols]
          if not not_dispatched.empty
          else pd.DataFrame(columns=nd_cols)
      )
      _safe_dataframe(
          nd_view, use_container_width=True, height=340, hide_index=True
      )
      st.download_button(
          "⬇️ Download Not-Dispatched CSV",
          nd_view.to_csv(index=False).encode("utf-8"),
          "not_dispatched.csv",
          "text/csv",
          key="dl_shp_nd",
      )


# ==============================================================================
# 8. PAGE 3: MYNTRA ANALYSIS (Myntra_Consolidated_Orders.xlsx)
# ==============================================================================
def render_myntra_page():
  df_all, _ = load_myntra_data(myntra_src)
  if df_all.empty:
    st.warning(
        f"File `{MYNTRA_CONSOLIDATED_NAME}` was not found in GitHub or upload"
        " panel."
    )
    return

  valid_dates = df_all["order_date_dt"].dropna()
  if valid_dates.empty:
    st.error("No valid dates found in order_date.")
    return

  min_d = valid_dates.min().date()
  max_d = valid_dates.max().date()

  f1, f2, f3, f4 = st.columns([1.1, 1.0, 1.0, 1.4])
  with f1:
    preset = st.selectbox(
        "📅 Quick Date Preset",
        [
            "All Available Dates",
            "01 Oct – 05 Nov 2026",
            "01 Jul – 30 Nov 2026",
            "Custom Dates",
        ],
        index=0,
        key="myn_preset",
    )
  if preset == "01 Oct – 05 Nov 2026":
    init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 11, 5), max_d), min_d)
  elif preset == "01 Jul – 30 Nov 2026":
    init_start = min(max(datetime.date(2026, 7, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 11, 30), max_d), min_d)
  else:
    init_start, init_end = min_d, max_d

  all_comb_statuses = sorted(df_all["Combined_Status"].unique().tolist())

  with f2:
    start_date = st.date_input(
        "📅 Start Date",
        value=init_start,
        min_value=min_d,
        max_value=max_d,
        key="myntra_start_date",
    )
  with f3:
    end_date = st.date_input(
        "📅 End Date",
        value=init_end,
        min_value=min_d,
        max_value=max_d,
        key="myntra_end_date",
    )
  with f4:
    sel_comb_statuses = st.multiselect(
        "🔀 Combined Status",
        all_comb_statuses,
        default=all_comb_statuses,
        key="myn_comb",
    )

  if not sel_comb_statuses:
    sel_comb_statuses = all_comb_statuses

  if start_date > end_date:
    st.error("Start Date must be on or before End Date.")
    return

  _html(f"""
    <div class="exec-banner myntra">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Myntra Analysis</div>
                <div class="exec-sub">Connected to Myntra_Consolidated_Orders.xlsx • Orders Created, Dispatched, RTO, Returns & Net Revenue</div>
            </div>
        </div>
        <div class="exec-pill">📅 Created: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
    </div>
    """)

  p_df = df_all[
      (df_all["order_date_dt"].dt.date >= start_date)
      & (df_all["order_date_dt"].dt.date <= end_date)
      & (df_all["Combined_Status"].isin(sel_comb_statuses))
  ].copy()

  if p_df.empty:
    st.info(
        "No Myntra orders found between"
        f" {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}."
    )
    return

  tot_ord = int(p_df["Unique_Order_Key"].nunique())
  tot_rows = len(p_df)

  has_pack = p_df["packing_date_dt"].notna()
  inv_col = _find_col(p_df, ["invoice_number", "Invoice Number"])
  has_inv = (
      (p_df[inv_col].fillna("").astype(str).str.strip() != "")
      if inv_col
      else pd.Series([False] * len(p_df), index=p_df.index)
  )
  is_disp_mask = (
      has_pack
      | has_inv
      | p_df["Status_Clean"].isin(
          ["delivered", "in_transit", "reverse_in_transit", "shipped"]
      )
  )
  disp_cnt = (
      int(p_df[is_disp_mask]["Unique_Order_Key"].nunique())
      if is_disp_mask.any()
      else 0
  )

  rt_l_series = p_df["Return_Type_Clean"]
  st_l_series = p_df["Status_Clean"]

  is_rto_mask = rt_l_series.str.contains(
      "rto", na=False
  ) | st_l_series.str.contains("rto", na=False)
  is_cust_ret_mask = (
      (~is_rto_mask)
      & (~rt_l_series.str.contains("exchange", na=False))
      & (
          rt_l_series.str.contains("return", na=False)
          | st_l_series.str.contains("reverse", na=False)
      )
  )
  is_exch_mask = rt_l_series.str.contains("exchange", na=False)

  rto_df = p_df[is_rto_mask].copy()
  cust_ret_df = p_df[is_cust_ret_mask].copy()
  exch_df = p_df[is_exch_mask].copy()
  deliv_df = p_df[st_l_series == "delivered"].copy()

  rto_cnt = int(rto_df["Unique_Order_Key"].nunique()) if not rto_df.empty else 0
  cust_ret_cnt = (
      int(cust_ret_df["Unique_Order_Key"].nunique())
      if not cust_ret_df.empty
      else 0
  )
  exch_cnt = (
      int(exch_df["Unique_Order_Key"].nunique()) if not exch_df.empty else 0
  )
  deliv_cnt = (
      int(deliv_df["Unique_Order_Key"].nunique()) if not deliv_df.empty else 0
  )

  seller_rev = float(p_df["seller_paid_amount"].sum())
  rto_seller_rev = (
      float(rto_df["seller_paid_amount"].sum()) if not rto_df.empty else 0.0
  )
  cust_ret_seller_rev = (
      float(cust_ret_df["seller_paid_amount"].sum())
      if not cust_ret_df.empty
      else 0.0
  )
  net_seller_rev = max(seller_rev - rto_seller_rev - cust_ret_seller_rev, 0.0)

  aov = seller_rev / tot_ord if tot_ord > 0 else 0.0
  rto_pct = (rto_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
  cust_ret_pct = (
      (cust_ret_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
  )

  k1, k2, k3, k4, k5 = st.columns(5)
  with k1:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Total Orders Created</div>
                <div class="kpi-val">{tot_ord:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_rows:,} Order Items</span>
            </div>
            <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
        </div>
        """)
  with k2:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Order Dispatched</div>
                <div class="kpi-val">{disp_cnt:,}</div>
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">{disp_cnt/max(tot_ord,1)*100:.1f}% Dispatched</span>
            </div>
            <div class="kpi-ico" style="background:#ECFEFF;">📦</div>
        </div>
        """)
  with k3:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">RTO Count</div>
                <div class="kpi-val">{rto_cnt:,} ({rto_pct:.1f}%)</div>
                <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">₹{rto_seller_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>
        """)
  with k4:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Customer Return Count</div>
                <div class="kpi-val">{cust_ret_cnt:,} ({cust_ret_pct:.1f}%)</div>
                <span class="kpi-tag" style="background:#FFF1F2; color:#BE123C;">₹{cust_ret_seller_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#FFF1F2;">📥</div>
        </div>
        """)
  with k5:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Net Revenue</div>
                <div class="kpi-val">₹{net_seller_rev:,.2f}</div>
                <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Gross: ₹{seller_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#ECFDF5;">💰</div>
        </div>
        """)

  st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

  tab1, tab2, tab3, tab4 = st.tabs([
      "📈 Overview & Combined Status",
      "↩️ RTO & Customer Returns",
      "👗 Article Types & Top SKUs",
      "📋 Orders Table & Download",
  ])

  with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
      _html(
          '<div class="card-box"><div class="card-title">📊 Daily Unique'
          " Orders & Seller Paid Revenue Trend</div>"
      )
      p_df["Order_Date_Only"] = p_df["order_date_dt"].dt.date
      daily = (
          p_df.groupby("Order_Date_Only")
          .agg(
              Orders=("Unique_Order_Key", "nunique"),
              Revenue=("seller_paid_amount", "sum"),
          )
          .reset_index()
          .sort_values("Order_Date_Only")
      )
      daily["Date_Label"] = pd.to_datetime(daily["Order_Date_Only"]).dt.strftime(
          "%d %b"
      )
      daily["Rev_Lakhs"] = (daily["Revenue"] / 1e5).round(2)
      daily["AOV"] = np.where(
          daily["Orders"] > 0, daily["Revenue"] / daily["Orders"], 0.0
      )
      daily["Custom_Hover"] = [
          f"₹{rev:,.2f} (₹{rev/1e5:.2f}L) | AOV: ₹{aov_v:,.0f}"
          for rev, aov_v in zip(daily["Revenue"], daily["AOV"])
      ]

      fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
      fig_dual.add_trace(
          go.Bar(
              x=daily["Date_Label"],
              y=daily["Orders"],
              name="Unique Orders",
              marker=dict(color="#6366F1", cornerradius=6),
              opacity=0.85,
              text=daily["Orders"],
              textposition="outside",
              cliponaxis=False,
              textfont=dict(
                  size=10, color="#312E81", family="Plus Jakarta Sans"
              ),
              hovertemplate=(
                  "<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>"
              ),
          ),
          secondary_y=False,
      )
      fig_dual.add_trace(
          go.Scatter(
              x=daily["Date_Label"],
              y=daily["Rev_Lakhs"],
              name="Revenue (₹ Lakhs)",
              mode="lines+markers",
              line=dict(color="#EC4899", width=3, shape="spline"),
              marker=dict(
                  size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")
              ),
              customdata=daily["Custom_Hover"],
              hovertemplate="Revenue: %{customdata}<extra></extra>",
          ),
          secondary_y=True,
      )
      max_ord_y = (
          max(float(daily["Orders"].max()) * 1.28, 5.0)
          if not daily.empty
          else 10.0
      )
      max_rev_y = (
          max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5)
          if not daily.empty
          else 1.0
      )
      fig_dual.update_layout(
          height=400,
          margin=dict(l=15, r=15, t=40, b=60),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          hovermode="x unified",
          bargap=0.28,
          legend=dict(
              orientation="h",
              yanchor="bottom",
              y=1.04,
              xanchor="right",
              x=1,
              font=dict(size=12),
          ),
          font=dict(family="Plus Jakarta Sans", color="#334155"),
      )
      fig_dual.update_xaxes(
          tickangle=-45,
          tickfont=dict(size=11, color="#475569"),
          nticks=18,
          showgrid=False,
      )
      fig_dual.update_yaxes(
          title_text="Unique Orders",
          range=[0, max_ord_y],
          showgrid=True,
          gridcolor="#F1F5F9",
          zeroline=False,
          secondary_y=False,
      )
      fig_dual.update_yaxes(
          title_text="Revenue (₹ Lakhs)",
          range=[0, max_rev_y],
          showgrid=False,
          zeroline=False,
          secondary_y=True,
      )
      st.plotly_chart(fig_dual, use_container_width=True)

      _html(
          '<div style="font-size:14px; font-weight:700; color:#0F172A;'
          ' margin-top:14px; margin-bottom:8px;">🔀 Combined Status'
          " (order_item_status + return_type)</div>"
      )
      comb_tbl = (
          p_df.groupby("Combined_Status")
          .agg(
              Unique_Orders=("Unique_Order_Key", "nunique"),
              Item_Rows=("Unique_Order_Key", "count"),
              Seller_Paid_INR=("seller_paid_amount", "sum"),
          )
          .reset_index()
          .sort_values("Unique_Orders", ascending=False)
      )
      comb_tbl["Seller_Paid_INR"] = comb_tbl["Seller_Paid_INR"].round(2)

      fig_comb = go.Figure(
          go.Bar(
              y=comb_tbl["Combined_Status"][::-1],
              x=comb_tbl["Unique_Orders"][::-1],
              orientation="h",
              marker=dict(color="#7C3AED", cornerradius=8),
              text=comb_tbl["Unique_Orders"][::-1],
              textposition="outside",
              cliponaxis=False,
          )
      )
      fig_comb.update_layout(
          height=260,
          margin=dict(l=10, r=45, t=15, b=15),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(
              showgrid=True,
              gridcolor="#F1F5F9",
              range=[0, max(float(comb_tbl["Unique_Orders"].max()) * 1.25, 3.0)],
          ),
      )
      st.plotly_chart(fig_comb, use_container_width=True)
      _safe_dataframe(
          comb_tbl, use_container_width=True, height=200, hide_index=True
      )
      _html("</div>")

    with c_right:
      _html(
          '<div class="card-box"><div class="card-title">🎯 Order & Return'
          " Funnel (Unique Orders)</div>"
      )
      funnel_labels = [
          "Orders Created",
          "Dispatched",
          "Delivered",
          "Customer Returns",
          "RTO Count",
          "Exchanges",
      ]
      funnel_vals = [
          tot_ord,
          disp_cnt,
          deliv_cnt,
          cust_ret_cnt,
          rto_cnt,
          exch_cnt,
      ]
      funnel_colors = [
          "#4F46E5",
          "#0EA5E9",
          "#10B981",
          "#E11D48",
          "#EF4444",
          "#8B5CF6",
      ]
      fig_fun = go.Figure(
          go.Bar(
              y=funnel_labels[::-1],
              x=funnel_vals[::-1],
              orientation="h",
              marker=dict(color=funnel_colors[::-1], cornerradius=8),
              text=[f"<b>{v:,}</b>" for v in funnel_vals[::-1]],
              textposition="outside",
              cliponaxis=False,
              textfont=dict(size=12, color="#0F172A"),
          )
      )
      fig_fun.update_layout(
          height=400,
          margin=dict(l=10, r=60, t=20, b=20),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(
              showgrid=True,
              gridcolor="#F1F5F9",
              zeroline=False,
              range=[0, max(funnel_vals + [1]) * 1.22],
          ),
          yaxis=dict(showgrid=False, tickfont=dict(size=12)),
          font=dict(family="Plus Jakarta Sans", color="#334155"),
      )
      st.plotly_chart(fig_fun, use_container_width=True)
      _html("</div>")

  with tab2:
    _html("""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: RTO & Customer Return Analysis</div>
            <div class="sec-sub">Reverse Status Breakdown & Net Seller Paid Summary</div>
        </div>
        """)
    rc1, rc2 = st.columns(2)
    with rc1:
      _html(
          '<div class="card-box"><div class="card-title">🍩 RTO Reverse'
          " Status (Donut)</div>"
      )
      if not rto_df.empty:
        r_st = (
            rto_df.groupby("Reverse_Status_Clean")["Unique_Order_Key"]
            .nunique()
            .reset_index(name="Count")
        )
        fig_rs = go.Figure(
            go.Pie(
                labels=r_st["Reverse_Status_Clean"],
                values=r_st["Count"],
                hole=0.58,
                textinfo="percent",
                textposition="inside",
                marker=dict(
                    colors=["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6"],
                    line=dict(color="#FFFFFF", width=2.5),
                ),
            )
        )
        fig_rs.update_layout(
            height=340,
            margin=dict(l=15, r=15, t=20, b=65),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5
            ),
            annotations=[
                dict(
                    text=f"<b>{rto_cnt:,}</b><br>RTO",
                    x=0.5,
                    y=0.5,
                    font_size=13,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_rs, use_container_width=True)
      else:
        st.info("No RTO orders in selected period.")
      _html("</div>")

    with rc2:
      _html(
          '<div class="card-box"><div class="card-title">🔄 Exchanges &'
          " Net Seller Paid Summary</div>"
      )
      st.metric("Gross Seller Paid Amount", f"₹{seller_rev:,.2f}")
      st.metric(
          "Less: RTO + Customer Return Amount",
          f"₹{(rto_seller_rev + cust_ret_seller_rev):,.2f}",
      )
      st.metric("Net Seller Paid Revenue", f"₹{net_seller_rev:,.2f}")
      st.caption(
          f"Active Exchange Orders: {exch_cnt:,} | Avg Order Value (AOV):"
          f" ₹{aov:,.0f}"
      )
      _html("</div>")

  with tab3:
    p1, p2 = st.columns([1.2, 1])
    with p1:
      _html(
          '<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by'
          " Unique Orders</div>"
      )
      top_sku = (
          p_df.groupby("SKU_Clean")["Unique_Order_Key"]
          .nunique()
          .sort_values(ascending=False)
          .head(7)
      )
      if not top_sku.empty:
        mv = top_sku.max()
        for rank, (sku, cnt) in enumerate(top_sku.items(), start=1):
          pct = cnt / mv * 100
          _html(
              f'<div class="prod-row"><div class="prod-meta"><span>#{rank}'
              f' &nbsp;{sku}</span><span style="color:#DB2777;">{cnt:,}'
              ' ord</span></div><div class="prod-track"><div'
              f' class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>'
          )
      _html("</div>")

    with p2:
      _html(
          '<div class="card-box"><div class="card-title">👗 Article Types'
          " (Unique Orders)</div>"
      )
      art_df = (
          p_df.groupby("Article_Clean")["Unique_Order_Key"]
          .nunique()
          .reset_index(name="Orders")
          .sort_values("Orders", ascending=False)
      )
      fig_art = go.Figure(
          go.Bar(
              x=art_df["Article_Clean"],
              y=art_df["Orders"],
              marker=dict(color="#8B5CF6", cornerradius=8),
              text=art_df["Orders"],
              textposition="outside",
              cliponaxis=False,
          )
      )
      fig_art.update_layout(
          height=310,
          margin=dict(l=10, r=10, t=25, b=10),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          yaxis=dict(
              showgrid=True,
              gridcolor="#F1F5F9",
              range=[0, max(float(art_df["Orders"].max()) * 1.25, 3.0)],
          ),
      )
      st.plotly_chart(fig_art, use_container_width=True)
      _html("</div>")

  with tab4:
    st.markdown(
        f"#### 📋 Filtered Myntra Orders ({tot_ord:,} Unique Orders /"
        f" {tot_rows:,} Rows)"
    )
    tbl_cols = [
        c
        for c in [
            "order_number",
            "sale_order_code",
            "Order_Create_Date",
            "order_date",
            "order_item_status",
            "return_type",
            "Combined_Status",
            "return_status",
            "product_sku_code",
            "article_type",
            "seller_paid_amount",
            "discount_amount",
            "delivery_charges",
        ]
        if c in p_df.columns
    ]
    _safe_dataframe(
        p_df[tbl_cols], use_container_width=True, height=360, hide_index=True
    )
    st.download_button(
        "⬇️ Download Filtered Myntra Data CSV",
        p_df[tbl_cols].to_csv(index=False).encode("utf-8"),
        f"myntra_analysis_{start_date}_{end_date}.csv",
        "text/csv",
        key="dl_myn_csv",
    )


# ==============================================================================
# 9. PAGE 4: NYKAA ANALYSIS (Myntra-aligned logic except KPI Orders)
# ==============================================================================
def render_nykaa_page():
  if nykaa_src is None:
    st.warning(
        f"File `{NYKAA_DEFAULT_NAME}` was not found in GitHub or upload panel."
    )
    return

  df_all = load_nykaa_data(nykaa_src)
  valid_dates = df_all["Order_Date_dt"].dropna()
  if valid_dates.empty:
    st.error("No valid dates found in Order Date.")
    return

  min_d = valid_dates.min().date()
  max_d = valid_dates.max().date()

  f1, f2, f3, f4, f5 = st.columns([1.0, 0.9, 0.9, 1.1, 1.3])
  with f1:
    preset = st.selectbox(
        "📅 Quick Date Preset",
        [
            "All Available Dates",
            "01 Oct – 31 Oct 2026",
            "01 Jul – 31 Oct 2026",
            "Custom Dates",
        ],
        index=0,
        key="nyk_preset",
    )
  if preset == "01 Oct – 31 Oct 2026":
    init_start = min(max(datetime.date(2026, 10, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 10, 31), max_d), min_d)
  elif preset == "01 Jul – 31 Oct 2026":
    init_start = min(max(datetime.date(2026, 7, 1), min_d), max_d)
    init_end = max(min(datetime.date(2026, 10, 31), max_d), min_d)
  else:
    init_start, init_end = min_d, max_d

  all_otypes = sorted(df_all["Order_Type_Clean"].unique().tolist())
  all_statuses = sorted(df_all["Status_Clean"].unique().tolist())

  with f2:
    start_date = st.date_input(
        "📅 Start Date",
        value=init_start,
        min_value=min_d,
        max_value=max_d,
        key="nykaa_start_date",
    )
  with f3:
    end_date = st.date_input(
        "📅 End Date",
        value=init_end,
        min_value=min_d,
        max_value=max_d,
        key="nykaa_end_date",
    )
  with f4:
    sel_otypes = st.multiselect(
        "💳 Filter Order Type (COD / Prepaid)",
        all_otypes,
        default=all_otypes,
        key="nyk_otypes",
    )
  with f5:
    sel_statuses = st.multiselect(
        "📦 Filter Status",
        all_statuses,
        default=all_statuses,
        key="nyk_statuses",
    )

  if not sel_otypes:
    sel_otypes = all_otypes
  if not sel_statuses:
    sel_statuses = all_statuses

  if start_date > end_date:
    st.error("Start Date must be on or before End Date.")
    return

  _html(f"""
    <div class="exec-banner nykaa">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Nykaa Analysis</div>
                <div class="exec-sub">Connected to OrderExport (16).xls • Nykaa Order Count + Myntra KPI & Revenue Logic</div>
            </div>
        </div>
        <div class="exec-pill">📅 Orders: {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</div>
    </div>
    """)

  p_df = df_all[
      (df_all["Order_Date_dt"].dt.date >= start_date)
      & (df_all["Order_Date_dt"].dt.date <= end_date)
      & (df_all["Order_Type_Clean"].isin(sel_otypes))
      & (df_all["Status_Clean"].isin(sel_statuses))
  ].copy()

  if p_df.empty:
    st.info(
        "No Nykaa orders found between"
        f" {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}."
    )
    return

  tot_ord = int(p_df["Order_Key"].nunique())
  tot_rows = len(p_df)
  tot_qty = int(p_df["Qty"].sum())

  st_l_series = p_df["Status_Lower"]
  is_exch_mask = st_l_series.str.contains("exchange", na=False)
  is_rto_mask = (~is_exch_mask) & st_l_series.str.contains("rto", na=False)
  is_cust_ret_mask = (
      (~is_rto_mask)
      & (~is_exch_mask)
      & st_l_series.str.contains("return", na=False)
  )
  is_canc_mask = st_l_series == "cancelled"

  disp_keys = set(
      p_df[
          (~is_canc_mask)
          & (
              is_rto_mask
              | is_cust_ret_mask
              | is_exch_mask
              | st_l_series.isin(
                  ["delivered", "shipped", "in_transit", "reverse_in_transit"]
              )
          )
      ]["Order_Key"].dropna()
  )
  disp_cnt = min(int(len(disp_keys)), tot_ord)

  rto_df = p_df[is_rto_mask].copy()
  cust_ret_df = p_df[is_cust_ret_mask].copy()
  exch_df = p_df[is_exch_mask].copy()
  deliv_df = p_df[st_l_series == "delivered"].copy()

  rto_cnt = int(rto_df["Order_Key"].nunique()) if not rto_df.empty else 0
  cust_ret_cnt = (
      int(cust_ret_df["Order_Key"].nunique()) if not cust_ret_df.empty else 0
  )
  exch_cnt = int(exch_df["Order_Key"].nunique()) if not exch_df.empty else 0
  deliv_cnt = int(deliv_df["Order_Key"].nunique()) if not deliv_df.empty else 0

  non_canc_df = p_df[~is_canc_mask].copy()
  gross_rev = (
      float(non_canc_df["Line Amount"].sum()) if not non_canc_df.empty else 0.0
  )
  rto_rev = float(rto_df["Line Amount"].sum()) if not rto_df.empty else 0.0
  cust_ret_rev = (
      float(cust_ret_df["Line Amount"].sum()) if not cust_ret_df.empty else 0.0
  )
  net_rev = max(gross_rev - rto_rev - cust_ret_rev, 0.0)

  aov = (
      gross_rev / max(int(non_canc_df["Order_Key"].nunique()), 1)
      if not non_canc_df.empty
      else 0.0
  )
  rto_pct = (rto_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
  cust_ret_pct = (
      (cust_ret_cnt / max(disp_cnt, 1) * 100) if disp_cnt > 0 else 0.0
  )

  k1, k2, k3, k4, k5 = st.columns(5)
  with k1:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Total Orders Created</div>
                <div class="kpi-val">{tot_ord:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_qty:,} Qty ({tot_rows} Rows)</span>
            </div>
            <div class="kpi-ico" style="background:#EEF2FF;">🛍️</div>
        </div>
        """)
  with k2:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Order Dispatched</div>
                <div class="kpi-val">{disp_cnt:,}</div>
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">{disp_cnt/max(tot_ord,1)*100:.1f}% Dispatched</span>
            </div>
            <div class="kpi-ico" style="background:#ECFEFF;">📦</div>
        </div>
        """)
  with k3:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">RTO Count</div>
                <div class="kpi-val">{rto_cnt:,} ({rto_pct:.1f}%)</div>
                <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">₹{rto_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>
        """)
  with k4:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Customer Return Count</div>
                <div class="kpi-val">{cust_ret_cnt:,} ({cust_ret_pct:.1f}%)</div>
                <span class="kpi-tag" style="background:#FFF1F2; color:#BE123C;">₹{cust_ret_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#FFF1F2;">📥</div>
        </div>
        """)
  with k5:
    _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Net Revenue</div>
                <div class="kpi-val">₹{net_rev:,.2f}</div>
                <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Gross: ₹{gross_rev:,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#ECFDF5;">💰</div>
        </div>
        """)

  st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

  tab1, tab2, tab3, tab4 = st.tabs([
      "📈 Overview & Status Breakdown",
      "↩️ RTO & Customer Returns",
      "👗 Top SKUs & Order Types",
      "📋 Orders Table & Download",
  ])

  st_tbl = (
      p_df.groupby("Status_Clean")
      .agg(
          Unique_Orders=("Order_Key", "nunique"),
          Qty=("Qty", "sum"),
          Line_Amount_INR=("Line Amount", "sum"),
      )
      .reset_index()
      .sort_values("Unique_Orders", ascending=False)
  )
  st_tbl["Line_Amount_INR"] = st_tbl["Line_Amount_INR"].round(2)

  with tab1:
    c_left, c_right = st.columns([1.85, 1.15])
    with c_left:
      _html(
          '<div class="card-box"><div class="card-title">📊 Daily Unique'
          " Orders & Revenue Trend (Excl. Cancelled)</div>"
      )
      nc_u = non_canc_df.copy()
      nc_u["Order_Date_Only"] = nc_u["Order_Date_dt"].dt.date
      daily = (
          nc_u.groupby("Order_Date_Only")
          .agg(Orders=("Order_Key", "nunique"), Revenue=("Line Amount", "sum"))
          .reset_index()
          .sort_values("Order_Date_Only")
      )
      daily["Date_Label"] = pd.to_datetime(daily["Order_Date_Only"]).dt.strftime(
          "%d %b"
      )
      daily["Rev_Lakhs"] = (daily["Revenue"] / 1e5).round(2)
      daily["AOV"] = np.where(
          daily["Orders"] > 0, daily["Revenue"] / daily["Orders"], 0.0
      )
      daily["Custom_Hover"] = [
          f"₹{rev:,.2f} (₹{rev/1e5:.2f}L) | AOV: ₹{aov_v:,.0f}"
          for rev, aov_v in zip(daily["Revenue"], daily["AOV"])
      ]

      fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
      fig_dual.add_trace(
          go.Bar(
              x=daily["Date_Label"],
              y=daily["Orders"],
              name="Unique Orders",
              marker=dict(color="#6366F1", cornerradius=6),
              opacity=0.85,
              text=daily["Orders"],
              textposition="outside",
              cliponaxis=False,
              textfont=dict(
                  size=10, color="#312E81", family="Plus Jakarta Sans"
              ),
              hovertemplate=(
                  "<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>"
              ),
          ),
          secondary_y=False,
      )
      fig_dual.add_trace(
          go.Scatter(
              x=daily["Date_Label"],
              y=daily["Rev_Lakhs"],
              name="Revenue (₹ Lakhs)",
              mode="lines+markers",
              line=dict(color="#EC4899", width=3, shape="spline"),
              marker=dict(
                  size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")
              ),
              customdata=daily["Custom_Hover"],
              hovertemplate="Revenue: %{customdata}<extra></extra>",
          ),
          secondary_y=True,
      )
      max_ord_y = (
          max(float(daily["Orders"].max()) * 1.28, 5.0)
          if not daily.empty
          else 10.0
      )
      max_rev_y = (
          max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5)
          if not daily.empty
          else 1.0
      )
      fig_dual.update_layout(
          height=400,
          margin=dict(l=15, r=15, t=40, b=60),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          hovermode="x unified",
          bargap=0.28,
          legend=dict(
              orientation="h",
              yanchor="bottom",
              y=1.04,
              xanchor="right",
              x=1,
              font=dict(size=12),
          ),
          font=dict(family="Plus Jakarta Sans", color="#334155"),
      )
      fig_dual.update_xaxes(
          tickangle=-45,
          tickfont=dict(size=11, color="#475569"),
          nticks=18,
          showgrid=False,
      )
      fig_dual.update_yaxes(
          title_text="Unique Orders",
          range=[0, max_ord_y],
          showgrid=True,
          gridcolor="#F1F5F9",
          zeroline=False,
          secondary_y=False,
      )
      fig_dual.update_yaxes(
          title_text="Revenue (₹ Lakhs)",
          range=[0, max_rev_y],
          showgrid=False,
          zeroline=False,
          secondary_y=True,
      )
      st.plotly_chart(fig_dual, use_container_width=True)
      _html("</div>")

    with c_right:
      _html(
          '<div class="card-box"><div class="card-title">🍩 Status Breakdown'
          " (Unique Orders)</div>"
      )
      st.plotly_chart(
          _make_donut_fig(
              st_tbl["Status_Clean"].tolist(),
              st_tbl["Unique_Orders"].tolist(),
              ["#10B981", "#F59E0B", "#EF4444", "#94A3B8", "#0EA5E9"],
              f"<b>{tot_ord:,}</b><br>Orders",
          ),
          use_container_width=True,
      )
      _html("</div>")

  with tab2:
    _html("""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: RTO & Customer Return Analysis</div>
            <div class="sec-sub">Status Breakdown & Net Revenue Summary (Myntra Logic)</div>
        </div>
        """)
    rc1, rc2 = st.columns(2)
    with rc1:
      _html(
          '<div class="card-box"><div class="card-title">🍩 Order Status'
          " Breakdown (Donut)</div>"
      )
      st.plotly_chart(
          _make_donut_fig(
              st_tbl["Status_Clean"].tolist(),
              st_tbl["Unique_Orders"].tolist(),
              ["#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#0EA5E9"],
              f"<b>{rto_cnt + cust_ret_cnt:,}</b><br>Ret/RTO",
          ),
          use_container_width=True,
      )
      _html("</div>")

    with rc2:
      _html(
          '<div class="card-box"><div class="card-title">🔄 Exchanges &'
          " Net Revenue Summary</div>"
      )
      st.metric("Gross Revenue (Excl. Cancelled)", f"₹{gross_rev:,.2f}")
      st.metric(
          "Less: RTO + Customer Return Amount",
          f"₹{(rto_rev + cust_ret_rev):,.2f}",
      )
      st.metric("Net Revenue", f"₹{net_rev:,.2f}")
      st.caption(
          f"Delivered Orders: {deliv_cnt:,} | Exchanges: {exch_cnt:,} | AOV:"
          f" ₹{aov:,.0f}"
      )
      _html("</div>")

    _html(
        '<div class="card-box"><div class="card-title">📋 Status-Wise'
        " Summary Table</div>"
    )
    _safe_dataframe(st_tbl, use_container_width=True, height=220, hide_index=True)
    _html("</div>")

  with tab3:
    t1, t2 = st.columns([1.3, 1])
    with t1:
      _html(
          '<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by'
          " Revenue (Excl. Cancelled)</div>"
      )
      top_sku = (
          non_canc_df.groupby(["SKU_Code_Clean", "SKU_Name_Clean"])[
              "Line Amount"
          ]
          .sum()
          .sort_values(ascending=False)
          .head(7)
      )
      if not top_sku.empty:
        mv = top_sku.max()
        for rank, ((skuc, skun), amt) in enumerate(top_sku.items(), start=1):
          pct = amt / mv * 100
          short_n = (
              f"{skuc} — {skun[:42]}..."
              if len(skun) > 42
              else f"{skuc} — {skun}"
          )
          _html(
              f'<div class="prod-row"><div class="prod-meta"><span>#{rank}'
              f' &nbsp;{short_n}</span><span style="color:#DB2777;">₹{amt:,.0f}</span></div><div'
              ' class="prod-track"><div class="prod-fill"'
              f' style="width:{pct:.1f}%;"></div></div></div>'
          )
      _html("</div>")

    with t2:
      _html(
          '<div class="card-box"><div class="card-title">💳 Order Type (COD'
          " vs Prepaid)</div>"
      )
      ot_tbl = (
          p_df.groupby("Order_Type_Clean")
          .agg(
              Unique_Orders=("Order_Key", "nunique"),
              Line_Amount_INR=("Line Amount", "sum"),
          )
          .reset_index()
      )
      ot_tbl["Line_Amount_INR"] = ot_tbl["Line_Amount_INR"].round(2)
      _safe_dataframe(
          ot_tbl, use_container_width=True, height=220, hide_index=True
      )
      _html("</div>")

  with tab4:
    st.markdown(
        f"#### 📋 Filtered Nykaa Orders ({tot_ord:,} Unique Orders /"
        f" {tot_rows:,} Rows)"
    )
    tbl_cols = [
        c
        for c in [
            "Web Order No",
            "Order_Create_Date",
            "Order Date",
            "Customer Name",
            "SKU Code",
            "SKU Name",
            "Order Type",
            "Qty",
            "Unit Price",
            "Line Amount",
            "Status",
            "Ship by Date",
        ]
        if c in p_df.columns
    ]
    _safe_dataframe(
        p_df[tbl_cols], use_container_width=True, height=360, hide_index=True
    )
    st.download_button(
        "⬇️ Download Nykaa Orders CSV",
        p_df[tbl_cols].to_csv(index=False).encode("utf-8"),
        f"nykaa_analysis_{start_date}_{end_date}.csv",
        "text/csv",
        key="dl_nyk_csv",
    )


def _run_page_safely(page_name: str, render_fn):
  """Render a dashboard page safely so runtime errors never leave a blank screen."""
  try:
    render_fn()
  except Exception as exc:
    st.error(f"Error rendering **{page_name}**: `{type(exc).__name__}: {exc}`")
    with st.expander("🔍 Technical Traceback Details"):
      import traceback

      st.code(traceback.format_exc(), language="python")


# ==============================================================================
# 10. INDIVIDUAL PAGE ROUTER
# ==============================================================================
page_now = st.session_state["active_page"]
if page_now == "📊 Daily Analysis":
  _run_page_safely(page_now, render_daily_page)
elif page_now == "👗 Shopify Analysis":
  _run_page_safely(page_now, render_shopify_page)
elif page_now == "🛍️ Myntra Analysis":
  _run_page_safely(page_now, render_myntra_page)
elif page_now == "💄 Nykaa Analysis":
  _run_page_safely(page_now, render_nykaa_page)
