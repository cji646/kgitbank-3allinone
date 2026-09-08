from flask import Flask
from routes.auth import auth_bp
from routes.safety import safety_bp
from datetime import timedelta
import os
import logging


# =========================
# HAProxy Health Check 로그 숨김
# =========================
class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return '"HEAD / HTTP/1.0"' not in record.getMessage()


logging.getLogger("werkzeug").addFilter(HealthCheckFilter())


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=10)

# 한글 JSON 출력
app.json.ensure_ascii = False

# 인증 관련 API 등록
app.register_blueprint(auth_bp)
app.register_blueprint(safety_bp)


# =========================
# HAProxy Health Check
# =========================
@app.route("/")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )

