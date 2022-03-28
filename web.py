from flask import Flask, jsonify, render_template, request, redirect
allStudents = [
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
app = Flask(__name__)
# Global message because I haven't found a better way to do this
headerMessage = ''


@app.route('/')
def RedirectHome(status=302):
    return redirect('/home', code=status)


@app.route("/home", methods=["GET"])
def MainPage():
    localVarMessage = GetGlobalMessage()
    return render_template(
        "home.html",
        message=localVarMessage,
        students=allStudents
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
        allStudents.append(request.json)
        return "Student added!", 200
    # Check if the form has all entries in AllStudents
    # Caching data so we can modify it
    formData = {}
    for entry in request.form:
        formData[entry] = request.form.get(entry)
    for list in allStudents:
        for key in list:
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
            if key == "student_number" and formData[key] == list[key]:
                # Replace if existing
                allStudents[allStudents.index(list)] = formData
                return "Existing student replaced!", 200
    newStudent = {
        "student_number": int(formData["student_number"]),
        "name": formData["name"],
        "credits": int(formData["credits"]),
        "degree": formData["degree"]
    }
    allStudents.append(newStudent)
    return "Student added!", 200


@ app.route("/students/degree/<degree>", methods=["GET"])
def StudentsDegree(degree):
    output = []
    for student in allStudents:
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
    for student in allStudents:
        if student["student_number"] == StudentID \
                or request.json and \
                request.json["student_number"] == student["student_number"]:

            if method == "PUT":
                allStudents[iterator] = request.json
                return ({"message": "Student replaced"}, 200)
            # Not necessary but makes it more readable
            if method == "PATCH":
                allStudents[iterator].update(request.json)
                return ({"message": "Collection updated"}, 200)
            if method == "DELETE":
                allStudents.pop(iterator)
                return ({"message": "Student deleted"}, 200)
        iterator += 1
    if method == "DELETE":
        return ({"message": "Student not found"}, 404)
    allStudents.insert(0, request.json)
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
            for students in allStudents:
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
    if response[1] != 200:
        return False
    return redirect('/home', code=302)


if __name__ == '__main__':
    app.run(debug=True)
