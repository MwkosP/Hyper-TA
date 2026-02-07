from fastapi import APIRouter

router = APIRouter(prefix="/ml", tags=["TA - Ml"])

@router.get("/")
def utils_root():
    return {"message": "🛠 ML API online"}