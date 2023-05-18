# Base image
# Use the Ubuntu base image
FROM ubuntu

# Update package lists and install necessary dependencies
RUN apt-get update && apt-get install -y wget gnupg python3 python3-pip

# Download and install Google Chrome
RUN apt -f install -y
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb -y

# Set working directory
WORKDIR /app

# Copy requirements.txt file
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask server code into the container
COPY ./flask_app /app/flask_app

# Copy history dir
COPY ./history /app/history

EXPOSE 5001

# Start the Flask server
CMD ["python3", "-m", "flask", "-A", "flask_app/main", "run", "-h", "0.0.0.0", "-p", "5001"]