from PIL import Image
import face_recognition
import os
import mydb
from datetime import datetime
import base64
import cv2

APP_ROOT = "/home/rsa-key-20200109/my_flask_app"

# is_there_a_face_in_the_image(image) return true/false


def is_there_a_face_in_the_image(pic):
    image = face_recognition.load_image_file(pic)
    face_list = face_recognition.face_locations(image)
    face_count = len(face_list)

    if face_count > 0:
        return True
    else:
        return False

# is the face_known(image) return true/false


def is_the_face_known(unknown_image_path):
    are_knowns = []
    are_unknowns = []
    face_names = []
    
    at_least_unknown = False
    
    
    list_of_knowns = mydb.get_list_of_knows()
    
    known_faces_encodings = []
    for i in range(len(list_of_knowns)):
        known_from_db = list_of_knowns[i]
        
        name_known = known_from_db["name_known"]
        pic_path = known_from_db["pic_path"]
        face_location_string = known_from_db["face_location"]
        
        face_location = stringToTuple(face_location_string, ',')
        try:
            # load image
            known_after_load_image = face_recognition.load_image_file(pic_path)
            # encodings
            known_encodings = face_recognition.face_encodings(known_after_load_image, known_face_locations=[face_location], num_jitters=1)[0]
            # add to list of faces encodings
            known_faces_encodings.append(known_encodings)
        except:
            print("Can't load knonw of {} in {}".format(name_known, log))
        
    try:
        # load image
        unknown_after_load_image = face_recognition.load_image_file(unknown_image_path)
        # locations of unknowns
        faces_loction_unkonw = face_recognition.face_locations(unknown_after_load_image)
        # encodings
        unknown_faces_encodings = face_recognition.face_encodings(unknown_after_load_image, known_face_locations=faces_loction_unkonw, num_jitters=1)
    except:
        print("Can't load unknonw")
        
    for i in range(len(unknown_faces_encodings)):
        unknown_faces_encoding = unknown_faces_encodings[i]
        result = face_recognition.compare_faces(known_faces_encodings, unknown_faces_encoding, tolerance=0.56)
        face_location_string = tupleToString(faces_loction_unkonw[i], ",")
        
        if not any(result):
            d = dict()
            d['index'] = i
            d['face_location'] = face_location_string
            are_unknowns.append(d)
            at_least_unknown = True
            face_names.append(None)
        else:
            for j in range(len(result)):
                if result[j]:
                    known = list_of_knowns[j]
                    d = dict()
                    d['index'] = j
                    d['name'] = known["name_known"]
                    d['id'] = known["id"]
                    d['face_location'] = face_location_string
                    are_knowns.append(d)
                    face_names.append(known["name_known"])
                    break

    temp_mark_image = ""        
    if at_least_unknown:
        # create temp image with mark faces
        image = cv2.imread(unknown_image_path)
        index = 1
        for (top, right, bottom, left), name in zip(faces_loction_unkonw, face_names):
            # Draw a box around the face
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            if name == None:
                name = "%d: unkown" % (index)
                index += 1
            cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 2)
            
        retval, buffer = cv2.imencode('.jpg', image)
        temp_mark_image = base64.b64encode(buffer)
        temp_mark_image = str(temp_mark_image, 'utf-8')

    d = dict()
    d['at_least_unknown'] = at_least_unknown
    d['all_knowns'] = not at_least_unknown
    d['list_knowns'] = are_knowns
    d['list_unknowns'] = are_unknowns
    d['image'] = temp_mark_image
    return d


# save_face_in_known(face_image) void
def cut_face_and_save_and_return_new_path(image_path):

    image_open = Image.open(image_path)

    image = face_recognition.load_image_file(image_path)
    face_list = face_recognition.face_locations(image)

    for face_loc in face_list:
        target = os.path.join(APP_ROOT, 'static/images/knowns')

        if not os.path.isdir(target):
            os.mkdir(target)

        top, right, bottom, left = face_loc
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)

        destination = "/".join([target, image_open.filename.split('/')[-1]])
        pil_image.save(destination)
        print("the face path is:")
        print(destination)
        return destination

def decode_and_save_image_and_return_file(encodedImg, target):
    #image = base64.b64decode(encodedImg)
    # datetime
    now = datetime.now()
    date_time = now.strftime("%m%d%Y%H%M%S")
    print("date and time:",date_time)
    
    # save image
    if not os.path.isdir(target):
        os.mkdir(target)
    
    new_path = convert_and_save(encodedImg, date_time, target)
    
    return Image.open(r"%s" % new_path)
    
def convert_and_save(encodedImg, file_name, target):
    print("{}/{}.jpg".format(target,file_name))
    with open("{}/{}.jpg".format(target,file_name), "wb") as fh:
        fh.write(base64.decodebytes(encodedImg.encode()))
        #fh.write(base64.standard_b64encode(encodedImg.encode()))
        os.chmod("{}/{}.jpg".format(target,file_name), 0o777)
    
    return "{}/{}.jpg".format(target,file_name)

# save_image(image) 
def save_image_first_time(file, target):
    # check if there folder, if not create
    if not os.path.isdir(target):
        os.mkdir(target)

    now = datetime.now()
    date_time = now.strftime("%m%d%Y%H%M%S")
    print("date and time:",date_time)
    
    filename = date_time
    full_path_of_image = "/".join([target, filename])
    
    file.save(full_path_of_image)
    return full_path_of_image

def save_image(file, target):
    # check if there folder, if not create
    if not os.path.isdir(target):
        os.mkdir(target)

    full_path_of_image = get_path_image(file, target)
    file.save(full_path_of_image)
    return full_path_of_image

def move_image(file, target_from, target_to):
    # check if there folder, if not create
    if not os.path.isdir(target_to):
        os.mkdir(target_to)
        
    full_path_of_image = get_path_image(file, target_to)
    os.rename(target_from, full_path_of_image)
    return full_path_of_image
# get path og image


def get_path_image(file, target):
    full_path = file.filename
    filename = full_path.split("/")[-1]
    return "/".join([target, filename])

def convert_server_path_to_client_path_image(server_path):
    flag = False
    path_to_array = server_path.split("/")
    path=""
    for item in path_to_array:
        if flag:
            path += "/" + item
        elif item == "my_flask_app":
            flag = True
    print(path)
    return path

def tupleToString(tup, key):
    string = '('
    for var in range(len(tup)):
        string += str(tup[var])
        if var < len(tup) - 1:
            string += key
    
    string += ')'
    return string

def stringToTuple(string, key):
    return tuple(map(int, string[1:-1].split(key)))
