# This script is used to run the ingestion process for existing documents in the database.
from app.api.ingest import ingest_all

if __name__ == "__main__":
    result = ingest_all()
    print(result)