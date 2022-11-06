FROM python:3.10.8
WORKDIR /code
COPY ./requirements /code/requirements
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/base.txt
COPY . /code
RUN useradd -ms /bin/bash purplemice
USER purplemice
ENTRYPOINT ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile", "/etc/letsencrypt/live/dr-viewer.online/privkey.pem", "--ssl-certfile", "/etc/letsencrypt/live/dr-viewer.online/fullchain.pem"]