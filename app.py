import base64
from flask import Flask, request, render_template, jsonify
import psycopg2
import binascii

app = Flask(__name__)

# Database configuration
DB_HOST = "localhost"
DB_NAME = "photo_db"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASS = "Bmz4795abbie!"  # Replace with your PostgreSQL password

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nickname = request.form["nickname"]
        mime_type = request.form["mime_type"]
        image_data = request.files["image_data"].read()

        # Convert image data to hex
        hex_data = binascii.hexlify(image_data).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO images (image_data, nickname, mime_type) VALUES (%s, %s, %s)", (hex_data, nickname, mime_type))
        conn.commit()
        cur.close()
        conn.close()
        return "Image uploaded successfully!"

    return render_template("index.html")

@app.route("/images/<nickname>")
def get_image(nickname):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image_data, mime_type FROM images WHERE nickname = %s", (nickname,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        images = []
        for row in rows:
            hex_data, mime_type = row

            # Decode the hex data to bytes
            image_data = binascii.unhexlify(hex_data)

            # Encode the bytes to base64
            base64_encoded_data = base64.b64encode(image_data).decode('utf-8')

            images.append({'image_data': base64_encoded_data, 'mime_type': mime_type})
        return jsonify(images)
    else:
        return "Image not found", 404

if __name__ == "__main__":
    app.run(debug=True)
