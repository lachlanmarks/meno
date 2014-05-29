from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from utils import local, route, auth, user_login, count
from models import User, Question, Answer, Category, QuestionStatus, AnswerEdit
from templater import Page, Login, Profile, QuestionsList, UsersList, PostQuestion, Register, Thread 

def respond(text):
    return Response(text, mimetype='text/html')

def not_found(request, **kwargs):
    page = Page()
    page.title = "Oops! - Meno"
    return respond(page.render("Page not found! Meno is really, really sorry."))

@route('/')
def index(request,**kwargs):
    return questions(request)

@route('/myprofile')
def myprofile(request, **kwargs):
    if not local.request.session['uid']:
        return questions(request)
    else:
        return user(request, local.request.session['uid'])

@route('/asking')
def asking(request, **kwargs):
    try:
        q_body = request.form['question-body']
        q_title = request.form['question-title']
        q_cat = request.form['question-category']
    except KeyError:
        return questions(request)

    q = Question()
    q.views = 0
    q.votes = 0
    q.body = q_body
    q.title = q_title
    q.category_id = Category.get(where=('category_name',q_cat))[0].id
    q.user_id = local.request.session['uid']

    q.insert()
    return question(request, qid = q.id)

@route('/registering')
def asking(request, **kwargs):
    try:
        u_fname = request.form['fname']
        u_lname = request.form['lname']
        u_username = request.form['username']
        u_email = request.form['email']
        u_password = request.form['pass']
        u_confirm_password = request.form['confirm-pass']
        u_location = request.form['location']
        u_day = request.form['dob-day']
        u_month = request.form['dob-month']
        u_year = request.form['dob-year']
        u_about_me = request.form['question-body']
        u_avatar_url = request.form['profile-pic']
    except KeyError:
        return questions(request)

    if request.form['pass'] != request.form['confirm-pass']:
        return register(request)
    u = User()
    u.first_name = request.form['fname']
    u.last_name = request.form['lname']
    u.name = request.form['username']
    u.email = request.form['email']
    u.password = request.form['pass']
    u.area = request.form['location']
    #u.day = request.form['dob-day']
    #u.month = request.form['dob-month']
    #u.year = request.form['dob-year']
    u.age = 18
    u.about = request.form['question-body']
    u.avatar = request.form['profile-pic']

    u.insert()
    print "the new uid is %s" % u.id
    user_login(u.id)
    return questions(request)


@route('/questions')
def questions(request, **kwargs):
    page_data = []
    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name

    page = Page(session_data)
    if 'search' in request.args:
        questions_list = Question.search(request.args['search'])
        page.title = "Questions - '%s' - Meno" % request.args['search']
    if 'sort' in request.args:
        sorts = {
            'new': 'date_created',
            }
        sort_attr = sorts[request.args['sort']]
        questions_list = Question.get(order=(sort_attr, 'desc'), limit=30)
    else:
        page.title = 'Questions - Meno'
        questions_list = Question.get_latest(30)
    for question in questions_list:
        edit = question.latest_edit()[0]
        user = User.get_by_id(question.user_id)[0]
        age = question.age()
        stat = question.latest_status()[0]
        question_data = {
                'question_id': str(question.id),
                'user_id': str(question.user_id),
                'views': str(question.views),
                'votes': str(question.votes),
                'date_created': str(question.created),
                'category': str(Category.get_by_id(question.category_id)[0].name),
                'answers_count': str(count(question.answers())),
                'title': str(edit.title),
                'user': str(user.name),
                'status': str(stat.status),
                'age': str("Asked %sh %sm %ss ago" % (age[0], age[0], age[1])),
                }
        page_data.append(question_data)
        
    
    content = QuestionsList(page_data)

    local.request.session['last'] = request.base_url
    return respond(page.render(content))

