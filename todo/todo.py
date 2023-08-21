from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)

# Import the 'abort' exception from 'werkzeug.exceptions'
from werkzeug.exceptions import abort

# Import the 'login_required' decorator from your 'auth' module
from todo.auth import login_required

# Import the 'get_db' function from your 'db' module
from todo.db import get_db

# Create a Blueprint named 'todo' with the module's name (__name__)
bp = Blueprint('todo', __name__)

# Define a route for the main page '/'
# Use the 'login_required' decorator to require login
@bp.route('/')
@login_required
def index():
    # Get the database connection and cursor
    db, c = get_db()

    # Execute a query to retrieve task records along with their creators
    c.execute(
        'SELECT t.id, description, completed, created_at, created_by, username'
        ' FROM todo t JOIN user u ON t.created_by = u.id'
        ' ORDER BY created_at DESC'
    )

    # Fetch all resulting records from the query
    todos = c.fetchall()

    # Render the 'todo/index.html' template and pass the list of tasks
    return render_template('todo/index.html', todos=todos)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        description = request.form['description']
        error = None

        if not description:
            error = 'Description is required.'
        
        if error is not None:
            flash(error)
        
        else:
            db, c = get_db()
            c.execute(
                'INSERT INTO todo (description, completed, created_by)'
                ' VALUES (%s, %s, %s)',
                (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')


def get_todo(id):
    db, c = get_db()
    c.execute(
        'SELECT t.id, description, completed, created_at, created_by, username'
        ' FROM todo t JOIN user u ON t.created_by = u.id'
        ' WHERE t.id = %s', (id,)
    )

    todo = c.fetchone()

    if todo is None:
        abort(404, f'Todo id {id} does not exist.'.format(id))

    return todo


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id)

    if request.method == 'POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not description:
            error = 'Description is required.'
        
        if error is not None:
            flash(error)
        
        else:
            db, c = get_db()
            c.execute(
                'UPDATE todo SET description = %s, completed = %s'
                ' WHERE id = %s',
                (description, completed, id)
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo=todo)


@bp.route('/<int:id>/update', methods=['POST'])
@login_required
def delete():
    return render_template('todo/update.html', todo=todo)

