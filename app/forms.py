from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField, FloatField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Email
from flask_wtf.file import FileField, FileAllowed

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('Admin')
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register User')


class SchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    website = StringField('Website', validators=[Length(max=100)])
    submit = SubmitField('Register School')

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    enrollment_date = DateField('Enrollment Date', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=100)])
    grade_level = StringField('Grade Level', validators=[DataRequired(), Length(max=20)])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save')


# class TeacherForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
#     subject = StringField('Subject', validators=[DataRequired(), Length(max=50)])
#     email = StringField('Email', validators=[DataRequired(), Length(max=100)])
#     phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
#     hire_date = DateField('Hire Date', validators=[DataRequired()])
#     submit = SubmitField('Save')



# class TeacherForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
#     subject = SelectField('Subject', coerce=int, validators=[DataRequired()])  # Store subject ID
#     hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[DataRequired()])
#     phone_number = StringField('Phone Number', validators=[Length(max=15)])
#     school_id = SelectField('School', coerce=int, validators=[DataRequired()])  # Store school ID
#     submit = SubmitField('Add Teacher')


# class TeacherForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
#     subject = SelectMultipleField('Subjects', coerce=int, validators=[DataRequired()])  # Multiple selection
#     hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[DataRequired()])
#     phone_number = StringField('Phone Number', validators=[Length(max=15)])
#     school_id = SelectField('School', coerce=int, validators=[DataRequired()])
#     submit = SubmitField('Add Teacher')

# class TeacherForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
#     subject = SelectMultipleField('Subjects', coerce=int, validators=[DataRequired()])  # Multi-select
#     hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[DataRequired()])
#     phone_number = StringField('Phone Number', validators=[Length(max=15)])
#     school_id = SelectField('School', coerce=int, validators=[DataRequired()])
#     submit = SubmitField('Add Teacher')




class TeacherForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    qualification = StringField('Qualification', validators=[Length(max=255)])
    address = StringField('Address', validators=[Length(max=255)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])  # Allow only images
    subject = SelectMultipleField('Subjects', coerce=int, validators=[DataRequired()])  # Multi-select
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Teacher')


class ClassForm(FlaskForm):
    class_name = StringField('Class Name', validators=[DataRequired(), Length(max=100)])  # Matches VARCHAR(100)
    teacher_id = IntegerField('Teacher ID', validators=[DataRequired(), NumberRange(min=1)])  # Matches INTEGER
    schedule = StringField('Schedule', validators=[DataRequired(), Length(max=50)])  # Matches VARCHAR(50)
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])  # Matches DATE
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])  # Matches DATE
    submit = SubmitField('Save')

class GradeForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired(), NumberRange(min=1)])
    class_id = IntegerField('Class ID', validators=[DataRequired(), NumberRange(min=1)])
    grade = IntegerField('Grade', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save')

class AttendanceForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired(), NumberRange(min=1)])
    class_id = IntegerField('Class ID', validators=[DataRequired(), NumberRange(min=1)])
    attendance_date = DateField('Attendance Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')], validators=[DataRequired()])
    submit = SubmitField('Save')


class AssessmentForm(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired(), Length(max=100)])
    date = DateField('Assessment Date', format='%Y-%m-%d', validators=[DataRequired()])
    assessment_type_id = SelectField('Assessment Type', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Assessment')


class AssessmentTypeForm(FlaskForm):
    name = StringField('Assessment Type', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save')

class AssessmentResultForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    marks_obtained = FloatField('Marks Obtained', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Result')


class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Subject')