FROM python:3.8

RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "wsgi.py"]
