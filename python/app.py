import base64
from flask import Flask, request, render_template, jsonify
import psycopg2
import sqlite3
import os
import logging
import uuid
import redis
import pika

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_EXCHANGE = "photo-app"
RABBITMQ_ROUTING_KEY = "image.uploaded"

def send_message_to_rabbitmq(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type='direct')
        channel.basic_publish(exchange=RABBITMQ_EXCHANGE, routing_key=RABBITMQ_ROUTING_KEY, body=message)
        connection.close()
        logging.info(f"Sent message to RabbitMQ: {message}")
    except Exception as e:
        logging.error(f"Error sending message to RabbitMQ: {e}")

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
            # For Postgres, use UUID type for the id
            cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id UUID PRIMARY KEY,
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

def sniff_mime_type(file_storage):
    # Try to get MIME type from file object
    mime_type = file_storage.mimetype
    if mime_type and mime_type != 'application/octet-stream':
        return mime_type
    # Fallback: use imghdr and mimetypes
    file_bytes = file_storage.read()
    file_storage.seek(0)
    ext = imghdr.what(None, h=file_bytes)
    if ext:
        guessed = mimetypes.types_map.get(f".{ext}", None)
        if guessed:
            return guessed
    return "application/octet-stream"

import json
from messaging import send_message, IMAGE_PROCESSING_EXCHANGE, IMAGE_PROCESSING_QUEUE

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            request_id = str(uuid.uuid4())
            nickname = request.form["nickname"]
            image_file = request.files["image_data"]
            image_data = image_file.read()
            image_file.seek(0)
            mime_type = sniff_mime_type(image_file)

            message = {
                "request_id": request_id,
                "nickname": nickname,
                "image_data": base64.b64encode(image_data).decode('utf-8'),
                "mime_type": mime_type
            }

            send_message(IMAGE_PROCESSING_EXCHANGE, IMAGE_PROCESSING_QUEUE, json.dumps(message))

            return f"<div class='success-message'>Request {request_id} received. Image '{nickname}' is being processed.</div>", 202
        except Exception as e:
            logging.error(f"Error during image upload: {e}")
            return f"<div class='error-message'>Image upload failed: {str(e)}</div>", 500

    return render_template("index.html")

@app.route("/dbtype")
def dbtype():
    return jsonify({"db_type": DB_TYPE})

@app.route("/sniff-mime", methods=["POST"])
def sniff_mime():
    try:
        image_file = request.files["image_data"]
        mime_type = sniff_mime_type(image_file)
        return jsonify({"mime_type": mime_type})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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
