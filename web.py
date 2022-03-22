from flask import Flask, jsonify, render_template, request
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


@app.route("/", methods=["GET"])
def MainPage():
    return render_template("index.html", students=allStudents)


@app.route("/add", methods=["GET"])
def ShowForm(message=""):
    return render_template("addStudentForm.html", message=message)


@app.route("/students", methods=["POST"])
def StudentsData():
    def render(message):
        return ShowForm(
            message=message,
        )

    # It seems to run with the last forms data if you refresh the page
    message = ""
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
    for list in allStudents:
        for key in list:
            formData[key] = request.form.get(key)
            if formData[key] == "":
                message = "Please fill out all the fields"
                return render(message)
            # Check the string if it is a number
            if typeChecks[key] == int:
                try:
                    -
                    int(formData[key])
                except ValueError:
                    message = "Please enter a number for " + key
                    return render(message)
                else:
                    formData[key] = int(formData[key])
            # Use isistance() to check types
            if not isinstance(formData[key], typeChecks[key]):
                message = key + " cannot be a " + \
                    str(type(formData[key]))
                return render(message)
            # if formData[key] == list[key]:
            #     message = "Student already exists"
            #     return render(message)
    newStudent = {
        "student_number": int(formData["student_number"]),
        "name": formData["name"],
        "credits": int(formData["credits"]),
        "degree": formData["degree"]
    }
    allStudents.append(newStudent)
    message = "Student added!"
    return render(message)


@ app.route("/students/<degree>", methods=["GET"])
def StudentsDegree(degree):
    output = []
    for student in allStudents:
        if student["degree"] == degree:
            output.append(student)
    return jsonify(output)


@ app.route("/students/<StudentID>", methods=["PUT", "PATCH", "DELETE"])
def ReplaceStudent(StudentID):
    if request.method != "PUT" and request.method != "PATCH" \
            and request.method != "DELETE":
        return (
            {"message": "Only PUT or PATCH or DELETE requests are allowed"},
            405
        )

    if not request.is_json:
        return ({"message": "Request must be JSON"}, 400)

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
                or request.json["student_number"] == student["student_number"]:
            if request.method == "PUT":
                allStudents[iterator] = request.json
                return ({"message": "Student replaced"}, 200)
            # Not necessary but makes it more readable
            if request.method == "PATCH":
                allStudents[iterator].update(request.json)
                return ({"message": "Collection updated"}, 200)
            if request.method == "DELETE":
                allStudents.pop(iterator)
                return ({"message": "Student deleted"}, 200)
        iterator += 1
    if request.method == "DELETE":
        return ({"message": "Student not found"}, 404)
    allStudents.insert(0, request.json)
    return ({"message": "Collection created"}, 201)


if __name__ == '__main__':
    app.run(debug=True)
