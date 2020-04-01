import sys
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  

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
		recipes = Recipe.query.order_by(Recipe.created_at).all()
		return render_template('index.html', recipes=recipes)


@app.route('/explore_ingredients', methods=['GET'])
def explore_ingredients():
	ingredients = Ingredient.query.all()
	if len(ingredients) == 0:
		return "There are no ingredients in the database!"

	return render_template('ingredients.html', ingredients=ingredients)


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

	if request.method == 'POST':
		# print('app.route: /update/' + str(recipe.id), file=sys.stdout)
		# print('control flow: POST')
		# print('data pre-submit: recipe.name: ' + recipe.name, file=sys.stdout)
		recipe.name = request.form['name']
		# print('data post-submit: recipe.name: ' + recipe.name, file=sys.stdout)

		try:
			db.session.commit()
			return redirect('/update/' + str(id))
		except: 
			return "There was a problem updating data."

	else:
		title = "Update Data"
		# print('app.route: /update/' + str(recipe.id), file=sys.stdout)
		# print('control flow: !POST')
		# print('data: recipe.name: ' + recipe.name, file=sys.stdout)
		return render_template('update.html', title=title, recipe=recipe)


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

		print('ingredient.name: ' + ingredient_name, file=sys.stdout)
		# check ingredient table for ingredient_name
		ingredient = Ingredient.query.filter(Ingredient.name == ingredient_name).filter(Ingredient.measurement_unit == ingredient_unit).all()
		if len(ingredient) != 1:
			return "This ingredient is not in the database. Add separately."
		else:
			print('id: ' + str(id), file=sys.stdout)
			print('ingredient[0].id: ' + str(ingredient[0].id), file=sys.stdout)
			print('unit_amount: ' + str(unit_amount), file=sys.stdout)

			new_stuff2 = RecipeIngredient(recipe_id=id, ingredient_id=ingredient[0].id, unit_amount=unit_amount) 
			print("new_stuff2")
			print(new_stuff2)

		try: 
			db.session.add(new_stuff2)
			db.session.commit()
			return redirect('/update/' + str(id))
		except:
			return "There was a problem adding the ingredient."


		




if __name__ == '__main__':
    app.run(debug=True)