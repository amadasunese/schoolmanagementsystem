from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import date


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    website = db.Column(db.String(100), nullable=True)

    # Relationships
    users = db.relationship('User', backref='school', lazy=True)
    students = db.relationship('Student', backref='school', lazy=True)
    teachers = db.relationship('Teacher', backref='school', lazy=True)
    classes = db.relationship('Class', backref='school', lazy=True)
    subjects = db.relationship('Subject', backref='school', lazy=True)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    enrollment_date = db.Column(db.Date)
    gender = db.Column(db.String(1))
    grade_level = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)


# class Teacher(db.Model):
#     __tablename__ = 'teachers'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     email = db.Column(db.String(100))
#     subject = db.Column(db.String(50))
#     hire_date = db.Column(db.Date)
#     phone_number = db.Column(db.String(15))
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)


# class Teacher(db.Model):
#     __tablename__ = 'teachers'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     email = db.Column(db.String(100))
#     hire_date = db.Column(db.Date)
#     phone_number = db.Column(db.String(15))
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
#     # Relationships
#     subjects = db.relationship('TeacherSubject', backref='teacher', lazy=True)


# class Teacher(db.Model):
#     __tablename__ = 'teachers'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     email = db.Column(db.String(100))
#     hire_date = db.Column(db.Date)
#     phone_number = db.Column(db.String(15))
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
#     # Relationships
#     subjects = db.relationship('TeacherSubject', backref='assigned_teacher', lazy=True)  # Unique backref name



class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    phone_number = db.Column(db.String(15))
    qualification = db.Column(db.String(255))
    address = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo = db.Column(db.String(255))  # Path to the uploaded photo
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    subjects = db.relationship('TeacherSubject', backref='assigned_teacher', lazy=True)

    # Calculate age dynamically
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None



# class Class(db.Model):
#     __tablename__ = 'classes'
#     id = db.Column(db.Integer, primary_key=True)
#     class_name = db.Column(db.String(100))
#     teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
#     schedule = db.Column(db.String(50))
#     start_date = db.Column(db.Date)
#     end_date = db.Column(db.Date)
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
#     grades = db.relationship('Grade', backref='class_', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    schedule = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    # Relationships
    grades = db.relationship('Grade', backref='related_class', lazy=True)
    attendance = db.relationship('Attendance', backref='related_class', lazy=True)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    classes = db.relationship('ClassSubject', backref='subject', lazy=True)


class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)


class AssessmentType(db.Model):
    __tablename__ = 'assessment_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Exam, Test 1, Test 2, etc.


class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Relationships
    assessment_type = db.relationship('AssessmentType', backref='assessments', lazy=True)
    subject_scores = db.relationship('AssessmentSubjectScore', backref='assessment', lazy=True)


class AssessmentSubjectScore(db.Model):
    __tablename__ = 'assessment_subject_scores'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)


class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)


# class Grade(db.Model):
#     __tablename__ = 'grades'
#     grade_id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
#     class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
#     grade = db.Column(db.String(5))

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)

    # Relationships
    student = db.relationship('Student', backref='grades', lazy=True)



# class Attendance(db.Model):
#     __tablename__ = 'attendance'
#     attendance_id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
#     class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'))
#     attendance_date = db.Column(db.Date)
#     status = db.Column(db.String(10))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)

    # Relationships
    student = db.relationship('Student', backref='attendance', lazy=True)



# class TeacherSubject(db.Model):
#     __tablename__ = 'teacher_subjects'
#     id = db.Column(db.Integer, primary_key=True)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
#     # Relationships
#     teacher = db.relationship('Teacher', backref='teacher_subjects', lazy=True)
#     subject = db.relationship('Subject', backref='teacher_subjects', lazy=True)


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='teacher_subjects', lazy=True)
    subject = db.relationship('Subject', backref='teacher_subjects', lazy=True)  # Unique backref name
