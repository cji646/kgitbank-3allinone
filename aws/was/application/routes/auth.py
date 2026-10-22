from flask import Blueprint, request, jsonify, session, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_db_connection
from soc_reporter import report_login, report_logout, report_signup, report_withdraw
import re
import time

auth_bp = Blueprint("auth", __name__)


# =========================
# 로그인 시도 제한 설정
# =========================

MAX_LOGIN_ATTEMPTS = 5
LOGIN_BLOCK_TIME = 300  # 5분

# 로그인 실패 기록
login_attempts = {}

# 이메일 형식 검사 패턴
EMAIL_PATTERN = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'


# =========================
# 공통 유틸 함수
# =========================

def is_valid_email(email):
    """이메일 형식 검사"""
    return re.match(EMAIL_PATTERN, email) is not None


def validate_password_strength(password):
    """
    비밀번호 강도 검사
    최소 8자 + 영문 + 숫자 + 특수문자
    통과하면 None, 실패하면 에러 메시지 반환
    """
    if len(password) < 8:
        return "비밀번호는 최소 8자 이상이어야 합니다."

    if not re.search(r'[A-Za-z]', password):
        return "비밀번호에는 영문자가 포함되어야 합니다."

    if not re.search(r'[0-9]', password):
        return "비밀번호에는 숫자가 포함되어야 합니다."

    if not re.search(r'[^A-Za-z0-9]', password):
        return "비밀번호에는 특수문자가 반드시 포함되어야 합니다."

    return None


def record_login_failure(email, current_time):
    """
    로그인 실패 기록 갱신 + SOC 로그인 실패 보고
    """
    if email not in login_attempts:
        login_attempts[email] = {
            "count": 1,
            "time": current_time
        }
    else:
        login_attempts[email]["count"] += 1

    # SOC 로그인 실패 보고
    report_login(
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        username=email,
        success=False,
        user_agent=request.headers.get("User-Agent")
    )


