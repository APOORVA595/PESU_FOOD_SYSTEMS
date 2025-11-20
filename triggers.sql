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
