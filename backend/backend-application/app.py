from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/api/message")
def message():
    return jsonify({
        "message": "Hello from the Kubernetes backend!"
    })


@app.route("/api/db")
def database():
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"]
        )

        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "database": result[0],
            "user": result[1],
            "status": "connected"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)