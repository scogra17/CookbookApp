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

	def __repr__(self):
		return '<Recipe %r>' % self.name 

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
		print('app.route: /update/' + str(recipe.id), file=sys.stdout)
		print('control flow: POST')
		print('data pre-submit: recipe.name: ' + recipe.name, file=sys.stdout)
		recipe.name = request.form['name']
		print('data post-submit: recipe.name: ' + recipe.name, file=sys.stdout)

		try:
			db.session.commit()
			return redirect('/')
		except: 
			return "There was a problem updating data."

	else:
		title = "Update Data"
		print('app.route: /update/' + str(recipe.id), file=sys.stdout)
		print('control flow: !POST')
		print('data: recipe.name: ' + recipe.name, file=sys.stdout)
		return render_template('update.html', title=title, recipe=recipe)



if __name__ == '__main__':
    app.run(debug=True)