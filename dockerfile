# Base image
FROM continuumio/anaconda3

# Install Python packages
COPY requirements.txt ./ 
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
RUN pip install -r requirements.txt && \
    pip install streamlit

# Create work directory
RUN mkdir -p /home/work
WORKDIR /home/work

EXPOSE 8501

# Streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# The command to run the app
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
