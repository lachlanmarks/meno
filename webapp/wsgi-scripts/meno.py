from werkzeug.wrappers import Request, Response
import werkzeug.contrib.sessions as sessions
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.utils import redirect
from werkzeug.exceptions import HTTPException
import templater
import views
from utils import url_map, local, local_manager

session_store = sessions.FilesystemSessionStore()

class Meno(object):

    def handle_request(self, request):
        url_adapter = url_map.bind_to_environ(request.environ)
        local.request.session['last'] = request.base_url
        try:
            endpoint, values = url_adapter.match()
            route = getattr(views, endpoint)
            response = route(request, **values)
        except NotFound, e:
            response = views.not_found(request)
        except HTTPException, e:
            response = views.not_found(request)
 
        return response

    def save_cookies(self, request, response):
        if request.session.should_save:
            session_store.save(request.session)
            response.set_cookie('cookie_meno', request.session.sid)

    def wsgi_app(self, environ, start_response):
        local.request = request = Request(environ)
        session_cookie = request.cookies.get('cookie_meno')
        if session_cookie is None:
            request.session = session_store.new()
            request.session['session_count'] = 0
            request.session['uid'] = 0
        else:
            request.session = session_store.get(session_cookie)
            if 'uid' not in request.session:
                request.session['uid'] = 0
        try:
            local.request.session['count'] += 1
        except KeyError:
            local.request.session['count'] = 0

        response = self.handle_request(request)
        self.save_cookies(request, response)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def new_app(**kwargs):
    return local_manager.make_middleware(Meno())
