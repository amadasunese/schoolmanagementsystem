from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField, FloatField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Email
from flask_wtf.file import FileField, FileAllowed

# class UserForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired(), Length(max=50)])
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
#     is_admin = BooleanField('Admin')
#     school_id = SelectField('School', coerce=int, validators=[DataRequired()])
#     submit = SubmitField('Register User')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')], validators=[DataRequired()])
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register')

class SchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    website = StringField('Website', validators=[Length(max=100)])
    submit = SubmitField('Register School')


from app.models import Class, School

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    enrollment_date = DateField('Enrollment Date', validators=[DataRequired()], format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    grade_level = StringField('Grade Level', validators=[DataRequired(), Length(max=20)])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email(), Length(max=100)])
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])  # Adjusted to be dynamic
    submit = SubmitField('Add Student')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the choices dynamically
        self.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]
        if not self.class_id.choices:
            self.class_id.choices = [(-1, 'No classes available')]  # Default placeholder

        self.school_id.choices = [(sch.id, sch.name) for sch in School.query.all()]
        if not self.school_id.choices:
            self.school_id.choices = [(-1, 'No schools available')]  # Default placeholder


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
    name = StringField('Assessment Name', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    assessment_type = SelectField('Assessment Type', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    academic_session = StringField('Academic Session', validators=[DataRequired()])
    term = SelectField('Term', choices=[('First Term', 'First Term'), ('Second Term', 'Second Term'), ('Third Term', 'Third Term')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class AssessmentTypeForm(FlaskForm):
    name = StringField('Assessment Type', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save')

class AssessmentResultForm(FlaskForm):
    studentSelectFieldlidators=[DataRequired()]
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    marks_obtained = FloatField('Marks Obtained', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Result')


class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Subject')


from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Teacher

def validate_teacher_id(form, field):
    if field.data and not Teacher.query.get(field.data):
        raise ValidationError('Invalid Teacher ID.')


class ClassForm(FlaskForm):
    class_name = StringField('Class Name', validators=[DataRequired()])
    class_level = StringField('Class Level', validators=[DataRequired()])
    # class_category = StringField('Class Category', validators=[DataRequired()])
    class_category = SelectField(
        'Class Category',
        choices=[('Nursery', 'Nursery'), ('Primary', 'Primary'), 
                 ('Junior Secondary', 'Junior Secondary'), ('Senior Secondary', 'Senior Secondary')],
        validators=[DataRequired()]
    )
    # teacher_ids = SelectMultipleField('Assign Teachers', coerce=int, validators=[DataRequired()])
    teacher_ids = SelectMultipleField('Teachers', coerce=int)  # For selecting multiple teachers
    submit = SubmitField('Add Class')


class AssignTeachersForm(FlaskForm):
    class_id = SelectField('Class', coerce=int)
    teacher_ids = SelectMultipleField('Teachers', coerce=int)
    submit = SubmitField('Assign Teachers')
