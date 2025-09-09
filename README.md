# Photos API App

This project is a simple web application using Flask and supports both PostgreSQL and SQLite as database backends.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python, used to build the web application.
- **PostgreSQL**: An open-source, advanced object-relational database system, used to store and manage the data for the application.
- **SQLite**: A lightweight, file-based database engine, supported as an alternative backend.
- **Python**: The primary programming language used for developing the application.
- **psycopg2**: A PostgreSQL adapter for Python used to interact with PostgreSQL.
- **sqlite3**: Python’s built-in library for interacting with SQLite databases.

### Environment Nuances

- Ensure Python 3.x is installed.
- For PostgreSQL: Postgres should be accessible locally with user privileges.
- For SQLite: No server setup is required; the database is stored as a file.
- The environment should have `psycopg2` installed to allow Flask to communicate with PostgreSQL.

## Setup Instructions

### Choose Your Database Backend

By default, the app uses PostgreSQL. To use SQLite, set the environment variable `DB_TYPE=sqlite` before running the app.

#### To use PostgreSQL:

1. **Install PostgreSQL Locally**

   Ensure PostgreSQL is installed and running on your local machine. You can install it via a package manager or download it from the PostgreSQL website.

2. **Database Setup**

   - **Delete Existing Database (if exists):**

     ```bash
     psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS photo_db"
     ```

   - **Create the Necessary Database:**

     ```bash
     psql -U postgres -d postgres -c "CREATE DATABASE photo_db WITH OWNER = postgres TEMPLATE template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' CONNECTION LIMIT = -1;"
     ```

#### To use SQLite:

1. **No Server Installation Needed**

   SQLite is file-based and requires no server setup. The default database file path is `/tmp/photo.db`, but you can override it by setting the `SQLITE_DB_PATH` environment variable.

   ```bash
   export DB_TYPE=sqlite
   export SQLITE_DB_PATH=/path/to/your/photo.db  # Optional, defaults to /tmp/photo.db
   ```

2. **Database Initialization**

   The database and table will be created automatically when you run the app for the first time.

### Install Dependencies

Set up a virtual environment and install the application dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask psycopg2
```

> If you are only using SQLite, `psycopg2` is not strictly required, but it is safe to install for both backends.

### Running the Application

Start the application using:

```bash
python3 app.py
```

## Database Management

### PostgreSQL: Create a Database Dump/Backup

To create a dump (backup) of the database:

```bash
pg_dump -U postgres -h localhost -p 5432 photo_db > ~/Downloads/photo_db.dump
```

### PostgreSQL: Restore Database from Dump File

To restore the database from a dump file:

```bash
psql -U postgres -d photo_db < photo_db.dump
```

Ensure the dump file location is correct and accessible. Adjust the file path as necessary.

### SQLite: Backup and Restore

To backup your SQLite database, simply copy the database file:

```bash
cp /tmp/photo.db ~/Downloads/photo_db_backup.db
```

To restore, copy the backup file back to the desired location:

```bash
cp ~/Downloads/photo_db_backup.db /tmp/photo.db
```

## Remarks

- Customize the database and user settings based on your local PostgreSQL or SQLite configurations.
- If any dependencies or configurations change, adjust the pip install command and database commands accordingly.
- The app will automatically create the necessary tables for either backend on startup.
