from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os
import time

app = FastAPI()

# --- Database connection ---
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "mydb"),
        user=os.getenv("DB_USER", "myuser"),
        password=os.getenv("DB_PASSWORD", "mypassword")
    )

# --- Auto-create table on startup ---
@app.on_event("startup")
def startup():
    retries = 5
    while retries > 0:
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Table ready!")
            break
        except Exception as e:
            print(f"DB not ready yet... retrying ({e})")
            retries -= 1
            time.sleep(3)

# --- Healthcheck endpoint ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- POST: Insert a record ---
class Item(BaseModel):
    name: str
    description: str = ""

@app.post("/items")
def create_item(item: Item):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id",
        (item.name, item.description)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "name": item.name, "description": item.description}

# --- GET: Fetch all records ---
@app.get("/items")
def get_items():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM items")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]

