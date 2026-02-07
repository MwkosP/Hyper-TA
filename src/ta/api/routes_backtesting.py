from fastapi import APIRouter

router = APIRouter(prefix="/backtesting", tags=["TA - Backtesting"])

@router.get("/")
def utils_root():
    return {"message": "🛠 Backtesting API online"}