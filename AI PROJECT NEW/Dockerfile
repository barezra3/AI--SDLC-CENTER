# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Make port 8501 available to the world outside this container (Streamlit default)
EXPOSE 8501

# 7. Define environment variables for Streamlit to run headlessly
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 8. Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]