import streamlit as st
import pandas as pd
import os
import datetime
import urllib.parse
import shutil
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration & Professional Corporate Light Styling
st.set_page_config(page_title="ARTH LIFE - Exhibition Invoice Generator", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #F4F7F6;
        color: #2C3E50;
    }
    .main-banner {
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 119, 182, 0.2);
        margin-bottom: 25px;
    }
    .banner-title {
        font-size: 30px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.5px;
        margin: 0;
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF;
        color: #2C3E50;
        border-radius: 8px;
        border: 1px solid #CBD5E1;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        height: 48px !important;
        box-shadow: 0 4px 10px rgba(0, 119, 182, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 119, 182, 0.4);
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #0077B6;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section with Logo & Title Banner
col_logo1, col_logo2, col_logo3 = st.columns([1, 3, 1])
with col_logo2:
    if os.path.exists("logo.png"):
        c_img1, c_img2, c_img3 = st.columns([1, 1, 1])
        with c_img2:
            st.image("logo.png", width=110)
            
    st.markdown("""
        <div class="main-banner">
            <p class="banner-title">🛍️ ARTH LIFE EXHIBITION INVOICE GENERATOR</p>
        </div>
    """, unsafe_allow_html=True)

# 2. ABSOLUTE PATH SETUP FOR GOOGLE DRIVE & LOCAL SYNC
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "Master_Exhibition_Sales.xlsx")
BASE_PDF_FOLDER = os.path.join(BASE_DIR, "Generated_Invoices")

if not os.path.exists(BASE_PDF_FOLDER):
    os.makedirs(BASE_PDF_FOLDER)

# Initialize Session States for Credentials and Exhibition
if 'admin_user_id' not in st.session_state:
    st.session_state['admin_user_id'] = "admin"
if 'admin_password' not in st.session_state:
    st.session_state['admin_password'] = "arth123"

if 'ex_name_input' not in st.session_state:
    st.session_state['ex_name_input'] = "Pune Exhibitions"
if 'ex_place_input' not in st.session_state:
    st.session_state['ex_place_input'] = "Viman Nagar, Pune"

# 3. Sidebar: Exhibition Setup & Admin Settings / Reports
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

with st.sidebar.expander("🔑 Change Admin ID & Password"):
    new_admin_id = st.text_input("New Admin ID", value=st.session_state['admin_user_id'], key="new_adm_id", autocomplete="off")
    new_admin_pass = st.text_input("New Password", type="password", value=st.session_state['admin_password'], key="new_adm_pass", autocomplete="new-password")
    if st.button("Update Credentials"):
        st.session_state['admin_user_id'] = new_admin_id
        st.session_state['admin_password'] = new_admin_pass
        st.success("✅ Admin credentials updated successfully!")

sidebar_admin_user = st.sidebar.text_input("Enter Admin ID", type="default", placeholder="Enter ID", key="side_admin_id", autocomplete="off")
sidebar_admin_pass = st.sidebar.text_input("Enter Password", type="password", placeholder="Enter Password", key="side_admin_pass", autocomplete="new-password")

sidebar_authenticated = (sidebar_admin_user == st.session_state['admin_user_id'] and sidebar_admin_pass == st.session_state['admin_password'])

if sidebar_authenticated:
    st.sidebar.success("🔓 Admin Access Granted!")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📊 Active Report: {exhibition_name}")
    
    if os.path.exists(EXCEL_FILE):
        try:
            all_sheets = pd.ExcelFile(EXCEL_FILE).sheet_names
            if clean_exhibition_name in all_sheets:
                df_ex_report = pd.read_excel(EXCEL_FILE, sheet_name=clean_exhibition_name)
            else:
                df_ex_report = pd.DataFrame()
                
            if not df_ex_report.empty:
                ex_sales = df_ex_report["Total"].sum()
                ex_bills = df_ex_report["Bill No"].nunique()
                st.sidebar.metric(f"💰 {exhibition_name} Sales", f"Rs. {ex_sales}")
                st.sidebar.metric(f"🧾 {exhibition_name} Bills", ex_bills)
            else:
                st.sidebar.info("No sales records for this exhibition yet.")
                
            with open(EXCEL_FILE, "rb") as master_f:
                st.sidebar.download_button(
                    label=f"📥 Download Master Excel (All Sheets)",
                    data=master_f,
                    file_name="Master_Exhibition_Sales.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📁 Exhibition Folder & ZIP")
    exhibition_main_path = os.path.join(BASE_PDF_FOLDER, clean_exhibition_name)
    if os.path.exists(exhibition_main_path) and os.listdir(exhibition_main_path):
        zip_filename = os.path.join(BASE_DIR, f"{clean_exhibition_name}_Invoices")
        shutil.make_archive(zip_filename, 'zip', exhibition_main_path)
        zip_path = f"{zip_filename}.zip"
        
        with open(zip_path, "rb") as zip_f:
            st.sidebar.download_button(
                label=f"📦 Download {exhibition_name} ZIP",
                data=zip_f,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
                key="dl_ex_zip"
            )
