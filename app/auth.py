from . import utils

# def loginStudent(cursor, conn, payload):
#     cursor.execute(f'''
#         SELECT * FROM users WHERE roll_number={payload.roll_no};
#     ''')
#     query_data = cursor.fetchone()
#     conn.commit()
#     return query_data

def checkRollNoExists(cursor, conn, payload):
    cursor.execute(f'''
        SELECT * FROM students WHERE roll_number={payload};
    ''')
    query_data = cursor.fetchone()
    conn.commit()
    if query_data is None:
        return False
    return True

def checkEmailExists(cursor, conn, payload):
    cursor.execute(f'''
        SELECT * FROM students WHERE email=(%s);
    ''', [payload])
    query_data = cursor.fetchone()
    conn.commit()
    if query_data is None:
        return False
    return True

def registerStudent(cursor, conn, payload):
    cursor.execute(f'''
        INSERT INTO students (name, department_id, programme_id, hometown, roll_number, email, password) VALUES
        ((%s), (%s), (%s), (%s), (%s), (%s), (%s) );
    ''', [payload.name, payload.department_id, payload.programme_id, payload.hometown, payload.roll_no, payload.email, payload.password])
    conn.commit()
    isSuccess = checkEmailExists(cursor, conn, payload.email)
    if isSuccess:
        return True
    else: 
        return False

def loginStudent(cursor, conn, email, password):
    cursor.execute('''
        SELECT * FROM students WHERE email=(%s);
    ''', [email])
    query_data = cursor.fetchone()
    conn.commit()
    if not query_data:
        return -1 # no such email
    
    # print(query_data)
    # # data = [(zip(cursor.column_names, x)) for x in query_data]
    # print(cursor.column_names)
    data = dict(zip(cursor.column_names, query_data))
    print('login student', data)

    if data['password'] == password:
        return data # successful login
    else: 
        return 0 # wrong password

def loginInstructor(cursor, conn, email, password):
    cursor.execute('''
        SELECT * FROM instructors WHERE email=(%s);
    ''', [email])
    query_data = cursor.fetchone()
    conn.commit()
    if not query_data:
        return -1 # no such email
    
    # print(query_data)
    # # data = [(zip(cursor.column_names, x)) for x in query_data]
    # print(cursor.column_names)
    data = dict(zip(cursor.column_names, query_data))
    print(data)

    if data['password'] == password:
        return data # successful login
    else: 
        return -1 # wrong password

def requestCourse(cursor, conn, payload): 
    checkCredentials = loginStudent(cursor, conn, payload.email, payload.password)
    print('request course check credentials: ',checkCredentials)
    if checkCredentials == 0 or checkCredentials== -1:
        return -1 # invalid credentials

    studentID = utils.getStudentID(cursor, conn, payload.email)
    print('line 89', studentID)

    cursor.execute('''
        SELECT * FROM course_requests WHERE student_id=(%s) AND course_id=(%s);
    ''', [studentID, payload.course_id])
    query_data = cursor.fetchone()
    print(query_data)
    conn.commit()

    if not query_data:
        cursor.execute('''
            INSERT INTO course_requests (student_id, course_id, status) VALUES 
            (%s, %s, 1)
        ''', [studentID, payload.course_id])
        conn.commit()
        return 5 #success
        ####
        #### INCLUDE db fail
        ####
    data = dict(zip(cursor.column_names, query_data))
    return data['status']

def acceptCourse(cursor, conn, payload):
    instructor = loginInstructor(cursor, conn, payload.email, payload.password)
    if instructor == -1:
        return -1 # invalid credentials

    courseRequestData = utils.getCourseIDfromCourseRequests(cursor, conn, payload.course_request_id)
    if courseRequestData == -1:
        return -2 # no such course request exists

    isInstructor = utils.checkInstructorForCourse(cursor, conn, instructor['id'], courseRequestData['course_id'])

    if isInstructor == 1:
        if courseRequestData['status'] == 2:
            return 2

        else:
            # accept Course
            cursor.execute('''
                UPDATE course_requests 
                SET status=2
                WHERE id=(%s)
            ''', [courseRequestData['id']])
            conn.commit()
            return 1
    else:
        return -3 # not the course instructor


def addAnnouncement(cursor, conn, payload):
    if payload.post_type != 1:
        return -4 # not an announcement (post type is wrong)

    instructor = loginInstructor(cursor, conn, payload.email, payload.password)
    if instructor == -1:
        return -1 # invalid credentials
    
    isInstructor = utils.checkInstructorForCourse(cursor, conn, instructor['id'], payload.course_id)

    if isInstructor == 1:
        cursor.execute('''
            INSERT INTO posts (course_id, owner_isStudent, owner_id, post_type_id, header, content) VALUES
            (%s, false, %s, 1, %s, %s);
        ''', [payload.course_id, instructor['id'], payload.header, payload.content])
        conn.commit()
    else:
        return -3 # not the course instructor

def addPost(cursor, conn, payload):
    if payload.post_type != 2:
        return -4 # not a post

    if payload.isStudent == True: ## Student
        student = loginStudent(cursor, conn, payload.email, payload.password)
        if student == 0 or student == -1:
            return -1 # invalid credentials
        
        isStudentAuth = utils.checkStudentForCourse(cursor, conn, student['id'], payload.course_id)
        if isStudentAuth == 1:
            # make post
            cursor.execute('''
                INSERT INTO posts (course_id, owner_isStudent, owner_id, post_type_id, header, content) VALUES
                (%s, true, %s, 2, %s, %s);
            ''', [payload.course_id, student['id'], payload.header, payload.content])
            conn.commit()
            return 1
        else:
            return isStudentAuth
    else: ## Teacher
        # owner = 
        instructor = loginInstructor(cursor, conn, payload.email, payload.password)
        if instructor == -1:
            return -1 # invalid credentials
        
        isInstructor = utils.checkInstructorForCourse(cursor, conn, instructor['id'], payload.course_id)
        print('is instructor: ', isInstructor)
        if isInstructor == 1:
            cursor.execute('''
                INSERT INTO posts (course_id, owner_isStudent, owner_id, post_type_id, header, content) VALUES
                (%s, false, %s, 2, %s, %s);
            ''', [payload.course_id, instructor['id'], payload.header, payload.content])
            conn.commit()
            return 1
        else:
            return -3 # not the course instructor


