FROM ubuntu
RUN apt-get update --fix-missing
RUN apt-get upgrade -y
RUN apt-get install python3 python3-pip -y 
RUN pip install flask pysqlite3 werkzeug gunicorn flask_limiter
COPY . . 
RUN chmod +x run.sh
EXPOSE 4446
ENTRYPOINT /run.sh