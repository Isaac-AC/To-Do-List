import functools
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from todo.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Route for user registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        
        # Check if the username is already registered
        c.execute(
            'SELECT id FROM user WHERE username = %s', (username,)
            )
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif c.fetchone() is not None:
            error = f'Username "{username}" is already registered.'
        
        if error is None:
            # Insert new user into the database
            c.execute(
                'INSERT INTO user (username, password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))
    
        flash(error)
    return render_template('auth/register.html')

# Route for user login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        
        # Retrieve user information from the database
        c.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = c.fetchone()

        if user is None:
            error = 'Invalid username and/or password'
        elif not check_password_hash(user['password'], password):
            error = 'Invalid username and/or password'
        
        if error is None:
            # Store user ID in session after successful login
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    # Load user information from the database into the 'g' object
    user_id = session.get('user_id')
    db, c = get_db()
    
    if user_id is None:
        g.user = None
    else:
        c.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        g.user = c.fetchone()


def login_required(view):
    # Decorator to check if user is logged in
    # If not, redirect to login page
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view
