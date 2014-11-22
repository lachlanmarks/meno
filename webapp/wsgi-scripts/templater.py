"""
templater.py

Python classes for html templating using ElementTree.etree.

Each companant of a page is represented by its own template object. The
controller will construct the page by invoking template objects of the 
page its self and its content. It must also pass the content object data and
set bool attributes in the page object to control various componants, and
then passing the template objects to page object. The page object may (and should
be initialised at any point but it must be passed the other templates before 
rendering the page and sending it to wsgi.

Logical control of the templates is via bool attributes. For example,
the attribute page.is_logged_in allows logical decisions required 
for the template depending on if a user is logged in. If this is set to
True by the controller, the navbar will be constructed of the form required.
For a list of all bool attributes see the comments before the Page class.

Data is passed to a content object on init. See comments before each class
for the data form required. It is hopefully just a model object.

"""

import copy, webbrowser, os.path, string, xml.etree.ElementTree

"""

Global variables:

"""
# Menu Maps:
MENU_QUESTIONS =	[('New','#?sort=new'), 
        ('Active','?sort=active'), 
        ('Expert Needed','?sort=expert_needed'), 
        ('Today','?sort=today'), 
        ('This Week','?sort=this_week')]
MENU_USERS = 		[('Rank','?sort=rank'), 
        ('Meetings','?sort=meetings'), 
        ('New Users','?sort=new_users'), 
        ('Moderators','?sort=moderators')]
MENU_CATEGORIES = 	[('Active','?sort=active'), 
        ('New','?sort=new'), 
        ('All','?sort=all')]
MENU_PROFILE = 		[('View Profile','#view_profile'), 
        ('Edit Profile','?edit'), 
        ('Account Settings','?settings'), 
        ('Logout','#logout')]
SUB_MENU_PROFILE = 	[('Rank','?tab=rank'), 
        ('Favourites','?tab=favourites'), 
        ('Questions','?tab=questions'), 
        ('Answers','?tab=answers'), 
        ('Chats','?tab=chats')]
SUB_MENU_THREAD = 	[('Rank','?tab=rank'), 
        ('Active','?tab=active'), 
        ('Newest','?tab=new'), 
        ('Oldest','?tab=old')] 

TEMPLATE_PATH = '/home/lmarks/meno/webapp/static/'
"""

Internal functions:

Should all be method in the Template superclass but ran out of time :(

"""
# Returns a list of elm objects with given name.
def _get_elm_by_name(template, name):
    return template.root.findall(".//*{}".format(name))

# Returns a list of a single elm object in a template with given id.
def _get_elm_by_id(template, id_name):
    return template.root.findall(".//*[@id='{}']".format(id_name))

# Returns a list of elm objects in a template with given class name.
def _get_elm_by_class(template, class_name):
    return template.root.findall(".//*[@class='{}']".format(class_name))

# Returns a list of a single elm object with given id.
def _get_subelm_by_id(elm, id_name):
    return elm.findall(".//*[@id='{}']".format(id_name))

# Returns a list of elm objects with given class name.
def _get_subelm_by_class(elm, class_name):
    return elm.findall(".//*[@class='{}']".format(class_name))

#Sets the text of a list of elm objects.
def _set_text(template, elm_list, text_in):
    for elm in elm_list:
        elm.text = text_in

# Sets a given attribute of a list of elm objects
def _set_attribute(template, elm_list, attr_in, text_in):
    for elm in elm_list:
        elm.set(attr_in, text_in)

# Inserts an xhtml template into the children of a list of elm objects at index.
# Use for inserting a new xhtml template into the current template.
def _insert_template(template, new_template_name, root_elms, index = 0):
    tmp_tree = xml.etree.ElementTree.parse('{0}/templates/{1}.xhtml'.format(TEMPLATE_PATH, new_template_name))
    tmp_root = tmp_tree.getroot()
    for elm in root_elms:
        elm.insert(index, tmp_root)

# Inserts new elm objects from a list into the given elm objects at index.
# Use for inserting existing elm objects into the current template
def _insert_element(template, root_elms, new_elms):
    for elm in root_elms:
        for new_elm in new_elms:
            elm.insert(0, new_elm.root)

