from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from services.resume_parser import extract_text
from services.skill_extractor import extract_skills
from services.resume_score import calculate_resume_score
from services.job_matcher import match_jobs
from database import get_connection

resume = Blueprint("resume", __name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@resume.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"message": "No file selected"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"message": "Empty file"}), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)
    resume_text = extract_text(filepath)

    print(resume_text)
    resume_text = extract_text(filepath)

    skills = extract_skills(resume_text)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    recommended_jobs = match_jobs(skills, jobs)

    experience = 0
    certifications = 2
    projects = 1

    score = calculate_resume_score(
    skills,
    experience,
    certifications,
    projects
    )

    print("Resume Text:")
    print(resume_text)

    print("Skills Found:")
    print(skills)

    return jsonify({
    "message": "Resume Uploaded Successfully",
    "file_path": filepath,
    "skills": skills,
    "resume_score": score,
    "recommended_jobs": recommended_jobs
})