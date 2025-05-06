import sqlite3
from pathlib import Path

db = Path(__file__).parent / "ziepessmu.db"
conn = sqlite3.connect(db)

conn.execute("""
CREATE TABLE atsauksmes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produkts_id INTEGER NOT NULL,
    vards TEXT NOT NULL,
    teksts TEXT NOT NULL,
    FOREIGN KEY (produkts_id) REFERENCES Produkts(id)
)
""")

conn.commit()
conn.close()
print("Tabula atsauksmes izveidota.")