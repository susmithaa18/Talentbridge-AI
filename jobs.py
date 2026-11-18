from flask import Blueprint, request, jsonify
from database import get_connection

jobs = Blueprint("jobs", __name__)

@jobs.route("/add_job", methods=["POST"])
def add_job():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO jobs
    (job_title, company_name, job_description,
     required_skills, experience_required,
     location, salary)
    VALUES(%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        data["job_title"],
        data["company_name"],
        data["job_description"],
        data["required_skills"],
        data["experience_required"],
        data["location"],
        data["salary"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Job Added Successfully"
    })

@jobs.route("/get_jobs", methods=["GET"])
def get_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")

    all_jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(all_jobs)

@jobs.route("/apply_job", methods=["POST"])
def apply_job():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO applications
    (candidate_id, job_id)
    VALUES (%s, %s)
    """

    cursor.execute(sql, (
        data["candidate_id"],
        data["job_id"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Job Applied Successfully"
    })

@jobs.route("/my_applications/<int:candidate_id>", methods=["GET"])
def my_applications(candidate_id):
    conn = get_connection()

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        sql = """
            SELECT
                a.application_id,
                a.candidate_id,
                a.job_id,
                j.job_title,
                j.company_name,
                a.application_status,
                a.applied_at
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.candidate_id = %s
            ORDER BY a.application_id DESC
        """

        cursor.execute(sql, (candidate_id,))
        applications = cursor.fetchall()

        return jsonify(applications)

    except Exception as e:
        print("My applications error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


@jobs.route("/schedule_interview", methods=["POST"])
def schedule_interview():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO interview_schedule
    (candidate_id, job_id, interview_date,
     interview_time, interview_mode, interview_status)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        data["candidate_id"],
        data["job_id"],
        data["interview_date"],
        data["interview_time"],
        data["interview_mode"],
        "Scheduled"
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Interview Scheduled Successfully"
    })

@jobs.route("/my_interviews/<int:candidate_id>", methods=["GET"])
def my_interviews(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        i.interview_id,
        j.job_title,
        j.company_name,
        i.interview_date,
        i.interview_time,
        i.interview_mode,
        i.interview_status
    FROM interview_schedule i
    JOIN jobs j
        ON i.job_id = j.job_id
    WHERE i.candidate_id = %s
    ORDER BY i.interview_date
    """

    cursor.execute(sql, (candidate_id,))
    interviews = cursor.fetchall()

    for interview in interviews:
        if interview["interview_time"]:
            interview["interview_time"] = str(interview["interview_time"])

    cursor.close()
    conn.close()

    return jsonify(interviews)



# UPDATE JOB
@jobs.route("/update_job", methods=["PUT"])
def update_job():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE jobs
    SET job_title=%s,
        company_name=%s,
        location=%s,
        salary=%s,
        experience_required=%s,
        required_skills=%s,
        job_description=%s
    WHERE job_id=%s
    """

    cursor.execute(sql, (
        data["job_title"],
        data["company_name"],
        data["location"],
        data["salary"],
        data["experience_required"],
        data["required_skills"],
        data["job_description"],
        data["job_id"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Job Updated Successfully"
    })


# DELETE JOB
@jobs.route("/delete_job/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM jobs WHERE job_id=%s",
            (job_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "message": "Job not found"
            }), 404

        return jsonify({
            "message": "Job Deleted Successfully"
        })

    except Exception as e:
        conn.rollback()
        print("Delete job error:", e)

        return jsonify({
            "message": "Cannot delete this job because applications or interviews may be linked to it."
        }), 400

    finally:
        cursor.close()
        conn.close()



@jobs.route("/all_interviews", methods=["GET"])
def all_interviews():

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        i.interview_id,
        i.candidate_id,
        i.job_id,
        u.full_name,
        u.email,
        j.job_title,
        j.company_name,
        i.interview_date,
        i.interview_time,
        i.interview_mode,
        i.interview_status
    FROM interview_schedule i
    JOIN candidates c
        ON i.candidate_id = c.candidate_id
    JOIN users u
        ON c.user_id = u.user_id
    JOIN jobs j
        ON i.job_id = j.job_id
    ORDER BY i.interview_date ASC
    """

    cursor.execute(sql)
    interviews = cursor.fetchall()

    for interview in interviews:
        if interview["interview_time"]:
            interview["interview_time"] = str(
                interview["interview_time"]
            )

    cursor.close()
    conn.close()

    return jsonify(interviews)


# UPDATE INTERVIEW
@jobs.route("/update_interview", methods=["PUT"])
def update_interview():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE interview_schedule
    SET interview_date=%s,
        interview_time=%s,
        interview_mode=%s
    WHERE interview_id=%s
    """

    cursor.execute(sql, (
        data["interview_date"],
        data["interview_time"],
        data["interview_mode"],
        data["interview_id"]
    ))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"message": "Interview not found"}), 404

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Interview Updated Successfully"
    })


# CANCEL INTERVIEW
@jobs.route("/cancel_interview", methods=["PUT"])
def cancel_interview():

    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE interview_schedule
    SET interview_status=%s
    WHERE interview_id=%s
    """

    cursor.execute(sql, (
        "Cancelled",
        data["interview_id"]
    ))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"message": "Interview not found"}), 404

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Interview Cancelled Successfully"
    })


@jobs.route("/all_applications", methods=["GET"])
def all_applications():

    conn = get_connection()

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = conn.cursor()

        sql = """
            SELECT
                a.application_id,
                a.candidate_id,
                a.job_id,
                u.full_name,
                u.email,
                j.job_title,
                j.company_name,
                a.application_status,
                a.applied_at
            FROM applications a
            JOIN candidates c
                ON a.candidate_id = c.candidate_id
            JOIN users u
                ON c.user_id = u.user_id
            JOIN jobs j
                ON a.job_id = j.job_id
            ORDER BY a.application_id DESC
        """

        cursor.execute(sql)

        # Directly fetch dictionary rows
        applications = cursor.fetchall()

        print("APPLICATIONS:", applications)

        return jsonify(applications)

    except Exception as e:
        print("All applications error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        conn.close()


@jobs.route("/update_application_status", methods=["PUT"])
def update_application_status():

    data = request.get_json()

    application_id = data.get("application_id")
    status = data.get("application_status")

    if not application_id or status not in ["Shortlisted", "Rejected"]:
        return jsonify({"error": "Invalid application details"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE applications
            SET application_status = %s
            WHERE application_id = %s
        """, (status, application_id))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Application not found"}), 404

        conn.commit()

        return jsonify({
            "message": "Application status updated successfully",
            "application_status": status
        }), 200

    except Exception as e:
        conn.rollback()
        print("Update status error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()