PESU Food System
A full-stack, database-powered food ordering and management system designed for PES University.
This application enables students, shop owners, and administrators to efficiently manage food orders, menu items, inventory, payments, kitchen operations, and notifications in real time.

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
Backend	                 Node.js
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
/food_system
│── /static
│     ├── /css
│     ├── /js
│     └── /uploads
│── /templates
│     ├── /admin
│     ├── /shop
│     ├── /user
│     └── /includes
│── /sql
│── app.js / server.js (backend)
│── PESU_FOOD_SYSTEMS.sql (database)
└── README.md

🚀 How to Run the Project
1. Clone the Repository
git clone https://github.com/your-repo-link.git
cd food_system

2. Import Database
Open MySQL / phpMyAdmin and import:
PESU_FOOD_SYSTEMS.sql

3. Install Dependencies
npm install

4. Start Server
node server.js

5. Open in Browser
http://localhost:3000

🤝 Contributors
Ashrita Hatwar T
Apoorva Biradar

📝 License
This project is developed as part of PES University – DBMS Mini Project
