from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

# API for TMDB "movie database":
API_KEY = "038b7b015c7941232816cb7859da867b"
API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMzhiN2IwMTVjNzk0MTIzMjgxNmNiNzg1OWRhODY3YiIsInN1YiI6IjYyZmNkMDQ4ZTU1OTM3MDA5M2JjMzFmNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.6AD5dWhwjuYubQNpFLEBZZ7842uG6y2mHktO3lOuhxw"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOBIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
BASE_URL = "http://image.tmdb.org/t/p/w200"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# 1. Create a DATABASE:
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviebase.db'
db = SQLAlchemy(app)


# 2. Create a TABLE "Movies":
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


# 3. Inserting VALUE into table "Movies" but only once:
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a\
#                  phone booth, pinned down by an extortionist's sniper\
#                  rifle. Unable to leave or receive outside help, Stuart's\
#                  negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


# 4. Make a form to pass in to the "edit movie" page:
class EditForm(FlaskForm):
    user_rating = StringField(label='Your rating out of 10: ')
    user_review = StringField(label='Your review: ')
    submit = SubmitField(label='SUBMIT')


# 7.1 Make a form to pass in to the "add movie" page:
class AddForm(FlaskForm):
    user_movie = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


# 5. Make a route for "edit movie" page and pass in the previously created form with "EditForm" class:
@app.route("/edit", methods=['POST', 'GET'])
def edit():
    form = EditForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.user_rating.data)
        movie.review = form.user_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)


# 6. Make a route that will DELETE a movie when button "delete" is pressed in "index.html":
@app.route("/delete", methods=['POST', 'GET'])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


# 7. Make a route that will ADD a movie when "add" button is pressed in "index.html":
@app.route("/add", methods=['POST', 'GET'])
def add():
    form = AddForm()

    if form.validate_on_submit():
        movie = form.user_movie.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={
            "api_key": API_KEY,
            "query": movie
        })
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOBIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={
            "api_key": API_KEY
        })
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f'{BASE_URL}{data["poster_path"]}',
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
