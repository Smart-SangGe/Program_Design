FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Define environment variable
ENV FLASK_APP=app.py

EXPOSE 8000

# Run uWSGI when the container launches
CMD ["uwsgi", "--ini", "config/uwsgi.ini"]
