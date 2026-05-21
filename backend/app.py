import os
import sys
import json
import bcrypt
import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
import jwt

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, "database")

DB_TYPE     = os.getenv("DB_TYPE")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SECRET_KEY  = os.getenv("SECRET_KEY", "cocoa-dashboard-secret-2026")
TOKEN_TTL_H = int(os.getenv("TOKEN_TTL_H", "8"))   


def get_db_url():
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
engine = get_engine = lambda: create_engine(get_db_url())

_engine = get_engine()



def make_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_TTL_H),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def require_auth(f):
    """Decorator that validates Bearer token."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth.split(" ", 1)[1]
        try:
            decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper



@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    with _engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, password_hash FROM users WHERE username = :u"),
            {"u": username},
        ).fetchone()

    if not row:
        return jsonify({"error": "Invalid credentials"}), 401

    user_id, pw_hash = row
    if isinstance(pw_hash, str):
        pw_hash = pw_hash.encode("utf-8")

    if not bcrypt.checkpw(password.encode("utf-8"), pw_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = make_token(user_id, username)
    return jsonify({"token": token, "username": username})


@app.route("/api/auth/logout", methods=["POST"])
@require_auth
def logout():
    # JWT is stateless — invalidation happens client-side by discarding the token
    return jsonify({"message": "Logged out"})



@app.route("/api/indicators/yearly", methods=["GET"])
@require_auth
def yearly_indicators():
    with _engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT series, year, avg_value, yoy_change, yoy_pct_change, pct_change_ref
                FROM yearly_indicators
                WHERE year BETWEEN 2020 AND 2026
                ORDER BY series, year
            """)
        ).fetchall()

    cocoa_data, ppi_data = [], []
    for r in rows:
        item = {
            "year": r[1],
            "avg_value": round(r[2], 4) if r[2] is not None else None,
            "yoy_change": round(r[3], 4) if r[3] is not None else None,
            "yoy_pct_change": round(r[4], 4) if r[4] is not None else None,
            "pct_change_ref": round(r[5], 4) if r[5] is not None else None,
        }
        if r[0] == "PCOCOUSDM":
            cocoa_data.append(item)
        else:
            ppi_data.append(item)

    return jsonify({"cocoa": cocoa_data, "ppi": ppi_data})


@app.route("/api/indicators/monthly", methods=["GET"])
@require_auth
def monthly_indicators():
    with _engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT date_str, series, value
                FROM raw_monthly
                ORDER BY series, date_str
            """)
        ).fetchall()

    cocoa_data, ppi_data = [], []
    for r in rows:
        item = {"date": r[0], "value": round(r[2], 4)}
        if r[1] == "PCOCOUSDM":
            cocoa_data.append(item)
        else:
            ppi_data.append(item)

    return jsonify({"cocoa": cocoa_data, "ppi": ppi_data})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[API] Starting Cocoa Dashboard API on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")