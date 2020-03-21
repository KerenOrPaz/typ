from PIL import Image
import face_recognition
import os
import mydb
from datetime import datetime
import base64

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


def is_the_face_known(known_folder_path, unknown_image_path):
    is_known = False
    name_face_db = ""
    id_face_db = 0
    list_of_knowns = mydb.get_list_of_knows()
    for i in range(len(list_of_knowns)):
        known_from_db = list_of_knowns[i]
        path_face_db = known_from_db[2]
        try:
            known = face_recognition.load_image_file(path_face_db)
            known_face_encoding = face_recognition.face_encodings(known)[0]

            unknown_picture = face_recognition.load_image_file(unknown_image_path)
            unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[
                0]

            results = face_recognition.compare_faces(
                [known_face_encoding], unknown_face_encoding)

            if results[0]:
                is_known = True
                name_face_db = known_from_db[1]
                id_face_db = known_from_db[0]
        except:
            print("Can't load knonw")

    d = dict()
    d['status'] = is_known
    d['name'] = name_face_db
    d['id'] = id_face_db
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
    
    return Image.open(new_path)
    
def convert_and_save(encodedImg, file_name, target):
    print("{}/{}.jpg".format(target,file_name))
    with open("{}/{}.jpg".format(target,file_name), "wb") as fh:
        fh.write(base64.decodebytes(encodedImg.encode()))
    
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