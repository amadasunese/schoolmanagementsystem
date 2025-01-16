# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from . import db
from .forms import TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm
from .models import Grade
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
import pandas as pd
from docx import Document


# Import additional models
from .models import (
    User, Student, Teacher, Class, Attendance, Assessment, AssessmentType, AssessmentSubjectScore, AssessmentResult, Subject, ClassSubject, TeacherSubject
)
from .forms import AssessmentForm, AssessmentResultForm, SubjectForm  # New forms for assessments and subjects

import os
from werkzeug.utils import secure_filename
from flask import current_app

from .forms import SchoolForm
from .models import School




# Create a Blueprint instance
main = Blueprint('main', __name__)
# Login route

@main.route('/')
def index():
    return render_template('index.html')


from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db
from .forms import SchoolForm, UserForm
from .models import School, User



@main.route('/register_school', methods=['GET', 'POST'])
def register_school():
    form = SchoolForm()
    if form.validate_on_submit():
        school = School(
            name=form.name.data,
            address=form.address.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            website=form.website.data
        )
        db.session.add(school)
        db.session.commit()
        flash('School registered successfully!', 'success')
        return redirect(url_for('main.register_user'))  # Redirect to user registration after school
    return render_template('register_school.html', form=form)

@main.route('/register_user', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            is_admin=form.is_admin.data,
            school_id=form.school_id.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('main.index'))  # Redirect to home or login
    return render_template('register_user.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Dashboard (Only accessible by Admins)
@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    class_count = Class.query.count()
    return render_template('dashboard.html', student_count=student_count,
                           teacher_count=teacher_count, class_count=class_count)

# Report Generation Route
@main.route('/generate_report/<report_type>')
@login_required
def generate_report(report_type):
    # Sample data fetching for report
    data = {
        "Students": pd.read_sql(Student.query.statement, db.session.bind),
        "Teachers": pd.read_sql(Teacher.query.statement, db.session.bind),
        "Classes": pd.read_sql(Class.query.statement, db.session.bind),
        "Grades": pd.read_sql(Grade.query.statement, db.session.bind),
        "Attendance": pd.read_sql(Attendance.query.statement, db.session.bind),
    }
    
    if report_type == "excel":
        with BytesIO() as output:
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            for sheet, df in data.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
            writer.save()
            output.seek(0)
            return send_file(output, attachment_filename="report.xlsx", as_attachment=True)
    
    elif report_type == "word":
        doc = Document()
        for section, df in data.items():
            doc.add_heading(section, level=1)
            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, column in enumerate(df.columns):
                hdr_cells[i].text = column
            for _, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, value in enumerate(row):
                    row_cells[i].text = str(value)
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        return send_file(output, attachment_filename="report.docx", as_attachment=True)

# Student route
@main.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

# Teacher route
@main.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)

# Classes routes
@main.route('/classes')
def classes():
    classes = Class.query.all()
    return render_template('classes.html', classes=classes)

# Grades routes
@main.route('/grades')
def grades():
    grades = Grade.query.all()
    return render_template('grades.html', grades=grades)

# Attendance routes
@main.route('/attendance')
def attendance():
    attendance = Attendance.query.all()
    return render_template('attendance.html', attendance=attendance)

