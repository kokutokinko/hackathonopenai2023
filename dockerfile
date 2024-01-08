# Base image
FROM continuumio/anaconda3


# Install Python packages
COPY requirements.txt ./ 
RUN pip install --upgrade pip && pip install -r requirements.txt



# Generate Jupyter notebook config
RUN jupyter notebook --generate-config
WORKDIR /root/.jupyter
RUN echo 'c.NotebookApp.allow_root = True' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.ip = "0.0.0.0"' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.token = ""' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.port = 8889' >> jupyter_notebook_config.py && \
    echo 'c.NotebookApp.open_browser = False' >> jupyter_notebook_config.py

# Create work directory
RUN mkdir -p /home/work
WORKDIR /home/work

# Start Jupyter Lab
CMD ["jupyter","lab"]