else:
    st.sidebar.info("🔒 Enter correct Admin ID & Password to unlock reports.")

# 4. Unique Bill ID Generator Across All Sheets
try:
    if os.path.exists(EXCEL_FILE):
        all_sheets_df = pd.read_excel(EXCEL_FILE, sheet_name=None)
        all_bills = []
        for sh_name, sh_df in all_sheets_df.items():
            if not sh_df.empty and "Bill No" in sh_df.columns:
                all_bills.extend(sh_df["Bill No"].dropna().astype(str).unique())
        
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

# Initialize Session States
if 'bill_items' not in st.session_state:
    st.session_state['bill_items'] = []

if 'current_bill_no' not in st.session_state:
    st.session_state['current_bill_no'] = default_bill_no

# 6. Product Database
product_database = {
    "OOSKU954N167": {"sku": "954", "name": "ARTH LIFE Party Outfit", "size": "5-6 Y", "price": 2799.0},
    "OOSKU955N168": {"sku": "955", "name": "ARTH LIFE Summer Frock", "size": "3-4 Y", "price": 1499.0},
    "OOSKU956N169": {"sku": "956", "name": "ARTH LIFE Ethnic Kurta", "size": "6-7 Y", "price": 1999.0}
}

# 7. Main Layout: Customer Details & Scanner Gun Input with Validations
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 👤 Customer Details")
    cust_name = st.text_input("Customer Full Name", "Walk-in Customer")
    cust_mobile = st.text_input("Customer Mobile Number (10 digits)", "9876543210")

with col2:
    st.markdown("### 📷 Barcode Scanner Gun / Input Mode")
    st.info("⚡ Click inside the box below and scan the product barcode using your Scanner Gun or type tag ID.")
    
    scanned_barcode_input = st.text_input("🔍 Scan Barcode Here", placeholder="Scan tag or type barcode...", key="scanner_input", autocomplete="off")

# Validate customer name and mobile number
is_name_valid = cust_name.replace(" ", "").isalpha()
is_mobile_valid = cust_mobile.isdigit() and len(cust_mobile) == 10

if not is_name_valid:
    st.warning("⚠️ Customer Name should contain only alphabets (letters).")
if not is_mobile_valid:
    st.warning("⚠️ Mobile Number must be exactly 10 digits.")

if scanned_barcode_input:
    scanned_barcode_input = scanned_barcode_input.strip()
    if scanned_barcode_input in product_database:
        selected_prod = product_database[scanned_barcode_input]
        
        item_found = False
        for item in st.session_state['bill_items']:
            if item["Barcode ID"] == scanned_barcode_input:
                item_found = True
                break
        
        if not item_found:
            st.session_state['bill_items'].append({
                "Bill No": st.session_state['current_bill_no'],
                "Customer Name": cust_name,
                "Mobile Number": cust_mobile,
                "Exhibition Name": exhibition_name,
                "Location": exhibition_place,
                "SKU": selected_prod["sku"],
                "Barcode ID": scanned_barcode_input,
                "Product Name": selected_prod["name"],
                "Size": selected_prod["size"],
                "Price": selected_prod["price"],
                "Quantity": 1,
                "Total": selected_prod["price"]
            })
            st.success(f"✅ **Added to Bill:** {selected_prod['name']} ({selected_prod['size']}) - ₹{selected_prod['price']}")
    else:
        if scanned_barcode_input != "":
            st.error(f"⚠️ Barcode '{scanned_barcode_input}' not found in product database!")

# 8. Active Final Bill Summary with Real-Time Manual Quantity Edit & Payment Mode
if st.session_state['bill_items']:
    st.markdown("---")
    st.markdown(f"### 📄 Active Bill Summary — **{st.session_state['current_bill_no']}** ({exhibition_name})")
    st.info("💡 Tip: You can manually edit the **Quantity** column in the table below. The total will update instantly.")
    
    df_current = pd.DataFrame(st.session_state['bill_items'])
    
    edited_df = st.data_editor(
        df_current[["SKU", "Barcode ID", "Product Name", "Size", "Price", "Quantity", "Total"]],
        num_rows="fixed",
        key="bill_editor"
    )
    
    updated_items = []
    for i, row in edited_df.iterrows():
        qty = int(row["Quantity"])
        if qty < 1:
            qty = 1
        price = float(row["Price"])
        subtotal = qty * price
        
        item_data = st.session_state['bill_items'][i]
        item_data["Quantity"] = qty
        item_data["Total"] = subtotal
        updated_items.append(item_data)
        
    st.session_state['bill_items'] = updated_items
    df_final_active = pd.DataFrame(st.session_state['bill_items'])
    grand_total = df_final_active["Total"].sum()
    
    st.markdown(f"### 💰 **Grand Total: Rs. {grand_total}**")

