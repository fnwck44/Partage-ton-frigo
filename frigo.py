import os
from datetime import datetime
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db: SQLAlchemy = SQLAlchemy(app)


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

    def __repr__(self):
        return "<Title: {}>".format(self.titre), \
               "<Quantity:{}>".format(self.quantity), \
               "Peremption:{}".format(self.peremption), \
               "Ajout:{}".format(self.ajout), \
               "frais:{}".format(self.frais), \
               "desc:{}".format(self.desc), \
               "dlc:{}".format(self.dlc),\
               "nom:{}".format(self.nom),


@app.route('/ajout', methods=["GET", "POST"])
def home():
    aliments = None
    if request.form:
        try:
            aliment = Aliment(titre=request.form.get("titre"),
                              quantity=request.form.get("quantity"),
                              peremption=datetime.strptime(request.form.get("peremption"), '%Y-%m-%d'),
                              frais=request.form.get("frais"),
                              ajout=datetime.today(),
                              desc=request.form.get("desc"),
                              dlc=request.form.get("dlc"),
                              nom=request.form.get("nom"))

            db.session.add(aliment)
            db.session.commit()
        except Exception as e:
            print("Failed to add aliment")
            print(e)
    aliments = Aliment.query.all()
    return render_template("ajout.html", aliments=aliments)


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
    aliments = Aliment.query.all()
    aliments = Aliment.query.order_by(func.max(ajout.Aliment))
    return render_template("demo.html", aliments=aliments)


@app.route("/delete", methods=["POST"])
def delete():
    iddelete = request.form.get("id")
    aliment = Aliment.query.filter_by(id=iddelete).first()
    db.session.delete(aliment)
    db.session.commit()
    return redirect("/")


@app.route("/prendre", methods=["POST"])
def prendre():
    idtake = request.form.get("id")
    take = request.form.get("takeqty")
    oldqty = request.form.get("qty")
    aliment = Aliment.query.filter_by(id=idtake).first()
    aliment.quantity = int(oldqty)-int(take)
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
if __name__ == "__main__":
    app.run(debug=True)
