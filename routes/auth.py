from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_db_connection
from soc_reporter import report_login
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

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
        return jsonify({
            "success": False,
            "message": "올바른 이메일 형식이 아닙니다."
        }), 400

    # =========================
    # 비밀번호 검사
    # 최소 8자
    # 영문 + 숫자 + 특수문자
    # =========================

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "비밀번호는 최소 8자 이상이어야 합니다."
        }), 400

    if not re.search(r'[A-Za-z]', password):
        return jsonify({
            "success": False,
            "message": "비밀번호에는 영문자가 포함되어야 합니다."
        }), 400

    if not re.search(r'[0-9]', password):
        return jsonify({
            "success": False,
            "message": "비밀번호에는 숫자가 포함되어야 합니다."
        }), 400

    if not re.search(r'[^A-Za-z0-9]', password):
        return jsonify({
            "success": False,
            "message": "비밀번호에는 특수문자가 반드시 포함되어야 합니다."
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

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
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

            # 로그인 실패 기록
            if email not in login_attempts:

                login_attempts[email] = {
                    "count": 1,
                    "time": current_time
                }

            else:

                login_attempts[email]["count"] += 1

            # SOC에 로그인 실패 보고
            report_login(request, email, success=False)
            
            return jsonify({
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }), 401

        # =========================
        # 비밀번호 확인
        # =========================

        if not check_password_hash(user["password"], password):

            # 로그인 실패 기록
            if email not in login_attempts:

                login_attempts[email] = {
                    "count": 1,
                    "time": current_time
                }

            else:

                login_attempts[email]["count"] += 1
            
            # SOC에 로그인 실패 보고
            report_login(request, email, success=False)
            
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
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        #SOC에 로그인 성공 보고
        report_login(request, email, success=True)

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

