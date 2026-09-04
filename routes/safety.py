from flask import Blueprint, jsonify
from db.connection import get_db_connection

safety_bp = Blueprint("safety", __name__)


@safety_bp.route("/safety", methods=["GET"])
def safety():

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:

            sql = """
                SELECT
                    country_id,
                    country_name,
                    continent,
                    safety_level,
                    emergency_number,
                    precautions,
                    updated_at
                FROM countries
                ORDER BY country_name
            """

            cursor.execute(sql)
            countries = cursor.fetchall()

        return jsonify({
            "success": True,
            "countries": countries
        })

    finally:
        conn.close()