# =========================
# 회원가입
# =========================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다."
        }), 400

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({
            "success": False,
            "message": "이메일, 비밀번호, 이름은 모두 입력해야 합니다."
        }), 400

    # =========================
    # 이메일 형식 검사
    # =========================

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "올바른 이메일 형식이 아닙니다."
        }), 400

    # =========================
    # 비밀번호 검사
    # 최소 8자
    # 영문 + 숫자 + 특수문자
    # =========================

    password_error = validate_password_strength(password)

    if password_error:
        return jsonify({
            "success": False,
            "message": password_error
        }), 400

    # =========================
    # 이름 길이 검사
    # 최대 50자
    # =========================

    if len(name) > 50:
        return jsonify({
            "success": False,
            "message": "이름은 최대 50자까지 입력할 수 있습니다."
        }), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:

            # 이메일 중복 확인
            sql = """
                SELECT user_id
                FROM users
                WHERE email = %s
            """

            cursor.execute(sql, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({
                    "success": False,
                    "message": "이미 가입된 이메일입니다."
                }), 409

            # 비밀번호 해시
            hashed_password = generate_password_hash(password)

            # 회원정보 저장
            sql = """
                INSERT INTO users
                (password, name, email)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                sql,
                (hashed_password, name, email)
            )

            conn.commit()

            user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "회원가입이 완료되었습니다.",
            "user_id": user_id
        }), 201

    except Exception as e:

        if conn:
            conn.rollback()

        print("회원가입 오류:", e)

        return jsonify({
            "success": False,
            "message": "회원가입 처리 중 오류가 발생했습니다."
        }), 500

    finally:
        if conn:
            conn.close()


# =========================
# 로그인
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "이메일과 비밀번호를 입력해야 합니다."
        }), 400

    # =========================
    # 이메일 형식 검사
    # =========================

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "올바른 이메일 형식이 아닙니다."
        }), 400

    # =========================
    # 로그인 시도 횟수 확인
    # =========================

    current_time = time.time()

    if email in login_attempts:

        attempt_count = login_attempts[email]["count"]
        first_attempt = login_attempts[email]["time"]

        # 5분이 지나면 실패 기록 초기화
        if current_time - first_attempt >= LOGIN_BLOCK_TIME:

            del login_attempts[email]

        # 5회 이상 실패한 경우
        elif attempt_count >= MAX_LOGIN_ATTEMPTS:

            return jsonify({
                "success": False,
                "message": "로그인 시도 횟수를 초과했습니다. 5분 후 다시 시도해주세요."
            }), 429

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:

            sql = """
                SELECT user_id, password, name, email, role
                FROM users
                WHERE email = %s
            """

            cursor.execute(sql, (email,))
            user = cursor.fetchone()

        if not user:

            # 로그인 실패 기록 + SOC 보고
            record_login_failure(email, current_time)

            return jsonify({
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }), 401

        # =========================
        # 비밀번호 확인
        # =========================

        if not check_password_hash(user["password"], password):

            # 로그인 실패 기록 + SOC 보고
            record_login_failure(email, current_time)

            return jsonify({
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }), 401

        # =========================
        # 로그인 성공
        # =========================

        # 실패 기록 삭제
        if email in login_attempts:
            del login_attempts[email]

        # 로그인 세션 생성
        session.permanent = True
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"] 

        #SOC에 로그인 보고
        report_login(
            ip=request.headers.get("X-Forwarded-For", request.remote_addr),
            username=email,
            success=True,
            user_agent=request.headers.get("User-Agent")
        )

        return jsonify({
            "success": True,
            "message": "로그인 성공",
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }), 200

    except Exception as e:

        print("로그인 오류:", e)

        return jsonify({
            "success": False,
            "message": "로그인 처리 중 오류가 발생했습니다."
        }), 500

    finally:

        if conn:
            conn.close()


# =========================
# 로그아웃
# =========================
@auth_bp.route("/logout", methods=["POST"])
def logout():

    # 로그아웃 전에 현재 로그인한 사용자 정보 가져오기
    user_id = session.get("user_id")
    email = session.get("email")

    # 로그인된 사용자라면 SOC에 로그아웃 이벤트 전송
    if user_id is not None:

        # 실제 클라이언트 IP 확인
        ip = request.headers.get(
            "X-Forwarded-For",
            request.remote_addr
        )

        # X-Forwarded-For에 IP가 여러 개 있으면 첫 번째 IP 사용
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

        # 사용자 브라우저 정보
        user_agent = request.headers.get("User-Agent")

        # SOC 로그아웃 이벤트 전송
        report_logout(
            ip=ip,
            username=email,
            user_agent=user_agent
        )

    # 세션 삭제
    session.clear()

    return jsonify({
        "success": True,
        "message": "로그아웃 되었습니다."
    }), 200

# =========================
# 세션 확인용
# =========================
@auth_bp.route("/me", methods=["GET"])
def me():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "로그인이 필요합니다."
        }), 401

    return jsonify({
        "success": True,
        "user_id": session["user_id"],
        "name": session["name"],
        "email": session["email"],
        "role": session["role"]
    }), 200


# =========================
# 비밀번호 찾기 / 재설정
# =========================
@auth_bp.route("/find-password", methods=["POST"])
def find_password():
    return jsonify({"success": False, "message": "이메일 인증 기능 준비 중입니다."}), 503

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다."
        }), 400

    email = data.get("email")
    name = data.get("name")
    new_password = data.get("new_password")

    # 필수값 확인
    if not email or not name or not new_password:
        return jsonify({
            "success": False,
            "message": "이메일, 이름, 새 비밀번호를 입력해주세요."
        }), 400

    # =========================
    # 새 비밀번호 검사
    # =========================

    password_error = validate_password_strength(new_password)

    if password_error:
        return jsonify({
            "success": False,
            "message": password_error
        }), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:

            # 이메일 + 이름으로 사용자 확인
            sql = """
            SELECT user_id
            FROM users
            WHERE email = %s
              AND name = %s
            """

            cursor.execute(sql, (email, name))
            user = cursor.fetchone()

            # 사용자 정보 불일치
            if not user:
                return jsonify({
                    "success": False,
                    "message": "이메일 또는 이름이 일치하지 않습니다."
                }), 404

            # 새 비밀번호 Hash
            hashed_password = generate_password_hash(new_password)

            # 비밀번호 변경
            sql = """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            """

            cursor.execute(
                sql,
                (hashed_password, user["user_id"])
            )

            conn.commit()

            return jsonify({
                "success": True,
                "message": "비밀번호가 변경되었습니다."
            }), 200

    except Exception as e:

        if conn:
            conn.rollback()

        print("비밀번호 변경 오류:", e)

        return jsonify({
            "success": False,
            "message": "비밀번호 변경 중 오류가 발생했습니다."
        }), 500

    finally:

        if conn:
            conn.close()




# 회원가입 요청 처리 후 SOC에 성공/실패 이벤트 전송
@auth_bp.after_request
def send_signup_event_to_soc(response):
    if request.endpoint != "auth.register":
        return response

    try:
        from ipaddress import ip_address, ip_network

        data = request.get_json(silent=True)
        email = data.get("email", "") if isinstance(data, dict) else ""
        email = email if isinstance(email, str) else ""

        # X-Forwarded-For는 신뢰하는 Web VPC에서 온 경우에만 사용
        ip = request.remote_addr or ""
        try:
            if ip_address(ip) in ip_network("10.40.0.0/16"):
                forwarded = request.headers.get("X-Forwarded-For", "")
                if forwarded:
                    candidate = forwarded.split(",")[0].strip()
                    ip_address(candidate)
                    ip = candidate
        except ValueError:
            pass

        report_signup(
            ip=ip,
            username=email,
            success=(response.status_code == 201)
        )

    except Exception:
        current_app.logger.warning("SOC signup event 처리 실패")

    return response



# =========================
# 회원 탈퇴
# =========================
@auth_bp.route("/withdraw", methods=["POST"])
def withdraw():

    # 1. 로그인 확인
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "로그인이 필요합니다."
        }), 401

    # 2. 비밀번호 입력 확인
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "올바른 요청 형식이 아닙니다."
        }), 400

    password = data.get("password")

    if not isinstance(password, str) or not password:
        return jsonify({
            "success": False,
            "message": "비밀번호를 입력해주세요."
        }), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:

            # 3. DB에서 현재 회원 조회 및 잠금
            cursor.execute(
                """
                SELECT user_id, password, role
                FROM users
                WHERE user_id = %s
                FOR UPDATE
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if not user:
                conn.rollback()
                session.clear()

                return jsonify({
                    "success": False,
                    "message": "존재하지 않는 회원입니다."
                }), 401

            # 관리자 계정은 일반 회원 탈퇴 API에서 제외
            if user["role"] == "admin":
                conn.rollback()

                return jsonify({
                    "success": False,
                    "message": "관리자 계정은 이 기능으로 탈퇴할 수 없습니다."
                }), 403

            # 4. 비밀번호 재확인
            if not check_password_hash(user["password"], password):
                conn.rollback()

                return jsonify({
                    "success": False,
                    "message": "비밀번호가 올바르지 않습니다."
                }), 401

            # 5. 실제 회원 삭제
            cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,)
            )

            if cursor.rowcount != 1:
                raise RuntimeError("회원 삭제 건수가 올바르지 않습니다.")

        # 6. DB 변경 확정
        conn.commit()

        # 7. 현재 로그인 세션 삭제
        session.clear()

        return jsonify({
            "success": True,
            "message": "회원 탈퇴가 완료되었습니다."
        }), 200

    except Exception:
        if conn:
            conn.rollback()

        current_app.logger.exception("회원 탈퇴 처리 오류")

        return jsonify({
            "success": False,
            "message": "회원 탈퇴 처리 중 오류가 발생했습니다."
        }), 500

    finally:
        if conn:
            conn.close()



