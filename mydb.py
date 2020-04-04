import mysql.connector
import helper

all_pictuers_table = 'all_pictuers'
pictuers_with_face_table = 'pictuers_with_face'

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


def insert_pictuers_with_face(id_all_pics, face_locations, name_knowns):
    mydb = connect()
    mycursor = mydb.cursor()

    for i in range(len(face_locations)):
        if name_knowns[i] != 'None':
            sql = "INSERT INTO " + pictuers_with_face_table + " (id_all_pics, face_location, name_known) VALUES (%s, %s, %s)"
            val = (int(id_all_pics), face_locations[i], name_knowns[i])
            mycursor.execute(sql, val)


    mydb.commit()
    # get the id
    return get_last_id(pictuers_with_face_table)


def insert_all_pictuers(path, datetime, location):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "INSERT INTO " + all_pictuers_table + \
        " (pic_path, timestamp, location) VALUES (%s, %s, %s)"
    val = (path, datetime, location)

    mycursor.execute(sql, val)

    mydb.commit()
    return get_last_id(all_pictuers_table)

def get_image_path_by_id(image_id):
    mydb = connect()
    mycursor = mydb.cursor()
    
    query = 'SELECT pic_path FROM %s WHERE id = %d' % (all_pictuers_table, int(image_id))

    mycursor.execute(query)


    return mycursor.fetchone()[0]


def update_path_original_image(image_id, image_path):
    mydb = connect()
    mycursor = mydb.cursor()

    query = ("UPDATE %s SET pic_path = '%s' WHERE id = %d" % (all_pictuers_table, image_path, int(image_id)))
    mycursor.execute(query)

    mydb.commit()





def is_there_a_face(image_id):
    mydb = connect()
    mycursor = mydb.cursor()
    
    query='SELECT COUNT(pictuers_with_face.id) FROM all_pictuers JOIN pictuers_with_face ON all_pictuers.id = pictuers_with_face.id_all_pics WHERE all_pictuers.id = %d' % (int(image_id))
    
    mycursor.execute(query)
    result = mycursor.fetchone()[0]
    
    return result


def no_face_show(image_id):
    mydb = connect()
    mycursor = mydb.cursor()

    query = 'SELECT all_pictuers.* FROM all_pictuers WHERE all_pictuers.id = %d AND all_pictuers.id NOT IN (SELECT pictuers_with_face.id_all_pics FROM pictuers_with_face )' % (int(image_id))
    mycursor.execute(query)

    result = mycursor.fetchone()
    
    d = dict()
    d["id"] = result[0]
    d["path"] = result[1]
    d["datetime"] = result[2]
    d["location"] = result[3]
 
    
    return d

def get_full_details_of_image(id_image):
    mydb = connect()
    mycursor = mydb.cursor()

    query = "SELECT all_pictuers.*, knowns.names FROM all_pictuers JOIN (SELECT GROUP_CONCAT(t1.name_known SEPARATOR ', ') as names, t1.id_all_pics FROM pictuers_with_face t1 WHERE t1.id_all_pics = %d GROUP BY t1.id_all_pics) knowns ON all_pictuers.id = knowns.id_all_pics" % (int(id_image))

    mycursor.execute(query)

    result = mycursor.fetchone()
    
    d = dict()
    d["id"] = result[0]
    d["path"] = result[1]
    d["datetime"] = result[2]
    d["location"] = result[3]
    d["names"] = result[4]
    
    return d

def get_list_of_pictuers():
    mydb = connect()
    mycursor = mydb.cursor()

    sql = "SELECT all_pictuers.* FROM %s" % (all_pictuers_table)

    mycursor.execute(sql)

    results = mycursor.fetchall()
    result_with_keys=[]
    for child in results:
        d=dict()
        child[0]
        d["id"] = child[0]
        d["path"] = child[1]
        d["datetime"] = child[2]
        d["location"] = child[3]
        result_with_keys.append(d)
        
    return result_with_keys
    
                                                 
def get_list_of_pictuers_by_name_known(name_known):
    mydb = connect()
    mycursor = mydb.cursor()

    query_sql = "SELECT all_pictuers.* FROM all_pictuers JOIN pictuers_with_face ON all_pictuers.id = pictuers_with_face.id_all_pics WHERE pictuers_with_face.name_known LIKE '%{}%'".format(name_known)
    
    print(query_sql)
    mycursor.execute(query_sql)
    results = mycursor.fetchall()
    result_with_keys=[]
    for child in results:
        d=dict()
        d["id"] = child[0]
        d["path"] = child[1]
        d["datetime"] = child[2]
        d["location"] = child[3]
        result_with_keys.append(d)
        
    return result_with_keys

def delete_from_all_pictuers(image_id):
    mydb = connect()
    mycursor = mydb.cursor()
    
    query1 = 'DELETE FROM %s WHERE id_all_pics = %d' % (pictuers_with_face_table, int(image_id))
    query2 = 'DELETE FROM %s WHERE id = %d' % (all_pictuers_table, int(image_id))

    mycursor.execute(query1)
    mydb.commit()
    mycursor.execute(query2)
    mydb.commit()
    



def get_list_of_knows():
    mydb = connect()
    mycursor = mydb.cursor()

    sql = "SELECT all_pictuers.id, t3.name_known, all_pictuers.pic_path, t3.face_location FROM ( SELECT t1.id, t1.id_all_pics, t1.face_location, t1.name_known FROM pictuers_with_face t1 JOIN ( SELECT MIN(pictuers_with_face.id) AS id, pictuers_with_face.name_known AS 'name_known' FROM pictuers_with_face GROUP BY pictuers_with_face.name_known ) t2 ON t1.id = t2.id ) t3 JOIN all_pictuers ON t3.id_all_pics = all_pictuers.id"
    

    mycursor.execute(sql)

    results = mycursor.fetchall()
    result_with_keys=[]
    for child in results:
        d=dict()
        d["id"] = child[0]
        d["name_known"] = child[1]
        d["pic_path"] = child[2]
        d["face_location"] = child[3]
        result_with_keys.append(d)
    

    return result_with_keys
