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

  # Keep Nykaa's own KPI Orders count (`tot_ord` via `Order_Key.nunique()`)
  tot_ord = int(p_df["Order_Key"].nunique())
  tot_rows = len(p_df)
  tot_qty = int(p_df["Qty"].sum())

  # Apply Myntra-style classification & metrics for Dispatched, RTO, Customer Return, Exchange, Delivered & Net Revenue
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
