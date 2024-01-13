# Base image
FROM continuumio/anaconda3

# Install Python packages
COPY requirements.txt ./  
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
    pip install -r requirements.txt && \
    

# Create work directory
RUN mkdir -p /home/work
WORKDIR /home/work

EXPOSE 8501

# Streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Set environment variables for Azure OpenAI
ENV AZURE_OPENAI_KEY="a39dc5505f15492aa3d8962b153bd149"
ENV AZURE_OPENAI_ENDPOINT="https://sunhackathon45.openai.azure.com/"

RUN jupyter notebook --generate-config
WORKDIR /root/.jupyter
RUN echo 'c.NotebookApp.allow_root = True' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.ip = "0.0.0.0"' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.token = ""' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.port = 8889' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.open_browser = False' >> jupyter_notebook_config.py

# The command to run the app
WORKDIR /home/work
CMD ["jupyter","lab"]
