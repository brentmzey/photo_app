import base64
from flask import Flask, request, render_template, jsonify
import psycopg2
import sqlite3
import os
import logging
import uuid
import redis

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "postgres")  # "postgres" or "sqlite"
DB_HOST = "localhost"
DB_NAME = "photo_db"
DB_USER = "postgres"  # Replace with your PostgreSQL username, if necessary
DB_PASS = os.getenv("PGPASSWORD", "<none>")  # Ideally should be a complete secret
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/tmp/photo.db")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
redis_client = None
use_redis = False  # Flag indicating if Redis is available

# Try to connect to Redis
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test if Redis is reachable
    use_redis = True
    logging.info("Connected to Redis.")
except redis.ConnectionError:
    logging.warning("Redis is not reachable. The application will not use caching.")

def get_db_connection():
    try:
        if DB_TYPE == "postgres":
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        elif DB_TYPE == "sqlite":
            conn = sqlite3.connect(SQLITE_DB_PATH)
        else:
            raise ValueError("Unsupported DB_TYPE specified")
        logging.info(f"Connected to the {DB_TYPE} database.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if DB_TYPE == "sqlite":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id TEXT PRIMARY KEY,
                    image_data BLOB NOT NULL,
                    nickname TEXT NOT NULL,
                    mime_type TEXT NOT NULL
                )
            """)
        elif DB_TYPE == "postgres":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    image_data BYTEA NOT NULL,
                    nickname TEXT NOT NULL,
                    mime_type TEXT NOT NULL
                )
            """)
        conn.commit()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing the database: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Initialize the database
init_db()

# Log the SQLite path if SQLite is used
if DB_TYPE == "sqlite":
    logging.info(f"SQLite database file is located at: {SQLITE_DB_PATH}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            nickname = request.form["nickname"]
            mime_type = request.form["mime_type"]
            image_data = request.files["image_data"].read()
            image_id = str(uuid.uuid4())  # Generate a new UUID for the image

            conn = get_db_connection()
            cur = conn.cursor()
            if DB_TYPE == "postgres":
                cur.execute(
                    "INSERT INTO images (image_id, image_data, nickname, mime_type) VALUES (%s, %s, %s, %s)",
                    (image_id, psycopg2.Binary(image_data), nickname, mime_type)
                )
            elif DB_TYPE == "sqlite":
                cur.execute(
                    "INSERT INTO images (id, image_data, nickname, mime_type) VALUES (?, ?, ?, ?)",
                    (image_id, sqlite3.Binary(image_data), nickname, mime_type)
                )
            
            conn.commit()
            logging.info(f"Image with nickname '{nickname}' uploaded successfully.")
            return f"<div class='success-message'>Image '{nickname}' uploaded successfully!</div>"
        except Exception as e:
            logging.error(f"Error during image upload: {e}")
            return f"<div class='error-message'>Image upload failed: {str(e)}</div>", 500
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("index.html")

@app.route("/dbtype")
def dbtype():
    return jsonify({"db_type": DB_TYPE})

@app.route("/images/<nickname>")
def get_image(nickname):
    conn = None
    cur = None
    try:
        # Try to fetch image data from Redis cache if Redis is available
        if use_redis and redis_client:
            cached_image = redis_client.get(nickname)
            if cached_image:
                logging.info(f"Cache hit for nickname '{nickname}'.")
                image_data, mime_type = cached_image.split(b'|')
                return jsonify([{
                    'image_data': base64.b64encode(image_data).decode('utf-8'),
                    'mime_type': mime_type.decode('utf-8')
                }])

        # If cache miss or Redis is not used, fetch from database
        logging.info(f"Cache miss for nickname '{nickname}' or caching is disabled. Fetching from database.")
        conn = get_db_connection()
        cur = conn.cursor()
        if DB_TYPE == "postgres":
            cur.execute("SELECT image_data, mime_type FROM images WHERE nickname = %s", (nickname,))
        elif DB_TYPE == "sqlite":
            cur.execute("SELECT image_data, mime_type FROM images WHERE nickname = ?", (nickname,))
        rows = cur.fetchall()

        images = []
        for row in rows:
            image_data, mime_type = row
            if hasattr(image_data, 'tobytes'):
                image_data = image_data.tobytes()
            base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
            images.append({'image_data': base64_encoded_data, 'mime_type': mime_type})

        if images:
            logging.info(f"Fetched images for nickname '{nickname}'.")
            # Cache the first image found if Redis is available
            if use_redis and redis_client:
                to_cache = b'|'.join([image_data, mime_type.encode('utf-8')])
                redis_client.set(nickname, to_cache)
        else:
            logging.info(f"No images found for nickname '{nickname}'.")

        return jsonify(images)

    except Exception as e:
        logging.error(f"Error fetching images for nickname '{nickname}': {e}")
        return jsonify({"error": f"Error fetching images for nickname '{nickname}'", "details": str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)