# PAYMENT METHOD & SAVE BUTTON
st.markdown("---")
st.markdown("### 💳 Payment & Finalize Invoice")
payment_status = st.selectbox("Select Payment Status / Mode", ["Cash", "UPI / GPay / PhonePe", "Credit/Debit Card"], key="payment_mode_select")

if st.button("🚀 Save Bill & Generate PDF", type="primary", disabled=not (is_name_valid and is_mobile_valid and len(st.session_state['bill_items']) > 0)):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_filename = os.path.join(exhibition_folder, f"Bill_{st.session_state['current_bill_no']}_{date_str}.pdf")
    
    rows_to_save = []
    for _, row in pd.DataFrame(st.session_state['bill_items']).iterrows():
        rows_to_save.append({
            "Timestamp": timestamp,
            "Exhibition Name": exhibition_name,
            "Location": exhibition_place,
            "Bill No": st.session_state['current_bill_no'],
            "Customer Name": cust_name,
            "Mobile Number": cust_mobile,
            "SKU": row["SKU"],
            "Barcode ID": row["Barcode ID"],
            "Product Name": row["Product Name"],
            "Size": row["Size"],
            "Price": row["Price"],
            "Quantity": row["Quantity"],
            "Payment Status": payment_status,
            "Total": row["Total"],
            "Bill PDF Link": pdf_filename
        })
        
    df_new_rows = pd.DataFrame(rows_to_save)
    
    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            all_existing = pd.read_excel(EXCEL_FILE, sheet_name=None)
            if clean_exhibition_name in all_existing:
                updated_sheet_df = pd.concat([all_existing[clean_exhibition_name], df_new_rows], ignore_index=True)
            else:
                updated_sheet_df = df_new_rows
            updated_sheet_df.to_excel(writer, sheet_name=clean_exhibition_name, index=False)
    else:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df_new_rows.to_excel(writer, sheet_name=clean_exhibition_name, index=False)
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    inv_title_style = ParagraphStyle('InvTitle', fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#2C3E50'), alignment=0)
    company_style = ParagraphStyle('CompStyle', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0077B6'), alignment=2)
    sub_company_style = ParagraphStyle('SubCompStyle', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#555555'), alignment=2)
    
    header_data = [
        [Paragraph("<b>INVOICE</b>", inv_title_style), Paragraph(f"<b>{exhibition_name}</b>", company_style)],
        [Paragraph(f"<b>Bill No:</b> {st.session_state['current_bill_no']}<br/><b>Date:</b> {timestamp}", styles['Normal']), 
         Paragraph(f"{exhibition_place}<br/><b>Payment:</b> {payment_status}", sub_company_style)]
    ]
    header_table = Table(header_data, colWidths=[250, 260])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    
    bill_to_data = [
        [Paragraph("<b>INVOICE TO:</b>", styles['Normal']), Paragraph("<b>COMPANY / EXHIBITION DETAILS:</b>", styles['Normal'])],
        [Paragraph(f"<b>Client Name:</b> {cust_name}<br/><b>Mobile:</b> {cust_mobile}", styles['Normal']),
         Paragraph(f"<b>ARTH LIFE POS</b><br/>{exhibition_name} Counter<br/>Email: support@arthlife.com", styles['Normal'])]
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
    
    for _, row in pd.DataFrame(st.session_state['bill_items']).iterrows():
        desc = f"{row['Product Name']} ({row['Size']}) [SKU: {row['SKU']}]"
        table_data.append([
            Paragraph(desc, td_style),
            Paragraph(f"{row['Price']:.2f}", td_center),
            Paragraph(str(row["Quantity"]), td_center),
            Paragraph(f"{row['Total']:.2f}", td_right)
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
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#2C2C2C')),
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
    st.success("🎉 Invoice saved, PDF generated, and Master Excel updated successfully!")
    st.session_state['pdf_ready'] = pdf_filename
    st.rerun()

if not (is_name_valid and is_mobile_valid):
    st.warning("⚠️ Please enter a valid Customer Name (alphabets only) and a 10-digit Mobile Number to enable bill generation.")

if 'pdf_ready' in st.session_state and os.path.exists(st.session_state['pdf_ready']):
    st.markdown("### 📥 Download, Print & Share Invoice")
    
    with open(st.session_state['pdf_ready'], "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Corrected JavaScript template with escaped double braces {{ and }}
    pdf_download_link = f'''
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <a href="data:application/pdf;base64,{b64_pdf}" download="{os.path.basename(st.session_state['pdf_ready'])}" style="flex: 1; background-color: #0077B6; color: white; padding: 12px 20px; text-align: center; text-decoration: none; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,119,182,0.3);">
                📥 Click Here to Download PDF
            </a>
            <button onclick="var win = window.open('data:application/pdf;base64,{b64_pdf}'); setTimeout(function(){{win.print();}}, 1000);" style="flex: 1; background-color: #2e7d32; color: white; padding: 12px 20px; border: none; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 10px rgba(46,125,50,0.3);">
                🖨️ Click Here to Print Bill Directly
            </button>
        </div>
    '''
    st.markdown(pdf_download_link, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label="📥 Download Professional Invoice PDF", 
            data=pdf_bytes, 
            file_name=os.path.basename(st.session_state['pdf_ready']), 
            mime="application/pdf", 
            key="dl_current_pdf"
        )
    with d_col2:
        msg = f"Hello {cust_name}, Thank you for shopping at {exhibition_name}! Your Bill No: {st.session_state['current_bill_no']}, Grand Total: Rs. {grand_total}."
        encoded_msg = urllib.parse.quote(msg)
        whatsapp_url = f"https://wa.me/91{cust_mobile}?text={encoded_msg}"
        st.markdown(f"👉 **[Click Here to Send Invoice via WhatsApp]({whatsapp_url})**", unsafe_allow_html=True)

if st.button("🔄 Complete & Start Next Bill"):
    st.session_state['bill_items'] = []
    if 'pdf_ready' in st.session_state:
        del st.session_state['pdf_ready']
    try:
        all_sheets_df = pd.read_excel(EXCEL_FILE, sheet_name=None)
        all_bills = []
        for sh_name, sh_df in all_sheets_df.items():
            if not sh_df.empty and "Bill No" in sh_df.columns:
                all_bills.extend(sh_df["Bill No"].dropna().astype(str).unique())
        num = len(all_bills) + 1
        next_bill = f"ARTH-{num:04d}"
        while next_bill in all_bills:
            num += 1
            next_bill = f"ARTH-{num:04d}"
        st.session_state['current_bill_no'] = next_bill
    except:
        st.session_state['current_bill_no'] = "ARTH-0001"
    st.rerun()

# 9. SEPARATE EXHIBITION-WISE LIVE DASHBOARDS AT THE BOTTOM
st.markdown("---")
st.markdown("## 📊 Exhibition-wise Live Dashboards (Today's Analytics)")

if os.path.exists(EXCEL_FILE):
    try:
        all_sheets_data = pd.read_excel(EXCEL_FILE, sheet_name=None)
        today_date_val = datetime.date.today()
        
        active_exhibitions_found = False
        for sh_name, sh_df in all_sheets_data.items():
            if not sh_df.empty and "Timestamp" in sh_df.columns:
                sh_df['ParsedDate'] = pd.to_datetime(sh_df['Timestamp']).dt.date
                df_today_ex = sh_df[sh_df['ParsedDate'] == today_date_val]
                
                if not df_today_ex.empty:
                    active_exhibitions_found = True
                    ex_rev = df_today_ex['Total'].sum()
                    ex_ord = df_today_ex['Bill No'].nunique()
                    tot_ex_sales = sh_df['Total'].sum()
                    
                    st.markdown(f"### 🎪 Exhibition: **{sh_name}**")
                    d_col1, d_col2, d_col3 = st.columns(3)
                    d_col1.metric(f"📦 Today's Orders ({sh_name})", ex_ord)
                    d_col2.metric(f"💵 Today's Revenue ({sh_name})", f"Rs. {ex_rev}")
                    d_col3.metric(f"🛍️ Cumulative Sales ({sh_name})", f"Rs. {tot_ex_sales}")
                    st.markdown("---")
                    
        if not active_exhibitions_found:
            st.info("ℹ️ No active sales records found for today across any exhibitions yet.")
    except Exception as e:
        st.error(f"Error loading exhibition dashboards: {e}")
else:
    st.info("ℹ️ Master Excel file not created yet. Save your first bill to view exhibition dashboards here.")
