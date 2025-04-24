from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy # type: ignore


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

db=SQLAlchemy(app)

class Student(db.Model):
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String(),nullable=False,unique=True)
    first_name=db.Column(db.String(),nullable=False)
    last_name=db.Column(db.String())
    #courses=db.relationship("Course",backref="student",secondary="enrollments")

class Course(db.Model):
     courses={'course_1': 1,'course_2': 2,'course_3': 3,'course_4': 4}
     course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     course_code=db.Column(db.String(25),nullable=False,unique=True)
     course_name=db.Column(db.String(),nullable=False)
     course_description=db.Column(db.String())
class Enrollments(db.Model):
     enrollment_id=db.Column(db.Integer,primary_key=True)
     estudent_id=db.Column(db.Integer,db.ForeignKey(Student.student_id),nullable=False,autoincrement=True)
     ecourse_id=db.Column(db.Integer,db.ForeignKey(Course.course_id),nullable=False)


app.app_context().push()
#with app.app_context():
db.create_all()

@app.route("/")
def index():
     all_std=Student.query.all()
     print(all_std)
     return render_template("index.html",all_std=all_std)

@app.route("/student/create",methods=['GET','POST'])
def add():
     if request.method=='GET':
          return render_template('add_student.html')
     elif request.method=='POST':
          roll_number=request.form['roll']
          first_name=request.form['f_name']
          last_name=request.form['l_name']
          scourses=request.form['courses']
          exist=Student.query.filter_by(roll_number=roll_number).first()
          if exist is None:
               db.session.add(Student(roll_number=roll_number,first_name=first_name,last_name=last_name))
               db.session.commit()
               courses=request.form.getlist('courses')
               for course in courses:
                    db.session.add(Enrollments(estudent_id=Student.query.filter_by(roll_number=request.form['roll']).first().student_id,ecourse_id=Course.courses[course]))
                    db.session.commit()
               return redirect('/')
          return render_template('already.html')
@app.route('/student/<int:student_id>/delete',methods=['GET','POST'])
def delete(student_id):
     Student.query.filter_by(student_id=student_id).delete()
     Enrollments.query.filter_by(estudent_id=student_id)
     db.session.commit()
     return redirect('/')


@app.route('/student/<int:student_id>/',methods=['GET','POST'])
def view(student_id):
     detail_s=Student.query.filter_by(student_id=student_id).first()
     enrollments=Enrollments.query.filter_by(estudent_id=student_id).all()
     courses=[]
     for enrollment in enrollments:
          course=Course.query.filter_by(course_id=enrollment.ecourse_id).first()
          if course:
               courses.append(course)
     return render_template('about.html',courses=courses,student=detail_s)

@app.route('/student/<int:student_id>/update',methods=['GET','POST'])
def update(student_id):
     if request.method=='GET':
          row=Student.query.filter_by(student_id=student_id).first()
          enrolls=Enrollments.query.filter_by(estudent_id=student_id).all()
          cid=[enroll.ecourse_id for enroll in enrolls]
          return render_template('update_s.html',row=row,cid=cid)
     elif request.method=='POST':
          stu=Student.query.filter_by(student_id=student_id).first()
          stu.first_name=request.form['f_name']
          stu.last_name=request.form['l_name']
          Enrollments.query.filter_by(estudent_id=student_id).delete()
          for course in request.form.getlist('courses'):
               db.session.add(Enrollments(estudent_id=student_id,ecourse_id=Course.courses[course]))
          db.session.commit()
          return redirect('/')
app.run(debug=True)