FROM python:3.7
RUN apt-get update && apt-get install -y git python3-pip && \
	pip install pydub

COPY main.py /data
COPY config.ini /data
	
WORKDIR /data
ENTRYPOINT ["python", "-u", "main.py"]