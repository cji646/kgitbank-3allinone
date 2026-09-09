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

# 세션 내용이 실제로 바뀌지 않는 한, 요청마다 세션 쿠키를 다시 서명해서
# 값이 매번 바뀌는 것을 막는다. 이걸 안 하면(기본값 True) Flask가 매
# 요청마다 만료시간을 갱신하며 쿠키 값을 새로 발급해서, SOC가 로그인
# 시점의 세션 값과 이후 페이지 방문 시점의 세션 값을 서로 다른 값으로
# 보게 되어 계정 단위 활동 추적(세션 기준 매칭)이 되지 않는다.
app.config["SESSION_REFRESH_EACH_REQUEST"] = False

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
