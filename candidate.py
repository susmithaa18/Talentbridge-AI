from flask import Blueprint, request, jsonify
from database import get_connection

candidate = Blueprint("candidate", __name__)


@candidate.route("/profile", methods=["POST"])
def create_profile():

    data = request.get_json()

    user_id = data["user_id"]
    phone = data["phone"]
    education = data["education"]
    experience = data["experience"]
    skills = data["skills"]
    projects = data["projects"]
    certifications = data["certifications"]
    resume_path = data["resume_path"]

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO candidates
    (user_id, phone, education, experience, skills, projects, certifications, resume_path)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        user_id,
        phone,
        education,
        experience,
        skills,
        projects,
        certifications,
        resume_path
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Candidate Profile Created Successfully"})