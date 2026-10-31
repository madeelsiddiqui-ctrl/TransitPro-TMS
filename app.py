"""
Transport Management System (TMS) - Flask web application
PGD DSAI (Batch XIV) - RDBMS Project | NED University of Engineering & Technology
Student: Muhammad Adeel Siddiqi  (PGD/DSAI/Apr-26/312564)

Run:   double-click START_HERE.bat   (or: python app.py)  ->  http://127.0.0.1:5000
"""
import re
from datetime import date

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   url_for)

import config
import db

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ===========================================================================
#  ENTITY DEFINITIONS  (one entry per table in the ERD)
#  Each entry describes the table, its primary key, the form fields and the
#  SELECT (often a JOIN) used to list the records.
# ===========================================================================
ENTITIES = {
    "customers": {
        "title": "Customers", "singular": "Customer", "icon": "users",
        "pk": "customer_id",
        "list_sql": "SELECT customer_id, full_name, company, phone, email, city FROM customers",
        "columns": [("customer_id", "ID"), ("full_name", "Name"), ("company", "Company"),
                    ("phone", "Phone"), ("email", "Email"), ("city", "City")],
        "search": ["full_name", "company", "phone", "email", "city"],
        "order": "customer_id DESC",
        "fields": [
            {"name": "full_name", "label": "Full Name", "required": True},
            {"name": "company", "label": "Company"},
            {"name": "phone", "label": "Phone", "type": "tel", "required": True, "help": "Must be unique"},
            {"name": "email", "label": "Email", "type": "email", "help": "Must be unique"},
            {"name": "city", "label": "City", "required": True},
            {"name": "address", "label": "Address", "type": "textarea", "wide": True},
        ],
    },
    "drivers": {
        "title": "Drivers", "singular": "Driver", "icon": "id",
        "pk": "driver_id",
        "list_sql": "SELECT driver_id, full_name, license_no, phone, license_expiry, experience_yrs, status FROM drivers",
        "columns": [("driver_id", "ID"), ("full_name", "Name"), ("license_no", "License No"),
                    ("phone", "Phone"), ("license_expiry", "License Expiry"),
                    ("experience_yrs", "Exp. (yrs)"), ("status", "Status")],
        "search": ["full_name", "license_no", "phone", "status"],
        "order": "driver_id DESC",
        "fields": [
            {"name": "full_name", "label": "Full Name", "required": True},
            {"name": "license_no", "label": "License No", "required": True, "help": "Must be unique"},
            {"name": "phone", "label": "Phone", "type": "tel", "required": True},
            {"name": "license_expiry", "label": "License Expiry", "type": "date", "required": True},
            {"name": "experience_yrs", "label": "Experience (years)", "type": "number", "min": 0, "max": 50, "required": True},
            {"name": "status", "label": "Status", "type": "select", "required": True,
             "options": ["Available", "On Trip", "On Leave"]},
        ],
    },
    "vehicles": {
        "title": "Vehicles", "singular": "Vehicle", "icon": "truck",
        "pk": "vehicle_id",
        "list_sql": "SELECT vehicle_id, plate_no, vehicle_type, model, make_year, capacity_kg, status FROM vehicles",
        "columns": [("vehicle_id", "ID"), ("plate_no", "Plate No"), ("vehicle_type", "Type"),
                    ("model", "Model"), ("make_year", "Year"), ("capacity_kg", "Capacity (kg)"),
                    ("status", "Status")],
        "search": ["plate_no", "vehicle_type", "model", "status"],
        "order": "vehicle_id DESC",
        "fields": [
            {"name": "plate_no", "label": "Plate No", "required": True, "help": "Must be unique"},
            {"name": "vehicle_type", "label": "Vehicle Type", "type": "select", "required": True,
             "options": ["Truck", "Mini Truck", "Van", "Pickup", "Container", "Trailer"]},
            {"name": "model", "label": "Model", "required": True},
            {"name": "make_year", "label": "Make Year", "type": "number", "min": 1990, "max": 2035, "required": True},
            {"name": "capacity_kg", "label": "Capacity (kg)", "type": "number", "step": "0.01", "min": 1, "required": True},
            {"name": "status", "label": "Status", "type": "select", "required": True,
             "options": ["Active", "In Maintenance", "Retired"]},
        ],
    },
    "routes": {
        "title": "Routes", "singular": "Route", "icon": "route",
        "pk": "route_id",
        "list_sql": "SELECT route_id, origin, destination, distance_km, est_hours, rate_per_kg FROM routes",
        "columns": [("route_id", "ID"), ("origin", "Origin"), ("destination", "Destination"),
                    ("distance_km", "Distance (km)"), ("est_hours", "Est. Hours"),
                    ("rate_per_kg", "Rate / kg")],
        "search": ["origin", "destination"],
        "order": "route_id",
        "fields": [
            {"name": "origin", "label": "Origin City", "required": True},
            {"name": "destination", "label": "Destination City", "required": True,
             "help": "Must differ from origin (CHECK)"},
            {"name": "distance_km", "label": "Distance (km)", "type": "number", "step": "0.01", "min": 1, "required": True},
            {"name": "est_hours", "label": "Estimated Hours", "type": "number", "step": "0.1", "min": 0.1, "required": True},
            {"name": "rate_per_kg", "label": "Rate per kg (PKR)", "type": "number", "step": "0.01", "min": 0, "required": True},
        ],
    },
    "shipments": {
        "title": "Shipments", "singular": "Shipment", "icon": "box",
        "pk": "shipment_id",
        # JOIN of 5 tables through the view v_shipment_details
        "list_sql": ("SELECT shipment_id, tracking_no, customer, origin, destination, vehicle, driver, "
                     "weight_kg, ship_date, status, freight_charge, amount_paid FROM v_shipment_details"),
        "columns": [("tracking_no", "Tracking No"), ("customer", "Customer"), ("origin", "From"),
                    ("destination", "To"), ("vehicle", "Vehicle"), ("driver", "Driver"),
                    ("weight_kg", "Weight (kg)"), ("ship_date", "Ship Date"), ("status", "Status"),
                    ("freight_charge", "Charge"), ("amount_paid", "Paid")],
        "search": ["tracking_no", "customer", "origin", "destination", "vehicle", "driver", "status"],
        "filters": {"status": ["Booked", "In Transit", "Delivered", "Cancelled"]},
        "order": "shipment_id DESC",
        "detail": True,
        "fields": [
            {"name": "tracking_no", "label": "Tracking No", "required": True, "help": "Unique. Auto-suggested."},
            {"name": "customer_id", "label": "Customer", "type": "fk", "required": True,
             "fk": ("customers", "customer_id", ["full_name", "city"])},
            {"name": "route_id", "label": "Route", "type": "fk", "required": True,
             "fk": ("routes", "route_id", ["origin", "destination"]), "sep": " → "},
            {"name": "vehicle_id", "label": "Vehicle", "type": "fk",
             "fk": ("vehicles", "vehicle_id", ["plate_no", "vehicle_type"])},
            {"name": "driver_id", "label": "Driver", "type": "fk",
             "fk": ("drivers", "driver_id", ["full_name", "status"])},
            {"name": "goods_desc", "label": "Goods Description", "required": True},
            {"name": "weight_kg", "label": "Weight (kg)", "type": "number", "step": "0.01", "min": 0.01, "required": True},
            {"name": "ship_date", "label": "Ship Date", "type": "date", "required": True},
            {"name": "delivery_date", "label": "Delivery Date", "type": "date", "help": "Must be on/after ship date"},
            {"name": "status", "label": "Status", "type": "select", "required": True,
             "options": ["Booked", "In Transit", "Delivered", "Cancelled"]},
            {"name": "freight_charge", "label": "Freight Charge (PKR)", "type": "number", "step": "0.01", "min": 0,
             "required": True, "help": "Leave 0 to auto-calculate: weight × route rate"},
        ],
    },
    "payments": {
        "title": "Payments", "singular": "Payment", "icon": "card",
        "pk": "payment_id",
        "list_sql": ("SELECT p.payment_id, s.tracking_no, c.full_name AS customer, p.amount, p.method, "
                     "p.payment_date, p.reference_no FROM payments p "
                     "INNER JOIN shipments s ON s.shipment_id = p.shipment_id "
                     "INNER JOIN customers c ON c.customer_id = s.customer_id"),
        "columns": [("payment_id", "ID"), ("tracking_no", "Shipment"), ("customer", "Customer"),
                    ("amount", "Amount"), ("method", "Method"), ("payment_date", "Date"),
                    ("reference_no", "Reference")],
        "search": ["tracking_no", "customer", "method", "reference_no"],
        "order": "payment_id DESC",
        "fields": [
            {"name": "shipment_id", "label": "Shipment", "type": "fk", "required": True,
             "fk": ("shipments", "shipment_id", ["tracking_no", "goods_desc"])},
            {"name": "amount", "label": "Amount (PKR)", "type": "number", "step": "0.01", "min": 0.01, "required": True},
            {"name": "method", "label": "Method", "type": "select", "required": True,
             "options": ["Cash", "Bank Transfer", "Card", "Cheque", "Online"]},
            {"name": "payment_date", "label": "Payment Date", "type": "date", "required": True},
            {"name": "reference_no", "label": "Reference No"},
        ],
    },
    "maintenance": {
        "title": "Maintenance", "singular": "Maintenance Record", "icon": "wrench",
        "pk": "maint_id",
        "list_sql": ("SELECT m.maint_id, v.plate_no, v.model, m.service_date, m.service_type, "
                     "m.description, m.cost FROM maintenance m "
                     "INNER JOIN vehicles v ON v.vehicle_id = m.vehicle_id"),
        "columns": [("maint_id", "ID"), ("plate_no", "Vehicle"), ("model", "Model"),
                    ("service_date", "Date"), ("service_type", "Service"),
                    ("description", "Description"), ("cost", "Cost")],
        "search": ["plate_no", "model", "service_type", "description"],
        "order": "maint_id DESC",
        "fields": [
            {"name": "vehicle_id", "label": "Vehicle", "type": "fk", "required": True,
             "fk": ("vehicles", "vehicle_id", ["plate_no", "model"])},
            {"name": "service_date", "label": "Service Date", "type": "date", "required": True},
            {"name": "service_type", "label": "Service Type", "type": "select", "required": True,
             "options": ["Oil Change", "Tyre", "Engine", "Brakes", "General Service", "Body Work"]},
            {"name": "description", "label": "Description", "type": "textarea", "wide": True},
            {"name": "cost", "label": "Cost (PKR)", "type": "number", "step": "0.01", "min": 0, "required": True},
        ],
    },
}