# Correct the indents when printing
def _indent(elm, level = 0):
    i = "\n" + level*"  "
    if len(elm):
        if not elm.text or not elm.text.strip():
            elm.text = i + "  "
            if not elm.tail or not elm.tail.strip():
                elm.tail = i
            for elm in elm:
                _indent(elm, level + 1)
            if not elm.tail or not elm.tail.strip():
                elm.tail = i
    else:
        if level and (not elm.tail or not elm.tail.strip()):
            elm.tail = i

"""

Template classes:

"""

# Superclass for all template objects:
class Template(object):
    def __init__(self, template_name):
        self.tree = xml.etree.ElementTree.parse(TEMPLATE_PATH + 'templates/{0}.xhtml'.format(template_name))
        self.root = self.tree.getroot()
        
    # Adds its self to the given Page object. For content objects:
    def add_to_page(self, page_template):
        content_root = _get_elm_by_id(page_template, 'content-main')	
        _insert_element(self, content_root, [self])

    # Adds menus to the parent page:
    def add_content_menu(self, page_template, menu_class_name, profile_user_name = False):
        # Add the menu
        content_menu_root = _get_elm_by_id(page_template, 'content-menu-wrapper')
        if not profile_user_name:
            tmp_menu = MENU_CLASS_MAPS[menu_class_name]
        else:
            tmp_menu = ProfileMenu(profile_user_name)
        _insert_element(self, content_menu_root, [tmp_menu])

# Superclass for menus
class Menu(Template):
    def __init__(self, template_name, menu_title, menu_list, menu_root_id):
        super(Menu, self).__init__(template_name)
        # Set the title of the menu, and the first and last tabs.
        if menu_title:
            _set_text(self, _get_elm_by_class(self, '{0}-title'.format(menu_root_id)), menu_title)
        _set_text(self, _get_elm_by_class(self, '{0}-tabs-first'.format(menu_root_id)), menu_list[0][0])
        _set_attribute(self, _get_elm_by_class(self, '{0}-tabs-first'.format(menu_root_id)), 'href', menu_list[0][1])
        _set_text(self, _get_elm_by_class(self, '{0}-tabs-last'.format(menu_root_id)), menu_list[-1][0])
        _set_attribute(self, _get_elm_by_class(self, '{0}-tabs-last'.format(menu_root_id)), 'href', menu_list[-1][1])
        # Iterate over the other tabs and insert.
        menu_root = _get_elm_by_class(self, '{0}-tabs'.format(menu_root_id))[0]
        for menu_text, menu_link in menu_list[1:-1]:
            tmp_elm = xml.etree.ElementTree.Element('a')
            tmp_elm.text = menu_text
            tmp_elm.set('href', menu_link)
            menu_root.insert(menu_list.index((menu_text, menu_link)), tmp_elm)

# Menus
class QuestionsMenu(Menu):
    def __init__(self):
        super(QuestionsMenu, self).__init__('content-menu', 'All Questions', MENU_QUESTIONS, 'content-menu')

class CategoriesMenu(Menu):
    def __init__(self):
        super(CategoriesMenu, self).__init__('content-menu', 'All Categories', MENU_CATEGORIES, 'content-menu')

class UsersMenu(Menu):
    def __init__(self):
        super(UsersMenu, self).__init__('content-menu', 'All Users', MENU_USERS, 'content-menu')

class ProfileMenu(Menu):
    def __init__(self, user_name):
        super(ProfileMenu, self).__init__('content-menu', user_name, MENU_PROFILE, 'content-menu')

class ProfileSubMenu(Menu):
    def __init__(self):
        super(ProfileSubMenu, self).__init__('profile-sub-menu', None, SUB_MENU_PROFILE, 'profile-sub-menu')

class ThreadSubMenu(Menu):
    def __init__(self):
        super(ThreadSubMenu, self).__init__('thread-sub-menu', None, SUB_MENU_THREAD, 'thread-sub-menu')

# Misc Maps:
MENU_CLASS_MAPS = 	{'QuestionsMenu': QuestionsMenu(),
        'UsersMenu': UsersMenu(),
        'CategoriesMenu': CategoriesMenu(),
        'ProfileSubMenu': ProfileSubMenu(),
        'ThreadSubMenu': ThreadSubMenu() }

