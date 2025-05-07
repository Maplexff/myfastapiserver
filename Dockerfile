FROM python:3.10

WORKDIR /MyFastApi

COPY ./requirements.txt /MyFastApi/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /MyFastApi/requirements.txt

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6

COPY ./myfastapi .

CMD ["uvicorn", "fastapimain:app", "--host", "0.0.0.0", "--port", "8000"]