MONEY_COLS = {"freight_charge", "amount_paid", "amount", "cost", "rate_per_kg", "revenue", "balance",
              "total_revenue", "total_business", "total_cost", "paid"}

# ===========================================================================
#  REPORTS  - pre-written SQL that demonstrates JOINs, GROUP BY, sub-queries
# ===========================================================================
REPORTS = [
    {
        "key": "inner-join",
        "title": "INNER JOIN – Shipments with customer, route, vehicle & driver",
        "concept": "INNER JOIN (5 tables)",
        "sql": """SELECT s.tracking_no, c.full_name AS customer, r.origin, r.destination,
       v.plate_no AS vehicle, d.full_name AS driver, s.status
FROM shipments s
INNER JOIN customers c ON s.customer_id = c.customer_id
INNER JOIN routes    r ON s.route_id    = r.route_id
INNER JOIN vehicles  v ON s.vehicle_id  = v.vehicle_id
INNER JOIN drivers   d ON s.driver_id   = d.driver_id
ORDER BY s.ship_date DESC""",
    },
    {
        "key": "left-join",
        "title": "LEFT JOIN – All customers and their number of shipments (incl. zero)",
        "concept": "LEFT JOIN + COUNT + GROUP BY",
        "sql": """SELECT c.full_name, c.city, COUNT(s.shipment_id) AS total_shipments,
       COALESCE(SUM(s.freight_charge), 0) AS total_business
FROM customers c
LEFT JOIN shipments s ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.city
ORDER BY total_business DESC""",
    },
    {
        "key": "route-revenue",
        "title": "Revenue by route",
        "concept": "JOIN + SUM / AVG + GROUP BY",
        "sql": """SELECT r.origin, r.destination, COUNT(*) AS shipments,
       SUM(s.weight_kg) AS total_weight_kg, SUM(s.freight_charge) AS total_revenue
FROM shipments s
INNER JOIN routes r ON r.route_id = s.route_id
WHERE s.status <> 'Cancelled'
GROUP BY r.route_id, r.origin, r.destination
ORDER BY total_revenue DESC""",
    },
    {
        "key": "having",
        "title": "Top customers – business above PKR 100,000",
        "concept": "GROUP BY + HAVING",
        "sql": """SELECT c.full_name, c.company, SUM(s.freight_charge) AS total_business
FROM customers c
INNER JOIN shipments s ON s.customer_id = c.customer_id
WHERE s.status <> 'Cancelled'
GROUP BY c.customer_id, c.full_name, c.company
HAVING SUM(s.freight_charge) > 100000
ORDER BY total_business DESC""",
    },
    {
        "key": "outstanding",
        "title": "Outstanding balances (unpaid freight)",
        "concept": "Correlated sub-query",
        "sql": """SELECT s.tracking_no, c.full_name AS customer, s.status, s.freight_charge,
       (SELECT COALESCE(SUM(p.amount), 0) FROM payments p
         WHERE p.shipment_id = s.shipment_id) AS paid,
       s.freight_charge - (SELECT COALESCE(SUM(p.amount), 0) FROM payments p
         WHERE p.shipment_id = s.shipment_id) AS balance
FROM shipments s
INNER JOIN customers c ON c.customer_id = s.customer_id
WHERE s.status <> 'Cancelled'
  AND s.freight_charge > (SELECT COALESCE(SUM(p.amount), 0) FROM payments p
                           WHERE p.shipment_id = s.shipment_id)
ORDER BY balance DESC""",
    },
    {
        "key": "idle-drivers",
        "title": "Drivers never assigned to any shipment",
        "concept": "Sub-query with NOT IN",
        "sql": """SELECT driver_id, full_name, license_no, status
FROM drivers
WHERE driver_id NOT IN (SELECT driver_id FROM shipments WHERE driver_id IS NOT NULL)""",
    },
    {
        "key": "vehicle-util",
        "title": "Vehicle utilisation and maintenance cost",
        "concept": "LEFT JOIN + sub-queries + aggregates",
        "sql": """SELECT v.plate_no, v.vehicle_type, v.capacity_kg, v.status,
       (SELECT COUNT(*) FROM shipments s
         WHERE s.vehicle_id = v.vehicle_id AND s.status <> 'Cancelled') AS trips,
       (SELECT COALESCE(SUM(m.cost), 0) FROM maintenance m
         WHERE m.vehicle_id = v.vehicle_id) AS total_cost
FROM vehicles v
ORDER BY trips DESC""",
    },
    {
        "key": "heavy",
        "title": "Shipments heavier than the average weight",
        "concept": "Sub-query with AVG",
        "sql": """SELECT tracking_no, goods_desc, weight_kg, status
FROM shipments
WHERE weight_kg > (SELECT AVG(weight_kg) FROM shipments)
ORDER BY weight_kg DESC""",
    },
    {
        "key": "self-join",
        "title": "Connecting routes (two-leg journeys)",
        "concept": "SELF JOIN",
        "sql": """SELECT r1.origin, r1.destination AS via, r2.destination AS final_destination,
       r1.distance_km + r2.distance_km AS total_km
FROM routes r1
INNER JOIN routes r2 ON r1.destination = r2.origin""",
    },
]


