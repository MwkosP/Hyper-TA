from fastapi import FastAPI

#?--------------------------------------------------
#? TA imports
#?--------------------------------------------------
from src.ta.api import (
    routes_data as ta_data,
    routes_functions as ta_functions,
    routes_ml as ta_ml,
    routes_strategies as ta_strategies,
    routes_backtesting as ta_backtesting,
    routes_utils as ta_utils,
)


# (later you can add OP, FA, etc.)
# from src.op.api import routes_data as op_data, routes_functions as op_functions, ...
# from src.fa.api import routes_data as fa_data, ...

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quant Backend", docs_url="/docs", redoc_url="/redoc")

origins = [
    "http://localhost:5173/",   # React dev server (Vite)
    "http://127.0.0.1:5173/",
    ""  # για δοκιμές επιτρέπει τα πάντα (βγάλτο σε production)
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],   # επιτρέπει όλα τα HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],   # επιτρέπει όλα τα headers
)


@app.get("/", tags=["ROOT"])
def root():
    return {"message": "✅ Quant FastAPI backend running"}

# TA Routers
app.include_router(ta_data.router, prefix="/ta")
app.include_router(ta_functions.router, prefix="/ta")
app.include_router(ta_ml.router, prefix="/ta")
app.include_router(ta_strategies.router, prefix="/ta")
app.include_router(ta_backtesting.router, prefix="/ta")
app.include_router(ta_utils.router, prefix="/ta")







#?--------------------------------------------------
#? OP Routers (when ready)
#?--------------------------------------------------
# app.include_router(op_data.router, prefix="/op")
# app.include_router(op_functions.router, prefix="/op")

# FA Routers (when ready)
# app.include_router(fa_data.router, prefix="/fa")
