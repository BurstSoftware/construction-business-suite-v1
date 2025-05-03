import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import io
import base64
from datetime import datetime

# Streamlit app configuration
st.set_page_config(page_title="Construction Business Suite", layout="wide")

# Initialize session state for data persistence
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'receipts' not in st.session_state:
    st.session_state.receipts = []
if 'invoices' not in st.session_state:
    st.session_state.invoices = []

# Title
st.title("Construction Business Suite")

# Sidebar for navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "Project Cost Estimator",
    "Contractor Management",
    "Invoice Generator",
    "Receipts Input",
    "QR Code Generator"
])

# Trade selection for cost estimator
trades = ["Roofing", "Plumbing", "Electrical", "HVAC", "Landscaping"]
selected_trade = st.sidebar.selectbox("Select Trade", trades)

# 1. Project Cost Estimator
if section == "Project Cost Estimator":
    st.header(f"Comprehensive {selected_trade} Project Cost Estimator")
    
    with st.form("cost_estimator_form"):
        project_name = st.text_input("Project Name")
        client_name = st.text_input("Client Name")
        material_cost = st.number_input("Material Costs ($)", min_value=0.0, step=100.0)
        labor_cost = st.number_input("Labor Costs ($)", min_value=0.0, step=100.0)
        overhead_cost = st.number_input("Overhead Costs ($)", min_value=0.0, step=50.0)
        markup_percentage = st.slider("Markup Percentage (%)", 0, 50, 20)
        
        submitted = st.form_submit_button("Calculate Total")
        
        if submitted:
            total_cost = material_cost + labor_cost + overhead_cost
            markup = total_cost * (markup_percentage / 100)
            final_cost = total_cost + markup
            
            st.write(f"**Total Estimated Cost for {project_name}:** ${final_cost:.2f}")
            st.write(f"- Materials: ${material_cost:.2f}")
            st.write(f"- Labor: ${labor_cost:.2f}")
            st.write(f"- Overhead: ${overhead_cost:.2f}")
            st.write(f"- Markup ({markup_percentage}%): ${markup:.2f}")
            
            # Save project
            st.session_state.projects.append({
                "Project Name": project_name,
                "Client Name": client_name,
                "Trade": selected_trade,
                "Material Cost": material_cost,
                "Labor Cost": labor_cost,
                "Overhead Cost": overhead_cost,
                "Markup %": markup_percentage,
                "Total Cost": final_cost,
                "Date": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("Project saved!")

    # Display saved projects
    if st.session_state.projects:
        st.subheader("Saved Projects")
        df_projects = pd.DataFrame(st.session_state.projects)
        st.dataframe(df_projects)

# 2. Contractor Management
elif section == "Contractor Management":
    st.header("Contractor Management Tool")
    
    with st.form("contractor_form"):
        subcontractor_name = st.text_input("Subcontractor Name")
        project_name = st.selectbox("Select Project", [p["Project Name"] for p in st.session_state.projects])
        task = st.text_input("Task Assigned")
        deadline = st.date_input("Deadline")
        
        submitted = st.form_submit_button("Add Subcontractor")
        
        if submitted:
            st.session_state.projects.append({
                "Subcontractor": subcontractor_name,
                "Project Name": project_name,
                "Task": task,
                "Deadline": deadline.strftime("%Y-%m-%d"),
                "Status": "Pending"
            })
            st.success("Subcontractor task added!")
    
    # Display subcontractor tasks
    if st.session_state.projects:
        st.subheader("Subcontractor Tasks")
        df_contractors = pd.DataFrame([p for p in st.session_state.projects if "Subcontractor" in p])
        st.dataframe(df_contractors)

# 3. Invoice Generator
elif section == "Invoice Generator":
    st.header("Simple Invoice Generator")
    
    with st.form("invoice_form"):
        project_name = st.selectbox("Select Project", [p["Project Name"] for p in st.session_state.projects])
        invoice_date = st.date_input("Invoice Date")
        due_date = st.date_input("Due Date")
        
        submitted = st.form_submit_button("Generate Invoice")
        
        if submitted:
            project = next((p for p in st.session_state.projects if p["Project Name"] == project_name), None)
            if project:
                invoice = {
                    "Invoice ID": f"INV-{len(st.session_state.invoices) + 1:04d}",
                    "Project Name": project_name,
                    "Client Name": project["Client Name"],
                    "Total Amount": project["Total Cost"],
                    "Invoice Date": invoice_date.strftime("%Y-%m-%d"),
                    "Due Date": due_date.strftime("%Y-%m-%d")
                }
                st.session_state.invoices.append(invoice)
                
                st.write(f"**Invoice {invoice['Invoice ID']}**")
                st.write(f"Project: {project_name}")
                st.write(f"Client: {project['Client Name']}")
                st.write(f"Total: ${project['Total Cost']:.2f}")
                st.write(f"Invoice Date: {invoice['Invoice Date']}")
                st.write(f"Due Date: {invoice['Due Date']}")
                st.success("Invoice generated!")
    
    # Display generated invoices
    if st.session_state.invoices:
        st.subheader("Generated Invoices")
        df_invoices = pd.DataFrame(st.session_state.invoices)
        st.dataframe(df_invoices)

# 4. Receipts Input
elif section == "Receipts Input":
    st.header("Simplified Receipts Input Tool")
    
    with st.form("receipt_form"):
        receipt_date = st.date_input("Receipt Date")
        vendor = st.text_input("Vendor Name")
        amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
        project_name = st.selectbox("Select Project", [p["Project Name"] for p in st.session_state.projects])
        description = st.text_area("Description")
        
        submitted = st.form_submit_button("Add Receipt")
        
        if submitted:
            st.session_state.receipts.append({
                "Receipt Date": receipt_date.strftime("%Y-%m-%d"),
                "Vendor": vendor,
                "Amount": amount,
                "Project Name": project_name,
                "Description": description
            })
            st.success("Receipt added!")
    
    # Display receipts
    if st.session_state.receipts:
        st.subheader("Receipts")
        df_receipts = pd.DataFrame(st.session_state.receipts)
        st.dataframe(df_receipts)

# 5. QR Code Generator
elif section == "QR Code Generator":
    st.header("Static QR Code Generator")
    
    with st.form("qr_form"):
        qr_content = st.text_input("QR Code Content (e.g., Payment Link or Project URL)")
        submitted = st.form_submit_button("Generate QR Code")
        
        if submitted:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_content)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            
            # Save QR code to bytes
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            st.image(img, caption="Generated QR Code")
            st.download_button(
                label="Download QR Code",
                data=buffered.getvalue(),
                file_name="qr_code.png",
                mime="image/png"
            )

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Construction Business Suite v1.0")
st.sidebar.write("Built with Streamlit")
