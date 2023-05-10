from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard

app = FastAPI(
  title="GarmentWise",
  description="This API allows users to get insights on their clothing reviews",
  version="1.0.0"
)

app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")

origins = [
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)