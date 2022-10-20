FROM python:3.8
LABEL maintainer="Azadeh Tavassol"


COPY ./requirements.txt /app/
COPY ./schema.sql /app/
COPY ./*.py /app/
ADD ./static/ /app/static/ 
ADD ./templates/ /app/templates/

WORKDIR /app/
RUN pip install -r requirements.txt

EXPOSE 3111
RUN [ "python", "init_db.py" ]
# command to run on container start
CMD [ "python", "app.py" ]
