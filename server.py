from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextInput
from flask_bootstrap import Bootstrap5
# sqlite database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"

db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)


# create table
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


class BootstrapTextInput(TextInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class', 'form-control')
        return super().__call__(field, **kwargs)


class AddBook(FlaskForm):
    title = StringField(label='Book Name', widget=BootstrapTextInput(), validators=[DataRequired()])
    author = StringField(label='Book Autor', widget=BootstrapTextInput(), validators=[DataRequired()])
    rating = StringField(label="Rating", widget=BootstrapTextInput(), validators=[DataRequired()])
    add = SubmitField(label="Add Book", render_kw={'class': 'btn btn-primary'})
    update = SubmitField(label="update", render_kw={'class': 'btn btn-primary'})


with app.app_context():
    db.create_all()

all_books = []


@app.route("/")
def home():
    global all_books
    result = db.session.execute(db.select(Book).order_by(Book.id))
    all_books = result.scalars()

    return render_template('index.html', books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_book = AddBook()
    if add_book.validate_on_submit():
        with app.app_context():
            new_book = Book(title=add_book.title.data, author=add_book.author.data, rating=add_book.rating.data)
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for("home"))

    return render_template('add.html', form=add_book)


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit(book_id):
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    add_book = AddBook(obj=book)
    if request.method == 'POST' and add_book.validate_on_submit():
        book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        book_to_update.title = add_book.title.data
        book_to_update.author = add_book.author.data
        book_to_update.rating = add_book.rating.data
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('edit.html', form=add_book, book_id=book_id)


# delete a specific book
@app.route("/delete/<int:book_id>")
def delete(book_id):
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
