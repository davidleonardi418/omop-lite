from os import getenv
import pyarrow.parquet as pq
import polars as pl
from pgvector.psycopg import register_vector
from tqdm import tqdm
import psycopg

uri = f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"

vector_length = (
    pl.scan_parquet("embeddings/embeddings.parquet")
    .first()
    .collect()
    .get_column("embeddings")[0]
    .shape[0]
)

conn = psycopg.connect(uri)
print("Connected to database\n")
register_vector(conn)
print("Registered vector type")
cursor = conn.cursor()

cursor.execute(
    f"""
    ALTER TABLE cdm.concept
    ADD COLUMN IF NOT EXISTS embeddings vector({vector_length});
    """
)

conn.commit()

# Open the Parquet file in streaming mode
parquet_file = pq.ParquetFile("embeddings/embeddings.parquet")

# Each row will occupy 8514-ish bytes at the end
# To keep the memory usage below 4 Gb, setting the batch size to 200_000
for batch in tqdm(parquet_file.iter_batches(batch_size=200000)):
    df = (
        pl.DataFrame(batch)
        .select(["concept_id", "embeddings"])
        .with_columns(
            pl.format(
                "[{}]",
                pl.col("embeddings")
                .cast(pl.List(pl.String))
                .list.join(",")
                .alias("embeddings"),
            )
        )
    )
    chunk_size = 10000
    update_query = """
        UPDATE cdm.concept
            SET embeddings = %s
            WHERE concept_id = %s"""

    for row_start in range(0, len(df), chunk_size):
        d_list = [
            (row[1], row[0])
            for row in df[row_start : row_start + chunk_size].iter_rows()
        ]
        cursor.executemany(update_query, d_list)
        conn.commit()
        print(f"Committed {chunk_size} entries")
conn.close()
