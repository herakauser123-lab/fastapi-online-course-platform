
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Online Course Platform"}

courses = [
    {"id": 1, "title": "Python Basics", "instructor": "John", "price": 1000, "category": "Programming", "is_available": True},
    {"id": 2, "title": "Data Science", "instructor": "Alice", "price": 2000, "category": "Data", "is_available": True},
    {"id": 3, "title": "Web Development", "instructor": "Bob", "price": 1500, "category": "Programming", "is_available": False},
    {"id": 4, "title": "Machine Learning", "instructor": "Sara", "price": 2500, "category": "AI", "is_available": True},
    {"id": 5, "title": "UI UX Design", "instructor": "Emma", "price": 1200, "category": "Design", "is_available": True},
    {"id": 6, "title": "Cyber Security", "instructor": "Mike", "price": 1800, "category": "Security", "is_available": True}
]

enrollments = []
enrollment_counter = 1

class EnrollmentRequest(BaseModel):
    student_name: str
    course_id: int

class NewCourse(BaseModel):
    title: str
    instructor: str
    price: int
    category: str
    is_available: bool = True

def find_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course
    return None

@app.get("/enrollments")
def get_enrollments():
    return {
        "total_enrollments": len(enrollments),
        "enrollments": enrollments
    }


@app.get("/courses")
def get_courses():
    return {
        "total": len(courses),
        "courses": courses
    }

@app.get("/courses/filter")
def filter_courses(
    category: str = None,
    max_price: int = None,
    is_available: bool = None
):
    filtered = courses

    if category is not None:
        filtered = [c for c in filtered if c["category"].lower() == category.lower()]

    if max_price is not None:
        filtered = [c for c in filtered if c["price"] <= max_price]

    if is_available is not None:
        filtered = [c for c in filtered if c["is_available"] == is_available]

    return {
        "total": len(filtered),
        "courses": filtered
    }



@app.get("/courses/summary")
def course_summary():
    total = len(courses)
    available = len([c for c in courses if c["is_available"]])
    unavailable = total - available
    categories = list(set([c["category"] for c in courses]))

    return {
        "total_courses": total,
        "available_courses": available,
        "unavailable_courses": unavailable,
        "categories": categories
    }

@app.post("/courses")
def add_course(course: NewCourse):
    new_id = len(courses) + 1

    # check duplicate title
    for c in courses:
        if c["title"].lower() == course.title.lower():
            return {"error": "Course already exists"}

    new_course = {
        "id": new_id,
        "title": course.title,
        "instructor": course.instructor,
        "price": course.price,
        "category": course.category,
        "is_available": course.is_available
    }

    courses.append(new_course)

    return {
        "message": "Course added successfully",
        "course": new_course
    }

@app.put("/courses/{course_id}")
def update_course(
    course_id: int,
    price: int = None,
    is_available: bool = None
):
    course = find_course(course_id)

    if not course:
        return {"error": "Course not found"}

    if price is not None:
        course["price"] = price

    if is_available is not None:
        course["is_available"] = is_available

    return {
        "message": "Course updated successfully",
        "course": course
    }

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    course = find_course(course_id)

    if not course:
        return {"error": "Course not found"}

    courses.remove(course)

    return {
        "message": "Course deleted successfully",
        "deleted_course": course["title"]
    }

@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    for e in enrollments:
        if e["enrollment_id"] == enrollment_id:
            enrollments.remove(e)
            return {
                "message": "Enrollment removed",
                "student": e["student_name"]
            }

    return {"error": "Enrollment not found"}

@app.get("/enrollments/summary")
def enrollment_summary():
    total = len(enrollments)
    students = list(set([e["student_name"] for e in enrollments]))

    return {
        "total_enrollments": total,
        "unique_students": len(students),
        "students": students
    }

@app.get("/courses/search")
def search_courses(keyword: str):
    result = [
        c for c in courses
        if keyword.lower() in c["title"].lower()
        or keyword.lower() in c["category"].lower()
    ]

    if not result:
        return {"message": "No courses found"}

    return {
        "total_found": len(result),
        "courses": result
    }

@app.get("/courses/sort")
def sort_courses(sort_by: str = "price", order: str = "asc"):
    
    if sort_by not in ["price", "title", "category"]:
        return {"error": "Invalid sort field"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    sorted_courses = sorted(
        courses,
        key=lambda c: c[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "courses": sorted_courses
    }

@app.get("/courses/page")
def paginate_courses(page: int = 1, limit: int = 3):
    
    start = (page - 1) * limit
    end = start + limit

    total = len(courses)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_courses": total,
        "total_pages": total_pages,
        "courses": courses[start:end]
    }

@app.get("/courses/browse")
def browse_courses(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = courses

    # 🔍 FILTER (Search)
    if keyword:
        result = [
            c for c in result
            if keyword.lower() in c["title"].lower()
            or keyword.lower() in c["category"].lower()
        ]

    # 🔄 SORT
    if sort_by in ["price", "title", "category"]:
        result = sorted(
            result,
            key=lambda c: c[sort_by],
            reverse=(order == "desc")
        )

    # 📄 PAGINATION
    start = (page - 1) * limit
    end = start + limit

    total = len(result)
    total_pages = (total + limit - 1) // limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "courses": result[start:end]
    }
@app.get("/enrollments/{enrollment_id}")
def get_enrollment(enrollment_id: int):
    for e in enrollments:
        if e["enrollment_id"] == enrollment_id:
            return e
    return {"error": "Enrollment not found"}

@app.put("/enrollments/{enrollment_id}")
def update_enrollment(enrollment_id: int, student_name: str = None):
    for e in enrollments:
        if e["enrollment_id"] == enrollment_id:
            if student_name is not None:
                e["student_name"] = student_name

            return {
                "message": "Enrollment updated",
                "enrollment": e
            }

    return {"error": "Enrollment not found"}

@app.get("/courses/count")
def course_count():
    return {
        "total_courses": len(courses)
    }

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course
    return {"error": "Course not found"}

@app.post("/enroll")
def enroll_course(request: EnrollmentRequest):
    global enrollment_counter

    # check if course exists
    course = find_course(request.course_id)

    if not course:
        return {"error": "Course not found"}

    # check availability
    if not course["is_available"]:
        return {"error": "Course not available"}

    # create enrollment
    enrollment = {
        "enrollment_id": enrollment_counter,
        "student_name": request.student_name,
        "course_id": request.course_id,
        "course_title": course["title"]
    }

    enrollments.append(enrollment)
    enrollment_counter += 1

    return {
        "message": "Enrollment successful",
        "enrollment": enrollment
    }
