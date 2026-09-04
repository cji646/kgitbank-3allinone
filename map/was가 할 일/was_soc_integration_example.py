"""
WAS(Flask) 쪽에서 SOC로 로그인/로그아웃을 보고하는 예시 코드.
기존 로그인/로그아웃 처리 로직 안에 이 부분만 추가하면 됩니다.

전제:
  - Flask의 session(서버 쿠키)과 별개로, SOC 추적용 session_id를 하나 더 발급해서
    로그인 시 Flask session에 저장해두고, 로그아웃 때 그대로 다시 사용합니다.
  - requests 라이브러리로 SOC(FastAPI, update_soc_v5.sh 적용된 상태)에 HTTP로 알립니다.
  - SOC 보고는 사이트 로그인/로그아웃 자체의 성공 여부에 절대 영향을 주면 안 되므로,
    항상 try/except로 감싸고 타임아웃을 짧게 둡니다 (SOC가 잠깐 죽어있어도 사이트는 정상 동작).
"""
import secrets

import requests
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = "여기에-실제-비밀키"  # 이미 갖고 계신 값 그대로 쓰세요

# SOC 서버(Linux-2) 주소. SOC API는 systemd 유닛에서 127.0.0.1:8001로만
# 리스닝하도록 되어 있으므로, 외부(WAS 서버)에서 직접 호출하려면
# --host 0.0.0.0 으로 바꾸거나 Nginx/Apache 리버스 프록시를 앞에 둬야 합니다.
SOC_INGEST_URL = "http://40.40.1.2:8001/ingest"
# systemd 유닛(soc-api.service)의 SOC_INGEST_TOKEN 값과 반드시 동일해야 합니다.
SOC_INGEST_TOKEN = "실제-SOC_INGEST_TOKEN-값"


def report_to_soc(path: str, payload: dict) -> None:
    """SOC 보고 실패가 로그인/로그아웃 흐름을 막으면 안 되므로 조용히 무시한다."""
    try:
        requests.post(
            f"{SOC_INGEST_URL}/{path}",
            json=payload,
            headers={"X-SOC-Token": SOC_INGEST_TOKEN},
            timeout=2,
        )
    except requests.RequestException:
        pass  # SOC가 잠깐 죽어있어도 로그인/로그아웃 자체는 정상 진행되어야 함


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    ip = request.remote_addr

    # === 기존에 이미 갖고 계신 로그인 검증 로직 자리 ===
    # (DB에서 계정 조회, 비밀번호 해시 비교 등 — 아래 check_credentials를
    #  실제 검증 함수로 교체하세요)
    success = check_credentials(username, password)

    if success:
        soc_session_id = secrets.token_hex(16)
        session["user"] = username
        session["soc_session_id"] = soc_session_id  # 로그아웃 때 이 값을 다시 사용

        report_to_soc(
            "login",
            {
                "ip": ip,
                "username": username,
                "success": True,
                "user_agent": request.headers.get("User-Agent"),
                "session_id": soc_session_id,
            },
        )
        return "로그인 성공"

    report_to_soc(
        "login",
        {
            "ip": ip,
            "username": username,
            "success": False,
        },
    )
    return "로그인 실패", 401


@app.route("/logout", methods=["POST"])
def logout():
    soc_session_id = session.get("soc_session_id")
    username = session.get("user")
    ip = request.remote_addr

    if soc_session_id:
        report_to_soc(
            "logout",
            {
                "session_id": soc_session_id,
                "ip": ip,
                "username": username,
            },
        )

    session.clear()
    return "로그아웃 완료"


def check_credentials(username: str, password: str) -> bool:
    """기존에 이미 갖고 계신 DB 조회/비밀번호 검증 함수로 교체하세요."""
    raise NotImplementedError