# Superclass for lists:
class List(Template):
    def __init__(self, template_name):
        super(List, self).__init__(template_name)
        self.list_elm = self.root
        # Generate the list
        wrapper_elm = xml.etree.ElementTree.Element('div')
        wrapper_elm.set('id', 'hidden-list-placeholder')
        list_wrapper_elm = xml.etree.ElementTree.Element('div')
        list_wrapper_elm.set('id', 'hidden-list')
        more_elm = xml.etree.ElementTree.Element('div')
        more_elm.set('id', 'display-more')
        more_elm.set('class', 'hidden-list-button')
        more_elm.text = 'Display More'
        load_elm = xml.etree.ElementTree.Element('a')
        load_elm.set('id', 'load-more')
        load_elm.set('class', 'hidden-list-button')
        load_elm.set('href', '#')
        load_elm.text = 'Load More'
        wrapper_elm.append(list_wrapper_elm)
        wrapper_elm.append(more_elm)
        wrapper_elm.append(load_elm)
        self.wrapper_elm = wrapper_elm
        self.list_wrapper_elm = list_wrapper_elm

# Lists:
class QuestionsList(List):
    def __init__(self, page_data = []):
        super(QuestionsList, self).__init__('questions-list')
        self.page_data = page_data

    def render(self, page_template):
        for data in self.page_data:
            new_list_elm = copy.deepcopy(self.list_elm)
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-rank-circle'), data['votes'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-views-circle'), data['views'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-answers-circle'), data['answers_count'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-category'), data['category'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-title'), data['title'])
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-title'), 'href', '/meno/question/' + data['question_id'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-user-link'), data['user'])
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-user-link'), 'href', '/meno/user/'+ data['user_id'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-status-text'), data['status'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'age'), data['age'])
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'q-status-icon'), 'class' , 'q-status-icon-' + data['status'])
            self.list_wrapper_elm.append(new_list_elm)
        self.root = self.wrapper_elm

        self.add_content_menu(page_template, 'QuestionsMenu')
        self.add_to_page(page_template)

class CategoriesList(List):
    def __init__(self, page_data = None):
        super(QuestionsList, self).__init__('questions-list')
        self.page_data = page_data

    def render(self, page_template):
        self.add_content_menu(page_template, 'QuestionsMenu')
        self.add_to_page(page_template)

class UsersList(List):
    def __init__(self, page_data = None):
        super(UsersList, self).__init__('users-list')
        self.page_data = page_data

    def render(self, page_template):
        for data in self.page_data:
            new_list_elm = copy.deepcopy(self.list_elm)
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-avatar'), 'src', data['avatar'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-username'), data['username'])
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-username'), 'href', '/meno/user/' + data['user_id'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-real-name'), data['first_name']+ ' ' + data['last_name'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-location'), data['area'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'user-rank-circle'), data['rank'])
            self.list_wrapper_elm.append(new_list_elm)
        self.root = self.wrapper_elm

        self.add_content_menu(page_template, 'UsersMenu')
        self.add_to_page(page_template)

class AnswersList(List):
    def __init__(self, page_data = None):
        super(AnswersList, self).__init__('answers-list')
        self.page_data = page_data

    def render(self):
        for data in self.page_data:
            new_list_elm = copy.deepcopy(self.list_elm)
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'answer-votes'), data['votes'])
            _set_attribute(new_list_elm, _get_subelm_by_class(new_list_elm, 'answer-avatar'), 'src', data['avatar'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'answer-author'), data['author'])
            _set_text(new_list_elm, _get_subelm_by_class(new_list_elm, 'answer-body'), data['body'])
            self.list_wrapper_elm.append(new_list_elm)
        self.root = self.wrapper_elm

class Register(Template):
    def __init__(self):
        super(Register, self).__init__('register')

     # Add the about me text area:
    def add_about_text_area(self):
        about_text_area = TextArea('About Me', 'about', 'Tell other users a little about yourself.')
        about_text_area_root = _get_elm_by_id(self, 'about-me-text-area')
        _insert_element(self, about_text_area_root, [about_text_area])

    def render(self, page_template):
        self.add_about_text_area()
        self.add_to_page(page_template)