def addComment(cursor, conn, payload):
    if payload.isStudent == True: #student
        student = loginStudent(cursor, conn, payload.email, payload.password)
        if student == 0 or student == -1:
            return -1 # invalid credentials
        
        isStudentAuth = utils.checkStudentForCourse(cursor, conn, student['id'], payload.course_id)
        if isStudentAuth == 1:
            # make post
            cursor.execute('''
                INSERT INTO comments (course_id, owner_isStudent, owner_id, parent_id, content) VALUES
                (%s, true, %s, %s, %s);
            ''', [payload.course_id, student['id'], payload.parent_id, payload.content])
            conn.commit()
            return 1
        else:
            return isStudentAuth
    else: #Teacher
                # owner = 
        instructor = loginInstructor(cursor, conn, payload.email, payload.password)
        if instructor == -1:
            return -1 # invalid credentials
        
        isInstructor = utils.checkInstructorForCourse(cursor, conn, instructor['id'], payload.course_id)
        print('is instructor: ', isInstructor)
        if isInstructor == 1:
            cursor.execute('''
                INSERT INTO comments (course_id, owner_isStudent, owner_id, parent_id, content) VALUES
                (%s, false, %s, %s, %s);
            ''', [payload.course_id, instructor['id'], payload.parent_id, payload.content])
            conn.commit()
            return 1
        else:
            return -3 # not the course instructor

def getCourses(cursor, conn, payload):
    if payload.isStudent == True:
        student = loginStudent(cursor, conn, payload.email, payload.password)
        if student == 0 or student == -1:
            return -1 # invalid credentials
    
        allCourses = utils.getAllCourses(cursor, conn)
        print(allCourses)

        print (student)
        studentCourses = utils.getStudentCourses(cursor, conn, student['id'])
        print('student courses: ',studentCourses)
        return {
            'all_courses': allCourses,
            'student_courses': studentCourses
        }
    else:
        instructor = loginInstructor(cursor, conn, payload.email, payload.password)
        if instructor == -1:
            return -1 # invalid credentials

        # allCourses = utils.getAllCourses(cursor, conn)
        instructorCourses = utils.getInstructorCourses(cursor, conn, instructor['id'])
        print('instructor courses: ', instructorCourses)

        allRequests = []
        for course in instructorCourses:
            if course['offered'] == 1:
                courseRequests = utils.getCourseRequests(cursor, conn, course['id'])
                allRequests.extend(courseRequests)


        return {
            'instructor_courses': instructorCourses,
            'course_requests': allRequests
        }

def getCourseDetails(cursor, conn, payload, course_id):
    if payload.isStudent == True:
        student = loginStudent(cursor, conn, payload.email, payload.password)
        if student == 0 or student == -1:
            return -1 # invalid credentials
        isStudentAuth = utils.checkStudentForCourse(cursor, conn, student['id'], course_id)
        if isStudentAuth != 1:
            return -1 #unauthorized
    else: 
        instructor = loginInstructor(cursor, conn, payload.email, payload.password)
        if instructor == -1:
            return -1 # invalid credentials
        isInstructor = utils.checkInstructorForCourse(cursor, conn, instructor['id'], course_id)
        if isInstructor != 1:
            return -1 #unauthorized

    ## student or teacher but has access to course
    _announcements = utils.getAnnouncements(cursor, conn, course_id)
    print(_announcements)
    announcements = []
    for announcement in _announcements:
        _comments = utils.getComments(cursor, conn, announcement['id'])
        announcements.append(
            {
                'announcement': announcement,
                'comments': _comments
            }
        )

    _posts = utils.getAnnouncements(cursor, conn, course_id)
    print(_posts)
    posts = []
    for post in _posts:
        _comments = utils.getComments(cursor, conn, post['id'])
        posts.append(
            {
                'post': announcement,
                'comments': _comments
            }
        )    
    return {
        'announcements': announcements,
        'posts': posts
    }

def updateComment(cursor, conn, payload):
    comment = utils.getCommentByID(cursor, conn, payload.comment_id)

    if payload.isStudent == True:
        student = loginStudent(cursor, conn, payload.email, payload.password)
        if student == 0 or student == -1:
            return -1 # invalid credentials
        
        if comment['owner_isStudent'] == 1 and student['id']==comment['owner_id']:
            #update comment
            cursor.execute('''
                UPDATE comments SET content=(%s) where id=(%s);
            ''', [payload.content, payload.comment_id])
            conn.commit()
            return 1
        else: 
            return -2

    else:
        instructor = loginInstructor(cursor, conn, payload.email, payload.password)
        if instructor == -1:
            return -1 # invalid credentials

        if comment['owner_isStudent'] == 0 and instructor['id']==comment['owner_id']:
            #update comment
            cursor.execute('''
                UPDATE comments SET content=(%s) where id=(%s);
            ''', [payload.content, payload.comment_id])
            conn.commit()
            return 1
        else: 
            return -2     