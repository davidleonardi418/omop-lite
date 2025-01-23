# omop-lite

A small container to get an OMOP CDM Postgres database running quickly.

Drop your data into `data/`, and run the container.

## Environment Variables

You can configure the Docker container using the following environment variables:

- `DB_HOST`: The hostname of the PostgreSQL database. Default is `db`.
- `DB_PORT`: The port number of the PostgreSQL database. Default is `5432`.
- `DB_USER`: The username for the PostgreSQL database. Default is `postgres`.
- `DB_PASSWORD`: The password for the PostgreSQL database. Default is `password`.
- `DB_NAME`: The name of the PostgreSQL database. Default is `omop`.
- `SCHEMA_NAME`: The name of the schema to be created/used in the database. Default is `omop`.
- `DATA_DIR`: The directory containing the data CSV files. Default is `data`.

## Usage

`docker run -v ./data:/data ghcr.io/AndyRae/omop-lite`

```yaml
# docker-compose.yml
services:
  omop-lite:
    image: ghcr.io/health-informatics-uon/omop-lite
    volumes:
      - ./data:/data
    depends_on:
      - db

  db:
    image: postgres:latest
    environment:
      - POSTGRES_DB=omop
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
```

## Bring Your Own Data

You can provide your own data for loading into the tables by placing your CSV files in the `data/` directory. This should contain `.csv` files matching the data tables (`DRUG_STRENGTH.csv`, `CONCEPT.csv`, etc.).

## Setup Script

The `setup.sh` script included in the Docker image will:

1. Create the schema if it does not already exist.
2. Execute the SQL files to set up the database schema, constraints, and indexes.
3. Load data from the `.csv` files located in the `DATA_DIR`.
