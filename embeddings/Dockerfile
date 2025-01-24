FROM python:3.13-bookworm

RUN pip install --no-cache duckdb --upgrade

COPY embeddings.parquet /embeddings.parquet
COPY load_embeddings.py /load_embeddings.py

ENTRYPOINT ["python", "load_embeddings.py"]
