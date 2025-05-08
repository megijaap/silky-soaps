from flask import Flask, render_template
from flask import Flask, render_template, request, redirect
app = Flask(__name__)
import sqlite3
from pathlib import Path
def get_db_connection():
    """
    Izveido un atgriež savienojumu ar SQLite datubāzi.
    """
    # Atrod ceļu uz datubāzes failu (tas atrodas tajā pašā mapē, kur šis fails)
    db = Path(__file__).parent / "ziepessmu.db"
    # Izveido savienojumu ar SQLite datubāzi
    conn = sqlite3.connect(db)
    # Nodrošina, ka rezultāti būs pieejami kā vārdnīcas (piemēram: product["name"])
    conn.row_factory = sqlite3.Row
    # Atgriež savienojumu
    return conn
@app.route("/produkti")
def products():
    conn = get_db_connection() # Pieslēdzas datubāzei
    # Izpilda SQL vaicājumu, kas atlasa visus produktus
    products = conn.execute("SELECT * FROM Produkts").fetchall()
    conn.close() # Aizver savienojumu ar datubāzi
    # Atgriežam HTML veidni "products.html", padodot produktus veidnei
    return render_template("products.html", products=products)

@app.route("/produkti/<int:product_id>")
def products_show(product_id):
    conn = get_db_connection() # Pieslēdzas datubāzei
# Izpilda SQL vaicājumu, kurš atgriež tikai vienu produktu pēc ID
    product = conn.execute(
        """
        SELECT "Produkts".*, "ipasibas"."ipasiba" AS "ipasiba", "color"."color" AS "color", "aroma"."aroma" AS "aroma"
        FROM "Produkts"
        LEFT JOIN "ipasibas" ON "Produkts"."ipasibas_id" = "ipasibas"."id"
        LEFT JOIN "color" ON "Produkts"."color_id" = "color"."id"
        LEFT JOIN "aroma" ON "Produkts"."aroma_id" = "aroma"."id"
        WHERE "Produkts"."id" = ?
    """,
        (product_id,),
    ).fetchone()
    atsauksmes = conn.execute("SELECT * FROM atsauksmes WHERE produkts_id = ?", (product_id,)).fetchall()
# ? ir vieta, kur tiks ievietota vērtība – šajā gadījumā product_id
    conn.close() # Aizver savienojumu ar datubāzi
# Atgriežam HTML veidni 'products_show.html', padodot konkrēto produktu veidnei
    return render_template("products_show.html", product=product, atsauksmes=atsauksmes)

@app.route("/")
def index():
    return render_template("index.html")
# @app.route("/produkti")
# # def products():
# #     return render_template("produkts.html")
@app.route("/par-mums")
def about():
    return render_template("about.html")
@app.route("/komanda")
def komanda():
    return render_template("komanda.html")

@app.route("/produkti/<int:product_id>/atsauksme", methods=["GET", "POST"])
def pievienot_atsauksmi(product_id):
    conn = get_db_connection()
    
    if request.method == "POST":
        vards = request.form["vards"]
        teksts = request.form["teksts"]

        conn.execute(
            "INSERT INTO atsauksmes (produkts_id, vards, teksts) VALUES (?, ?, ?)",
            (product_id, vards, teksts)
        )
        conn.commit()
        conn.close()
        return redirect(f"/produkti/{product_id}")  # Atgriežas uz produkta lapu

    # GET metode — rāda formu
    conn.close()
    return render_template("pievienot_atsauksmi.html", product_id=product_id)

@app.route("/atsauksme/<int:id>/edit", methods=["GET", "POST"])
def rediget_atsauksmi(id):
    conn = get_db_connection()
    atsauksme = conn.execute("SELECT * FROM atsauksmes WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        vards = request.form["vards"]
        teksts = request.form["teksts"]

        conn.execute(
            "UPDATE atsauksmes SET vards = ?, teksts = ? WHERE id = ?",
            (vards, teksts, id)
        )
        conn.commit()
        conn.close()
        return redirect(f"/produkti/{atsauksme['produkts_id']}")  # atgriežas uz produkta lapu

    conn.close()
    return render_template("rediget_atsauksmi.html", atsauksme=atsauksme)
@app.route("/atsauksme/<int:id>/delete", methods=["POST"])
def dzest_atsauksmi(id):
    conn = get_db_connection()
    atsauksme = conn.execute("SELECT * FROM atsauksmes WHERE id = ?", (id,)).fetchone()

    if atsauksme is None:
        conn.close()
        return "Atsauksme nav atrasta", 404

    conn.execute("DELETE FROM atsauksmes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(f"/produkti/{atsauksme['produkts_id']}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

