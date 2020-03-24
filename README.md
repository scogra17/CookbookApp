## Starting the app 
$ pipenv shell 
$ python app.py

## Adding to the db 

1. Create the new model in app.py 
2. In a python shell, run:
	$ from app import db
	$ db.create_all()
	$ from app import <Object name> 
	$ obj.<Object name>(<pk>='<pk_value>')
	$ db.session.add(obj)
	$ db.session.commit()

3. In a python shell, access by: 
	$ <Object name>.query.all()


## Project journal 
https://docs.google.com/document/d/1fzTE_AFB1A7JmUz-4jXnifOgEtxpAvjl_dLOgh2XTK8/edit?usp=sharing

## Reviewing Flask 
https://medium.com/technest/build-a-crud-app-with-flask-bootstrap-heroku-60dfa3a788e8

## Killing process
https://dev.to/dechamp/the-dreaded-bind-address-already-in-use-kill-it-583l
$lsof -i :<PORT#>
$kill -9 <PID>

## Troubleshooting 

### Css changes won't load in broswer
The browser is likely caching the old main.css. Click 'reload' while holding down the 'shift' key to do a full reload of the browser. 