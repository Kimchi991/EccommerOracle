import sys
import os
import shutil
import glob

# Try importing fpdf
try:
    from fpdf import FPDF
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from FPDF import FPDF

class ProjectPDF(FPDF):
    def header(self):
        self.set_text_color(80, 50, 120)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "ORACLESHOP MANAGER - DATABASE INTEGRATION SYSTEM", new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_draw_color(180, 180, 180)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(180, 180, 180)
        self.line(10, 280, 200, 280)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", new_x="LMARGIN", new_y="NEXT", align="C")

def copy_clean_screenshots():
    brain_dir = r"C:\Users\ASUS TUF\.gemini\antigravity\brain\3ab66ad2-bdf8-4df5-b535-4314c4d0968e"
    
    pages = [
        {"prefix": "login_page_src", "local": "login_page.png"},
        {"prefix": "dashboard_page_src", "local": "dashboard_page.png"},
        {"prefix": "customers_page_src", "local": "customers_page.png"},
        {"prefix": "products_page_src", "local": "products_page.png"},
        {"prefix": "orders_page_src", "local": "orders_page.png"},
        {"prefix": "order_details_page_src", "local": "order_details_page.png"},
        {"prefix": "payments_page_src", "local": "payments_page.png"},
        {"prefix": "logs_page_src", "local": "logs_page.png"}
    ]
    
    for page in pages:
        src_pattern = os.path.join(brain_dir, f"{page['prefix']}_*.png")
        matches = glob.glob(src_pattern)
        if matches:
            shutil.copy(matches[-1], page["local"])
            print(f"Copied clean {page['local']} from brain.")
        else:
            print(f"Warning: No match found for {src_pattern}")

def add_screenshot_block(pdf, img_path, caption, legend):
    if not os.path.exists(img_path):
        return
    
    start_y = pdf.get_y()
    
    # 1. Print clean image (160mm width, 90mm height) Centered (x = 25)
    pdf.image(img_path, x=25, y=start_y, w=160, h=90)
    
    # 2. Advance Y coordinate past the image height (90mm) + small padding (2mm)
    pdf.set_y(start_y + 92)
    
    # 3. Print Caption
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, caption, new_x="LMARGIN", new_y="NEXT", align="C")
    
    # 4. Print Legend details
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4.5, legend)
    
    # 5. Add spacing after block
    pdf.ln(4)

