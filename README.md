# Project Techtrends - Azadeh Tavassol
## Project Overview

TechTrends is an online website used as a news sharing platform, that enables consumers to access the latest news within the cloud-native ecosystem. In addition to accessing the available articles, readers are able to create new media articles and share them with the wider community. In this project, you are taking the role of a platform engineer with the main role to package and deploy the application to a Kubernetes platform. Throughout this project, you have used Docker to package the application, and automated the Continuous Integration process with GitHub Actions. For the release process, you have used Kubernetes declarative manifests, which were templated using Helm. To automated the Continuous Delivery process, you have used ArgoCD.

Additionally, the initial sitemap of the website can be found below:
Diagram with the sitemap of the web applciation

Where:

    About page - presents a quick overview of the TechTrends site
    Index page - contains the content of the main page, with a list of all available posts within TechTrends
    New Post page - provides a form to submit a new post
    404 page - is rendered when an article ID does not exist is accessed

And lastly, the first prototype of the application is storing and accessing posts from the "POSTS" SQL table. A post entry contains the post ID (primary key), creation timestamp, title, and content. The "POSTS" table schema can be examined below:


## TechTreds Web Application

This is a Flask application that lists the latest articles within the cloud-native ecosystem.

### Run 

To run this application there are 2 steps required:

1. Initialize the database by using the `python init_db.py` command. This will create or overwrite the `database.db` file that is used by the web application.
2.  Run the TechTrends application by using the `python app.py` command. The application is running on port `3111` and you can access it by querying the `http://127.0.0.1:3111/` endpoint.
