import mysql.connector

pictuers_table = 'Pictuers'
knowns_table = 'Knowns'
pics_of_known_table = 'PicsOfKnown'


def connect():
    return mysql.connector.connect(
        host="localhost",
        user="phpmyadmin",
        passwd="1416typ",
        database="myApp"
    )


def get_last_id(table):
    mydb = connect()
    mycursor = mydb.cursor()

    mycursor.execute('SELECT id FROM ' + table + ' ORDER BY id DESC LIMIT 1')

    return mycursor.fetchone()[0]


def insert_known_image(name_face, face_path):
    mydb = connect()
    mycursor = mydb.cursor()
    # Qurey
    sql = "INSERT INTO " + knowns_table + \
        " (name, face_path) VALUES (%s, %s)"
    val = (name_face, face_path)

    mycursor.execute(sql, val)

    mydb.commit()
    # get the id
    return get_last_id(knowns_table)


def insert_temp_image(path, datetime, location):
    mydb = connect()
    mycursor = mydb.cursor()
    # Qurey
    sql = "INSERT INTO " + pictuers_table + \
        " (pic_path, date, location) VALUES (%s, %s, %s)"
    val = (path, datetime, location)

    mycursor.execute(sql, val)

    mydb.commit()
    # get the id
    return get_last_id(pictuers_table)


def insert_pictuers_image(path, datetime, location):
    mydb = connect()
    mycursor = mydb.cursor()
    # Qurey
    sql = "INSERT INTO " + pictuers_table + \
        " (pic_path, date, location) VALUES (%s, %s, %s)"
    val = (path, datetime, location)

    mycursor.execute(sql, val)

    mydb.commit()
    # get the id
    return get_last_id(pictuers_table)


def insert_to_PicsOfKnown(id_face, id_full_image):
    mydb = connect()
    mycursor = mydb.cursor()
    # Qurey
    sql = "INSERT INTO " + pics_of_known_table + \
        " (id_of_known, id_of_pic) VALUES (%s, %s)"
    val = (id_face, id_full_image)

    mycursor.execute(sql, val)

    mydb.commit()
    # get the id
    return get_last_id(pics_of_known_table)


def update_path_original_image(image_id, image_path):
    mydb = connect()
    mycursor = mydb.cursor()
    print("-------------------------------------------------")
    print("in DB: the vars that we pass and the type in the same order: ")
    print(image_id)
    print(type(image_id))
    print(image_path)
    print(type(image_path))
    print("-------------------------------------------------")


    query = ("UPDATE %s SET pic_path = '%s' WHERE id = %d" % (pictuers_table, image_path, int(image_id)))
    print("-------------------------------------------------")
    print("the query that we are ex")
    print(query)
    print("-------------------------------------------------")
    mycursor.execute(query)

    mydb.commit()


def delete_from_knowns(image_id):
    mydb = connect()
    mycursor = mydb.cursor()

    mycursor.execute('DELETE FROM %s WHERE id = %d' % (knowns_table, image_id))

    mydb.commit()


def delete_from_pictuers(image_id):
    mydb = connect()
    mycursor = mydb.cursor()

    query = 'DELETE FROM %s WHERE id = %d' % (pictuers_table, int(image_id))
    print(query)

    mycursor.execute(query)

    mydb.commit()
    




def delete_from_PicsOfKnowns(image_id):
    mydb = connect()
    mycursor = mydb.cursor()

    mycursor.execute('DELETE FROM %s WHERE id = %d' % (pics_of_known_table, image_id))

    mydb.commit()


def get_image_path_by_id(image_id):
    mydb = connect()
    mycursor = mydb.cursor()
    print("--------------------------------------------")
    print("get image by id")
    print(image_id)
    print(type(image_id))
    print("fail?")

    query = 'SELECT pic_path FROM %s WHERE id = %d' % (pictuers_table, int(image_id))

    print(query)

    mycursor.execute(query)
    print("--------------------------------------------")
    print("the image was passed")
    print("--------------------------------------------")


    return mycursor.fetchone()[0]

def get_list_of_knows():
    mydb = connect()
    mycursor = mydb.cursor()

    sql = "SELECT id, name, face_path FROM %s" % (knowns_table)

    mycursor.execute(sql)

    result = mycursor.fetchall()
    # array_of_result = []
    # for i in range(len(result)):
	#      d = dict()
    #      d["id"] = result[i][0]
    #      d["name"] = result[i][1]
    #      d["face_path"] = result[i][2]
    #      array_of_result.append(d)
    # print(array_of_result)
    # print(result)

    return result

def get_list_of_pictuers():
    mydb = connect()
    mycursor = mydb.cursor()

    sql = "SELECT id, pic_path, date, location FROM %s" % (pictuers_table)

    mycursor.execute(sql)

    results = mycursor.fetchall()
    result_with_keys=[]
    for child in results:
        d=dict()
        d["id"] = child[0]
        d["pic_path"] = child[1]
        d["date"] = child[2]
        d["location"] = child[3]
        result_with_keys.append(d)
        
    
    
    return result_with_keys

def get_list_of_pictuers_by_name_known(name_known):
    mydb = connect()
    mycursor = mydb.cursor()
    
    query = "SELECT Pictuers.* FROM Pictuers JOIN PicsOfKnown ON Pictuers.id = PicsOfKnown.id_of_pic WHERE PicsOfKnown.id_of_pic = Pictuers.id"
    query +=" AND PicsOfKnown.id_of_known IN(SELECT Knowns.id FROM Knowns WHERE Knowns.name = %s)" % (name_known)
    mycursor.execute(query)
    print("-------------------------------------------------")
    print("done")
    print("-------------------------------------------------")
    results = mycursor.fetchall()
    result_with_keys=[]
    for child in results:
        d=dict()
        d["id"] = child[0]
        d["pic_path"] = child[1]
        d["date"] = child[2]
        d["location"] = child[3]
        result_with_keys.append(d)
    
    return result_with_keys

# for the search
#def get_images_path_by_name(image_name):
#    mydb = connect()
#    mycursor = mydb.cursor()
#    mycursor.execute('SELECT pic_path FROM ' + pics_of_known_table + ' JOIN ' + pictuers_table + /
#            ' WHERE id = id_of_pic AND id_of_known = (SELECT id FROM ' + knowns_table + ' WHERE name = ' + image_name))
#    return mycursor.fetchone()

def get_full_details_of_image(id_image):
    mydb = connect()
    mycursor = mydb.cursor()

    query = 'SELECT Pictuers.*, Knowns.name FROM Pictuers JOIN PicsOfKnown JOIN Knowns WHERE PicsOfKnown.id_of_pic=Pictuers.id AND PicsOfKnown.id_of_known = Knowns.id AND Pictuers.id= %d' % (int(id_image))
    print(query)

    mycursor.execute(query)

    result = mycursor.fetchone()
    
    d = dict()
    d["id"] = result[0]
    d["path"] = result[1]
    d["datetime"] = result[2]
    d["location"] = result[3]
    d["name"] = result[4]
    
    return d