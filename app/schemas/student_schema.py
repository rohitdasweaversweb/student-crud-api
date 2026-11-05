from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=5, le=100)
    course: str = Field(..., min_length=2, max_length=100)
    marks: float = Field(..., ge=0, le=100)


class StudentUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(None, ge=5, le=100)
    course: str | None = Field(None, min_length=2, max_length=100)
    marks: float | None = Field(None, ge=0, le=100)


class StudentResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: int
    course: str
    marks: float
    image: str 