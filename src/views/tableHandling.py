from flask import redirect, render_template, request, abort
from controllers.studentController import AddStudent, UpdateStudent, \
    GetAllStudents, JSONParse


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
