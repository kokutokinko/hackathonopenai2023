# Base image
FROM continuumio/anaconda3

# Install Python packages
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
    pip install streamlit && \
    pip install openai

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

# The command to run the app
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
