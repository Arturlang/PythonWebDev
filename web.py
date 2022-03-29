from flask import Flask, jsonify, render_template, request, redirect
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {
    "db": "student_db",
    "host": "localhost",
    "port": 27017
}
db = MongoEngine()
db.init_app(app)


class Student(db.Document):
    student_number = db.IntField(required=True)
    name = db.StringField(required=True)
    credits = db.IntField()
    degree = db.StringField()
    # Document does not like _init being overridden
    # def __init__(self, student_number, name, credits, degree):
    #     self.student_number = student_number
    #     self.name = name
    #     self.credits = credits
    #     self.degree = degree

    def __iter__(self):
        return iter(
            {
                "student_number": self.student_number,
                "name": self.name,
                "credits": self.credits,
                "degree": self.degree
            }
        )

    def __getitem__(self, item):
        return getattr(self, item)


class StudentHandler:
    def GetAllStudents(self):
        return Student.objects()

    def GetStudent(self, student_number):
        # Get the first student with the student number
        student = Student.objects(student_number=student_number).first()
        if student is not None:
            return student
        return None

    def AddStudent(self, student):
        student.save()

    def RemoveStudentWithNum(self, student_number):
        student = Student.objects(student_number=student_number).first()
        if student is not None:
            student.delete()
            return True
        return False

    def RemoveStudentWithClass(self, student):
        return self.RemoveStudentWithNum(student["student_number"])

    def UpdateStudent(self, student):
        students = Student.objects(student_number=student["student_number"])
        if students is not None:
            try:
                students.update(
                    student_number=student["student_number"],
                    name=student["name"],
                    credits=student["credits"],
                    degree=student["degree"]
                )
                return True
            except ValueError:
                return False
        return False

    def JSONParse(self, input, callback):
        student = None
        try:
            student = Student(
                student_number=input["student_number"],
                name=input["name"],
                credits=input["credits"],
                degree=input["degree"]
            )
            return callback(student)
        except ValueError:
            return jsonify({"error": "Invalid JSON"})


def ResetDatabase(data, resetDatabase):
    if resetDatabase:
        print("Resetting database")
        Student.drop_collection()
    # Delete all students in MongoDB
    global allStudents
    print('Adding initial students')
    for student in data:
        allStudents.JSONParse(student, allStudents.AddStudent)
    # allStudents.AddStudent(Student("Alice Brown", 123123, 130, "it"))
    # allStudents.AddStudent(Student("Bob Jones", 111222, 157, "it"))
    # allStudents.AddStudent(Student("Richard Brown", 333444, 57, "machine"))


studentDict = [
    {
        "student_number": 123123,
        "name": "Alice Brown",
                "credits": 130,
                "degree": "it"
    },
    {
        "student_number": 111222,
        "name": "Bob Jones",
                "credits": 157,
                "degree": "it"
    },
    {
        "student_number": 333444,
        "name": "Richard Brown",
                "credits": 57,
                "degree": "machine"
    }
]

# Global message because I haven't found a better way to do this
headerMessage = ''
allStudents = StudentHandler()
resetDatabase = False
if resetDatabase:
    ResetDatabase(studentDict, True)


@app.route('/')
def RedirectHome(status=302):
    return redirect('/home', code=status)


@app.route("/home", methods=["GET"])
def MainPage():
    localVarMessage = GetGlobalMessage()
    return render_template(
        "home.html",
        message=localVarMessage,
        students=allStudents.GetAllStudents()
    )


def GetGlobalMessage():
    localVarMessage = ''
    global headerMessage
    if headerMessage != '':
        localVarMessage = headerMessage
        headerMessage = ''
    return localVarMessage


@app.route("/add/<studentID>", methods=["GET"])
def AddStudentFormWithID(studentID):
    student = {
        "student_number": int(studentID),
    }
    return ModifyStudent(student, "Add the student!")
    # return render_template("form.html", message=headerMessage,
    # student=student, target=)


@app.route("/add", methods=["GET"])
def AddStudentForm():
    return ModifyStudent({}, "Add the student!")


@app.route("/students", methods=["POST"])
def AddStudent(request):
    headerMessage = GetFormData(request)
    return GetFormData(msg=headerMessage[0])


