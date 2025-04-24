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
    courses=db.relationship("Courses",backref="student",secondary="enrollments")

class Courses(db.Model):
     courses={'course_1': 1,'course_1': 2,'course_1': 3,'course_1': 4}
     course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     course_code=db.Column(db.String(25),nullable=False,unique=True)
     course_name=db.Column(db.String(),nullable=False)
     course_description=db.Column(db.String())
class Enrollments(db.Model):
     enrollment_id=db.Column(db.Integer,primary_key=True)
     estudent_id=db.Column(db.Integer,db.ForeignKey(Student.student_id),nullable=False,autoincrement=True)
     ecourse_id=db.Column(db.Integer,db.ForeignKey(Courses.course_id),nullable=False)


#app.app_context().push()
with app.app_context():
    db.create_all()

@app.route("/")
def index():
     all_std=Student.query.all()
     print(all_std)
     return render_template("index.html",all_std=all_std)

@app.route("/student/create",methods=['GET','POST'])
def add_student():
    if request.method=="GET":
        return render_template("add_student.html")
    if request.method=="POST":
        roll=request.form.get('roll')
        s=Student.query.filter_by(roll_number=roll).first()
        if s:
            return render_template('already.html')
        else:
            f_name=request.form.get('f_name')
            l_name=request.form.get('l_name')
            courses =request.form.getlist('courses')
            new_s=Student(roll_number=roll,first_name=f_name,last_name=l_name)
            db.session.add(new_s)
            db.session.commit()
            for course in courses:
                s_id=new_s.student_id
                new_e=Enrollments(estudent_id=s_id,ecourse_id=int(course))
                db.session.add(new_e)
                db.session.commit()

        return redirect("/")
@app.route('/student/<int:student>/update',methods=['GET','POST'])
def up_add(student):
    to_update=Student.query.filter_by(student_id=student).first()
    if request.method=='GET':
        return render_template('update_s.html',to_updt=to_update)
    if request.method=='POST':
        f_name=request.form.get('f_name')
        l_name=request.form.get('l_name')
        courses =request.form.getlist('courses')
        to_update.first_name=f_name
        to_update.last_name=l_name
        to_update.courses=[]
        db.session.commit()
        for course in courses:
            s_id=to_update.student_id
            new_e=Enrollments(estudent_id=s_id,ecourse_id=int(course))
            db.session.add(new_e)
            db.session.commit()
        return redirect("/")
    
@app.route('/student/<int:s>/delete')
def Del(s):
    to_delete=Student.query.get(s)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect("/")

@app.route('/student/<int:s>')
def details(s):
    infor=Student.query.get(s)
    his_courses=infor.courses
    print(his_courses)
    return render_template("student_courses.html",infor=infor,his_courses=his_courses)




          


app.run(debug=True)
