from flask import Flask,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api,fields,marshal_with,reqparse
from werkzeug.exceptions import HTTPException
import json

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///api_database.sqlite3'
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()
api=Api(app)

class Student(db.Model):
    __tablename__='student'
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String(),nullable=False,unique=True)
    first_name=db.Column(db.String(),nullable=False)
    last_name=db.Column(db.String())
    course=db.relationship("Course",backref='student',secondary='enrollment',cascade='all,delete')

class Course(db.Model):
    __tablename__='course'
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code=db.Column(db.String(25),nullable=False,unique=True)
    course_name=db.Column(db.String(),nullable=False)
    course_description=db.Column(db.String())


class Enrollment(db.Model):
    __tablename__='enrollment'
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_id=db.Column(db.Integer,db.ForeignKey(Student.student_id),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey(Course.course_id),nullable=False)

#with app.app_context():
    #db.create_all()

class FoundError(HTTPException):
    def __init__(self,status_code,message=''):
        self.response=make_response(message,status_code)
    
class NotGivenError(HTTPException):
    def __init__(self,status_code,error_code,error_message):
        message=({"error_code":error_code,"error_message":error_message})
        self.response=make_response(status_code,json.dumps(message))

#output fields
student_fields={
    "student_id":fields.Integer,
    "first_name":fields.String,
    "last_name":fields.String,
    "roll_number":fields.String

}

course_fields={
    "course_id":fields.Integer,
    "course_name":fields.String,
    "course_code":fields.String,
    "course_description":fields.String

}

# parsers

course_parse=reqparse.RequestParser()
course_parse.add_argument("course_name")
course_parse.add_argument("course_code")
course_parse.add_argument("course_description")


student_parse=reqparse.RequestParser()
student_parse.add_argument("first_name")
student_parse.add_argument("last_name")
student_parse.add_argument("roll_number")

enrollment_parse=reqparse.RequestParser()
enrollment_parse.add_argument("course_id")

class CourseApi(Resource):
    @marshal_with(course_fields)
    def get(self,course_id):
        course=Course.query.filter(Course.course_id==course_id).first()
        if course:
            return course
        else:
            raise FoundError(status_code=404)
        
    @marshal_with(course_fields)
    def post(self):
        args=course_parse.parse_args()
        course_name=args.get("course_name",None)
        course_code=args.get("course_code",None)
        course_description=args.get("course_description",None)
        if course_name is None:
            raise NotGivenError(status_code=400,error_code="COURSEOO1",error_message='Course Name is required')
        if course_code is None:
            raise NotGivenError(status_code=400,error_code="COURSE002",error_message='Course Code is required')
        
        course=Course.query.filter(Course.course_code==course_code).first()
        if course is None:
            course=Course(course_name=course_name,course_code=course_code,course_description=course_description)
            db.session.add(course)
            db.session.commit()
            return course,201
        else:
            raise FoundError(status_code=409)
        
    @marshal_with(course_fields)
    def put(self,course_id):
        course=Course.query.filter(Course.course_id==course_id).first()
        if course is None:
            raise FoundError(status_code=404)
        args=course_parse.parse_args()
        course_name=args.get("course_name",None)
        course_code=args.get("course_code",None)
        course_description=args.get("course_description",None)
        if course_name is None:
            raise NotGivenError(status_code=400,error_code="COURSEOO1",error_message='Course Name is required')
        if course_code is None:
            raise NotGivenError(status_code=400,error_code="COURSE002",error_message='Course Code is required')
        
        else:
            course.course_name=course_name
            course.course_code=course_code
            course.course_description=course_description
            db.session.add(course)
            db.session.commit()
            return course
        

    def delete(self,course_id):
        course=Course.query.filter(Course.course_id==course_id).scalar()
        if course is None:
            raise FoundError(status_code=404)
        db.session.delete(course)
        db.session.commit()
        return "",200

