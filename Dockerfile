FROM python:3.9

WORKDIR /C:/Users/simon/PycharmProjects/IoT_project

# Copy the project files into the container
COPY . .
# Copy the settings file into the container
COPY HomeCatalog/HomeCatalog_settings.json .
COPY ResourceCatalog/HomeCatalog_settings.json .
COPY Sensors/HomeCatalog_settings.json .
# Install dependencies
RUN pip install -r requirements.txt

# Run the Python scripts
CMD python HomeCatalog/ManagerHome.py && \
    python ResourceCatalog/ManagerResource_new.py ResourceCatalog/ResourceCatalog_settings.json ResourceCatalog/ResourceCatalog_info.json && \
    python Sensors/RoomTemperatureControl.py Sensors/Room_Temperature_settings.json && \
    python RoomTemperature.py Room_Temperature_settings.json && \
    python HeartRate.py HeartRate_settings.json