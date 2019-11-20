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

db = SQLAlchemy(app)

class Aliment(db.Model):
    nom = db.Column(db.String(80),  nullable=False, primary_key=True)
    quantity = db.Column(db.Integer,  nullable=False, primary_key=True)
    peremption = db.Column(db.Date)
    ajout = db.Column(db.Date)

    def __repr__(self):
        return "<Title: {}>".format(self.nom),\
               "<Qt:{}>".format(self.quantity),\
               "Per:{}".format(self.peremption),\
               "Ajt:{}".format(self.ajout),


@app.route('/', methods=["GET", "POST"])
def home():
    aliments = None
    if request.form:
        try:
            aliment = Aliment(nom=request.form.get("nom"),
                              quantity=request.form.get("quantity"),
                              peremption=datetime.strptime(request.form.get("peremption"), '%Y-%m-%d'),
                              ajout=datetime.today())

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
        aliment = Aliment.query.filter_by(nom=oldtitle).first()
        aliment.nom = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update aliment nom")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    nom = request.form.get("nom")
    aliment = Aliment.query.filter_by(nom=nom).first()
    db.session.delete(aliment)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
