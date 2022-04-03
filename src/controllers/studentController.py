# Could use moving to different files, but i'm unsure where to
from models.student import Student
from flask import abort, redirect, render_template, request


headerMessage = ''


def GetMessage():
    global headerMessage
    localVarMessage = headerMessage
    headerMessage = ''
    return localVarMessage


def SetHeaderMessage(message=''):
    global headerMessage
    headerMessage = message


def RedirectStudentTable():
    return redirect('/home')


def ShowStudentTable():
    # return jsonify(GetAllStudents())
    return render_template(
        "home.html",
        message=GetMessage(),
        students=GetAllStudents()
    )


def ShowAddStudentForm():
    if request.method == 'GET':
        return render_template('form.html')
    if request.method == 'POST':
        output = HandleFormData(request)
        SetHeaderMessage(output[0])
        return ShowStudentTable()
    return abort(404)


def GetGlobalMessage():
    localVarMessage = ''
    global headerMessage
    if headerMessage != '':
        localVarMessage = headerMessage
        headerMessage = ''
    return localVarMessage


def HandleFormData(request):
    # It seems to run with the last forms data if you refresh the page
    typeChecks = {
        "student_number": int,
        "name": str,
        "credits": int,
        "degree": str
    }
    # Meant for direct requests
    if request.is_json:
        JSONParse(request.json, AddStudent)
        return "StudentHandler added!", 200
    # Check if the form has all entries in AllStudents
    # Caching data so we can modify it
    formData = {}
    for entry in request.form:
        formData[entry] = request.form.get(entry)
    studentList = GetAllStudents()
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
                if UpdateStudent(formData):
                    return "Existing student replaced!", 200
                return "Failed to replace existing student!", 400
    JSONParse(formData, AddStudent)
    return "Student added!", 200


def ReplaceStudent(StudentID, argMethod=False):
    method = request.method
    if argMethod:
        method = argMethod
    if not argMethod and method != "PUT" \
        and method != "PATCH" \
            and method != "DELETE" and method != "POST":
        return (
            {
                "message": "Only GET, POST, PUT, PATCH, DELETE \
                    requests are allowed"
            },
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
    studentList = GetAllStudents()
    for student in studentList:
        if student["student_number"] == StudentID \
                or request.json and \
                request.json["student_number"] == student["student_number"]:
            if method == "PUT" or method == "PATCH":
                if JSONParse(
                        request.json,
                        UpdateStudent):
                    return ({"message": "Student replaced"}, 200)
                return ({"message": "Failed to replace student"}, 400)
            if method == "DELETE":
                if RemoveStudentWithClass(student):
                    return ({"message": "Student deleted"}, 200)
                return ({"message": "Failed to delete student"}, 400)
        iterator += 1
    if method == "DELETE":
        return ({"message": "Student not found"}, 404)
    JSONParse(request.json, UpdateStudent)
    return ({"message": "Student added"}, 201)


def ModifyStudentForm(student_number):
    student = {}

    def render():
        return render_template(
            "form.html",
            message=GetMessage(),
            student=student,
            target="/edit/" + str(student_number),
        )

    if request.method == "GET":
        if student_number:
            studentList = GetAllStudents()
            for students in studentList:
                if students["student_number"] == int(student_number):
                    student = students
        if GetMessage() == "":
            SetHeaderMessage("Modify Student: " + student["name"])
        return render()
    if request.method == "POST" or request.method == "PUT" \
            or request.method == "PATCH":
        result = HandleFormData(request)
        SetHeaderMessage(result[0])
        if result[1] == 200:
            return redirect("/home")
    return render()


def DeleteStudent(student_number):
    ReplaceStudent(student_number, "DELETE")
    return redirect("/home")


def GetAllStudents():
    return Student.objects()


def GetStudent(student_number):
    # Get the first student with the student number
    student = Student.objects(student_number=student_number).first()
    if student is not None:
        return student
    return False


def AddStudent(student):
    student.save()
    return ('Student added successfully!', 200)


def RemoveStudentWithNum(student_number):
    student = Student.objects(student_number=student_number).first()
    if student is not None:
        student.delete()
        return ('Student removed successfully!', 200)
    return ('Student not found', 404)


def RemoveStudentWithClass(student):
    return RemoveStudentWithNum(student["student_number"])


def UpdateStudent(student):
    students = Student.objects(student_number=student["student_number"])
    if students is not None:
        try:
            students.update(
                student_number=student["student_number"],
                name=student["name"],
                credits=student["credits"],
                degree=student["degree"]
            )
            return ('Student updated successfully!', 200)
        except ValueError:
            return ('Invalid data supplied', 400)
    return ('Student not found', 404)


def JSONParse(input, callback):
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
        return ('Invalid data supplied', 400)


# Can't be in the database folder due to circular imports
def ResetDatabase(document, dataToAdd, resetDatabase):
    if resetDatabase:
        print("Resetting database")
        document.drop_collection()
    # Delete all students in MongoDB
    print('Adding initial students')
    for student in dataToAdd:
        JSONParse(student, AddStudent)