# ===========================================================================
#  request lifecycle / helpers
# ===========================================================================
def get_db():
    if "conn" not in g:
        g.conn = db.connect()
    return g.conn


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()


@app.context_processor
def inject_globals():
    return {"P": config.PROJECT, "ENTITIES": ENTITIES, "ENGINE": db.ACTIVE_ENGINE,
            "MONEY_COLS": MONEY_COLS, "today": date.today().isoformat()}


@app.template_filter("money")
def money(v):
    if v is None or v == "":
        return "—"
    try:
        return f"{float(v):,.0f}"
    except (TypeError, ValueError):
        return v


@app.template_filter("num")
def num(v):
    if v is None or v == "":
        return "—"
    try:
        f = float(v)
        return f"{f:,.0f}" if f.is_integer() else f"{f:,.2f}"
    except (TypeError, ValueError):
        return v


def entity_or_404(name):
    ent = ENTITIES.get(name)
    if not ent:
        abort(404)
    return ent


def fk_options(conn, field):
    table, pk, label_cols = field["fk"]
    rows = db.query(conn, f"SELECT {pk}, {', '.join(label_cols)} FROM {table} ORDER BY {pk}")
    sep = field.get("sep", " — ")
    return [(r[pk], f"#{r[pk]}  " + sep.join(str(r[c]) for c in label_cols if r[c] is not None))
            for r in rows]


