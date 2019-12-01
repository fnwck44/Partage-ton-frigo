import os
from datetime import datetime
from flask import Flask, Response, flash, request, redirect, url_for, send_from_directory
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
import os.path as op
from flask_basicauth import BasicAuth
from flask_admin.contrib import sqla
from werkzeug.exceptions import HTTPException

from pyzbar.pyzbar import decode
from PIL import Image, ExifTags
import openfoodfacts



project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db: SQLAlchemy = SQLAlchemy(app)


UPLOAD_FOLDER = './static/img_db/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            message, 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ModelView(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated. Refresh the page.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class Aliment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titre = db.Column(db.String(80))
    quantity = db.Column(db.Integer, nullable=False)
    peremption = db.Column(db.Date)
    ajout = db.Column(db.Date)
    frais = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(150))
    dlc = db.Column(db.String(30))
    nom = db.Column(db.String(50))
    image = db.Column(db.String(50))
    nutriscore = db.Column(db.String(10))
    cb = db.Column(db.String(30))


    def __repr__(self):
        return "<Title: {}>".format(self.titre), \
               "<Quantity:{}>".format(self.quantity), \
               "Peremption:{}".format(self.peremption), \
               "Ajout:{}".format(self.ajout), \
               "frais:{}".format(self.frais), \
               "desc:{}".format(self.desc), \
               "dlc:{}".format(self.dlc), \
               "nom:{}".format(self.nom)


admin = Admin(app)
admin.add_view(ModelView(Aliment, db.session))
path_static = op.join(op.dirname(__file__), 'static')
path_db = op.join(op.dirname(__file__), 'img_db')
admin.add_view(FileAdmin(path_static, '/static/', name='Static Files'))
#admin.add_view(FileAdmin(path_db, '/img_db/', name='image database'))


@app.route('/logout')
def Logout():
    raise AuthException('Successfully logged out.')


@app.route('/add', methods=["GET", "POST"])
def home():
    aliments = None
    if request.form:
        try:

            code=''
            nutriscore=''
            img=''
            if request.method == 'POST':
                # check if the post request has the file part
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                print(request.files)
                file = request.files['file']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    flash('No selected file')
                    img=url_for('static', filename='img_db/'+request.form.get("frais")+".jpg")
                if file and allowed_file(file.filename):
                    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
                    img_name=file.filename
                    try :
                        codes = decode(Image.open('./static/img_db/' + img_name))
                        print(codes)
                        print(1)
                        if len(codes)>0 :
                            print(codes)
                            code=codes[0].data.decode("utf-8")
                        else :
                            code = ''
                        print(2)
                        product = openfoodfacts.products.get_product(code)
                        print(2.5)
                        if product['status_verbose'] == 'product found':
                            print(3)
                            try:
                                img = product['product']['image_small_url']
                                os.remove("./static/img_db/" + img_name)
                                print(4)

                            except:
                                basewidth = 500

                                file = Image.open('./static/img_db/' + img_name)
                                try:
                                    for orientation in ExifTags.TAGS.keys():
                                        if ExifTags.TAGS[orientation] == 'Orientation':
                                            break
                                    exif = dict(file._getexif().items())

                                    if exif[orientation] == 3:
                                        file = file.rotate(180, expand=True)
                                    elif exif[orientation] == 6:
                                        file = file.rotate(270, expand=True)
                                    elif exif[orientation] == 8:
                                        file = file.rotate(90, expand=True)

                                except (AttributeError, KeyError, IndexError):
                                    # cases: image don't have getexif
                                    pass
                                wpercent = (basewidth / float(file.size[0]))
                                hsize = int((float(file.size[1]) * float(wpercent)))
                                file = file.resize((basewidth, hsize), Image.ANTIALIAS)
                                file.save('./static/img_db/' + img_name)
                                file.close()
                                img = url_for('static', filename='img_db/'+ img_name)


                            try:
                                nutriscore = product['product']['nutriscore_grade']
                            except:
                                nutriscore = '0'
                    except :
                        print('erreur')
                        img=img_name



            aliment = Aliment(titre=request.form.get("titre"),
                              quantity=request.form.get("quantity"),
                              peremption=datetime.strptime(request.form.get("peremption"), '%Y-%m-%d'),
                              frais=request.form.get("frais"),
                              ajout=datetime.today(),
                              desc=request.form.get("desc"),
                              dlc=request.form.get("dlc"),
                              nom=request.form.get("nom"),
                              image=img,
                              nutriscore =nutriscore,
                              cb=code
                              )

            db.session.add(aliment)
            db.session.commit()
        except Exception as e:
            print("Failed to add aliment")
            print(e)



    aliments = Aliment.query.all()
    return render_template("add.html", aliments=aliments)


@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        aliment = Aliment.query.filter_by(titre=oldtitle).first()
        aliment.titre = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update aliment titre")
        print(e)
    return redirect("/")


@app.route('/', methods=["GET", "POST"])
def list():
    filter = request.form.get("filter")
    order = request.form.get("order")
    if filter == "sec":
        aliments = Aliment.query.filter_by(frais='sec')
    elif filter == "frais":
        aliments = Aliment.query.filter_by(frais='frais')
    elif filter == "ok":
        ajd = datetime.today()
        aliments = Aliment.query.filter(Aliment.peremption > ajd)
    elif filter == "perime":
        ajd = datetime.today()
        aliments = Aliment.query.filter(Aliment.peremption < ajd)
    elif order == "date+":
        aliments = Aliment.query.order_by(Aliment.ajout)
    elif order == "date-":
        aliments = Aliment.query.order_by(desc(Aliment.ajout))
    elif order == "dlc+":
        aliments = Aliment.query.order_by(Aliment.peremption)
    elif order == "dlc-":
        aliments = Aliment.query.order_by(desc(Aliment.peremption))
    elif order == "name":
        aliments = Aliment.query.order_by(Aliment.titre)
    else:
        aliments = Aliment.query.order_by(desc(Aliment.ajout))

    return render_template("index.html", aliments=aliments)


@app.route("/delete", methods=["POST"])
def delete():
    iddelete = request.form.get("id")
    aliment = Aliment.query.filter_by(id=iddelete).first()
    db.session.delete(aliment)
    db.session.commit()
    if not ((aliment.image=="/static/img_db/frais.jpg") or (aliment.image=="/static/img_db/sec.jpg")) :
        try :
            os.remove("."+aliment.image)
        except :
            pass
    return redirect("/")


@app.route("/prendre", methods=["POST"])
def prendre():
    idtake = request.form.get("id")
    take = request.form.get("takeqty")
    oldqty = request.form.get("qty")
    aliment = Aliment.query.filter_by(id=idtake).first()
    aliment.quantity = int(oldqty) - int(take)
    db.session.commit()
    if aliment.quantity == 0:
        db.session.delete(aliment)
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route('/how')
def how():
    return render_template("how.html")


@app.route('/what')
def what():
    return render_template("what.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = '123'
    basic_auth = BasicAuth(app)
    app.debug = True
    app.run(host='192.168.0.11', port=5000)
    #app.run()
