-- =====================================================================
--  TRANSPORT MANAGEMENT SYSTEM - SQL CONCEPTS DEMONSTRATION
--  Run THIRD in MySQL Workbench (optional, for viva / presentation).
--  Covers: CRUD, JOINs, Aggregates, GROUP BY/HAVING, Sub-queries,
--          Views, Indexes, Stored Procedure, Function, Triggers,
--          Transactions (COMMIT/ROLLBACK), Constraint tests, DCL.
--  TIP: In Workbench place the cursor on one statement and press
--       Ctrl+Enter to run only that statement.
-- =====================================================================
USE transport_db;

-- =====================================================================
-- PART A : CRUD OPERATIONS  (Create, Read, Update, Delete)
-- =====================================================================

-- CREATE (INSERT)
INSERT INTO customers (full_name, company, phone, email, city, address)
VALUES ('Test Customer', 'Demo Co', '+92-399-0000001', 'test@demo.pk', 'Karachi', 'Clifton');

-- READ (SELECT with WHERE, ORDER BY, LIMIT)
SELECT customer_id, full_name, city FROM customers
WHERE city = 'Karachi'
ORDER BY full_name
LIMIT 5;

-- READ with search (LIKE)
SELECT * FROM customers WHERE full_name LIKE '%Test%';

-- UPDATE
UPDATE customers SET city = 'Hyderabad', address = 'Qasimabad'
WHERE phone = '+92-399-0000001';

-- DELETE
DELETE FROM customers WHERE phone = '+92-399-0000001';


-- =====================================================================
-- PART B : JOINS
-- =====================================================================

-- B1. INNER JOIN (4 tables) - every shipment with customer, route, driver
SELECT s.tracking_no, c.full_name AS customer,
       CONCAT(r.origin, ' -> ', r.destination) AS route,
       d.full_name AS driver, s.status
FROM shipments s
INNER JOIN customers c ON s.customer_id = c.customer_id
INNER JOIN routes    r ON s.route_id    = r.route_id
INNER JOIN drivers   d ON s.driver_id   = d.driver_id
ORDER BY s.ship_date;

-- B2. LEFT JOIN - all customers, even those with NO shipment (Omar Farooq)
SELECT c.full_name, c.city, COUNT(s.shipment_id) AS total_shipments
FROM customers c
LEFT JOIN shipments s ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.city
ORDER BY total_shipments DESC;

-- B3. RIGHT JOIN - all vehicles, including vehicles that never carried a shipment
SELECT v.plate_no, v.vehicle_type, s.tracking_no
FROM shipments s
RIGHT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
ORDER BY v.plate_no;

-- B4. Find shipments with NO driver assigned yet (LEFT JOIN + IS NULL)
SELECT s.tracking_no, s.status, s.ship_date
FROM shipments s
LEFT JOIN drivers d ON s.driver_id = d.driver_id
WHERE d.driver_id IS NULL;

-- B5. SELF JOIN - routes that start where another route ends (connecting routes)
SELECT r1.origin, r1.destination AS via, r2.destination AS final_destination,
       r1.distance_km + r2.distance_km AS total_km
FROM routes r1
INNER JOIN routes r2 ON r1.destination = r2.origin;


-- =====================================================================
-- PART C : AGGREGATE FUNCTIONS, GROUP BY, HAVING
-- =====================================================================

-- C1. Revenue and shipment count per route
SELECT CONCAT(r.origin, ' -> ', r.destination) AS route,
       COUNT(*)              AS shipments,
       SUM(s.weight_kg)      AS total_weight_kg,
       SUM(s.freight_charge) AS total_revenue,
       AVG(s.freight_charge) AS avg_charge
FROM shipments s
JOIN routes r ON r.route_id = s.route_id
WHERE s.status <> 'Cancelled'
GROUP BY r.route_id, r.origin, r.destination
ORDER BY total_revenue DESC;

-- C2. Customers whose total business is more than 100,000 PKR (HAVING)
SELECT c.full_name, SUM(s.freight_charge) AS total_business
FROM customers c
JOIN shipments s ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
HAVING SUM(s.freight_charge) > 100000;

