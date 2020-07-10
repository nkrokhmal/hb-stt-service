FROM python:3.6

WORKDIR /app


#RUN pip install --upgrade pip \
#    && pip install -r requirements.txt
RUN wget https://alphacephei.com/kaldi/models/vosk-model-ru-0.10.zip \
    && unzip vosk-model-ru-0.10.zip \
    && mv vosk-model-ru-0.10 model \
    && rm vosk-model-ru-0.10.zip
RUN mkdir -p /opt \
    && chmod -R 777 /opt/ \
    && mkdir -p /opt/download \
    && chmod -R 777 /opt/download
COPY . .
EXPOSE 53456
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
CMD ["python", "-u", "run.py"]
