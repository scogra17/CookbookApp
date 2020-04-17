import sys
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy import func, text
from sqlalchemy import or_
from datetime import datetime
from math import inf
from werkzeug.security import generate_password_hash, check_password_hash 

from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

db = SQLAlchemy(app) 

migrate = Migrate(app, db)	

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, 
		default=datetime.utcnow)
	recipeingredient = db.relationship('RecipeIngredient', backref='recipe',\
		lazy=True)
	created_by = db.Column(db.String(100), default=None)
	is_public = db.Column(db.Boolean, default=True)  

	def __repr__(self):
		return '<Recipe %r>' % self.name 

class Ingredient(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False, 
		unique=True)
	created_at = db.Column(db.DateTime, nullable=False,
		default=datetime.utcnow)
	measurement_unit=db.Column(db.String(64), nullable=False)
	unit_cost=db.Column(db.Float(), nullable=False)
	recipeingredient = db.relationship('RecipeIngredient', backref='ingredient',\
		lazy=True)

	def __repr__(self):
		return "<Ingredient name: %r, measurement_unit: %r , \
		unit_cost: %f>"% (self.name, self.measurement_unit, self.unit_cost)

class RecipeIngredient(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
	ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
	unit_amount = db.Column(db.Float(), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<id: %r, recipe_id: %r , ingredient_id: %r>"\
		% (self.id, self.recipe_id, self.ingredient_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(1000))
    last_name = db.Column(db.String(1000))

    def __repr__(self):
    	return '<User %r>' % self.email


@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
	if request.method == 'POST':
		name = request.form['name']
		created_by = current_user.email 
		new_stuff = Recipe(name=name, created_by=created_by)

		try: 
			db.session.add(new_stuff)
			db.session.commit()
			return redirect('/add_recipe')
		except:
			return "There was a problem adding a new recipe."

	else: 
		my_recipes = Recipe.query\
			.filter_by(created_by = current_user.email)\
			.order_by(Recipe.created_at.desc()).all()
		community_recipes = Recipe.query\
			.filter(or_(Recipe.created_by != current_user.email, Recipe.created_by == None))\
			.filter(or_(Recipe.is_public == 1, Recipe.is_public == None))\
			.order_by(Recipe.created_at.desc()).all()

		return render_template('add_recipe.html', 
			my_recipes=my_recipes, community_recipes=community_recipes)


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
	    email = request.form.get('email')
	    password = request.form.get('password')
	    remember = True if request.form.get('remember') else False

	    user = User.query.filter_by(email=email).first()

	    # check if user actually exists
	    # take the user supplied password, hash it, and compare it to the hashed password in database
	    if not user or not check_password_hash(user.password, password):
	        flash('Please check your login details and try again.')
	        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page

	    # if the above check passes, then we know the user has the right credentials
	    login_user(user, remember=remember)
	    return redirect(url_for('profile'))
	else: 
	    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
	    # validate and add user to database 
	    email = request.form.get('email')
	    first_name = request.form.get('name')
	    password = request.form.get('password')

	    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

	    if user: # if a user is found, we want to redirect back to signup page so user can try again
	        flash('Email address already exists')
	        return redirect(url_for('signup'))

	     # create new user with the form data. Hash the password so plaintext version isn't saved.
	    new_user = User(email=email, first_name=first_name, password=generate_password_hash(password, method='sha256'))

	    # add the new user to the database
	    db.session.add(new_user)
	    db.session.commit()

	    return redirect(url_for('login'))
	else:
		return render_template('signup.html')
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.first_name)

@app.route('/explore_ingredients', methods=['GET', 'POST'])
@login_required
def explore_ingredients():
	if request.method == 'POST':
		name = request.form['name']
		measurement_unit = request.form['measurement_unit']
		unit_cost = request.form['unit_cost']
		new_ingredient = Ingredient(name=name, measurement_unit=measurement_unit,
			unit_cost=unit_cost)

		try: 
			db.session.add(new_ingredient)
			db.session.commit()
			return redirect('/explore_ingredients')
		except:
			return "There was a problem adding a new ingredient." 
	
	else: 
		ingredients = Ingredient.query.order_by(Ingredient.created_at.desc()).all()
		return render_template('ingredients.html', ingredients=ingredients)

@app.route('/find_recipes', methods=['GET', 'POST'])
@login_required
def find_recipes():
	if request.method == 'POST':
		form_recipe_ingredient_count = int(request.form['form_recipe_ingredient_count'] or 1000)
		form_recipe_total_cost = float(request.form['form_recipe_total_cost'] or 1000)
	
		recipes = db.session.query(\
			(Recipe.id).label('recipe_id'),\
			(Recipe.name).label('recipe_name'),
			(func.count(Ingredient.id).label('recipe_ingredient_count')),\
			(func.sum(Ingredient.unit_cost * RecipeIngredient.unit_amount).label('recipe_total_cost')))\
			.filter(Recipe.id == RecipeIngredient.recipe_id)\
			.filter(Ingredient.id == RecipeIngredient.ingredient_id)\
			.group_by(Recipe.id, Recipe.name)\
			.having(text("count(ingredient.id)<=:form_recipe_ingredient_count"))\
			.having(text("sum(ingredient.unit_cost * recipe_ingredient.unit_amount)<=:form_recipe_total_cost"))\
			.params(form_recipe_ingredient_count=form_recipe_ingredient_count, form_recipe_total_cost=form_recipe_total_cost)\
			.all()
	
		return render_template('find_recipes.html', recipes=recipes)

	else:
		return render_template('find_recipes.html')

@app.route('/explore_recipe_ingredients', methods=['GET'])
@login_required
def explore_recipe_ingredients():
	recipeIngredients = RecipeIngredient.query.all()
	if len(recipeIngredients) == 0:
		return "There are no recipe ingredients in the database!"

	return render_template('recipe_ingredients.html', recipeIngredients=recipeIngredients)



@app.route('/delete/<int:id>')
@login_required
def delete(id):
	recipe = Recipe.query.get_or_404(id)

	try: 
		db.session.delete(recipe)
		db.session.commit()
		return redirect('/add_recipe')
	except: 
		return "There was a problem deleting data."


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	recipe = Recipe.query.get_or_404(id)

	recipe_ingredients = db.session.query((Recipe.name).label('recipe_name'),\
		(Ingredient.name).label('ingredient_name'),\
		(Ingredient.measurement_unit).label('measurement_unit'),\
		(RecipeIngredient.unit_amount).label('unit_amount'),\
		(RecipeIngredient.id).label('recipe_ingredient_id'))\
		.filter(Recipe.id == RecipeIngredient.recipe_id)\
		.filter(Ingredient.id == RecipeIngredient.ingredient_id)\
		.filter(Recipe.id == id).order_by(Recipe.created_at).all()

	if request.method == 'POST':
		recipe.name = request.form['name']

		try:
			db.session.commit()
			return redirect('/update/' + str(id))
		except: 
			return "There was a problem updating data."

	else:
		title = "Update Data"
		#TODO: and ingredients as parameter and update update.html
		return render_template('update.html', title=title, recipe=recipe,\
			recipe_ingredients=recipe_ingredients)


@app.route('/update/<int:id>/add_ingredient', methods=['POST'])
@login_required
def add_ingredient(id):
	recipe = Recipe.query.get_or_404(id)
	recipeName = recipe.name
	# ingredient must already be in ingredient list. we only choose ingredient name 
	# and amount here  
	if request.method == 'POST':
		ingredient_name = request.form['ingredient_name']
		ingredient_unit = request.form['ingredient_unit']
		unit_amount = request.form['unit_amount']
		
		# check ingredient table for ingredient_name
		ingredient = Ingredient.query.filter(Ingredient.name == ingredient_name).filter(Ingredient.measurement_unit == ingredient_unit).all()
		if len(ingredient) != 1:
			return "This ingredient is not in the database. Add separately."
		else:
			new_stuff = RecipeIngredient(recipe_id=id, ingredient_id=ingredient[0].id, unit_amount=unit_amount) 

		try: 
			db.session.add(new_stuff)
			db.session.commit()
			return redirect('/update/' + str(id))
		except:
			return "There was a problem adding the ingredient."

@app.route('/update/<int:id>/delete/<int:recipe_ingredient_id>')
@login_required
def delete_recipe_ingredient(id, recipe_ingredient_id):
	recipe_ingredient = RecipeIngredient.query.get_or_404(recipe_ingredient_id)

	try: 
		db.session.delete(recipe_ingredient)
		db.session.commit()
		return redirect('/update/' + str(id))
	except: 
		return "There was a problem deleting data."


if __name__ == '__main__':
    app.run(debug=True)