def GetFormData(request):
    # It seems to run with the last forms data if you refresh the page
    typeChecks = {
        "student_number": int,
        "name": str,
        "credits": int,
        "degree": str
    }
    # Meant for direct requests

    if request.is_json:
        allStudents.JSONParse(request.json, allStudents.AddStudent)
        return "Student added!", 200
    # Check if the form has all entries in AllStudents
    # Caching data so we can modify it
    formData = {}
    for entry in request.form:
        formData[entry] = request.form.get(entry)
    studentList = allStudents.GetAllStudents()
    for student in studentList:
        for key in student:
            for objectKey in typeChecks:
                if objectKey not in formData:
                    return "Missing object key", 400
            if formData[key] == "":
                return "Please fill out all the fields!", 400
            # Check the string if it is a number
            if typeChecks[key] == int:
                try:
                    int(formData[key])
                except ValueError:
                    return "Please enter a number for " + key, 400
                else:
                    formData[key] = int(formData[key])
            # Use isistance() to check types
            if not isinstance(formData[key], typeChecks[key]):
                return key + " cannot be a " + \
                    str(type(formData[key])), 400
            # Check if the student number is unique
            if key == "student_number" and formData[key] == student[key]:
                # Replace if existing
                if allStudents.UpdateStudent(formData):
                    return "Existing student replaced!", 200
                return "Failed to replace existing student!", 400
    allStudents.JSONParse(formData, allStudents.AddStudent)
    return "Student added!", 200


@ app.route("/students/degree/<degree>", methods=["GET"])
def StudentsDegree(degree):
    output = []
    studentList = allStudents.GetAllStudents()
    for student in studentList:
        if student["degree"] == degree:
            output.append(student)
    return jsonify(output)


@ app.route("/backend/modifyStudent/<StudentID>",
            methods=["PUT", "PATCH", "DELETE"])
def ReplaceStudent(StudentID, argMethod=False):
    method = request.method
    if argMethod:
        method = argMethod
    if not argMethod and method != "PUT" \
        and method != "PATCH" \
            and method != "DELETE":
        return (
            {"message": "Only GET, PUT, PATCH, DELETE requests are allowed"},
            405
        )

    # if not request.is_json:
    #     return ({"message": "Request must be JSON"}, 400)

    try:
        StudentID = int(StudentID)
    except ValueError:
        return (
            {"message": "The field after /students/ has to be a number"}, 400
        )
    # Replace the student with the same ID with data from request
    iterator = 0
    studentList = allStudents.GetAllStudents()
    for student in studentList:
        if student["student_number"] == StudentID \
                or request.json and \
                request.json["student_number"] == student["student_number"]:
            if method == "PUT" or method == "PATCH":
                if allStudents.JSONParse(
                        request.json,
                        allStudents.UpdateStudent):
                    return ({"message": "Student replaced"}, 200)
                return ({"message": "Failed to replace student"}, 400)
            if method == "DELETE":
                if allStudents.RemoveStudentWithClass(student):
                    return ({"message": "Student deleted"}, 200)
                return ({"message": "Failed to delete student"}, 400)
        iterator += 1
    if method == "DELETE":
        return ({"message": "Student not found"}, 404)
    allStudents.JSONParse(request.json, allStudents.UpdateStudent)
    return ({"message": "Student added"}, 201)


@app.route('/students/<studentID>/<delete>', methods=["GET"])
def HandleButtonHREFGet(studentID, delete):
    if request.method != "GET":
        # Shouldn't be possible to get here using the UI
        return (
            {"message": "Only GET requests are allowed"}, 405
        )
    if(delete == "delete"):
        result = ReplaceStudent(studentID, "DELETE")
        global headerMessage
        headerMessage = result[0]["message"]
        return redirect("/home", code=302)
    else:
        return redirect('/students/modify/' + studentID, code=302)


@app.route('/students/modify/<studentID>')
def ModifyStudent(studentID, msg=""):
    infoMessage = msg
    student = {}

    def render():
        return render_template(
            "form.html",
            message=infoMessage,
            student=student,
            target="/students/getFormData/"
        )

    if request.method == "GET":
        if studentID:
            studentList = allStudents.GetAllStudents()
            for students in studentList:
                if students["student_number"] == int(studentID):
                    student = students
        if not infoMessage or infoMessage == "":
            infoMessage = "Modify Student: " + student["name"]
        return render()


@app.route('/students/getFormData/', methods=["POST", "GET"])
def HandleReplaceForm():
    # print(request.form)
    response = GetFormData(request)
    global headerMessage
    headerMessage = response[0]
    return redirect('/home', code=302)


if __name__ == '__main__':
    app.run(debug=True)
