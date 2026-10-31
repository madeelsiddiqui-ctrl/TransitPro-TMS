import subprocess
T = {
 "customers":[("customer_id","INT","PK"),("full_name","VARCHAR(100)",""),("company","VARCHAR(100)",""),("phone","VARCHAR(20)","UQ"),("email","VARCHAR(100)","UQ"),("city","VARCHAR(50)",""),("address","VARCHAR(200)",""),("created_at","TIMESTAMP","")],
 "routes":[("route_id","INT","PK"),("origin","VARCHAR(50)","UQ*"),("destination","VARCHAR(50)","UQ*"),("distance_km","DECIMAL(8,2)",""),("est_hours","DECIMAL(5,2)",""),("rate_per_kg","DECIMAL(8,2)","")],
 "shipments":[("shipment_id","INT","PK"),("tracking_no","VARCHAR(20)","UQ"),("customer_id","INT","FK"),("route_id","INT","FK"),("vehicle_id","INT","FK"),("driver_id","INT","FK"),("goods_desc","VARCHAR(150)",""),("weight_kg","DECIMAL(10,2)",""),("ship_date","DATE",""),("delivery_date","DATE",""),("status","VARCHAR(20)",""),("freight_charge","DECIMAL(12,2)","")],
 "vehicles":[("vehicle_id","INT","PK"),("plate_no","VARCHAR(20)","UQ"),("vehicle_type","VARCHAR(20)",""),("model","VARCHAR(50)",""),("make_year","INT",""),("capacity_kg","DECIMAL(10,2)",""),("status","VARCHAR(20)","")],
 "drivers":[("driver_id","INT","PK"),("full_name","VARCHAR(100)",""),("license_no","VARCHAR(30)","UQ"),("phone","VARCHAR(20)",""),("license_expiry","DATE",""),("experience_yrs","INT",""),("status","VARCHAR(20)","")],
 "payments":[("payment_id","INT","PK"),("shipment_id","INT","FK"),("amount","DECIMAL(12,2)",""),("method","VARCHAR(20)",""),("payment_date","DATE",""),("reference_no","VARCHAR(40)","")],
 "maintenance":[("maint_id","INT","PK"),("vehicle_id","INT","FK"),("service_date","DATE",""),("service_type","VARCHAR(30)",""),("description","VARCHAR(200)",""),("cost","DECIMAL(10,2)","")],
}
HEAD={"shipments":"#1d4ed8","payments":"#0f766e","maintenance":"#0f766e"}
def node(n,cols):
    h=HEAD.get(n,"#0b1b33")
    rows="".join(
      f'<tr><td align="left" port="{c}" bgcolor="{"#eef3ff" if k=="PK" else ("#e6f5f3" if k=="FK" else "white")}"><font face="Helvetica" point-size="10" color="{"#1d4ed8" if k=="PK" else ("#0f766e" if k=="FK" else "#0f1b2d")}">{"<b>"+c+"</b>" if k in("PK","FK") else c}</font></td>'
      f'<td align="left" bgcolor="{"#eef3ff" if k=="PK" else ("#e6f5f3" if k=="FK" else "white")}"><font face="Helvetica" point-size="9" color="#64748b">{t}</font></td>'
      f'<td port="{c}_r" bgcolor="{"#eef3ff" if k=="PK" else ("#e6f5f3" if k=="FK" else "white")}"><font face="Helvetica" point-size="9" color="#b45309">{"<b>"+k+"</b>" if k else " "}</font></td></tr>' for c,t,k in cols)
    return f'{n} [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5" color="#cbd3df"><tr><td colspan="3" bgcolor="{h}"><font face="Helvetica-Bold" color="white" point-size="12">{n.upper()}</font></td></tr>{rows}</table>>];'
E=[("customers","customer_id","shipments","customer_id","places"),
   ("routes","route_id","shipments","route_id","follows"),
   ("vehicles","vehicle_id","shipments","vehicle_id","carries"),
   ("drivers","driver_id","shipments","driver_id","drives"),
   ("shipments","shipment_id","payments","shipment_id","paid by"),
   ("vehicles","vehicle_id","maintenance","vehicle_id","serviced in")]
dot=['digraph ERD { graph [rankdir=LR, bgcolor="white", pad=0.4, nodesep=0.5, ranksep=1.1, label=<<font face="Helvetica-Bold" point-size="18">Transport Management System — Entity Relationship Diagram</font><br/><font face="Helvetica" point-size="11" color="#64748b">PK = Primary Key · FK = Foreign Key · UQ = Unique · crow\'s foot = many · Muhammad Adeel Siddiqi · PGD/DSAI/Apr-26/312564</font>>, labelloc=t]; node [shape=plaintext]; edge [color="#475569", penwidth=1.3, fontname="Helvetica", fontsize=10, fontcolor="#1d4ed8"];']
for n,c in T.items(): dot.append(node(n,c))
dot.append("{rank=same; customers; routes;} {rank=same; vehicles; drivers;}")
for a,ac,b,bc,lab in E:
    opt = b=="shipments" and ac in("vehicle_id","driver_id")
    dot.append(f'{a}:{ac}_r:e -> {b}:{bc}:w [arrowtail="{"teetee"}", arrowhead="{"crowodot" if opt else "crowtee"}", dir=both, label="{lab}\\n1 : N", taillabel="", headlabel=""];')
dot.append("}")
open("docs/erd.dot","w").write("\n".join(dot))
for fmt in("png","svg"):
    subprocess.run(["dot",f"-T{fmt}","-Gdpi=170","docs/erd.dot","-o",f"docs/ERD.{fmt}"],check=True)
