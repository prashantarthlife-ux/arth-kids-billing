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


def _style_fig(
    fig: go.Figure,
    height: int = 360,
    margins: dict = None,
    showlegend: bool = True,
    hovermode: str = "closest",
) -> go.Figure:
    """Apply consistent executive SaaS styling to Plotly figures."""
    m = margins or dict(l=14, r=18, t=34, b=26)
    fig.update_layout(
        height=height,
        margin=m,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode=hovermode,
        showlegend=showlegend,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11.5, color="#1E293B"),
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#334155",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#FFFFFF"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.75)",
            font=dict(size=11.5, color="#1E293B"),
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color="#475569", size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F6", zeroline=False, tickfont=dict(color="#475569", size=11))
    return fig


def _to_excel_bytes(data_or_sheets, sheet_name: str = "Report") -> bytes:
    """Export a DataFrame or dict of {sheet_name: df} to an Excel (.xlsx) byte stream."""
    out = io.BytesIO()
    sheets = data_or_sheets if isinstance(data_or_sheets, dict) else {sheet_name: data_or_sheets}
    clean_sheets = {}
    for s_nm, raw_df in sheets.items():
        safe_s = re.sub(r"[\\/*?:\[\]]", "", str(s_nm or "Report"))[:31] or "Report"
        while safe_s in clean_sheets:
            safe_s = (safe_s[:28] + f"_{len(clean_sheets)+1}")[:31]
        cdf = raw_df.copy() if raw_df is not None else pd.DataFrame()
        for col in cdf.columns:
            if pd.api.types.is_datetime64tz_dtype(cdf[col]):
                cdf[col] = cdf[col].dt.tz_localize(None)
        clean_sheets[safe_s] = cdf

    try:
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            for s_nm, cdf in clean_sheets.items():
                cdf.to_excel(writer, sheet_name=s_nm, index=False)
    except Exception:
        with pd.ExcelWriter(out) as writer:
            for s_nm, cdf in clean_sheets.items():
                cdf.to_excel(writer, sheet_name=s_nm, index=False)
    out.seek(0)
    return out.getvalue()


_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 45%, #F4F6FB 100%);
    overflow-x: hidden;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

