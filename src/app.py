from flask import Flask
from routes.studentRoutes import studentRoutes
from database.mongoDB import initialize_db
from data.studentsStrings import studentDict
from models.student import Student
from controllers.studentController import ResetDatabase

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {
    "db": "student_db",
    "host": "localhost",
    "port": 27017
}
# app.config.from_object('config')
initialize_db(app)
ResetDatabase(Student, studentDict, True)
app.register_blueprint(studentRoutes)


if __name__ == '__main__':
    app.run(debug=True)
