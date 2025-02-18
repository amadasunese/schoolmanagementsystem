from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def school_required(model, school_field="school_id"):
    """Decorator to restrict access to objects linked to the logged-in user's school."""
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "warning")
                return redirect(url_for('main.index'))

            if not current_user.school_id:
                flash("You are not linked to any school.", "warning")
                return redirect(url_for('main.dashboard'))

            # Fetch the requested object from the database
            obj = model.query.get(kwargs.get("id"))
            if not obj:
                flash("Requested resource not found.", "danger")
                return redirect(url_for('main.dashboard'))

            # Check if the object's school_id matches the user's school_id
            if getattr(obj, school_field) != current_user.school_id:
                flash("You do not have permission to access this resource.", "danger")
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return wrapped_function
    return decorator


def filter_by_school(model, school_field="school_id"):
    """Decorator to filter query results so that users only see data from their school."""
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "warning")
                return redirect(url_for('main.index'))

            if not current_user.school_id:
                flash("You are not linked to any school.", "danger")
                return redirect(url_for('main.dashboard'))

            # Modify the function to return only data linked to the user's school
            filtered_data = model.query.filter_by(**{school_field: current_user.school_id})

            return f(filtered_data, *args, **kwargs)
        return wrapped_function
    return decorator