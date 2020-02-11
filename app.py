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
    temp_id = mydb.insert_temp_image(full_path_of_image, datetime, location)
    # Check if there is face at image
    if helper.is_there_a_face_in_the_image(image_file):
        # if have - check if know
        # TODO: take knowns from DB and not from folder
        check_known = helper.is_the_face_known('static/images/knowns', full_path_of_image)
        print("check_known")
        # if know save at gallery and remove from temp and update galley DB (know, new path)
        if check_known['status']:
            print(" ")
            print("This pic is known, need to update path to gallery")
            # Save image in gallery folder
            print(" ")
            print("target gallery: " + target_gallery)
            print(" ")
            #TODO:need to move the pic from temp to gallery not save new, after nees to get the new path to the pic for DB
            new_path = helper.save_image(image_file, target_gallery)
            # update path in db
            #full_path_of_image = helper.get_path_image(image_file, new_path)
            print(" ")
            print("new full path of the image: " + new_path)
            print(" ")
            print(type(target_gallery))
            print("")
            #gallery_id = mydb.insert_pictuers_image(new_path, datetime, location)
            mydb.update_path_original_image(temp_id, new_path)
            # update in db table picsofknown
            print("------")
            print("is KNOWN!!!")
            print(check_known)
            print("------")
            mydb.insert_to_PicsOfKnown(check_known['id'], temp_id)
            mydb.delete_from_temp(temp_id)
            return jsonify(action="done", known=check_known['name'], path_image=new_path)
        # else if no know but have face - asking from user name to face with id of image in gallrey db
        else:
            print("    ")
            print(temp_id)
            print("    ")

            # return render_template(get_name.html)?
            return jsonify(action="add name", temp_id=temp_id)
    # return jsonify(action="fail")

    # else if no face at image - move image to gallrey folder and update gallery DB (path)
    helper.save_image(image_file, target_gallery)
    mydb.update_path_original_image(image_file, target_gallery)


@app.route("/askName", methods=['GET'])
def askName():
    # save the face in knowns folder
    # save in db - known table
    return render_template("get_name.html")


@app.route("/enterName", methods=['POST'])
def enterName():
    # then get name face and cut face and save face image at knowns folder then save at knowns DB
    # get id of knowns then move original image to gallrey folder and update gallery DB (path, known)
    # get name and gallery id
    name_face = request.form['inputName']
    gallery_id = request.form['galleryId']
    print("    ")
    print("the name we got: " + name_face)
    print("the gallery id is: " + gallery_id)
    print("    ")

    # cut face from original image and save in knowns folder
    path_original_image = mydb.get_image_path_by_id(gallery_id)
    print("    ")
    print("    ")
    print(path_original_image)
    print("    ")
    print("    ")

    # cut and save
    face_path = helper.cut_face_and_save_and_return_new_path(path_original_image)


    # save in knowns DB and get known id
    known_id = mydb.insert_known_image(name_face, face_path)

    # move original image to gallrey folder
    target_to_gallery = os.path.join(APP_ROOT, 'static/images/gallery')
    if not os.path.isdir(target_to_gallery):
        os.mkdir(target_to_gallery)
    new_path = "/".join([target_to_gallery, path_original_image.split('/')[-1]])

    os.rename(path_original_image, new_path)

    # update gallery DB (path)
    mydb.update_path_original_image(gallery_id, new_path)
    # add to PicsOfKnown DB (gallery_id, known_id)
    mydb.insert_to_PicOfKnown(known_id, gallery_id)

    return jsonify(action="done")


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

@app.route("/test")
def test():
    mydb.get_list_of_knows()
    return jsonify(action="done")