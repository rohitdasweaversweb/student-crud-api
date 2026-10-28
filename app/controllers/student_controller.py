from bson import ObjectId
from fastapi import HTTPException, UploadFile
from pathlib import Path
import uuid

from app.models.student_model import student_collection, student_helper
from app.schemas.student_schema import StudentCreate, StudentUpdate


# Image upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image formats
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB


# Save uploaded image
async def save_image(image: UploadFile | None):

    if image is None:
        return None

    if image.content_type not in ALLOWED_TYPES:
        await image.close()
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WebP images are allowed.",
        )

    filename = f"{uuid.uuid4().hex}{ALLOWED_TYPES[image.content_type]}"
    file_path = UPLOAD_DIR / filename

    size = 0

    try:
        with file_path.open("wb") as file:
            while True:
                chunk = await image.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_IMAGE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Image size must not exceed 2 MB.",
                    )

                file.write(chunk)

        return f"uploads/{filename}"

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    finally:
        await image.close()


# 1. Create student
async def create_student(
    student_data: StudentCreate,
    image: UploadFile | None = None,
):

    existing_student = student_collection.find_one(
        {"email": str(student_data.email)}
    )

    if existing_student:
        raise HTTPException(
            status_code=409,
            detail="Student email already exists.",
        )

    image_path = await save_image(image)

    student_dict = student_data.model_dump()
    student_dict["email"] = str(student_data.email)
    student_dict["image"] = image_path

    try:
        result = student_collection.insert_one(student_dict)

        student = student_collection.find_one(
            {"_id": result.inserted_id}
        )

        return student_helper(student)

    except Exception:
        if image_path:
            Path(image_path).unlink(missing_ok=True)
        raise


# 2. Get all students
async def get_all_students():

    students = []

    for student in student_collection.find():
        students.append(student_helper(student))

    return students


# 3. Get student by ID
async def get_student_by_id(student_id: str):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID.",
        )

    student = student_collection.find_one(
        {"_id": ObjectId(student_id)}
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student_helper(student)


# 4. Update student
async def update_student(
    student_id: str,
    student_data: StudentUpdate,
    image: UploadFile | None = None,
):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID.",
        )

    student = student_collection.find_one(
        {"_id": ObjectId(student_id)}
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    update_data = student_data.model_dump(exclude_unset=True)

    if update_data.get("email") is not None:

        update_data["email"] = str(update_data["email"])

        duplicate = student_collection.find_one(
            {
                "email": update_data["email"],
                "_id": {"$ne": ObjectId(student_id)},
            }
        )

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Email already belongs to another student.",
            )

    new_image_path = None

    if image is not None:
        new_image_path = await save_image(image)
        update_data["image"] = new_image_path

    try:
        if update_data:
            student_collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": update_data},
            )

        updated_student = student_collection.find_one(
            {"_id": ObjectId(student_id)}
        )

        if new_image_path and student.get("image"):
            Path(student["image"]).unlink(missing_ok=True)

        return student_helper(updated_student)

    except Exception:
        if new_image_path:
            Path(new_image_path).unlink(missing_ok=True)
        raise


# 5. Delete student
async def delete_student(student_id: str):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID.",
        )

    student = student_collection.find_one(
        {"_id": ObjectId(student_id)}
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    student_collection.delete_one(
        {"_id": ObjectId(student_id)}
    )

    if student.get("image"):
        Path(student["image"]).unlink(missing_ok=True)

    return {
        "message": "Student deleted successfully."
    }