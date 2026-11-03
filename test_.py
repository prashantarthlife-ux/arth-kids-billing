import streamlit as st
import pandas as pd
import os
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Streamlit Page Configuration
st.set_page_config(page_title="ARTH KIDS Billing System", page_icon="🛍️", layout="centered")

st.title("🛍️ ARTH KIDS - Exhibition Billing System")
st.write("Pune Exhibition Live Online Billing & Master Storage Dashboard")

excel_file = "Bill.xlsx"

# Initialize or Load Master Excel File
columns_list = ["Bill No", "Customer Name", "Mobile Number", "City", "SKU", "Barcode ID", "Product Name", "Size", "Price", "Quantity", "Total"]

if not os.path.exists(excel_file):
    df_master = pd.DataFrame(columns=columns_list)
    df_master.to_excel(excel_file, index=False)
else:
    try:
        df_master = pd.read_excel(excel_file)
    except:
        df_master = pd.DataFrame(columns=columns_list)

# Auto-determine Next Bill Number from Excel Master
if df_master.empty or "Bill No" not in df_master.columns or df_master["Bill No"].dropna().empty:
    default_bill_no = "A-0001"
else:
    last_bill = str(df_master["Bill No"].dropna().iloc[-1])
    try:
        prefix, num_str = last_bill.split("-")
        next_num = int(num_str) + 1
        default_bill_no = f"{prefix}-{next_num:04d}"
    except:
        default_bill_no = "A-0001"

# Initialize Session States
if 'bill_items' not in st.session_state:
    st.session_state['bill_items'] = []

if 'current_bill_no' not in st.session_state:
    st.session_state['current_bill_no'] = default_bill_no

# Customer Details Input Section
st.subheader("👤 Customer Details")
cust_name = st.text_input("Customer Name", "Walk-in Customer")
cust_mobile = st.text_input("Mobile Number (10 digits)", "9999999999")

# Fixed Product Details (Exhibition Tag SKU 954)
city_name = "Pune"
sku_number = "954"
barcode_id = "OOSKU954N167"
default_name = "ARTH KIDS Outfit"
default_size = "5-6 Y"
default_price = 2799.0

st.markdown("---")
st.subheader("🏷️ Scanned Product Information")
st.info(f"**SKU:** {sku_number} | **Barcode ID:** {barcode_id} | **Price:** ₹{default_price} | **Size:** {default_size}")

# Add Product Button
if st.button("➕ Add Product to Current Bill", type="primary"):
    item_found = False
    for item in st.session_state['bill_items']:
        if item["SKU"] == sku_number:
            item["Quantity"] += 1
            item["Total"] = item["Quantity"] * item["Price"]
            item_found = True
            break
    
    if not item_found:
        st.session_state['bill_items'].append({
            "Bill No": st.session_state['current_bill_no'],
            "Customer Name": cust_name,
            "Mobile Number": cust_mobile,
            "City": city_name,
            "SKU": sku_number,
            "Barcode ID": barcode_id,
            "Product Name": default_name,
            "Size": default_size,
            "Price": default_price,
            "Quantity": 1,
            "Total": default_price
        })
    st.success(f"Product SKU {sku_number} added to Bill {st.session_state['current_bill_no']}!")

# Display Current Bill Table & Total
if st.session_state['bill_items']:
    st.markdown("---")
    st.subheader(f"📄 Active Bill Summary: {st.session_state['current_bill_no']}")
    
    df_current = pd.DataFrame(st.session_state['bill_items'])
    st.dataframe(df_current[["SKU", "Barcode ID", "Product Name", "Size", "Price", "Quantity", "Total"]])
    
    grand_total = df_current["Total"].sum()
    st.markdown(f"### 💰 **Grand Total: Rs. {grand_total}**")
    
    # Generate PDF & Save to Excel Master Button
    if st.button("🖨️ Save Bill & Generate PDF"):
        # Save current bill items permanently to master Excel file safely
        if os.path.exists(excel_file):
            df_master_existing = pd.read_excel(excel_file)
            df_master_updated = pd.concat([df_master_existing, df_current], ignore_index=True)
        else:
            df_master_updated = df_current
            
        df_master_updated.to_excel(excel_file, index=False)
        
        pdf_filename = f"Bill_{st.session_state['current_bill_no']}.pdf"
        
        # Build PDF using ReportLab
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1A237E'), alignment=1, spaceAfter=10
        )
        
        elements.append(Paragraph("<b>ARTH KIDS - EXHIBITION BILLING</b>", title_style))
        elements.append(Paragraph(f"<b>Location:</b> {city_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Bill No:</b> {st.session_state['current_bill_no']}", styles['Normal']))
        elements.append(Paragraph(f"<b>Customer Name:</b> {cust_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Mobile:</b> {cust_mobile}", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        table_data = [["SKU", "Barcode ID", "Product Name", "Size", "Price", "Qty", "Total"]]
        for _, row in df_current.iterrows():
            table_data.append([str(row["SKU"]), str(row["Barcode ID"]), str(row["Product Name"]), str(row["Size"]), str(row["Price"]), str(row["Quantity"]), str(row["Total"])])
            
        table_data.append(["", "", "", "", "", "<b>Grand Total:</b>", f"<b>Rs. {grand_total}</b>"])
        
        t = Table(table_data, colWidths=[45, 110, 140, 50, 60, 40, 65])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3F51B5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0),(-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#F5F5F5')),
            ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ]))
        
        elements.append(t)
        doc.build(elements)
        
        st.success(f"Bill successfully saved to Excel and PDF generated: {pdf_filename}")
        
        # Download PDF Button
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="📥 Download PDF Bill",
                data=pdf_file,
                file_name=pdf_filename,
                mime="application/pdf"
            )
            
        # WhatsApp Direct Integration Link
        msg = f"Hello {cust_name}, Thank you for shopping with ARTH KIDS (Pune)! Your Bill No: {st.session_state['current_bill_no']}, Grand Total: Rs. {grand_total}."
        encoded_msg = urllib.parse.quote(msg)
        whatsapp_url = f"https://wa.me/91{cust_mobile}?text={encoded_msg}"
        
        st.markdown(f"👉 **[Click Here to Send Bill via WhatsApp]({whatsapp_url})**", unsafe_allow_html=True)

    # Complete & Next Bill Button
    if st.button("🔄 Complete & Next Bill"):
        st.session_state['bill_items'] = []
        try:
            prefix, num = st.session_state['current_bill_no'].split("-")
            st.session_state['current_bill_no'] = f"{prefix}-{int(num)+1:04d}"
        except:
            st.session_state['current_bill_no'] = "A-0002"
        st.rerun()

# Sidebar Master Data Viewer
st.sidebar.title("📊 Master Data Record")
if os.path.exists(excel_file):
    try:
        df_sidebar = pd.read_excel(excel_file)
        with open(excel_file, "rb") as f:
            st.sidebar.download_button(
                label="📥 Download Master Excel (Bill.xlsx)",
                data=f,
                file_name="Bill.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.sidebar.markdown("---")
        st.sidebar.subheader("Recent Saved Bills")
        st.sidebar.dataframe(df_sidebar[["Bill No", "Customer Name", "Total"]].tail(10))
    except:
        pass