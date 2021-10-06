FROM python:3.7
ENV PYTHONUNBUFFERED 1
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

RUN python run_app.py -ac config.json migrate --init
RUN python run_app.py -ac config.json migrate --migrate
RUN python run_app.py -ac config.json migrate --upgrade

CMD ["python", "run_app.py", "-ac", "config.json"]