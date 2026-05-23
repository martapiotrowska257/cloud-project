import os
from flask import Flask, jsonify, request
from flask_cors import CORS # Cross-Origin Resource Sharing, komunikacja między frontendem, a backendem mimo różnych portów
from dotenv import load_dotenv
import psycopg2 # biblioteka do komunikacji z bazą danych PostgreSQL
import psycopg2.extras

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "tododb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", "5432")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ── Health check — Kubernetes będzie to odpytywał ──────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ── Pobierz wszystkie zadania ───────────────────────────────────────
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # zwraca wyniki jako słowniki, co ułatwia konwersję do JSON
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(list(tasks))

# ── Dodaj zadanie ───────────────────────────────────────────────────
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Tytuł nie może być pusty"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING *",
        (title,)
    )
    task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(task)), 201

# ── Zaktualizuj zadanie (toggle done) ──────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "UPDATE tasks SET done = %s WHERE id = %s RETURNING *",
        (data.get("done"), task_id)
    )
    task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not task:
        return jsonify({"error": "Nie znaleziono zadania"}), 404
    return jsonify(dict(task))

# ── Usuń zadanie ────────────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Usunięto"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)