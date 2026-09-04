from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_db_connection

auth_bp = Blueprint("auth", __name__)

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
            return jsonify({
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }), 401

        # 비밀번호 확인
        if not check_password_hash(user["password"], password):
            return jsonify({
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }), 401

        # 로그인 세션 생성
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

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


@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "로그아웃 되었습니다."
    }), 200

# 세션 확인용 
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
