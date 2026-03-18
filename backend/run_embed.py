# This script is used to run the embedding process for existing documents in the database.
from app.api.ingest import embed_existing

if __name__ == "__main__":
    result = embed_existing()
    print(result)