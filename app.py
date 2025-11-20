from flask import Flask, request, jsonify, render_template
import pymysql
import mysql.connector
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def get_db_connection_pymysql():
    """
    PyMySQL connection (used for Phase 1 - Enhanced ordering)
    """
    try:
        return pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'apoorva28'),
            database=os.getenv('DB_NAME', 'pesu_food_systems'),
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as err:
        print(f"PyMySQL Connection Error: {err}")
        return None

def get_db_connection():
    """
    MySQL Connector connection (used for Phase 2 - Admin features)
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'apoorva28'),
            database=os.getenv('DB_NAME', 'pesu_food_systems')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"MySQL Connector Connection Error: {err}")
        return None


@app.route('/')
def home():
    """Serves the login page as the entry point."""
    return render_template('login.html')

@app.route('/order-page')
def customer_page():
    """Serves the customer ordering page (Phase 1)."""
    return render_template('customer_order_page.html')

@app.route('/my-orders')
def my_orders_page():
    """Serves the customer order tracking page."""
    return render_template('customer_orders.html')

@app.route('/admin-dashboard')
def admin_page():
    """Serves the admin dashboard page (Phase 2)."""
    return render_template('admin_dashboard.html')

@app.route('/kitchen-dashboard')
def kitchen():
    """Serves the kitchen management page."""
    return render_template('kitchen_dashboard.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handles user login and determines the user's role (Customer, Admin, or Kitchen)."""
    user_id = request.json.get('user_id')
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500
    
    cursor = db.cursor()
    role = None

    try:
        # Check Customer table
        cursor.execute("SELECT customer_id FROM Customer WHERE customer_id = %s", (user_id,))
        if cursor.fetchone():
            role = 'Customer'
        
        # Check Shop table (Admin)
        if not role:
            cursor.execute("SELECT shop_ID FROM Shop WHERE shop_ID = %s", (user_id,))
            if cursor.fetchone():
                role = 'Admin'
        
        # Check Kitchen_Staff table
        if not role:
            cursor.execute("SELECT staff_id, shop_id FROM Kitchen_Staff WHERE staff_id = %s", (user_id,))
            kitchen_staff = cursor.fetchone()
            if kitchen_staff:
                role = 'Kitchen'
        
        if role:
            return jsonify({'status': 'Success', 'role': role, 'user_id': user_id})
        else:
            return jsonify({'status': 'Failed', 'message': 'User ID not found'}), 401

    except mysql.connector.Error as err:
        print(f"Login Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error during login: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()


#CUSTOMER ORDERING APIS


@app.route('/place_order', methods=['POST'])
def place_order():
    """
    Enhanced endpoint with complete order details
    """
    try:
        print("🎯 DEBUG: Enhanced place_order function started")
        
        
        data = request.get_json()
        print(f"📦 DEBUG: Received data: {data}")
        
    
        customer_id = data.get('customer_id')
        shop_id = data.get('shop_id')
        items = data.get('items', [])
        payment_mode = data.get('payment_mode', 'Online')
        
        print(f"🔍 DEBUG: customer_id={customer_id}, shop_id={shop_id}, items_count={len(items)}, payment_mode={payment_mode}")
      
        valid_payment_modes = ['Cash', 'UPI', 'Card', 'Online', 'CASH', 'CARD']
        if payment_mode not in valid_payment_modes:
            return jsonify({'error': f'Invalid payment mode. Must be one of: {valid_payment_modes}'}), 400
        
        if not customer_id or not shop_id or not items:
            return jsonify({'error': 'Missing required fields'}), 400
        
        print("🛢️ DEBUG: Attempting database connection...")
        connection = get_db_connection_pymysql()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        print(" DEBUG: Database connection successful")
       
        order_id = 'O' + str(uuid.uuid4().hex[:7]).upper()
        payment_id = 'TXN' + str(uuid.uuid4().hex[:7]).upper()
        prep_id = 'PREP' + str(uuid.uuid4().hex[:7]).upper()
        
        print(f" DEBUG: Generated order_id: {order_id}")
        print(f" DEBUG: Generated transaction_id: {payment_id}")
        
        total_quantity = sum(item['quantity'] for item in items)
        total_preparation_time = 0
        order_details = []
        total_amount = 0
        
        print(" DEBUG: Calculating order details...")
        for i, item in enumerate(items):
        
            cursor.execute(
                "SELECT item_name, price, countdown FROM Menu_Item WHERE item_ID = %s",
                (item['item_ID'],)
            )
            item_data = cursor.fetchone()
            
            if item_data:
                item_name = item_data['item_name']
                item_price = item_data['price']
                item_countdown = item_data['countdown']
                item_total = item_price * item['quantity']
                preparation_time = item_countdown * item['quantity']
                
                total_amount += item_total
                total_preparation_time += preparation_time
                
                order_details.append({
                    'item_id': item['item_ID'],
                    'item_name': item_name,
                    'quantity': item['quantity'],
                    'unit_price': float(item_price),
                    'total_price': float(item_total),
                    'preparation_time_per_unit': item_countdown,
                    'total_preparation_time': preparation_time
                })
                
                print(f"    Item {i+1}: {item_name} x {item['quantity']} = ₹{item_total} | Prep: {preparation_time}min")
            else:
                print(f"    ERROR: Item {item['item_ID']} not found in Menu_Item")
                connection.close()
                return jsonify({'error': f'Item {item["item_ID"]} not found in menu'}), 400
        
        print(f" DEBUG: Total preparation time: {total_preparation_time} minutes")
        print(f" DEBUG: Total order amount: ₹{total_amount}")
        
        # Start transaction
        connection.begin()
        
        # 1. Insert into Orders table FIRST
        print(" DEBUG: Inserting into Orders table...")
        cursor.execute(
            "INSERT INTO Orders (order_id, order_time, status, quantity, customer_id, shop_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (order_id, datetime.now(), 'Pending', total_quantity, customer_id, shop_id)
        )
        print(" DEBUG: Order inserted successfully")
        
        # 2. Insert order items AFTER order is created
        print(" DEBUG: Inserting order items...")
        for i, item in enumerate(items):
            cursor.execute(
                "INSERT INTO Order_Menu_Item (order_id, item_id, quantity) VALUES (%s, %s, %s)",
                (order_id, item['item_ID'], item['quantity'])
            )
            print(f"    Added {item['item_ID']} x {item['quantity']}")
        print(" DEBUG: All order items inserted")
        
        # 3. Create payment record
        print(" DEBUG: Creating payment record...")
        cursor.execute(
            "INSERT INTO Payment (payment_id, timestamp, mode, pstatus, order_id) VALUES (%s, %s, %s, %s, %s)",
            (payment_id, datetime.now(), payment_mode, 'Pending', order_id)
        )
        print(" DEBUG: Payment record created")
        
        # 4. Create kitchen status
        print(" DEBUG: Creating kitchen status...")
        kitchen_status = 'Preparing'
        cursor.execute(
            "INSERT INTO Kitchen_Status (prep_id, current_status, start_time, order_id) VALUES (%s, %s, %s, %s)",
            (prep_id, kitchen_status, datetime.now(), order_id)
        )
        print(" DEBUG: Kitchen status created")
        
        # Calculate estimated ready time
        order_time = datetime.now()
        estimated_ready_time = order_time + timedelta(minutes=total_preparation_time)
        
        # COMMIT ALL TRANSACTIONS TOGETHER
        print(" DEBUG: Committing all transactions...")
        connection.commit()
        print(" DEBUG: All transactions committed successfully")
        
        cursor.close()
        connection.close()
        print(" DEBUG: Database connection closed")
        
        # Prepare comprehensive response
        response_data = {
            'success': True,
            'order_id': order_id,
            'order_summary': {
                'order_id': order_id,
                'transaction_id': payment_id,
                'customer_id': customer_id,
                'shop_id': shop_id,
                'order_time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Pending',
                'kitchen_status': kitchen_status,
                'preparation_id': prep_id
            },
            'payment_details': {
                'payment_mode': payment_mode,
                'payment_status': 'Pending',
                'transaction_id': payment_id
            },
            'order_timing': {
                'total_preparation_time_minutes': total_preparation_time,
                'order_placed_at': order_time.strftime('%H:%M:%S'),
                'estimated_ready_at': estimated_ready_time.strftime('%H:%M:%S'),
                'countdown_timer': f"{total_preparation_time} minutes"
            },
            'financial_summary': {
                'total_amount': float(total_amount),
                'total_quantity': total_quantity,
                'currency': 'INR'
            },
            'order_items': order_details,
            'message': f'Order placed successfully! Your food will be ready in approximately {total_preparation_time} minutes.'
        }
        
        print("🎉 DEBUG: Order completed successfully with all details")
        return jsonify(response_data)
        
    except Exception as e:
        print(f" CRITICAL ERROR: {str(e)}")
        error_details = traceback.format_exc()
        print(f" FULL ERROR TRACEBACK:\n{error_details}")
        
        # Rollback if connection exists
        if 'connection' in locals() and connection:
            print(" DEBUG: Rolling back transaction...")
            connection.rollback()
            connection.close()
            
        return jsonify({'error': str(e)}), 500

# 4. MENU APIS


@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Fetches and displays the entire menu from all shops, joining Menu_Item, Inventory, and Shop."""
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500
    
    cursor = db.cursor(dictionary=True)
    
    # Complex SELECT Query to get full menu details with shop information
    query = """
        SELECT 
            MI.item_ID, 
            MI.item_name, 
            MI.price, 
            MI.countdown, 
            MI.delay, 
            MI.shop_ID,
            S.shop_name,
            S.location,
            I.quantity,
            I.available
        FROM 
            Menu_Item MI
        JOIN 
            Shop S ON MI.shop_ID = S.shop_ID
        LEFT JOIN
            Inventory I ON MI.item_ID = I.item_ID
        ORDER BY 
            S.shop_ID, MI.item_name;
    """
    
    try:
        cursor.execute(query)
        menu_data = cursor.fetchall()
        
        # Process data for the frontend
        for item in menu_data:
            item['prep_time'] = item['countdown'] + item['delay']
            item['available'] = bool(item['available']) if item['available'] is not None else False
            item['price'] = float(item['price']) if item['price'] else 0.0
            item['quantity'] = item['quantity'] if item['quantity'] is not None else 0
            
        return jsonify(menu_data)

    except mysql.connector.Error as err:
        print(f"Menu Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error fetching menu: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/menu_items/<shop_id>', methods=['GET'])
def get_menu_items(shop_id):
    """Get menu items for a specific shop (kept for backward compatibility)"""
    try:
        connection = get_db_connection_pymysql()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT mi.item_ID, mi.item_name, mi.price, mi.countdown, i.quantity as available
            FROM Menu_Item mi
            LEFT JOIN Inventory i ON mi.item_ID = i.item_ID
            WHERE mi.shop_ID = %s
        """, (shop_id,))
        
        menu_items = cursor.fetchall()
        
        # Convert Decimal to float for JSON serialization
        for item in menu_items:
            if item['price']:
                item['price'] = float(item['price'])
        
        return jsonify({'menu_items': menu_items})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()


