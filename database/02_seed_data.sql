-- =====================================================================
--  TRANSPORT MANAGEMENT SYSTEM - SAMPLE DATA (DML : INSERT)
--  Run SECOND in MySQL Workbench (after 01_schema_mysql.sql)
--  Amounts are in PKR. Same file is also used by the SQLite mode.
-- =====================================================================
USE transport_db;

-- ---------- CUSTOMERS ----------
INSERT INTO customers (customer_id, full_name, company, phone, email, city, address) VALUES
(1,  'Ahmed Raza',        'Raza Textiles Pvt Ltd',   '+92-300-1112233', 'ahmed@razatextiles.pk',  'Karachi',   'Plot 12, SITE Area'),
(2,  'Sana Malik',        'TechZone Electronics',    '+92-321-2223344', 'sana@techzone.pk',       'Karachi',   'Saddar, Electronics Market'),
(3,  'Bilal Khan',        'Khan Builders',           '+92-333-3334455', 'bilal@khanbuilders.pk',  'Hyderabad', 'Latifabad Unit 7'),
(4,  'Dr. Ayesha Noor',   'Noor Pharma',             '+92-345-4445566', 'ayesha@noorpharma.pk',   'Lahore',    'Gulberg III'),
(5,  'Usman Tariq',       'Tariq Rice Mills',        '+92-301-5556677', 'usman@tariqrice.pk',     'Karachi',   'Korangi Industrial Area'),
(6,  'Fahad Qureshi',     'Qureshi Auto Parts',      '+92-322-6667788', 'fahad@qautoparts.pk',    'Lahore',    'Badami Bagh'),
(7,  'Hina Javed',        NULL,                      '+92-334-7778899', 'hina.javed@gmail.com',   'Islamabad', 'F-10 Markaz'),
(8,  'Imran Siddiqui',    'Siddiqui Ceramics',       '+92-302-8889900', 'imran@sceramics.pk',     'Karachi',   'North Karachi Ind. Area'),
(9,  'Kamran Ali',        'Ali Steel Works',         '+92-311-9990011', 'kamran@alisteel.pk',     'Karachi',   'Port Qasim'),
(10, 'Zainab Hussain',    'Hussain Book Depot',      '+92-312-1012020', 'zainab@hbooks.pk',       'Lahore',    'Urdu Bazaar'),
(11, 'Omar Farooq',       'Farooq Traders',          '+92-313-2023030', 'omar@farooqtraders.pk',  'Multan',    'Hussain Agahi');

-- ---------- DRIVERS ----------
INSERT INTO drivers (driver_id, full_name, license_no, phone, license_expiry, experience_yrs, status) VALUES
(1, 'Muhammad Aslam',   'LTV-KHI-100231', '+92-300-9001001', '2028-05-14', 15, 'Available'),
(2, 'Ghulam Rasool',    'HTV-LHR-200452', '+92-300-9001002', '2027-08-30', 12, 'Available'),
(3, 'Abdul Sattar',     'HTV-KHI-300673', '+92-300-9001003', '2029-01-10', 20, 'On Trip'),
(4, 'Shahid Mehmood',   'LTV-ISB-400894', '+92-300-9001004', '2026-11-20',  8, 'On Trip'),
(5, 'Niaz Muhammad',    'HTV-QTA-501115', '+92-300-9001005', '2028-12-01', 18, 'Available'),
(6, 'Riaz Ahmed',       'HTV-PSH-601336', '+92-300-9001006', '2027-03-22', 10, 'Available'),
(7, 'Tariq Jamil',      'LTV-ISB-701557', '+92-300-9001007', '2028-07-07',  6, 'Available'),
(8, 'Saleem Akhtar',    'LTV-KHI-801778', '+92-300-9001008', '2027-10-15',  4, 'On Trip'),
(9, 'Waqas Hameed',     'HTV-MUL-901999', '+92-300-9001009', '2029-04-18',  9, 'On Leave');

-- ---------- VEHICLES ----------
INSERT INTO vehicles (vehicle_id, plate_no, vehicle_type, model, make_year, capacity_kg, status) VALUES
(1, 'KHI-TRK-1021', 'Truck',      'Hino 500 FG',      2021, 15000, 'Active'),
(2, 'LHR-TRK-2210', 'Truck',      'Isuzu FVR',        2020, 12000, 'Active'),
(3, 'KHI-TRL-3301', 'Trailer',    'Volvo FH16',       2019, 25000, 'Active'),
(4, 'ISB-VAN-4410', 'Van',        'Toyota HiAce',     2022,  1800, 'Active'),
(5, 'QTA-CON-5520', 'Container',  'Mercedes Actros',  2018, 30000, 'Active'),
(6, 'PSH-MTR-6610', 'Mini Truck', 'Hyundai Shehzore', 2023,  5000, 'Active'),
(7, 'ISB-PKP-7701', 'Pickup',     'Suzuki Ravi',      2022,  3000, 'Active'),
(8, 'KHI-VAN-8802', 'Van',        'Changan Karvaan',  2024,  1000, 'Active'),
(9, 'MUL-TRK-9901', 'Truck',      'Hino Ranger',      2017, 14000, 'In Maintenance');

