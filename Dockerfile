# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# we need ffmpeg, lets install it
RUN apt update -y && apt install ffmpeg -y

# install a pre-release version of numba
RUN pip install --pre numba

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

ENV BOT_TOKEN="empty"
ENV TRANSCRIBE_ENGINE="whisper"
ENV TRANSCRIBE_APIKEY="0"
ENV TRANSCRIBE_AUTOMATICALLY="false"
ENV TRANSCRIBE_VMS_ONLY="true"
ENV ADMIN_USERS="0, 1, 2"
ENV ADMIN_ROLE="0"

ENTRYPOINT ["python"]

# Set the container command to run your application
CMD ["main.py"]

