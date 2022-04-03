# from database.mongoDB import mongo
from database.mongoDB import db


class Student(db.Document):
    student_number = db.IntField(required=True)
    name = db.StringField(required=True)
    credits = db.IntField()
    degree = db.StringField()

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
