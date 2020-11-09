FROM python:3.6
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python setup.py install
RUN chmod +x /app/bin/get-ec2-password
ENV PYTHONPATH /app
ENTRYPOINT ["/app/bin/get-ec2-password"]
