FROM python:3.9

WORKDIR /C:/Users/simon/PycharmProjects/IoT_project

# Copy the project files into the container
COPY .. .
# Copy the settings file into the container
COPY HomeCatalog_settings.json .
COPY requirements.txt .
COPY MyMQTT.py .
# Install dependencies
RUN pip install -r requirements.txt