@route('/users')
def users(request, **kwargs):
    page_data = []
    users_list = User.get(order=('rank', 'desc'), limit=30)
    for user in users_list:
        user_data = {
                'user_id': str(user.id),
                'username': str(user.name),
                'first_name': str(user.first_name),
                'last_name': str(user.last_name),
                'avatar': str(user.avatar),
                'area': str(user.area),
                'rank': str(user.rank),
                }
        page_data.append(user_data)

    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name

    page = Page(session_data)
    page.title = 'Users - Meno'
    content = UsersList(page_data)

    local.request.session['last'] = request.base_url
    return respond(page.render(content))
 
@route('/user/<uid>')
def user(request, uid, **kwargs):
    user = User.get_by_id(uid)[0]
    questions = Question.get(where=('author_id', uid), order=('date_created', 'desc'))
    try:
        user.questions_count = len(questions)
    except TypeError:
        user.questions_count = None

    answers = Answer.get(where=('author_id', uid), order=('date_created', 'desc'))
    try:
        user.answers_count = len(questions)
    except TypeError:
        user.answers_count = None

    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name

    page = Page(session_data)
    page.title = user.name + "'s Profile - Meno"
    content = Profile(user)

    local.request.session['last'] = request.base_url
    return respond(page.render(content))

@route('/ask')
def post_question(request, **kwargs):

    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name
    else:
        return login(request, **kwargs)

    page = Page(session_data)
    page.title = 'Ask a Question - Meno'
    content = PostQuestion()
    local.request.session['last'] = request.base_url
    return respond(page.render(content))

@route('/question/<int:qid>')
def question(request, qid, **kwargs):

    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name
    try:
        question = Question.get_by_id(qid)[0]
    except TypeError:
        return not_found(request)

    question.views += 1
    question.update()

    edit = question.latest_edit()[0]
    category = Category.get_by_id(question.category_id)[0]
    user = User.get_by_id(question.user_id)[0]
    
    question_data =  {
        'title' : str(edit.title),
        'category' : str(category.name),
        'votes' : str(question.votes),
        'author' : str(user.name),
        'author_id' : str(user.id),
        'avatar' : str(user.avatar),
        'views' : str(question.views),
        'created' : str(question.created),
        'body' : str(edit.body),
        }
    
    try:
        answers_list = Answer.get(where=('question_id', qid), order=('votes', 'desc'))
        answer_data_list = []
        for answer in answers_list:
            answer_user = User.get_by_id(answer.user_id)[0]
            answer_edit = AnswerEdit.get(where=('answer_id', answer.id))[0]
            answer_data = {
                'votes' : str(answer.votes),
                'author' : str(answer_user.name),
                'author_id' : str(answer_user.id),
                'avatar' : str(answer_user.avatar),
                'body' : str(answer_edit.body),
                }
            answer_data_list.append(answer_data)
            
    except TypeError:
        answer_data_list = False
    
    page = Page(session_data)
    page.title = str(edit.title) + ' - Meno'
    content = Thread(question_data, answer_data_list)
    local.request.session['last'] = request.base_url
    return respond(page.render(content))

@route('/register')
def register(request, **kwargs):

    session_data = {}
    if local.request.session['uid']:
        session_data['user_name'] = User.get_by_id(local.request.session['uid'])[0].name

    page = Page(session_data)
    page.title = 'Register - Meno'
    content = Register()
    local.request.session['last'] = request.base_url
    return respond(page.render(content))
 
@route('/login')
def login(request, **kwargs):
    page = Page()
    try:
        user = request.form['username']
        pwd = request.form['password']
        print "*****%s******" % auth(user, pwd)
        authorized = auth(user, pwd)
    except KeyError:
        return respond(page.render(Login('You must be logged in to do that')))
    if authorized:
        user_login(authorized)
        return questions(request, **kwargs)
    else:
        content = Login('Please try again')
        return respond(page.render(content))

@route('/logout')
def logout(request, **kwargs):
    local.request.session['uid'] = 0
    page = Page()
    return questions(request, **kwargs)
    #return redirect(local.request.session['last'])

