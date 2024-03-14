FROM python:3.7 AS builder

ENV VIRTUAL_ENV=/opt/venv
RUN python3.7 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ADD . /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade cryptography
RUN pip install -U cffi
RUN pip install --target=/app -r requirements.txt


FROM gcr.io/distroless/python3-debian10
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]