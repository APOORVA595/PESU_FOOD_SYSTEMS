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
