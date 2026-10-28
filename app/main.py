from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.student_routes import router as student_router


app = FastAPI(
    title="Student Management API",
    description="Student CRUD API with Image Upload",
    version="1.0.0",
)


# Create uploads folder
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Serve uploaded images
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)


# Register student routes
app.include_router(student_router)


@app.get("/")
async def home():
    return {
        "message": "Student Management API is running"
    }