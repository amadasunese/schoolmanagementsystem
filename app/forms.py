# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

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


class TeacherForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=15)])
    submit = SubmitField('Save')

class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(max=50)])
    schedule = StringField('Schedule', validators=[DataRequired(), Length(max=100)])  # E.g., Mon-Wed-Fri, 9-11 AM
    submit = SubmitField('Save')

class GradeForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired(), NumberRange(min=1)])
    class_id = IntegerField('Class ID', validators=[DataRequired(), NumberRange(min=1)])
    grade = IntegerField('Grade', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save')

class AttendanceForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired(), NumberRange(min=1)])
    class_id = IntegerField('Class ID', validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')], validators=[DataRequired()])
    submit = SubmitField('Save')
