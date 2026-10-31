-- =====================================================================
--  TRANSPORT MANAGEMENT SYSTEM - SQLite version of the same schema
--  (used automatically when DB_ENGINE = "sqlite" — no installation needed)
--  Identical tables, keys and constraints as 01_schema_mysql.sql
-- =====================================================================
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     VARCHAR(100) NOT NULL,
    company       VARCHAR(100),
    phone         VARCHAR(20)  NOT NULL UNIQUE,
    email         VARCHAR(100) UNIQUE CHECK (email IS NULL OR email LIKE '%_@_%._%'),
    city          VARCHAR(50)  NOT NULL,
    address       VARCHAR(200),
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE drivers (
    driver_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      VARCHAR(100) NOT NULL,
    license_no     VARCHAR(30)  NOT NULL UNIQUE,
    phone          VARCHAR(20)  NOT NULL,
    license_expiry DATE         NOT NULL,
    experience_yrs INTEGER      NOT NULL DEFAULT 0 CHECK (experience_yrs BETWEEN 0 AND 50),
    status         VARCHAR(20)  NOT NULL DEFAULT 'Available'
                   CHECK (status IN ('Available','On Trip','On Leave'))
);

CREATE TABLE vehicles (
    vehicle_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_no      VARCHAR(20)   NOT NULL UNIQUE,
    vehicle_type  VARCHAR(20)   NOT NULL
                  CHECK (vehicle_type IN ('Truck','Mini Truck','Van','Pickup','Container','Trailer')),
    model         VARCHAR(50)   NOT NULL,
    make_year     INTEGER       NOT NULL CHECK (make_year BETWEEN 1990 AND 2035),
    capacity_kg   DECIMAL(10,2) NOT NULL CHECK (capacity_kg > 0),
    status        VARCHAR(20)   NOT NULL DEFAULT 'Active'
                  CHECK (status IN ('Active','In Maintenance','Retired'))
);

CREATE TABLE routes (
    route_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    origin        VARCHAR(50)  NOT NULL,
    destination   VARCHAR(50)  NOT NULL,
    distance_km   DECIMAL(8,2) NOT NULL CHECK (distance_km > 0),
    est_hours     DECIMAL(5,2) NOT NULL CHECK (est_hours > 0),
    rate_per_kg   DECIMAL(8,2) NOT NULL CHECK (rate_per_kg >= 0),
    UNIQUE (origin, destination),
    CHECK (origin <> destination)
);

CREATE TABLE shipments (
    shipment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_no    VARCHAR(20)   NOT NULL UNIQUE,
    customer_id    INTEGER       NOT NULL REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    route_id       INTEGER       NOT NULL REFERENCES routes(route_id)       ON UPDATE CASCADE ON DELETE RESTRICT,
    vehicle_id     INTEGER       REFERENCES vehicles(vehicle_id) ON UPDATE CASCADE ON DELETE SET NULL,
    driver_id      INTEGER       REFERENCES drivers(driver_id)   ON UPDATE CASCADE ON DELETE SET NULL,
    goods_desc     VARCHAR(150)  NOT NULL,
    weight_kg      DECIMAL(10,2) NOT NULL CHECK (weight_kg > 0),
    ship_date      DATE          NOT NULL,
    delivery_date  DATE,
    status         VARCHAR(20)   NOT NULL DEFAULT 'Booked'
                   CHECK (status IN ('Booked','In Transit','Delivered','Cancelled')),
    freight_charge DECIMAL(12,2) NOT NULL CHECK (freight_charge >= 0),
    CHECK (delivery_date IS NULL OR delivery_date >= ship_date)
);
CREATE INDEX idx_ship_status ON shipments(status);
CREATE INDEX idx_ship_date   ON shipments(ship_date);

CREATE TABLE payments (
    payment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id   INTEGER       NOT NULL REFERENCES shipments(shipment_id) ON UPDATE CASCADE ON DELETE CASCADE,
    amount        DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    method        VARCHAR(20)   NOT NULL CHECK (method IN ('Cash','Bank Transfer','Card','Cheque','Online')),
    payment_date  DATE          NOT NULL,
    reference_no  VARCHAR(40)
);

CREATE TABLE maintenance (
    maint_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id    INTEGER       NOT NULL REFERENCES vehicles(vehicle_id) ON UPDATE CASCADE ON DELETE CASCADE,
    service_date  DATE          NOT NULL,
    service_type  VARCHAR(30)   NOT NULL
                  CHECK (service_type IN ('Oil Change','Tyre','Engine','Brakes','General Service','Body Work')),
    description   VARCHAR(200),
    cost          DECIMAL(10,2) NOT NULL CHECK (cost >= 0)
);

CREATE VIEW v_shipment_details AS
SELECT  s.shipment_id, s.tracking_no,
        c.full_name AS customer, c.phone AS customer_phone,
        r.origin, r.destination, r.distance_km,
        v.plate_no  AS vehicle, d.full_name AS driver,
        s.goods_desc, s.weight_kg, s.ship_date, s.delivery_date,
        s.status, s.freight_charge,
        COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.shipment_id = s.shipment_id), 0) AS amount_paid
FROM        shipments s
INNER JOIN  customers c ON c.customer_id = s.customer_id
INNER JOIN  routes    r ON r.route_id    = s.route_id
LEFT  JOIN  vehicles  v ON v.vehicle_id  = s.vehicle_id
LEFT  JOIN  drivers   d ON d.driver_id   = s.driver_id;
