import os
import pika
import logging

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
IMAGE_PROCESSING_EXCHANGE = "image-processing"
IMAGE_PROCESSING_QUEUE = "image-processing-queue"
IMAGE_UPLOADED_EXCHANGE = "photo-app"
IMAGE_UPLOADED_ROUTING_KEY = "image.uploaded"

def send_message(exchange, routing_key, body):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='direct')
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)
        connection.close()
        logging.info(f"Sent message to exchange '{exchange}' with routing key '{routing_key}': {body}")
    except Exception as e:
        logging.error(f"Error sending message to RabbitMQ: {e}")
