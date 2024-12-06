# Use a lightweight Python image
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /WellTrack

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY ./WellTrack /WellTrack
# COPY wait-for-it.sh /wait-for-it.sh
# RUN chmod +x /wait-for-it.sh

# Install dependencies
RUN pip install -r requirements.txt
RUN pip install tensorflow-cpu

# --no-cache-dir
# Expose application port
EXPOSE 8000


# Command to run the app python manage.py runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
