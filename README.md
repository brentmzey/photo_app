# Photos API App

This project is a simple web application using Flask and PostgreSQL.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python, which is used to build the web application.
- **PostgreSQL**: An open-source, advanced object-relational database system, used to store and manage the data for the application.
- **Python**: The primary programming language used for developing the application.
- **psycopg2**: A PostgreSQL adapter for Python used to interact with the database.

### Environment Nuances

- Ensure Python 3.x is installed.
- Postgres should be accessible locally with user privileges.
- The environment should have `psycopg2` installed to allow Flask to communicate with PostgreSQL.

## Setup Instructions

### Install PostgreSQL Locally

Ensure PostgreSQL is installed and running on your local machine. Normally, this can be done through a package manager or by downloading it directly from the PostgreSQL website.

### Database Setup

1. **Delete Existing Database (if exists):**

   If there's an existing database named `photo_db`, you can drop it using:

   ```bash
   psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS photo_db"
   ```

2. **Create the Necessary Database:**

   To create a new database, run:

   ```bash
   psql -U postgres -d postgres -c "CREATE DATABASE photo_db WITH OWNER = postgres TEMPLATE template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' CONNECTION LIMIT = -1;"
   ```

### Install Dependencies

Set up a virtual environment and install the application dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask psycopg2
```

### Running the Application

Start the application using:

```bash
python3 app.py
```

## Database Management

### Create a Database Dump/Backup

To create a dump (backup) of the database:

```bash
pg_dump -U postgres -h localhost -p 5432 photo_db > ~/Downloads/photo_db.dump
```

### Restore Database from Dump File

To restore the database from a dump file:

```bash
psql -U postgres -d photo_db < photo_db.dump
```

Ensure the dump file location is correct and accessible. Adjust the file path as necessary.

## Remarks

Customize the database and user settings based on your local PostgreSQL configurations.

If any dependencies or configurations change, adjust the pip install command and database commands accordingly.