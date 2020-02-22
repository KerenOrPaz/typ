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
    sql = "INSERT INTO " + pictuers_table + \
        " (pic_path, date, location) VALUES (%s, %s, %s)"
    val = (path, datetime, location)

    mycursor.execute(sql, val)

    mydb.commit()
    return get_last_id(pictuers_table)


def insert_pictuers_image(path, datetime, location):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "INSERT INTO " + pictuers_table + \
        " (pic_path, date, location) VALUES (%s, %s, %s)"
    val = (path, datetime, location)

    mycursor.execute(sql, val)

    mydb.commit()
    return get_last_id(pictuers_table)


def insert_to_PicsOfKnown(id_face, id_full_image):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "INSERT INTO " + pics_of_known_table + \
        " (id_of_known, id_of_pic) VALUES (%s, %s)"
    val = (id_face, id_full_image)

    mycursor.execute(sql, val)

    mydb.commit()
    return get_last_id(pics_of_known_table)


def update_path_original_image(image_id, image_path):
    mydb = connect()
    mycursor = mydb.cursor()

    query = ("UPDATE %s SET pic_path = '%s' WHERE id = %d" % (pictuers_table, image_path, int(image_id)))
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

    query = 'SELECT pic_path FROM %s WHERE id = %d' % (pictuers_table, int(image_id))

    mycursor.execute(query)


    return mycursor.fetchone()[0]

def get_list_of_knows():
    mydb = connect()
    mycursor = mydb.cursor()

    sql = "SELECT id, name, face_path FROM %s" % (knowns_table)

    mycursor.execute(sql)

    result = mycursor.fetchall()

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
        child[0]
        d["id"] = child[0]
        d["pic_path"] = child[1]
        d["date"] = child[2]
        d["location"] = child[3]
        result_with_keys.append(d)
        
    
    
    return result_with_keys
                                                     
def get_list_of_pictuers_by_name_known(name_known):
    mydb = connect()
    mycursor = mydb.cursor()

    query_sql = "SELECT Pictuers.* FROM Pictuers JOIN PicsOfKnown ON Pictuers.id = PicsOfKnown.id_of_pic WHERE PicsOfKnown.id_of_pic = Pictuers.id"
    query_sql +=" AND PicsOfKnown.id_of_known = (SELECT Knowns.id FROM Knowns WHERE Knowns.name LIKE '%s')" % (name_known)
    mycursor.execute(query_sql)
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