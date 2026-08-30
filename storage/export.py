"""Export de l'historique des vols en CSV. Voir chapitre 12 du livre."""
import csv


def export_flights_csv(conn, path="export_vols.csv"):
    rows = conn.execute("SELECT * FROM flights").fetchall()
    columns = [d[0] for d in conn.execute("SELECT * FROM flights").description]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