class StudentAPI(Resource):
    @marshal_with(student_fields)
    def get(self,student_id):
        student=Student.query.filter(Student.student_id==student_id).first()
        if student:
            return student
        else:
            raise FoundError(status_code=404)
    
    @marshal_with(student_fields)
    def post(self):
        args=student_parse.parse_args()
        first_name=args.get('first_name',None)
        last_name=args.get('last_name',None)
        roll_number=args.get('roll_number',None)
        if roll_number is None:
            raise NotGivenError(status_code=400,error_code="STUDENT001",error_message="Roll Number is required")
        if first_name is None:
            raise NotGivenError(status_code=400,error_code="STUDENT002",error_message="First Name is required")
        student=Student.query.filter(Student.roll_number==roll_number).first()
        if student is None:
            student=Student(first_name=first_name,last_name=last_name,roll_number=roll_number)
            db.session.add(student)
            db.session.commit()
            return student,201
        else:
            raise FoundError(status_code=409)
    

    @marshal_with(student_fields)
    def put(self,student_id):
        student=Student.query.filter(Student.student_id==student_id).first()
        if student is None:
            raise FoundError(status_code=404)
        args=student_parse.parse_args()
        first_name=args.get('first_name',None)
        last_name=args.get('last_name',None)
        roll_number=args.get('roll_number',None)
        if roll_number is None:
            raise NotGivenError(status_code=400,error_code="STUDENT001",error_message='Roll Number is required')
        elif first_name is None:
            raise NotGivenError(status_code=400,error_code="STUDENT002",error_message='First Name is required')
        else:
            student.first_name=first_name
            student.last_name=last_name
            student.roll_number=roll_number
            db.session.add(student)
            db.session.commit()
            return student

        

    def delete(self,student_id):
        student=Student.query.filter(Student.student_id==student_id).scalar()
        if student is None:
            raise FoundError(status_code=404)
        db.session.delete(student)
        db.session.commit()
        return "",200
        

class EnrollmentAPI(Resource):
    def get(self,student_id):
        student=Student.query.filter(Student.student_id==student_id).first()
        if student is None:
            raise NotGivenError(status_code=400,error_code='ENROLLMENT002',error_message='Student does not exist')
        enrollments=Enrollment.query.filter(Enrollment.student_id==student_id).all()
        if enrollments:
            enrolls=[]
            for enrollment in enrollments:
                enrolls.append({"enrollment_id":enrollment.enrollment_id,"student_id":enrollment.student_id,"course_id":enrollment.course_id})
            return enrolls
        else:
            raise FoundError(status_code=404)

    def delete(self,student_id,course_id):
        course=Course.query.filter(Course.course_id==course_id).first()
        if course is None:
            raise NotGivenError(status_code=400,error_code='ENROLLMENT001',error_message='Course does not exist')
        student=Student.query.filter(Student.student_id == student_id).first()
        if student is None:
            raise NotGivenError(status_code=400,error_code='ENROLLMENT002',error_message='Student does not exist')
        enrollments=Enrollment.query.filter(Enrollment.student_id ==student_id).all()
        if enrollments:
            for enroll in enrollments:
                if enroll.course_id==course_id:
                    db.session.delete(enroll)
            db.session.commit()
        else:
            raise FoundError(status_code=404)
        
    def post(self,student_id):
        student=Student.query.filter(Student.student_id==student_id).first()
        if student:
            args=enrollment_parse.parse_args()
            course_id=args.get("course_id",None)
            course=Course.query.filter(Course.course_id==course_id).first()
            if course:
                enroll=Enrollment(student_id=student_id,course_id=course_id)
                db.session.add(enroll)
                db.session.commit()
            else:
                raise NotGivenError(status_code=400,error_code='ENROLLMENT002',error_message='Student does not exist')
            
            return [{"enrollment_id":enroll.enrollment_id,"student_id":enroll.student_id,"course_id":enroll.course_id}], 201
        else:
            raise FoundError(status_code=404)








api.add_resource(CourseApi,"/api/course/<int:course_id>","/api/course")
api.add_resource(StudentAPI,"/api/student/<int:student_id>","/api/student")
api.add_resource(EnrollmentAPI, "/api/student/<int:student_id>/course","/api/student/<int:student_id>/course/<int:course_id>")
#api.add_resource(EnrollmentAPI, "/api/student/<int:student_id>/course/<int:course_id>")

app.run(debug=True)