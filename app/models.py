
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
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

    @property
    def teacher_names(self):
        """
        Returns the names of all teachers assigned to the class.
        """
        return ', '.join([f"{teacher.first_name} {teacher.last_name}" for teacher in self.teachers])



# class Subject(db.Model):
#     __tablename__ = 'subjects'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

#     # Relationships
#     teacher_subjects = db.relationship('TeacherSubject', backref='subject', lazy=True)
#     class_subjects = db.relationship('ClassSubject', backref='subject', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher_subject', lazy=True)
    # assessment_scores = db.relationship('AssessmentSubjectScore', backref='subject', lazy=True)  # Unique backref
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


# class Assessment(db.Model):
#     __tablename__ = 'assessments'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
#     class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

#     # Relationships
#     assessment_type = db.relationship('AssessmentType', backref='assessments', lazy=True)
#     scores = db.relationship('AssessmentSubjectScore', backref='assessment', lazy=True)

# class Assessment(db.Model):
#     __tablename__ = 'assessments'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
#     class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
#     academic_session = db.Column(db.String(20), nullable=False)  # E.g., "2024/2025"

#     # Relationships
#     assessment_type = db.relationship('AssessmentType', backref='assessments', lazy=True)
#     scores = db.relationship('AssessmentSubjectScore', backref='assessment', lazy=True)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    academic_session = db.Column(db.String(20), nullable=False)  # E.g., "2024/2025"
    term = db.Column(db.String(20), nullable=False)  # E.g., "Term 1"


    # Relationships
    assessment_type = db.relationship('AssessmentType', backref='assessments', lazy=True)
    subject_scores = db.relationship('AssessmentSubjectScore', backref='assessmentsubjectscores', lazy=True)  # Updated backref



# class AssessmentSubjectScore(db.Model):
#     __tablename__ = 'assessment_subject_scores'
#     id = db.Column(db.Integer, primary_key=True)
#     assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
#     total_marks = db.Column(db.Integer, nullable=False)

# class AssessmentSubjectScore(db.Model):
#     __tablename__ = 'assessment_subject_scores'
#     id = db.Column(db.Integer, primary_key=True)
#     assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)  # Link to students
#     total_marks = db.Column(db.Integer, nullable=False)

#     assessment = db.relationship('Assessment', backref=db.backref('scores', lazy=True))
#     subject = db.relationship('Subject', backref=db.backref('scores', lazy=True))
#     student = db.relationship('Student', backref=db.backref('scores', lazy=True))

# class AssessmentSubjectScore(db.Model):
#     __tablename__ = 'assessment_subject_scores'
#     id = db.Column(db.Integer, primary_key=True)
#     assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)  # Link to students
#     total_marks = db.Column(db.Integer, nullable=False)

#     # Update the backref names to avoid conflict
#     assessment = db.relationship('Assessment', backref=db.backref('assessment_subject_scores', lazy=True))
#     subject = db.relationship('Subject', backref=db.backref('subject_scores', lazy=True))
#     student = db.relationship('Student', backref=db.backref('student_scores', lazy=True))

# class AssessmentSubjectScore(db.Model):
#     __tablename__ = 'assessment_subject_scores'
#     id = db.Column(db.Integer, primary_key=True)
#     assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
#     total_marks = db.Column(db.Integer, nullable=False)

#     # Relationships with unique backref names
#     assessment = db.relationship('Assessment', backref=db.backref('subject_scores', lazy=True))  # Changed from `scores`
#     subject = db.relationship('Subject', backref=db.backref('assessment_scores', lazy=True))     # Changed from `scores`
#     student = db.relationship('Student', backref=db.backref('subjects_scores', lazy=True))     # Changed from `scores`


class AssessmentSubjectScore(db.Model):
    __tablename__ = 'assessment_subject_scores'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', name='fk_assessment_subject_scores_subject_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)

    # Relationships with unique backref names
    assessment = db.relationship('Assessment', backref=db.backref('assessment_subject_scores', lazy=True)) 
    subject = db.relationship('Subject', backref=db.backref('subject_ref', lazy=True)) 
    # subject = db.relationship('Subject', backref=db.backref('subject_assessments', lazy=True))  # Unique backref
    student = db.relationship('Student', backref=db.backref('student_assessments', lazy=True))  # Unique backref



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
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

