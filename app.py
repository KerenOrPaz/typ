import os
import helper
import mydb
from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response

app = Flask(__name__)


APP_ROOT = "/home/rsa-key-20200109/my_flask_app"


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
    #global variables
    target_gallery = os.path.join(APP_ROOT, 'static/images/gallery')
    target_temp = os.path.join(APP_ROOT, 'static/images/temp')


    # Get the fisrt image from form
    image_file = request.files.getlist("file")[0]

    # Save image in temp folder
    helper.save_image(image_file, target_temp)

    # Save in DB - temp image, location and datetime
    full_path_of_image = helper.get_path_image(image_file, target_temp)
    datetime = request.form['datetime']
    location = request.form['location']
    # insert DB
    image_id = mydb.insert_pictuers_image(full_path_of_image, datetime, location)

    print("-------------------------------------------------")
    print("in this point we entered the image to temp table and now checking if the image has a face")
    print("-------------------------------------------------")
    
    # Check if there is face at image
    if helper.is_there_a_face_in_the_image(image_file):
        # if have - check if know
        print("-------------------------------------------------")
        print("in this point we got an image with a face, now checking is the face is known")
        print("-------------------------------------------------")
        check_known = helper.is_the_face_known('static/images/knowns', full_path_of_image)
        print("is the face known? ")
        print(check_known['status'])

        # if know save at gallery and remove from temp and update galley DB (know, new path)
        if check_known['status']:
            print("-------------------------------------------------")
            print("the face is knowns, now we save the image in gallery and updateing it's path")
            print("-------------------------------------------------")
            # Save image in gallery folder and delete from temp folder
            new_path = helper.save_image(image_file, target_gallery)
            os.remove(full_path_of_image)

            # update path in db
            mydb.update_path_original_image(image_id, new_path)
            # update in db table picsofknown
            mydb.insert_to_PicsOfKnown(check_known['id'], image_id)
            return jsonify(action="show image", known=check_known['name'], path_image=new_path)

        # else if no know but have face - 
        # asking from user name to face with id of image in gallrey db
        else:
            print("-------------------------------------------------")
            print("the face is not known we asking for a name and ")
            print("-------------------------------------------------")
            #when getting to this point (for now) we need to redirect to http://35.238.145.42/askName
            print("go to http://35.238.145.42/askName the id is: " + image_id)
            return jsonify(action="ask name", temp_id=image_id)

    # else if no face at image - move image to gallrey folder and update gallery DB (path)
    print("-------------------------------------------------")
    print("there is no face in this image save and update the image id is:")
    print(image_id)
    print("-------------------------------------------------")
    new_path = helper.save_image(image_file, target_gallery)
    mydb.update_path_original_image(image_id, new_path)
    #TODO: show image
    return jsonify(action="show image", temp_id=image_id)


@app.route("/askName", methods=['GET'])
def askName():
    return render_template("get_name.html")


@app.route("/enterName", methods=['POST'])
def enterName():
    # then get name face 
    # cut face and save face image at knowns folder 
    # save at knowns DB
    # get id of knowns then move original image to gallrey folder and update gallery DB (path, known)
    # get name and image id
    name_face = request.form['inputName']
    image_id = request.form['galleryId']
    print("-------------------------------------------------")
    print("got the name and id")
    print("-------------------------------------------------")

    print("this is the image id: ")
    print(image_id)
    print("")
    # cut face from original image and save in knowns folder
    path_original_image = mydb.get_image_path_by_id(image_id)
    print("")
    print(path_original_image)
    print("--------------------------------------------")
    print("got the path to the image")
    print("--------------------------------------------")

    print("")

    # cut and save
    face_path = helper.cut_face_and_save_and_return_new_path(path_original_image)
    print("-------------------------------------------------")
    print("got the face path from DB: ")    
    print("-------------------------------------------------")
    print("")
    print(face_path)
    print("")

    # save in knowns DB and get known id
    known_id = mydb.insert_known_image(name_face, face_path)
    print("-------------------------------------------------")
    print("at this point we got an id for the face image, this is the known id:")
    print(known_id)
    print("now we need to move the pictuer to gallery, not the face")
    print("this is the path of the image:")
    print(path_original_image)
    print("-------------------------------------------------")

    # move original image to gallrey folder
    target_to_gallery = os.path.join(APP_ROOT, 'static/images/gallery')
    if not os.path.isdir(target_to_gallery):
        os.mkdir(target_to_gallery)
    new_path = "/".join([target_to_gallery, path_original_image.split('/')[-1]])
    print("-------------------------------------------------")
    print("this is the new path for the full image: ")
    print(new_path)
    print("-------------------------------------------------")

    

    print("-------------------------------------------------")
    print(new_path)
    print("we moved the image to gallery, and now we updateing in DB")
    print("in app.py the vars that we move to DB ant the type are: (in this order) the image id and the path to the full image ")
    print(image_id)
    print(type(image_id))
    print(new_path)
    print(type(new_path))
    print("-------------------------------------------------")
    #mydb.update_path_original_image(image_id, new_path)

    # update gallery DB (path)
    mydb.update_path_original_image(image_id, new_path)
    print("-------------------------------------------------")
    print("path for the image was updated")
    # add to PicsOfKnown DB (image_id, known_id)
    mydb.insert_to_PicsOfKnown(known_id, image_id)
    os.rename(path_original_image, new_path)
    #TODO: show image
    return jsonify(action="show image")


@app.route("/showImage", methods=['GET'])
def showImage():
    return request.args.get('id')


@app.route("/search", methods=['GET'])
def search():
    return "map"


@app.route("/delete", methods=['DELETE'])
def delete():
    gallery_id = request.form['galleryId']
    image_path = mydb.get_image_path_by_id(gallery_id)
    os.remove(image_path)

    return jsonify(action="done")

