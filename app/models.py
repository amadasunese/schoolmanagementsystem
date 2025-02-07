
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date
from enum import Enum


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    school_logo = db.Column(db.String(255), nullable=True)


    # Relationships
    users = db.relationship('User', backref='school', lazy=True)
    students = db.relationship('Student', backref='school', lazy=True)
    teachers = db.relationship('Teacher', backref='school', lazy=True)
    classes = db.relationship('Class', backref='school', lazy=True)
    subjects = db.relationship('Subject', backref='school', lazy=True)



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('admin', 'teacher', 'student', name='user_roles'), nullable=False)
    school_id = db.Column(
        db.Integer, 
        db.ForeignKey('schools.id', name='fk_users_school_id'), 
        nullable=False
    )

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
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    school_id = db.Column(
        db.Integer, 
        db.ForeignKey('schools.id', name='fk_students_school_id'), 
        nullable=False
    )
    class_id = db.Column(
        db.Integer, 
        db.ForeignKey('classes.id', name='fk_students_class_id'),
        nullable=False
    )

    # Relationships
    grades = db.relationship('Grade', backref='student', lazy=True)
    attendance = db.relationship('Attendance', backref='student', lazy=True)


class_teacher_association = db.Table(
    'class_teacher_association',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True)
)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    school_id = db.Column(
        db.Integer, 
        db.ForeignKey('schools.id', name='fk_teachers_school_id'), 
        nullable=False
    )
    class_id = db.Column(
        db.Integer, 
        db.ForeignKey('classes.id', name='fk_teachers_class_id'), 
        nullable=True
    )

    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher', lazy=True)

    # Corrected Many-to-Many Relationship
    assigned_classes = db.relationship(
        'Class',
        secondary=class_teacher_association,
        backref=db.backref('assigned_teachers', lazy='dynamic'),
        lazy=True
    )

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), unique=True, nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    class_category = db.Column(db.String(50), nullable=False)
    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', name='fk_classes_school_id'),
        nullable=False
    )
    students = db.relationship('Student', backref='class_', lazy=True)

    # Many-to-Many Relationship with Teachers
    teachers = db.relationship('Teacher', secondary=class_teacher_association, backref='classes')
    fee_components = db.relationship('ClassFeeComponent', backref='class_assoc', lazy=True)

    @property
    def teacher_names(self):
        """
        Returns the names of all teachers assigned to the class.
        """
        return ', '.join([f"{teacher.first_name} {teacher.last_name}" for teacher in self.teachers])
    

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher_subject', lazy=True)
    assessment_scores = db.relationship('AssessmentSubjectScore', backref='subject_ref', lazy=True)
    class_subjects = db.relationship('ClassSubject', backref='class_subject', lazy=True)



class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)


class AssessmentType(db.Model):
    __tablename__ = 'assessment_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    academic_session = db.Column(db.String(20), nullable=False)
    term = db.Column(db.String(20), nullable=False)


    # Relationships
    assessment_type = db.relationship('AssessmentType', backref='assessments', lazy=True)
    subject_scores = db.relationship('AssessmentSubjectScore', backref='assessmentsubjectscores', lazy=True)


class AssessmentSubjectScore(db.Model):
    __tablename__ = 'assessment_subject_scores'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', name='fk_assessment_subject_scores_subject_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    # marks_obtainable = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)

    # Relationships with unique backref names
    assessment = db.relationship('Assessment', backref=db.backref('assessment_subject_scores', lazy=True)) 
    subject = db.relationship('Subject', backref=db.backref('subject_ref', lazy=True)) 
    student = db.relationship('Student', backref=db.backref('student_assessments', lazy=True))



class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    days_present = db.Column(db.Integer, nullable=False, default=0)
    total_days_opened = db.Column(db.Integer, nullable=False, default=0)


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subject'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    # Relationship with Subject
    subject = db.relationship('Subject', backref='teachers_subjects')

    def __repr__(self):
        return f"<TeacherSubject teacher_id={self.teacher_id}, subject_id={self.subject_id}>"


# fees processing
    
class StudentFee(db.Model):
    __tablename__ = 'student_fees'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('fee_components.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.Enum('paid', 'unpaid', name='payment_status'), default='unpaid', nullable=False)

    # Relationships
    student = db.relationship('Student', backref='student_fees')
    component = db.relationship('FeeComponent', backref='student_fees')

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    student_fee_id = db.Column(db.Integer, db.ForeignKey('student_fees.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    receipt_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    student_fee = db.relationship('StudentFee', backref='fee_payments')

class FeeComponent(db.Model):
    __tablename__ = 'fee_components'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    # Relationships
    school = db.relationship('School', backref='fee_components')
    class_fees = db.relationship('ClassFeeComponent', backref='fee_component_assoc', lazy=True)

class ClassFeeComponent(db.Model):
    __tablename__ = 'class_fee_components'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('fee_components.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # Relationships
    class__ = db.relationship('Class', backref='class_fee_components_assoc')
    fee_component = db.relationship('FeeComponent', backref='class_fee_components_assoc')