# Could use moving to different files, but i'm unsure where to
from models.student import Student
from flask import redirect, request


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
