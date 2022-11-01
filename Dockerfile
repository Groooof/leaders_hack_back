FROM python:3.7
WORKDIR /code
COPY ./requirements /code/requirements
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/base.txt
COPY . /code
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]