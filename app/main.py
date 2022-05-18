from fastapi import FastAPI, HTTPException, status
import mysql.connector
from mysql.connector import Error
import time

from requests import request

from . import schemas
from . import auth

import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()

while True:
    try:
        print('trying to connect')
        conn = mysql.connector.connect(host='localhost',
                                        database='forum',
                                        user='root',
                                        password='9719')
        if conn.is_connected():
            cursor = conn.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)

            print('connection successful')
            # cursor.execute('''SELECT * FROM departments;''')
            # data = cursor.fetchall()
            # print(data)
        break
    
    except Error as error:
        time.sleep(2)

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastApi', user='postgres', password='9719', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('connection successful')
#         break
#     except Exception as error:
#         print('connection to db failed')
#         print(error)
#         time.sleep(2)



@app.post('/login/student')
async def login(payload: schemas.Login):
    student = auth.loginStudent(cursor, conn, payload.email, payload.password)
    print(student)
    if student == 0 or student == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')
    else:
        return {'message': 'login successful'}

@app.post('/login/instructor')
async def loginI(payload: schemas.Login):
    temp = auth.loginInstructor(cursor, conn, payload.email, payload.password)
    print(temp)
    if temp == 0 or temp == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')
    else:
        return {'message': 'login successful'}
    # if login==1:
    #     return {'message': 'login successful'}
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')

    # print(payload)
    # # cursor.execute(f'''
    # #     SELECT * FROM users WHERE roll_number={payload.roll_no};
    # # ''')
    # # query_data = cursor.fetchone()
    # # conn.commit()
    # query_data = auth.loginStudent(cursor, conn, payload)


    # # data = [dict(zip(cursor.column_names, x)) for x in query_data]
    # # print(query_data)
    # if query_data is None: 
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')

    # data = dict(zip(cursor.column_names, query_data))    
    # # print(data)
    
    # if data['password']!=payload.password:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')

    # return {'msg': 'login successful'}

@app.post('/register/student')
async def register(payload: schemas.RegisterStudent):
    check_rno = auth.checkRollNoExists(cursor, conn, payload.roll_no)
    if check_rno:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='roll number already exists')
    
    check_email = auth.checkEmailExists(cursor, conn, payload.email)
    if check_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exists')

    register_student = auth.registerStudent(cursor, conn, payload)
    if register_student:
        return {'message': 'successfully registered'}
    else:
        return {'message': 'Error occured, please try again'}


@app.post('/request')
async def requestCourse(payload: schemas.RequestCourse):
    temp = auth.requestCourse(cursor, conn, payload)
    if temp==5:
        return {'message': 'course successfully requested'}
    if temp==-1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorized')
    if temp==1:
        return {'message': 'course already requested'}
    if temp==2:
        return {'message': 'course accepted'}

    if temp==3:
        return {'message': 'course rejected cannot request again'}

@app.post('/accept')
async def acceptCourse(payload: schemas.AcceptCouse):
    temp = auth.acceptCourse(cursor, conn, payload)
    if temp == 1:
        return {'message': 'accepted'}

    if temp == 2:
        return {'message': 'course already accepted'}
    
    if temp == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')

    if temp == -2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='no such course request exists')

    if temp == -3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you are not the course instructor!')

@app.post('/announcement')
async def announcement(payload: schemas.Post):
    temp = auth.addAnnouncement(cursor, conn, payload)
    if temp == 1:
        return {'message': 'Success'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='An error occured')

@app.post('/post')
async def post(payload: schemas.Post2):
    temp = auth.addPost(cursor, conn, payload)
    if temp == 1:
        return {'message': 'Success'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='An error occured')

@app.post('/comment')
async def comment(payload: schemas.Comment):
    temp = auth.addComment(cursor, conn, payload)
    if temp ==1:
        return {'message': 'Success'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='An error occured')

@app.get('/courses')
async def courses(payload: schemas.getCourses):
    temp = auth.getCourses(cursor, conn, payload)
    if temp == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')
    else:
        return {
            'data': temp
        }

@app.get('/courses/{id}')
async def courseDetails(payload: schemas.getCourses, id):
    print(id)
    temp = auth.getCourseDetails(cursor, conn, payload, id)
    if temp == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')
    else:
        return {
            'data': temp
        }

@app.patch('/comment')
async def updateComment(payload: schemas.UpdateComment):
    temp = auth.updateComment(cursor, conn, payload)
    if temp == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credentials')
    if temp == -2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorized')
    if temp == 1:
        return {'message': 'updated'}

# @app.post('/check')
# async def temp(payload: schemas.getCourses):
#     print('processing')
#     user = auth.checkRollNoExists(cursor, conn, payload)
#     print(user)