# routes to records new students, teachers, classes, attendance and grades
@main.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            name=form.name.data,
            age=form.age.data,
            class_id=form.class_id.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('main.students'))
    return render_template('add_student.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the list of schools
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the list of subjects from the Subject table
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             subject=form.subject.data,  # Save subject ID instead of name
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
#         flash('Teacher added successfully!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the school choices
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the subject choices
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         # Save the teacher with multiple subjects
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
        
#         # Associate the teacher with selected subjects
#         for subject_id in form.subject.data:
#             teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
#             db.session.add(teacher_subject)
        
#         db.session.commit()
#         flash('Teacher added successfully with selected subjects!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the school choices
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the subject choices
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         # Save the teacher's data
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             subject=form.subject.data,
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
        
#         # Associate the teacher with selected subjects
#         for subject_id in form.subject.data:
#             teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
#             db.session.add(teacher_subject)
        
#         db.session.commit()
#         flash('Teacher added successfully with selected subjects!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the school choices
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the subject choices
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         # Save the teacher's data
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
        
#         # Associate the teacher with selected subjects
#         for subject_id in form.subject.data:
#             teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
#             db.session.add(teacher_subject)
        
#         db.session.commit()
#         flash('Teacher added successfully with selected subjects!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the school choices
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the subject choices
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         # Save the teacher's data
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
        
#         # Associate the teacher with selected subjects
#         for subject_id in form.subject.data:
#             teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
#             db.session.add(teacher_subject)
        
#         db.session.commit()
#         flash('Teacher added successfully with selected subjects!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)




# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
    
#     # Populate the school choices
#     form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    
#     # Populate the subject choices
#     form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
#     if form.validate_on_submit():
#         # Handle file upload
#         photo_filename = None
#         if form.photo.data:
#             photo_file = form.photo.data
#             photo_filename = secure_filename(photo_file.filename)
#             photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo_filename)
#             photo_file.save(photo_path)
        
#         # Save the teacher's data
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             hire_date=form.hire_date.data,
#             phone_number=form.phone_number.data,
#             qualification=form.qualification.data,
#             address=form.address.data,
#             date_of_birth=form.date_of_birth.data,
#             gender=form.gender.data,
#             photo=photo_filename,
#             school_id=form.school_id.data
#         )
#         db.session.add(teacher)
#         db.session.commit()
        
#         # Associate the teacher with selected subjects
#         for subject_id in form.subject.data:
#             teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
#             db.session.add(teacher_subject)
        
#         db.session.commit()
#         flash('Teacher added successfully with photo and details!')
#         return redirect(url_for('main.teachers'))
    
#     return render_template('add_teacher.html', form=form)


@main.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    
    # Populate choices
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    
    if form.validate_on_submit():
        # Handle photo upload
        photo_filename = None
        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo_filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure directory exists
            photo_file.save(photo_path)
        
        # Save the teacher's data
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            hire_date=form.hire_date.data,
            phone_number=form.phone_number.data,
            qualification=form.qualification.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            photo=photo_filename,
            school_id=form.school_id.data
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Associate teacher with subjects
        for subject_id in form.subject.data:
            teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
            db.session.add(teacher_subject)
        
        db.session.commit()
        flash('Teacher added successfully with photo and details!')
        return redirect(url_for('main.teachers'))
    
    return render_template('add_teacher.html', form=form)


# @main.route('/add_teacher', methods=['GET', 'POST'])
# @login_required
# def add_teacher():
#     form = TeacherForm()
#     if form.validate_on_submit():
#         teacher = Teacher(
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             subject=form.subject.data,
#             email=form.email.data,
#             phone_number=form.phone_number.data,
#             hire_date=form.hire_date.data

#         )
#         db.session.add(teacher)
#         db.session.commit()
#         flash('Teacher added successfully!')
#         return redirect(url_for('main.teachers'))
#     return render_template('add_teacher.html', form=form)


# Edit Teacher
# @main.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
# def edit_teacher(teacher_id):
#     teacher = Teacher.query.get_or_404(teacher_id)
    
#     if request.method == 'POST':
#         # You would typically update the teacher's information based on form input
#         teacher.name = request.form['name']
#         teacher.subject = request.form['subject']
#         db.session.commit()
#         flash('Teacher updated successfully!', 'success')
#         return redirect(url_for('index'))
    
#     return render_template('edit_teacher.html', teacher=teacher)

# # Delete Teacher
# @main.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
# def delete_teacher(teacher_id):
#     teacher = Teacher.query.get_or_404(teacher_id)
#     db.session.delete(teacher)
#     db.session.commit()
#     flash('Teacher deleted successfully!', 'danger')
#     return redirect(url_for('index'))


@main.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    if form.validate_on_submit():
        # Create a new class instance with form data
        new_class = Class(
            class_name=form.class_name.data,
            teacher_id=form.teacher_id.data,
            schedule=form.schedule.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully!', 'success')
        return redirect(url_for('main.classes'))
    return render_template('add_class.html', form=form)


@main.route('/add_or_edit_class', methods=['GET', 'POST'])
@login_required
def add_or_edit_class():
    form = ClassForm()
    """Handle both adding and editing classes."""
    class_id = request.args.get('class_id', None)
    if class_id:
        # If class_id is provided, retrieve the class for editing
        class_instance = Class.query.get_or_404(class_id)
        form = ClassForm(obj=class_instance)
        if form.validate_on_submit():
            # Update class details
            class_instance.class_name = form.class_name.data
            class_instance.teacher_id = form.teacher_id.data
            class_instance.schedule = form.schedule.data
            class_instance.start_date = form.start_date.data
            class_instance.end_date = form.end_date.data
            db.session.commit()
            flash('Class updated successfully!', 'success')
            return redirect(url_for('main.classes'))
    else:
        # If no class_id is provided, create a blank form for adding
        form = ClassForm()
        if form.validate_on_submit():
            # Add a new class
            new_class = Class(
                class_name=form.class_name.data,
                teacher_id=form.teacher_id.data,
                schedule=form.schedule.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data
            )
            db.session.add(new_class)
            db.session.commit()
            flash('Class added successfully!', 'success')
            return redirect(url_for('main.classes'))

    return render_template('add_or_edit_class.html', form=form, class_id=class_id)


@main.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    """Handle editing an existing class."""
    class_instance = Class.query.get_or_404(class_id)
    form = ClassForm(obj=class_instance)
    if form.validate_on_submit():
        # Update class details
        class_instance.class_name = form.class_name.data
        class_instance.teacher_id = form.teacher_id.data
        class_instance.schedule = form.schedule.data
        class_instance.start_date = form.start_date.data
        class_instance.end_date = form.end_date.data
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('main.classes'))
    return render_template('edit_class.html', form=form, class_instance=class_instance)


@main.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    """Handle deleting a class."""
    class_instance = Class.query.get_or_404(class_id)
    db.session.delete(class_instance)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('main.classes'))


