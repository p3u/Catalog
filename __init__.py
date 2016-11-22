import os
import random
import string
import requests
import httplib2
import json
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, flash, send_from_directory, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Product, User
from werkzeug.utils import secure_filename
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

UPLOADED_IMGS_FOLDER = '/var/www/app/app/img/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOADED_IMGS_FOLDER
app.secret_key = 'pass'
engine = create_engine('postgresql://catalog:pass@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('/var/www/app/app/client_secrets.json', 'r').read())['web']['client_id']


def upsertUser(login_session):
    q = session.query(User).filter(User.id == login_session['gplus_id'])
    if (q.count() > 0):
        user = q.first()
        user.email = login_session['email']
    else:
        newUser = User(email=login_session['email'],
                       id=login_session['gplus_id'])
        session.add(newUser)

    session.commit()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/login/", methods=["GET"])
def showLogin():
    if request.method == "GET":
        state = "".join(random.choice(
                        string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session["state"] = state
        return render_template("login.html", STATE=login_session["state"])


@app.route("/gconnect", methods=["POST"])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    print code
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/app/app/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['email'] = data['email']

    upsertUser(login_session)
    response = make_response(redirect('/index'))
    response.set_cookie('user_id', value=gplus_id)
    return response


@app.route('/gdisconnect',  methods=["POST"])
def gdisconnect():
    access_token = login_session['credentials']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['email']
        response = make_response(redirect('/index'))
        response.headers['Content-Type'] = 'application/json'
        response.set_cookie('user_id', '', expires=0)
        return response
    else:
        print result
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/index/JSON/')
def indexJSON():
    # Adding Categories to the JSON Dictionary
    index = {"categories": {}}
    categories = session.query(Category).all()
    for category in categories:
        index["categories"][category.id] = {}
        index["categories"][category.id]["name"] = category.name
        index["categories"][category.id]["user_id"] = category.user_id
        index["categories"][category.id]["products"] = {}

    # Adding Products to the JSON Dictionary (Nested inside it's category)
    products = session.query(Product).all()
    for product in products:
        # Getting every attribute and value in that Object, to add to the JSON
        product_attributes = {}
        for attribute, value in product.__dict__.iteritems():
            # This is some SQLalchemy attribute that we don't care about
            if(attribute != "_sa_instance_state"):
                product_attributes[attribute] = value
        if(product.category_id in index["categories"]):
            index["categories"][product.category_id]["products"][product.id] =\
                                                            product_attributes
        else:
            print("ALERT: The product with ID " + str(product.id))
            print("is in the deleted category " + str(product.category_id))
    return jsonify(index)


# Main page where products are listed
@app.route("/", methods=["GET"])
@app.route("/index/", methods=["GET"])
def listProducts():
    if request.method == "GET":
        state = "".join(random.choice(
                        string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        if "state" not in login_session:
            login_session["state"] = state
        categories = session.query(Category).all()
        if "gplus_id" not in login_session:
            gplus_id = ""
        else:
            gplus_id = login_session["gplus_id"]
        return render_template("catalog.html",
                               categories=categories,
                               logged_user_id=gplus_id,
                               STATE=login_session["state"])


# New product
@app.route("/new/product/<int:category_id>/", methods=["GET", "POST"])
def addProduct(category_id):
    if "email" not in login_session:
        return redirect(url_for("showLogin"))
    if request.method == "GET":
        return render_template("newproduct.html", category_id=category_id)
    if request.method == "POST":
        if 'image' not in request.files:
            flash('Please upload an image for the product')
            return redirect(request.url)
        file = request.files['image']
	imgpath = ""
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('Please upload an image for the product')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imgpath = "/uploads/" + filename
        newProduct = Product(name=request.form['name'],
                             description=request.form['description'],
                             price=request.form['price'],
                             category_id=category_id,
                             imgpath=imgpath,
                             user_id=login_session['gplus_id'])
        session.add(newProduct)
        session.commit()
        return redirect(url_for("listProducts"))


@app.route("/" + UPLOADED_IMGS_FOLDER + "/<filename>")
def uploaded_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# New Category
@app.route("/new/category", methods=["GET", "POST"])
def addCategory():
    if "email" not in login_session:
        return redirect(url_for("showLogin"))
    if request.method == "GET":
        return render_template("newcategory.html")
    if request.method == "POST":
        if "email" in login_session:
            if (request.form["name"] != ""):
                newCategory = Category(name=request.form['name'],
                                       user_id=login_session['gplus_id'])
                session.add(newCategory)
                session.commit()
            else:
                flash("A category must have a name.")
                return render_template("newcategory.html")

            return redirect(url_for("listProducts"))


@app.route('/delete/<string:item_type>/<int:id>/<string:name>/',
           methods=['GET', 'POST'])
def deleteItem(item_type, id, name):
    if "email" not in login_session:
        return redirect(url_for("showLogin"))
    if request.method == "GET":
        return render_template("deleteitem.html", item_type=item_type, id=id,
                               name=name)
    if request.method == "POST":
        if item_type == "category":
            category = session.query(Category).filter(Category.id == id)
            if (category.first().user_id == login_session['gplus_id']):
                category.delete(synchronize_session=False)
                session.query(Product).filter(Product.category_id == id).\
                    delete(synchronize_session=False)
            else:
                return render_template("notallowed.html")
        if item_type == "product":
            product = session.query(Product).filter(Product.id == id)
            if (product.first().user_id == login_session['gplus_id']):
                product.delete(synchronize_session=False)
            else:
                return render_template("notallowed.html")
        return redirect(url_for("listProducts"))


@app.route('/edit/<string:item_type>/<int:id>/',
           methods=['GET', 'POST'])
def editItem(item_type, id):
    if "email" not in login_session:
        return redirect(url_for("showLogin"))
    if request.method == "GET":
        if (item_type == "product"):
            product = session.query(Product).filter(Product.id == id).first()
            if (product.user_id == login_session['gplus_id']):
                return render_template("editproduct.html", product=product)
            else:
                return render_template("notallowed.html")
        if (item_type == "category"):
            category = session.query(Category).filter(Category.id == id).first()
            if (category.user_id == login_session['gplus_id']):
                return render_template("editcategory.html", category=category,
                                       user_id=login_session['gplus_id'])
            else:
                return render_template("notallowed.html")
    if request.method == "POST":
        if (item_type == "product"):
            product = session.query(Product).filter(Product.id == id).first()
            if (product.user_id == login_session['gplus_id']):
                product.name = request.form['name']
                product.description = request.form['description']
                product.price = request.form['price']
                if(request.form['name'] == "" or
                   request.form['description'] == "" or
                   request.form['price'] == ""):
                    flash('Product must have a name, description and price')
                    return render_template("editproduct.html", product=product)
                else:
                    file = request.files['image']
                    # if user does not select file, browser also
                    # submit a empty part without filename
                    if (file.filename != ''):
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                      filename))
                            product.imgpath = url_for('uploaded_img',
                                                      filename=filename)
                    session.commit()
        if (item_type == "category"):
            category = session.query(Category).filter(Category.id == id).first()
            if (category.user_id == login_session['gplus_id']):
                category.name = request.form['name']
                if(request.form['name'] == ""):
                    flash('Category must have a name')
                    return render_template("editcategory.html",
                                           category=category,
                                           user_id=login_session['gplus_id'])
                else:
                    session.commit()
        return redirect(url_for("listProducts"))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