def form_values(ent):
    """Read the submitted form; empty optional fields become NULL."""
    values = {}
    for f in ent["fields"]:
        v = request.form.get(f["name"], "").strip()
        values[f["name"]] = v if v != "" else None
    return values


def validate(ent, values):
    errors = []
    for f in ent["fields"]:
        if f.get("required") and values[f["name"]] is None:
            errors.append(f"{f['label']} is required.")
    return errors


def next_tracking_no(conn):
    row = db.query_one(conn, "SELECT MAX(shipment_id) AS m FROM shipments")
    n = (row["m"] or 0) + 1
    return f"TMS-{date.today().year}-{n:04d}"


def apply_business_rules(conn, name, values):
    """Small business logic layer for shipments."""
    if name != "shipments":
        return
    # auto-calculate freight = weight x route rate when left as 0
    try:
        charge = float(values.get("freight_charge") or 0)
    except ValueError:
        charge = 0
    if charge == 0 and values.get("route_id") and values.get("weight_kg"):
        r = db.query_one(conn, "SELECT rate_per_kg FROM routes WHERE route_id = %s", (values["route_id"],))
        if r:
            values["freight_charge"] = round(float(values["weight_kg"]) * float(r["rate_per_kg"]), 2)
    # delivered without a date -> today
    if values.get("status") == "Delivered" and not values.get("delivery_date"):
        values["delivery_date"] = date.today().isoformat()


