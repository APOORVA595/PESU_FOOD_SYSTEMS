CREATE TABLE Shop (
    shop_ID VARCHAR(10) PRIMARY KEY,
    shop_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100)
);

CREATE TABLE Customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Customer_Phone (
    customer_id VARCHAR(20),
    phone VARCHAR(15) CHECK (phone REGEXP '^[0-9]{10}$'),
    PRIMARY KEY (customer_id, phone),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

CREATE TABLE Customer_Email (
    customer_id VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    PRIMARY KEY (customer_id, email),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

CREATE TABLE Menu_Item (
    item_ID VARCHAR(10) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    countdown INT DEFAULT 0 CHECK (countdown >= 0),
    delay INT DEFAULT 0 CHECK (delay >= 0),
    price DECIMAL(6,2) NOT NULL CHECK (price > 0),
    shop_ID VARCHAR(10),
    FOREIGN KEY (shop_ID) REFERENCES Shop(shop_ID)
        ON DELETE CASCADE
);

CREATE TABLE Inventory (
    inventory_id VARCHAR(10) PRIMARY KEY,
    item_name VARCHAR(100) UNIQUE NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    available BOOLEAN DEFAULT TRUE,
    reorder_level INT DEFAULT 10 CHECK (reorder_level >= 0),
    unit VARCHAR(10) CHECK (unit IN ('kg', 'packets', 'l/ml')),
    item_ID VARCHAR(10) UNIQUE,
    FOREIGN KEY (item_ID) REFERENCES Menu_Item(item_ID)
        ON DELETE SET NULL
);

CREATE TABLE Orders (
    order_id VARCHAR(20) PRIMARY KEY,
    order_time DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    quantity INT CHECK (quantity > 0),
    pickup_time DATETIME,
    customer_id VARCHAR(20),
    shop_id VARCHAR(10),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE,
    FOREIGN KEY (shop_id) REFERENCES Shop(shop_ID)
        ON DELETE CASCADE
);

CREATE TABLE Order_Menu_Item (
    order_id VARCHAR(20),
    item_id VARCHAR(10),
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Menu_Item(item_ID)
);

CREATE TABLE Payment (
    payment_id VARCHAR(20) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    mode VARCHAR(50) CHECK (mode IN ('Cash', 'UPI', 'Card', 'Online')),
    pstatus VARCHAR(50) CHECK (pstatus IN ('Success', 'Pending', 'Failed')),
    order_id VARCHAR(20) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE
);

CREATE TABLE Kitchen_Status (
    prep_id VARCHAR(20) PRIMARY KEY,
    current_status VARCHAR(50) CHECK (current_status IN ('Preparing', 'Ready', 'Delivered')),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    order_id VARCHAR(20) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE
);

CREATE TABLE Notification (
    notification_id VARCHAR(20) PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    order_id VARCHAR(20),
    prep_id VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (prep_id) REFERENCES Kitchen_Status(prep_id)
        ON DELETE CASCADE
);


--TRIGGERS
--Auto Notification When Order is Ready
DELIMITER //
CREATE TRIGGER NotifyOrderReady
AFTER UPDATE ON Kitchen_Status
FOR EACH ROW
BEGIN
    IF NEW.current_status = 'Ready' THEN
        INSERT INTO Notification (notification_id, message, generated_at, is_read, order_id, prep_id)
        VALUES (CONCAT('N', UUID()), CONCAT('Order ', NEW.order_id, ' is ready for pickup!'), NOW(), FALSE, NEW.order_id, NEW.prep_id);
    END IF;
END //
DELIMITER ;


--Auto Check for Low Inventory
DELIMITER //
CREATE TRIGGER CheckReorderLevel
AFTER UPDATE ON Inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity <= NEW.reorder_level THEN
        INSERT INTO Notification (notification_id, message, generated_at, is_read)
        VALUES (CONCAT('N', UUID()), CONCAT('Reorder needed for ', NEW.item_name), NOW(), FALSE);
    END IF;
END //
DELIMITER ;


--FUNCTIONS
--Calculate Total Order Amount
DELIMITER //
CREATE FUNCTION GetOrderTotal(p_order_id VARCHAR(20))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT SUM(m.price * o.quantity)
    INTO total
    FROM Order_Menu_Item o
    JOIN Menu_Item m ON o.item_id = m.item_ID
    WHERE o.order_id = p_order_id;
    RETURN IFNULL(total, 0);
END //
DELIMITER ;


--Check Inventory Availability
DELIMITER //
CREATE FUNCTION IsItemAvailable(p_item_id VARCHAR(10))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE available BOOLEAN;
    SELECT available INTO available
    FROM Inventory
    WHERE item_ID = p_item_id;
    RETURN available;
END //
DELIMITER ;


--PROCEDURES
--Add a new order
DELIMITER //
CREATE PROCEDURE AddOrder (
    IN p_order_id VARCHAR(20),
    IN p_customer_id VARCHAR(20),
    IN p_shop_id VARCHAR(10),
    IN p_quantity INT
)
BEGIN
    INSERT INTO Orders (order_id, order_time, quantity, customer_id, shop_id)
    VALUES (p_order_id, NOW(), p_quantity, p_customer_id, p_shop_id);
END //
DELIMITER ;

--Update Inventory After an Order
DELIMITER //
CREATE PROCEDURE UpdateInventory (
    IN p_item_id VARCHAR(10),
    IN p_order_qty INT
)
BEGIN
    UPDATE Inventory
    SET quantity = quantity - p_order_qty,
        available = CASE WHEN quantity - p_order_qty <= 0 THEN FALSE ELSE TRUE END
    WHERE item_ID = p_item_id;
END //
DELIMITER ;

--QUERIES
INSERT INTO Orders (order_id, order_time, status, quantity, customer_id, shop_id) VALUES (%s, %s, %s, %s, %s, %s)
INSERT INTO Order_Menu_Item (order_id, item_id, quantity) VALUES (%s, %s, %s)
INSERT INTO Payment (payment_id, timestamp, mode, pstatus, order_id) VALUES (%s, %s, %s, %s, %s)
INSERT INTO Kitchen_Status (prep_id, current_status, start_time, order_id) VALUES (%s, %s, %s, %s)

--Complex queries to get full menu details with shop information
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

SELECT mi.item_ID, mi.item_name, mi.price, mi.countdown, i.quantity as available
            FROM Menu_Item mi
            LEFT JOIN Inventory i ON mi.item_ID = i.item_ID
            WHERE mi.shop_ID = %s;

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

UPDATE Orders 
            SET status = 'Completed'
            WHERE order_id = %s;   

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
            KS.current_status = 'Preparing';

GROUP BY 
            O.order_id, O.order_time, O.quantity, O.customer_id, 
            S.shop_name, S.shop_ID, KS.prep_id, KS.current_status, KS.start_time
        ORDER BY 
            O.order_time ASC;

UPDATE Kitchen_Status 
            SET current_status = %s, end_time = NOW() 
            WHERE prep_id = %s;

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

UPDATE Inventory 
            SET quantity = %s,
                available = CASE WHEN %s > 0 THEN 1 ELSE 0 END
            WHERE item_ID = %s;

SELECT I.quantity, I.reorder_level, MI.item_name 
            FROM Inventory I
            JOIN Menu_Item MI ON I.item_ID = MI.item_ID
            WHERE I.item_ID = %s;

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
