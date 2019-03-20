from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Course, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
from flask import Flask, render_template, \
                  url_for, request, redirect,\
                  flash, jsonify

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('Gclient_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Online Courses"


'''Connect to Database and create database session'''
engine = create_engine('sqlite:///coursedata.db', connect_args={
    'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
'''Decorator function for login'''


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


'''Create anti-forgery state token'''


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Validate state token'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    '''Obtain authorization code'''
    code = request.data

    try:
        '''Upgrade the authorization code into a credentials object'''
        oauth_flow = flow_from_clientsecrets('Gclient_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Check that the access token is valid.'''
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    '''Submit request, parse response - Python3 compatible'''
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    '''If there was an error in the access token info, abort.'''
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    '''Verify that the access token is used for the intended user.'''
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    '''Verify that the access token is valid for this app.'''
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        '''return response'''

    '''Store the access token in the session for later use.'''
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    '''Get user info'''
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    '''ADD PROVIDER TO LOGIN SESSION'''
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    '''see if user exists, if it doesn't make a new one'''
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
                            -webkit-border-radius: 150px;-moz-border-radius: \
                                150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


'''User Helper Functions'''


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
'''DISCONNECT - Revoke a current user's token and reset their login_session'''


@app.route('/gdisconnect')
def gdisconnect():
    '''Only disconnect a connected user.'''
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        '''Reset the user's sesson.'''
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        login_session.clear()

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        '''return response'''
        return redirect(url_for('showCourses'))
    else:
        '''For whatever reason, the given token was invalid.'''
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


'''JSON APIs to view Courses'''


@app.route('/course/<int:course_id>/menu/JSON')
def courseMenuJSON(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    items = session.query(MenuItem).filter_by(
        course_id=course_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/course/<int:course_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(course_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/course/JSON')
def coursesJSON():
    courses = session.query(Course).all()
    return jsonify(course=[r.serialize for r in courses])


'''Show all courses'''


@app.route('/')
@app.route('/course/')
def showCourses():
    courses = session.query(Course).distinct(Course.name).group_by(Course.name)
    if 'username' not in login_session:
        return render_template('publiccourses.html',
                               courses=courses)
    else:
        return render_template('courses.html', courses=courses)

'''Create a new course'''


@app.route('/course/new/', methods=['GET', 'POST'])
@login_required
def newCourse():
    if request.method == 'POST':
        newCourse = Course(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCourse)
        flash('New Course is %s Created Successfully' % newCourse.name)
        session.commit()
        return redirect(url_for('showCourses'))
    else:
        return render_template('newCourse.html')


'''Edit a course'''


@app.route('/course/<int:course_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCourse(course_id):
    editedCourse = session.query(
        Course).filter_by(id=course_id).one()
    if editedCourse.user_id != login_session['user_id']:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to edit this course." \
               "Please create your own course in order to edit.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCourse.name = request.form['name']
            flash('Course Successfully Edited %s' % editedCourse.name)
            return redirect(url_for('showCourses'))
    else:
        return render_template('editCourse.html',
                               course=editedCourse)


'''Delete a course'''


@app.route('/course/<int:course_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCourse(course_id):
    courseToDelete = session.query(
        Course).filter_by(id=course_id).one()
    if courseToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to delete this course." \
               "Please create your own course in order to delete.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(courseToDelete)
        flash('%s Successfully Deleted' % courseToDelete.name)
        session.commit()
        return redirect(url_for('showCourses',
                                course_id=course_id))
    else:
        return render_template('deleteCourse.html',
                               course=courseToDelete)


'''Showing Courses List Menu'''


@app.route('/course/<int:course_id>/')
@app.route('/course/<int:course_id>/menu/')
def showMenu(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    creator = getUserInfo(course.user_id)
    items = session.query(MenuItem).filter_by(
        course_id=course_id).all()
    if 'username' not in login_session or \
       creator.id != login_session.get('user_id'):
        return render_template('publicmenu.html', items=items,
                               course=course, creator=creator)
    else:
        return render_template('menu.html', items=items,
                               course=course, creator=creator)

'''Creating new menu item in List Menu'''


@app.route('/course/<int:course_id>/menu/new/',
           methods=['GET', 'POST'])
@login_required
def newMenuItem(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    if login_session['user_id'] != course.user_id:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to add menu items to this" \
               "course. Please create your own course in order to" \
               "add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           picture=request.form['picture'],
                           course_id=course_id,
                           user_id=course.user_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', course_id=course_id))
    else:
        return render_template('newmenuitem.html', course_id=course_id)


'''Edit Courses Menu item'''


@app.route('/course/<int:course_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editMenuItem(course_id, menu_id):
    editItem = session.query(MenuItem).filter_by(id=menu_id).one()
    course = session.query(Course).filter_by(id=course_id).one()
    if login_session['user_id'] != course.user_id:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to edit menu items to this" \
               "course. Please create your own course in order to" \
               "edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['price']:
            editItem.price = request.form['price']
        if request.form['picture']:
            editItem.picture = request.form['picture']
        session.add(editItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu',
                                course_id=course_id))
    else:
        return render_template('editmenuitem.html',
                               course_id=course_id,
                               menu_id=menu_id, item=editItem)


'''Deleting Course menu item'''


@app.route('/course/<int:course_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteMenuItem(course_id, menu_id):
    course = session.query(Course).filter_by(id=course_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != course.user_id:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to delete menu items to this" \
               "course. Please create your own course in order to" \
               "delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', course_id=course_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


'''Disconnect based on provider'''


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            login_session.clear()
            flash("You have successfully been logged out.")
            return redirect(url_for('showCourses'))
        else:
            flash("You were not logged in")
            return redirect(url_for('showCourses'))
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)