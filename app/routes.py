# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from . import db
from .forms import TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm
from .models import User, Student, Teacher, Class, Grade, Attendance
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
import pandas as pd
from docx import Document


# Create a Blueprint instance
main = Blueprint('main', __name__)
# Login route

@main.route('/')
def index():
    return render_template('index.html')


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

@main.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            subject=form.subject.data,
            email=form.email.data,
            phone=form.phone.data,
            hire_date=form.hire_date.data

        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!')
        return redirect(url_for('main.teachers'))
    return render_template('add_teacher.html', form=form)


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

