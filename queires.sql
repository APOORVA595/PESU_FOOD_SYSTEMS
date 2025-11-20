CREATE TABLE Shop (
    shop_ID VARCHAR(10) PRIMARY KEY,
    shop_name VARCHAR(100) NOT NULL,
    location VARCHAR(100)
);

CREATE TABLE Customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Customer_Phone (
    customer_id VARCHAR(20),
    phone VARCHAR(15),
    PRIMARY KEY (customer_id, phone),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Customer_Email (
    customer_id VARCHAR(20),
    email VARCHAR(100),
    PRIMARY KEY (customer_id, email),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Menu_Item (
    item_ID VARCHAR(10) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    countdown INT,
    delay INT,
    price DECIMAL(6,2) NOT NULL,
    shop_ID VARCHAR(10),
    FOREIGN KEY (shop_ID) REFERENCES Shop(shop_ID)
);

CREATE TABLE Inventory (
    inventory_id VARCHAR(10) PRIMARY KEY,
    item_name VARCHAR(100) UNIQUE,
    quantity INT NOT NULL,
    available BOOLEAN,
    reorder_level INT,
    unit VARCHAR(10) CHECK (unit IN ('kg', 'packets', 'l/ml')),
    item_ID VARCHAR(10) UNIQUE,
    FOREIGN KEY (item_ID) REFERENCES Menu_Item(item_ID)
);

CREATE TABLE Orders (
    order_id VARCHAR(20) PRIMARY KEY,
    order_time DATETIME NOT NULL,
    status VARCHAR(50),
    quantity INT,
    pickup_time DATETIME,
    customer_id VARCHAR(20),
    shop_id VARCHAR(10),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (shop_id) REFERENCES Shop(shop_ID)
);

CREATE TABLE Order_Menu_Item (
    order_id VARCHAR(20),
    item_id VARCHAR(10),
    quantity INT NOT NULL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (item_id) REFERENCES Menu_Item(item_ID)
);

CREATE TABLE Payment (
    payment_id VARCHAR(20) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    mode VARCHAR(50),
    pstatus VARCHAR(50) CHECK (pstatus IN ('Success', 'Pending', 'Failed')),
    order_id VARCHAR(20) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

CREATE TABLE Kitchen_Status (
    prep_id VARCHAR(20) PRIMARY KEY,
    current_status VARCHAR(50),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    order_id VARCHAR(20) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

CREATE TABLE Notification (
    notification_id VARCHAR(20) PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    generated_at DATETIME NOT NULL,
    is_read BOOLEAN,
    order_id VARCHAR(20),
    prep_id VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (prep_id) REFERENCES Kitchen_Status(prep_id)
);
