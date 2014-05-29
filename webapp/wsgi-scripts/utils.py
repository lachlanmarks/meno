from werkzeug.routing import Map, Rule
from werkzeug.local import Local, LocalManager
from models import User, Session

url_map = Map()

local = Local()
local_manager = LocalManager([local])

def string_compare(s1, s2):
    s1 = s1.lower().strip("/.,:;'*(){}[]&^%$#@!~`|/<>")
    return s1 in s2.lower()

def count(x):
    if x is None:
        return 0
    try:
        return len(x)
    except TypeError:
        return 1

def route(rule, **kwargs):
    def decorator(fn):
        kwargs['endpoint'] = fn.__name__
        url_map.add(Rule(rule, **kwargs))
        return fn
    return decorator

def auth(user_name, password):
    user = User.get_by_name(user_name) 
    if not user:
        return False
    if password == user[0].password:
        return user[0].id
    else:
        return False

def user_login(uid):
    user = User.get_by_id(uid)
    if not user:
        return None

    local.request.session['uid'] = uid
    session = Session()
    session.user_id = uid
    session.action = 'in'
    session.insert()
