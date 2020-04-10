import sys
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy import func, text
from datetime import datetime
from math import inf 

from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 

migrate = Migrate(app, db)	

class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, 
		default=datetime.utcnow)
	recipeingredient = db.relationship('RecipeIngredient', backref='recipe',\
		lazy=True) 

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


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		name = request.form['name']
		new_stuff = Recipe(name=name)

		try: 
			db.session.add(new_stuff)
			db.session.commit()
			return redirect('/')
		except:
			return "There was a problem adding a new recipe."

	else: 
		recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
		return render_template('index.html', recipes=recipes)


@app.route('/explore_ingredients', methods=['GET', 'POST'])
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
		
		print(recipes, file=sys.stdout)

		recipes = recipes.all()

# 			.having(func.count(Ingredient.id)<=":recipe_ingredient_count")\
# 			.having(func.sum(Ingredient.unit_cost * RecipeIngredient.unit_amount)<=":recipe_total_cost")\
	
		return render_template('find_recipes.html', recipes=recipes)

	else:
		return render_template('find_recipes.html')

@app.route('/explore_recipe_ingredients', methods=['GET'])
def explore_recipe_ingredients():
	recipeIngredients = RecipeIngredient.query.all()
	if len(recipeIngredients) == 0:
		return "There are no recipe ingredients in the database!"

	return render_template('recipe_ingredients.html', recipeIngredients=recipeIngredients)



@app.route('/delete/<int:id>')
def delete(id):
	recipe = Recipe.query.get_or_404(id)

	try: 
		db.session.delete(recipe)
		db.session.commit()
		return redirect('/')
	except: 
		return "There was a problem deleting data."


@app.route('/update/<int:id>', methods=['GET', 'POST'])
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

	print(recipe_ingredients, file=sys.stdout)

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