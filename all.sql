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

