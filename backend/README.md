ragini/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── ingest.py
│   │   │   ├── query.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── supabase_service.py
│   │   │   ├── chunk_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── semantic_cache_service.py
│   │   │   ├── scaledown_service.py
│   │   │   └── llm_service.py
│   │   │
│   │   ├── db/
│   │   │   ├── mongo.py
│   │   │   ├── postgres.py
│   │   │   └── models.py
│   │   │
│   │   └── utils/
│   │       ├── text_cleaner.py
│   │       └── tokenizer.py
│   │ 
│   │
│   ├── .env
│   ├── requirements.txt
│   └── README.md
│
└── frontend/ (later)




pip install fastapi uvicorn
pip install pytesseract pdf2image  pymupdf pillow
pip install supabase python-dotenv


pip install pymongo            psycopg2-binary

pip install pinecone
pip install google-genai
pip install redis redisvl


pip install authlib python-jose[cryptography] sqlalchemy psycopg2-binary 

pip install itsdangerous