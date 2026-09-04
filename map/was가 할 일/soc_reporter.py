"""
SOC 연동 모듈 - Flask 로그인 라우트에 붙여서 쓰는 헬퍼.

사용법 (로그인 처리하는 뷰 함수 안에서):

    from soc_reporter import report_login

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            report_login(request, username, success=True)
            # ... 로그인 성공 처리 (세션 생성 등)
            return redirect(url_for("home"))
        else:
            report_login(request, username, success=False)
            # ... 로그인 실패 처리
            return "로그인 실패", 401

환경변수 설정 (WAS 서버에서):
    export SOC_INGEST_URL="http://SOC서버IP/ingest/login"
    export SOC_INGEST_TOKEN="SOC 서버의 SOC_INGEST_TOKEN과 동일한 값"

필요 패키지: pip install requests
"""
import os
import logging

import requests

logger = logging.getLogger("soc_reporter")

SOC_INGEST_URL = os.environ.get("SOC_INGEST_URL", "http://SOC서버IP/ingest/login")
SOC_INGEST_TOKEN = os.environ.get("SOC_INGEST_TOKEN", "")

# SOC가 느리거나 죽어있어도 사이트 로그인 자체가 느려지거나 막히면 안 되므로
# 아주 짧은 타임아웃을 쓰고, 실패해도 예외를 절대 밖으로 던지지 않는다 (fail-open).
SOC_TIMEOUT_SEC = 1.5


def get_client_ip(request) -> str:
    """리버스 프록시(Nginx 등) 뒤에 있으면 request.remote_addr는 프록시
    IP가 잡히므로, X-Forwarded-For 헤더의 첫 IP를 우선 사용한다."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def report_login(request, username: str, success: bool) -> None:
    """로그인 성공/실패를 SOC로 보고한다. 비밀번호 원문은 절대 보내지 않는다."""
    if not SOC_INGEST_TOKEN:
        logger.debug("SOC_INGEST_TOKEN 미설정 - 보고를 건너뜁니다.")
        return

    try:
        requests.post(
            SOC_INGEST_URL,
            json={
                "ip": get_client_ip(request),
                "username": username,
                "success": success,
            },
            headers={"X-SOC-Token": SOC_INGEST_TOKEN},
            timeout=SOC_TIMEOUT_SEC,
        )
    except requests.RequestException:
        # SOC 연동 실패는 로그인 자체를 막는 이유가 되면 안 되므로 조용히 무시.
        logger.warning("SOC 로그인 이벤트 보고 실패 (무시하고 계속 진행)", exc_info=True)
