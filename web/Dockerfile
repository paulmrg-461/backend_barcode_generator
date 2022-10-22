FROM python:3.6
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
# expose the port at which we'll run our app
EXPOSE 5050

# sleep to wait for sql server to boot then run our app
CMD sleep 5; python app.py