# Quarkus Photo App

This document outlines the Quarkus-based Java application for handling photo uploads. The application is designed to be resilient and scalable, using asynchronous messaging for image processing.

## Architecture Overview

The application follows a message-driven architecture. When an image is uploaded to the REST API, the application does not immediately process and save the image to the database. Instead, it sends a message to a RabbitMQ queue and returns a response to the client, indicating that the request has been received and is being processed.

A separate consumer service within the application listens for messages on this queue, processes the image, and saves it to the database. Once the image is successfully saved, the consumer sends a notification message to another RabbitMQ exchange.

A notification consumer service listens for these notifications and can be used to trigger other actions, such as sending an email or updating a dashboard.

This asynchronous architecture ensures that the web application remains responsive, even under heavy load, and that image processing can be scaled independently of the web application.

## Technologies Used

- **Quarkus**: A Kubernetes-native Java stack tailored for GraalVM and OpenJDK HotSpot, crafted from the best of breed Java libraries and standards.
- **RESTEasy Reactive**: A reactive RESTful framework for building non-blocking web applications.
- **Hibernate ORM with Panache**: A simplified and opinionated data access layer for Hibernate ORM.
- **PostgreSQL**: An open-source, advanced object-relational database system.
- **SQLite**: A lightweight, file-based database engine.
- **Redis**: An in-memory data structure store, used for caching.
- **SmallRye Reactive Messaging**: A framework for building event-driven and reactive applications, with support for RabbitMQ.
- **Maven**: A build automation tool used for project management and dependency management.

## Project Structure

```text
java/
└── photo-app/
    ├── src/
    │   └── main/
    │       ├── java/
    │       │   └── com/
    │       │       └── example/
    │       │           ├── Image.java
    │       │           ├── ImageRepository.java
    │       │           ├── ImageResource.java
    │       │           ├── ImageProcessor.java
    │       │           └── NotificationConsumer.java
    │       └── resources/
    │           ├── META-INF/
    │           │   └── resources/
    │           │       └── index.html
    │           └── application.properties
    ├── pom.xml
    └── README.md
```

## Messaging

The application uses RabbitMQ for asynchronous message passing. There are two main message flows:

1.  **Image Processing**: When an image is uploaded, a message is sent to the `image-processing` channel. The `ImageProcessor` service consumes messages from this channel. The channel is configured in `application.properties` as follows:
    ```properties
    mp.messaging.incoming.image-processing.connector=smallrye-rabbitmq
    mp.messaging.incoming.image-processing.queue.name=image-processing-queue
    ```
2.  **Image Upload Notification**: After an image has been successfully processed and saved to the database, a message containing the image ID is sent to the `image-uploaded` channel. The `NotificationConsumer` service consumes messages from this channel. The channel is configured in `application.properties` as follows:
    ```properties
    mp.messaging.outgoing.image-uploaded.connector=smallrye-rabbitmq
    mp.messaging.outgoing.image-uploaded.exchange.name=photo-app
    mp.messaging.outgoing.image-uploaded.routing.key=image.uploaded
    ```
    The `NotificationConsumer` is configured to consume from the `photo-app` exchange:
    ```properties
    mp.messaging.incoming.photo-app.connector=smallrye-rabbitmq
    mp.messaging.incoming.photo-app.exchange.name=photo-app
    mp.messaging.incoming.photo-app.queue.name=photo-app-notification-queue
    ```

## Setup Instructions

### 1. Prerequisites

- Java 17+
- Maven 3.8+
- Docker (or a local installation of PostgreSQL, SQLite, Redis, and RabbitMQ)

### 2. Database Setup

The application can use either PostgreSQL or SQLite. The default is PostgreSQL for development and SQLite for production. The database schema is automatically created or updated on startup.

- **PostgreSQL**: Ensure a PostgreSQL instance is running and accessible. The default connection details are configured in `application.properties`.
- **SQLite**: The database file will be created automatically at the path specified in `application.properties`.

### 3. Redis Setup

Ensure a Redis instance is running and accessible. The default connection details are configured in `application.properties`.

### 4. RabbitMQ Setup

Ensure a RabbitMQ instance is running and accessible. The default connection details are configured in `application.properties`.

### 5. Build and Run

1.  **Navigate to the project directory:**

    ```bash
    cd java/photo-app
    ```

2.  **Build the application:**

    ```bash
    ./mvnw install
    ```

3.  **Run the application in development mode:**

    ```bash
    ./mvnw quarkus:dev
    ```

The application will be available at [http://localhost:8080](http://localhost:8080).

## Database Management

Since the application uses Hibernate ORM, the database schema is managed automatically. You can configure the behavior in `application.properties` using the `quarkus.hibernate-orm.database.generation` property.

- **`update`**: This will update the schema if it has changed.
- **`create`**: This will create the schema on every startup.
- **`drop-and-create`**: This will drop and then create the schema on every startup.
- **`validate`**: This will validate the schema against the entities.
- **`none`**: This will do nothing.

For manual database operations, you can use standard database tools like `psql` for PostgreSQL or `sqlite3` for SQLite.