class Profile(Template):
    def __init__(self, user = None):
        super(Profile, self).__init__('profile')
        self.user = user

    # Adds the profile sub menu:
    def add_profile_sub_menu(self):
        sub_menu_root = _get_elm_by_id(self, 'profile-sub-menu')
        tmp_sub_menu = ProfileSubMenu()
        _insert_element(self, sub_menu_root, [tmp_sub_menu])

    def render(self, page_template):
        _set_text(self, _get_elm_by_id(self, 'profile-title'), str(self.user.name)) 
        _set_attribute(self, _get_elm_by_id(self, 'profile-picture'), 'alt', str(self.user.avatar)) 
        _set_attribute(self, _get_elm_by_id(self, 'profile-picture'), 'src', str(self.user.avatar)) 
        _set_text(self, _get_elm_by_id(self, 'profile-rank'), 'ranks not implemented yet') 
        _set_text(self, _get_elm_by_id(self, 'profile-about'), str(self.user.about))
        _set_text(self, _get_elm_by_id(self, 'profile-name'), str(self.user.first_name) + ' ' + str(self.user.last_name))
        _set_text(self, _get_elm_by_id(self, 'profile-age'), str(self.user.age))
        _set_text(self, _get_elm_by_id(self, 'profile-username'), str(self.user.name))
        _set_text(self, _get_elm_by_id(self, 'profile-email'), str(self.user.email))
        _set_attribute(self, _get_elm_by_id(self, 'profile-email'), 'href', 'mailto:' + str(self.user.email))
        _set_text(self, _get_elm_by_id(self, 'profile-join-date'), str(self.user.created))
        _set_text(self, _get_elm_by_id(self, 'profile-seen'), 'session not implemented yet')
        _set_text(self, _get_elm_by_id(self, 'profile-location'), str(self.user.area))
        _set_text(self, _get_elm_by_id(self, 'profile-questions'), str(self.user.questions_count)) 
        _set_text(self, _get_elm_by_id(self, 'profile-answers'), str(self.user.answers_count))
        self.add_content_menu(page_template, 'ProfileMenu', str(self.user.name))
        self.add_profile_sub_menu()
        self.add_to_page(page_template)


class ProfileEdit(Template):
    def __init__(self, data = None):
        super(ProfileEdit, self).__init__('profile-edit')

    def render(self, parent):
        _set_text(self, _get_elm_by_id(self, 'error-fname'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-lname'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-email'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-old-pass'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-new-pass'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-confirm-pass'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-location'), 'test')
        _set_text(self, _get_elm_by_id(self, 'error-pic'), 'test')
        self.add_content_menu('ProfileMenu')
        self.add_to_page(page_template)

class TextArea(Template):
    def __init__(self, text_area_title, text_area_name, text_area_default_text):
        super(TextArea, self).__init__('text-area')
        _set_text(self, _get_elm_by_id(self, 'text-area-title'), text_area_title)
        _set_attribute(self, _get_elm_by_name(self, 'textarea'), 'name', text_area_name)
        _set_text(self, _get_elm_by_name(self, 'textarea'), text_area_default_text)

class PostQuestion(Template):
    def __init__(self, data = None):
        super(PostQuestion, self).__init__('post-question')

    # Adds the text area:
    def add_post_question_text_area(self):
        post_question_text_area = TextArea('Question', 'question-body', 'Enter Question Here')
        post_question_text_area_root = _get_elm_by_id(self, 'post-question-text-area')
        _insert_element(self, post_question_text_area_root, [post_question_text_area])

    def render(self, page_template):
        self.add_post_question_text_area()
        self.add_to_page(page_template)

