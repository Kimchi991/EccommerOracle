import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import oracledb
from dotenv import load_dotenv

import db_helper

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_shop_key")

# ============================================================================
# APP ROUTES
# ============================================================================

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template('login.html')
            
        try:
            user = db_helper.execute_read(
                "SELECT username, password, role FROM users WHERE LOWER(username) = :username",
                {"username": username},
                fetch_all=False
            )
            
            if user and user['password'] == password:
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f"Welcome back, {user['username']} ({user['role']})!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.", "error")
        except Exception as e:
            flash(f"Database connection error: {e}", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    try:
        stats = {}
        
        # 1. Customers Count
        cust_count = db_helper.execute_read("SELECT COUNT(*) as count FROM customer", fetch_all=False)
        stats['customers_count'] = cust_count['count'] if cust_count else 0
        
        # 2. Products Count
        prod_count = db_helper.execute_read("SELECT COUNT(*) as count FROM product", fetch_all=False)
        stats['products_count'] = prod_count['count'] if prod_count else 0
        
        # 3. Orders Count
        order_count = db_helper.execute_read("SELECT COUNT(*) as count FROM orders", fetch_all=False)
        stats['orders_count'] = order_count['count'] if order_count else 0
        
        # 4. Total Sales Revenue
        sales_sum = db_helper.execute_read("SELECT SUM(total_amount) as sum FROM orders WHERE status = 'PAID'", fetch_all=False)
        stats['total_sales'] = sales_sum['sum'] if sales_sum and sales_sum['sum'] is not None else 0.00
        
        # 5. Low Stock Products (stock < 5)
        low_stock = db_helper.execute_read(
            "SELECT product_name, stock FROM product WHERE stock < 5 ORDER BY stock ASC"
        )
        stats['low_stock_list'] = low_stock
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f"Error loading dashboard statistics: {e}", "error")
        return render_template('dashboard.html', stats={"customers_count": 0, "products_count":0, "orders_count":0, "total_sales":0.00, "low_stock_list":[]})

# ============================================================================
# CUSTOMERS ROUTING (CRUD)
# ============================================================================
@app.route('/customers')
def customers():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    try:
        customer_list = db_helper.execute_read("SELECT * FROM customer ORDER BY name")
        return render_template('customers.html', customers=customer_list)
    except Exception as e:
        flash(f"Error fetching customers: {e}", "error")
        return render_template('customers.html', customers=[])

@app.route('/customers/add', methods=['POST'])
def add_customer():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name').strip()
    email = request.form.get('email').strip()
    phone = request.form.get('phone').strip()
    
    if not name or not email or not phone:
        flash("All customer fields are required.", "error")
        return redirect(url_for('customers'))
        
    try:
        db_helper.execute_write(
            "INSERT INTO customer (name, email, phone) VALUES (:name, :email, :phone)",
            {"name": name, "email": email, "phone": phone}
        )
        flash(f"Customer '{name}' registered successfully!", "success")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        if error_obj.code == 1:  # Unique constraint violation (ORA-00001)
            flash("Error: A customer with this email already exists.", "error")
        else:
            flash(f"Database Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error registering customer: {e}", "error")
        
    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name').strip()
    email = request.form.get('email').strip()
    phone = request.form.get('phone').strip()
    
    if not name or not email or not phone:
        flash("All fields are required.", "error")
        return redirect(url_for('customers'))
        
    try:
        db_helper.execute_write(
            "UPDATE customer SET name = :name, email = :email, phone = :phone WHERE customer_id = :id",
            {"name": name, "email": email, "phone": phone, "id": customer_id}
        )
        flash(f"Customer ID {customer_id} updated successfully!", "success")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        if error_obj.code == 1:
            flash("Error: Another customer already uses this email address.", "error")
        else:
            flash(f"Database Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error updating customer: {e}", "error")
        
    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'ADMIN':
        flash("Access denied: Administrative permissions required to delete customer logs.", "error")
        return redirect(url_for('customers'))
    try:
        db_helper.execute_write(
            "DELETE FROM customer WHERE customer_id = :id",
            {"id": customer_id}
        )
        flash("Customer profile deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting customer: {e}", "error")
    return redirect(url_for('customers'))

# ============================================================================
# PRODUCTS ROUTING (CRUD)
# ============================================================================
@app.route('/products')
def products():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    try:
        product_list = db_helper.execute_read("SELECT * FROM product ORDER BY product_name")
        return render_template('products.html', products=product_list)
    except Exception as e:
        flash(f"Error fetching products: {e}", "error")
        return render_template('products.html', products=[])

