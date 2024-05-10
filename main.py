from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return result


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafes_dict_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafes_dict_list)


@app.route("/search", methods=["GET"])
def get_cafe_by_location():
    loc = request.args.get("loc")
    cafes_loc = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    if cafes_loc:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes_loc])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    result = db.session.execute(db.update(Cafe).where(Cafe.id == cafe_id).values(coffee_price=new_price))
    db.session.commit()
    if result.rowcount > 0:
        return jsonify(response={"success": "Successfully updated the price."})
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == API_KEY:
        to_delete = db.session.get(Cafe, cafe_id)
        if to_delete:
            db.session.delete(to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted cafe information."}), 200
        return jsonify(error={"Not Found": "A cafe with that id was not found in the database."}), 404
    elif api_key != API_KEY:
        return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct api key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