class Thread(Template):
    def __init__(self, question_data = None, answers_data = None):
        super(Thread, self).__init__('thread')
        self.question_data = question_data
        self.answers_data = answers_data
        
    # Adds the thread sub menu:
    def add_thread_sub_menu(self):
        sub_menu_root = _get_elm_by_id(self, 'thread-sub-menu')
        tmp_sub_menu = ThreadSubMenu()
        _insert_element(self, sub_menu_root, [tmp_sub_menu])		

    # Add the answers list:
    def add_answers_list(self):
        answers = AnswersList(self.answers_data)
        answers.render()
        answers_root = _get_elm_by_id(self, 'answers-wrapper')
        _insert_element(self, answers_root, [answers])

    # Add the answer text area:
    def add_answer_text_area(self):
        answer_text_area = TextArea('Post an Answer', 'Show Formatted Answer', 'Enter Answer Here')
        answer_text_area_root = _get_elm_by_id(self, 'answer-text-area-wrapper')
        _insert_element(self, answer_text_area_root, [answer_text_area])

    def render(self, page_template):
        _set_text(self, _get_elm_by_id(self, 'question-title'), self.question_data['title'])
        _set_text(self, _get_elm_by_id(self, 'question-category'), self.question_data['category'])
        _set_text(self, _get_elm_by_id(self, 'question-category'), self.question_data['category'])
        _set_text(self, _get_elm_by_id(self, 'question-votes'), self.question_data['votes'])
        _set_text(self, _get_elm_by_id(self, 'question-author'), self.question_data['author'])
        _set_attribute(self, _get_elm_by_id(self, 'question-avatar'), 'src', self.question_data['avatar'])
        _set_text(self, _get_elm_by_id(self, 'question-views'), self.question_data['views'])
        _set_text(self, _get_elm_by_id(self, 'question-created'), self.question_data['created'])
        _set_text(self, _get_elm_by_id(self, 'question-body'), self.question_data['body'])
        if self.answers_data:
            self.add_thread_sub_menu()
            self.add_answers_list()
        self.add_answer_text_area()
        self.add_to_page(page_template)

class Login(Template):
    def __init__(self, error):
        super(Login, self).__init__('login')
        self.error = error

    def render(self, page_template):
        _set_text(self, _get_elm_by_id(self, 'error-message-wrapper'), self.error)
        self.add_to_page(page_template)

"""
Page class:

- Pass content template object on .render() method.

TO DO:
- Make elements included in the head dynamic.
"""
class Page(Template):
    def __init__(self, session_data = {}, **kwargs):
        super(Page, self).__init__('wrapper')
        self.title = 'No Title Specified'
        self.session_data = session_data

    def session_logic(self):
        # Add the nav and the dialog:
        nav_root = _get_elm_by_id(self, 'nav-links-dropdown-wrapper')
        dialog_root = _get_elm_by_id(self, 'shadow')
        try:
            self.session_data['user_name']
            _insert_template(self, 'nav-in', nav_root)
            dropdown_parent = _get_elm_by_id(self, 'dropdown-username')[0]
            dropdown_parent.text = str(self.session_data['user_name'])
        except KeyError:
            _insert_template(self, 'nav-out', nav_root)
            _insert_template(self, 'dialog', dialog_root)
        # Add first-time:
        try:
            self.session_data['session_count']
            content_root = _get_elm_by_id(self, 'content-main')
            _insert_template(self, 'first-time', content_root)
        except KeyError:
            pass

    # use trys on attribute error?
    def content_logic(self, content):
        # Escape of no content specified. Perhaps render an error?
        if not content:
            return False
        # Check if etree element or string:
        Element = type(xml.etree.ElementTree.Element(None))
        if isinstance(content, str):
             content_root = _get_elm_by_id(self, 'content-main')[0]
             content_root.text = content
        elif isinstance(content.root, Element):
            content.render(self)
        else:
            return False
        return True

    def render(self, content = False):
        # Set title:
        _set_text(self, _get_elm_by_name(self, 'title'), self.title)
        # Add content:
        if not self.content_logic(content):
            print 'Content Error: No content specified or invalid content type.'
        # Pass to session_logic for readability.
        self.session_logic()
        # Return the template as a string:
        _indent(self.root)
        return xml.etree.ElementTree.tostring(self.root, 'utf-8', 'html')

"""	
Function for locally rendering. For debug.
"""
DTD = '<!DOCTYPE html>\n'
def browse_local(template_str):
    file_name = "test.html"
    file = open(file_name, "w")
    file.write(DTD + template_str) 
    file.close()
    webbrowser.open(os.path.abspath(file_name))
