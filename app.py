import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

import os 
import sys

# Define the Flask application
app = Flask(__name__)
app.config['connection_counter'] = 0


def get_db_connection():
    ''' 
    Function to get a database connection. 
    This function connects to database with the name database.db 
    '''
    try:
        if os.path.exists("database.db"):
            connection = sqlite3.connect("database.db")
        else:
            raise RuntimeError('Database error! file database.db not found')
    except sqlite3.OperationalError:
        logging.error('Delete Database.db and run python init_db.py.')
    connection.row_factory = sqlite3.Row
    app.config['connection_counter'] = app.config['connection_counter'] + 1
    return connection

def get_post(post_id):
    '''
    Function to get a post using its ID
    '''
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

@app.route('/')
def index():
    '''
    Define the main route of the web application @app.route('/')
    '''
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('index (main page) request successfull')
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    '''
    Define how each individual article is rendered 
    If the post ID is not found a 404 page is shown
    '''
    post = get_post(post_id)
    if post is None:
      app.logger.error(f"Article with ID {post['ID']} not found, page 404 accessed.")
      return render_template('404.html'), 404
    else:
      app.logger.debug(f"Article with title \"{post['title']}\" is retrieved.")
      return render_template('post.html', post=post)

@app.route('/about')
def about():
    '''
    Define the About Us page
    '''
    app.logger.info(f"About request successful")
    return render_template('about.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    '''
    Define the post creation functionality 
    '''
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

@app.route('/healthz')
def healthcheck():
    '''
    Defines the healthz endpoint - returning:
       - An HTTP 200 status code
       - A JSON response containing the result: OK - healthy message
    '''
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

@app.route('/metrics')
def metrics():
    '''
    Defines the metrics endpoints - returns
       - An HTTP 200 status code
       - A JSON response with the following metrics:
           - Total amount of posts in the database
           - Total amount of connections to the database. For example, 
             accessing an article will query the database, hence will count as a connection 
    '''
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": app.config['connection_counter'], "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('metrics request successfull')
    return response  

# start the application on port 3111
if __name__ == "__main__":

    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)# stdout handler `
    stderr_handler =  logging.FileHandler(filename='app.log')# stderr handler 
    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = '%(asctime)s %(message)s'
    ## stream logs to app.log file
    logging.basicConfig(handlers=handlers, format=format_output,level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
