# Python Photo App

This project is a simple web application using Flask and supports both PostgreSQL and SQLite as database backends. It also supports Redis caching for image retrieval and uses RabbitMQ for asynchronous message processing.

## Architecture Overview

The application is designed to be resilient and scalable. When an image is uploaded, the web application (app.py) does not immediately process and save the image to the database. Instead, it sends a message to a RabbitMQ queue and immediately returns a response to the client, indicating that the request has been received and is being processed.

A separate consumer process (consumer.py) listens for messages on this queue, processes the image, and saves it to the database. Once the image is successfully saved, the consumer sends a notification message to another RabbitMQ exchange.

A notification consumer (notification_consumer.py) listens for these notifications and can be used to trigger other actions, such as sending an email or updating a dashboard.

This asynchronous architecture ensures that the web application remains responsive, even under heavy load, and that image processing can be scaled independently of the web application.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python, used to build the web application.
- **PostgreSQL**: An open-source, advanced object-relational database system, used to store and manage the data for the application.
- **SQLite**: A lightweight, file-based database engine, supported as an alternative backend.
- **Redis**: An in-memory data structure store, used for caching image data.
- **RabbitMQ**: A popular open-source message broker that is used for asynchronous processing.
- **Pika**: A pure-Python implementation of the AMQP 0-9-1 protocol that is used to interact with RabbitMQ.
- **Python**: The primary programming language used for developing the application.
- **psycopg2-binary**: A PostgreSQL adapter for Python used to interact with PostgreSQL.
- **redis (Python package)**: Python client for Redis.
- **sqlite3**: Python’s built-in library for interacting with SQLite databases.

## Project Structure

```text
photo_app/
├── app.py
├── consumer.py
├── notification_consumer.py
├── messaging.py
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

## Messaging

The application uses RabbitMQ for asynchronous message passing. There are two main message flows:

1.  **Image Processing**: When an image is uploaded, a message is sent to the `image-processing` exchange with a routing key of `image-processing-queue`. The `consumer.py` script consumes messages from this queue.
2.  **Image Upload Notification**: After an image has been successfully processed and saved to the database, a message containing the image ID is sent to the `photo-app` exchange with a routing key of `image.uploaded`. The `notification_consumer.py` script consumes messages from a queue bound to this exchange.

## Setup Instructions

### 1. Prerequisites

- Python 3.x
- Docker (or a local installation of PostgreSQL, SQLite, Redis, and RabbitMQ)

### 2. Database Setup

The application can use either PostgreSQL or SQLite. The default is PostgreSQL. To use SQLite, set the environment variable `DB_TYPE=sqlite`.

- **PostgreSQL**: Ensure a PostgreSQL instance is running and accessible.
- **SQLite**: The database file will be created automatically.

### 3. Redis Setup

Ensure a Redis instance is running and accessible.

### 4. RabbitMQ Setup

Ensure a RabbitMQ instance is running and accessible.

### 5. Install Dependencies

Set up a virtual environment and install the application dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6. Running the Application

1.  **Start the web application:**

    ```bash
    python3 app.py
    ```

    The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

2.  **Start the image processing consumer:**

    ```bash
    python3 consumer.py
    ```

3.  **Start the notification consumer:**

    ```bash
    python3 notification_consumer.py
    ```
