from flask import Flask
from routes.studentRoutes import studentRoutes
from database.mongoDB import initialize_db

app = Flask(__name__)

app.config.from_object('config')
initialize_db(app)
print(" * Database Initialized")
app.register_blueprint(studentRoutes)


if __name__ == '__main__':
    app.run(debug=True)
