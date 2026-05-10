FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8787

WORKDIR /app

RUN useradd --create-home --shell /bin/bash sentinel

COPY app ./app
COPY web ./web
COPY samples ./samples
COPY README.md PRODUCT_BRIEF.md ./

RUN mkdir -p /app/out/audits && chown -R sentinel:sentinel /app/out

USER sentinel

EXPOSE 8787

CMD ["python", "app/server.py", "--host", "0.0.0.0"]

