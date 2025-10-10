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