@main.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            class_id=form.class_id.data,
            score=form.score.data
        )
        db.session.add(grade)
        db.session.commit()
        flash('Grade added successfully!')
        return redirect(url_for('main.grades'))
    return render_template('add_grade.html', form=form)

# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()
#     if form.validate_on_submit():
#         attendance = Attendance(
#             student_id=form.student_id.data,
#             class_id=form.class_id.data,
#             date=form.date.data,
#             status=form.status.data
#         )
#         db.session.add(attendance)
#         db.session.commit()
#         flash('Attendance record added successfully!')
#         return redirect(url_for('main.attendance'))
#     return render_template('add_attendance.html', form=form)





############################################################################################################


# @main.route('/register_school', methods=['GET', 'POST'])
# @login_required
# def register_school():
#     # Only admins or superusers should be allowed to register schools
#     if not current_user.is_admin:
#         flash('You do not have permission to register a school.', 'danger')
#         return redirect(url_for('main.index'))

#     form = SchoolForm()
#     if form.validate_on_submit():
#         # Create a new school instance
#         new_school = School(
#             name=form.name.data,
#             address=form.address.data,
#             email=form.email.data,
#             phone_number=form.phone_number.data,
#             website=form.website.data
#         )
#         db.session.add(new_school)
#         db.session.commit()
#         flash('School registered successfully!', 'success')
#         return redirect(url_for('main.dashboard'))  # Redirect to dashboard or relevant page
#     return render_template('register_school.html', form=form)


# Route to display all subjects
@main.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('subjects.html', subjects=subjects)

# Route to add a subject
@main.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            school_id=current_user.school_id
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!')
        return redirect(url_for('main.subjects'))
    return render_template('add_subject.html', form=form)

# Route to display all assessments
@main.route('/assessments')
@login_required
def assessments():
    assessments = Assessment.query.filter_by(class_id=current_user.school_id).all()
    return render_template('assessments.html', assessments=assessments)

# Route to add an assessment
@main.route('/add_assessment', methods=['GET', 'POST'])
@login_required
def add_assessment():
    form = AssessmentForm()
    if form.validate_on_submit():
        assessment = Assessment(
            name=form.name.data,
            date=form.date.data,
            assessment_type_id=form.assessment_type_id.data,
            class_id=form.class_id.data
        )
        db.session.add(assessment)
        db.session.commit()
        flash('Assessment added successfully!')
        return redirect(url_for('main.assessments'))
    return render_template('add_assessment.html', form=form)

