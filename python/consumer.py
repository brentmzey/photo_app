import json
import logging
import pika
import psycopg2
import sqlite3
import base64
import uuid
from messaging import send_message, IMAGE_PROCESSING_EXCHANGE, IMAGE_PROCESSING_QUEUE, IMAGE_UPLOADED_EXCHANGE, IMAGE_UPLOADED_ROUTING_KEY

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "postgres")  # "postgres" or "sqlite"
DB_HOST = "localhost"
DB_NAME = "photo_db"
DB_USER = "postgres"  # Replace with your PostgreSQL username, if necessary
DB_PASS = os.getenv("PGPASSWORD", "<none>")  # Ideally should be a complete secret
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/tmp/photo.db")

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

def process_image(ch, method, properties, body):
    message = json.loads(body)
    request_id = message.get("request_id")
    nickname = message.get("nickname")
    image_data = base64.b64decode(message.get("image_data"))
    mime_type = message.get("mime_type")
    image_id = str(uuid.uuid4())

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if DB_TYPE == "postgres":
            cur.execute(
                "INSERT INTO images (id, image_data, nickname, mime_type) VALUES (%s, %s, %s, %s)",
                (image_id, psycopg2.Binary(image_data), nickname, mime_type)
            )
        elif DB_TYPE == "sqlite":
            cur.execute(
                "INSERT INTO images (id, image_data, nickname, mime_type) VALUES (?, ?, ?, ?)",
                (image_id, sqlite3.Binary(image_data), nickname, mime_type)
            )
        conn.commit()
        logging.info(f"Request {request_id}: Image with nickname '{nickname}' uploaded successfully.")
        send_message(IMAGE_UPLOADED_EXCHANGE, IMAGE_UPLOADED_ROUTING_KEY, image_id)
    except Exception as e:
        logging.error(f"Request {request_id}: Error during image processing: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "localhost")))
    channel = connection.channel()

    channel.exchange_declare(exchange=IMAGE_PROCESSING_EXCHANGE, exchange_type='direct')
    result = channel.queue_declare(queue=IMAGE_PROCESSING_QUEUE, durable=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=IMAGE_PROCESSING_EXCHANGE, queue=queue_name, routing_key=IMAGE_PROCESSING_QUEUE)

    channel.basic_consume(queue=queue_name, on_message_callback=process_image)

    logging.info("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    main()
