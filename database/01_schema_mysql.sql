-- =====================================================================
--  TRANSPORT MANAGEMENT SYSTEM (TMS)  -  MySQL 8.x SCHEMA
--  Course     : RDBMS - Database Management Systems (PGD DSAI, Batch XIV)
--  Student    : Muhammad Adeel Siddiqi  (PGD/DSAI/Apr-26/312564)
--  Instructor : Sajid Majeed  |  NED University of Engineering & Technology
--
--  Run this file FIRST in MySQL Workbench (File > Open SQL Script > Execute ⚡)
--  It creates the database, 7 tables, all keys/constraints, indexes and a view.
-- =====================================================================

DROP DATABASE IF EXISTS transport_db;
CREATE DATABASE transport_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE transport_db;

-- ---------------------------------------------------------------------
-- 1. CUSTOMERS  (people / companies who book shipments)
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id   INT           NOT NULL AUTO_INCREMENT,
    full_name     VARCHAR(100)  NOT NULL,
    company       VARCHAR(100)  NULL,
    phone         VARCHAR(20)   NOT NULL,
    email         VARCHAR(100)  NULL,
    city          VARCHAR(50)   NOT NULL,
    address       VARCHAR(200)  NULL,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_customers        PRIMARY KEY (customer_id),
    CONSTRAINT uq_customers_phone  UNIQUE (phone),
    CONSTRAINT uq_customers_email  UNIQUE (email),
    CONSTRAINT chk_customers_email CHECK (email IS NULL OR email LIKE '%_@_%._%')
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 2. DRIVERS
-- ---------------------------------------------------------------------
CREATE TABLE drivers (
    driver_id      INT           NOT NULL AUTO_INCREMENT,
    full_name      VARCHAR(100)  NOT NULL,
    license_no     VARCHAR(30)   NOT NULL,
    phone          VARCHAR(20)   NOT NULL,
    license_expiry DATE          NOT NULL,
    experience_yrs INT           NOT NULL DEFAULT 0,
    status         VARCHAR(20)   NOT NULL DEFAULT 'Available',
    CONSTRAINT pk_drivers          PRIMARY KEY (driver_id),
    CONSTRAINT uq_drivers_license  UNIQUE (license_no),
    CONSTRAINT chk_drivers_exp     CHECK (experience_yrs BETWEEN 0 AND 50),
    CONSTRAINT chk_drivers_status  CHECK (status IN ('Available','On Trip','On Leave'))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 3. VEHICLES
-- ---------------------------------------------------------------------
CREATE TABLE vehicles (
    vehicle_id    INT           NOT NULL AUTO_INCREMENT,
    plate_no      VARCHAR(20)   NOT NULL,
    vehicle_type  VARCHAR(20)   NOT NULL,
    model         VARCHAR(50)   NOT NULL,
    make_year     INT           NOT NULL,
    capacity_kg   DECIMAL(10,2) NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_vehicles          PRIMARY KEY (vehicle_id),
    CONSTRAINT uq_vehicles_plate    UNIQUE (plate_no),
    CONSTRAINT chk_vehicles_type    CHECK (vehicle_type IN ('Truck','Mini Truck','Van','Pickup','Container','Trailer')),
    CONSTRAINT chk_vehicles_cap     CHECK (capacity_kg > 0),
    CONSTRAINT chk_vehicles_year    CHECK (make_year BETWEEN 1990 AND 2035),
    CONSTRAINT chk_vehicles_status  CHECK (status IN ('Active','In Maintenance','Retired'))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 4. ROUTES
-- ---------------------------------------------------------------------
CREATE TABLE routes (
    route_id      INT           NOT NULL AUTO_INCREMENT,
    origin        VARCHAR(50)   NOT NULL,
    destination   VARCHAR(50)   NOT NULL,
    distance_km   DECIMAL(8,2)  NOT NULL,
    est_hours     DECIMAL(5,2)  NOT NULL,
    rate_per_kg   DECIMAL(8,2)  NOT NULL,
    CONSTRAINT pk_routes            PRIMARY KEY (route_id),
    CONSTRAINT uq_routes_pair       UNIQUE (origin, destination),
    CONSTRAINT chk_routes_dist      CHECK (distance_km > 0),
    CONSTRAINT chk_routes_hours     CHECK (est_hours > 0),
    CONSTRAINT chk_routes_rate      CHECK (rate_per_kg >= 0),
    CONSTRAINT chk_routes_diff      CHECK (origin <> destination)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 5. SHIPMENTS  (central / transaction entity)
-- ---------------------------------------------------------------------
CREATE TABLE shipments (
    shipment_id    INT           NOT NULL AUTO_INCREMENT,
    tracking_no    VARCHAR(20)   NOT NULL,
    customer_id    INT           NOT NULL,
    route_id       INT           NOT NULL,
    vehicle_id     INT           NULL,
    driver_id      INT           NULL,
    goods_desc     VARCHAR(150)  NOT NULL,
    weight_kg      DECIMAL(10,2) NOT NULL,
    ship_date      DATE          NOT NULL,
    delivery_date  DATE          NULL,
    status         VARCHAR(20)   NOT NULL DEFAULT 'Booked',
    freight_charge DECIMAL(12,2) NOT NULL,
    CONSTRAINT pk_shipments          PRIMARY KEY (shipment_id),
    CONSTRAINT uq_shipments_tracking UNIQUE (tracking_no),
    CONSTRAINT fk_ship_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_ship_route    FOREIGN KEY (route_id)    REFERENCES routes(route_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_ship_vehicle  FOREIGN KEY (vehicle_id)  REFERENCES vehicles(vehicle_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_ship_driver   FOREIGN KEY (driver_id)   REFERENCES drivers(driver_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_ship_weight  CHECK (weight_kg > 0),
    CONSTRAINT chk_ship_charge  CHECK (freight_charge >= 0),
    CONSTRAINT chk_ship_status  CHECK (status IN ('Booked','In Transit','Delivered','Cancelled')),
    CONSTRAINT chk_ship_dates   CHECK (delivery_date IS NULL OR delivery_date >= ship_date)
) ENGINE = InnoDB;

CREATE INDEX idx_ship_status ON shipments(status);
CREATE INDEX idx_ship_date   ON shipments(ship_date);

-- ---------------------------------------------------------------------
-- 6. PAYMENTS  (one shipment -> many payments / installments)
-- ---------------------------------------------------------------------
CREATE TABLE payments (
    payment_id    INT           NOT NULL AUTO_INCREMENT,
    shipment_id   INT           NOT NULL,
    amount        DECIMAL(12,2) NOT NULL,
    method        VARCHAR(20)   NOT NULL,
    payment_date  DATE          NOT NULL,
    reference_no  VARCHAR(40)   NULL,
    CONSTRAINT pk_payments        PRIMARY KEY (payment_id),
    CONSTRAINT fk_pay_shipment    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_pay_amount     CHECK (amount > 0),
    CONSTRAINT chk_pay_method     CHECK (method IN ('Cash','Bank Transfer','Card','Cheque','Online'))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 7. MAINTENANCE  (vehicle service history)
-- ---------------------------------------------------------------------
CREATE TABLE maintenance (
    maint_id      INT           NOT NULL AUTO_INCREMENT,
    vehicle_id    INT           NOT NULL,
    service_date  DATE          NOT NULL,
    service_type  VARCHAR(30)   NOT NULL,
    description   VARCHAR(200)  NULL,
    cost          DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_maintenance     PRIMARY KEY (maint_id),
    CONSTRAINT fk_maint_vehicle   FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_maint_cost     CHECK (cost >= 0),
    CONSTRAINT chk_maint_type     CHECK (service_type IN ('Oil Change','Tyre','Engine','Brakes','General Service','Body Work'))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- VIEW : full shipment details (multi-table JOIN used by the web app)
-- ---------------------------------------------------------------------
CREATE VIEW v_shipment_details AS
SELECT  s.shipment_id,
        s.tracking_no,
        c.full_name      AS customer,
        c.phone          AS customer_phone,
        r.origin,
        r.destination,
        r.distance_km,
        v.plate_no       AS vehicle,
        d.full_name      AS driver,
        s.goods_desc,
        s.weight_kg,
        s.ship_date,
        s.delivery_date,
        s.status,
        s.freight_charge,
        COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.shipment_id = s.shipment_id), 0) AS amount_paid
FROM        shipments s
INNER JOIN  customers c ON c.customer_id = s.customer_id
INNER JOIN  routes    r ON r.route_id    = s.route_id
LEFT  JOIN  vehicles  v ON v.vehicle_id  = s.vehicle_id
LEFT  JOIN  drivers   d ON d.driver_id   = s.driver_id;