# 1. API to get customer's active orders with status
@app.route('/api/customer/my-orders/<customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    """
    Fetches all orders for a specific customer with their current status.
    Used for real-time notifications on customer side.
    """
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT 
            O.order_id,
            O.order_time,
            O.status as order_status,
            O.quantity as total_items,
            S.shop_name,
            S.location as shop_location,
            KS.current_status as kitchen_status,
            KS.start_time as prep_start_time,
            KS.end_time as prep_end_time,
            P.mode as payment_mode,
            P.pstatus as payment_status,
            GROUP_CONCAT(CONCAT(MI.item_name, ' x', OMI.quantity) SEPARATOR ', ') as order_items,
            SUM(MI.price * OMI.quantity) as total_amount
        FROM 
            Orders O
        JOIN 
            Shop S ON O.shop_id = S.shop_ID
        LEFT JOIN
            Kitchen_Status KS ON O.order_id = KS.order_id
        LEFT JOIN
            Payment P ON O.order_id = P.order_id
        LEFT JOIN
            Order_Menu_Item OMI ON O.order_id = OMI.order_id
        LEFT JOIN
            Menu_Item MI ON OMI.item_id = MI.item_ID
        WHERE 
            O.customer_id = %s
            AND O.order_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY 
            O.order_id, O.order_time, O.status, O.quantity,
            S.shop_name, S.location, KS.current_status, 
            KS.start_time, KS.end_time, P.mode, P.pstatus
        ORDER BY 
            O.order_time DESC;
    """
    
    try:
        cursor.execute(query, (customer_id,))
        orders = cursor.fetchall()
        
        # Format datetime and calculate prep time
        for order in orders:
            if order['order_time']:
                order['order_time'] = order['order_time'].strftime('%Y-%m-%d %H:%M:%S')
            if order['prep_start_time']:
                order['prep_start_time'] = order['prep_start_time'].strftime('%Y-%m-%d %H:%M:%S')
            if order['prep_end_time']:
                order['prep_end_time'] = order['prep_end_time'].strftime('%Y-%m-%d %H:%M:%S')
                
            # Calculate preparation time if completed
            if order['prep_start_time'] and order['prep_end_time']:
                start = datetime.strptime(order['prep_start_time'], '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(order['prep_end_time'], '%Y-%m-%d %H:%M:%S')
                prep_minutes = (end - start).total_seconds() / 60
                order['actual_prep_time'] = f"{int(prep_minutes)} minutes"
            
            # Convert Decimal to float
            if order['total_amount']:
                order['total_amount'] = float(order['total_amount'])
            
            # Add notification flag
            order['needs_notification'] = (order['kitchen_status'] == 'Ready' and 
                                          order['order_status'] != 'Completed')
        
        return jsonify({
            'status': 'Success',
            'customer_id': customer_id,
            'orders': orders
        })

    except mysql.connector.Error as err:
        print(f"Customer Orders Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()


# 2. API to get notification count for a customer
@app.route('/api/customer/notifications/<customer_id>', methods=['GET'])
def get_customer_notifications(customer_id):
    """
    Get count of orders that are ready for pickup (notifications).
    """
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT 
            COUNT(*) as notification_count,
            GROUP_CONCAT(O.order_id SEPARATOR ',') as ready_orders
        FROM 
            Orders O
        JOIN 
            Kitchen_Status KS ON O.order_id = KS.order_id
        WHERE 
            O.customer_id = %s
            AND KS.current_status = 'Ready'
            AND O.status != 'Completed'
            AND O.order_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR);
    """
    
    try:
        cursor.execute(query, (customer_id,))
        result = cursor.fetchone()
        
        return jsonify({
            'status': 'Success',
            'customer_id': customer_id,
            'notification_count': result['notification_count'] or 0,
            'ready_orders': result['ready_orders'].split(',') if result['ready_orders'] else []
        })

    except mysql.connector.Error as err:
        print(f"Notifications Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()


# 3. API to mark order as picked up/completed
@app.route('/api/customer/complete-order/<order_id>', methods=['POST'])
def complete_order(order_id):
    """
    Mark an order as completed/picked up.
    """
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor()
    
    try:
        # Update order status to Completed
        update_query = """
            UPDATE Orders 
            SET status = 'Completed'
            WHERE order_id = %s
        """
        cursor.execute(update_query, (order_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'status': 'Failed', 'message': 'Order not found'}), 404
        
        return jsonify({
            'status': 'Success',
            'message': 'Order marked as completed',
            'order_id': order_id
        })

    except mysql.connector.Error as err:
        db.rollback()
        print(f"Complete Order Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

# PHASE 2: ADMIN/REPORTS APIS

@app.route('/api/kitchen/staff-info', methods=['GET'])
def get_kitchen_staff_info():
    """Fetches kitchen staff information including assigned shop."""
    staff_id = request.args.get('staff_id')
    
    if not staff_id:
        return jsonify({'status': 'Failed', 'message': 'staff_id is required'}), 400
    
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT 
            KS.staff_id,
            KS.staff_name,
            KS.shop_id,
            KS.role,
            KS.shift_timing,
            S.shop_name,
            S.location
        FROM 
            Kitchen_Staff KS
        JOIN 
            Shop S ON KS.shop_id = S.shop_ID
        WHERE 
            KS.staff_id = %s;
    """
    
    try:
        cursor.execute(query, (staff_id,))
        staff_info = cursor.fetchone()
        
        if staff_info:
            return jsonify({
                'status': 'Success',
                **staff_info
            })
        else:
            return jsonify({'status': 'Failed', 'message': 'Staff not found'}), 404

    except mysql.connector.Error as err:
        print(f"Staff Info Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/admin/active-orders', methods=['GET'])
def get_active_orders():
    """Fetches all active orders with kitchen status for the kitchen dashboard."""
    shop_id = request.args.get('shop_id')  
    
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT 
            O.order_id,
            O.order_time,
            O.quantity as item_count,
            O.customer_id,
            S.shop_name,
            S.shop_ID,
            KS.prep_id,
            KS.current_status,
            KS.start_time,
            GROUP_CONCAT(CONCAT(MI.item_name, ' x', OMI.quantity) SEPARATOR ', ') as order_items
        FROM 
            Orders O
        JOIN 
            Shop S ON O.shop_id = S.shop_ID
        JOIN
            Kitchen_Status KS ON O.order_id = KS.order_id
        LEFT JOIN
            Order_Menu_Item OMI ON O.order_id = OMI.order_id
        LEFT JOIN
            Menu_Item MI ON OMI.item_id = MI.item_ID
        WHERE 
            KS.current_status = 'Preparing'
    """
    
    # Add shop filter if provided
    if shop_id:
        query += " AND S.shop_ID = %s"
    
    query += """
        GROUP BY 
            O.order_id, O.order_time, O.quantity, O.customer_id, 
            S.shop_name, S.shop_ID, KS.prep_id, KS.current_status, KS.start_time
        ORDER BY 
            O.order_time ASC;
    """
    
    try:
        if shop_id:
            cursor.execute(query, (shop_id,))
        else:
            cursor.execute(query)
            
        orders_data = cursor.fetchall()
        
        # Convert datetime objects to strings
        for order in orders_data:
            if order['order_time']:
                order['order_time'] = order['order_time'].strftime('%Y-%m-%d %H:%M:%S')
            if order['start_time']:
                order['start_time'] = order['start_time'].strftime('%Y-%m-%d %H:%M:%S')
            
        return jsonify(orders_data)

    except mysql.connector.Error as err:
        print(f"Active Orders Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error fetching active orders: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/admin/update-status', methods=['POST'])
def update_order_status():
    """Updates kitchen status to 'Ready' which triggers the NotifyOrderReady trigger."""
    data = request.json
    prep_id = data.get('prep_id')
    new_status = data.get('new_status', 'Ready')
    
    if not prep_id:
        return jsonify({'status': 'Failed', 'message': 'prep_id is required'}), 400
    
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor()
    
    try:
        # Update kitchen status to 'Ready' - this will trigger the NotifyOrderReady trigger
        update_query = """
            UPDATE Kitchen_Status 
            SET current_status = %s, end_time = NOW() 
            WHERE prep_id = %s
        """
        cursor.execute(update_query, (new_status, prep_id))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'status': 'Failed', 'message': 'prep_id not found'}), 404
        
        return jsonify({
            'status': 'Success', 
            'message': f'Order status updated to {new_status}. Notification triggered.',
            'prep_id': prep_id
        })

    except mysql.connector.Error as err:
        db.rollback()
        print(f"Status Update Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error updating status: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()


@app.route('/api/admin/inventory', methods=['GET'])
def get_inventory_status():
    """
    Fetches inventory status showing items that need reordering.
    This demonstrates the CheckReorderLevel trigger functionality.
    """
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT 
            MI.item_name,
            S.shop_name,
            I.quantity,
            I.unit,
            I.reorder_level,
            CASE 
                WHEN I.quantity <= I.reorder_level THEN 1
                ELSE 0
            END AS reorder_needed
        FROM 
            Inventory I
        JOIN 
            Menu_Item MI ON I.item_ID = MI.item_ID
        JOIN 
            Shop S ON MI.shop_ID = S.shop_ID
        ORDER BY 
            reorder_needed DESC,
            S.shop_name,
            MI.item_name;
    """
    
    try:
        cursor.execute(query)
        inventory_data = cursor.fetchall()
        
        # Convert reorder_needed to boolean
        for item in inventory_data:
            item['reorder_needed'] = bool(item['reorder_needed'])
            
        return jsonify(inventory_data)

    except mysql.connector.Error as err:
        print(f"Inventory Fetch Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error fetching inventory: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/admin/update-inventory', methods=['POST'])
def update_inventory():
    """Updates inventory by reducing quantity when items are used."""
    data = request.json
    item_id = data.get('item_id')
    quantity_used = data.get('quantity_used')
    
    if not item_id or not quantity_used:
        return jsonify({'status': 'Failed', 'message': 'item_id and quantity_used are required'}), 400
    
    try:
        quantity_used = int(quantity_used)
        if quantity_used <= 0:
            return jsonify({'status': 'Failed', 'message': 'Quantity must be positive'}), 400
    except ValueError:
        return jsonify({'status': 'Failed', 'message': 'Invalid quantity value'}), 400
    
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    try:
        # Check if item exists in inventory
        cursor.execute("SELECT inventory_id, quantity, item_ID FROM Inventory WHERE item_ID = %s", (item_id,))
        inventory = cursor.fetchone()
        
        if not inventory:
            return jsonify({'status': 'Failed', 'message': f'Item {item_id} not found in inventory'}), 404
        
        current_quantity = inventory['quantity']
        
        # Check if enough quantity available
        if current_quantity < quantity_used:
            return jsonify({
                'status': 'Failed', 
                'message': f'Insufficient inventory. Available: {current_quantity}, Requested: {quantity_used}'
            }), 400
        
        # Update inventory by reducing quantity
        new_quantity = current_quantity - quantity_used
        
        update_query = """
            UPDATE Inventory 
            SET quantity = %s,
                available = CASE WHEN %s > 0 THEN 1 ELSE 0 END
            WHERE item_ID = %s
        """
        
        cursor.execute(update_query, (new_quantity, new_quantity, item_id))
        db.commit()
        
        # Get updated inventory info
        cursor.execute("""
            SELECT I.quantity, I.reorder_level, MI.item_name 
            FROM Inventory I
            JOIN Menu_Item MI ON I.item_ID = MI.item_ID
            WHERE I.item_ID = %s
        """, (item_id,))
        
        updated_item = cursor.fetchone()
        
        response_data = {
            'status': 'Success',
            'message': f'Inventory updated successfully for {item_id}',
            'item_id': item_id,
            'item_name': updated_item['item_name'] if updated_item else 'Unknown',
            'quantity_used': quantity_used,
            'previous_quantity': current_quantity,
            'new_quantity': new_quantity
        }
        
        # Add reorder alert if needed
        if updated_item and new_quantity <= updated_item['reorder_level']:
            response_data['alert'] = f" Low stock alert! Current: {new_quantity}, Reorder Level: {updated_item['reorder_level']}"
        
        return jsonify(response_data)

    except mysql.connector.Error as err:
        db.rollback()
        print(f"Inventory Update Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Database error: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/admin/sales-report', methods=['GET'])
def get_sales_report():
    """
    Executes a complex query for sales analysis.
    """
    db = get_db_connection()
    if not db:
        return jsonify({'status': 'Failed', 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    
    complex_query = """
        SELECT 
            S.shop_name, 
            COUNT(DISTINCT O.order_id) AS total_orders, 
            SUM(OMI.quantity) AS total_items_sold,
            SUM(MI.price * OMI.quantity) AS gross_revenue
        FROM 
            Orders O
        JOIN 
            Shop S ON O.shop_id = S.shop_ID
        JOIN 
            Order_Menu_Item OMI ON O.order_id = OMI.order_id
        JOIN 
            Menu_Item MI ON OMI.item_id = MI.item_ID
        GROUP BY 
            S.shop_name
        ORDER BY 
            gross_revenue DESC;
    """
    
    try:
        cursor.execute(complex_query)
        report_data = cursor.fetchall()
        
        for row in report_data:
            row['gross_revenue'] = float(row['gross_revenue']) if row['gross_revenue'] is not None else 0.0

        return jsonify(report_data)

    except mysql.connector.Error as err:
        print(f"Sales Report Query Error: {err}")
        return jsonify({'status': 'Failed', 'message': f'Server error fetching sales report: {err.msg}'}), 500
    finally:
        cursor.close()
        db.close()



@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'PESU Food Systems API is running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })



if __name__ == '__main__':
    app.run(debug=True, port=5000)