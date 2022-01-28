FROM python:3.9

WORKDIR /usr/share/app
RUN pip install requests
COPY realm-export.json main.py ./

CMD ["python", "main.py"]