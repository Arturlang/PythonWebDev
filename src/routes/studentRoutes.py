from flask import Blueprint
from controllers.studentController import DeleteStudent
from views.tableHandling import ShowAddStudentForm, \
    RedirectStudentTable, ShowStudentTable, ModifyStudentForm


studentRoutes = Blueprint('studentRoutes', __name__)
studentRoutes.route('/', methods=['GET'])(RedirectStudentTable)
studentRoutes.route('/home', methods=['GET'])(ShowStudentTable)
studentRoutes.route('/add', methods=['GET', 'POST'])(ShowAddStudentForm)
studentRoutes.route(
    '/edit/<int:student_number>',
    methods=['GET', 'POST']
)(ModifyStudentForm)
studentRoutes.route(
    '/delete/<int:student_number>',
    methods=['GET']
)(DeleteStudent)
