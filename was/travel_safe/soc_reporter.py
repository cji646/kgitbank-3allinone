import os
import logging
import requests

logger = logging.getLogger("soc_reporter")

# SOC 서버 주소
SOC_INGEST_URL = os.environ.get(
    "SOC_INGEST_URL",
    "http://SOC_SERVER_IP/ingest/login"
)

# SOC 서버와 약속한 인증 토큰
SOC_INGEST_TOKEN = os.environ.get(
    "SOC_INGEST_TOKEN",
    ""
)


def report_login(ip, username, success, user_agent=None):
    """
    WAS에서 로그인 성공/실패가 발생했을 때
    SOC 서버의 /ingest/login으로 이벤트를 전달합니다.
    """

    payload = {
        "ip": ip,
        "username": username,
        "success": success,
        "user_agent": user_agent
    }

    headers = {
        "X-SOC-Token": SOC_INGEST_TOKEN
    }

    try:
        response = requests.post(
            SOC_INGEST_URL,
            json=payload,
            headers=headers,
            timeout=3
        )

        print("SOC 전송 시도:", SOC_INGEST_URL)
        print("SOC 응답:", response.status_code, response.text)

        if response.status_code != 200:
            logger.warning(
                "SOC login event 전송 실패: %s %s",
                response.status_code,
                response.text
            )

    except Exception as e:
        # SOC 서버가 죽어 있어도
        # 사용자 로그인 자체는 실패하지 않도록 합니다.
        logger.warning("SOC login event 전송 오류: %s", e)


def report_logout(ip, username, user_agent=None):
    """
    WAS에서 로그아웃이 발생했을 때
    SOC 서버의 /ingest/logout으로 이벤트를 전달합니다.
    """

    logout_url = SOC_INGEST_URL.replace(
        "/ingest/login",
        "/ingest/logout"
    )

    payload = {
        "ip": ip,
        "username": username,
        "user_agent": user_agent
    }

    headers = {
        "X-SOC-Token": SOC_INGEST_TOKEN
    }

    try:
        response = requests.post(
            logout_url,
            json=payload,
            headers=headers,
            timeout=3
        )

        if response.status_code != 200:
            logger.warning(
                "SOC logout event 전송 실패: %s %s",
                response.status_code,
                response.text
            )

    except Exception as e:
        logger.warning("SOC logout event 전송 오류: %s", e)