# ===========================================================================
#  DASHBOARD
# ===========================================================================
@app.route("/")
def dashboard():
    conn = get_db()
    counts = {k: db.query_one(conn, f"SELECT COUNT(*) AS n FROM {k}")["n"] for k in ENTITIES}
    revenue = db.query_one(conn, "SELECT COALESCE(SUM(freight_charge),0) AS v FROM shipments WHERE status <> 'Cancelled'")["v"]
    received = db.query_one(conn, "SELECT COALESCE(SUM(amount),0) AS v FROM payments")["v"]
    by_status = db.query(conn, "SELECT status, COUNT(*) AS n FROM shipments GROUP BY status ORDER BY n DESC")
    top_routes = db.query(conn, """
        SELECT r.origin, r.destination, COUNT(*) AS n, SUM(s.freight_charge) AS revenue
        FROM shipments s INNER JOIN routes r ON r.route_id = s.route_id
        WHERE s.status <> 'Cancelled'
        GROUP BY r.route_id, r.origin, r.destination
        ORDER BY revenue DESC LIMIT 5""")
    recent = db.query(conn, "SELECT * FROM v_shipment_details ORDER BY ship_date DESC, shipment_id DESC LIMIT 6")
    fleet = db.query(conn, "SELECT status, COUNT(*) AS n FROM vehicles GROUP BY status")
    drivers = db.query(conn, "SELECT status, COUNT(*) AS n FROM drivers GROUP BY status")
    max_status = max([r["n"] for r in by_status] or [1])
    max_route = max([float(r["revenue"] or 0) for r in top_routes] or [1])
    return render_template("dashboard.html", counts=counts, revenue=revenue, received=received,
                           outstanding=float(revenue) - float(received), by_status=by_status,
                           top_routes=top_routes, recent=recent, fleet=fleet, drivers=drivers,
                           max_status=max_status, max_route=max_route)


# ===========================================================================
#  GENERIC CRUD  (works for every table in ENTITIES)
# ===========================================================================
@app.route("/<name>/")
def list_records(name):
    ent = entity_or_404(name)
    conn = get_db()
    q = request.args.get("q", "").strip()
    where, params = [], []
    if q:
        where.append("(" + " OR ".join(f"{c} LIKE %s" for c in ent["search"]) + ")")
        params += [f"%{q}%"] * len(ent["search"])
    for col, allowed in ent.get("filters", {}).items():
        val = request.args.get(col, "")
        if val in allowed:
            where.append(f"{col} = %s")
            params.append(val)
    statement = f"SELECT * FROM ({ent['list_sql']}) AS t"
    if where:
        statement += " WHERE " + " AND ".join(where)
    statement += f" ORDER BY {ent['order']}"
    rows = db.query(conn, statement, params)
    shown_sql = statement
    for p in params:
        shown_sql = shown_sql.replace("%s", f"'{p}'", 1)
    return render_template("list.html", name=name, ent=ent, rows=rows, q=q, sql=shown_sql)