@app.route('/products/add', methods=['POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form.get('product_name').strip()
    price = request.form.get('price')
    stock = request.form.get('stock')
    
    if not name or not price or not stock:
        flash("All product fields are required.", "error")
        return redirect(url_for('products'))
        
    try:
        db_helper.execute_write(
            "INSERT INTO product (product_name, price, stock) VALUES (:name, :price, :stock)",
            {"name": name, "price": float(price), "stock": int(stock)}
        )
        flash(f"Product '{name}' added successfully!", "success")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        if error_obj.code == 1:
            flash("Error: A product with this name already exists.", "error")
        else:
            flash(f"Database Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error adding product: {e}", "error")
        
    return redirect(url_for('products'))

@app.route('/products/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form.get('product_name').strip()
    price = request.form.get('price')
    stock = request.form.get('stock')
    
    if not name or not price or not stock:
        flash("All fields are required.", "error")
        return redirect(url_for('products'))
        
    try:
        db_helper.execute_write(
            "UPDATE product SET product_name = :name, price = :price, stock = :stock WHERE product_id = :id",
            {"name": name, "price": float(price), "stock": int(stock), "id": product_id}
        )
        flash(f"Product ID {product_id} updated successfully!", "success")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        if error_obj.code == 1:
            flash("Error: Another product with this name already exists.", "error")
        else:
            flash(f"Database Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error updating product: {e}", "error")
        
    return redirect(url_for('products'))

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'ADMIN':
        flash("Access denied: Administrative permissions required to delete items.", "error")
        return redirect(url_for('products'))
    try:
        db_helper.execute_write(
            "DELETE FROM product WHERE product_id = :id",
            {"id": product_id}
        )
        flash("Product record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting product: {e}", "error")
    return redirect(url_for('products'))

# ============================================================================
# ORDERS & ORDER ITEMS ROUTING (CRUD & TRIGGER INTERACTION)
# ============================================================================
@app.route('/orders')
def orders():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    try:
        # Fetch active orders and display them alongside customer names
        order_list = db_helper.execute_read(
            """SELECT o.order_id, c.name as customer_name, o.order_date, o.status, o.total_amount 
               FROM orders o 
               JOIN customer c ON o.customer_id = c.customer_id 
               ORDER BY o.order_date DESC"""
        )
        # For order creation form
        customer_list = db_helper.execute_read("SELECT customer_id, name FROM customer ORDER BY name")
        return render_template('orders.html', orders=order_list, customers=customer_list)
    except Exception as e:
        flash(f"Error loading orders page: {e}", "error")
        return render_template('orders.html', orders=[], customers=[])

@app.route('/orders/create', methods=['POST'])
def create_order():
    if 'username' not in session:
        return redirect(url_for('login'))
    customer_id = request.form.get('customer_id')
    status = request.form.get('status', 'PENDING')
    
    if not customer_id:
        flash("Please select a customer.", "error")
        return redirect(url_for('orders'))
        
    try:
        # Insert a blank parent order (total_amount defaults to 0)
        db_helper.execute_write(
            "INSERT INTO orders (customer_id, status) VALUES (:cust_id, :status)",
            {"cust_id": int(customer_id), "status": status}
        )
        # Fetch the newly created order ID to redirect to its details page
        new_order = db_helper.execute_read(
            "SELECT MAX(order_id) as last_id FROM orders",
            fetch_all=False
        )
        flash("Order record initialized. Please add products to this order below.", "success")
        return redirect(url_for('view_order', order_id=new_order['last_id']))
    except Exception as e:
        flash(f"Error creating order: {e}", "error")
        return redirect(url_for('orders'))

@app.route('/orders/<int:order_id>')
def view_order(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        # Get order info
        order_info = db_helper.execute_read(
            """SELECT o.order_id, c.name as customer_name, c.email as customer_email, 
                      o.order_date, o.status, o.total_amount, o.customer_id
               FROM orders o 
               JOIN customer c ON o.customer_id = c.customer_id 
               WHERE o.order_id = :id""",
            {"id": order_id},
            fetch_all=False
        )
        
        if not order_info:
            flash("Order not found.", "error")
            return redirect(url_for('orders'))
            
        # Get order items
        items = db_helper.execute_read(
            """SELECT oi.order_item_id, p.product_name, p.price, oi.quantity, (p.price * oi.quantity) as item_total
               FROM order_item oi
               JOIN product p ON oi.product_id = p.product_id
               WHERE oi.order_id = :id
               ORDER BY oi.order_item_id""",
            {"id": order_id}
        )
        
        # Get products with stock > 0 for addition form
        products_list = db_helper.execute_read(
            "SELECT product_id, product_name, price, stock FROM product WHERE stock > 0 ORDER BY product_name"
        )
        
        # Get all customers in case they want to change the customer
        customers_list = db_helper.execute_read("SELECT customer_id, name FROM customer ORDER BY name")
        
        return render_template('order_details.html', order=order_info, items=items, products=products_list, customers=customers_list)
    except Exception as e:
        flash(f"Error loading order details: {e}", "error")
        return redirect(url_for('orders'))

@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    customer_id = request.form.get('customer_id')
    status = request.form.get('status')
    
    if not customer_id or not status:
        flash("All fields are required.", "error")
        return redirect(url_for('view_order', order_id=order_id))
        
    try:
        db_helper.execute_write(
            "UPDATE orders SET customer_id = :cust_id, status = :status WHERE order_id = :id",
            {"cust_id": int(customer_id), "status": status, "id": order_id}
        )
        flash("Order updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating order: {e}", "error")
        
    return redirect(url_for('view_order', order_id=order_id))

@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        # If order items are deleted, stock is NOT restored in this simple rubric trigger logic,
        # but in cascading deletion, items are dropped cleanly.
        db_helper.execute_write(
            "DELETE FROM orders WHERE order_id = :id",
            {"id": order_id}
        )
        flash("Order record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting order: {e}", "error")
    return redirect(url_for('orders'))

# Add Order Item (Triggers Inventory Stock Deduction & Order Total updates)
@app.route('/orders/items/add/<int:order_id>', methods=['POST'])
def add_order_item(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    
    if not product_id or not quantity:
        flash("Product and quantity must be specified.", "error")
        return redirect(url_for('view_order', order_id=order_id))
        
    try:
        prod_id = int(product_id)
        qty = int(quantity)
        
        # 1. Create order item.
        # This will fire the AFTER INSERT trigger 'trg_update_stock' to reduce product stock,
        # and 'trg_calculate_order_total' to add the cost of this item to orders.total_amount.
        # If product.stock is not enough, it causes ORA-02290 constraint violation error.
        db_helper.execute_write(
            "INSERT INTO order_item (order_id, product_id, quantity) VALUES (:order_id, :product_id, :qty)",
            {"order_id": order_id, "product_id": prod_id, "qty": qty}
        )
        
        flash("Item added to order successfully. Stock and totals updated.", "success")
        
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        # ORA-02290 is check constraint violation (stock >= 0)
        if error_obj.code == 2290:
            flash("Database Transaction Rolled Back: Insufficient inventory stock available!", "error")
        else:
            flash(f"Database Integrity Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error adding item: {e}", "error")
        
    return redirect(url_for('view_order', order_id=order_id))

# ============================================================================
# PAYMENTS ROUTING (CRUD & TRIGGER INTERACTION)
# ============================================================================
@app.route('/payments')
def payments():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    try:
        # Fetch payment history
        payment_list = db_helper.execute_read(
            """SELECT p.payment_id, p.order_id, c.name as customer_name, 
                      o.total_amount, p.payment_method, p.payment_date 
               FROM payment p
               JOIN orders o ON p.order_id = o.order_id
               JOIN customer c ON o.customer_id = c.customer_id
               ORDER BY p.payment_date DESC"""
        )
        
        # Fetch orders that are NOT paid yet (status is 'PENDING')
        unpaid_orders = db_helper.execute_read(
            """SELECT o.order_id, c.name as customer_name, o.total_amount 
               FROM orders o 
               JOIN customer c ON o.customer_id = c.customer_id
               WHERE o.status = 'PENDING' AND o.total_amount > 0
               ORDER BY o.order_id DESC"""
        )
        
        return render_template('payments.html', payments=payment_list, unpaid_orders=unpaid_orders)
    except Exception as e:
        flash(f"Error fetching payments: {e}", "error")
        return render_template('payments.html', payments=[], unpaid_orders=[])

@app.route('/payments/create', methods=['POST'])
def create_payment():
    if 'username' not in session:
        return redirect(url_for('login'))
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    
    if not order_id or not payment_method:
        flash("Please specify both order and payment method.", "error")
        return redirect(url_for('payments'))
        
    try:
        # Inserting a payment records triggers 'trg_payment_auto_status' which sets order status to PAID
        db_helper.execute_write(
            "INSERT INTO payment (order_id, payment_method) VALUES (:order_id, :method)",
            {"order_id": int(order_id), "method": payment_method}
        )
        flash(f"Payment recorded for Order #{order_id}! Order status updated to PAID.", "success")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        # Unique constraint violation if payment is already recorded for that order (1-to-1 helper)
        if error_obj.code == 1:
            flash("Error: Payment has already been recorded for this order.", "error")
        else:
            flash(f"Database Error: {error_obj.message}", "error")
    except Exception as e:
        flash(f"Error recording payment: {e}", "error")
        
    return redirect(url_for('payments'))

@app.route('/payments/delete/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'ADMIN':
        flash("Access denied: Administrative permissions required to delete payment entries.", "error")
        return redirect(url_for('payments'))
    try:
        db_helper.execute_write(
            "DELETE FROM payment WHERE payment_id = :id",
            {"id": payment_id}
        )
        flash("Payment entry deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting payment entry: {e}", "error")
    return redirect(url_for('payments'))

# ============================================================================
# AUDIT LOGS ROUTING (ADMIN ONLY - TRIGGER DEMO)
# ============================================================================
@app.route('/logs')
def logs():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    if session.get('role') != 'ADMIN':
        flash("Access denied: Administrator permissions required.", "error")
        return redirect(url_for('dashboard'))
    try:
        audit_trail = db_helper.execute_read("SELECT * FROM audit_log ORDER BY created_at DESC")
        return render_template('logs.html', logs=audit_trail)
    except Exception as e:
        flash(f"Error loading audit logs: {e}", "error")
        return render_template('logs.html', logs=[])

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================
if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
