import mysql.connector
import click
from flask import current_app, g
from flask.cli import with_appcontext
from .schema import instructions

# Function to get the database connection and cursor
def get_db():
    # Check if the 'db' object is not already stored in the 'g' object (application context)
    if 'db' not in g:
        # Create a database connection using the configuration from the app's config
        g.db = mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'],
            user=current_app.config['DATABASE_USER'],
            password=current_app.config['DATABASE_PASSWORD'],
            database=current_app.config['DATABASE']
        )

        # Create a cursor for executing queries, using dictionary mode (returns results as dictionaries)
        g.c = g.db.cursor(dictionary=True)
    
    # Return the database connection and cursor
    return g.db, g.c 

# Function to close the database connection
def close_db(e=None):
    # Pop the 'db' object from the 'g' object, effectively removing it from the app context
    db = g.pop('db', None)

    # If there was a database connection, close it
    if db is not None:
        db.close()

# Function to initialize the database by executing schema instructions
def init_db():
    db, c = get_db()

    # Iterate through the list of schema instructions and execute each one
    for i in instructions:
        c.execute(i)

    # Commit the changes to the database
    db.commit()

# Command-line command to initialize the database
@click.command('init-db')  # Creates a CLI command named 'init-db'
@with_appcontext            # Ensures access to the Flask app context
def init_db_command():
    init_db()               # Call the function to initialize the database
    click.echo('Base de datos inicializada')


# Function to initialize the app and set up teardown behavior
def init_app(app):
    # Register the 'close_db' function to be called when the app context is torn down
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