@app.route("/<name>/new", methods=["GET", "POST"])
def create_record(name):
    ent = entity_or_404(name)
    conn = get_db()
    values = {f["name"]: None for f in ent["fields"]}
    if name == "shipments":
        values.update(tracking_no=next_tracking_no(conn), ship_date=date.today().isoformat(),
                      status="Booked", freight_charge="0")
    if name in ("payments",):
        values["payment_date"] = date.today().isoformat()
    if name == "maintenance":
        values["service_date"] = date.today().isoformat()
    if request.args.get("shipment_id"):
        values["shipment_id"] = request.args["shipment_id"]

    if request.method == "POST":
        values = form_values(ent)
        errors = validate(ent, values)
        if not errors:
            apply_business_rules(conn, name, values)
            cols = list(values.keys())
            statement = (f"INSERT INTO {name} ({', '.join(cols)}) "
                         f"VALUES ({', '.join(['%s'] * len(cols))})")
            try:
                new_id, _ = db.execute(conn, statement, [values[c] for c in cols])
                flash(f"{ent['singular']} #{new_id} created successfully.", "success")
                flash(f"INSERT INTO {name} ({', '.join(cols)}) VALUES (...)", "sql")
                if name == "shipments":
                    return redirect(url_for("shipment_detail", rid=new_id))
                return redirect(url_for("list_records", name=name))
            except db.DB_ERRORS as e:
                errors.append(db.friendly_error(e))
        for err in errors:
            flash(err, "error")
    options = {f["name"]: fk_options(conn, f) for f in ent["fields"] if f.get("type") == "fk"}
    return render_template("form.html", name=name, ent=ent, values=values, options=options, mode="new")


@app.route("/<name>/<int:rid>/edit", methods=["GET", "POST"])
def edit_record(name, rid):
    ent = entity_or_404(name)
    conn = get_db()
    record = db.query_one(conn, f"SELECT * FROM {name} WHERE {ent['pk']} = %s", (rid,))
    if not record:
        abort(404)
    values = {f["name"]: record[f["name"]] for f in ent["fields"]}
    if request.method == "POST":
        values = form_values(ent)
        errors = validate(ent, values)
        if not errors:
            apply_business_rules(conn, name, values)
            cols = list(values.keys())
            statement = (f"UPDATE {name} SET {', '.join(c + ' = %s' for c in cols)} "
                         f"WHERE {ent['pk']} = %s")
            try:
                db.execute(conn, statement, [values[c] for c in cols] + [rid])
                flash(f"{ent['singular']} #{rid} updated successfully.", "success")
                flash(f"UPDATE {name} SET ... WHERE {ent['pk']} = {rid}", "sql")
                if name == "shipments":
                    return redirect(url_for("shipment_detail", rid=rid))
                return redirect(url_for("list_records", name=name))
            except db.DB_ERRORS as e:
                errors.append(db.friendly_error(e))
        for err in errors:
            flash(err, "error")
    options = {f["name"]: fk_options(conn, f) for f in ent["fields"] if f.get("type") == "fk"}
    return render_template("form.html", name=name, ent=ent, values=values, options=options,
                           mode="edit", rid=rid)


@app.route("/<name>/<int:rid>/delete", methods=["POST"])
def delete_record(name, rid):
    ent = entity_or_404(name)
    conn = get_db()
    try:
        _, count = db.execute(conn, f"DELETE FROM {name} WHERE {ent['pk']} = %s", (rid,))
        if count:
            flash(f"{ent['singular']} #{rid} deleted.", "success")
            flash(f"DELETE FROM {name} WHERE {ent['pk']} = {rid}", "sql")
        else:
            flash("Record not found.", "error")
    except db.DB_ERRORS as e:
        msg = db.friendly_error(e)
        if "foreign key" in msg.lower():
            msg = (f"Cannot delete {ent['singular'].lower()} #{rid}: it is still referenced by other "
                   f"records (FOREIGN KEY ... ON DELETE RESTRICT). Delete or re-assign those records first.")
        flash(msg, "error")
    return redirect(url_for("list_records", name=name))


