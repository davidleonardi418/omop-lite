from os import getenv
import duckdb


vector_length = duckdb.sql(
    """
    SELECT array_length(embeddings[1]) 
    FROM 'embeddings.parquet'
"""
).fetchone()[0]


with duckdb.connect() as con:
    con.sql(
        f"""
    INSTALL postgres;
    LOAD postgres;
    ATTACH '
    dbname={getenv("DB_NAME")}
    hostaddr={getenv("DB_HOST")}
    port={getenv("DB_PORT")}
    user={getenv("DB_USER")}
    password={getenv("DB_PASSWORD")}
    ' AS db (TYPE postgres, SCHEMA {getenv("SCHEMA_NAME")})
    """
    )

    con.sql(
        f"""
    ALTER TABLE db.concept
    ADD COLUMN IF NOT EXISTS embedding vector({vector_length})
    """
    )

    con.sql(
        """
    UPDATE db.concept c
    SET embedding = e.embeddings
    FROM (
        SELECT concept_id, embeddings 
        FROM 'embeddings.parquet'
    ) e
    WHERE c.concept_id = e.concept_id
    """
    )
