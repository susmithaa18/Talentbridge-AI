from flask import Blueprint, request, jsonify
from database import get_connection
from flask_bcrypt import Bcrypt

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data["full_name"]
    email = data["email"]
    password = data["password"]
    role = data["role"]

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO users(full_name, email, password, role)
    VALUES(%s, %s, %s, %s)
    """

    cursor.execute(sql, (
        full_name,
        email,
        hashed_password,
        role
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "User Registered Successfully"
    })


@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    """
    SELECT
        u.user_id,
        u.full_name,
        u.email,
        u.password,
        u.role,
        c.candidate_id
    FROM users u
    LEFT JOIN candidates c
        ON u.user_id = c.user_id
    WHERE u.email=%s
    """,
    (email,)
)

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return jsonify({
            "message": "User not found"
        }), 404

    if bcrypt.check_password_hash(user["password"], password):

        return jsonify({
    "message": "Login Successful",
    "user_id": user["user_id"],
    "candidate_id": user["candidate_id"],
    "full_name": user["full_name"],
    "email": user["email"],
    "role": user["role"]
})

    return jsonify({
        "message": "user not found"
    }), 401
    