# =========================
# 회원 탈퇴 SOC 이벤트 연결
# =========================

@auth_bp.before_request
def remember_withdraw_user():
    if request.endpoint == "auth.withdraw":
        # 탈퇴 성공 시 세션이 삭제되므로 이메일을 미리 보관
        g.withdraw_username = session.get("email") or ""


@auth_bp.after_request
def send_withdraw_event_to_soc(response):

    if request.endpoint != "auth.withdraw":
        return response

    try:
        from ipaddress import ip_address, ip_network

        # 기본적으로 직접 접속한 IP 사용
        ip = request.remote_addr or ""

        # Web VPC에서 전달한 요청일 때만 X-Forwarded-For 사용
        try:
            if ip_address(ip) in ip_network("10.40.0.0/16"):
                forwarded = request.headers.get("X-Forwarded-For", "")
                if forwarded:
                    candidate = forwarded.split(",")[0].strip()
                    ip_address(candidate)
                    ip = candidate
        except ValueError:
            pass

        data = response.get_json(silent=True)
        success = (
            response.status_code == 200
            and isinstance(data, dict)
            and data.get("success") is True
        )

        if success:
            reason = "user_initiated"
        else:
            reason = {
                400: "invalid_request",
                401: "authentication_failed",
                403: "forbidden",
                500: "server_error"
            }.get(response.status_code, "withdraw_failed")

        report_withdraw(
            ip=ip,
            username=g.get("withdraw_username", ""),
            success=success,
            reason=reason
        )

    except Exception:
        current_app.logger.warning(
            "SOC 회원 탈퇴 이벤트 처리 오류"
        )

    return response
