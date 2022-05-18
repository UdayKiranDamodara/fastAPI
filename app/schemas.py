import email
from pydantic import BaseModel

class RegisterStudent(BaseModel):
    name: str
    department_id: int
    programme_id: int
    hometown: str
    roll_no: int
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str

class RequestCourse(BaseModel):
    email: str
    password: str
    course_id: int

class AcceptCouse(BaseModel):
    email: str
    password: str
    course_request_id: int

class Post(BaseModel):
    email: str
    password: str
    post_type: int
    course_id: int
    header: str
    content: str

class Post2(Post):
    isStudent: bool

class Comment(BaseModel):
    email: str
    password: str
    course_id: int
    isStudent: bool
    parent_id: int
    content: str

class getCourses(Login):
    isStudent: bool

class UpdateComment(BaseModel):
    email: str
    password: str
    isStudent: bool
    comment_id: int
    content: str