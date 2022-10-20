import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

import os 

connection_counter = 0  #counter to count the connections to db
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_counter
    try:
        if os.path.exists("database.db"):
            connection = sqlite3.connect("database.db")
        else:
            raise RuntimeError('Database error! file database.db not found')
    except sqlite3.OperationalError:
        logging.error('Delete Database.db and run python init_db.py.')
    connection.row_factory = sqlite3.Row
    connection_counter = connection_counter + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('index (main page) request successfull')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error(f"Article with ID {post['ID']} not found, page 404 accessed.")
      return render_template('404.html'), 404
    else:
      app.logger.debug(f"Article with title \"{post['title']}\" is retrieved.")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f"About request successful")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.debug(f"A new article with title \"{title}\" is added")
            return redirect(url_for('index'))

    return render_template('create.html')

# Defines the healthz endpoint - returning:
#   - An HTTP 200 status code
#   - A JSON response containing the result: OK - healthy message
@app.route('/healthz')
def healthcheck():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
        )   
        app.logger.info('healthz request successfull')
        return response
    except Exception:
        response = app.response_class(
                response=json.dumps({"result":"ERROR - unhealthy"}),
                status=500,
                mimetype='application/json'
        )   
        return response
# Defines the metrics endpoints - returns
#   - An HTTP 200 status code
#   - A JSON response with the following metrics:
#       - Total amount of posts in the database
#       - Total amount of connections to the database. For example, 
#         accessing an article will query the database, hence will count as a connection 
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": connection_counter, "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('metrics request successfull')
    return response  

# start the application on port 3111
if __name__ == "__main__":
    ## stream logs to app.log file
    logging.basicConfig(level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