-- C3. Shipments count by status
SELECT status, COUNT(*) AS total FROM shipments GROUP BY status;

-- C4. Total maintenance cost per vehicle (MAX, MIN, SUM)
SELECT v.plate_no, COUNT(m.maint_id) AS services,
       SUM(m.cost) AS total_cost, MAX(m.service_date) AS last_service
FROM vehicles v
LEFT JOIN maintenance m ON m.vehicle_id = v.vehicle_id
GROUP BY v.vehicle_id, v.plate_no;


-- =====================================================================
-- PART D : SUB-QUERIES
-- =====================================================================

-- D1. Shipments heavier than the average weight
SELECT tracking_no, goods_desc, weight_kg
FROM shipments
WHERE weight_kg > (SELECT AVG(weight_kg) FROM shipments);

-- D2. Outstanding balance per shipment (correlated sub-query)
SELECT s.tracking_no, s.freight_charge,
       (SELECT COALESCE(SUM(p.amount),0) FROM payments p WHERE p.shipment_id = s.shipment_id) AS paid,
       s.freight_charge - (SELECT COALESCE(SUM(p.amount),0) FROM payments p WHERE p.shipment_id = s.shipment_id) AS balance
FROM shipments s
WHERE s.status <> 'Cancelled'
HAVING balance > 0;

-- D3. Drivers who have NEVER been assigned a shipment (NOT IN)
SELECT full_name, status FROM drivers
WHERE driver_id NOT IN (SELECT driver_id FROM shipments WHERE driver_id IS NOT NULL);

-- D4. Customers who used the Karachi -> Lahore route (IN + sub-query)
SELECT full_name FROM customers
WHERE customer_id IN (SELECT customer_id FROM shipments
                      WHERE route_id = (SELECT route_id FROM routes
                                        WHERE origin='Karachi' AND destination='Lahore'));


-- =====================================================================
-- PART E : VIEWS
-- =====================================================================
SELECT * FROM v_shipment_details ORDER BY ship_date DESC;

CREATE OR REPLACE VIEW v_vehicle_utilisation AS
SELECT v.plate_no, v.vehicle_type, v.capacity_kg,
       COUNT(s.shipment_id) AS trips,
       COALESCE(SUM(s.weight_kg),0) AS total_carried_kg
FROM vehicles v
LEFT JOIN shipments s ON s.vehicle_id = v.vehicle_id AND s.status <> 'Cancelled'
GROUP BY v.vehicle_id, v.plate_no, v.vehicle_type, v.capacity_kg;

SELECT * FROM v_vehicle_utilisation;


-- =====================================================================
-- PART F : ALTER TABLE / INDEX (DDL)
-- =====================================================================
ALTER TABLE customers ADD COLUMN ntn_no VARCHAR(20) NULL AFTER company;
ALTER TABLE customers DROP COLUMN ntn_no;
CREATE INDEX idx_customers_city ON customers(city);
SHOW INDEX FROM customers;
DESCRIBE shipments;


-- =====================================================================
-- PART G : STORED PROCEDURE + FUNCTION
-- =====================================================================
DROP PROCEDURE IF EXISTS sp_customer_history;
DROP FUNCTION  IF EXISTS fn_shipment_balance;

DELIMITER $$

-- Procedure: full shipment history of a customer
CREATE PROCEDURE sp_customer_history(IN p_customer_id INT)
BEGIN
    SELECT s.tracking_no, r.origin, r.destination, s.ship_date,
           s.status, s.freight_charge
    FROM shipments s
    JOIN routes r ON r.route_id = s.route_id
    WHERE s.customer_id = p_customer_id
    ORDER BY s.ship_date DESC;
END $$

