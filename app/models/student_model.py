from bson import ObjectId
from app.database.mongodb import database


student_collection = database["students"]


def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "email": student["email"],
        "age": student["age"],
        "course": student["course"],
        "marks": student["marks"],
        "image": student.get("image"),
    }