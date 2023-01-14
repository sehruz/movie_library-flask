
from dataclasses import asdict
from datetime import datetime
import functools
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from moduls import Model, User
from passlib.hash import pbkdf2_sha256
from move_library.forms import ExtendedMovieForm, LoginForm, MovieForm, RegisterForm



pages=Blueprint('pages', __name__, static_folder='static', template_folder='templates')

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get('email') is None:
            return redirect(url_for('.login'))
        return route(*args,**kwargs)
    return route_wrapper

@pages.route('/')
@login_required
def index():
    user_data=current_app.db.user.find_one({'email': session['email']})
    user=User(**user_data)

    movie_data=current_app.db.movie.find({'_id': {'$in': user.movie}})
    movies=[Model(**movie) for movie in movie_data]
    
    return render_template('index.html', movies_data=movies)


@pages.route('/register', methods=['POST', 'GET'])
def register():
    if session.get('email'):
        return redirect(url_for('.index'))
    
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(
            _id= uuid.uuid4().hex,
            email=form.email.data,
            password= pbkdf2_sha256.hash(form.password.data)
        )
        current_app.db.user.insert_one(asdict(user))

        flash('User Registered successfully', 'success')

        return redirect(url_for('.login'))
    return render_template('register.html', title='Movie Whatchlist | Register', form=form)


@pages.route('/login', methods=['POST','GET'])
def login():

    if session.get('email'):
        return redirect(url_for('.index'))
    
    form=LoginForm()

    if form.validate_on_submit():
        user_data=current_app.db.user.find_one({'email': form.email.data})
        if not user_data:
            flash('Login is not correct', category='danger')
            return redirect(url_for('.login'))
        user=User(**user_data)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session['user_id']=user._id
            session['email']=user.email

            return redirect(url_for('.index'))
        
        flash('You Log in not correct', category='danger')
    
    return render_template('login.html',title='Movie Whatlist | Login', form=form)

@pages.route('/logout')
def logout():
    # this will keep theme in session
    # current_theme=session['theme']
    # session.clear()
    # session['theme']=current_theme

    # delete one by one

    del session['user_id']
    del session['email']

    return redirect(url_for('.login'))



   

@pages.route('/edit/<string:_id>', methods=['POST', 'GET'])
@login_required
def edit_movie(_id: str):
    movie=Model(**current_app.db.movie.find_one({'_id': _id}))
    form=ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title=form.title.data
        movie.director=form.director.data
        movie.year=form.year.data
        movie.cast=form.cast.data
        movie.series=form.series.data
        movie.tags=form.tags.data
        movie.description=form.description.data
        movie.video_link=form.video_link.data

        current_app.db.movie.update_one({'_id':movie._id},{'$set': asdict(movie)})
        return redirect(url_for('.movie_details', _id=movie._id))
    return render_template('movie_form.html', movie=movie, form=form)

@pages.route('/movie/<string:_id>')
def movie_details(_id: str):
      movie=current_app.db.movie.find_one({'_id': _id})
      movie_det=Model(**movie)

      return render_template('movie_details.html',movie=movie_det )


@pages.get('/movie/<string:_id>/rate')
@login_required
def rating(_id: str):
    rating=int(request.args.get('rating'))
    current_app.db.movie.update_one({'_id': _id}, {'$set': {'rating': rating }})
    return redirect(url_for('.movie_details', _id=_id, ))


@pages.get('/movie/<string:_id>/watched')
@login_required
def last_watched(_id: str):
    last_watched=datetime.today()
    print(last_watched)
    current_app.db.movie.update_one({'_id': _id}, {'$set': {'last_watched': last_watched }})
    return redirect(url_for('.movie_details', _id=_id, ))




@pages.route('/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    form=MovieForm()

    if form.validate_on_submit():
        movie=Model(
            _id= uuid.uuid4().hex,
            title= form.title.data,
            director=form.director.data,
            year=form.year.data
        )
        current_app.db.movie.insert_one(asdict(movie))
        current_app.db.user.update_one({'_id': session.get('user_id')}, {'$push':{'movie':movie._id}})
        return redirect(url_for('.index'))

    return render_template('new_movie.html', form=form)



@pages.get('/toggle_theme')
def toggle_theme():
    current_theme=session.get('theme')
    if current_theme == 'dark':
        session['theme']='light'
    else:
        session['theme']='dark'
    
    return redirect(request.args.get('current_page'))