.block-container {
    padding-top: 1.0rem !important;
    padding-bottom: 2.4rem !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
    max-width: 100% !important;
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
    flex-wrap: wrap;
}
.hub-brand-title { font-size: 18px; font-weight: 800; color: #0F172A; margin: 0; }
.hub-brand-sub { font-size: 12px; color: #64748B; }
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
    margin-bottom: 16px;
    box-shadow: 0 14px 30px rgba(30, 41, 59, 0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
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
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 14px 16px 8px 16px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
div[data-testid="stPlotlyChart"] > div {
    border-radius: 0 0 14px 14px;
    overflow: hidden;
}
.kpi-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
.kpi-lbl { font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.4px; }
.kpi-pill-pos { background: #ECFDF5; color: #059669; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-pill-neg { background: #FFF1F2; color: #E11D48; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-pill-neu { background: #F1F5F9; color: #475569; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.kpi-main-num { font-size: 28px; font-weight: 800; color: #0F172A; margin: 8px 0 6px 0; line-height: 1.05; }
.kpi-foot { font-size: 11.5px; font-weight: 600; color: #334155; border-top: 1px dashed #E2E8F0; padding-top: 6px; }

.viz-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 14px 16px 12px 16px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
    margin-bottom: 14px;
}
.viz-heading { text-align: center; font-size: 14.5px; font-weight: 800; color: #0F172A; margin-bottom: 6px; }
.viz-info {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 8px 12px;
    margin-top: 8px;
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
.sec-header-ctrl {
    background: linear-gradient(90deg, #FFFBEB 0%, #FFFFFF 100%);
    border-left: 5px solid #F59E0B;
    border-radius: 14px;
    padding: 14px 20px;
    margin-top: 24px;
    margin-bottom: 14px;
    border-top: 1px solid #FEF3C7;
    border-right: 1px solid #FEF3C7;
    border-bottom: 1px solid #FEF3C7;
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

/* Tablet & Mobile Responsive Overrides */
@media (max-width: 992px) {
    .block-container {
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }
    .exec-banner {
        padding: 18px 20px;
        border-radius: 18px;
    }
    .exec-title {
        font-size: 20px;
    }
    .kpi-main-num {
        font-size: 24px;
    }
    .kpi-val {
        font-size: 19px;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-top: 0.65rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    .login-wrap {
        margin: 24px auto 14px auto;
        padding: 24px 18px;
        border-radius: 18px;
    }
    .hub-topbar, .main-banner, .card-box, .viz-card {
        padding: 12px 14px;
        border-radius: 14px;
    }
    .hub-brand-title {
        font-size: 15.5px;
    }
    .exec-banner {
        padding: 14px 16px;
        border-radius: 16px;
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    .exec-banner-left {
        gap: 11px;
    }
    .exec-title {
        font-size: 17px;
    }
    .exec-sub {
        font-size: 11.5px;
    }
    .exec-pill {
        font-size: 11.5px;
        padding: 6px 12px;
        white-space: normal;
    }
    .sec-title {
        font-size: 15.5px;
    }
    .kpi-card {
        padding: 14px 15px;
        margin-bottom: 8px;
    }
    .kpi-main-num {
        font-size: 22px;
    }
    .kpi-val {
        font-size: 18px;
    }
    .kpi-ico {
        width: 44px;
        height: 44px;
        min-width: 44px;
        font-size: 22px;
        border-radius: 12px;
    }
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
    }
}
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
                if keyword_tokens and any(tok in low for tok in keyword_tokens) and low.endswith(
                    (".xlsx", ".xls", ".csv")
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
    'style="width:82px;height:82px;border-radius:50%;object-fit:cover;margin:0 auto 12px auto;display:block;box-shadow:0 8px 20px rgba(15,23,42,0.14);border:2px solid #E2E8F0;" />'
    if LOGO_URI
    else '<div class="login-badge">📊</div>'
)
LOGO_BANNER_HTML = (
    f'<img src="{LOGO_URI}" alt="ARTH LIFE Logo" '
    'style="width:58px;height:58px;min-width:58px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.45);box-shadow:0 6px 16px rgba(0,0,0,0.22);" />'
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
                return f"https://raw.githubusercontent.com/{repo}/{branch}/" + "/".join(parts)
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
    local_fp = _find_local_file(local_candidates, globs=globs, keyword_tokens=keyword_tokens)
    if local_fp:
        return local_fp, f"GitHub Repo: {os.path.basename(local_fp)}"
    if fallback_local_path and os.path.exists(fallback_local_path):
        return fallback_local_path, f"Local Path: {os.path.basename(fallback_local_path)}"
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
    """Build a styled Plotly donut chart with crisp slice callouts."""
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.60,
            textinfo="percent+value",
            textposition="inside",
            insidetextorientation="horizontal",
            pull=[0.03 if i == 0 else 0.0 for i in range(len(labels))],
            marker=dict(
                colors=colors[: len(labels)],
                line=dict(color="#FFFFFF", width=2.5),
            ),
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>",
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


def _extract_size_from_text(series: pd.Series) -> pd.Series:
    """Extract garment/kids age size label from product title or variant text if explicit Size column is missing."""
    s = series.fillna("").astype(str)
    pat = r"(?i)\b(\d{1,2}\s*[-–to]+\s*\d{1,2}\s*(?:yrs?|years?|months?|m)|newborn|free\s*size|xs|s|m|l|xl|xxl)\b"
    extracted = s.str.extract(pat, expand=False).fillna("").str.strip()
    return extracted.replace("", "Unspecified")


def _render_rto_return_control_section(
    sku_df: pd.DataFrame,
    size_df: pd.DataFrame,
    sku_col_name: str,
    size_col_name: str,
    rto_col_name: str,
    ret_col_name: str,
    issue_col_name: str,
    total_ord_col_name: str,
    start_date: datetime.date,
    end_date: datetime.date,
    key_prefix: str,
):
    """Render the RTO & Return Control block at the bottom of the returns tab."""
    _html("""
    <div class="sec-header-ctrl">
        <div class="sec-title">🎯 RTO & Return Control: High-Return SKUs & Size / Age-Group Issues</div>
        <div class="sec-sub">Identify high-return SKUs and size or fit issues to improve upcoming production batches</div>
    </div>
    """)

    if sku_df is None or sku_df.empty:
        st.info("No SKU-level return or RTO data available for the selected period.")
        return

    sk_work = sku_df.copy()
    sk_work["RTO_%"] = np.where(
        sk_work[total_ord_col_name] > 0,
        (sk_work[rto_col_name] / sk_work[total_ord_col_name] * 100).round(1),
        0.0,
    )
    sk_work["Return_Size_%"] = np.where(
        sk_work[total_ord_col_name] > 0,
        (sk_work[ret_col_name] / sk_work[total_ord_col_name] * 100).round(1),
        0.0,
    )
    sk_work["Total_Issue_%"] = np.where(
        sk_work[total_ord_col_name] > 0,
        (sk_work[issue_col_name] / sk_work[total_ord_col_name] * 100).round(1),
        0.0,
    )
    sk_work["Production_Action"] = np.where(
        (sk_work["Return_Size_%"] >= 12.0) & (sk_work[ret_col_name] >= 2),
        "⚠️ Fit / Size Issue — Review Size Chart & Grading",
        np.where(
            (sk_work["RTO_%"] >= 20.0) & (sk_work[rto_col_name] >= 2),
            "🚨 High RTO — Verify COD & Listing Details",
            np.where(sk_work[issue_col_name] > 0, "🔍 Monitor Quality & Fit", "✅ Healthy"),
        ),
    )
    sk_work = sk_work.sort_values(by=[issue_col_name, "Total_Issue_%"], ascending=[False, False])

    ct_l, ct_r = st.columns([1.25, 1.0])
    with ct_l:
        _html('<div class="card-box"><div class="card-title">🚨 Top 10 High-Return / RTO SKUs</div>')
        top10_sku = sk_work[sk_work[issue_col_name] > 0].head(10).iloc[::-1]
        if not top10_sku.empty:
            fig_sku_ret = go.Figure()
            fig_sku_ret.add_trace(
                go.Bar(
                    y=top10_sku[sku_col_name].apply(lambda x: str(x)[:36] + "..." if len(str(x)) > 36 else str(x)),
                    x=top10_sku[rto_col_name],
                    name="RTO Orders",
                    orientation="h",
                    marker=dict(color="#EF4444", cornerradius=5),
                    text=top10_sku[rto_col_name],
                    textposition="inside",
                )
            )
            fig_sku_ret.add_trace(
                go.Bar(
                    y=top10_sku[sku_col_name].apply(lambda x: str(x)[:36] + "..." if len(str(x)) > 36 else str(x)),
                    x=top10_sku[ret_col_name],
                    name="Return / Exchange Orders",
                    orientation="h",
                    marker=dict(color="#8B5CF6", cornerradius=5),
                    text=top10_sku[ret_col_name],
                    textposition="inside",
                )
            )
            _style_fig(fig_sku_ret, height=350, margins=dict(l=10, r=25, t=28, b=15), hovermode="y unified")
            fig_sku_ret.update_layout(barmode="stack")
            st.plotly_chart(fig_sku_ret, use_container_width=True, key=f"{key_prefix}_sku_ret_ctrl")
        else:
            st.info("No SKU-level RTO or return issues recorded in this period.")
        _html("</div>")

    with ct_r:
        _html('<div class="card-box"><div class="card-title">📏 Size / Age-Group Return Rate (%)</div>')
        if size_df is not None and not size_df.empty:
            sz_work = size_df.copy()
            sz_work["Issue_%"] = np.where(
                sz_work["Orders"] > 0, (sz_work["Issues"] / sz_work["Orders"] * 100).round(1), 0.0
            )
            sz_work = sz_work.sort_values(by=["Issues", "Issue_%"], ascending=[False, False]).head(10)
            fig_sz = go.Figure()
            fig_sz.add_trace(
                go.Bar(
                    x=sz_work[size_col_name],
                    y=sz_work["Issue_%"],
                    name="Issue Rate %",
                    marker=dict(color="#F59E0B", cornerradius=6),
                    text=[f"{v:.1f}% ({int(c)})" for v, c in zip(sz_work["Issue_%"], sz_work["Issues"])],
                    textposition="outside",
                )
            )
            _style_fig(fig_sz, height=350, margins=dict(l=10, r=10, t=28, b=25), showlegend=False)
            fig_sz.update_yaxes(range=[0, max(float(sz_work["Issue_%"].max()) * 1.28, 10.0)])
            st.plotly_chart(fig_sz, use_container_width=True, key=f"{key_prefix}_size_ret_ctrl")
        else:
            st.info("No size or age-group return breakdown available for this period.")
        _html("</div>")

    _html('<div class="card-box"><div class="card-title">📋 SKU-Wise Return & Production Action Summary</div>')
    _safe_dataframe(
        sk_work[
            [
                sku_col_name,
                total_ord_col_name,
                rto_col_name,
                "RTO_%",
                ret_col_name,
                "Return_Size_%",
                "Total_Issue_%",
                "Production_Action",
            ]
        ],
        use_container_width=True,
        height=250,
        hide_index=True,
    )
    st.download_button(
        "⬇️ Download SKU Return & Size Control CSV",
        sk_work.to_csv(index=False).encode("utf-8"),
        f"{key_prefix}_sku_return_control_{start_date}_{end_date}.csv",
        "text/csv",
        key=f"dl_{key_prefix}_sku_ctrl",
    )
    _html("</div>")


# ==============================================================================
# 2B. MONTH-WISE & LATEST/CURRENT DATE HELPERS
# ==============================================================================
def _resolve_default_latest_date(min_d: datetime.date, max_d: datetime.date) -> datetime.date:
    """Resolve default selected date to the latest data date or today (whichever fits bounds)."""
    today_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date()
    cand = max(max_d, today_ist) if max_d else today_ist
    return min(max(cand, min_d), max_d)


def _sync_refresh_dates(
    prefix: str,
    min_d: datetime.date,
    max_d: datetime.date,
    default_start: datetime.date,
    default_end: datetime.date,
):
    """Ensure date widgets always default to latest/current dates on fresh load or refresh."""
    run_token = st.session_state.get("_app_boot_id")
    if run_token is None:
        import uuid

        run_token = str(uuid.uuid4())
        st.session_state["_app_boot_id"] = run_token

    token_key = f"_{prefix}_boot_token"
    s_key = f"{prefix}_start_date"
    e_key = f"{prefix}_end_date"

    if st.session_state.get(token_key) != run_token:
        st.session_state[token_key] = run_token
        st.session_state[s_key] = min(max(default_start, min_d), max_d)
        st.session_state[e_key] = min(max(default_end, min_d), max_d)
    else:
        if s_key in st.session_state:
            st.session_state[s_key] = min(max(st.session_state[s_key], min_d), max_d)
        if e_key in st.session_state:
            st.session_state[e_key] = min(max(st.session_state[e_key], min_d), max_d)


def _month_bounds(ym_str: str, min_d: datetime.date, max_d: datetime.date):
    """Return clamped (start_date, end_date) for a YYYY-MM month string."""
    p = pd.Period(ym_str, freq="M")
    m_start = max(p.start_time.date(), min_d)
    m_end = min(p.end_time.date(), max_d)
    if m_start > m_end:
        m_start = m_end
    return m_start, m_end


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
            in_pass = st.text_input("🔑 Password", type="password", placeholder="Enter Password")
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
        sheet = preferred_sheet if (preferred_sheet and preferred_sheet in xls.sheet_names) else xls.sheet_names[0]
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
    orders_sheet = "Dim_Orders (2)" if "Dim_Orders (2)" in xls.sheet_names else "Dim_Orders"
    disp_sheet = "Fact_Dispatches (2)" if "Fact_Dispatches (2)" in xls.sheet_names else "Fact_Dispatches"
    rev_sheet = (
        "Fact_Reverse_Logistics (2)"
        if "Fact_Reverse_Logistics (2)" in xls.sheet_names
        else ("Fact_Reverse_Logistics" if "Fact_Reverse_Logistics" in xls.sheet_names else None)
    )

    orders = pd.read_excel(xls, sheet_name=orders_sheet)
    disp = pd.read_excel(xls, sheet_name=disp_sheet)
    rev = pd.read_excel(xls, sheet_name=rev_sheet) if rev_sheet else pd.DataFrame()

    orders["Order_Date_dt"] = pd.to_datetime(
        orders["Order_Date"], format="mixed", dayfirst=True, errors="coerce"
    )
    for c in ["Order_Total", "Order_Subtotal", "Discount", "Shipping", "Total_Line_Items"]:
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


def _read_myntra_sheets(src):
    """Read Myntra_All_Orders, RTO_Returns, and Exchanges sheets when available."""
    name = src if isinstance(src, str) else getattr(src, "name", MYNTRA_CONSOLIDATED_NAME)
    base_nm = os.path.basename(str(name))
    low = str(name).lower()
    if low.endswith(".csv"):
        if hasattr(src, "seek"):
            src.seek(0)
        df_all = pd.read_csv(src, low_memory=False)
        return df_all, pd.DataFrame(), pd.DataFrame(), base_nm

    if hasattr(src, "seek"):
        src.seek(0)
    try:
        xls = pd.ExcelFile(src)
        sheets = xls.sheet_names
        main_sh = "Myntra_All_Orders" if "Myntra_All_Orders" in sheets else sheets[0]
        df_all = pd.read_excel(xls, sheet_name=main_sh)
        df_rto = pd.read_excel(xls, sheet_name="RTO_Returns") if "RTO_Returns" in sheets else pd.DataFrame()
        df_ex = pd.read_excel(xls, sheet_name="Exchanges") if "Exchanges" in sheets else pd.DataFrame()
        return df_all, df_rto, df_ex, base_nm
    except Exception:
        df_all = _read_excel_or_html_table(src, preferred_sheet="Myntra_All_Orders")
        return df_all, pd.DataFrame(), pd.DataFrame(), base_nm


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
    """Load and normalize Myntra order data following Myntra_All_Orders, RTO_Returns, and Exchanges sheets."""
    if source is None:
        return pd.DataFrame(), []
    tmp, rto_sh, ex_sh, nm = _read_myntra_sheets(source)
    meta_ignore = [c for c in ["_source_file", "_part_tag", "order_date_dt"] if c in tmp.columns]
    biz_cols = [c for c in tmp.columns if c not in meta_ignore]
    df = tmp.drop_duplicates(subset=biz_cols if biz_cols else None, keep="last").copy()
    if "item_id" in df.columns and df["item_id"].notna().any():
        df = df.drop_duplicates(subset=["item_id"], keep="last").copy()

    # Cross-reference RTO_Returns and Exchanges sheets on item_id / order_number
    rto_item_ids = set(rto_sh["item_id"].dropna().astype(str).str.strip()) if (not rto_sh.empty and "item_id" in rto_sh.columns) else set()
    ex_item_ids = set(ex_sh["item_id"].dropna().astype(str).str.strip()) if (not ex_sh.empty and "item_id" in ex_sh.columns) else set()
    item_s = df["item_id"].astype(str).str.strip() if "item_id" in df.columns else pd.Series([""] * len(df), index=df.index)
    df["_in_rto_returns_sheet"] = item_s.isin(rto_item_ids)
    df["_in_exchanges_sheet"] = item_s.isin(ex_item_ids)

    ord_dt_existing = _find_col(df, ["order_date_dt"])
    ord_dt_col = _find_col(df, ["order_date", "Order Date", "order_created_date"])
    pack_dt_col = _find_col(df, ["packing_date", "Packing Date", "packed_date"])

    parsed_from_raw = (
        pd.to_datetime(df[ord_dt_col], format="mixed", errors="coerce")
        if ord_dt_col
        else pd.Series(pd.NaT, index=df.index)
    )
    if hasattr(parsed_from_raw.dt, "tz") and parsed_from_raw.dt.tz is not None:
        parsed_from_raw = parsed_from_raw.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)

    if ord_dt_existing:
        parsed_existing = pd.to_datetime(df[ord_dt_existing], format="mixed", errors="coerce")
        if hasattr(parsed_existing.dt, "tz") and parsed_existing.dt.tz is not None:
            parsed_existing = parsed_existing.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
        df["order_date_dt"] = parsed_existing.fillna(parsed_from_raw)
    else:
        df["order_date_dt"] = parsed_from_raw

    df["Order_Create_Date"] = df["order_date_dt"].dt.date

    df["packing_date_dt"] = (
        pd.to_datetime(df[pack_dt_col], format="mixed", errors="coerce")
        if pack_dt_col
        else pd.Series(pd.NaT, index=df.index)
    )
    if hasattr(df["packing_date_dt"].dt, "tz") and df["packing_date_dt"].dt.tz is not None:
        df["packing_date_dt"] = df["packing_date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)

    for canonical, cands in [
        ("seller_paid_amount", ["seller_paid_amount", "Seller Paid Amount", "seller_payable_amount"]),
        ("Total_Customer_Paid", ["Total_Customer_Paid", "total_customer_paid", "customer_paid_amount"]),
        ("mrp", ["mrp", "MRP"]),
        ("discount_amount", ["discount_amount", "Discount Amount", "discount"]),
        ("delivery_charges", ["delivery_charges", "Delivery Charges", "shipping_fee"]),
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

    raw_ois = df[ois_col].fillna("").astype(str).str.strip() if ois_col else pd.Series([""] * len(df))
    raw_rt = df[rt_col].fillna("").astype(str).str.strip() if rt_col else pd.Series([""] * len(df))
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
    df["Combined_Status"] = [_build_combined_status(a, b) for a, b in zip(raw_ois, raw_rt)]

    art_col = _find_col(df, ["article_type", "Article Type", "category"])
    sku_col = _find_col(df, ["product_sku_code", "Product SKU Code", "sku_code", "sku"])
    size_col = _find_col(df, ["size", "Size", "product_size", "variant_size", "age_group"])

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
    if size_col:
        df["Size_Clean"] = df[size_col].fillna("Unspecified").astype(str).str.strip().replace("", "Unspecified")
    else:
        df["Size_Clean"] = _extract_size_from_text(df["SKU_Clean"])
    return df, [nm]


@st.cache_data(show_spinner=False)
def load_nykaa_data(file_src):
    """Load and normalize Nykaa export data."""
    if file_src is None:
        return pd.DataFrame()
    name = file_src if isinstance(file_src, str) else getattr(file_src, "name", NYKAA_DEFAULT_NAME)
    if str(name).lower().endswith(".csv"):
        if hasattr(file_src, "seek"):
            file_src.seek(0)
        df = pd.read_csv(file_src, low_memory=False)
    else:
        df = _read_excel_or_html_table(file_src, preferred_sheet="Export")

    df = df.drop_duplicates().copy()
    odate_col = _find_col(df, ["Order Date", "order_date", "Created Date"])
    df["Order_Date_dt"] = pd.to_datetime(
        df[odate_col] if odate_col else pd.Series(dtype=str), format="mixed", dayfirst=True, errors="coerce"
    )
    if hasattr(df["Order_Date_dt"].dt, "tz") and df["Order_Date_dt"].dt.tz is not None:
        df["Order_Date_dt"] = df["Order_Date_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["Order_Create_Date"] = df["Order_Date_dt"].dt.date

    for canonical, cands in [
        ("Qty", ["Qty", "Quantity", "qty"]),
        ("Unit Price", ["Unit Price", "unit_price", "Price"]),
        ("Line Amount", ["Line Amount", "line_amount", "Total Amount", "Amount"]),
    ]:
        found_c = _find_col(df, cands)
        df[canonical] = _to_num(df[found_c]) if found_c else 0.0

    wno_col = _find_col(df, ["Web Order No", "web_order_no", "Order No", "Order ID"])
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
    size_col = _find_col(df, ["Size", "size", "Variant", "Age Group"])

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
    if size_col:
        df["Size_Clean"] = df[size_col].fillna("Unspecified").astype(str).str.strip().replace("", "Unspecified")
    else:
        df["Size_Clean"] = _extract_size_from_text(df["SKU_Name_Clean"] + " " + df["SKU_Code_Clean"])
    return df


# ==============================================================================
# 4B. CUSTOMER COHORT MATRIX BUILDER (INFORMATIVE BOTTOM SECTION)
# ==============================================================================
def _detect_customer_key(df: pd.DataFrame):
    """Detect the best customer identifier column in orders data."""
    cust_col = _find_col(
        df,
        [
            "Customer_ID",
            "Customer Id",
            "Customer_Email",
            "Email",
            "Customer_Phone",
            "Phone",
            "Customer_Name",
            "Customer Name",
        ],
    )
    if not cust_col:
        return None
    s = df[cust_col].fillna("").astype(str).str.strip()
    s = s[~s.str.lower().isin(["", "nan", "none", "guest", "unknown"])]
    if s.empty:
        return None
    return cust_col


def _render_customer_cohort_matrix(orders_df: pd.DataFrame, max_months: int = 8):
    """Render a detailed Customer Cohort Analysis matrix with cohort size & retention insights."""
    _html('<div class="card-box"><div class="card-title">📊 Customer Cohort Retention Analysis (Month-by-Month Repeat Activity)</div>')

    if orders_df is None or orders_df.empty or "_dt" not in orders_df.columns:
        st.info("No order history available to compute customer cohorts.")
        _html("</div>")
        return

    cust_col = _detect_customer_key(orders_df)
    if not cust_col:
        st.info("Customer identifier column (Customer_Email / Customer_ID / Customer_Name) not found in orders sheet.")
        _html("</div>")
        return

    cdf = orders_df.dropna(subset=["_dt"]).copy()
    cdf["_cust"] = cdf[cust_col].fillna("").astype(str).str.strip()
    cdf = cdf[~cdf["_cust"].str.lower().isin(["", "nan", "none", "guest", "unknown"])].copy()
    if cdf.empty:
        st.info("No valid customer records found for cohort analysis.")
        _html("</div>")
        return

    cdf["_order_ym"] = cdf["_dt"].dt.to_period("M")
    first_ym_map = cdf.groupby("_cust")["_order_ym"].min()
    cdf["_cohort_ym"] = cdf["_cust"].map(first_ym_map)
    cdf["_month_idx"] = (
        (cdf["_order_ym"].dt.year - cdf["_cohort_ym"].dt.year) * 12
        + (cdf["_order_ym"].dt.month - cdf["_cohort_ym"].dt.month)
    )
    cdf = cdf[cdf["_month_idx"] >= 0].copy()

    cohort_sizes = cdf.groupby("_cohort_ym")["_cust"].nunique()
    if cohort_sizes.empty:
        st.info("No cohort sizes available.")
        _html("</div>")
        return

    max_m_data = int(cdf["_month_idx"].max())
    num_cols = min(max_months, max(1, max_m_data + 1))
    month_cols = [f"Month {i}" for i in range(num_cols)]

    active_by_cm = (
        cdf[cdf["_month_idx"] < num_cols]
        .groupby(["_cohort_ym", "_month_idx"])["_cust"]
        .nunique()
        .unstack(fill_value=0)
    )

    pct_matrix = pd.DataFrame(index=cohort_sizes.index, columns=range(num_cols), dtype=float)
    cnt_matrix = pd.DataFrame(index=cohort_sizes.index, columns=range(num_cols), dtype=float)
    for c_ym, c_size in cohort_sizes.items():
        if c_size <= 0:
            continue
        for m_i in range(num_cols):
            if m_i in active_by_cm.columns and c_ym in active_by_cm.index:
                act_cnt = float(active_by_cm.loc[c_ym, m_i])
                if m_i == 0 or act_cnt > 0:
                    cnt_matrix.loc[c_ym, m_i] = act_cnt
                    pct_matrix.loc[c_ym, m_i] = (act_cnt / float(c_size)) * 100.0

    all_cohorts_row = {}
    for m_i in range(num_cols):
        col_vals = pct_matrix[m_i].dropna()
        all_cohorts_row[m_i] = float(col_vals.mean()) if not col_vals.empty else np.nan

    def _fmt_pct(val):
        if pd.isna(val):
            return ""
        rounded = round(float(val), 2)
        if float(rounded).is_integer():
            return f"{int(rounded)}%"
        s = f"{rounded:.2f}".rstrip("0").rstrip(".")
        return f"{s}%"

    def _cell_style(val, max_v):
        if pd.isna(val) or max_v <= 0:
            return "background: transparent; color: transparent;"
        ratio = float(np.clip(val / max_v, 0.0, 1.0))
        r = int(round(220 + ratio * (15 - 220)))
        g = int(round(228 + ratio * (47 - 228)))
        b = int(round(250 + ratio * (158 - 250)))
        txt_color = "#FFFFFF" if ratio >= 0.62 else "#0F172A"
        return f"background-color: rgb({r},{g},{b}); color: {txt_color}; font-weight: 600;"

    max_cell_val = float(pct_matrix.max().max()) if not pct_matrix.empty else 1.0
    if pd.isna(max_cell_val) or max_cell_val <= 0:
        max_cell_val = 1.0

    th_cells = [
        '<th style="text-align:left; padding:10px 14px; color:#334155; font-weight:700; font-size:13px; border-bottom:1px solid #E2E8F0;">Cohort (Users)</th>'
    ]
    for mc in month_cols:
        th_cells.append(
            f'<th style="text-align:center; padding:10px 10px; color:#334155; font-weight:600; font-size:13px; border-bottom:1px solid #E2E8F0;">{mc}</th>'
        )

    all_cells = [
        '<td style="text-align:left; padding:12px 14px; font-weight:800; color:#0F172A; font-size:13px; border-bottom:1px solid #E2E8F0;">All cohorts</td>'
    ]
    for m_i in range(num_cols):
        v = all_cohorts_row.get(m_i, np.nan)
        lbl = _fmt_pct(v)
        all_cells.append(
            f'<td style="text-align:center; padding:12px 10px; font-weight:800; color:#0F172A; font-size:13px; border-bottom:1px solid #E2E8F0;">{lbl}</td>'
        )

    body_rows_html = []
    m1_rates = []
    for c_ym in sorted(pct_matrix.index):
        c_lbl = c_ym.strftime("%b %Y")
        c_sz = int(cohort_sizes.get(c_ym, 0))
        if 1 in pct_matrix.columns and not pd.isna(pct_matrix.loc[c_ym, 1]):
            m1_rates.append(float(pct_matrix.loc[c_ym, 1]))
        tds = [
            f'<td style="text-align:left; padding:6px 14px; color:#1E293B; font-size:13px; white-space:nowrap;"><b>{c_lbl}</b> <span style="color:#64748B; font-size:11.5px;">({c_sz:,})</span></td>'
        ]
        for m_i in range(num_cols):
            val = pct_matrix.loc[c_ym, m_i]
            act_u = cnt_matrix.loc[c_ym, m_i] if not pd.isna(cnt_matrix.loc[c_ym, m_i]) else 0.0
            if pd.isna(val):
                tds.append('<td style="padding:4px; text-align:center;"></td>')
            else:
                st_css = _cell_style(val, max_cell_val)
                lbl = _fmt_pct(val)
                tip = f"{c_lbl} | Month {m_i}: {lbl} ({int(act_u):,}/{c_sz:,} customers)"
                tds.append(
                    f'<td style="padding:3px; text-align:center;" title="{tip}">'
                    f'<div style="{st_css} border-radius:6px; padding:10px 8px; font-size:12.5px; min-width:74px;">{lbl}</div>'
                    f"</td>"
                )
        body_rows_html.append("<tr>" + "".join(tds) + "</tr>")

    table_html = (
        '<div style="overflow-x:auto; width:100%;">'
        '<table style="width:100%; border-collapse:separate; border-spacing:2px 4px; font-family:Plus Jakarta Sans,sans-serif;">'
        f'<thead><tr>{"".join(th_cells)}</tr></thead>'
        f'<tbody><tr>{"".join(all_cells)}</tr>{"".join(body_rows_html)}</tbody>'
        "</table></div>"
    )
    _html(table_html)

    avg_m1 = f"{np.mean(m1_rates):.1f}%" if m1_rates else "N/A"
    largest_c_ym = cohort_sizes.idxmax()
    _html(f"""
    <div class="viz-info">
        <b>Cohort Intelligence:</b> Tracked <b>{len(cohort_sizes):,}</b> monthly cohorts (Total first-time customers: <b>{int(cohort_sizes.sum()):,}</b>) ·
        Largest cohort: <b>{largest_c_ym.strftime('%b %Y')} ({int(cohort_sizes.max()):,} users)</b> ·
        Avg Month 1 repeat retention: <b>{avg_m1}</b>. Hover any cell for exact active customer counts.
    </div>
    """)
    _html("</div>")


# ==============================================================================
# 5. CONNECT GITHUB FILES & INDIVIDUAL PAGE NAVIGATION
# ==============================================================================
DASHBOARD_PAGES = [
    "📊 Daily Analysis",
    "👗 Shopify Analysis",
    "🔮 Shopify Forecast",
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
        "Myntra_Consolidated_Orders.xlsx", type=["xlsx", "xls", "csv"], key="sb_up_myntra"
    )
    sb_up_nykaa = st.file_uploader(
        "OrderExport (16).xls", type=["xls", "xlsx", "csv"], key="sb_up_nykaa"
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
    ["*Myntra_Consolidated*.xlsx", "*myntra*.xlsx", "part-*.csv", "*myntra*.csv"],
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
# 6. PAGE 1: DAILY ANALYSIS (WITH DAILY RTO STATUS & EXCHANGE STATUS + EXCEL)
# ==============================================================================
def render_daily_page():
    if model_src is None:
        st.warning(f"Model file `{MODEL_FILENAME}` was not found in GitHub or local folders.")
        return

    df_orders, df_disp, df_rev = load_model_excel(model_src)
    valid_dates = df_orders["Order_Date_dt"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in Order_Date.")
        return

    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()
    init_date = _resolve_default_latest_date(min_d, max_d)
    if "_daily_boot_seen" not in st.session_state:
        st.session_state["_daily_boot_seen"] = True
        st.session_state["arth_daily_date"] = init_date

    b1, b2 = st.columns([1.8, 1.0])
    with b1:
        _html("""
        <div class="main-banner">
            <div class="main-h1">Arth life Daily Analysis</div>
            <div class="main-sub">Particular Date KPIs + Rolling 7-Day Trend, Daily RTO Status & Daily Exchange Status</div>
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
    date_lbls_7d = [d.strftime("%d %b") for d in dates_7d]
    prev_date = selected_date - datetime.timedelta(days=1)

    f_orders = df_orders.copy()
    f_orders["_ord_d"] = f_orders["Order_Date_dt"].dt.date
    f_orders["_ym"] = f_orders["Order_Date_dt"].dt.to_period("M").astype(str)

    fin_low = f_orders["Financial_Status"].fillna("").astype(str).str.strip().str.lower()
    valid_orders = f_orders[~fin_low.isin(["voided", "cancelled"])].copy()
    dax_orders = f_orders[~fin_low.isin(["voided", "cancelled", "refunded"])].copy()

    f_disp = df_disp[df_disp["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))].copy()
    f_disp["_disp_d"] = f_disp["Dispatch_Date_dt"].dt.date
    stat_str = f_disp["Shipment_Status"].fillna("").astype(str).str.strip()
    valid_disp = f_disp[~stat_str.isin(["CANCELLED", "Stop Booking/Delivery"])].copy()

    if not df_rev.empty and "Base_Order_ID" in df_rev.columns:
        f_rev = df_rev[df_rev["Base_Order_ID"].isin(set(f_orders["Base_Order_ID"]))].copy()
        if "Pickup_Date_dt" in f_rev.columns and f_rev["Pickup_Date_dt"].notna().any():
            f_rev["_rev_d"] = f_rev["Pickup_Date_dt"].dt.date
        else:
            ord_date_map = f_orders.dropna(subset=["_ord_d"]).drop_duplicates("Base_Order_ID").set_index("Base_Order_ID")["_ord_d"]
            f_rev["_rev_d"] = f_rev["Base_Order_ID"].map(ord_date_map)
    else:
        f_rev = pd.DataFrame(columns=["Base_Order_ID", "_rev_d"])
    f_rev_id_col = _find_col(f_rev, ["Order_ID", "Base_Order_ID"]) if not f_rev.empty else None

    latest_ym_val = f_orders[f_orders["_ord_d"] <= selected_date]["_ym"].dropna().max()
    if pd.isna(latest_ym_val) or not latest_ym_val:
        latest_ym_val = f_orders["_ym"].dropna().max()

    ful_str_dax = dax_orders["Fulfillment_Status"].fillna("").astype(str).str.strip()
    latest_month_unful_df = dax_orders[
        (dax_orders["_ym"] == latest_ym_val) & (ful_str_dax.loc[dax_orders.index] == "Unfulfilled")
    ].copy()
    latest_month_unful_cnt = int(len(latest_month_unful_df))

    day_ord = valid_orders[valid_orders["_ord_d"] == selected_date]
    ord_day_cnt = len(set(day_ord["Base_Order_ID"].dropna().astype(str)))
    ord_prev_cnt = len(set(valid_orders[valid_orders["_ord_d"] == prev_date]["Base_Order_ID"].dropna().astype(str)))
    ord_diff = ord_day_cnt - ord_prev_cnt
    day_rev_amt = float(day_ord["Order_Total"].sum())
    day_aov_amt = day_rev_amt / ord_day_cnt if ord_day_cnt > 0 else 0.0

    pre_day_cnt = len(
        set(
            day_ord[
                day_ord["Financial_Status"].fillna("").astype(str).str.strip().str.lower().isin(["paid", "authorized"])
            ]["Base_Order_ID"].dropna().astype(str)
        )
    )
    cod_day_cnt = max(0, ord_day_cnt - pre_day_cnt)

    ful_low = valid_orders["Fulfillment_Status"].fillna("").astype(str).str.strip().str.lower()
    ful_day_cnt = len(
        set(
            valid_orders[(valid_orders["_ord_d"] == selected_date) & (ful_low == "fulfilled")]["Base_Order_ID"]
            .dropna()
            .astype(str)
        )
    )
    unful_day_cnt = len(
        set(
            valid_orders[(valid_orders["_ord_d"] == selected_date) & (~ful_low.isin(["fulfilled", "shipped"]))][
                "Base_Order_ID"
            ]
            .dropna()
            .astype(str)
        )
    )
    unful_prev_cnt = len(
        set(
            valid_orders[(valid_orders["_ord_d"] == prev_date) & (~ful_low.isin(["fulfilled", "shipped"]))][
                "Base_Order_ID"
            ]
            .dropna()
            .astype(str)
        )
    )
    unful_diff = unful_day_cnt - unful_prev_cnt

    disp_day_cnt = len(set(valid_disp[valid_disp["_disp_d"] == selected_date]["Base_Order_ID"].dropna().astype(str)))
    disp_prev_cnt = len(set(valid_disp[valid_disp["_disp_d"] == prev_date]["Base_Order_ID"].dropna().astype(str)))
    disp_diff = disp_day_cnt - disp_prev_cnt

    disp_up_to_eff = set(valid_disp[valid_disp["_disp_d"] <= selected_date]["Base_Order_ID"].dropna().astype(str))
    rto_mask = f_disp["Is_RTO"].astype(bool) | stat_str.isin(
        ["RETURNED_TO_ORIGIN", "RETURNING_TO_ORIGIN", "RTO Delivered", "Set RTO"]
    )

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
        delh_k = int((ddf_k["Dispatch_Category"] == "Delhivery").sum()) if "Dispatch_Category" in ddf_k.columns else 0
        dtdc_k = int((ddf_k["Dispatch_Category"] == "DTDC").sum()) if "Dispatch_Category" in ddf_k.columns else 0

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

        rto_k = int(f_disp[(f_disp["_disp_d"] == d_k) & rto_mask]["Base_Order_ID"].nunique())
        ex_k = (
            int(f_rev[f_rev["_rev_d"] == d_k][f_rev_id_col].nunique())
            if (not f_rev.empty and "_rev_d" in f_rev.columns and f_rev_id_col)
            else 0
        )

        rows_7d.append(
            {
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
            }
        )
    df_7d = pd.DataFrame(rows_7d)

    def _spark(x_labels, y_vals, line_color="#4F46E5", fill_rgba="rgba(79, 70, 229, 0.08)"):
        y_arr = np.asarray(y_vals, dtype=float)
        y_min = float(np.min(y_arr)) if len(y_arr) else 0.0
        y_max = float(np.max(y_arr)) if len(y_arr) else 1.0
        span = max(y_max - y_min, 1.0)
        pad_low = max(0.0, y_min - span * 0.25)
        pad_high = y_max + span * 0.30

        fig = go.Figure(
            go.Scatter(
                x=list(range(len(x_labels))),
                y=y_arr,
                mode="lines+markers",
                fill="tozeroy",
                fillcolor=fill_rgba,
                line=dict(color=line_color, width=2.2, shape="spline"),
                marker=dict(size=5, color="#FFFFFF", line=dict(color=line_color, width=1.8)),
                customdata=list(x_labels),
                text=[f"{int(v):,}" for v in y_arr],
                hovertemplate="%{customdata}: <b>%{text}</b><extra></extra>",
            )
        )
        fig.update_layout(
            height=46,
            margin=dict(l=10, r=10, t=6, b=6),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            showlegend=False,
            xaxis=dict(
                visible=False,
                range=[-0.4, max(len(x_labels) - 0.6, 0.6)],
                fixedrange=True,
            ),
            yaxis=dict(
                visible=False,
                range=[pad_low, pad_high],
                fixedrange=True,
            ),
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
            _spark(df_7d["Date"], df_7d["Orders"], "#4F46E5", "rgba(79, 70, 229, 0.08)"),
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
            _spark(df_7d["Date"], df_7d["Unfulfilled"], "#E11D48", "rgba(225, 29, 72, 0.08)"),
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
            _spark(df_7d["Date"], df_7d["Fulfilled"], "#7C3AED", "rgba(124, 58, 237, 0.08)"),
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
            _spark(df_7d["Date"], df_7d["Unfulfilled"], "#F59E0B", "rgba(245, 158, 11, 0.08)"),
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

    _html('<div class="sec-bar">Section 1 — Orders Created, Revenue/AOV & Daily Dispatches (7 Days)</div>')
    s1_l, s1_r = st.columns([1.05, 1.0])
    with s1_l:
        _html('<div class="viz-card"><div class="viz-heading">Order Created by Prepaid or COD</div>')
        fig_oc = go.Figure()
        fig_oc.add_trace(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Prepaid"],
                name="Prepaid Orders",
                marker=dict(color="#4F46E5", cornerradius=5),
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
                marker=dict(color="#06B6D4", cornerradius=5),
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
                mode="lines+markers+text",
                line=dict(color="#1E1B4B", width=1.8, dash="dot"),
                marker=dict(size=6, color="#1E1B4B"),
                text=[f"<b>{v}</b>" for v in df_7d["Orders"]],
                textposition="top center",
                textfont=dict(size=11.5, color="#1E1B4B"),
            )
        )
        _style_fig(fig_oc, height=275, margins=dict(l=8, r=8, t=28, b=6), hovermode="x unified")
        fig_oc.update_layout(barmode="stack")
        fig_oc.update_yaxes(range=[0, max(df_7d["Orders"].max(), 1) * 1.32])
        st.plotly_chart(fig_oc, use_container_width=True)
        _html(f'<div class="viz-info"><b>7D Orders:</b> Total <b>{tot_7d_ord:,}</b> orders (Prepaid: <b>{tot_7d_pre:,}</b> | COD: <b>{tot_7d_cod:,}</b>) · Avg <b>{tot_7d_ord/7:.1f}/day</b>.</div></div>')

        _html('<div class="viz-card"><div class="viz-heading">Daily Order Revenue (₹) & Average Order Value (AOV)</div>')
        fig_rev = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rev.add_trace(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Revenue"],
                name="Revenue (₹)",
                marker=dict(color="#6366F1", cornerradius=6),
                opacity=0.88,
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
                line=dict(color="#F59E0B", width=2.8, shape="spline"),
                marker=dict(size=7.5, color="#FFFFFF", line=dict(color="#F59E0B", width=2.2)),
            ),
            secondary_y=True,
        )
        _style_fig(fig_rev, height=245, margins=dict(l=8, r=8, t=26, b=6), hovermode="x unified")
        fig_rev.update_yaxes(range=[0, max(df_7d["Revenue"].max(), 1) * 1.30], secondary_y=False)
        fig_rev.update_yaxes(range=[0, max(df_7d["AOV"].max(), 1) * 1.38], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_rev, use_container_width=True)
        _html(f'<div class="viz-info"><b>7D Revenue:</b> Gross <b>₹{tot_7d_rev:,.0f}</b> · 7-Day Avg AOV: <b>₹{avg_7d_aov:,.0f}</b>.</div></div>')

    with s1_r:
        _html(f"""
        <div class="kpi-box" style="--accent:#10B981;">
            <div class="kpi-head"><span class="kpi-lbl">Total Dispatched Output ({selected_date.strftime('%d %b')})</span>{_pill(disp_diff, disp_prev_cnt)}</div>
            <div class="kpi-main-num">{disp_day_cnt:,}</div>
            <div class="kpi-foot">Prev Day ({prev_date.strftime('%d %b')}): <b>{disp_prev_cnt:,}</b> Dispatched</div>
        </div>
        """)
        st.plotly_chart(
            _spark(df_7d["Date"], df_7d["Dispatched"], "#10B981", "rgba(16, 185, 129, 0.08)"),
            use_container_width=True,
        )

        _html('<div class="viz-card"><div class="viz-heading">Dispatched Orders (7 Days)</div>')
        fig_dp = go.Figure(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Dispatched"],
                name="Dispatched",
                marker=dict(color="#10B981", cornerradius=6),
                text=[f"<b>{v}</b>" for v in df_7d["Dispatched"]],
                textposition="outside",
                textfont=dict(color="#065F46", size=11),
            )
        )
        _style_fig(fig_dp, height=235, margins=dict(l=8, r=8, t=26, b=6), showlegend=False)
        fig_dp.update_yaxes(range=[0, max(df_7d["Dispatched"].max(), 1) * 1.30])
        st.plotly_chart(fig_dp, use_container_width=True)
        _html(f'<div class="viz-info"><b>Dispatch Summary:</b> Total <b>{tot_7d_disp:,}</b> dispatches in 7 days · Peak: <b>{int(df_7d["Dispatched"].max()):,}</b> · Avg: <b>{tot_7d_disp/7:.1f}/day</b>.</div></div>')

        _html('<div class="viz-card"><div class="viz-heading">Carrier-wise Daily Dispatch (Delhivery vs DTDC)</div>')
        fig_car = go.Figure()
        fig_car.add_trace(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Delhivery"],
                name="Delhivery",
                marker=dict(color="#0EA5E9", cornerradius=5),
                text=df_7d["Delhivery"],
                textposition="inside",
            )
        )
        fig_car.add_trace(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["DTDC"],
                name="DTDC",
                marker=dict(color="#8B5CF6", cornerradius=5),
                text=df_7d["DTDC"],
                textposition="inside",
            )
        )
        _style_fig(fig_car, height=215, margins=dict(l=8, r=8, t=24, b=6), hovermode="x unified")
        fig_car.update_layout(barmode="stack")
        st.plotly_chart(fig_car, use_container_width=True)
        _html(f'<div class="viz-info"><b>7D Carrier Parcels:</b> Delhivery: <b>{tot_7d_delh:,}</b> | DTDC: <b>{tot_7d_dtdc:,}</b>.</div></div>')

    _html('<div class="sec-bar">Section 2 — Undispatched Orders, Fulfilled, Daily RTO & Exchange (7 Days)</div>')
    s2_1, s2_2, s2_3, s2_4 = st.columns(4)
    with s2_1:
        _html('<div class="viz-card"><div class="viz-heading">Undispatched Orders (7D)</div>')
        fig_bl = go.Figure(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Undispatched"],
                marker=dict(color="#F43F5E", cornerradius=6),
                text=[f"<b>{v}</b>" for v in df_7d["Undispatched"]],
                textposition="outside",
                textfont=dict(color="#9F1239", size=10.5),
            )
        )
        _style_fig(fig_bl, height=210, margins=dict(l=6, r=6, t=24, b=6), showlegend=False)
        fig_bl.update_yaxes(range=[0, max(df_7d["Undispatched"].max(), 1) * 1.34])
        st.plotly_chart(fig_bl, use_container_width=True)
        _html(f'<div class="viz-info"><b>Total Undispatched (7D):</b> <b>{tot_7d_undisp:,}</b></div></div>')

    with s2_2:
        _html('<div class="viz-card"><div class="viz-heading">Daily Fulfilled (7D)</div>')
        fig_fl = go.Figure(
            go.Scatter(
                x=df_7d["Date"],
                y=df_7d["Fulfilled"],
                mode="lines+markers+text",
                fill="tozeroy",
                fillcolor="rgba(124, 58, 237, 0.16)",
                line=dict(color="#7C3AED", width=2.8, shape="spline"),
                marker=dict(size=7, color="#FFFFFF", line=dict(color="#7C3AED", width=2.2)),
                text=[f"<b>{v}</b>" for v in df_7d["Fulfilled"]],
                textposition="top center",
                textfont=dict(color="#5B21B6", size=10.5),
            )
        )
        _style_fig(fig_fl, height=210, margins=dict(l=6, r=6, t=24, b=6), showlegend=False)
        fig_fl.update_yaxes(range=[0, max(df_7d["Fulfilled"].max(), 1) * 1.36])
        st.plotly_chart(fig_fl, use_container_width=True)
        _html(f'<div class="viz-info"><b>Total Fulfilled:</b> <b>{tot_7d_ful:,}</b></div></div>')

    with s2_3:
        _html('<div class="viz-card"><div class="viz-heading">Daily RTO (7D)</div>')
        fig_rto = go.Figure(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["RTO"],
                marker=dict(color="#EF4444", cornerradius=6),
                text=[f"<b>{v}</b>" for v in df_7d["RTO"]],
                textposition="outside",
                textfont=dict(color="#991B1B", size=10.5),
            )
        )
        _style_fig(fig_rto, height=210, margins=dict(l=6, r=6, t=24, b=6), showlegend=False)
        fig_rto.update_yaxes(range=[0, max(df_7d["RTO"].max(), 1) * 1.36])
        st.plotly_chart(fig_rto, use_container_width=True)
        _html(f'<div class="viz-info"><b>7D RTO Count:</b> <b>{tot_7d_rto:,}</b></div></div>')

    with s2_4:
        _html('<div class="viz-card"><div class="viz-heading">Daily Exchange (7D)</div>')
        fig_ex = go.Figure(
            go.Bar(
                x=df_7d["Date"],
                y=df_7d["Exchange"],
                marker=dict(color="#8B5CF6", cornerradius=6),
                text=[f"<b>{v}</b>" for v in df_7d["Exchange"]],
                textposition="outside",
                textfont=dict(color="#5B21B6", size=10.5),
            )
        )
        _style_fig(fig_ex, height=210, margins=dict(l=6, r=6, t=24, b=6), showlegend=False)
        fig_ex.update_yaxes(range=[0, max(df_7d["Exchange"].max(), 1) * 1.36])
        st.plotly_chart(fig_ex, use_container_width=True)
        _html(f'<div class="viz-info"><b>7D Exchange Pickups:</b> <b>{tot_7d_ex:,}</b></div></div>')

    # --------------------------------------------------------------------------
    # Section 2B — Daily RTO Status & Daily Exchange Status (Chart + Full Excel)
    # --------------------------------------------------------------------------
    _html('<div class="sec-bar">Section 2B — Daily RTO Status & Daily Exchange Status (7 Days + Full Data Excel)</div>')
    s2b_l, s2b_r = st.columns(2)
    status_palette = ["#EF4444", "#F97316", "#F59E0B", "#8B5CF6", "#0EA5E9", "#10B981", "#EC4899", "#64748B"]

    with s2b_l:
        _html('<div class="viz-card"><div class="viz-heading">🚚 Daily RTO Status Breakdown (7 Days)</div>')
        rto_7d_df = f_disp[f_disp["_disp_d"].isin(dates_7d) & rto_mask].copy()
        st_col_d = _find_col(rto_7d_df, ["Shipment_Status", "Status"]) if not rto_7d_df.empty else None
        if not rto_7d_df.empty:
            rto_7d_df["_rto_st"] = (
                rto_7d_df[st_col_d].fillna("RTO").astype(str).str.strip().replace("", "RTO")
                if st_col_d
                else "RTO"
            )
            rto_st_piv = pd.DataFrame(0, index=date_lbls_7d, columns=sorted(rto_7d_df["_rto_st"].unique().tolist()))
            for d_k, d_lbl in zip(dates_7d, date_lbls_7d):
                sub_d = rto_7d_df[rto_7d_df["_disp_d"] == d_k]
                if not sub_d.empty:
                    vc = sub_d.groupby("_rto_st")["Base_Order_ID"].nunique()
                    for k_st, v_cnt in vc.items():
                        rto_st_piv.loc[d_lbl, k_st] = int(v_cnt)

            fig_rto_st = go.Figure()
            for idx_s, st_nm in enumerate(rto_st_piv.columns):
                y_s = rto_st_piv[st_nm].to_numpy(dtype=int)
                fig_rto_st.add_trace(
                    go.Bar(
                        x=rto_st_piv.index,
                        y=y_s,
                        name=st_nm,
                        marker=dict(color=status_palette[idx_s % len(status_palette)], cornerradius=4),
                        text=[str(v) if v > 0 else "" for v in y_s],
                        textposition="inside",
                    )
                )
            _style_fig(fig_rto_st, height=245, margins=dict(l=8, r=8, t=28, b=10), hovermode="x unified")
            fig_rto_st.update_layout(barmode="stack")
            st.plotly_chart(fig_rto_st, use_container_width=True, key="daily_rto_status_chart")

            rto_full_cols = [
                c
                for c in [
                    "Base_Order_ID",
                    "Order_ID",
                    "Dispatch_Date",
                    "Order_Date",
                    "Customer_Name",
                    "Carrier",
                    "Tracking_Number",
                    "Shipment_Status",
                    "Amount",
                    "Order_Notes",
                ]
                if c in rto_7d_df.columns
            ]
            rto_full_view = rto_7d_df.sort_values(by="Dispatch_Date_dt", ascending=False)[
                rto_full_cols if rto_full_cols else rto_7d_df.columns.tolist()
            ]
            rto_sum_df = rto_st_piv.reset_index().rename(columns={"index": "Dispatch_Date"})
            rto_sum_df["Total_RTO_Orders"] = rto_st_piv.sum(axis=1).values

            st.download_button(
                label="📊 Download Full RTO Status Data (Excel)",
                data=_to_excel_bytes({"RTO_Full_Details": rto_full_view, "RTO_Daily_Summary": rto_sum_df}),
                file_name=f"daily_rto_status_full_{start_7d}_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_daily_rto_status_xlsx",
            )
            _safe_dataframe(rto_full_view, use_container_width=True, height=195, hide_index=True)
            _html(f'<div class="viz-info"><b>7D RTO Full Records:</b> <b>{len(rto_full_view):,}</b> rows ({int(rto_st_piv.values.sum()):,} unique orders) across <b>{len(rto_st_piv.columns)}</b> status(es).</div>')
        else:
            empty_rto_df = pd.DataFrame({"Dispatch_Date": date_lbls_7d, "RTO_Orders": [0] * 7})
            st.download_button(
                label="📊 Download Full RTO Status Data (Excel)",
                data=_to_excel_bytes({"RTO_Full_Details": pd.DataFrame(), "RTO_Daily_Summary": empty_rto_df}),
                file_name=f"daily_rto_status_full_{start_7d}_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_daily_rto_status_empty_xlsx",
            )
            st.info("No RTO orders in the selected 7-day window.")
        _html("</div>")

    with s2b_r:
        _html('<div class="viz-card"><div class="viz-heading">🔄 Daily Exchange Status Breakdown (7 Days)</div>')
        ex_7d_df = f_rev[f_rev["_rev_d"].isin(dates_7d)].copy() if (not f_rev.empty and "_rev_d" in f_rev.columns) else pd.DataFrame()
        ex_st_col = (
            _find_col(ex_7d_df, ["Reverse_Status", "Return_Status", "Exchange_Status", "Status"])
            if not ex_7d_df.empty
            else None
        )
        ex_id_col = _find_col(ex_7d_df, ["Order_ID", "Base_Order_ID"]) if not ex_7d_df.empty else None
        if not ex_7d_df.empty:
            ex_7d_df["_ex_st"] = (
                ex_7d_df[ex_st_col].fillna("Exchange").astype(str).str.strip().replace("", "Exchange")
                if ex_st_col
                else "Exchange"
            )
            ex_st_piv = pd.DataFrame(0, index=date_lbls_7d, columns=sorted(ex_7d_df["_ex_st"].unique().tolist()))
            for d_k, d_lbl in zip(dates_7d, date_lbls_7d):
                sub_e = ex_7d_df[ex_7d_df["_rev_d"] == d_k]
                if not sub_e.empty:
                    vc_e = sub_e.groupby("_ex_st")[ex_id_col].nunique() if ex_id_col else sub_e.groupby("_ex_st").size()
                    for k_st, v_cnt in vc_e.items():
                        ex_st_piv.loc[d_lbl, k_st] = int(v_cnt)

            fig_ex_st = go.Figure()
            for idx_e, st_nm in enumerate(ex_st_piv.columns):
                y_e = ex_st_piv[st_nm].to_numpy(dtype=int)
                fig_ex_st.add_trace(
                    go.Bar(
                        x=ex_st_piv.index,
                        y=y_e,
                        name=st_nm,
                        marker=dict(color=status_palette[(idx_e + 2) % len(status_palette)], cornerradius=4),
                        text=[str(v) if v > 0 else "" for v in y_e],
                        textposition="inside",
                    )
                )
            _style_fig(fig_ex_st, height=245, margins=dict(l=8, r=8, t=28, b=10), hovermode="x unified")
            fig_ex_st.update_layout(barmode="stack")
            st.plotly_chart(fig_ex_st, use_container_width=True, key="daily_ex_status_chart")

            ex_full_cols = [c for c in ex_7d_df.columns if not c.startswith("_") and not c.endswith("_dt")]
            ex_sort_col = "Pickup_Date_dt" if "Pickup_Date_dt" in ex_7d_df.columns else None
            ex_full_view = (
                ex_7d_df.sort_values(by=ex_sort_col, ascending=False)[ex_full_cols]
                if ex_sort_col
                else ex_7d_df[ex_full_cols]
            )
            ex_sum_df = ex_st_piv.reset_index().rename(columns={"index": "Pickup_Date"})
            ex_sum_df["Total_Exchange_Orders"] = ex_st_piv.sum(axis=1).values

            st.download_button(
                label="📊 Download Full Exchange Status Data (Excel)",
                data=_to_excel_bytes({"Exchange_Full_Details": ex_full_view, "Exchange_Daily_Summary": ex_sum_df}),
                file_name=f"daily_exchange_status_full_{start_7d}_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_daily_ex_status_xlsx",
            )
            _safe_dataframe(ex_full_view, use_container_width=True, height=195, hide_index=True)
            _html(f'<div class="viz-info"><b>7D Exchange Full Records:</b> <b>{len(ex_full_view):,}</b> rows ({int(ex_st_piv.values.sum()):,} unique orders) across <b>{len(ex_st_piv.columns)}</b> status(es).</div>')
        else:
            empty_ex_df = pd.DataFrame({"Pickup_Date": date_lbls_7d, "Exchange_Orders": [0] * 7})
            st.download_button(
                label="📊 Download Full Exchange Status Data (Excel)",
                data=_to_excel_bytes({"Exchange_Full_Details": pd.DataFrame(), "Exchange_Daily_Summary": empty_ex_df}),
                file_name=f"daily_exchange_status_full_{start_7d}_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_daily_ex_status_empty_xlsx",
            )
            st.info("No exchange records in the selected 7-day window.")
        _html("</div>")

    _html('<div class="sec-bar">Section 3 — MOM RTO & Actionable Unfulfilled Orders</div>')
    s3_1, s3_2 = st.columns([1.0, 1.6])
    with s3_1:
        _html('<div class="viz-card"><div class="viz-heading">RTO Count Analysis MOM</div>')
        rto_m = f_disp[rto_mask].copy()
        rto_m = rto_m[rto_m["Dispatch_Date_dt"].dt.date <= selected_date]
        rto_m["YM"] = rto_m["Dispatch_Date_dt"].dt.to_period("M")
        mom_s = rto_m.groupby("YM")["Base_Order_ID"].nunique().tail(5)
        m_lbls = [p.strftime("%b") for p in mom_s.index]
        m_vals = mom_s.values
        indigo_shades = ["#818CF8", "#6366F1", "#4F46E5", "#312E81", "#A5B4FC"][: len(m_vals)]
        fig_mom = go.Figure(
            go.Bar(
                x=m_lbls,
                y=m_vals,
                marker=dict(color=indigo_shades, cornerradius=6),
                text=[f"<b>{v}</b>" for v in m_vals],
                textposition="outside",
                textfont=dict(size=10.5),
            )
        )
        _style_fig(fig_mom, height=240, margins=dict(l=6, r=6, t=24, b=6), showlegend=False)
        fig_mom.update_yaxes(range=[0, max(list(m_vals) + [1]) * 1.30])
        st.plotly_chart(fig_mom, use_container_width=True)
        peak_m_txt = f"{m_lbls[int(np.argmax(m_vals))]} ({int(np.max(m_vals)):,})" if len(m_vals) > 0 else "N/A"
        _html(f'<div class="viz-info"><b>Peak Month:</b> <b>{peak_m_txt}</b></div></div>')

    with s3_2:
        _html(f'<div class="viz-card"><div class="viz-heading">Actionable Unfulfilled Orders ({latest_ym_val}: {latest_month_unful_cnt})</div>')
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
        pending_view = latest_month_unful_df.sort_values(by="Order_Date_dt", ascending=False)[show_cols]
        _safe_dataframe(pending_view, use_container_width=True, height=235, hide_index=True)
        st.download_button(
            label="⬇️ Download Unfulfilled Orders CSV",
            data=pending_view.to_csv(index=False).encode("utf-8"),
            file_name=f"unfulfilled_{latest_ym_val}_{selected_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="dl_daily_unful",
        )
        _html("</div>")


# ==============================================================================
# 7. PAGE 2: SHOPIFY ANALYSIS (BANNER ON TOP + RTO & RETURN CONTROL AT BOTTOM)
# ==============================================================================
def render_shopify_page():
    if model_src is None:
        st.warning(f"Model file `{MODEL_FILENAME}` was not found in GitHub or local folders.")
        return

    df_orders, df_disp, df_rev = load_model_excel(model_src)
    valid_order_dates = df_orders["Order_Date_dt"].dropna()
    if valid_order_dates.empty:
        st.error("No valid dates found in Order_Date.")
        return

    min_d = valid_order_dates.min().date()
    max_d = valid_order_dates.max().date()

    avail_months_shp = sorted(valid_order_dates.dt.to_period("M").astype(str).unique().tolist(), reverse=True)
    latest_m_shp = avail_months_shp[0]
    def_end_shp = _resolve_default_latest_date(min_d, max_d)
    def_start_shp, _ = _month_bounds(latest_m_shp, min_d, def_end_shp)
    _sync_refresh_dates("shp", min_d, max_d, def_start_shp, def_end_shp)

    disp_start = st.session_state.get("shp_start_date", def_start_shp)
    disp_end = st.session_state.get("shp_end_date", def_end_shp)

    _html(f"""
    <div class="exec-banner">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Shopify Analysis</div>
                <div class="exec-sub">Pure RTO & Cancelled Exchange Returns, Financial KPIs & SKU/Size Return Control</div>
            </div>
        </div>
        <div class="exec-pill">📅 Created: {disp_start.strftime('%d %b %Y')} — {disp_end.strftime('%d %b %Y')}</div>
    </div>
    """)

    f_c1, f_c2, f_c3, f_c4 = st.columns([1.15, 1.05, 1.0, 1.0])
    with f_c1:
        sel_m_shp = st.selectbox(
            "🗓️ Month-wise Filter",
            options=["Latest Month (" + latest_m_shp + ")"] + avail_months_shp + ["All Available Dates"],
            index=0,
            key="shp_month_sel",
        )
    with f_c2:
        preset = st.selectbox(
            "📅 Quick Preset",
            ["Month / Latest", "01 Oct – 05 Nov 2026", "01 Sep – 14 Sep 2026", "All Available Dates"],
            index=0,
            key="shp_preset",
        )
    if preset == "01 Sep – 14 Sep 2026":
        p_s = min(max(datetime.date(2026, 9, 1), min_d), max_d)
        p_e = max(min(datetime.date(2026, 9, 14), max_d), min_d)
    elif preset == "All Available Dates" or sel_m_shp == "All Available Dates":
        p_s, p_e = min_d, max_d
    elif preset == "01 Oct – 05 Nov 2026":
        p_s = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        p_e = max(min(datetime.date(2026, 11, 5), max_d), min_d)
    else:
        chosen_m = latest_m_shp if sel_m_shp.startswith("Latest Month") else sel_m_shp
        p_s, p_e = _month_bounds(chosen_m, min_d, max_d)

    if st.session_state.get("_shp_last_choice") != (sel_m_shp, preset):
        st.session_state["_shp_last_choice"] = (sel_m_shp, preset)
        st.session_state["shp_start_date"] = p_s
        st.session_state["shp_end_date"] = p_e
        st.rerun()

    with f_c3:
        start_date = st.date_input("📅 Start Date", min_value=min_d, max_value=max_d, key="shp_start_date")
    with f_c4:
        end_date = st.date_input("📅 End Date", min_value=min_d, max_value=max_d, key="shp_end_date")

    if start_date > end_date:
        st.error("Start Date must be on or before End Date.")
        return

    p_orders = df_orders[
        (df_orders["Order_Date_dt"].dt.date >= start_date)
        & (df_orders["Order_Date_dt"].dt.date <= end_date)
    ].copy()

    fin_status_col = _find_col(p_orders, ["Financial_Status"])
    if fin_status_col:
        p_orders = p_orders[
            p_orders[fin_status_col].fillna("").astype(str).str.strip().str.lower() != "voided"
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
                "Customer_Region",
                "Shipping_State",
                "State",
                "Shipping_City",
            ]
            if c in p_orders.columns and (c == base_oid_col or c not in p_disp.columns)
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
            (p_disp[del_col_d].notna() & (p_disp[del_col_d].astype(str).str.strip() != ""))
            if del_col_d
            else pd.Series([False] * len(p_disp))
        )
        is_rto = p_disp["Is_RTO"].astype(bool) if "Is_RTO" in p_disp.columns else pd.Series([False] * len(p_disp))
        is_del = (
            p_disp["Is_Delivered"].astype(bool)
            if "Is_Delivered" in p_disp.columns
            else pd.Series([False] * len(p_disp))
        )
        is_bad = status_u.isin(["CANCELLED", "CANCELED", "LOST"])

        p_disp["True_Delivered"] = (
            (is_del | (status_u.isin(["SHIPPED", "PROCESSING", "OUT_FOR_DELIVERY"]) & has_del))
            & (~is_rto)
            & (~is_bad)
        )
        p_disp["True_In_Transit"] = (
            (~p_disp["True_Delivered"]) & (~is_rto) & (~is_bad) & (status_u != "UNDELIVERED")
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
        p_disp["RTO_Pending_Hub"] = is_rto & (~has_del) & (~status_u.isin(received_hub_tokens))
    else:
        if not p_disp.empty:
            p_disp["True_Delivered"] = False
            p_disp["True_In_Transit"] = False
            p_disp["RTO_Pending_Hub"] = False

    dispatched_ids = set(p_disp[disp_base_col].dropna()) if (not p_disp.empty and disp_base_col) else set()
    not_dispatched = p_orders[~p_orders[base_oid_col].isin(dispatched_ids)].copy() if base_oid_col else pd.DataFrame()

    del_oids = (
        set(p_disp[p_disp["True_Delivered"]][disp_base_col].dropna())
        if (not p_disp.empty and disp_base_col)
        else set()
    )
    rto_all_oids = (
        set(p_disp[p_disp["Is_RTO"]][disp_base_col].dropna()) if (not p_disp.empty and disp_base_col) else set()
    )
    rto_oids = rto_all_oids - del_oids

    rto_pending_hub_df = p_disp[p_disp["RTO_Pending_Hub"]].copy() if not p_disp.empty else pd.DataFrame()
    rto_pending_hub_oids = (
        set(rto_pending_hub_df[disp_base_col].dropna())
        if (not rto_pending_hub_df.empty and disp_base_col)
        else set()
    )
    int_oids = (
        (set(p_disp[p_disp["True_In_Transit"]][disp_base_col].dropna()) - del_oids - rto_oids)
        if (not p_disp.empty and disp_base_col)
        else set()
    )

    rev_base_col = _find_col(df_rev, ["Base_Order_ID", "Order_ID"]) if not df_rev.empty else None
    rev_order_id_col = _find_col(df_rev, ["Order_ID", "Base_Order_ID"]) if not df_rev.empty else None
    rev_status_col = (
        _find_col(df_rev, ["Reverse_Status", "Return_Status", "Exchange_Status", "Status"])
        if not df_rev.empty
        else None
    )

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
        set(p_rev_cancelled[rev_base_col].dropna()) if (not p_rev_cancelled.empty and rev_base_col) else set()
    )
    all_affected_ret_oids = rto_order_ids_set.union(canc_exch_order_ids_set)

    tot_ret_amt = (
        float(p_orders_uniq[p_orders_uniq[base_oid_col].isin(all_affected_ret_oids)]["Order_Total"].sum())
        if (len(p_orders_uniq) > 0 and base_oid_col)
        else 0.0
    )
    net_rev = max(gross_rev - tot_ret_amt, 0.0)
    realized_deliv_rev = (
        float(p_orders_uniq[p_orders_uniq[base_oid_col].isin(del_oids)]["Order_Total"].sum())
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
        st.info(f"No orders found between {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}.")
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
            _html('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Revenue Trend</div>')
            p_orders_uniq["Order_Date_Only"] = p_orders_uniq["Order_Date_dt"].dt.date
            daily = (
                p_orders_uniq.groupby("Order_Date_Only")
                .agg(Orders=(base_oid_col, "nunique"), Revenue=("Order_Total", "sum"))
                .reset_index()
                .sort_values("Order_Date_Only")
            )
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
                    x=daily["Date_Label"],
                    y=daily["Orders"],
                    name="Unique Orders",
                    marker=dict(color="#6366F1", cornerradius=6),
                    opacity=0.88,
                    text=daily["Orders"],
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(size=10, color="#312E81", family="Plus Jakarta Sans"),
                    hovertemplate="<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig_dual.add_trace(
                go.Scatter(
                    x=daily["Date_Label"],
                    y=daily["Rev_Lakhs"],
                    name="Revenue (₹ Lakhs)",
                    mode="lines+markers",
                    fill="tozeroy",
                    fillcolor="rgba(236, 72, 153, 0.08)",
                    line=dict(color="#EC4899", width=3, shape="spline"),
                    marker=dict(size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")),
                    customdata=daily["Custom_Hover"],
                    hovertemplate="Revenue: %{customdata}<extra></extra>",
                ),
                secondary_y=True,
            )
            max_ord_y = max(float(daily["Orders"].max()) * 1.28, 5.0) if not daily.empty else 10.0
            max_rev_y = max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5) if not daily.empty else 1.0
            _style_fig(fig_dual, height=410, margins=dict(l=15, r=15, t=40, b=60), hovermode="x unified")
            fig_dual.update_layout(bargap=0.28)
            fig_dual.update_xaxes(tickangle=-45, tickfont=dict(size=11, color="#475569"), nticks=18)
            fig_dual.update_yaxes(title_text="Unique Orders", range=[0, max_ord_y], secondary_y=False)
            fig_dual.update_yaxes(title_text="Revenue (₹ Lakhs)", range=[0, max_rev_y], showgrid=False, secondary_y=True)
            st.plotly_chart(fig_dual, use_container_width=True)

            _html('<div style="font-size:13px; font-weight:700; color:#334155; margin-top:10px; margin-bottom:6px;">📋 Day-Wise Orders & Revenue Verification</div>')
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
            d_verify["Date"] = pd.to_datetime(d_verify["Order_Date_Only"]).dt.strftime("%d %b %Y")
            d_verify["AOV_INR"] = np.where(
                d_verify["Unique_Orders"] > 0, (d_verify["Revenue_INR"] / d_verify["Unique_Orders"]).round(0), 0
            )
            d_verify["Revenue_INR"] = d_verify["Revenue_INR"].round(2)
            d_verify["Discount_INR"] = d_verify["Discount_INR"].round(2)
            d_verify["Shipping_INR"] = d_verify["Shipping_INR"].round(2)
            _safe_dataframe(
                d_verify[["Date", "Unique_Orders", "Revenue_INR", "AOV_INR", "Discount_INR", "Shipping_INR"]],
                use_container_width=True,
                height=210,
                hide_index=True,
            )
            _html("</div>")

        with c_right:
            _html('<div class="card-box"><div class="card-title">🎯 Order-to-Delivery Funnel (Unique Orders)</div>')
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
            funnel_colors = ["#4F46E5", "#0EA5E9", "#10B981", "#EF4444", "#E11D48", "#EA580C", "#F59E0B", "#94A3B8"]
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
            _style_fig(fig_fun, height=410, margins=dict(l=10, r=60, t=20, b=20), showlegend=False)
            fig_fun.update_xaxes(range=[0, max(funnel_vals + [1]) * 1.22])
            fig_fun.update_yaxes(showgrid=False, tickfont=dict(size=12))
            st.plotly_chart(fig_fun, use_container_width=True)
            _html("</div>")

    with tab2:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            _html(f'<div class="sub-kpi"><div><div class="sub-kpi-lbl">Total Returns Display</div><div class="sub-kpi-val">{tot_ret_cnt:,} ({tot_ret_pct:.2f}%)</div></div><div class="sub-kpi-ico" style="background:#FEF2F2;">↩️</div></div>')
        with m2:
            _html(f'<div class="sub-kpi"><div><div class="sub-kpi-lbl">Total Return Amount</div><div class="sub-kpi-val">₹{tot_ret_amt:,.2f}</div></div><div class="sub-kpi-ico" style="background:#FFF1F2;">💸</div></div>')
        with m3:
            _html(f'<div class="sub-kpi"><div><div class="sub-kpi-lbl">Pure RTO Orders</div><div class="sub-kpi-val">{pure_rto_cnt:,}</div></div><div class="sub-kpi-ico" style="background:#FFEDD5;">🚚</div></div>')
        with m4:
            _html(f'<div class="sub-kpi"><div><div class="sub-kpi-lbl">Exchanged Cancelled</div><div class="sub-kpi-val">{canc_exch_cnt:,}</div></div><div class="sub-kpi-ico" style="background:#FCE7F3;">❌</div></div>')
        with m5:
            _html(f'<div class="sub-kpi"><div><div class="sub-kpi-lbl">Active Exchange Orders</div><div class="sub-kpi-val">{exch_cnt:,}</div></div><div class="sub-kpi-ico" style="background:#F3E8FF;">🔄</div></div>')

        # Section 1: Pure RTO Analysis
        _html(f"""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: Pure RTO Analysis (Pure RTO: {pure_rto_cnt:,} | Cancelled Exchanges: {canc_exch_cnt:,} | Total Returns: {tot_ret_cnt:,})</div>
            <div class="sec-sub">RTO Status Donut, Region & State-wise RTO Returns & Day-Wise RTO Orders Trend</div>
        </div>
        """)

        rto_df = p_disp[p_disp["Is_RTO"]].copy() if (not p_disp.empty and "Is_RTO" in p_disp.columns) else pd.DataFrame()
        rto_c1, rto_c2, rto_c3 = st.columns([1.05, 1.1, 1.35])

        with rto_c1:
            _html('<div class="card-box"><div class="card-title">🍩 RTO Status Breakdown (Donut)</div>')
            if not rto_df.empty and disp_base_col:
                st_col_rto = _find_col(rto_df, ["Shipment_Status", "Status"])
                if st_col_rto:
                    rto_st_agg = (
                        rto_df.groupby(rto_df[st_col_rto].fillna("RTO").astype(str).str.strip())[disp_base_col]
                        .nunique()
                        .reset_index(name="Count")
                    )
                    rto_st_agg.columns = ["Status", "Count"]
                else:
                    rto_st_agg = pd.DataFrame(
                        {
                            "Status": ["RTO Pending Hub", "RTO Received Hub"],
                            "Count": [rto_hub_orders, max(pure_rto_cnt - rto_hub_orders, 0)],
                        }
                    )
                rto_st_agg = rto_st_agg[rto_st_agg["Count"] > 0]
                st.plotly_chart(
                    _make_donut_fig(
                        rto_st_agg["Status"].tolist(),
                        rto_st_agg["Count"].tolist(),
                        ["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6", "#10B981"],
                        f"<b>{pure_rto_cnt:,}</b><br>Pure RTO",
                    ),
                    use_container_width=True,
                    key="shp_s1_rto_donut",
                )
                top_rto_st = rto_st_agg.sort_values("Count", ascending=False).iloc[0]
                _html(f'<div class="viz-info"><b>Top RTO Status:</b> <b>{top_rto_st["Status"]}</b> ({int(top_rto_st["Count"]):,}) · Pending Hub: <b>{rto_hub_orders:,}</b>.</div>')
            else:
                st.info("No RTO orders in selected period.")
            _html("</div>")

        with rto_c2:
            _html('<div class="card-box"><div class="card-title">🗺️ Region & State-wise RTO Returns</div>')
            if not rto_df.empty and disp_base_col:
                r_col_d = _find_col(rto_df, ["Customer_Region", "Region"])
                s_col_d = _find_col(rto_df, ["Shipping_State", "State"])
                if r_col_d and s_col_d:
                    rto_df["Region_State_Lbl"] = (
                        rto_df[r_col_d].fillna("Unknown").astype(str).str.strip()
                        + " — "
                        + rto_df[s_col_d].fillna("Unknown").astype(str).str.strip()
                    )
                    geo_rto = (
                        rto_df.groupby("Region_State_Lbl")[disp_base_col]
                        .nunique()
                        .reset_index(name="RTO_Orders")
                        .sort_values("RTO_Orders", ascending=True)
                        .tail(8)
                    )
                    y_lbl_col = "Region_State_Lbl"
                else:
                    fallback_col = r_col_d or s_col_d or _find_col(rto_df, ["Shipping_City", "City"])
                    geo_rto = (
                        rto_df.groupby(rto_df[fallback_col].fillna("Unknown").astype(str).str.strip())[disp_base_col]
                        .nunique()
                        .reset_index(name="RTO_Orders")
                        .sort_values("RTO_Orders", ascending=True)
                        .tail(8)
                    )
                    y_lbl_col = fallback_col

                fig_geo_rto = go.Figure(
                    go.Bar(
                        y=geo_rto[y_lbl_col],
                        x=geo_rto["RTO_Orders"],
                        orientation="h",
                        marker=dict(color="#0284C7", cornerradius=8),
                        text=geo_rto["RTO_Orders"],
                        textposition="outside",
                        cliponaxis=False,
                    )
                )
                _style_fig(fig_geo_rto, height=370, margins=dict(l=10, r=45, t=20, b=20), showlegend=False)
                fig_geo_rto.update_xaxes(range=[0, max(float(geo_rto["RTO_Orders"].max()) * 1.28, 3.0)])
                st.plotly_chart(fig_geo_rto, use_container_width=True, key="shp_s1_geo_rto")
                top_geo_row = geo_rto.iloc[-1]
                _html(f'<div class="viz-info"><b>Highest RTO Segment:</b> <b>{top_geo_row[y_lbl_col]}</b> ({int(top_geo_row["RTO_Orders"]):,} orders).</div>')
            else:
                st.info("No RTO region/state data.")
            _html("</div>")

        with rto_c3:
            _html('<div class="card-box"><div class="card-title">📅 Day-Wise RTO Orders Analysis</div>')
            if not rto_df.empty and "Order_Date_dt" in rto_df.columns and disp_base_col:
                d_rto = (
                    rto_df.groupby(rto_df["Order_Date_dt"].dt.date)[disp_base_col]
                    .nunique()
                    .reset_index(name="RTO_Count")
                    .sort_values("Order_Date_dt")
                )
                d_rto["Date_Lbl"] = pd.to_datetime(d_rto["Order_Date_dt"]).dt.strftime("%d %b")
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
                        fill="tozeroy",
                        fillcolor="rgba(234, 88, 12, 0.10)",
                        line=dict(color="#EA580C", width=2.6, shape="spline"),
                        marker=dict(size=6.5, color="#FFFFFF", line=dict(color="#EA580C", width=2)),
                    )
                )
                _style_fig(fig_d_rto, height=370, margins=dict(l=15, r=15, t=25, b=55), showlegend=False, hovermode="x unified")
                fig_d_rto.update_xaxes(tickangle=-45, nticks=18)
                fig_d_rto.update_yaxes(range=[0, max(float(d_rto["RTO_Count"].max()) * 1.32, 3.0)])
                st.plotly_chart(fig_d_rto, use_container_width=True, key="shp_s1_day_rto")
                peak_rto_row = d_rto.loc[d_rto["RTO_Count"].idxmax()]
                _html(f'<div class="viz-info"><b>Peak RTO Day:</b> <b>{peak_rto_row["Date_Lbl"]}</b> ({int(peak_rto_row["RTO_Count"]):,}) · Avg: <b>{d_rto["RTO_Count"].mean():.1f}/day</b>.</div>')
            else:
                st.info("No day-wise RTO data.")
            _html("</div>")

        # Section 2: Exchange Analysis (INCLUDES ALL EXCHANGES — DOES NOT EXCLUDE CANCELLED)
        _html(f"""
        <div class="sec-header-exch">
            <div class="sec-title">🔄 Section 2: Exchange Analysis (All Exchanges: {int(p_rev_all[rev_order_id_col if rev_order_id_col else rev_base_col].nunique()) if not p_rev_all.empty else 0:,} | Active: {exch_cnt:,} | Cancelled: {canc_exch_cnt:,})</div>
            <div class="sec-sub">Exchanged Status by Reverse_Status, Day-Wise Exchange Orders (All Exchanges incl. Cancelled) & Reverse Logistics Table</div>
        </div>
        """)

        ex_c1, ex_c2 = st.columns([1.05, 1.45])
        with ex_c1:
            _html('<div class="card-box"><div class="card-title">🍩 Exchange Status by Reverse_Status (Donut)</div>')
            if not p_rev_all.empty:
                id_for_cnt = rev_order_id_col if rev_order_id_col else rev_base_col
                if rev_status_col and id_for_cnt:
                    ex_st_df = (
                        p_rev_all.groupby(p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip())[
                            id_for_cnt
                        ]
                        .nunique()
                        .reset_index(name="Count")
                    )
                    ex_st_df.columns = ["Reverse_Status", "Count"]
                elif rev_status_col:
                    ex_st_df = (
                        p_rev_all.groupby(p_rev_all[rev_status_col].fillna("Unknown").astype(str).str.strip())
                        .size()
                        .reset_index(name="Count")
                    )
                    ex_st_df.columns = ["Reverse_Status", "Count"]
                else:
                    ex_st_df = pd.DataFrame({"Reverse_Status": ["Recorded"], "Count": [len(p_rev_all)]})
                ex_st_df = ex_st_df[ex_st_df["Count"] > 0]
                st.plotly_chart(
                    _make_donut_fig(
                        ex_st_df["Reverse_Status"].tolist(),
                        ex_st_df["Count"].tolist(),
                        ["#10B981", "#8B5CF6", "#F59E0B", "#0EA5E9", "#EF4444", "#EC4899"],
                        f"<b>{int(ex_st_df['Count'].sum()):,}</b><br>Total Exch",
                    ),
                    use_container_width=True,
                    key="shp_s2_ex_donut",
                )
                _html(f'<div class="viz-info"><b>Exchange Mix:</b> Active <b>{exch_cnt:,}</b> vs Cancelled <b>{canc_exch_cnt:,}</b> across {len(ex_st_df)} statuses.</div>')
            else:
                st.info("No Exchange records in Fact_Reverse_Logistics for selected period.")
            _html("</div>")

        with ex_c2:
            _html('<div class="card-box"><div class="card-title">📅 Day-Wise Exchange Orders Analysis (All Exchanges)</div>')
            if not p_rev_all.empty and rev_base_col:
                rev_d = p_rev_all.merge(
                    p_orders_uniq[[base_oid_col, "Order_Date_dt"]], left_on=rev_base_col, right_on=base_oid_col, how="left"
                )
                id_for_day = (
                    rev_order_id_col if (rev_order_id_col and rev_order_id_col in rev_d.columns) else rev_base_col
                )
                # Prefer exchange Pickup_Date if present, fallback to Order_Date_dt
                if "Pickup_Date_dt" in rev_d.columns and rev_d["Pickup_Date_dt"].notna().any():
                    rev_d["_ex_plot_dt"] = rev_d["Pickup_Date_dt"].fillna(rev_d["Order_Date_dt"])
                else:
                    rev_d["_ex_plot_dt"] = rev_d["Order_Date_dt"]

                if rev_d["_ex_plot_dt"].notna().any():
                    d_ex = (
                        rev_d.dropna(subset=["_ex_plot_dt"])
                        .groupby(rev_d["_ex_plot_dt"].dt.date)[id_for_day]
                        .nunique()
                        .reset_index(name="Exchange_Count")
                        .rename(columns={"_ex_plot_dt": "Order_Date_dt"})
                        .sort_values("Order_Date_dt")
                    )
                    d_ex["Date_Lbl"] = pd.to_datetime(d_ex["Order_Date_dt"]).dt.strftime("%d %b")
                    fig_d_ex = go.Figure()
                    fig_d_ex.add_trace(
                        go.Bar(
                            x=d_ex["Date_Lbl"],
                            y=d_ex["Exchange_Count"],
                            name="Day-Wise Exchanges (All)",
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
                            fill="tozeroy",
                            fillcolor="rgba(124, 58, 237, 0.10)",
                            line=dict(color="#7C3AED", width=2.6, shape="spline"),
                            marker=dict(size=6.5, color="#FFFFFF", line=dict(color="#7C3AED", width=2)),
                        )
                    )
                    _style_fig(fig_d_ex, height=370, margins=dict(l=15, r=15, t=25, b=55), showlegend=False, hovermode="x unified")
                    fig_d_ex.update_xaxes(tickangle=-45, nticks=18)
                    fig_d_ex.update_yaxes(range=[0, max(float(d_ex["Exchange_Count"].max()) * 1.32, 3.0)])
                    st.plotly_chart(fig_d_ex, use_container_width=True, key="shp_s2_day_ex")
                    peak_ex_row = d_ex.loc[d_ex["Exchange_Count"].idxmax()]
                    _html(f'<div class="viz-info"><b>Peak Exchange Day (All):</b> <b>{peak_ex_row["Date_Lbl"]}</b> ({int(peak_ex_row["Exchange_Count"]):,}) · Total: <b>{int(d_ex["Exchange_Count"].sum()):,}</b> · Avg: <b>{d_ex["Exchange_Count"].mean():.1f}/day</b>.</div>')
                else:
                    st.info("No dated exchange records in selected period.")
            else:
                st.info("No day-wise exchange data in selected period.")
            _html("</div>")

        st.markdown(
            f"#### 🔄 Reverse Logistics Table (Fact_Reverse_Logistics — Active: {exch_cnt:,} | Cancelled: {canc_exch_cnt:,})"
        )
        if not p_rev_all.empty:
            _safe_dataframe(p_rev_all, use_container_width=True, height=250, hide_index=True)
            st.download_button(
                "⬇️ Download Reverse Logistics CSV",
                p_rev_all.to_csv(index=False).encode("utf-8"),
                f"exchanges_{start_date}_{end_date}.csv",
                "text/csv",
                key="dl_shp_exch",
            )
        else:
            st.info("No Exchange records found for the selected created orders window.")

        if not p_disp.empty and disp_base_col:
            prod_col_ctrl = _find_col(p_disp, ["Clean_Product_Name", "Product_Name", "Title", "SKU"])
            age_col_ctrl = _find_col(p_disp, ["Product_Age_Group", "Age_Group", "Size"])
            exch_all_oids = set(p_rev_all[rev_base_col].dropna()) if (not p_rev_all.empty and rev_base_col) else set()

            ctrl_df = p_disp.copy()
            ctrl_df["_sku_lbl"] = (
                ctrl_df[prod_col_ctrl].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
                if prod_col_ctrl
                else "Unknown"
            )
            if age_col_ctrl:
                ctrl_df["_size_lbl"] = (
                    ctrl_df[age_col_ctrl].fillna("Unspecified").astype(str).str.strip().replace("", "Unspecified")
                )
            else:
                ctrl_df["_size_lbl"] = _extract_size_from_text(ctrl_df["_sku_lbl"])

            ctrl_df["_is_rto_flag"] = ctrl_df[disp_base_col].isin(rto_all_oids)
            ctrl_df["_is_exch_flag"] = ctrl_df[disp_base_col].isin(exch_all_oids)
            ctrl_df["_is_issue_flag"] = ctrl_df["_is_rto_flag"] | ctrl_df["_is_exch_flag"]

            sku_grp = (
                ctrl_df[~ctrl_df["_sku_lbl"].str.lower().isin(["", "nan", "none", "unknown", "standard"])]
                .groupby("_sku_lbl")
                .agg(
                    Dispatched_Orders=(disp_base_col, "nunique"),
                    RTO_Orders=(disp_base_col, lambda s: s[ctrl_df.loc[s.index, "_is_rto_flag"]].nunique()),
                    Exchange_Return_Orders=(disp_base_col, lambda s: s[ctrl_df.loc[s.index, "_is_exch_flag"]].nunique()),
                    Total_Issue_Orders=(disp_base_col, lambda s: s[ctrl_df.loc[s.index, "_is_issue_flag"]].nunique()),
                )
                .reset_index()
                .rename(columns={"_sku_lbl": "Product_SKU"})
            )
            size_grp = (
                ctrl_df[~ctrl_df["_size_lbl"].str.lower().isin(["", "nan", "none", "unspecified", "standard / free size"])]
                .groupby("_size_lbl")
                .agg(
                    Orders=(disp_base_col, "nunique"),
                    Issues=(disp_base_col, lambda s: s[ctrl_df.loc[s.index, "_is_issue_flag"]].nunique()),
                )
                .reset_index()
                .rename(columns={"_size_lbl": "Size_Age_Group"})
            )
            _render_rto_return_control_section(
                sku_df=sku_grp,
                size_df=size_grp,
                sku_col_name="Product_SKU",
                size_col_name="Size_Age_Group",
                rto_col_name="RTO_Orders",
                ret_col_name="Exchange_Return_Orders",
                issue_col_name="Total_Issue_Orders",
                total_ord_col_name="Dispatched_Orders",
                start_date=start_date,
                end_date=end_date,
                key_prefix="shp",
            )

    with tab3:
        p1, p2 = st.columns([1.2, 1])
        with p1:
            _html('<div class="card-box"><div class="card-title">🏆 Top 7 Bestselling Delivered Products</div>')
            prod_col = _find_col(p_disp, ["Clean_Product_Name", "Product_Name", "Title"]) if not p_disp.empty else None
            if not p_disp.empty and prod_col:
                prod_s = p_disp[p_disp["True_Delivered"]][prod_col].dropna().astype(str).str.strip()
                prod_s = prod_s[
                    ~prod_s.str.lower().isin(
                        ["", "nan", "none", "garment item", "manual dispatch item", "dresses", "standard"]
                    )
                ]
                top_p = prod_s.value_counts().head(7)
                if not top_p.empty:
                    mv = top_p.max()
                    for rank, (name, cnt) in enumerate(top_p.items(), start=1):
                        pct = cnt / mv * 100
                        short = name if len(name) <= 44 else name[:44] + "..."
                        _html(f'<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{short}</span><span style="color:#DB2777;">{cnt:,} pcs</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>')
            _html("</div>")

        with p2:
            _html('<div class="card-box"><div class="card-title">👶 Top Kids Age Groups (Delivered)</div>')
            age_col = _find_col(p_disp, ["Product_Age_Group", "Age_Group", "Size"]) if not p_disp.empty else None
            if not p_disp.empty and age_col:
                age_s = p_disp[p_disp["True_Delivered"]][age_col].dropna().astype(str).str.strip()
                age_s = age_s[~age_s.str.lower().isin(["", "nan", "none", "standard / free size"])]
                top_a = age_s.value_counts().head(7).reset_index()
                top_a.columns = ["Age Group", "Count"]
                if not top_a.empty:
                    age_palette = ["#8B5CF6", "#7C3AED", "#6366F1", "#4F46E5", "#0EA5E9", "#06B6D4", "#10B981"]
                    fig_age = go.Figure(
                        go.Bar(
                            x=top_a["Age Group"],
                            y=top_a["Count"],
                            marker=dict(color=age_palette[: len(top_a)], cornerradius=8),
                            text=top_a["Count"],
                            textposition="outside",
                            cliponaxis=False,
                        )
                    )
                    _style_fig(fig_age, height=310, margins=dict(l=10, r=10, t=25, b=10), showlegend=False)
                    fig_age.update_yaxes(range=[0, max(float(top_a["Count"].max()) * 1.25, 3.0)])
                    st.plotly_chart(fig_age, use_container_width=True)
            _html("</div>")

    with tab4:
        st.markdown(f"#### 🏭 RTO Pending to Hub ({rto_hub_parcels} Parcels / {rto_hub_orders} Unique Orders)")
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
        hub_view = rto_pending_hub_df[hub_cols] if not rto_pending_hub_df.empty else pd.DataFrame(columns=hub_cols)
        _safe_dataframe(hub_view, use_container_width=True, height=280, hide_index=True)
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
                f"#### 🚚 Truly In-Transit Parcels ({int(p_disp['True_In_Transit'].sum()) if (not p_disp.empty and 'True_In_Transit' in p_disp.columns) else 0})"
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
            _safe_dataframe(it_view, use_container_width=True, height=340, hide_index=True)
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
            nd_view = not_dispatched[nd_cols] if not not_dispatched.empty else pd.DataFrame(columns=nd_cols)
            _safe_dataframe(nd_view, use_container_width=True, height=340, hide_index=True)
            st.download_button(
                "⬇️ Download Not-Dispatched CSV",
                nd_view.to_csv(index=False).encode("utf-8"),
                "not_dispatched.csv",
                "text/csv",
                key="dl_shp_nd",
            )


# ==============================================================================
# 7B. PAGE 2B: SHOPIFY FORECAST & COHORT (BANNER ON TOP + COHORT AT BOTTOM)
# ==============================================================================
def render_shopify_forecast_page():
    """Render Shopify July-to-latest-month comparison, forecast & Customer Cohort Analysis at bottom."""
    if model_src is None:
        st.warning(f"Model file `{MODEL_FILENAME}` was not found in GitHub or local folders.")
        return

    df_orders, df_disp, df_rev = load_model_excel(model_src)
    valid_dates = df_orders["Order_Date_dt"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in Order_Date.")
        return

    fin_col = _find_col(df_orders, ["Financial_Status"])
    if fin_col:
        orders_clean = df_orders[
            df_orders[fin_col].fillna("").astype(str).str.strip().str.lower() != "voided"
        ].copy()
    else:
        orders_clean = df_orders.copy()

    oid_col = _find_col(orders_clean, ["Base_Order_ID", "Order_ID", "Name"])
    if not oid_col:
        st.error("Order identifier column (Base_Order_ID / Order_ID) not found.")
        return

    orders_clean["_dt"] = orders_clean["Order_Date_dt"]
    orders_clean = orders_clean.dropna(subset=["_dt"]).copy()
    if orders_clean.empty:
        st.error("No valid non-voided order dates available.")
        return

    max_dt = orders_clean["_dt"].max().date()
    min_dt = orders_clean["_dt"].min().date()
    latest_end_fc = _resolve_default_latest_date(min_dt, max_dt)
    july_candidate = datetime.date(latest_end_fc.year, 7, 1)
    if july_candidate > latest_end_fc:
        july_candidate = datetime.date(latest_end_fc.year - 1, 7, 1)
    start_bound = max(min_dt, july_candidate)

    jul_df = orders_clean[
        (orders_clean["_dt"].dt.date >= start_bound) & (orders_clean["_dt"].dt.date <= max_dt)
    ].copy()
    if jul_df.empty:
        jul_df = orders_clean.copy()
        start_bound = jul_df["_dt"].min().date()

    avail_months_fc = sorted(orders_clean["_dt"].dt.to_period("M").astype(str).unique().tolist(), reverse=True)
    latest_m_fc = avail_months_fc[0]
    m_start_fc, _ = _month_bounds(latest_m_fc, min_dt, latest_end_fc)

    if "_shp_fc_boot_seen" not in st.session_state:
        st.session_state["_shp_fc_boot_seen"] = True
        st.session_state["shp_fc_start"] = m_start_fc
        st.session_state["shp_fc_end"] = latest_end_fc

    disp_h_fc = st.session_state.get("shp_fc_horizon", 14)

    _html(f"""
    <div class="exec-banner">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Shopify Forecast & Comparison</div>
                <div class="exec-sub">July ({start_bound.strftime('%b %Y')}) to Latest ({max_dt.strftime('%d %b %Y')}) • Period Comparison, Seasonality, Risk, Forecast & Cohort</div>
            </div>
        </div>
        <div class="exec-pill">🔮 +{disp_h_fc}d Forecast</div>
    </div>
    """)

    c_f1, c_f2, c_f3, c_f4, c_f5, c_f6 = st.columns([1.05, 0.95, 0.95, 0.9, 1.1, 0.85])
    with c_f1:
        sel_m_fc = st.selectbox(
            "🗓️ Month / Range",
            options=["Latest Month (" + latest_m_fc + ")"] + avail_months_fc + ["July to Latest"],
            index=0,
            key="shp_fc_month_sel",
        )
    if st.session_state.get("_shp_fc_last_m") != sel_m_fc:
        st.session_state["_shp_fc_last_m"] = sel_m_fc
        if sel_m_fc == "July to Latest":
            st.session_state["shp_fc_start"] = start_bound
            st.session_state["shp_fc_end"] = latest_end_fc
        else:
            m_c = latest_m_fc if sel_m_fc.startswith("Latest Month") else sel_m_fc
            ms_c, me_c = _month_bounds(m_c, min_dt, max_dt)
            st.session_state["shp_fc_start"] = ms_c
            st.session_state["shp_fc_end"] = max(me_c, latest_end_fc) if m_c == latest_m_fc else me_c
        st.rerun()

    with c_f2:
        range_start = st.date_input("📅 Start Date", min_value=min_dt, max_value=max_dt, key="shp_fc_start")
    with c_f3:
        range_end = st.date_input("📅 End Date", min_value=min_dt, max_value=max_dt, key="shp_fc_end")
    with c_f4:
        horizon_days = st.selectbox(
            "🔮 Forecast Horizon",
            options=[7, 14, 30],
            index=1,
            format_func=lambda d: f"Next {d} Days",
            key="shp_fc_horizon",
        )
    with c_f5:
        compare_mode = st.selectbox(
            "⚖️ Comparison Baseline",
            options=["Previous Equal Window", "Previous Calendar Month"],
            index=0,
            key="shp_fc_cmp_mode",
        )
    with c_f6:
        conf_level = st.selectbox(
            "🛡️ Confidence Band",
            options=[0.80, 0.90],
            index=0,
            format_func=lambda c: f"{int(c*100)}% Band",
            key="shp_fc_conf",
        )

    if range_start > range_end:
        st.error("Analysis Start Date must be on or before Analysis End Date.")
        return

    cur_df = orders_clean[
        (orders_clean["_dt"].dt.date >= range_start) & (orders_clean["_dt"].dt.date <= range_end)
    ].copy()
    cur_uniq = cur_df.drop_duplicates(subset=[oid_col]).copy() if not cur_df.empty else cur_df.copy()

    span_days = max((range_end - range_start).days + 1, 1)
    if compare_mode == "Previous Equal Window":
        prev_end = range_start - datetime.timedelta(days=1)
        prev_start = prev_end - datetime.timedelta(days=span_days - 1)
    else:
        first_of_range = datetime.date(range_start.year, range_start.month, 1)
        prev_end = first_of_range - datetime.timedelta(days=1)
        prev_start = datetime.date(prev_end.year, prev_end.month, 1)

    prev_df = orders_clean[
        (orders_clean["_dt"].dt.date >= prev_start) & (orders_clean["_dt"].dt.date <= prev_end)
    ].copy()
    prev_uniq = prev_df.drop_duplicates(subset=[oid_col]).copy() if not prev_df.empty else prev_df.copy()

    cur_orders_cnt = int(cur_uniq[oid_col].nunique()) if not cur_uniq.empty else 0
    prev_orders_cnt = int(prev_uniq[oid_col].nunique()) if not prev_uniq.empty else 0

    cur_rev = float(cur_uniq["Order_Total"].sum()) if (not cur_uniq.empty and "Order_Total" in cur_uniq.columns) else 0.0
    prev_rev = float(prev_uniq["Order_Total"].sum()) if (not prev_uniq.empty and "Order_Total" in prev_uniq.columns) else 0.0

    cur_aov = cur_rev / cur_orders_cnt if cur_orders_cnt > 0 else 0.0
    prev_aov = prev_rev / prev_orders_cnt if prev_orders_cnt > 0 else 0.0

    cur_oids_set = set(cur_uniq[oid_col].dropna().astype(str)) if not cur_uniq.empty else set()
    prev_oids_set = set(prev_uniq[oid_col].dropna().astype(str)) if not prev_uniq.empty else set()

    cur_cod_cnt = (
        int(cur_uniq[cur_uniq["Payment_Category"] == "COD"][oid_col].nunique())
        if (not cur_uniq.empty and "Payment_Category" in cur_uniq.columns)
        else 0
    )
    prev_cod_cnt = (
        int(prev_uniq[prev_uniq["Payment_Category"] == "COD"][oid_col].nunique())
        if (not prev_uniq.empty and "Payment_Category" in prev_uniq.columns)
        else 0
    )
    cur_cod_share = (cur_cod_cnt / cur_orders_cnt * 100.0) if cur_orders_cnt > 0 else 0.0
    prev_cod_share = (prev_cod_cnt / prev_orders_cnt * 100.0) if prev_orders_cnt > 0 else 0.0

    disp_oid_col = _find_col(df_disp, ["Base_Order_ID", "Order_ID"]) if not df_disp.empty else None
    cur_rto_cnt = (
        int(df_disp[df_disp[disp_oid_col].astype(str).isin(cur_oids_set) & df_disp["Is_RTO"].astype(bool)][disp_oid_col].nunique())
        if (not df_disp.empty and disp_oid_col and "Is_RTO" in df_disp.columns)
        else 0
    )
    prev_rto_cnt = (
        int(df_disp[df_disp[disp_oid_col].astype(str).isin(prev_oids_set) & df_disp["Is_RTO"].astype(bool)][disp_oid_col].nunique())
        if (not df_disp.empty and disp_oid_col and "Is_RTO" in df_disp.columns)
        else 0
    )
    cur_disp_cnt = (
        int(df_disp[df_disp[disp_oid_col].astype(str).isin(cur_oids_set)][disp_oid_col].nunique())
        if (not df_disp.empty and disp_oid_col)
        else 0
    )
    cur_rto_rate = (cur_rto_cnt / cur_disp_cnt * 100.0) if cur_disp_cnt > 0 else 0.0

    def _delta_pct(cur_v, prev_v):
        if prev_v > 0:
            return ((cur_v - prev_v) / prev_v) * 100.0
        return 0.0

    ord_chg_pct = _delta_pct(cur_orders_cnt, prev_orders_cnt)
    rev_chg_pct = _delta_pct(cur_rev, prev_rev)
    aov_chg_pct = _delta_pct(cur_aov, prev_aov)

    all_dates_idx = pd.date_range(start=range_start, end=range_end, freq="D")
    daily_cur = (
        cur_uniq.assign(_d=cur_uniq["_dt"].dt.normalize())
        .groupby("_d")
        .agg(Orders=(oid_col, "nunique"), Revenue=("Order_Total", "sum"))
        .reindex(all_dates_idx, fill_value=0.0)
    )
    daily_cur["Orders"] = daily_cur["Orders"].astype(float)
    daily_cur["Revenue"] = daily_cur["Revenue"].astype(float)

    fit_window = daily_cur.tail(min(60, len(daily_cur))).copy()
    dow_arr = fit_window.index.dayofweek
    z_score = 1.2816 if conf_level == 0.80 else 1.6449

    def _forecast_with_band(y_series: np.ndarray, days_ahead: int):
        """Forecast using recent 7-day rolling baseline, damped 14-day slope, and day-of-week seasonality."""
        fut_dates = pd.date_range(
            start=range_end + datetime.timedelta(days=1), periods=days_ahead, freq="D"
        )
        clean_y = y_series.copy()
        if len(clean_y) > 7 and clean_y[-1] == 0:
            clean_y = clean_y[:-1]

        if len(clean_y) >= 3 and np.std(clean_y) > 0:
            recent_7 = clean_y[-min(7, len(clean_y)) :]
            recent_14 = clean_y[-min(14, len(clean_y)) :]
            baseline_level = float(np.mean(recent_7))

            x_rec = np.arange(len(recent_14), dtype=float)
            raw_slope, _ = np.polyfit(x_rec, recent_14, 1)
            max_daily_step = baseline_level * 0.025
            damped_slope = float(np.clip(raw_slope * 0.45, -max_daily_step, max_daily_step))

            dow_use = dow_arr[-len(clean_y) :]
            overall_mean = max(float(np.mean(clean_y)), 1e-6)
            dow_factors = {}
            for dow_i in range(7):
                vals_d = clean_y[dow_use == dow_i]
                raw_f = float(np.mean(vals_d)) / overall_mean if len(vals_d) > 0 else 1.0
                dow_factors[dow_i] = float(np.clip(raw_f, 0.75, 1.35))
            avg_f = np.mean(list(dow_factors.values())) or 1.0
            dow_factors = {k: v / avg_f for k, v in dow_factors.items()}

            preds = []
            for step_i, dt in enumerate(fut_dates, start=1):
                effective_steps = sum(0.92 ** k for k in range(step_i))
                level_t = max(baseline_level * 0.55, baseline_level + damped_slope * effective_steps)
                preds.append(level_t * dow_factors[int(dt.dayofweek)])
            preds = np.array(preds, dtype=float)

            sigma = float(np.std(recent_14, ddof=1)) if len(recent_14) > 1 else baseline_level * 0.15
            sigma = min(sigma, baseline_level * 0.35)
            step_scale = np.sqrt(1.0 + np.arange(1, days_ahead + 1, dtype=float) / max(len(recent_14), 1))
            margin = z_score * sigma * step_scale
            lower = np.maximum(preds * 0.35, preds - margin)
            upper = preds + margin
            return fut_dates, preds, lower, upper, damped_slope

        avg_val = max(0.0, float(np.mean(clean_y))) if len(clean_y) > 0 else 0.0
        preds = np.full(days_ahead, avg_val, dtype=float)
        return fut_dates, preds, preds * 0.75, preds * 1.25, 0.0

    fut_dates, fc_orders, ord_low, ord_high, ord_slope = _forecast_with_band(
        fit_window["Orders"].to_numpy(dtype=float), horizon_days
    )
    _, fc_rev, rev_low, rev_high, rev_slope = _forecast_with_band(
        fit_window["Revenue"].to_numpy(dtype=float), horizon_days
    )

    pred_orders_total = float(np.sum(fc_orders))
    pred_rev_total = float(np.sum(fc_rev))
    pred_aov = pred_rev_total / pred_orders_total if pred_orders_total > 0 else cur_aov

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Selected Period Orders</div>
                <div class="kpi-val">{cur_orders_cnt:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">Prev: {prev_orders_cnt:,} ({ord_chg_pct:+.1f}%)</span>
            </div>
            <div class="kpi-ico" style="background:#EEF2FF;">📦</div>
        </div>
        """)
    with k2:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Selected Period Revenue</div>
                <div class="kpi-val">₹{cur_rev:,.0f}</div>
                <span class="kpi-tag" style="background:#ECFDF5; color:#059669;">Prev: ₹{prev_rev:,.0f} ({rev_chg_pct:+.1f}%)</span>
            </div>
            <div class="kpi-ico" style="background:#ECFDF5;">💰</div>
        </div>
        """)
    with k3:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Forecast Orders ({horizon_days}d)</div>
                <div class="kpi-val">{pred_orders_total:,.0f}</div>
                <span class="kpi-tag" style="background:#F5F3FF; color:#7C3AED;">Range: {np.sum(ord_low):,.0f} – {np.sum(ord_high):,.0f}</span>
            </div>
            <div class="kpi-ico" style="background:#F5F3FF;">🔮</div>
        </div>
        """)
    with k4:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Forecast Revenue ({horizon_days}d)</div>
                <div class="kpi-val">₹{pred_rev_total:,.0f}</div>
                <span class="kpi-tag" style="background:#FDF2F8; color:#BE185D;">Est. AOV: ₹{pred_aov:,.0f} ({aov_chg_pct:+.1f}%)</span>
            </div>
            <div class="kpi-ico" style="background:#FDF2F8;">📈</div>
        </div>
        """)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    trend_dir = "Upward" if rev_slope > 0 else ("Downward" if rev_slope < 0 else "Flat")
    best_dow_idx = int(np.argmax(fc_rev[: min(7, len(fc_rev))])) if len(fc_rev) > 0 else 0
    best_fc_day = fut_dates[best_dow_idx].strftime("%a (%d %b)") if len(fut_dates) > 0 else "N/A"
    best_fc_val = float(fc_rev[best_dow_idx]) if len(fc_rev) > 0 else 0.0
    expected_rto_in_fc = pred_orders_total * (cur_rto_rate / 100.0)

    _html(f"""
    <div class="viz-card">
        <div class="card-title">💡 Executive Forecast & Comparison Insights</div>
        <div style="font-size:13px; color:#1E293B; line-height:1.65;">
- <b>Period Comparison ({range_start.strftime('%d %b')}–{range_end.strftime('%d %b')} vs {prev_start.strftime('%d %b')}–{prev_end.strftime('%d %b')}):</b>
              Revenue changed by <b>{rev_chg_pct:+.1f}%</b> and orders changed by <b>{ord_chg_pct:+.1f}%</b>, while AOV shifted from <b>₹{prev_aov:,.0f}</b> to <b>₹{cur_aov:,.0f}</b>.<br>
- <b>Trend & Peak Window:</b> Recent 14-day revenue trajectory is <b>{trend_dir}</b> (<b>₹{rev_slope:+,.0f}/day</b> damped slope). Highest projected day in the forecast window is <b>{best_fc_day}</b> at <b>₹{best_fc_val:,.0f}</b>.<br>
- <b>COD & Return Watchout:</b> Current COD share is <b>{cur_cod_share:.1f}%</b> (Prev: <b>{prev_cod_share:.1f}%</b>) and historical RTO rate is <b>{cur_rto_rate:.1f}%</b> (Prev RTO orders: <b>{prev_rto_cnt:,}</b>), implying ~<b>{expected_rto_in_fc:.0f}</b> potential RTO orders across the next {horizon_days} days.
        </div>
    </div>
    """)

    _html('<div class="card-box"><div class="card-title">📈 Daily Shopify Revenue — Actual, 7D Moving Avg & Forecast Band</div>')
    roll_rev_7d = daily_cur["Revenue"].rolling(7, min_periods=1).mean()
    fig_fc_rev = go.Figure()
    fig_fc_rev.add_trace(
        go.Bar(
            x=daily_cur.index.strftime("%d %b"),
            y=daily_cur["Revenue"],
            name="Actual Revenue (₹)",
            marker=dict(color="#6366F1", cornerradius=5),
            opacity=0.84,
        )
    )
    fig_fc_rev.add_trace(
        go.Scatter(
            x=daily_cur.index.strftime("%d %b"),
            y=roll_rev_7d,
            name="7-Day Rolling Avg (₹)",
            mode="lines",
            line=dict(color="#0F172A", width=2.4, shape="spline"),
        )
    )
    fig_fc_rev.add_trace(
        go.Scatter(
            x=fut_dates.strftime("%d %b"),
            y=rev_high,
            name=f"Upper Band ({int(conf_level*100)}%)",
            mode="lines",
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig_fc_rev.add_trace(
        go.Scatter(
            x=fut_dates.strftime("%d %b"),
            y=rev_low,
            name=f"{int(conf_level*100)}% Confidence Band",
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(236, 72, 153, 0.16)",
        )
    )
    fig_fc_rev.add_trace(
        go.Scatter(
            x=fut_dates.strftime("%d %b"),
            y=fc_rev,
            name=f"Forecast Revenue ({horizon_days}d)",
            mode="lines+markers",
            line=dict(color="#EC4899", width=3, dash="dash"),
            marker=dict(size=7.5, color="#FFFFFF", line=dict(color="#EC4899", width=2.2)),
        )
    )
    _style_fig(fig_fc_rev, height=385, margins=dict(l=15, r=15, t=30, b=50), hovermode="x unified")
    fig_fc_rev.update_xaxes(tickangle=-45, nticks=20)
    st.plotly_chart(fig_fc_rev, use_container_width=True)
    _html("</div>")

    ch_l, ch_r = st.columns([1.35, 1.0])
    with ch_l:
        _html('<div class="card-box"><div class="card-title">📦 Daily Orders — Actual, 7D Avg & Forecast Band</div>')
        roll_ord_7d = daily_cur["Orders"].rolling(7, min_periods=1).mean()
        fig_fc_ord = go.Figure()
        fig_fc_ord.add_trace(
            go.Bar(
                x=daily_cur.index.strftime("%d %b"),
                y=daily_cur["Orders"],
                name="Actual Orders",
                marker=dict(color="#0EA5E9", cornerradius=5),
                opacity=0.84,
            )
        )
        fig_fc_ord.add_trace(
            go.Scatter(
                x=daily_cur.index.strftime("%d %b"),
                y=roll_ord_7d,
                name="7D Avg Orders",
                mode="lines",
                line=dict(color="#0F172A", width=2.4, shape="spline"),
            )
        )
        fig_fc_ord.add_trace(
            go.Scatter(
                x=fut_dates.strftime("%d %b"),
                y=ord_high,
                name="Upper Orders",
                mode="lines",
                line=dict(width=0),
                showlegend=False,
            )
        )
        fig_fc_ord.add_trace(
            go.Scatter(
                x=fut_dates.strftime("%d %b"),
                y=ord_low,
                name=f"{int(conf_level*100)}% Order Band",
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(16, 185, 129, 0.16)",
            )
        )
        fig_fc_ord.add_trace(
            go.Scatter(
                x=fut_dates.strftime("%d %b"),
                y=fc_orders,
                name=f"Forecast Orders ({horizon_days}d)",
                mode="lines+markers",
                line=dict(color="#10B981", width=3, dash="dash"),
                marker=dict(size=7.5, color="#FFFFFF", line=dict(color="#10B981", width=2.2)),
            )
        )
        _style_fig(fig_fc_ord, height=350, margins=dict(l=15, r=15, t=30, b=50), hovermode="x unified")
        fig_fc_ord.update_xaxes(tickangle=-45, nticks=18)
        st.plotly_chart(fig_fc_ord, use_container_width=True)
        _html("</div>")

    with ch_r:
        _html('<div class="card-box"><div class="card-title">📅 Avg Revenue by Day of Week</div>')
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_agg = (
            cur_uniq.assign(_dow=cur_uniq["_dt"].dt.day_name())
            .groupby("_dow")
            .agg(Avg_Rev=("Order_Total", "sum"), Orders=(oid_col, "nunique"))
            .reindex(dow_order)
            .fillna(0.0)
        )
        dow_counts = pd.Series(all_dates_idx.day_name()).value_counts().reindex(dow_order).fillna(1)
        dow_agg["Daily_Avg_Rev"] = (dow_agg["Avg_Rev"] / dow_counts.values).round(0)

        dow_colors = ["#818CF8", "#6366F1", "#4F46E5", "#7C3AED", "#8B5CF6", "#A855F7", "#EC4899"]
        fig_dow = go.Figure(
            go.Bar(
                x=[d[:3] for d in dow_order],
                y=dow_agg["Daily_Avg_Rev"],
                marker=dict(color=dow_colors, cornerradius=7),
                text=[f"₹{v/1000:.1f}k" if v >= 1000 else f"₹{v:.0f}" for v in dow_agg["Daily_Avg_Rev"]],
                textposition="outside",
                cliponaxis=False,
            )
        )
        _style_fig(fig_dow, height=350, margins=dict(l=10, r=10, t=30, b=35), showlegend=False)
        fig_dow.update_yaxes(range=[0, max(float(dow_agg["Daily_Avg_Rev"].max()) * 1.25, 100.0)])
        st.plotly_chart(fig_dow, use_container_width=True)
        _html("</div>")

    _html('<div class="card-box"><div class="card-title">🗓️ Monthly Shopify Performance (July to Latest Month)</div>')
    jul_uniq = jul_df.drop_duplicates(subset=[oid_col]).copy()
    jul_uniq["Year_Month"] = jul_uniq["_dt"].dt.to_period("M").astype(str)
    m_tbl = (
        jul_uniq.groupby("Year_Month")
        .agg(
            Unique_Orders=(oid_col, "nunique"),
            Gross_Revenue_INR=("Order_Total", "sum"),
        )
        .reset_index()
        .sort_values("Year_Month")
    )
    m_tbl["AOV_INR"] = np.where(
        m_tbl["Unique_Orders"] > 0, (m_tbl["Gross_Revenue_INR"] / m_tbl["Unique_Orders"]).round(0), 0
    )
    m_tbl["MoM_Revenue_Change_%"] = m_tbl["Gross_Revenue_INR"].pct_change().fillna(0.0).mul(100).round(1)
    m_tbl["Gross_Revenue_INR"] = m_tbl["Gross_Revenue_INR"].round(2)
    _safe_dataframe(m_tbl, use_container_width=True, height=220, hide_index=True)
    _html("</div>")

    st.markdown(f"#### 🔮 Future Forecast Schedule ({horizon_days} Days)")
    fc_schedule = pd.DataFrame(
        {
            "Forecast_Date": fut_dates.strftime("%Y-%m-%d"),
            "Day_of_Week": fut_dates.day_name(),
            "Predicted_Orders": np.round(fc_orders, 1),
            "Orders_Lower": np.round(ord_low, 1),
            "Orders_Upper": np.round(ord_high, 1),
            "Predicted_Revenue_INR": np.round(fc_rev, 2),
            "Revenue_Lower_INR": np.round(rev_low, 2),
            "Revenue_Upper_INR": np.round(rev_high, 2),
        }
    )
    _safe_dataframe(fc_schedule, use_container_width=True, height=260, hide_index=True)
    st.download_button(
        "⬇️ Download Shopify Forecast CSV",
        fc_schedule.to_csv(index=False).encode("utf-8"),
        f"shopify_forecast_{range_start}_{range_end}_{horizon_days}d.csv",
        "text/csv",
        key="dl_shp_forecast_csv",
    )

    _render_customer_cohort_matrix(orders_clean, max_months=8)


# ==============================================================================
# 8. PAGE 3: MYNTRA ANALYSIS (BANNER ON TOP + ACCURATE ORDER DATES + RTO CONTROL)
# ==============================================================================
def render_myntra_page():
    """Render Myntra analytics with Shopify-aligned 10 KPIs and order-creation month cohort tracking."""
    df_all, _ = load_myntra_data(myntra_src)
    if df_all.empty:
        st.warning(f"File `{MYNTRA_CONSOLIDATED_NAME}` was not found in GitHub or upload panel.")
        return

    valid_dates = df_all["order_date_dt"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in Myntra `order_date` / `order_date_dt`.")
        return

    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()

    avail_months_myn = sorted(valid_dates.dt.to_period("M").astype(str).unique().tolist(), reverse=True)
    latest_m_myn = avail_months_myn[0]
    def_start_myn, def_end_myn = _month_bounds(latest_m_myn, min_d, max_d)
    _sync_refresh_dates("myntra", min_d, max_d, def_start_myn, def_end_myn)

    disp_m_start = min(max(st.session_state.get("myntra_start_date", def_start_myn), min_d), max_d)
    disp_m_end = min(max(st.session_state.get("myntra_end_date", def_end_myn), min_d), max_d)

    _html(f"""
    <div class="exec-banner myntra">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Myntra Analysis</div>
                <div class="exec-sub">Order-Creation Month Cohort (RTO/Return/Exchange attributed to Order Date) • Shopify-Aligned KPIs</div>
            </div>
        </div>
        <div class="exec-pill">📅 Created: {disp_m_start.strftime('%d %b %Y')} — {disp_m_end.strftime('%d %b %Y')}</div>
    </div>
    """)

    oct_lbl = f"01 Oct – {min(datetime.date(max_d.year, 10, 31), max_d).strftime('%d %b %Y')}"
    jul_lbl = f"01 Jul – {max_d.strftime('%d %b %Y')}"

    f1, f2, f3, f4, f5 = st.columns([1.15, 1.05, 0.95, 0.95, 1.35])
    with f1:
        sel_m_myn = st.selectbox(
            "🗓️ Month-wise Filter",
            options=["Latest Month (" + latest_m_myn + ")"] + avail_months_myn + ["All Available Dates"],
            index=0,
            key="myn_month_sel",
        )
    with f2:
        preset = st.selectbox(
            "📅 Quick Preset",
            ["Month / Latest", oct_lbl, jul_lbl, "All Available Dates"],
            index=0,
            key="myn_preset",
        )

    if preset == oct_lbl:
        p_s = min(max(datetime.date(max_d.year, 10, 1), min_d), max_d)
        p_e = min(max(datetime.date(max_d.year, 10, 31), min_d), max_d)
    elif preset == jul_lbl:
        p_s = min(max(datetime.date(max_d.year, 7, 1), min_d), max_d)
        p_e = max_d
    elif preset == "All Available Dates" or sel_m_myn == "All Available Dates":
        p_s, p_e = min_d, max_d
    else:
        chosen_m = latest_m_myn if sel_m_myn.startswith("Latest Month") else sel_m_myn
        p_s, p_e = _month_bounds(chosen_m, min_d, max_d)

    p_s = min(max(p_s, min_d), max_d)
    p_e = min(max(p_e, min_d), max_d)

    if st.session_state.get("_myn_last_choice") != (sel_m_myn, preset):
        st.session_state["_myn_last_choice"] = (sel_m_myn, preset)
        st.session_state["myntra_start_date"] = p_s
        st.session_state["myntra_end_date"] = p_e
        st.rerun()

    all_comb_statuses = sorted(df_all["Combined_Status"].unique().tolist())

    with f3:
        start_date = st.date_input("📅 Start Date", min_value=min_d, max_value=max_d, key="myntra_start_date")
    with f4:
        end_date = st.date_input("📅 End Date", min_value=min_d, max_value=max_d, key="myntra_end_date")
    with f5:
        sel_comb_statuses = st.multiselect(
            "🔀 Combined Status", all_comb_statuses, default=all_comb_statuses, key="myn_comb"
        )

    start_date = min(max(start_date, min_d), max_d)
    end_date = min(max(end_date, min_d), max_d)

    if not sel_comb_statuses:
        sel_comb_statuses = all_comb_statuses

    if start_date > end_date:
        st.error("Start Date must be on or before End Date.")
        return

    # Filter strictly by order_date_dt (order creation date) so returns/RTO/exchanges stay in the order's creation month
    p_df = df_all[
        (df_all["order_date_dt"].dt.date >= start_date)
        & (df_all["order_date_dt"].dt.date <= end_date)
        & (df_all["Combined_Status"].isin(sel_comb_statuses))
    ].copy()

    if p_df.empty:
        st.info(
            f"No Myntra orders found between {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}. "
            f"Available Myntra order dates are {min_d.strftime('%d %b %Y')} to {max_d.strftime('%d %b %Y')}."
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
        has_pack | has_inv | p_df["Status_Clean"].isin(["delivered", "in_transit", "reverse_in_transit", "shipped"])
    )
    disp_cnt = int(p_df[is_disp_mask]["Unique_Order_Key"].nunique()) if is_disp_mask.any() else 0

    rt_l_series = p_df["Return_Type_Clean"]
    st_l_series = p_df["Status_Clean"]
    rst_l_series = p_df["Reverse_Status_Clean"].fillna("").astype(str).str.strip().str.upper()

    in_rto_sh = (
        p_df["_in_rto_returns_sheet"].astype(bool)
        if "_in_rto_returns_sheet" in p_df.columns
        else pd.Series([False] * len(p_df), index=p_df.index)
    )
    in_ex_sh = (
        p_df["_in_exchanges_sheet"].astype(bool)
        if "_in_exchanges_sheet" in p_df.columns
        else pd.Series([False] * len(p_df), index=p_df.index)
    )

    is_exch_all_mask = rt_l_series.str.contains("exchange", na=False) | in_ex_sh
    is_exch_canc_mask = is_exch_all_mask & (rst_l_series == "CANCELLED")
    is_exch_active_mask = is_exch_all_mask & (~is_exch_canc_mask)

    is_rto_mask = (~is_exch_all_mask) & (
        rt_l_series.str.contains("rto", na=False)
        | st_l_series.str.contains("rto", na=False)
        | (in_rto_sh & (~rt_l_series.str.contains("return", na=False)))
    )
    is_cust_ret_mask = (
        (~is_rto_mask)
        & (~is_exch_all_mask)
        & (
            rt_l_series.str.contains("return", na=False)
            | st_l_series.str.contains("reverse", na=False)
            | in_rto_sh
        )
    )

    rto_df = p_df[is_rto_mask].copy()
    cust_ret_df = p_df[is_cust_ret_mask].copy()
    exch_df = p_df[is_exch_all_mask].copy()
    exch_active_df = p_df[is_exch_active_mask].copy()
    exch_canc_df = p_df[is_exch_canc_mask].copy()
    deliv_df = p_df[st_l_series == "delivered"].copy()

    rto_cnt = int(rto_df["Unique_Order_Key"].nunique()) if not rto_df.empty else 0
    cust_ret_cnt = int(cust_ret_df["Unique_Order_Key"].nunique()) if not cust_ret_df.empty else 0
    exch_cnt = int(exch_active_df["Unique_Order_Key"].nunique()) if not exch_active_df.empty else 0
    canc_exch_cnt = int(exch_canc_df["Unique_Order_Key"].nunique()) if not exch_canc_df.empty else 0
    deliv_cnt = int(deliv_df["Unique_Order_Key"].nunique()) if not deliv_df.empty else 0

    tot_ret_cnt = rto_cnt + cust_ret_cnt + canc_exch_cnt
    tot_ret_pct = (tot_ret_cnt / disp_cnt * 100.0) if disp_cnt > 0 else 0.0
    deliv_pct = (deliv_cnt / disp_cnt * 100.0) if disp_cnt > 0 else 0.0

    gross_rev = float(p_df["seller_paid_amount"].sum())
    tot_disc = float(p_df["discount_amount"].sum()) if "discount_amount" in p_df.columns else 0.0
    tot_ship = float(p_df["delivery_charges"].sum()) if "delivery_charges" in p_df.columns else 0.0

    affected_ret_keys = set(rto_df["Unique_Order_Key"]).union(set(cust_ret_df["Unique_Order_Key"])).union(set(exch_canc_df["Unique_Order_Key"]))
    tot_ret_amt = float(p_df[p_df["Unique_Order_Key"].isin(affected_ret_keys)]["seller_paid_amount"].sum()) if affected_ret_keys else 0.0
    net_rev = max(gross_rev - tot_ret_amt, 0.0)
    realized_deliv_rev = float(deliv_df["seller_paid_amount"].sum()) if not deliv_df.empty else 0.0
    aov = gross_rev / tot_ord if tot_ord > 0 else 0.0

    rto_pending_hub_df = rto_df[st_l_series != "delivered"].copy() if not rto_df.empty else pd.DataFrame()
    rto_hub_parcels = len(rto_pending_hub_df)
    rto_hub_orders = int(rto_pending_hub_df["Unique_Order_Key"].nunique()) if not rto_pending_hub_df.empty else 0

    # Row 1: Shopify-aligned Financial KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Orders</div>
                <div class="kpi-val">{tot_ord:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_rows:,} Items</span>
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

    # Row 2: Shopify-aligned Operational & Return KPIs
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
                <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO {rto_cnt:,} + Ret {cust_ret_cnt:,} + Canc {canc_exch_cnt:,}</span>
            </div>
            <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>
        """)
    with f4:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Pure RTO / Exch Canc</div>
                <div class="kpi-val">{rto_cnt:,} / {canc_exch_cnt:,}</div>
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

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview & Combined Status",
        "↩️ RTO & Exchange Analysis",
        "👗 Article Types & Top SKUs",
        "📋 Orders Table & Download",
    ])

    with tab1:
        c_left, c_right = st.columns([1.85, 1.15])
        with c_left:
            _html('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Seller Paid Revenue Trend (By Order Date)</div>')
            p_df["Order_Date_Only"] = p_df["order_date_dt"].dt.date
            daily = (
                p_df.groupby("Order_Date_Only")
                .agg(Orders=("Unique_Order_Key", "nunique"), Revenue=("seller_paid_amount", "sum"))
                .reset_index()
                .sort_values("Order_Date_Only")
            )
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
                    x=daily["Date_Label"],
                    y=daily["Orders"],
                    name="Unique Orders",
                    marker=dict(color="#6366F1", cornerradius=6),
                    opacity=0.88,
                    text=daily["Orders"],
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(size=10, color="#312E81", family="Plus Jakarta Sans"),
                    hovertemplate="<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig_dual.add_trace(
                go.Scatter(
                    x=daily["Date_Label"],
                    y=daily["Rev_Lakhs"],
                    name="Revenue (₹ Lakhs)",
                    mode="lines+markers",
                    fill="tozeroy",
                    fillcolor="rgba(236, 72, 153, 0.08)",
                    line=dict(color="#EC4899", width=3, shape="spline"),
                    marker=dict(size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")),
                    customdata=daily["Custom_Hover"],
                    hovertemplate="Revenue: %{customdata}<extra></extra>",
                ),
                secondary_y=True,
            )
            max_ord_y = max(float(daily["Orders"].max()) * 1.28, 5.0) if not daily.empty else 10.0
            max_rev_y = max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5) if not daily.empty else 1.0
            _style_fig(fig_dual, height=400, margins=dict(l=15, r=15, t=40, b=60), hovermode="x unified")
            fig_dual.update_layout(bargap=0.28)
            fig_dual.update_xaxes(tickangle=-45, tickfont=dict(size=11, color="#475569"), nticks=18)
            fig_dual.update_yaxes(title_text="Unique Orders", range=[0, max_ord_y], secondary_y=False)
            fig_dual.update_yaxes(title_text="Revenue (₹ Lakhs)", range=[0, max_rev_y], showgrid=False, secondary_y=True)
            st.plotly_chart(fig_dual, use_container_width=True, key="my_dual")

            _html('<div style="font-size:14px; font-weight:700; color:#0F172A; margin-top:14px; margin-bottom:8px;">🔀 Combined Status (order_item_status + return_type)</div>')
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
            _style_fig(fig_comb, height=260, margins=dict(l=10, r=45, t=15, b=15), showlegend=False)
            fig_comb.update_xaxes(range=[0, max(float(comb_tbl["Unique_Orders"].max()) * 1.25, 3.0)])
            st.plotly_chart(fig_comb, use_container_width=True, key="my_comb")
            _safe_dataframe(comb_tbl, use_container_width=True, height=200, hide_index=True)
            _html("</div>")

        with c_right:
            _html('<div class="card-box"><div class="card-title">🎯 Order & Return Funnel (Unique Orders)</div>')
            funnel_labels = ["Orders Created", "Dispatched", "Delivered", "Customer Returns", "RTO Count", "Exchanges"]
            funnel_vals = [tot_ord, disp_cnt, deliv_cnt, cust_ret_cnt, rto_cnt, exch_cnt]
            funnel_colors = ["#4F46E5", "#0EA5E9", "#10B981", "#E11D48", "#EF4444", "#8B5CF6"]
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
            _style_fig(fig_fun, height=400, margins=dict(l=10, r=60, t=20, b=20), showlegend=False)
            fig_fun.update_xaxes(range=[0, max(funnel_vals + [1]) * 1.22])
            fig_fun.update_yaxes(showgrid=False, tickfont=dict(size=12))
            st.plotly_chart(fig_fun, use_container_width=True, key="my_fun")
            _html("</div>")

    with tab2:
        _html(f"""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: Myntra RTO & Customer Return Analysis (Attributed to Order Date • RTO: {rto_cnt:,} | Cust Return: {cust_ret_cnt:,})</div>
            <div class="sec-sub">Reverse Status Donut & Day-Wise RTO + Customer Return Orders by Order Creation Date</div>
        </div>
        """)
        s1_mc1, s1_mc2 = st.columns([1.05, 1.45])
        with s1_mc1:
            _html('<div class="card-box"><div class="card-title">🍩 RTO Reverse Status (Donut)</div>')
            if not rto_df.empty:
                r_st = rto_df.groupby("Reverse_Status_Clean")["Unique_Order_Key"].nunique().reset_index(name="Count")
                st.plotly_chart(
                    _make_donut_fig(
                        r_st["Reverse_Status_Clean"].tolist(),
                        r_st["Count"].tolist(),
                        ["#EF4444", "#F97316", "#F59E0B", "#0EA5E9", "#8B5CF6"],
                        f"<b>{rto_cnt:,}</b><br>RTO",
                    ),
                    use_container_width=True,
                    key="my_rto_dn",
                )
                _html(f'<div class="viz-info"><b>RTO Impact (Order Cohort):</b> <b>{rto_cnt:,}</b> RTO orders ({rto_pct:.1f}% of dispatched) · Seller Value: <b>₹{rto_seller_rev:,.0f}</b>.</div>')
            else:
                st.info("No RTO orders in selected order date period.")
            _html("</div>")

        with s1_mc2:
            _html('<div class="card-box"><div class="card-title">📅 Day-Wise RTO & Customer Return Orders (By Order Date)</div>')
            ret_rto_comb_df = p_df[is_rto_mask | is_cust_ret_mask].copy()
            if not ret_rto_comb_df.empty and ret_rto_comb_df["order_date_dt"].notna().any():
                d_mr = (
                    ret_rto_comb_df.groupby(ret_rto_comb_df["order_date_dt"].dt.date)["Unique_Order_Key"]
                    .nunique()
                    .reset_index(name="Issue_Count")
                    .sort_values("order_date_dt")
                )
                d_mr["Date_Lbl"] = pd.to_datetime(d_mr["order_date_dt"]).dt.strftime("%d %b")
                fig_dmr = go.Figure()
                fig_dmr.add_trace(
                    go.Bar(
                        x=d_mr["Date_Lbl"],
                        y=d_mr["Issue_Count"],
                        name="RTO + Cust Return (Order Date)",
                        marker=dict(color="#FB7185", cornerradius=6),
                        text=d_mr["Issue_Count"],
                        textposition="outside",
                        cliponaxis=False,
                    )
                )
                fig_dmr.add_trace(
                    go.Scatter(
                        x=d_mr["Date_Lbl"],
                        y=d_mr["Issue_Count"],
                        name="Trend",
                        mode="lines+markers",
                        fill="tozeroy",
                        fillcolor="rgba(225, 29, 72, 0.08)",
                        line=dict(color="#E11D48", width=2.5, shape="spline"),
                        marker=dict(size=6.5, color="#FFFFFF", line=dict(color="#E11D48", width=2)),
                    )
                )
                _style_fig(fig_dmr, height=370, margins=dict(l=15, r=15, t=25, b=55), showlegend=False, hovermode="x unified")
                fig_dmr.update_xaxes(tickangle=-45, nticks=18)
                fig_dmr.update_yaxes(range=[0, max(float(d_mr["Issue_Count"].max()) * 1.32, 3.0)])
                st.plotly_chart(fig_dmr, use_container_width=True, key="my_day_rr")
                _html(f'<div class="viz-info"><b>Customer Returns (Order Cohort):</b> <b>{cust_ret_cnt:,}</b> orders ({cust_ret_pct:.1f}%) · Seller Value: <b>₹{cust_ret_seller_rev:,.0f}</b>.</div>')
            else:
                st.info("No day-wise RTO or Customer Return orders in selected order date period.")
            _html("</div>")

        _html(f"""
        <div class="sec-header-exch">
            <div class="sec-title">🔄 Section 2: Myntra Exchange Orders by Order Date & Net Revenue (Active Exch: {exch_cnt:,} | Exch Canc: {canc_exch_cnt:,})</div>
            <div class="sec-sub">Day-Wise Exchange Orders plotted by Original Order Date + Net Revenue Summary</div>
        </div>
        """)
        s2_mc1, s2_mc2 = st.columns([1.35, 1.0])
        with s2_mc1:
            _html('<div class="card-box"><div class="card-title">📅 Day-Wise Exchange Orders (By Order Date)</div>')
            if not exch_df.empty and exch_df["order_date_dt"].notna().any():
                d_mex = (
                    exch_df.groupby(exch_df["order_date_dt"].dt.date)["Unique_Order_Key"]
                    .nunique()
                    .reset_index(name="Exchange_Count")
                    .sort_values("order_date_dt")
                )
                d_mex["Date_Lbl"] = pd.to_datetime(d_mex["order_date_dt"]).dt.strftime("%d %b")
                fig_dmex = go.Figure()
                fig_dmex.add_trace(
                    go.Bar(
                        x=d_mex["Date_Lbl"],
                        y=d_mex["Exchange_Count"],
                        name="Exchanges (Order Date)",
                        marker=dict(color="#8B5CF6", cornerradius=6),
                        text=d_mex["Exchange_Count"],
                        textposition="outside",
                        cliponaxis=False,
                    )
                )
                fig_dmex.add_trace(
                    go.Scatter(
                        x=d_mex["Date_Lbl"],
                        y=d_mex["Exchange_Count"],
                        name="Trend",
                        mode="lines+markers",
                        fill="tozeroy",
                        fillcolor="rgba(139, 92, 246, 0.10)",
                        line=dict(color="#7C3AED", width=2.5, shape="spline"),
                        marker=dict(size=6.5, color="#FFFFFF", line=dict(color="#7C3AED", width=2)),
                    )
                )
                _style_fig(fig_dmex, height=340, margins=dict(l=15, r=15, t=25, b=55), showlegend=False, hovermode="x unified")
                fig_dmex.update_xaxes(tickangle=-45, nticks=18)
                fig_dmex.update_yaxes(range=[0, max(float(d_mex["Exchange_Count"].max()) * 1.32, 3.0)])
                st.plotly_chart(fig_dmex, use_container_width=True, key="my_day_ex")
            else:
                st.info("No exchange records in selected order date period.")
            _html("</div>")

        with s2_mc2:
            _html('<div class="card-box"><div class="card-title">💰 Net Revenue Summary</div>')
            st.metric("Gross Revenue", f"₹{gross_rev:,.2f}")
            st.metric("Less: RTO + Return + Cancelled Exch", f"₹{tot_ret_amt:,.2f}")
            st.metric("Net Revenue", f"₹{net_rev:,.2f}")
            st.caption(f"Delivered Revenue: ₹{realized_deliv_rev:,.0f} | AOV: ₹{aov:,.0f}")
            _html("</div>")

        m_ctrl = p_df.copy()
        m_ctrl["_is_rto"] = is_rto_mask
        m_ctrl["_is_cret"] = is_cust_ret_mask
        m_ctrl["_is_exch"] = is_exch_all_mask
        m_ctrl["_is_issue"] = is_rto_mask | is_cust_ret_mask | is_exch_canc_mask

        m_sku_grp = (
            m_ctrl.groupby("SKU_Clean")
            .agg(
                Total_Orders=("Unique_Order_Key", "nunique"),
                RTO_Orders=("Unique_Order_Key", lambda s: s[m_ctrl.loc[s.index, "_is_rto"]].nunique()),
                Return_Orders=("Unique_Order_Key", lambda s: s[m_ctrl.loc[s.index, "_is_cret"] | m_ctrl.loc[s.index, "_is_exch"]].nunique()),
                Total_Issue_Orders=("Unique_Order_Key", lambda s: s[m_ctrl.loc[s.index, "_is_issue"]].nunique()),
            )
            .reset_index()
            .rename(columns={"SKU_Clean": "SKU_Code"})
        )
        group_col_m = "Size_Clean" if m_ctrl["Size_Clean"].nunique() > 1 else "Article_Clean"
        m_sz_grp = (
            m_ctrl.groupby(group_col_m)
            .agg(
                Orders=("Unique_Order_Key", "nunique"),
                Issues=("Unique_Order_Key", lambda s: s[m_ctrl.loc[s.index, "_is_issue"]].nunique()),
            )
            .reset_index()
        )
        _render_rto_return_control_section(
            sku_df=m_sku_grp,
            size_df=m_sz_grp,
            sku_col_name="SKU_Code",
            size_col_name=group_col_m,
            rto_col_name="RTO_Orders",
            ret_col_name="Return_Orders",
            issue_col_name="Total_Issue_Orders",
            total_ord_col_name="Total_Orders",
            start_date=start_date,
            end_date=end_date,
            key_prefix="myn",
        )

    with tab3:
        p1, p2 = st.columns([1.2, 1])
        with p1:
            _html('<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by Unique Orders</div>')
            top_sku = p_df.groupby("SKU_Clean")["Unique_Order_Key"].nunique().sort_values(ascending=False).head(7)
            if not top_sku.empty:
                mv = top_sku.max()
                for rank, (sku, cnt) in enumerate(top_sku.items(), start=1):
                    pct = cnt / mv * 100
                    _html(f'<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{sku}</span><span style="color:#DB2777;">{cnt:,} ord</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>')
            _html("</div>")

        with p2:
            _html('<div class="card-box"><div class="card-title">👗 Article Types (Unique Orders)</div>')
            art_df = (
                p_df.groupby("Article_Clean")["Unique_Order_Key"]
                .nunique()
                .reset_index(name="Orders")
                .sort_values("Orders", ascending=False)
            )
            art_palette = ["#8B5CF6", "#7C3AED", "#6366F1", "#4F46E5", "#0EA5E9", "#06B6D4", "#10B981"]
            fig_art = go.Figure(
                go.Bar(
                    x=art_df["Article_Clean"],
                    y=art_df["Orders"],
                    marker=dict(color=art_palette[: len(art_df)], cornerradius=8),
                    text=art_df["Orders"],
                    textposition="outside",
                    cliponaxis=False,
                )
            )
            _style_fig(fig_art, height=310, margins=dict(l=10, r=10, t=25, b=10), showlegend=False)
            fig_art.update_yaxes(range=[0, max(float(art_df["Orders"].max()) * 1.25, 3.0)])
            st.plotly_chart(fig_art, use_container_width=True, key="my_art")
            _html("</div>")

    with tab4:
        st.markdown(f"#### 📋 Filtered Myntra Orders ({tot_ord:,} Unique Orders / {tot_rows:,} Rows)")
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
        _safe_dataframe(p_df[tbl_cols], use_container_width=True, height=360, hide_index=True)
        st.download_button(
            "⬇️ Download Filtered Myntra Data CSV",
            p_df[tbl_cols].to_csv(index=False).encode("utf-8"),
            f"myntra_analysis_{start_date}_{end_date}.csv",
            "text/csv",
            key="dl_myn_csv",
        )


def render_nykaa_page():
    """Render Nykaa analytics with Shopify-aligned 10 KPIs and order-creation month cohort tracking."""
    if nykaa_src is None:
        st.warning(f"File `{NYKAA_DEFAULT_NAME}` was not found in GitHub or upload panel.")
        return

    df_all = load_nykaa_data(nykaa_src)
    valid_dates = df_all["Order_Date_dt"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in Order Date.")
        return

    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()

    avail_months_nyk = sorted(valid_dates.dt.to_period("M").astype(str).unique().tolist(), reverse=True)
    latest_m_nyk = avail_months_nyk[0]
    def_end_nyk = _resolve_default_latest_date(min_d, max_d)
    def_start_nyk, _ = _month_bounds(latest_m_nyk, min_d, def_end_nyk)
    _sync_refresh_dates("nykaa", min_d, max_d, def_start_nyk, def_end_nyk)

    disp_n_start = st.session_state.get("nykaa_start_date", def_start_nyk)
    disp_n_end = st.session_state.get("nykaa_end_date", def_end_nyk)

    _html(f"""
    <div class="exec-banner nykaa">
        <div class="exec-banner-left">
            {LOGO_BANNER_HTML}
            <div>
                <div class="exec-title">ARTH LIFE Kids Fashion — Nykaa Analysis</div>
                <div class="exec-sub">Order-Creation Month Cohort (RTO/Return attributed to Order Date) • Shopify-Aligned KPIs</div>
            </div>
        </div>
        <div class="exec-pill">📅 Created: {disp_n_start.strftime('%d %b %Y')} — {disp_n_end.strftime('%d %b %Y')}</div>
    </div>
    """)

    f1, f2, f3, f4, f5, f6 = st.columns([1.05, 0.95, 0.85, 0.85, 1.05, 1.2])
    with f1:
        sel_m_nyk = st.selectbox(
            "🗓️ Month-wise Filter",
            options=["Latest Month (" + latest_m_nyk + ")"] + avail_months_nyk + ["All Available Dates"],
            index=0,
            key="nyk_month_sel",
        )
    with f2:
        preset = st.selectbox(
            "📅 Quick Preset",
            ["Month / Latest", "01 Oct – 31 Oct 2026", "01 Jul – 31 Oct 2026", "All Available Dates"],
            index=0,
            key="nyk_preset",
        )
    if preset == "01 Oct – 31 Oct 2026":
        p_s = min(max(datetime.date(2026, 10, 1), min_d), max_d)
        p_e = max(min(datetime.date(2026, 10, 31), max_d), min_d)
    elif preset == "01 Jul – 31 Oct 2026":
        p_s = min(max(datetime.date(2026, 7, 1), min_d), max_d)
        p_e = max(min(datetime.date(2026, 10, 31), max_d), min_d)
    elif preset == "All Available Dates" or sel_m_nyk == "All Available Dates":
        p_s, p_e = min_d, max_d
    else:
        chosen_m = latest_m_nyk if sel_m_nyk.startswith("Latest Month") else sel_m_nyk
        p_s, p_e = _month_bounds(chosen_m, min_d, max_d)

    if st.session_state.get("_nyk_last_choice") != (sel_m_nyk, preset):
        st.session_state["_nyk_last_choice"] = (sel_m_nyk, preset)
        st.session_state["nykaa_start_date"] = p_s
        st.session_state["nykaa_end_date"] = p_e
        st.rerun()

    all_otypes = sorted(df_all["Order_Type_Clean"].unique().tolist())
    all_statuses = sorted(df_all["Status_Clean"].unique().tolist())

    with f3:
        start_date = st.date_input("📅 Start Date", min_value=min_d, max_value=max_d, key="nykaa_start_date")
    with f4:
        end_date = st.date_input("📅 End Date", min_value=min_d, max_value=max_d, key="nykaa_end_date")
    with f5:
        sel_otypes = st.multiselect("💳 Filter Order Type (COD / Prepaid)", all_otypes, default=all_otypes, key="nyk_otypes")
    with f6:
        sel_statuses = st.multiselect("📦 Filter Status", all_statuses, default=all_statuses, key="nyk_statuses")

    if not sel_otypes:
        sel_otypes = all_otypes
    if not sel_statuses:
        sel_statuses = all_statuses

    if start_date > end_date:
        st.error("Start Date must be on or before End Date.")
        return

    # Filter strictly by Order_Date_dt (order creation date) so returns/RTO stay in the order's creation month
    p_df = df_all[
        (df_all["Order_Date_dt"].dt.date >= start_date)
        & (df_all["Order_Date_dt"].dt.date <= end_date)
        & (df_all["Order_Type_Clean"].isin(sel_otypes))
        & (df_all["Status_Clean"].isin(sel_statuses))
    ].copy()

    if p_df.empty:
        st.info(f"No Nykaa orders found between {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}.")
        return

    tot_ord = int(p_df["Order_Key"].nunique())
    tot_rows = len(p_df)
    tot_qty = int(p_df["Qty"].sum())

    non_canc_df = p_df[p_df["Status_Lower"] != "cancelled"].copy()
    canc_df = p_df[p_df["Status_Lower"] == "cancelled"].copy()
    deliv_df = p_df[p_df["Status_Lower"] == "delivered"].copy()
    shipped_df = p_df[p_df["Status_Lower"] == "shipped"].copy()
    rto_df = p_df[p_df["Status_Lower"].str.contains("rto", na=False)].copy()
    ret_df = p_df[
        (~p_df["Status_Lower"].str.contains("rto", na=False)) & (p_df["Status_Lower"].str.contains("return", na=False))
    ].copy()

    deliv_cnt = int(deliv_df["Order_Key"].nunique()) if not deliv_df.empty else 0
    shipped_cnt = int(shipped_df["Order_Key"].nunique()) if not shipped_df.empty else 0
    disp_cnt = int(p_df[p_df["Status_Lower"].isin(["delivered", "shipped", "returned", "rto delivered"])]["Order_Key"].nunique()) if not p_df.empty else 0

    rto_cnt = int(rto_df["Order_Key"].nunique()) if not rto_df.empty else 0
    ret_cnt = int(ret_df["Order_Key"].nunique()) if not ret_df.empty else 0
    canc_cnt = int(canc_df["Order_Key"].nunique()) if not canc_df.empty else 0
    exch_cnt = int(p_df[p_df["Status_Lower"].str.contains("exchange", na=False)]["Order_Key"].nunique()) if not p_df.empty else 0

    tot_ret_cnt = rto_cnt + ret_cnt
    tot_ret_pct = (tot_ret_cnt / disp_cnt * 100.0) if disp_cnt > 0 else 0.0
    deliv_pct = (deliv_cnt / disp_cnt * 100.0) if disp_cnt > 0 else 0.0

    gross_rev = float(non_canc_df["Line Amount"].sum()) if not non_canc_df.empty else 0.0
    rto_amt = float(rto_df["Line Amount"].sum()) if not rto_df.empty else 0.0
    ret_amt = float(ret_df["Line Amount"].sum()) if not ret_df.empty else 0.0
    canc_amt = float(canc_df["Line Amount"].sum()) if not canc_df.empty else 0.0
    net_rev = max(gross_rev - rto_amt - ret_amt, 0.0)
    realized_deliv_rev = float(deliv_df["Line Amount"].sum()) if not deliv_df.empty else 0.0
    tot_disc = 0.0
    tot_ship = 0.0
    aov = gross_rev / max(int(non_canc_df["Order_Key"].nunique()), 1) if not non_canc_df.empty else 0.0

    rto_pending_df = rto_df[~rto_df["Status_Lower"].str.contains("delivered", na=False)].copy() if not rto_df.empty else pd.DataFrame()
    rto_hub_parcels = len(rto_pending_df)
    rto_hub_orders = int(rto_pending_df["Order_Key"].nunique()) if not rto_pending_df.empty else 0

    # Row 1: Shopify-aligned Financial KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Orders</div>
                <div class="kpi-val">{tot_ord:,}</div>
                <span class="kpi-tag" style="background:#EEF2FF; color:#4F46E5;">{tot_qty:,} Items ({tot_rows} Rows)</span>
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
                <span class="kpi-tag" style="background:#FDF2F8; color:#BE185D;">0.0% Disc. Share</span>
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
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">Avg: ₹0.0/Order</span>
            </div>
            <div class="kpi-ico" style="background:#ECFEFF;">🚢</div>
        </div>
        """)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Row 2: Shopify-aligned Operational & Return KPIs
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Unique Dispatched</div>
                <div class="kpi-val">{disp_cnt:,}</div>
                <span class="kpi-tag" style="background:#ECFEFF; color:#0891B2;">Shipped: {shipped_cnt:,}</span>
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
                <span class="kpi-tag" style="background:#FEF2F2; color:#DC2626;">RTO {rto_cnt:,} + Ret {ret_cnt:,}</span>
            </div>
            <div class="kpi-ico" style="background:#FEF2F2;">↩️</div>
        </div>
        """)
    with f4:
        _html(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-lbl">Pure RTO / Exch Canc</div>
                <div class="kpi-val">{rto_cnt:,} / {canc_cnt:,}</div>
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

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview & Daily Trend",
        "↩️ RTO & Exchange Analysis",
        "👗 Top SKUs & Payment Mix",
        "📋 Orders Table & Download",
    ])

    st_tbl = (
        p_df.groupby("Status_Clean")
        .agg(Unique_Orders=("Order_Key", "nunique"), Qty=("Qty", "sum"), Line_Amount_INR=("Line Amount", "sum"))
        .reset_index()
        .sort_values("Unique_Orders", ascending=False)
    )
    st_tbl["Line_Amount_INR"] = st_tbl["Line_Amount_INR"].round(2)

    with tab1:
        c_left, c_right = st.columns([1.85, 1.15])
        with c_left:
            _html('<div class="card-box"><div class="card-title">📊 Daily Unique Orders & Revenue Trend (By Order Date, Excl. Cancelled)</div>')
            nc_u = non_canc_df.copy()
            nc_u["Order_Date_Only"] = nc_u["Order_Date_dt"].dt.date
            daily = (
                nc_u.groupby("Order_Date_Only")
                .agg(Orders=("Order_Key", "nunique"), Revenue=("Line Amount", "sum"))
                .reset_index()
                .sort_values("Order_Date_Only")
            )
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
                    x=daily["Date_Label"],
                    y=daily["Orders"],
                    name="Unique Orders",
                    marker=dict(color="#6366F1", cornerradius=6),
                    opacity=0.88,
                    text=daily["Orders"],
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(size=10, color="#312E81", family="Plus Jakarta Sans"),
                    hovertemplate="<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig_dual.add_trace(
                go.Scatter(
                    x=daily["Date_Label"],
                    y=daily["Rev_Lakhs"],
                    name="Revenue (₹ Lakhs)",
                    mode="lines+markers",
                    fill="tozeroy",
                    fillcolor="rgba(236, 72, 153, 0.08)",
                    line=dict(color="#EC4899", width=3, shape="spline"),
                    marker=dict(size=7, color="#FFFFFF", line=dict(width=2.5, color="#EC4899")),
                    customdata=daily["Custom_Hover"],
                    hovertemplate="Revenue: %{customdata}<extra></extra>",
                ),
                secondary_y=True,
            )
            max_ord_y = max(float(daily["Orders"].max()) * 1.28, 5.0) if not daily.empty else 10.0
            max_rev_y = max(float(daily["Rev_Lakhs"].max()) * 1.28, 0.5) if not daily.empty else 1.0
            _style_fig(fig_dual, height=400, margins=dict(l=15, r=15, t=40, b=60), hovermode="x unified")
            fig_dual.update_layout(bargap=0.28)
            fig_dual.update_xaxes(tickangle=-45, tickfont=dict(size=11, color="#475569"), nticks=18)
            fig_dual.update_yaxes(title_text="Unique Orders", range=[0, max_ord_y], secondary_y=False)
            fig_dual.update_yaxes(title_text="Revenue (₹ Lakhs)", range=[0, max_rev_y], showgrid=False, secondary_y=True)
            st.plotly_chart(fig_dual, use_container_width=True, key="ny_dual")
            _html("</div>")

        with c_right:
            _html('<div class="card-box"><div class="card-title">🍩 Status Breakdown (Unique Orders)</div>')
            st.plotly_chart(
                _make_donut_fig(
                    st_tbl["Status_Clean"].tolist(),
                    st_tbl["Unique_Orders"].tolist(),
                    ["#10B981", "#F59E0B", "#EF4444", "#94A3B8", "#0EA5E9"],
                    f"<b>{tot_ord:,}</b><br>Orders",
                ),
                use_container_width=True,
                key="ny_dn",
            )
            _html("</div>")

    with tab2:
        _html(f"""
        <div class="sec-header-rto">
            <div class="sec-title">🚚 Section 1: Nykaa RTO & Customer Return Analysis (By Order Date • RTO: {rto_cnt:,} | Cust Return: {ret_cnt:,} | Cancelled: {canc_cnt:,})</div>
            <div class="sec-sub">Order Status Breakdown & Day-Wise RTO + Return Orders by Order Creation Date</div>
        </div>
        """)
        r1, r2, r3 = st.columns(3)
        r1.metric("RTO Delivered Orders", f"{rto_cnt:,}", f"₹{rto_amt:,.2f}")
        r2.metric("Customer Returned Orders", f"{ret_cnt:,}", f"₹{ret_amt:,.2f}")
        r3.metric("Cancelled Orders", f"{canc_cnt:,}", f"₹{canc_amt:,.2f}")

        n_s1_l, n_s1_r = st.columns([1.05, 1.45])
        with n_s1_l:
            _html('<div class="card-box"><div class="card-title">🍩 Status Mix (Donut)</div>')
            st.plotly_chart(
                _make_donut_fig(
                    st_tbl["Status_Clean"].tolist(),
                    st_tbl["Unique_Orders"].tolist(),
                    ["#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#0EA5E9"],
                    f"<b>{tot_ord:,}</b><br>Orders",
                ),
                use_container_width=True,
                key="ny_s1_dn",
            )
            _html("</div>")

        with n_s1_r:
            _html('<div class="card-box"><div class="card-title">📅 Day-Wise RTO & Customer Return Trend (By Order Date)</div>')
            ny_rr_df = p_df[p_df["Status_Lower"].str.contains("rto|return", na=False)].copy()
            if not ny_rr_df.empty and ny_rr_df["Order_Date_dt"].notna().any():
                d_nr = (
                    ny_rr_df.groupby(ny_rr_df["Order_Date_dt"].dt.date)["Order_Key"]
                    .nunique()
                    .reset_index(name="Return_Count")
                    .sort_values("Order_Date_dt")
                )
                d_nr["Date_Lbl"] = pd.to_datetime(d_nr["Order_Date_dt"]).dt.strftime("%d %b")
                fig_dnr = go.Figure()
                fig_dnr.add_trace(
                    go.Bar(
                        x=d_nr["Date_Lbl"],
                        y=d_nr["Return_Count"],
                        name="RTO + Return (Order Date)",
                        marker=dict(color="#FB7185", cornerradius=6),
                        text=d_nr["Return_Count"],
                        textposition="outside",
                        cliponaxis=False,
                    )
                )
                fig_dnr.add_trace(
                    go.Scatter(
                        x=d_nr["Date_Lbl"],
                        y=d_nr["Return_Count"],
                        name="Trend",
                        mode="lines+markers",
                        fill="tozeroy",
                        fillcolor="rgba(225, 29, 72, 0.08)",
                        line=dict(color="#E11D48", width=2.5, shape="spline"),
                        marker=dict(size=6.5, color="#FFFFFF", line=dict(color="#E11D48", width=2)),
                    )
                )
                _style_fig(fig_dnr, height=370, margins=dict(l=15, r=15, t=25, b=55), showlegend=False, hovermode="x unified")
                fig_dnr.update_xaxes(tickangle=-45, nticks=18)
                fig_dnr.update_yaxes(range=[0, max(float(d_nr["Return_Count"].max()) * 1.32, 3.0)])
                st.plotly_chart(fig_dnr, use_container_width=True, key="ny_s1_day_rr")
            else:
                st.info("No day-wise RTO or Customer Return records in selected order date period.")
            _html("</div>")

        _html("""
        <div class="sec-header-exch">
            <div class="sec-title">🔄 Section 2: Nykaa Status Summary & Net Revenue Impact</div>
            <div class="sec-sub">Status-wise Orders, Quantity & Line Amount Impact</div>
        </div>
        """)
        _html('<div class="card-box"><div class="card-title">📋 Status-Wise Summary Table</div>')
        _safe_dataframe(st_tbl, use_container_width=True, height=230, hide_index=True)
        _html("</div>")

        n_ctrl = non_canc_df.copy()
        n_ctrl["_is_rto"] = n_ctrl["Status_Lower"].str.contains("rto", na=False)
        n_ctrl["_is_ret"] = (~n_ctrl["_is_rto"]) & n_ctrl["Status_Lower"].str.contains("return", na=False)
        n_ctrl["_is_issue"] = n_ctrl["_is_rto"] | n_ctrl["_is_ret"]

        n_sku_grp = (
            n_ctrl.groupby("SKU_Code_Clean")
            .agg(
                Total_Orders=("Order_Key", "nunique"),
                RTO_Orders=("Order_Key", lambda s: s[n_ctrl.loc[s.index, "_is_rto"]].nunique()),
                Return_Orders=("Order_Key", lambda s: s[n_ctrl.loc[s.index, "_is_ret"]].nunique()),
                Total_Issue_Orders=("Order_Key", lambda s: s[n_ctrl.loc[s.index, "_is_issue"]].nunique()),
            )
            .reset_index()
            .rename(columns={"SKU_Code_Clean": "SKU_Code"})
        )
        n_sz = (
            n_ctrl[n_ctrl["Size_Clean"] != "Unspecified"]
            .groupby("Size_Clean")
            .agg(
                Orders=("Order_Key", "nunique"),
                Issues=("Order_Key", lambda s: s[n_ctrl.loc[s.index, "_is_issue"]].nunique()),
            )
            .reset_index()
        )
        _render_rto_return_control_section(
            sku_df=n_sku_grp,
            size_df=n_sz,
            sku_col_name="SKU_Code",
            size_col_name="Size_Clean",
            rto_col_name="RTO_Orders",
            ret_col_name="Return_Orders",
            issue_col_name="Total_Issue_Orders",
            total_ord_col_name="Total_Orders",
            start_date=start_date,
            end_date=end_date,
            key_prefix="nyk",
        )

    with tab3:
        t1, t2 = st.columns([1.3, 1])
        with t1:
            _html('<div class="card-box"><div class="card-title">🏆 Top 7 SKUs by Revenue (Excl. Cancelled)</div>')
            top_sku = (
                non_canc_df.groupby(["SKU_Code_Clean", "SKU_Name_Clean"])["Line Amount"]
                .sum()
                .sort_values(ascending=False)
                .head(7)
            )
            if not top_sku.empty:
                mv = top_sku.max()
                for rank, ((skuc, skun), amt) in enumerate(top_sku.items(), start=1):
                    pct = amt / mv * 100
                    short_n = f"{skuc} — {skun[:42]}..." if len(skun) > 42 else f"{skuc} — {skun}"
                    _html(f'<div class="prod-row"><div class="prod-meta"><span>#{rank} &nbsp;{short_n}</span><span style="color:#DB2777;">₹{amt:,.0f}</span></div><div class="prod-track"><div class="prod-fill" style="width:{pct:.1f}%;"></div></div></div>')
            _html("</div>")

        with t2:
            _html('<div class="card-box"><div class="card-title">💳 Order Type (COD vs Prepaid)</div>')
            ot_tbl = (
                p_df.groupby("Order_Type_Clean")
                .agg(Unique_Orders=("Order_Key", "nunique"), Line_Amount_INR=("Line Amount", "sum"))
                .reset_index()
            )
            ot_tbl["Line_Amount_INR"] = ot_tbl["Line_Amount_INR"].round(2)
            _safe_dataframe(ot_tbl, use_container_width=True, height=220, hide_index=True)
            _html("</div>")

    with tab4:
        st.markdown(f"#### 📋 Filtered Nykaa Orders ({tot_ord:,} Unique Orders / {tot_rows:,} Rows)")
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
        _safe_dataframe(p_df[tbl_cols], use_container_width=True, height=360, hide_index=True)
        st.download_button(
            "⬇️ Download Nykaa Orders CSV",
            p_df[tbl_cols].to_csv(index=False).encode("utf-8"),
            f"nykaa_analysis_{start_date}_{end_date}.csv",
            "text/csv",
            key="dl_nyk_csv",
        )


# ==============================================================================
# 10. INDIVIDUAL PAGE ROUTER
# ==============================================================================
page_now = st.session_state["active_page"]
if page_now == "📊 Daily Analysis":
    render_daily_page()
elif page_now == "👗 Shopify Analysis":
    render_shopify_page()
elif page_now == "🔮 Shopify Forecast":
    render_shopify_forecast_page()
elif page_now == "🛍️ Myntra Analysis":
    render_myntra_page()
elif page_now == "💄 Nykaa Analysis":
    render_nykaa_page()
