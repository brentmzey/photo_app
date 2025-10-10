# Polyglot Photo Application

This project demonstrates a polyglot microservices-based architecture with two standalone applications: one written in Python (Flask) and the other in Java (Quarkus). Both applications provide the same functionality: a web interface for uploading and viewing images, with asynchronous processing of image uploads.

## Architecture Overview

This project showcases a message-driven architecture where the web applications (Python/Flask and Java/Quarkus) act as producers, and background workers act as consumers. When an image is uploaded, the web application sends a message to a RabbitMQ exchange and immediately returns a response to the client. This ensures that the web application remains responsive and that image processing can be scaled independently.

There are two main message flows:

1.  **Image Processing**: A message containing the image data is sent to an `image-processing` queue. A consumer for each application listens to this queue, processes the image, and saves it to the database.
2.  **Image Upload Notification**: Once an image is successfully saved, a notification message is sent to a `photo-app` exchange. Both the Python and Java applications have a consumer that listens for these notifications and logs them to the console.

## Project Structure

```
/
├── README.md            (High-level overview of the polyglot project)
├── python/
│   ├── README.md        (Detailed README for the Python application)
│   ├── app.py
│   ├── consumer.py
│   ├── notification_consumer.py
│   ├── messaging.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
└── java/
    ├── README.md        (Detailed README for the Java application)
    └── photo-app/
        └── ...          (Java application files)
```

## Projects

This repository contains two standalone projects:

-   **Python Photo App**: A Flask-based web application. For more details, see the [Python Photo App README](python/README.md).
-   **Java Photo App**: A Quarkus-based web application. For more details, see the [Java Photo App README](java/README.md).

## Shared Infrastructure

Both applications are configured to use the following shared infrastructure:

-   **Database**: PostgreSQL or SQLite for data storage.
-   **Caching**: Redis for caching image data.
-   **Messaging**: RabbitMQ for asynchronous communication between services.

## Getting Started

To run this project, you will need to set up the shared infrastructure and then run each application independently. Please refer to the `README.md` file in each project's directory for detailed setup and running instructions.

## Example Run: Java, PostgreSQL, and Redis

For a production-like environment that prioritizes type safety, resiliency, and performance, the recommended setup is the Java (Quarkus) application with PostgreSQL and Redis.

Here is how to run this setup:

### 1. Start the Infrastructure

The easiest way to get PostgreSQL, Redis, and RabbitMQ running is with Docker. These commands will start the necessary services:

**PostgreSQL:**
```bash
docker run -d --name postgres-db -p 5432:5432 -e POSTGRES_DB=photo_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres
```

**Redis:**
```bash
docker run -d --name redis-cache -p 6379:6379 redis
```

**RabbitMQ:**
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 2. Run the Java Application

The Java application is configured to work with the services started above. The database schema will be created automatically on startup.

**Navigate to the Java project directory:**
```bash
cd java/photo-app
```

**Build the application:**
```bash
./mvnw install
```

**Run the application in development mode:**
```bash
./mvnw quarkus:dev
```

### 3. Access the Application

The application will be available at [http://localhost:8080](http://localhost:8080). You can now use the web interface to upload and view images.