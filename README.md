PESU Food System
PESU Food System A full-stack, database-powered food ordering and management system designed for PES University. This application enables students, shop owners, and administrators to efficiently manage food orders, menu items, inventory, payments, kitchen operations, and notifications in real time.

🌟Features:
👤Customer Features:
1. Browse shops and menus
2. View item availability
3. Add items to cart
4. Place orders
5. Track order status (Preparing → Ready → Delivered)
6. Receive notifications when the order is ready

🏪Kitchen Features:
1. Manage menu & item details
2. View incoming orders
3. Update kitchen status (Preparing/Ready/Delivered)
4. Monitor inventory levels

👨‍💼Admin Features:
1. Manage shops and customers
2. Track inventory shortages
3. Handles payment distribution between different shops manually.

🗄️Database Architecture:
The system is built using a normalized relational schema with the following core entities:
Shop
Customer
Menu_Item
Inventory
Orders
Order_Menu_Item
Payment
Kitchen_Status
Notification

✔Enforced using:
Foreign key
Unique constraints
Check constraints
Cascade deletions
Triggers
Stored procedures
Functions

⚙️Technologies Used:
Component	                Details
Frontend	               HTML, CSS, JavaScript
Backend	                 Python Flask
Database                 MySQL
Version Control	         Git & GitHub
Tools	                   VS Code, MySQL Workbench

🧩 SQL Components:
🔥 Triggers
1️⃣ NotifyOrderReady
Automatically creates a notification when an order becomes Ready.

2️⃣ CheckReorderLevel
Alerts admin/shop when inventory is low.

🧮 Functions
✔ GetOrderTotal(order_id)
Calculates order bill using menu prices × item quantities.

✔ IsItemAvailable(item_id)
Checks whether a menu item is available.

🛠 Procedures
✔ AddOrder(…)
Inserts a new order into the system.

✔ UpdateInventory(…)
Reduces item quantity after order completion.

📊 Complex SQL Queries:
The system includes advanced SQL operations:
JOIN queries (shop, menu, inventory, orders, payment)
Aggregation queries (SUM, COUNT, GROUP BY)
Inventory reorder checks
Last-24-hour order listings
Kitchen staff & shop mapping queries
Real-time order tracking queries

📂 Project Structure:
DBMS MINI PROJECT/
├── static/
│   ├── admin.js
│   ├── kitchen.js
│   ├── login.js
│   ├── script.js
│   └── style.css
├── templates/
│   ├── admin_dashboard.html
│   ├── customer_order_page.html
│   ├── customer_orders.html
│   ├── kitchen_dashboard.html
│   ├── login.html
│   └── reports_dashboard.html
├── app.py
├── functions.sql
├── PESUFoodSystems.pdf
├── PESU_FOOD_SYSTEMS.sql
├── procedures.sql
├── queries_with_constraints.sql
├── queries.sql
└── triggers.sql

🚀 How to Run the Project
1. Clone the Repository
git clone https://github.com/APOORVA595/PESU_FOOD_SYSTEMS
cd PESU_FOOD_SYSTEMS

2. Import Database
Open MySQL / phpMyAdmin and import:
PESU_FOOD_SYSTEMS.sql

3. Install Dependencies
pip install flask
pip install mysql-connector-python
pip install flask-cors
pip install python-dotenv

5. Start Server
python app.py

6. Open in Browser
(http://127.0.0.1:5000/)

🤝 Contributors
Ashrita Hatwar T
Apoorva Biradar

📝 License
This project is developed as part of PES University – DBMS Mini Project