# Route to record assessment scores per subject
@main.route('/add_assessment_score/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def add_assessment_score(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.class_id not in [cls.id for cls in current_user.school.classes]:
        flash('You do not have permission to edit this assessment.')
        return redirect(url_for('main.assessments'))
    form = AssessmentResultForm()
    if form.validate_on_submit():
        result = AssessmentResult(
            student_id=form.student_id.data,
            assessment_id=assessment_id,
            subject_id=form.subject_id.data,
            marks_obtained=form.marks_obtained.data
        )
        db.session.add(result)
        db.session.commit()
        flash('Score added successfully!')
        return redirect(url_for('main.assessments'))
    return render_template('add_assessment_score.html', form=form, assessment=assessment)

# Route to view all scores for an assessment
@main.route('/assessment_scores/<int:assessment_id>')
@login_required
def assessment_scores(assessment_id):
    scores = AssessmentResult.query.filter_by(assessment_id=assessment_id).all()
    return render_template('assessment_scores.html', scores=scores)

# Route to add attendance
@main.route('/add_attendance', methods=['GET', 'POST'])
@login_required
def add_attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        attendance = Attendance(
            student_id=form.student_id.data,
            class_id=form.class_id.data,
            date=form.date.data,
            status=form.status.data
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance record added successfully!')
        return redirect(url_for('main.attendance'))
    return render_template('add_attendance.html', form=form)

# Route to generate a report of all assessment scores
@main.route('/generate_assessment_report/<int:assessment_id>')
@login_required
def generate_assessment_report(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    scores = AssessmentResult.query.filter_by(assessment_id=assessment_id).all()
    data = pd.DataFrame([{
        "Student": f"{score.student.first_name} {score.student.last_name}",
        "Subject": score.subject.name,
        "Marks Obtained": score.marks_obtained
    } for score in scores])
    
    with BytesIO() as output:
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        data.to_excel(writer, index=False, sheet_name='Assessment Scores')
        writer.save()
        output.seek(0)
        return send_file(output, attachment_filename=f"Assessment_{assessment.name}_Report.xlsx", as_attachment=True)


# Route to list all assessment types
@main.route('/assessment_types')
@login_required
def assessment_types():
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    assessment_types = AssessmentType.query.all()
    return render_template('assessment_types.html', assessment_types=assessment_types)

# Route to add an assessment type
@main.route('/add_assessment_type', methods=['GET', 'POST'])
@login_required
def add_assessment_type():
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Assessment type name is required.', 'danger')
        else:
            new_type = AssessmentType(name=name)
            db.session.add(new_type)
            db.session.commit()
            flash('Assessment type added successfully!', 'success')
            return redirect(url_for('main.assessment_types'))
    return render_template('add_assessment_type.html')


# Route to view subject scores for an assessment
@main.route('/assessment_subject_scores/<int:assessment_id>')
@login_required
def assessment_subject_scores(assessment_id):
    scores = AssessmentSubjectScore.query.filter_by(assessment_id=assessment_id).all()
    return render_template('assessment_subject_scores.html', scores=scores, assessment_id=assessment_id)

# Route to add a subject score for an assessment
@main.route('/add_assessment_subject_score/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def add_assessment_subject_score(assessment_id):
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    assessment = Assessment.query.get_or_404(assessment_id)
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        total_marks = request.form.get('total_marks')
        if not subject_id or not total_marks:
            flash('All fields are required.', 'danger')
        else:
            new_score = AssessmentSubjectScore(
                assessment_id=assessment_id,
                subject_id=subject_id,
                total_marks=total_marks
            )
            db.session.add(new_score)
            db.session.commit()
            flash('Subject score added successfully!', 'success')
            return redirect(url_for('main.assessment_subject_scores', assessment_id=assessment_id))
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('add_assessment_subject_score.html', assessment=assessment, subjects=subjects)


# Route to view all subjects for a class
@main.route('/class_subjects/<int:class_id>')
@login_required
def class_subjects(class_id):
    class_instance = Class.query.get_or_404(class_id)
    subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    return render_template('class_subjects.html', class_instance=class_instance, subjects=subjects)

# Route to add a subject to a class
@main.route('/add_class_subject/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_class_subject(class_id):
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    class_instance = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        if not subject_id:
            flash('Subject is required.', 'danger')
        else:
            new_class_subject = ClassSubject(
                class_id=class_id,
                subject_id=subject_id
            )
            db.session.add(new_class_subject)
            db.session.commit()
            flash('Subject added to class successfully!', 'success')
            return redirect(url_for('main.class_subjects', class_id=class_id))
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('add_class_subject.html', class_instance=class_instance, subjects=subjects)

