from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["TA - Utils"])

@router.get("/")
def utils_root():
    return {"message": "🛠 Utils API online"}

@router.get("/config")
def get_config():
    return {"config": "current settings"}

@router.get("/logs")
def get_logs():
    return {"logs": ["log1", "log2", "log3"]}
