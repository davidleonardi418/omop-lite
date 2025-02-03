from os import getenv
import adbc_driver_postgresql.dbapi
import psycopg2
from pgvector.psycopg2 import register_vector
from tqdm import tqdm
import polars as pl
import pyarrow.parquet as pq


# uri = f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
uri = "postgresql://postgres:password@localhost:5432/omop"

with psycopg2.connect(uri) as con:
    print("\nConnected to database\n")
    register_vector(con)
    cursor = con.cursor()
    parquet_file = pq.ParquetFile("embeddings.parquet")
    print("Got parquet")

    embeddings = pl.scan_parquet("embeddings.parquet")
    vector_length = embeddings.first().collect().get_column("embeddings")[0].shape[0]

    cursor.execute(
        f"""
        CREATE TEMP TABLE temp_parquet_data (
            concept_id INTEGER,
            embeddings vector({vector_length})
        );
    """
    )

    con.commit()

    # Each row will occupy 8514-ish bytes at the end
    # To keep the memory usage below 4 Gb, setting the batch size to 200_000
    for n, batch in tqdm(
        enumerate(parquet_file.iter_batches(batch_size=200000))
    ):  # Iterate through batches
        print(f"\nProcessing batch {n}")
        (
            pl.DataFrame(batch)
            .select(["concept_id", "embeddings"])
            .with_columns(
                pl.format(
                    "[{}]",
                    pl.col("embeddings").cast(pl.List(pl.String)).list.join(","),
                )
            )
            .write_database(
                table_name="cdm.temp_parquet_data",
                connection=uri,
                engine="adbc",
                if_table_exists="append",
            )
        )

        print(f"Processed batch {n}")
        con.commit()

        cursor.execute(
            """
            UPDATE cdm.concept c
                SET embedding = tpd.embeddings
                FROM temp_parquet_data tpd
                WHERE c.concept_id = tpd.concept_id;
            """
        )  # Commit after processing each batch for performance
        con.close()