-- Function: remaining balance of a shipment
CREATE FUNCTION fn_shipment_balance(p_shipment_id INT)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_charge DECIMAL(12,2);
    DECLARE v_paid   DECIMAL(12,2);
    SELECT freight_charge INTO v_charge FROM shipments WHERE shipment_id = p_shipment_id;
    SELECT COALESCE(SUM(amount),0) INTO v_paid FROM payments WHERE shipment_id = p_shipment_id;
    RETURN v_charge - v_paid;
END $$

DELIMITER ;

CALL sp_customer_history(1);
SELECT tracking_no, fn_shipment_balance(shipment_id) AS balance FROM shipments;


-- =====================================================================
-- PART H : TRIGGERS  (audit log + business rule)
-- =====================================================================
CREATE TABLE IF NOT EXISTS shipment_status_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT NOT NULL,
    old_status  VARCHAR(20),
    new_status  VARCHAR(20),
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
);

DROP TRIGGER IF EXISTS trg_shipment_delivered;
DROP TRIGGER IF EXISTS trg_shipment_status_log;

DELIMITER $$

-- BEFORE UPDATE: when status becomes Delivered, auto-fill delivery_date
CREATE TRIGGER trg_shipment_delivered
BEFORE UPDATE ON shipments
FOR EACH ROW
BEGIN
    IF NEW.status = 'Delivered' AND NEW.delivery_date IS NULL THEN
        SET NEW.delivery_date = CURDATE();
    END IF;
END $$

-- AFTER UPDATE: keep an audit trail of every status change
CREATE TRIGGER trg_shipment_status_log
AFTER UPDATE ON shipments
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO shipment_status_log (shipment_id, old_status, new_status)
        VALUES (NEW.shipment_id, OLD.status, NEW.status);
    END IF;
END $$

DELIMITER ;

-- Test the triggers
UPDATE shipments SET status = 'Delivered' WHERE tracking_no = 'TMS-2026-0012';
SELECT tracking_no, status, delivery_date FROM shipments WHERE tracking_no = 'TMS-2026-0012';
SELECT * FROM shipment_status_log;


-- =====================================================================
-- PART I : TRANSACTION  (ACID - COMMIT / ROLLBACK)
-- =====================================================================
START TRANSACTION;
    INSERT INTO payments (shipment_id, amount, method, payment_date)
    VALUES (5, 50000, 'Bank Transfer', CURDATE());
    UPDATE shipments SET status = 'Delivered' WHERE shipment_id = 5;
ROLLBACK;      -- change mind: nothing above is saved
-- COMMIT;     -- use COMMIT instead to save permanently

SELECT * FROM payments WHERE shipment_id = 5;


-- =====================================================================
-- PART J : CONSTRAINT TESTS (each of these SHOULD FAIL with an error)
-- =====================================================================
-- PRIMARY KEY violation (duplicate id)
-- INSERT INTO customers (customer_id, full_name, phone, city) VALUES (1, 'Dup', '+92-000', 'Karachi');

-- UNIQUE violation (duplicate tracking number)
-- INSERT INTO shipments (tracking_no, customer_id, route_id, goods_desc, weight_kg, ship_date, freight_charge)
-- VALUES ('TMS-2026-0001', 1, 1, 'Test', 10, '2026-10-01', 100);

-- FOREIGN KEY violation (customer 999 does not exist)
-- INSERT INTO shipments (tracking_no, customer_id, route_id, goods_desc, weight_kg, ship_date, freight_charge)
-- VALUES ('TMS-X-1', 999, 1, 'Test', 10, '2026-10-01', 100);

-- CHECK violation (negative weight)
-- UPDATE shipments SET weight_kg = -5 WHERE shipment_id = 1;

-- ON DELETE RESTRICT (customer has shipments, cannot delete)
-- DELETE FROM customers WHERE customer_id = 1;


-- =====================================================================
-- PART K : DCL  (users & privileges)  - needs root/admin login
-- =====================================================================
-- CREATE USER 'tms_user'@'localhost' IDENTIFIED BY 'Tms@12345';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON transport_db.* TO 'tms_user'@'localhost';
-- REVOKE DELETE ON transport_db.* FROM 'tms_user'@'localhost';
-- FLUSH PRIVILEGES;