# ===========================================================================
#  SHIPMENT DETAIL + TRACKING
# ===========================================================================
@app.route("/shipments/<int:rid>")
def shipment_detail(rid):
    conn = get_db()
    s = db.query_one(conn, """
        SELECT s.*, c.full_name AS customer, c.company, c.phone AS customer_phone, c.email AS customer_email,
               c.city AS customer_city, r.origin, r.destination, r.distance_km, r.est_hours, r.rate_per_kg,
               v.plate_no, v.vehicle_type, v.model, v.capacity_kg,
               d.full_name AS driver, d.phone AS driver_phone, d.license_no
        FROM shipments s
        INNER JOIN customers c ON c.customer_id = s.customer_id
        INNER JOIN routes    r ON r.route_id    = s.route_id
        LEFT  JOIN vehicles  v ON v.vehicle_id  = s.vehicle_id
        LEFT  JOIN drivers   d ON d.driver_id   = s.driver_id
        WHERE s.shipment_id = %s""", (rid,))
    if not s:
        abort(404)
    payments = db.query(conn, "SELECT * FROM payments WHERE shipment_id = %s ORDER BY payment_date", (rid,))
    paid = sum(float(p["amount"]) for p in payments)
    over_capacity = s["capacity_kg"] is not None and float(s["weight_kg"]) > float(s["capacity_kg"])
    return render_template("shipment.html", s=s, payments=payments, paid=paid,
                           balance=float(s["freight_charge"]) - paid, over_capacity=over_capacity)


@app.route("/track")
def track():
    tn = request.args.get("tracking_no", "").strip()
    if tn:
        row = db.query_one(get_db(), "SELECT shipment_id FROM shipments WHERE tracking_no = %s", (tn,))
        if row:
            return redirect(url_for("shipment_detail", rid=row["shipment_id"]))
        flash(f"No shipment found with tracking number '{tn}'.", "error")
    return render_template("track.html", tn=tn)


# ===========================================================================
#  REPORTS + SQL CONSOLE + ABOUT
# ===========================================================================
@app.route("/reports")
def reports():
    key = request.args.get("r", REPORTS[0]["key"])
    rep = next((r for r in REPORTS if r["key"] == key), REPORTS[0])
    cols, rows = db.raw_select(get_db(), rep["sql"])
    return render_template("reports.html", reports=REPORTS, rep=rep, cols=cols, rows=rows)


READ_ONLY = re.compile(r"^\s*(select|with|show|describe|desc|explain|pragma\s+table_info)\b", re.I)


@app.route("/console", methods=["GET", "POST"])
def console():
    statement = request.form.get("sql", "SELECT * FROM v_shipment_details LIMIT 10").strip()
    cols, rows, error = [], [], None
    if request.method == "POST":
        if ";" in statement.rstrip(";"):
            error = "Please run one statement at a time."
        elif not READ_ONLY.match(statement):
            error = ("The web console is READ-ONLY (SELECT / SHOW / DESCRIBE). "
                     "Use the forms for INSERT, UPDATE and DELETE, or MySQL Workbench.")
        else:
            try:
                cols, rows = db.raw_select(get_db(), statement.rstrip(";"))
            except Exception as e:  # noqa: BLE001
                error = str(e)
    return render_template("console.html", statement=statement, cols=cols, rows=rows, error=error)


@app.route("/about")
def about():
    conn = get_db()
    tables = []
    for k, ent in ENTITIES.items():
        tables.append({"name": k, "title": ent["title"], "pk": ent["pk"],
                       "rows": db.query_one(conn, f"SELECT COUNT(*) AS n FROM {k}")["n"],
                       "fks": [f["name"] for f in ent["fields"] if f.get("type") == "fk"]})
    return render_template("about.html", tables=tables)


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", code=404, message="Page or record not found."), 404


# ===========================================================================
if __name__ == "__main__":
    import sys
    if "--init-mysql" in sys.argv:
        db.init_mysql()
        print("[TMS] MySQL database 'transport_db' created with sample data.")
        sys.exit(0)
    if "--reset-sqlite" in sys.argv:
        db.init_sqlite(force=True)
        print("[TMS] SQLite database recreated.")
    db.choose_engine()
    import logging
    import flask.cli
    logging.getLogger("werkzeug").setLevel(logging.ERROR)   # keep the window clean
    flask.cli.show_server_banner = lambda *a, **k: None
    print("\n   App running at  http://127.0.0.1:5000   (keep this window open)\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
else:
    db.choose_engine()   # when run by a WSGI server (PythonAnywhere / Render / gunicorn)
