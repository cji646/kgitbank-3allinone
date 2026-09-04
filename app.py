from flask import Flask
from routes.auth import auth_bp
from routes.safety import safety_bp
import os


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

# 한글 JSON 출력
app.json.ensure_ascii = False

# 인증 관련 API 등록
app.register_blueprint(auth_bp)
app.register_blueprint(safety_bp)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
