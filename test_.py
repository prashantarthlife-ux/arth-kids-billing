import streamlit as st
import pandas as pd
import os
import datetime
import shutil
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from supabase import create_client, Client

# 1. Page Configuration & Ultra-Modern Professional Styling
st.set_page_config(page_title="ARTH LIFE - Exhibition Invoice Generator", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }
    .main-banner {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px -4px rgba(14, 165, 233, 0.25);
        margin-bottom: 25px;
    }
    .banner-title {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.8px;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF;
        color: #0F172A;
        border-radius: 10px;
        border: 1.5px solid #CBD5E1;
        padding: 10px 14px;
        font-weight: 500;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0EA5E9;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 48px !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.45);
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0 15px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border-left: 5px solid #0EA5E9;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase Client securely from Streamlit Secrets
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    supabase = None

# 2. PATH SETUP & LOGO CHECK (Supports .jpeg, .jpg, .png automatically)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "Master_Exhibition_Sales.xlsx")
BASE_PDF_FOLDER = os.path.join(BASE_DIR, "Generated_Invoices")

LOGO_FILE = None
for ext in ["jpeg", "jpg", "png"]:
    path = os.path.join(BASE_DIR, f"logo.{ext}")
    if os.path.exists(path):
        LOGO_FILE = path
        break

if not os.path.exists(BASE_PDF_FOLDER):
    os.makedirs(BASE_PDF_FOLDER)

# Initialize Session States
if 'admin_user_id' not in st.session_state:
    st.session_state['admin_user_id'] = "admin"
if 'admin_password' not in st.session_state:
    st.session_state['admin_password'] = "arth123"

if 'ex_name_input' not in st.session_state:
    st.session_state['ex_name_input'] = "Mumbai Exhibitions"
if 'ex_place_input' not in st.session_state:
    st.session_state['ex_place_input'] = "Bandra Kurla Complex, Mumbai"

if 'last_generated_pdf' not in st.session_state:
    st.session_state['last_generated_pdf'] = None
if 'last_bill_no' not in st.session_state:
    st.session_state['last_bill_no'] = None
if 'last_pdf_url' not in st.session_state:
    st.session_state['last_pdf_url'] = None
if 'last_cust_name' not in st.session_state:
    st.session_state['last_cust_name'] = None
if 'last_cust_mobile' not in st.session_state:
    st.session_state['last_cust_mobile'] = None

if 'bill_items' not in st.session_state:
    st.session_state['bill_items'] = []

# Header Section with Centered Logo & Title Banner
if LOGO_FILE:
    c_img1, c_img2, c_img3 = st.columns([2, 1, 2])
    with c_img2:
        st.image(LOGO_FILE, width=120)
            
st.markdown("""
    <div class="main-banner">
        <p class="banner-title">🛍️ ARTH LIFE EXHIBITION INVOICE GENERATOR</p>
    </div>
""", unsafe_allow_html=True)

# 3. Sidebar: Exhibition Setup & Admin Settings
st.sidebar.header("🎪 Exhibition Setup & Switcher")

exhibition_name = st.sidebar.text_input("Active Exhibition Name", value=st.session_state['ex_name_input'], key="ex_name_field")
exhibition_place = st.sidebar.text_input("Exhibition Location / City", value=st.session_state['ex_place_input'], key="ex_place_field")

st.session_state['ex_name_input'] = exhibition_name
st.session_state['ex_place_input'] = exhibition_place

clean_exhibition_name = "".join([c if c.isalnum() else "_" for c in exhibition_name])

date_str = datetime.datetime.now().strftime("%Y-%m-%d")
exhibition_folder = os.path.join(BASE_PDF_FOLDER, clean_exhibition_name, date_str)
if not os.path.exists(exhibition_folder):
    os.makedirs(exhibition_folder)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Admin Access & Settings")

sidebar_admin_user = st.sidebar.text_input("Enter Admin ID", type="default", placeholder="Enter ID", key="side_admin_id", autocomplete="off")
sidebar_admin_pass = st.sidebar.text_input("Enter Password", type="password", placeholder="Enter Password", key="side_admin_pass", autocomplete="new-password")

sidebar_authenticated = (sidebar_admin_user == st.session_state['admin_user_id'] and sidebar_admin_pass == st.session_state['admin_password'])

if sidebar_authenticated:
    st.sidebar.success("🔓 Admin Access Granted!")
    st.sidebar.markdown(f"### 📊 Active Report: {exhibition_name}")
    
    try:
        if supabase:
            res = supabase.table("sales_records").select("*").eq("exhibition_name", exhibition_name).execute()
            df_ex_report = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        else:
            df_ex_report = pd.DataFrame()
            if os.path.exists(EXCEL_FILE):
                all_sheets = pd.ExcelFile(EXCEL_FILE).sheet_names
                if clean_exhibition_name in all_sheets:
                    df_ex_report = pd.read_excel(EXCEL_FILE, sheet_name=clean_exhibition_name)
                
        if not df_ex_report.empty and "total" in df_ex_report.columns:
            ex_sales = df_ex_report["total"].sum()
            ex_bills = df_ex_report["bill_no"].nunique() if "bill_no" in df_ex_report.columns else 0
            st.sidebar.metric(f"💰 {exhibition_name} Sales", f"Rs. {ex_sales}")
            st.sidebar.metric(f"🧾 {exhibition_name} Bills", ex_bills)
    except Exception as e:
        st.sidebar.error(f"Error loading report: {e}")

    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as master_f:
            st.sidebar.download_button(
                label=f"📥 Download Master Excel",
                data=master_f,
                file_name="Master_Exhibition_Sales.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.sidebar.info("🔒 Enter correct Admin ID & Password to unlock reports.")

# 4. Bill ID Generator
try:
    if supabase:
        res = supabase.table("sales_records").select("bill_no").execute()
        all_bills = list(set([row["bill_no"] for row in res.data if row.get("bill_no")])) if res.data else []
        if all_bills:
            num = len(all_bills) + 1
            candidate_bill = f"ARTH-{num:04d}"
            while candidate_bill in all_bills:
                num += 1
                candidate_bill = f"ARTH-{num:04d}"
            default_bill_no = candidate_bill
        else:
            default_bill_no = "ARTH-0001"
    else:
        default_bill_no = "ARTH-0001"
except:
    default_bill_no = "ARTH-0001"

if 'current_bill_no' not in st.session_state:
    st.session_state['current_bill_no'] = default_bill_no

# 5. Product Database
product_database = {
    "OOSKU954N167": {"sku": "954", "name": "ARTH LIFE Party Outfit", "size": "5-6 Y", "price": 2799.0},
    "OOSKU955N168": {"sku": "955", "name": "ARTH LIFE Summer Frock", "size": "3-4 Y", "price": 1499.0},
    "OOSKU956N169": {"sku": "956", "name": "ARTH LIFE Ethnic Kurta", "size": "6-7 Y", "price": 1999.0}
}

# 6. Main Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 👤 Customer Details")
    cust_name = st.text_input("Customer Full Name", "Atish")
    cust_mobile = st.text_input("Customer Mobile Number (10 digits)", "9876543210")

with col2:
    st.markdown("### 📷 Barcode Scanner Gun / Input Mode")
    st.info("⚡ Click inside the box below and scan multiple product barcodes using your Scanner Gun continuously.")

is_name_valid = len(cust_name.strip()) > 0
is_mobile_valid = cust_mobile.isdigit() and len(cust_mobile) == 10

# Scanner Callback Function
def process_scan():
    barcode = st.session_state.get("scanner_input", "").strip()
    if barcode:
        if barcode in product_database:
            selected_prod = product_database[barcode]
            
            item_found = False
            for item in st.session_state['bill_items']:
                if item["barcode_id"] == barcode:
                    item["quantity"] += 1
                    item["total"] = item["quantity"] * item["price"]
                    item_found = True
                    break
            
            if not item_found:
                st.session_state['bill_items'].append({
                    "bill_no": st.session_state['current_bill_no'],
                    "customer_name": cust_name,
                    "mobile_number": cust_mobile,
                    "exhibition_name": exhibition_name,
                    "location": exhibition_place,
                    "sku": selected_prod["sku"],
                    "barcode_id": barcode,
                    "product_name": selected_prod["name"],
                    "size": selected_prod["size"],
                    "price": selected_prod["price"],
                    "quantity": 1,
                    "total": selected_prod["price"]
                })
        else:
            st.error(f"⚠️ Barcode '{barcode}' database madhe sapadla nahi!")
        
        st.session_state["scanner_input"] = ""

st.text_input("🔍 Scan Barcode Here", placeholder="Scan tag or type barcode and press Enter...", key="scanner_input", on_change=process_scan, autocomplete="off")

# 7. Active Bill Summary & Item Cancellation
if st.session_state['bill_items']:
    st.markdown("---")
    st.markdown(f"### 📄 Active Bill Summary — **{st.session_state['current_bill_no']}** ({exhibition_name})")
    
    c_action1, c_action2 = st.columns([3, 1])
    with c_action2:
        if st.button("❌ Cancel Entire Bill", type="secondary"):
            st.session_state['bill_items'] = []
            st.success("🗑️ Current bill cancelled successfully!")
            st.rerun()

    updated_items = []
    for idx, item in enumerate(st.session_state['bill_items']):
        cols = st.columns([3, 1, 1, 1, 1])
        with cols[0]:
            st.write(f"**{item['product_name']}** ({item['size']}) [SKU: {item['sku']}]")
        with cols[1]:
            st.write(f"₹{item['price']}")
        with cols[2]:
            new_qty = st.number_input("Qty", min_value=1, value=item['quantity'], key=f"qty_{idx}", label_visibility="collapsed")
            item['quantity'] = new_qty
            item['total'] = new_qty * item['price']
        with cols[3]:
            st.write(f"**₹{item['total']}**")
        with cols[4]:
            if st.button("🗑️ Remove", key=f"del_{idx}"):
                continue
        updated_items.append(item)
        
    st.session_state['bill_items'] = updated_items
    
    if st.session_state['bill_items']:
        df_final_active = pd.DataFrame(st.session_state['bill_items'])
        grand_total = df_final_active["total"].sum()
        st.markdown(f"### 💰 **Grand Total: Rs. {grand_total}**")
    else:
        st.warning("⚠️ All items removed from current bill.")
        st.rerun()

# PAYMENT METHOD & SAVE BUTTON
st.markdown("---")
st.markdown("### 💳 Payment & Finalize Invoice")
payment_status = st.selectbox("Select Payment Status / Mode", ["Cash", "UPI / GPay / PhonePe", "Credit/Debit Card"], key="payment_mode_select")

if st.button("🚀 Save Bill & Generate PDF", type="primary", disabled=not (is_name_valid and is_mobile_valid and len(st.session_state['bill_items']) > 0)):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_bill = st.session_state['current_bill_no']
    pdf_filename = os.path.join(exhibition_folder, f"Bill_{current_bill}_{date_str}.pdf")
    
    # 1. PDF GENERATION LOCALLY WITH LOGO EMBEDDED
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    inv_title_style = ParagraphStyle('InvTitle', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#2C3E50'), alignment=0)
    company_style = ParagraphStyle('CompStyle', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0077B6'), alignment=2)
    sub_company_style = ParagraphStyle('SubCompStyle', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#555555'), alignment=2)
    
    # Header containing Arth Life Logo and Invoice Details
    if LOGO_FILE:
        logo_img = RLImage(LOGO_FILE, width=55, height=55)
        header_table_data = [
            [logo_img, Paragraph(f"<b>{exhibition_name}</b>", company_style)],
            [Paragraph("<b>INVOICE</b>", inv_title_style), Paragraph(f"{exhibition_place}<br/><b>Payment:</b> {payment_status}", sub_company_style)]
        ]
        header_table = Table(header_table_data, colWidths=[120, 390])
    else:
        header_table_data = [
            [Paragraph("<b>INVOICE</b>", inv_title_style), Paragraph(f"<b>{exhibition_name}</b>", company_style)],
            [Paragraph(f"<b>Bill No:</b> {current_bill}<br/><b>Date:</b> {timestamp}", styles['Normal']), 
             Paragraph(f"{exhibition_place}<br/><b>Payment:</b> {payment_status}", sub_company_style)]
        ]
        header_table = Table(header_table_data, colWidths=[250, 260])
        
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)
    
    meta_data = [
        [Paragraph(f"<b>Bill No:</b> {current_bill}<br/><b>Date:</b> {timestamp}", styles['Normal']), Paragraph("<b>ARTH LIFE OFFICIAL</b>", company_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 260])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))
    
    bill_to_data = [
        [Paragraph("<b>INVOICE TO:</b>", styles['Normal']), Paragraph("<b>COMPANY / EXHIBITION DETAILS:</b>", styles['Normal'])],
        [Paragraph(f"<b>Client Name:</b> {cust_name}<br/><b>Mobile:</b> {cust_mobile}", styles['Normal']),
         Paragraph(f"<b>ARTH LIFE</b><br/>Navmaharashtra Society, Parvati Industrial Estate,<br/>Parvati Paytha, Pune, Maharashtra 411009<br/>Email: support@arthlife.com | Ph: +91 75572 07557", styles['Normal'])]
    ]
    bill_to_table = Table(bill_to_data, colWidths=[250, 260])
    bill_to_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(bill_to_table)
    elements.append(Spacer(1, 20))
    
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2C3E50'))
    th_center = ParagraphStyle('THC', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2C3E50'), alignment=1)
    th_right = ParagraphStyle('THR', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2C3E50'), alignment=2)
    
    table_data = [[
        Paragraph("ITEM DESCRIPTION", th_style), 
        Paragraph("PRICE (Rs.)", th_center), 
        Paragraph("QTY", th_center), 
        Paragraph("SUBTOTAL (Rs.)", th_right)
    ]]
    
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'))
    td_center = ParagraphStyle('TDC', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'), alignment=1)
    td_right = ParagraphStyle('TDR', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'), alignment=2)
    
    df_final_active = pd.DataFrame(st.session_state['bill_items'])
    grand_total = df_final_active["total"].sum()
    
    for _, row in df_final_active.iterrows():
        desc = f"{row['product_name']} ({row['size']}) [SKU: {row['sku']}] | GST: 0.0%"
        table_data.append([
            Paragraph(desc, td_style),
            Paragraph(f"{row['price']:.2f}", td_center),
            Paragraph(str(row["quantity"]), td_center),
            Paragraph(f"{row['total']:.2f}", td_right)
        ])
        
    tot_label = ParagraphStyle('TotL', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#2C2C2C'), alignment=2)
    tot_val = ParagraphStyle('TotV', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#0077B6'), alignment=2)
    
    table_data.append([
        Paragraph("", td_style),
        Paragraph("", td_style),
        Paragraph("TOTAL", tot_label),
        Paragraph(f"Rs. {grand_total:.2f}", tot_val)
    ])
    
    item_table = Table(table_data, colWidths=[230, 90, 60, 130])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#CAF0F8')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#2C3E50')),
        ('BACKGROUND', (2,-1), (-1,-1), colors.HexColor('#ADE8F4')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    
    elements.append(item_table)
    elements.append(Spacer(1, 30))
    
    footer_data = [
        [Paragraph("<b>Payment Info:</b><br/>Paid via " + payment_status + "<br/>Account: ARTH LIFE Official", styles['Normal']),
         Paragraph("<font size=14><b>Thank you!</b></font>", ParagraphStyle('ThankYou', parent=styles['Normal'], alignment=2, textColor=colors.HexColor('#0077B6')))]
    ]
    footer_table = Table(footer_data, colWidths=[300, 210])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(footer_table)
    
    doc.build(elements)

    # 2. UPLOAD PDF TO SUPABASE STORAGE BUCKET
    cloud_pdf_url = pdf_filename
    try:
        if supabase:
            with open(pdf_filename, "rb") as f:
                file_bytes = f.read()
            
            storage_path = f"{clean_exhibition_name}/{date_str}/Bill_{current_bill}_{date_str}.pdf"
            
            supabase.storage.from_("invoices").upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
            cloud_pdf_url = supabase.storage.from_("invoices").get_public_url(storage_path)
    except Exception as e:
        print("Cloud Storage Upload Note:", e)

    rows_to_save = []
    for _, row in df_final_active.iterrows():
        rows_to_save.append({
            "timestamp": timestamp,
            "exhibition_name": exhibition_name,
            "location": exhibition_place,
            "bill_no": current_bill,
            "customer_name": cust_name,
            "mobile_number": cust_mobile,
            "sku": row["sku"],
            "barcode_id": row["barcode_id"],
            "product_name": row["product_name"],
            "size": row["size"],
            "price": row["price"],
            "quantity": row["quantity"],
            "payment_status": payment_status,
            "total": row["total"],
            "bill_pdf_link": cloud_pdf_url
        })
        
    df_new_rows = pd.DataFrame(rows_to_save)
    
    # 3. SAVE TO SUPABASE CLOUD DATABASE
    try:
        if supabase:
            records = df_new_rows.to_dict(orient="records")
            for r in records:
                r.pop('id', None)
            supabase.table("sales_records").insert(records).execute()
    except Exception as e:
        st.error(f"❌ Supabase Cloud Error Detail: {e}")
        st.stop()

    # 4. SAVE TO LOCAL EXCEL FILE
    try:
        if os.path.exists(EXCEL_FILE):
            all_sheets_data = pd.read_excel(EXCEL_FILE, sheet_name=None)
            if clean_exhibition_name in all_sheets_data:
                all_sheets_data[clean_exhibition_name] = pd.concat([all_sheets_data[clean_exhibition_name], df_new_rows], ignore_index=True)
            else:
                all_sheets_data[clean_exhibition_name] = df_new_rows
                
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                for sh_name, sh_df in all_sheets_data.items():
                    sh_df.to_excel(writer, sheet_name=sh_name, index=False)
        else:
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                df_new_rows.to_excel(writer, sheet_name=clean_exhibition_name, index=False)
    except Exception as e:
        print("Excel backup note:", e)

    st.session_state['last_generated_pdf'] = pdf_filename
    st.session_state['last_bill_no'] = current_bill
    st.session_state['last_pdf_url'] = cloud_pdf_url
    st.session_state['last_cust_name'] = cust_name
    st.session_state['last_cust_mobile'] = cust_mobile
    
    st.success("🎉 Bill saved & PDF uploaded to Supabase successfully!")
    st.balloons()
    
    st.session_state['bill_items'] = []
    
    try:
        if supabase:
            res = supabase.table("sales_records").select("bill_no").execute()
            all_bills = list(set([row["bill_no"] for row in res.data if row.get("bill_no")])) if res.data else []
            num = len(all_bills) + 1
            next_bill = f"ARTH-{num:04d}"
            while next_bill in all_bills:
                num += 1
                next_bill = f"ARTH-{num:04d}"
            st.session_state['current_bill_no'] = next_bill
        else:
            st.session_state['current_bill_no'] = "ARTH-0001"
    except:
        st.session_state['current_bill_no'] = "ARTH-0001"

# 5. DOWNLOAD BUTTON & WHATSAPP SHARE (Clean Filename Link Display)
if st.session_state['last_generated_pdf'] and os.path.exists(st.session_state['last_generated_pdf']):
    st.markdown("---")
    pdf_filename_only = os.path.basename(st.session_state['last_generated_pdf'])
    
    st.success(f"📥 Latest Generated Invoice Ready: **{st.session_state['last_bill_no']}** ({st.session_state['last_cust_name']})")
    
    st.markdown(f"🔗 **Invoice File Link:** [{pdf_filename_only}]({st.session_state['last_pdf_url']})")
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        with open(st.session_state['last_generated_pdf'], "rb") as pdf_file:
            st.download_button(
                label=f"📥 Download PDF ({st.session_state['last_bill_no']})",
                data=pdf_file,
                file_name=pdf_filename_only,
                mime="application/pdf",
                type="primary"
            )
            
    with dl_col2:
        wa_msg = f"Hello {st.session_state['last_cust_name']}, Thank you for shopping with ARTH LIFE! Here is your invoice *{pdf_filename_only}*: {st.session_state['last_pdf_url']}"
        encoded_wa_msg = urllib.parse.quote(wa_msg)
        wa_link = f"https://wa.me/91{st.session_state['last_cust_mobile']}?text={encoded_wa_msg}"
        
        st.markdown(f"""
            <a href="{wa_link}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; border-radius: 8px; font-weight: bold; height: 48px; width: 100%; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                    💬 Send Bill via WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)

if not (is_name_valid and is_mobile_valid):
    st.warning("⚠️ Please enter a valid Customer Name and a 10-digit Mobile Number to enable bill generation.")

# 8. LIVE DASHBOARDS FROM SUPABASE
st.markdown("---")
st.markdown("## 📊 Exhibition-wise Live Dashboards (Analytics)")

try:
    if supabase:
        res = supabase.table("sales_records").select("*").execute()
        
        if res.data and len(res.data) > 0:
            df_all_sales = pd.DataFrame(res.data)
            
            if not df_all_sales.empty and "timestamp" in df_all_sales.columns:
                df_all_sales['ParsedDate'] = pd.to_datetime(df_all_sales['timestamp'], errors='coerce').dt.date
                today_date_val = datetime.date.today()
                df_today = df_all_sales[df_all_sales['ParsedDate'] == today_date_val]
                
                exhibitions = df_all_sales['exhibition_name'].unique()
                for ex in exhibitions:
                    df_ex = df_all_sales[df_all_sales['exhibition_name'] == ex]
                    df_ex_today = df_today[df_today['exhibition_name'] == ex] if not df_today.empty else pd.DataFrame()
                    
                    ex_rev = df_ex_today['total'].sum() if not df_ex_today.empty else 0
                    ex_ord = df_ex_today['bill_no'].nunique() if not df_ex_today.empty else 0
                    tot_ex_sales = df_ex['total'].sum()
                    
                    st.markdown(f"### 🎪 Exhibition: **{ex}**")
                    d_col1, d_col2, d_col3 = st.columns(3)
                    d_col1.metric(f"📦 Today's Orders", ex_ord)
                    d_col2.metric(f"💵 Today's Revenue", f"Rs. {ex_rev}")
                    d_col3.metric(f"🛍️ Cumulative Sales", f"Rs. {tot_ex_sales}")
                    st.markdown("---")
            else:
                st.info("ℹ️ Supabase table connected, but no records found yet.")
        else:
            st.info("ℹ️ Supabase table is empty right now. Create your first bill above to initialize live dashboards!")
    else:
        st.info("ℹ️ Supabase not connected.")
except Exception as e:
    st.info("ℹ️ Complete your first bill transaction to initialize the dashboard analytics.")