def generate_pdf(output_path):
    # Copy clean screenshots (no annotation drawings)
    copy_clean_screenshots()
    
    pdf = ProjectPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Section
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 12, "OracleShop Manager", new_x="LMARGIN", new_y="NEXT", align="L")
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Integration of Oracle DB to Programming Language (100 pts Submission)", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.cell(0, 7, "Course Module: M1P3 - Database Integration & Trigger Enforcement", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(4)
    
    # 1. System Overview
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "1. System Overview", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    overview_text = (
        "For my project, I built OracleShop Manager, a desktop-web hybrid application designed for "
        "managing a small online store. I integrated the frontend interface directly with an Oracle 21c XE "
        "database to show how we can combine a modern programming language (Python/Flask) with enterprise "
        "database procedures.\n\n"
        "My system allows shop staff to register customers, keep track of a product inventory catalog, "
        "initialize invoices, process payments, and track secure logs, with multiple database operations "
        "automated directly via PL/SQL database triggers."
    )
    pdf.multi_cell(0, 5, overview_text)
    pdf.ln(4)
    
    # 2. Technology Stack
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "2. Tech Stack & Integration Connectivity", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    tech_text = (
        "- Programming Language / Framework: Python 3 with Flask\n"
        "- Database Server: Oracle Database 21c Express Edition (XE)\n"
        "- Connection Driver: oracledb (configured in Thin Mode for direct connection without client binaries)\n"
        "- Interface Design: Clean HTML5 with custom Vanilla CSS styles (Slate Dark mode styling)\n"
        "- Credentials Configuration: Local .env variables for secure credential mapping"
    )
    pdf.multi_cell(0, 5, tech_text)
    pdf.ln(4)
    
    # 3. Database Schema
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "3. Database Schema & Entity Relationships", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    schema_text = (
        "I designed a relational schema consisting of six tables connected with foreign keys to enforce "
        "data structure integrity:\n\n"
        "1. USERS: Stores user accounts and authorization roles (user_id, username, password, role).\n"
        "2. CUSTOMER: Stores customer profiles (customer_id, name, email [UNIQUE], phone).\n"
        "3. PRODUCT: Manages catalog pricing and stocks (product_id, product_name, price, stock [CHECK stock >= 0]).\n"
        "4. ORDERS: Logs invoices and order records (order_id, customer_id, order_date, status, total_amount).\n"
        "5. ORDER_ITEM: Line details connecting products to invoices (order_item_id, order_id, product_id, quantity).\n"
        "6. PAYMENT: Handles transactional logs for payments (payment_id, order_id, payment_method, payment_date)."
    )
    pdf.multi_cell(0, 5, schema_text)
    
    # Force clean page break to keep Page 2 structured
    pdf.add_page()
    
    # 4. CRUD Functionality
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "4. CRUD Operations & Functions", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    crud_text = (
        "- Create: Users can register new customers, insert product items, create empty orders, and add item lines.\n"
        "- Read: Real-time queries list customers, product inventory catalogs, orders history, and logs.\n"
        "- Update: Staff can edit customer contact info, update product pricing/stock, or edit invoice statuses.\n"
        "- Delete: I restricted deletion functionality. Only users logged in as ADMIN or MANAGER can execute "
        "delete statements; standard STAFF profiles are blocked from deleting records."
    )
    pdf.multi_cell(0, 5, crud_text)
    pdf.ln(4)
    
    # 5. Triggers
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "5. Database Trigger Implementations", new_x="LMARGIN", new_y="NEXT", align="L")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Trigger A: Inventory Stock Control (TRG_UPDATE_STOCK)", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    trigger_a = (
        "I wrote this trigger to execute AFTER INSERT ON ORDER_ITEM. It automatically deducts the purchased "
        "quantity from the product's available stock. If a purchase quantity is larger than the available stock, "
        "the PRODUCT table's constraint CHECK (stock >= 0) is violated. The trigger triggers an exception, and "
        "Oracle instantly aborts and rolls back the entire insert transaction to keep our inventory clean."
    )
    pdf.multi_cell(0, 5, trigger_a)
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Trigger B: Invoice Calculation (TRG_CALCULATE_ORDER_TOTAL)", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    trigger_b = (
        "Fires AFTER INSERT ON ORDER_ITEM. This trigger automatically looks up the product price, multiplies "
        "it by the order quantity, and increments the parent order's total_amount automatically. This eliminates "
        "the need to compute invoice totals on the front-end application level."
    )
    pdf.multi_cell(0, 5, trigger_b)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Trigger C: Automatic Payment Transition (TRG_PAYMENT_AUTO_STATUS)", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    trigger_c = (
        "Fires AFTER INSERT ON PAYMENT. Whenever a payment is processed, it immediately updates the status "
        "of the corresponding order invoice to 'PAID' automatically."
    )
    pdf.multi_cell(0, 5, trigger_c)
    pdf.ln(4)

    # 6. Verification Details
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 8, "6. Audit Trails & Verification", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    verification_text = (
        "1. Active Audit Trail: Every transaction (stock deduction, payments) is logged in the AUDIT_LOG table "
        "directly by database triggers. The entries detail timestamps and actions recorded.\n"
        "2. Security Testing: I tested and verified that accessing restricted pages is blocked unless a "
        "user has the corresponding authorization token in the session."
    )
    pdf.multi_cell(0, 5, verification_text)

    # Disable automatic page break temporarily to control the placement exactly
    pdf.set_auto_page_break(auto=False)
    
    # PAGE 3: Login and Dashboard
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 10, "7. System Interfaces & Features Explanations", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(2)
    
    add_screenshot_block(
        pdf, 
        "login_page.png", 
        "Figure 1: Custom Sign In Portal with Quick Access selectors",
        "(1) Quick Account Access: Clickable role cards to autofill administrator and staff credentials.\n"
        "(2) System Configuration: Shows direct XE database host details and schema user mapping.\n"
        "(3) Standard Form: Session-based security inputs linked with database user validation."
    )
    
    add_screenshot_block(
        pdf,
        "dashboard_page.png",
        "Figure 2: Store Operations Dashboard Portal",
        "(1) Real-Time Store Statistics: Counts for customers, inventory catalog products, and paid sales.\n"
        "(2) Operations Grid: Core shortcut buttons mapping to the database management screens.\n"
        "(3) Low Stock Alerts: Warning triggers displayed when items fall below 5 units.\n"
        "(4) Connection status link."
    )
    
    # PAGE 4: Customers and Products
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 10, "Customers & Products Interfaces", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(2)
    
    add_screenshot_block(
        pdf,
        "customers_page.png",
        "Figure 3: Customer Profiles Management Registry",
        "(1) Register Customer: Triggers a modal screen checking unique constraint validation for emails.\n"
        "(2) Records Registry: Interactive rows displaying details, edit buttons, and cascade delete tools."
    )
    
    add_screenshot_block(
        pdf,
        "products_page.png",
        "Figure 4: Product Catalog and Stock Management",
        "(1) Product Catalog: Database table view tracking individual item pricing details.\n"
        "(2) Inventory Warning Badges: Color-coded warnings ('Low Stock' and 'Out of Stock') matching stock thresholds."
    )
    
    # PAGE 5: Orders and Order Details
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 10, "Orders & Invoicing Management", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(2)
    
    add_screenshot_block(
        pdf,
        "orders_page.png",
        "Figure 5: Store Orders and Invoices Registry",
        "(1) Create New Order: Instantiates an empty order in the database.\n"
        "(2) Invoices Ledger: Lists dates, customer assignments, and total invoice sums.\n"
        "(3) Details Navigation: Opens the items view to edit individual line items."
    )
    
    add_screenshot_block(
        pdf,
        "order_details_page.png",
        "Figure 6: Order Itemized Line details View",
        "(1) Add Line Item Form: Form used to insert item lines, triggering automatic stock reduction.\n"
        "(2) Real-Time Totals: Invoice details computed automatically via the calculated order total trigger."
    )
    
    # PAGE 6: Payments and Audit Logs
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 10, "Payments & Audit Trail Ledger", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(2)
    
    add_screenshot_block(
        pdf,
        "payments_page.png",
        "Figure 7: Invoicing Payments Portal",
        "(1) Select Order Dropdown: Populated with pending billing documents.\n"
        "(2) Processed Payments: Log tracking exact amounts, methods, and transaction times."
    )
    
    add_screenshot_block(
        pdf,
        "logs_page.png",
        "Figure 8: Database Audit Trail Ledger",
        "(1) Audit Log Messages: Clear records outlining stock updates and billing payments.\n"
        "(2) Action Trigger Badges: Classifies logging sources mapped to exact database events."
    )
    
    # PAGE 7: Conclusion
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(80, 50, 120)
    pdf.cell(0, 10, "8. Conclusion", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    conclusion_text = (
        "This project successfully demonstrates the integration of an Oracle 21c Express Edition database "
        "with a Python Flask web application backend. By moving calculations and stock constraints directly "
        "into Oracle PL/SQL triggers (TRG_UPDATE_STOCK, TRG_CALCULATE_ORDER_TOTAL, TRG_PAYMENT_AUTO_STATUS), "
        "the application ensures strict data integrity, performance, and robustness.\n\n"
        "The interface has been thoroughly verified for different authentication roles, unique constraints "
        "handling, stock protection rollback states, and automated billing status changes. This completes "
        "the requirements for the M1P3 Database Integration module."
    )
    pdf.multi_cell(0, 5, conclusion_text)

    pdf.output(output_path)
    print(f"Successfully generated PDF at {output_path}")

if __name__ == "__main__":
    generate_pdf("M1P3_YourLastnameFirstname.pdf")
