# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the server application files to the working directory
COPY . .

# Install server dependencies
RUN pip install -r requirements.txt

# Expose port 80
EXPOSE 80

# Command to run the server
CMD ["python", "todo.py"]
