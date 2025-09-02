# Dockerfile

# Step 1: Start with a basic Linux computer that has Python 3.9 installed.
FROM python:3.9-slim

# Step 2: Set the working directory inside the container to /app.
WORKDIR /app

# Step 3: Install the Supervisor program into the container's operating system.
RUN apt-get update && apt-get install -y supervisor

# Step 4: Copy ONLY the requirements file first.
# (This is a Docker optimization: if this file doesn't change, Docker can skip reinstalling libraries on future builds.)
COPY requirements.txt .

# Step 5: Install all the Python libraries from the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Now, copy all of your project files (like the 'app' folder) into the container.
COPY . .

# Step 7: Copy your Supervisor configuration file into the location where Supervisor expects to find it.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Step 8: Set the default command for the entire container.
# This tells Docker to start Supervisor, which will then start your two Python scripts.
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]