# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from . import db
import os
from .forms import (
    TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm, AssignTeachersForm,
    AssessmentForm, AssessmentResultForm, SubjectForm, SchoolForm, UserForm, AssessmentTypeForm
)
from .models import (
    User, Student, Teacher, Class, Attendance, Assessment, AssessmentType,
    AssessmentSubjectScore, AssessmentResult, Subject, ClassSubject, TeacherSubject, School
)
from .models import Grade
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
import pandas as pd
from docx import Document
from flask import send_from_directory
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import current_app
from config import Config
from sqlalchemy.orm import joinedload



# Create a Blueprint instance
main = Blueprint('main', __name__)
# Login route

@main.route('/')
def index():
    return render_template('index.html', is_authenticated=current_user.is_authenticated)




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
        return redirect(url_for('main.register_user'))
    return render_template('register_school.html', form=form)


@main.route('/register_user', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('main.register_user'))
        user = User(
            username=form.username.data,
            role=form.role.data,
            school_id=form.school_id.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the user.', 'danger')
    return render_template('register_user.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('main.teacher.dashboard'))
            else:
                return redirect(url_for('main.student.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')




@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Student Dashboard (Only accessible by Students)
@main.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role!= 'student':
        return redirect(url_for('main.index'))
    student_name = Student.query.get(current_user.id).name
    return render_template('student_dashboard.html', student_name=student_name)

# Teacher Dashboard (Only accessible by Teachers)
@main.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('main.index'))
    teacher_name = Teacher.query.get(current_user.id).name
    return render_template('teacher_dashboard.html', teacher_name=teacher_name)



# Dashboard (Only accessible by Admins)
@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role== 'admin':
        return redirect(url_for('main.index'))
    school_name = School.query.get(current_user.school_id).name
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    class_count = Class.query.count()
    return render_template('dashboard.html', school_name=school_name, student_count=student_count,
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


@main.route('/students')
def students():
    # Fetch all students along with their class information using eager loading
    students = Student.query.join(Class, Student.class_id == Class.id).add_columns(
        Student.id, 
        Student.first_name, 
        Student.last_name, 
        Student.grade_level,
        Student.enrollment_date,
        Class.class_name.label('class_name')
    ).all()
    return render_template('students.html', students=students)

@main.route('/add_student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()

    # Populate the choices dynamically for class_id
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]
    if not form.class_id.choices:
        form.class_id.choices = [(-1, 'No classes available')]

    # Populate the choices dynamically for school_id
    form.school_id.choices = [(sch.id, sch.name) for sch in School.query.all()]
    if not form.school_id.choices:
        form.school_id.choices = [(-1, 'No schools available')]

    if form.validate_on_submit():
        # Handle the form submission
        try:
            if form.class_id.data == -1:
                flash("Please select a valid class.", "warning")
                return render_template('add_student.html', form=form)

            if form.school_id.data == -1:
                flash("Please select a valid school.", "warning")
                return render_template('add_student.html', form=form)

            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                date_of_birth=form.date_of_birth.data,
                enrollment_date=form.enrollment_date.data,
                gender=form.gender.data,
                grade_level=form.grade_level.data,
                contact_email=form.contact_email.data,
                school_id=current_user.school_id,
                class_id=form.class_id.data
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('main.students'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while adding the student: {str(e)}", "danger")

    return render_template('add_student.html', form=form)


@main.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# Teacher route
@main.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)

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
            photo_path = os.path.join(Config.UPLOAD_FOLDER, photo_filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
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


@main.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    # Delete associated subjects
    TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()

    # Delete the teacher record
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!')
    return redirect(url_for('main.teachers'))


@main.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(obj=teacher)

    # Populate choices
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

    if form.validate_on_submit():
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data
        teacher.hire_date = form.hire_date.data
        teacher.phone_number = form.phone_number.data
        teacher.qualification = form.qualification.data
        teacher.address = form.address.data
        teacher.date_of_birth = form.date_of_birth.data
        teacher.gender = form.gender.data
        teacher.school_id = form.school_id.data

        # Update subjects
        TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()
        for subject_id in form.subject.data:
            teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
            db.session.add(teacher_subject)

        db.session.commit()
        flash('Teacher updated successfully!')
        return redirect(url_for('main.teachers'))

    return render_template('edit_teacher.html', form=form, teacher=teacher)




@main.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    teachers = Teacher.query.filter_by(school_id=current_user.school_id).all()

    # Populate form teacher_ids choices dynamically
    form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]

    if form.validate_on_submit():
        # Create a new class instance
        new_class = Class(
            class_name=form.class_name.data,
            class_level=form.class_level.data,
            class_category=form.class_category.data,
            school_id=current_user.school_id,
        )

        # Add selected teachers to the class
        selected_teacher_ids = form.teacher_ids.data
        selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()
        new_class.teachers.extend(selected_teachers)

        try:
            db.session.add(new_class)
            db.session.commit()
            flash('Class added successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding class: {str(e)}', 'danger')

    return render_template('add_class.html', form=form)


@main.route('/classes')
@login_required
def classes():
    # Query classes, join teachers, and calculate student counts
    classes = db.session.query(
        Class,
        func.count(Student.id).label('student_count')
    ).outerjoin(Student, Student.class_id == Class.id) \
     .filter(Class.school_id == current_user.school_id) \
     .group_by(Class.id).options(joinedload('teachers')).all()

    # The result is a list of tuples: (Class object, student_count)
    return render_template('classes.html', classes=classes)


@main.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    # Fetch the class by ID
    class_to_edit = Class.query.get_or_404(class_id)

    if request.method == 'POST':
        # Update the class details
        class_to_edit.class_name = request.form['class_name']
        class_to_edit.class_category = request.form['class_category']
        
        try:
            db.session.commit()
            flash('Class updated successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating class: {str(e)}', 'danger')

    return render_template('edit_class.html', class_to_edit=class_to_edit)

@main.route('/delete_class/<int:class_id>', methods=['GET', 'POST'])
def delete_class(class_id):
    # Fetch the class by ID
    class_to_delete = Class.query.get_or_404(class_id)

    try:
        db.session.delete(class_to_delete)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting class: {str(e)}', 'danger')

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
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    assessment_types = AssessmentType.query.all()
    return render_template('assessment_types.html', assessment_types=assessment_types)

# Route to add an assessment type
@main.route('/add_assessment_type', methods=['GET', 'POST'])
@login_required
def add_assessment_type():
    form = AssessmentTypeForm()
    if not current_user.role == 'admin':
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
    return render_template('add_assessment_type.html', form=form)




@main.route('/assessments')
@login_required
def assessments():
    all_assessments = Assessment.query.join(Class,
                                            Assessment.class_id == Class.id).join(AssessmentType,
                                            Assessment.assessment_type_id == AssessmentType.id).add_columns(
        Assessment.id, 
        Assessment.name, 
        Assessment.date, 
        Assessment.academic_session,
        Assessment.term,
        Class.class_name.label('class_name'), 
        AssessmentType.name.label('assessment_type_name') 
    ).all()
    return render_template('assessments.html', assessments=all_assessments)




@main.route('/add_assessment', methods=['GET', 'POST'])
@login_required
def add_assessment():
    form = AssessmentForm()
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]

    if form.validate_on_submit():
        new_assessment = Assessment(
            name=form.name.data,
            date=form.date.data,
            assessment_type_id=form.assessment_type.data,
            class_id=form.class_id.data,
            academic_session=form.academic_session.data,
            term=form.term.data
        )
        db.session.add(new_assessment)
        db.session.commit()
        flash('Assessment added successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('add_assessment.html', form=form)


@main.route('/edit_assessment/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def edit_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    form = AssessmentForm(obj=assessment)
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]

    if form.validate_on_submit():
        assessment.name = form.name.data
        assessment.date = form.date.data
        assessment.assessment_type_id = form.assessment_type.data
        assessment.class_id = form.class_id.data
        assessment.academic_session = form.academic_session.data
        assessment.term = form.term.data

        db.session.commit()
        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('edit_assessment.html', form=form, assessment=assessment)

@main.route('/delete_assessment/<int:assessment_id>', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    db.session.delete(assessment)
    db.session.commit()
    flash('Assessment deleted successfully!', 'success')
    return redirect(url_for('main.assessments'))


@main.route('/assessment_subject_scores')
def assessment_subject_scores():


    # Fetch all records from AssessmentSubjectScore with their related assessments
    scores = (
        db.session.query(
            AssessmentSubjectScore.id,
            Assessment.name.label('assessment_name'),
            Assessment.academic_session,
            Subject.name.label('subject_name'),
            Student.first_name,
            Student.last_name,
            Class.class_name,
            AssessmentSubjectScore.total_marks
        )
        .join(Assessment, AssessmentSubjectScore.assessment_id == Assessment.id)
        .join(Subject, AssessmentSubjectScore.subject_id == Subject.id)
        .join(Student, AssessmentSubjectScore.student_id == Student.id)
        .join(Class, Assessment.class_id == Class.id)
        .all()
    )
    return render_template('assessment_subject_scores.html', scores=scores)

@main.route('/add_assessment_score', methods=['GET', 'POST'])
def add_assessment_score():
    if request.method == 'POST':
        academic_session = request.form['academic_session']
        assessment_id = request.form['assessment_id']
        subject_id = request.form['subject_id']
        student_id = request.form['student_id']
        class_id = request.form['class_id']
        total_marks = request.form['total_marks']

        # Create a new score record
        new_score = AssessmentSubjectScore(
            assessment_id=assessment_id,
            subject_id=subject_id,
            student_id=student_id,
            total_marks=total_marks
        )
        
        try:
            db.session.add(new_score)
            db.session.commit()
            flash('Assessment score added successfully!', 'success')
            return redirect(url_for('main.assessment_subject_scores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding assessment score: {e}', 'danger')

    # Fetch academic sessions, assessments, subjects, and students
    academic_sessions = list(set(assessment.academic_session for assessment in Assessment.query.all()))
    assessments = Assessment.query.all()
    subjects = Subject.query.all()
    students = Student.query.all()
    classes = Class.query.all()


    return render_template(
        'add_assessment_subject_score.html',
        academic_sessions=academic_sessions,
        assessments=assessments,
        subjects=subjects,
        students=students,
        classes=classes
    )


@main.route('/assessment_subject_scores/edit/<int:id>', methods=['GET', 'POST'])
def edit_assessment_subject_score(id):
    score = AssessmentSubjectScore.query.get_or_404(id)

    if request.method == 'POST':
        score.subject_id = request.form['subject_id']
        score.total_marks = request.form['total_marks']

        try:
            db.session.commit()
            flash('Assessment Subject Score updated successfully!', 'success')
            return redirect(url_for('assessment_subject_scores'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating score: ' + str(e), 'danger')

    # Fetch related data for dropdowns
    subjects = Subject.query.all()
    assessments = Assessment.query.all()
    return render_template('edit_assessment_subject_score.html', score=score, subjects=subjects, assessments=assessments)



# Route to delete an assessment subject score
@main.route('/assessment_subject_scores/delete/<int:id>', methods=['POST'])
def delete_assessment_subject_score(id):
    score = AssessmentSubjectScore.query.get_or_404(id)

    try:
        db.session.delete(score)
        db.session.commit()
        flash('Assessment Subject Score deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting score: ' + str(e), 'danger')

    return redirect(url_for('assessment_subject_scores'))

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
    if not current_user.role == 'admin':
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


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from flask import send_file

# def generate_result_sheet(student):
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=A4)

#     # Title Section
#     pdf.setFont("Helvetica-Bold", 14)
#     pdf.drawCentredString(300, 800, "UNIVERSITY OF  CONSULTANCY SCHOOLS")
#     pdf.setFont("Helvetica", 12)
#     pdf.drawCentredString(300, 780, "University of Benin, Ekehuan Road Campus, P.M.B. 1154, Benin City")
#     pdf.drawCentredString(300, 760, "INDIVIDUAL STUDENT'S ASSESSMENT SHEET")
#     pdf.drawCentredString(300, 740, "JUNIOR SECONDARY SCHOOL")

#     # Student Details
#     pdf.setFont("Helvetica", 10)BENIN
#     pdf.drawString(50, 710, f"RESULT ID: {student['result_id']}")
#     pdf.drawString(250, 710, f"SEX: {student['sex']}")
#     pdf.drawString(400, 710, f"TERM: {student['term']}")
#     pdf.drawString(50, 690, f"NAME OF STUDENT: {student['name']}")
#     pdf.drawString(250, 690, f"SESSION: {student['session']}")
#     pdf.drawString(400, 690, f"NO. OF TIMES PRESENT: {student['times_present']}")
#     pdf.drawString(50, 670, f"CLASS: {student['class_name']}")
#     pdf.drawString(250, 670, f"NO. OF TIMES SCHOOL OPENED: {student['times_opened']}")

#     # Subject Table Headers
#     pdf.setFont("Helvetica-Bold", 10)
#     y_start = 650
#     headers = ["SUBJECT", "CONTINUOUS ASSESSMENT", "TERM SUMMARY"]
#     pdf.drawString(50, y_start, headers[0])
#     pdf.drawString(200, y_start, headers[1])
#     pdf.drawString(450, y_start, headers[2])

#     # Table Data
#     y = y_start - 20
#     pdf.setFont("Helvetica", 9)

#     for subject in student['subjects']:
#         pdf.drawString(50, y, subject['name'])
#         pdf.drawString(200, y, f"{subject['ca_scores']}")
#         pdf.drawString(450, y, f"{subject['term_summary']}")
#         y -= 20
#         if y < 100:
#             pdf.showPage()
#             y = 750

#     # Footer Section
#     pdf.setFont("Helvetica-Bold", 10)
#     pdf.drawString(50, 80, f"Term Grand Total: {student['grand_total']}")
#     pdf.drawString(250, 80, f"Overall Grade: {student['overall_grade']}")
#     pdf.drawString(400, 80, f"Next Term Begins: {student['next_term']}")

#     # Save the PDF
#     pdf.save()
#     buffer.seek(0)

#     return buffer



# @main.route('/download_result/<int:student_id>')
# def download_result(student_id):
#     # Replace this with actual student data from your database
#     student = {
#         "result_id": "UCS2024/JSS1A/1564460",
#         "name": "Maxwell Oduwa Amadasun",
#         "sex": "Male",
#         "term": "1st Term",
#         "session": "2024/2025",
#         "times_present": 112,
#         "times_opened": 112,
#         "class_name": "JSS 1A",
#         "subjects": [
#             {"name": "English Language", "ca_scores": "10, 20, 15", "term_summary": "GOOD"},
#             {"name": "Mathematics", "ca_scores": "15, 18, 20", "term_summary": "EXCELLENT"},
#             {"name": "Computer Science", "ca_scores": "5, 15, 10", "term_summary": "PASS"},
#             # Add more subjects here...
#         ],
#         "grand_total": 929,
#         "overall_grade": "C",
#         "next_term": "2025-01-06"
#     }

#     pdf_buffer = generate_result_sheet(student)
#     return send_file(
#         pdf_buffer,
#         as_attachment=True,
#         download_name=f"{student['name']}_result.pdf",
#         mimetype='application/pdf'
#     )

from flask import send_file, jsonify
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
# from your_project.models import Student, SubjectScore, db  # Adjust import paths to match your project structure

def generate_result_sheet(student):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    # Title Section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(300, 800, "UNIVERSITY OF BENIN CONSULTANCY SCHOOLS")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(300, 780, "University of Benin, Ekehuan Road Campus, P.M.B. 1154, Benin City")
    pdf.drawCentredString(300, 760, "INDIVIDUAL STUDENT'S ASSESSMENT SHEET")
    pdf.drawCentredString(300, 740, "JUNIOR SECONDARY SCHOOL")

    # Student Details
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 710, f"RESULT ID: {student['result_id']}")
    pdf.drawString(250, 710, f"SEX: {student['sex']}")
    pdf.drawString(400, 710, f"TERM: {student['term']}")
    pdf.drawString(50, 690, f"NAME OF STUDENT: {student['name']}")
    pdf.drawString(250, 690, f"SESSION: {student['session']}")
    pdf.drawString(400, 690, f"NO. OF TIMES PRESENT: {student['times_present']}")
    pdf.drawString(50, 670, f"CLASS: {student['class_name']}")
    pdf.drawString(250, 670, f"NO. OF TIMES SCHOOL OPENED: {student['times_opened']}")

    # Subject Table Headers
    pdf.setFont("Helvetica-Bold", 10)
    y_start = 650
    headers = ["SUBJECT", "CONTINUOUS ASSESSMENT", "TERM SUMMARY"]
    pdf.drawString(50, y_start, headers[0])
    pdf.drawString(200, y_start, headers[1])
    pdf.drawString(450, y_start, headers[2])

    # Table Data
    y = y_start - 20
    pdf.setFont("Helvetica", 9)

    for subject in student['subjects']:
        pdf.drawString(50, y, subject['name'])
        pdf.drawString(200, y, f"{subject['ca_scores']}")
        pdf.drawString(450, y, f"{subject['term_summary']}")
        y -= 20
        if y < 100:
            pdf.showPage()
            y = 750

    # Footer Section
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, 80, f"Term Grand Total: {student['grand_total']}")
    pdf.drawString(250, 80, f"Overall Grade: {student['overall_grade']}")
    pdf.drawString(400, 80, f"Next Term Begins: {student['next_term']}")

    # Save the PDF
    pdf.save()
    buffer.seek(0)

    return buffer


@main.route('/download_result/<int:student_id>')
def download_result(student_id):
    try:
        # Fetch student personal details
        student_record = Student.query.filter_by(id=student_id).first()
        if not student_record:
            return jsonify({"error": "Student not found"}), 404

        # Fetch student academic records
        subjects = AssessmentSubjectScore.query.filter_by(student_id=student_id).all()

        students_assessment = Assessment.query.all()

         # Fetch student academic records
        # students_assessment = Assessment.query.filter_by(assessment_id=assessments).all()
        # students_assessment = Assessment.query.filter(Assessment.id.in_(assessments)).all()
        # students_assessment = Assessment.query.filter_by(id=assessments).all()
        # students_assessment = Assessment.query.filter_by(id=assessments).first()
        # if not students_assessment:
        #     return jsonify({"error": "Assessment not found"}), 404

  



        # Prepare student data
        # student = {
        #     "result_id": student_record.result_id,
        #     "name": f"{student_record.first_name} {student_record.last_name}",
        #     "sex": student_record.sex,
        #     "term": student_record.term,
        #     "session": student_record.session,
        #     "times_present": student_record.times_present,
        #     "times_opened": student_record.times_opened,
        #     "class_name": student_record.class_name,
        #     "subjects": [
        #         {
        #             "name": subject.subject_name,
        #             "ca_scores": ", ".join(map(str, [subject.ca1, subject.ca2, subject.ca3])),
        #             "term_summary": subject.term_summary
        #         }
        #         for subject in subjects
        #     ],
        #     "grand_total": sum(subject.total_score for subject in subjects),
        #     "overall_grade": student_record.overall_grade,
        #     "next_term": student_record.next_term
        # }

        student = {
            "result_id": student_record.student.id,
            "name": f"{student_record.first_name} {student_record.last_name}",
            "sex": student_record.gender,
            "term": students_assessment.term,
            "session": subjects.academic_session,
            # "times_present": student_record.times_present,
            # "times_opened": student_record.times_opened,
            "class_name": student_record.class_name,
            "subjects": [
                {
                    "name": subject.subject_name,
                    "ca_scores": ", ".join(map(str, [subject.ca1, subject.ca2, subject.ca3])),
                    "term_summary": subject.term_summary
                }
                for subject in subjects
            ],
            "grand_total": sum(subject.total_score for subject in subjects),
            "overall_grade": student_record.overall_grade,
            "next_term": student_record.next_term
        }

        # Generate the PDF
        pdf_buffer = generate_result_sheet(student)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{student['name']}_result.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/assign_teachers', methods=['GET', 'POST'])
@login_required
def assign_teachers():
    # Create the form
    form = AssignTeachersForm()

    # Get the classes and teachers for the current school
    classes = Class.query.filter_by(school_id=current_user.school_id).all()
    teachers = Teacher.query.filter_by(school_id=current_user.school_id).all()

    # Populate the form choices dynamically
    form.class_id.choices = [(cls.id, cls.class_name) for cls in classes]
    form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]

    # if form.validate_on_submit():
    #     class_id = form.class_id.data
    #     selected_teacher_ids = form.teacher_ids.data

    #     # Fetch the class and selected teachers
    #     selected_class = Class.query.get(class_id)
    #     selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()

    #     # Add teachers to the class
    #     selected_class.teachers.extend(selected_teachers)

    #     try:
    #         db.session.commit()
    #         flash('Teachers assigned successfully!', 'success')
    #         return redirect(url_for('main.classes'))
    #     except Exception as e:
    #         db.session.rollback()
    #         flash(f'Error assigning teachers: {str(e)}', 'danger')

    if form.validate_on_submit():
        class_id = form.class_id.data
        selected_teacher_ids = form.teacher_ids.data

        # Fetch the class and selected teachers
        selected_class = Class.query.get(class_id)
        selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()

        # Clear existing teachers to avoid duplicates
        selected_class.teachers = []

        # Add new teachers to the class
        selected_class.teachers.extend(selected_teachers)

        try:
            db.session.commit()
            flash('Teachers assigned successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning teachers: {str(e)}', 'danger')


    return render_template('assign_teachers.html', form=form)
