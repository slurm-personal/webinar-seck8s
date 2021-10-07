FROM python:3.8-slim

WORKDIR /opt/workdir

COPY requirements.txt requirements.txt
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app.py app.py
COPY templates/ templates/
# TODO: move DB to a separate postgres service
COPY Database.db Database.db

EXPOSE 8080
# CMD ["flask", "run"]
CMD ["python", "app.py"]
