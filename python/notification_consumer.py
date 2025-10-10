import logging
import pika
import os

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
EXCHANGE_NAME = "photo-app"

def process_notification(ch, method, properties, body):
    image_id = body.decode()
    logging.info(f"Received notification for uploaded image: {image_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key="image.uploaded")

    logging.info("Waiting for notifications. To exit press CTRL+C")
    channel.basic_consume(queue=queue_name, on_message_callback=process_notification)
    channel.start_consuming()

if __name__ == '__main__':
    main()
