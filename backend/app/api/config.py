# backend/app/api/config.py
from fastapi import APIRouter, HTTPException
from app.services.ocr_service import supabase
import os

router = APIRouter(prefix="/config", tags=["Config"])

BUCKET = os.getenv("SUPABASE_BUCKET", "CBSE_BOOKS")


@router.get("/subjects")
def get_subjects():
    """
    Reads class and subject structure directly from Supabase bucket.
    No hardcoding needed — automatically reflects any new folders added.
    """
    try:
        result = {}

        # List all class folders
        class_folders = supabase.storage.from_(BUCKET).list()

        for class_folder in class_folders:
            class_name = class_folder["name"]

            # List subject folders inside each class
            subject_folders = supabase.storage.from_(BUCKET).list(class_name)

            result[class_name] = {}

            for subject_folder in subject_folders:
                subject_name = subject_folder["name"]
                # key = exact folder name, value = formatted display name
                display = subject_name.replace("-", " ").replace("_", " ").title()
                result[class_name][subject_name] = display

        return {
            "classes": {k: k.replace("_", " ").title() for k in result.keys()},
            "subjects": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {str(e)}")