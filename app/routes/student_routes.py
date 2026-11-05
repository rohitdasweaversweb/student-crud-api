from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.controllers import student_controller
from app.schemas.student_schema import StudentCreate, StudentUpdate


router = APIRouter(
    prefix="/api/v1/students",
    tags=["Students"],
)


# 1. Create student
@router.post("/")
async def create_student(
    name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    course: str = Form(...),
    marks: float = Form(...),
    image: UploadFile = File(...),
):

    try:
        student_data = StudentCreate(
            name=name,
            email=email,
            age=age,
            course=course,
            marks=marks,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_url=False),
        )

    return await student_controller.create_student(
        student_data,
        image,
    )


# 2. Get all students
@router.get("/")
async def get_all_students():

    return await student_controller.get_all_students()


# 3. Get student by ID
@router.get("/{student_id}")
async def get_student(student_id: str):

    return await student_controller.get_student_by_id(student_id)


# 4. Update student
@router.put("/{student_id}")
async def update_student(
    student_id: str,
    name: str | None = Form(None),
    email: str | None = Form(None),
    age: int | None = Form(None),
    course: str | None = Form(None),
    marks: float | None = Form(None),
    image: UploadFile | None = File(None),
):

    update_fields = {
        "name": name,
        "email": email,
        "age": age,
        "course": course,
        "marks": marks,
    }

    # Keep only the fields supplied by the user
    update_data = {
        key: value
        for key, value in update_fields.items()
        if value is not None
    }

    try:
        student_data = StudentUpdate(**update_data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_url=False),
        )

    return await student_controller.update_student(
        student_id,
        student_data,
        image,
    )


# 5. Delete student
@router.delete("/{student_id}")
async def delete_student(student_id: str):

    return await student_controller.delete_student(student_id)