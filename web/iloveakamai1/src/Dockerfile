FROM ubuntu
RUN apt-get update --fix-missing
RUN apt-get install python3 python3-pip -y
RUN pip install flask_jwt_extended flask gunicorn
COPY . .
RUN chmod +x run.sh
EXPOSE 4829
ENTRYPOINT /run.sh