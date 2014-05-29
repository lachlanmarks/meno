
def route(end_point, args, request):

	map = {'question': 'question page',
			'index': "<a href='/register'>register</a>",
			'register': register(args, request),
			'login': login(request)
			}

	return map[end_point]

def login(request):
	if not request.form:
		return forms.login
	form = request.form
	username = form['username']
	password = form['password']
	user = model.User.get_by_name(username)
	if not user:
		return 'sorry, never heard of %s!' % username
	else:
		if user.password == password:
			return 'good job!'
		else:
			return 'wrong!'
		
def register(args, request):
	if not request.form:
		return forms.register #view 
	form = request.form
	username = form['username']
	password = form['password']
	if model.User.get_by_name(username):
		return 'user name "{0}" already taken'.format(username) #view
	else:
		user = model.User()
		user.name = username
		user.password = password
		user.insert()
		return 'done!' #view
