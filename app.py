import os
import helper
import mydb
from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response
import face_recognition

app = Flask(__name__)
APP_ROOT = "/home/rsa-key-20200109/my_flask_app"
target_gallery = os.path.join(APP_ROOT, 'static/images/gallery')
target_temp = os.path.join(APP_ROOT, 'static/images/temp')

@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
    print("/upload")
    encodedImg = request.form['file']
    image_file = helper.decode_and_save_image_and_return_file(encodedImg, target_temp)
    # Save image in temp folder
    # need to remove the line below
    #print("type(image_file)")
    #print(type(image_file))
    #print("image_file")
    #print(image_file)
    #temp_image_file = helper.save_image_first_time(image_file, target_temp)
    # Save in DB - temp image, location and datetime
    full_path_of_image = helper.get_path_image(image_file, target_temp)
    datetime = request.form['datetime']
    location = request.form['location']
    # insert DB
    image_id = mydb.insert_pictuers_image(full_path_of_image, datetime, location)
    
    # Check if there is face at image
    if helper.is_there_a_face_in_the_image(full_path_of_image):
        # if have - check if know
        # check_known = helper.is_the_face_known(full_path_of_image)
        check_known = helper.is_the_face_known(full_path_of_image)
        # if know save at gallery and remove from temp and update galley DB (know, new path)
        if check_known['status']:
            # Save image in gallery folder 
            new_path = helper.save_image(image_file, target_gallery)
            # delete from temp folder
            os.remove(full_path_of_image)
            # update path in db
            mydb.update_path_original_image(image_id, new_path)
            # update in db table picsofknown
            mydb.insert_to_PicsOfKnown(check_known['id'], image_id)
            # convert server path to client path of image
            client_path_image = helper.convert_server_path_to_client_path_image(new_path)
            return jsonify(action="show image", known=check_known['name'], path_image=client_path_image, image_id=image_id)

        # else if no know but have face - asking from user name to face with id of image in gallrey db
        else:
            return jsonify(action="ask name", image_id=image_id)

    # else if no face at image - move image to gallrey folder and update gallery DB (path)
    new_path = helper.save_image(image_file, target_gallery)
    mydb.update_path_original_image(image_id, new_path)
    os.remove(full_path_of_image)
    return jsonify(action="show image", image_id=image_id)


@app.route("/askName", methods=['GET'])
def askName():
    return render_template("get_name.html")


@app.route("/enterName", methods=['POST'])
def enterName():
    name_face = request.form['inputName']
    image_id = request.form['galleryId']
    # cut face from original image and save in knowns folder
    path_original_image = mydb.get_image_path_by_id(image_id)
    # cut and save
    face_path = helper.cut_face_and_save_and_return_new_path(path_original_image)
    # save in knowns DB and get known id
    known_id = mydb.insert_known_image(name_face, face_path)
    # move original image to gallrey folder
    if not os.path.isdir(target_gallery):
        os.mkdir(target_gallery)
    new_path = "/".join([target_gallery, path_original_image.split('/')[-1]])
    # update gallery DB (path)
    mydb.update_path_original_image(image_id, new_path)
    # add to PicsOfKnown DB (image_id, known_id)
    mydb.insert_to_PicsOfKnown(known_id, image_id)
    os.rename(path_original_image, new_path)
    return jsonify(action="show image", image_id=image_id)


@app.route("/showImage/<id>", methods=['GET'])
def showImage(id):
    print("----------------------------")
    print(mydb.is_there_a_face(id))
    print("----------------------------")
    if mydb.is_there_a_face(id)==0: 
        result=mydb.no_face_show(id)
    else:
        result = mydb.get_full_details_of_image(id)
    
    result["path"] = helper.convert_server_path_to_client_path_image(result["path"])
    return jsonify( result )

@app.route("/showImages", methods=['GET'])
def showImages():
    results = mydb.get_list_of_pictuers()
    for child in results:
        child["path"] = helper.convert_server_path_to_client_path_image(child["path"])
    return jsonify(results)

@app.route("/search/<name_person>", methods=['GET'])
def search(name_person):
    results = mydb.get_list_of_pictuers_by_name_known(name_person)
    for child in results:
        child["path"] = helper.convert_server_path_to_client_path_image(child["path"])
    return jsonify(results)


@app.route("/delete/<gallery_id>", methods=['DELETE'])
def delete(gallery_id):
    image_path = mydb.get_image_path_by_id(gallery_id)
    mydb.delete_from_pictuers(gallery_id)
    try:
        os.remove(image_path)
    except:
        return jsonify(action="Fail")

    return jsonify(action="done")

@app.route("/getLocationOfFace", methods=['GET'])
def test():
    image = face_recognition.load_image_file("/home/rsa-key-20200109/my_flask_app/static/images/gallery/03082020163444.jpg")
    locations = face_recognition.face_locations(image)
    return location
    # locations = [(172,603,726,48)]
    #face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2)
    #print(face_locations)
    #print(type(face_locations))
    #print(face_locations[0])
    #print(type(face_locations[0]))
    face_encodings = face_recognition.face_encodings(image, known_face_locations=locations, num_jitters=1)
    print('face_encodings')
    print(face_encodings)
    print(type(face_encodings))
    #test_face = face_recognition.face_encodings(image)
    return jsonify(test_face='test_face')

@app.route("/forListLoctaionOfFaceToCompareFaces", methods=['GET'])
def test2():
    # image_test = face_recognition.load_image_file("/home/rsa-key-20200109/my_flask_app/static/images/gallery/03082020163537.jpg")
    # image_2 = face_recognition.load_image_file("/home/rsa-key-20200109/my_flask_app/static/images/gallery/03112020181843.jpg")
    # image_3 = face_recognition.load_image_file("/home/rsa-key-20200109/my_flask_app/static/images/gallery/03102020155859.jpg")
    
    # face_test = face_recognition.face_locations(image_test)
    # face_2 = face_recognition.face_locations(image_2)
    # face_3 = face_recognition.face_locations(image_3)
    
    face_location_1 = [(0,0,0,0)]
    face_location_2 = [(0,0,0,0)]
    face_location_3 = [(0,0,0,0)]
    
    face_encodings_test = face_recognition.face_encodings(image_test, known_face_locations=face_location_1, num_jitters=1)[0]
    face_encodings_2 = face_recognition.face_encodings(image_2, known_face_locations=face_location_2, num_jitters=1)[0]
    face_encodings_3 = face_recognition.face_encodings(image_3, known_face_locations=face_location_3, num_jitters=1)[0]
    
    known_faces = [face_encodings_2, face_encodings_3]
    result = face_recognition.compare_faces(known_faces, face_encodings_test, tolerance=0.56)
    return result

    print(result)
    print(type(result))
    
    distance = face_recognition.face_distance(known_faces, face_encodings_test)
    print('distance')
    print(distance)
    print(type(distance))
    
    #face_list = face_recognition.face_locations(image)
    #locations = [(172,603,726,48)]
    #face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2)
    #print(face_locations)
    #print(type(face_locations))
    #print(face_locations[0])
    #print(type(face_locations[0]))
    #face_encodings = face_recognition.face_encodings(image, known_face_locations=locations, num_jitters=1)
    # print('face_encodings')
    # print(face_encodings)
    # print(type(face_encodings))
    #test_face = face_recognition.face_encodings(image)
    return jsonify(test_face='test_face')