-- ---------- ROUTES ----------
INSERT INTO routes (route_id, origin, destination, distance_km, est_hours, rate_per_kg) VALUES
(1, 'Karachi',   'Lahore',     1210, 18.0, 12.00),
(2, 'Karachi',   'Islamabad',  1410, 21.0, 14.00),
(3, 'Karachi',   'Hyderabad',   165,  3.0,  4.00),
(4, 'Lahore',    'Islamabad',   375,  5.0,  6.00),
(5, 'Karachi',   'Quetta',      690, 12.0, 10.00),
(6, 'Lahore',    'Peshawar',    510,  7.5,  8.00),
(7, 'Karachi',   'Multan',      900, 13.0, 11.00),
(8, 'Islamabad', 'Peshawar',    185,  2.5,  4.50);

-- ---------- SHIPMENTS ----------
INSERT INTO shipments (shipment_id, tracking_no, customer_id, route_id, vehicle_id, driver_id, goods_desc, weight_kg, ship_date, delivery_date, status, freight_charge) VALUES
(1,  'TMS-2026-0001', 1,  1, 1,    1,    'Textile rolls',        8000, '2026-09-02', '2026-09-04', 'Delivered',  96000),
(2,  'TMS-2026-0002', 2,  2, 2,    2,    'Consumer electronics', 3500, '2026-09-05', '2026-09-07', 'Delivered',  49000),
(3,  'TMS-2026-0003', 3,  3, 3,    3,    'Cement bags',         12000, '2026-09-08', '2026-09-08', 'Delivered',  48000),
(4,  'TMS-2026-0004', 4,  4, 4,    4,    'Pharmaceuticals',      1500, '2026-09-12', '2026-09-12', 'Delivered',   9000),
(5,  'TMS-2026-0005', 5,  5, 5,    5,    'Rice sacks',          10000, '2026-09-15', '2026-09-16', 'Delivered', 100000),
(6,  'TMS-2026-0006', 1,  7, 1,    1,    'Cotton bales',         9000, '2026-09-20', '2026-09-21', 'Delivered',  99000),
(7,  'TMS-2026-0007', 6,  6, 6,    6,    'Auto parts',           4000, '2026-09-25', '2026-09-26', 'Delivered',  32000),
(8,  'TMS-2026-0008', 7,  8, 7,    7,    'Household furniture',  2500, '2026-10-01', '2026-10-01', 'Delivered',  11250),
(9,  'TMS-2026-0009', 8,  1, 2,    2,    'Ceramic tiles',        7000, '2026-10-10', '2026-10-12', 'Delivered',  84000),
(10, 'TMS-2026-0010', 2,  2, 8,    8,    'Mobile phones',         800, '2026-10-18', NULL,         'In Transit', 11200),
(11, 'TMS-2026-0011', 9,  3, 3,    3,    'Steel rods',          11000, '2026-10-22', NULL,         'In Transit', 44000),
(12, 'TMS-2026-0012', 10, 4, 4,    4,    'Books & stationery',   1200, '2026-10-25', NULL,         'In Transit',  7200),
(13, 'TMS-2026-0013', 3,  5, NULL, NULL, 'Fertilizer',           9500, '2026-10-28', NULL,         'Booked',     95000),
(14, 'TMS-2026-0014', 4,  6, NULL, NULL, 'Medical equipment',    2000, '2026-10-29', NULL,         'Booked',     16000),
(15, 'TMS-2026-0015', 5,  7, NULL, NULL, 'Sugar bags',           6000, '2026-10-15', NULL,         'Cancelled',  66000);

-- ---------- PAYMENTS ----------
INSERT INTO payments (payment_id, shipment_id, amount, method, payment_date, reference_no) VALUES
(1,  1,  96000, 'Bank Transfer', '2026-09-04', 'HBL-TRX-88120'),
(2,  2,  25000, 'Cash',          '2026-09-05', NULL),
(3,  2,  24000, 'Bank Transfer', '2026-09-10', 'MCB-TRX-44211'),
(4,  3,  48000, 'Cheque',        '2026-09-09', 'CHQ-001245'),
(5,  4,   9000, 'Online',        '2026-09-12', 'JC-55120'),
(6,  5,  50000, 'Bank Transfer', '2026-09-16', 'UBL-TRX-90012'),
(7,  6,  99000, 'Bank Transfer', '2026-09-22', 'HBL-TRX-88901'),
(8,  7,  32000, 'Cash',          '2026-09-26', NULL),
(9,  8,  11250, 'Card',          '2026-10-01', 'POS-77612'),
(10, 9,  40000, 'Bank Transfer', '2026-10-12', 'MZN-TRX-12001'),
(11, 10, 11200, 'Online',        '2026-10-18', 'EP-99812'),
(12, 11, 20000, 'Cash',          '2026-10-22', NULL),
(13, 13, 30000, 'Bank Transfer', '2026-10-28', 'ABL-TRX-30331');

-- ---------- MAINTENANCE ----------
INSERT INTO maintenance (maint_id, vehicle_id, service_date, service_type, description, cost) VALUES
(1, 1, '2026-08-20', 'Oil Change',      'Engine oil + filter replaced',        18500),
(2, 3, '2026-08-25', 'Tyre',            'Two rear tyres replaced',             96000),
(3, 5, '2026-09-01', 'General Service', '50,000 km scheduled service',         45000),
(4, 2, '2026-09-18', 'Brakes',          'Brake pads and shoes replaced',       22000),
(5, 9, '2026-10-05', 'Engine',          'Engine overhaul - head gasket',      185000),
(6, 4, '2026-10-08', 'Oil Change',      'Synthetic oil change',                 9500),
(7, 6, '2026-10-14', 'Body Work',       'Rear door dent repair and paint',     27000),
(8, 1, '2026-10-26', 'Tyre',            'Wheel alignment and balancing',        6500);
