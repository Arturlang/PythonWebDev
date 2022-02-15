from flask import Flask, jsonify

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
print(type(allStudents))
app = Flask(__name__)


@app.route("/")
def main():
    return "Welcome to the REST API"


@app.route("/students")
def students():
    output = jsonify(allStudents)
    return output


@app.route("/students/<degree>")
def students_degree(degree):
    output = []
    for student in allStudents:
        if student["degree"] == degree:
            output.append(student)
    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
