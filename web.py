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
    return render_template("index.html")


@app.route("/students", methods=["GET", "POST"])
def StudentsData():
    def render(message):
        return render_template("index.html", message=message)

    # It seems to run with the last forms data if you refresh the page
    message = ""
    typeChecks = {
        "student_number": int,
        "name": str,
        "credits": int,
        "degree": str
    }
    # Meant for direct requests
    if request.method == "GET":
        return jsonify(allStudents)
    else:
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
        return jsonify(allStudents)


@app.route("/students/<degree>", methods=["GET"])
def StudentsDegree(degree):
    output = []
    for student in allStudents:
        if student["degree"] == degree:
            output.append(student)
    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
