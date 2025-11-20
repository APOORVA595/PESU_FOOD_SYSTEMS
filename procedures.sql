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
