from flask import Flask
from flask_bcrypt import Bcrypt
from routes.auth import auth
from routes.candidate import candidate
from routes.resume import resume
from routes.jobs import jobs
from flask_cors import CORS

app = Flask(__name__)

bcrypt = Bcrypt(app)
CORS(app)

app.register_blueprint(auth)
app.register_blueprint(candidate)
app.register_blueprint(resume)
app.register_blueprint(jobs)

@app.route("/")
def home():
    return "TalentBridge AI Backend Running Successfully"

@app.route("/test")
def test():
    return "Login backend route test"

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)