def getDepartmentID(cursor, conn, payload):
    cursor.execute(f'''
        SELECT * FROM 
    ''')

def getProgramID(cursor, conn, payload):
    cursor.execute(f'''
        SELECT * FROM 
    ''')

def getStudentID(cursor, conn, email):
    cursor.execute('''
        SELECT * FROM students where email=(%s);
    ''', [email])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data:
        data = dict(zip(cursor.column_names, query_data))
        print('getStudentID data: ', data)
        return data['id']
    else:
        return -1

def getCourseIDfromCourseRequests(cursor, conn, course_request_id):
    cursor.execute('''
        SELECT * FROM course_requests WHERE id=(%s);
    ''', [course_request_id])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data:
        data = dict(zip(cursor.column_names, query_data))
        print(data)
        return data
    else:
        return -1

def checkInstructorForCourse(cursor, conn, instructor_id, course_id):
    cursor.execute('''
        SELECT * FROM courses WHERE id=(%s);
    ''', [course_id])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data:
        data = dict(zip(cursor.column_names, query_data))
        if(data['instructor_id']==instructor_id):
            return 1 # authorized
        else:
            return -2 # not the right instructor
    else:
        return -1 # no such course id ==> no such course

def checkStudentForCourse(cursor, conn, student_id, course_id):
    cursor.execute('''
        SELECT * FROM course_requests WHERE course_id=(%s) AND student_id=(%s);
    ''',[course_id, student_id])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data:
        data = dict(zip(cursor.column_names, query_data))
        if data['status']==2:
            return 1 # authorized
        else:
            return -2 # status either requested or rejected
    else:
        return -1 # no entry

def getAllCourses(cursor, conn):
    cursor.execute('''
        SELECT * FROM courses;
    ''')
    query_data = cursor.fetchall()
    print('all courses',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getStudentCourses(cursor, conn, studentID):
    cursor.execute('''
        SELECT * FROM course_requests WHERE student_id=(%s) AND status=2
    ''', [studentID])
    query_data = cursor.fetchall()
    print('all courses',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getInstructorCourses(cursor, conn, instructor_id):
    cursor.execute('''
        SELECT * FROM courses WHERE instructor_id=(%s);
    ''',[instructor_id])
    query_data = cursor.fetchall()
    print('all courses',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getCourseRequests(cursor, conn, course_id):
    cursor.execute('''
        SELECT c.id, c.student_id, s.name, s.department_id, d.code, s.programme_id, p.code, c.course_id, c.status 
        FROM course_requests as c
        JOIN students as s on c.student_id=s.id
        JOIN departments as d ON s.department_id=d.id
        JOIN programmes as p ON s.programme_id=p.id
        WHERE c.course_id=(%s);
    ''', [course_id])
    query_data = cursor.fetchall()
    print('all courses',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getAnnouncements(cursor, conn, course_id):
    cursor.execute('''
        SELECT * FROM posts WHERE post_type_id=1 AND course_id=(%s) ORDER BY created_at;
    ''',[course_id])
    query_data = cursor.fetchall()
    print('all announcements',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getPosts(cursor, conn, course_id):
    cursor.execute('''
        SELECT * FROM posts WHERE post_type_id=2 AND course_id=(%s) ORDER BY created_at;
    ''',[course_id])
    query_data = cursor.fetchall()
    print('all posts',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return -1

def getComments(cursor, conn, parent_id):
    cursor.execute('''
        SELECT * FROM comments WHERE parent_id=(%s) ORDER BY created_at;
    ''', [parent_id])
    query_data = cursor.fetchall()
    print('all comments',query_data)
    conn.commit()
    if query_data:
        data = [dict(zip(cursor.column_names, x)) for x in query_data]
        return data
    else:
        return []

def getCommentByID(cursor, conn, comment_id):
    cursor.execute('''
        SELECT * FROM comments WHERE id=(%s);
    ''', [comment_id])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data:
        data = dict(zip(cursor.column_names, query_data))
        print(data)
        return data
    else:
        return -1