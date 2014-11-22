CATEGORY_MAP = {
        'category_id': 'id',
        'category_name': 'name',
        }

SESSION_MAP = {
        'session_id': 'id',
        'user_id': 'user_id',
        'action': 'action',
        'date_created': 'date_created',
        }
        
ANSWER_MAP = {
        'answer_id': 'id',
        'author_id': 'user_id',
        'date_created': 'created',
        'question_id': 'question_id',
        'votes': 'votes',
        }

ANSWER_EDIT_MAP = {
        'edit_id': 'id',
        'answer_id': 'answer_id',
        'date_created': 'created',
        'body': 'body',
        }

ANSWER_VOTE_MAP = {
        'answer_vote_id': 'id',
        'answer_id': 'answer_id',
        'voter_id': 'user_id',
        'direction': 'direction',
        'date_created': 'created',
        }

ANSWER_STATUS_MAP = {
        'status_id': 'id',
        'answer_id': 'answer_id',
        'status': 'status',
        'date_created': 'created',
        }

QUESTION_MAP = {
        'question_id': 'id',
        'author_id': 'user_id',
        'category_id': 'category_id',
        'date_created': 'created',
        'votes': 'votes',
        'views': 'views',
        }

QUESTION_EDIT_MAP = {
        'edit_id': 'id',
        'question_id': 'question_id',
        'date_created': 'created',
        'title': 'title',
        'body': 'body',
        }

QUESTION_VOTE_MAP = {
        'question_vote_id': 'id',
        'question_id': 'question_id',
        'voter_id': 'user_id',
        'direction': 'direction',
        'date_created': 'created',
        }

QUESTION_STATUS_MAP = {
        'status_id': 'id',
        'question_id': 'question_id',
        'status': 'status',
        'date_created': 'created',
        }

USER_MAP = {
        'user_id': 'id',
        'user_name': 'name',
        'password': 'password',
        'date_created': 'created',
        'avatar_url': 'avatar',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'age': 'age',
        'area': 'area',
        'email': 'email',
        'about_me': 'about',
        'rank': 'rank',
        }

#Table names and correspond field mappings
FIELD_MAPS = {
        'category': CATEGORY_MAP,
        'session': SESSION_MAP,
        'user': USER_MAP,
        'answer': ANSWER_MAP,
        'answer_edit': ANSWER_EDIT_MAP,
        'answer_vote': ANSWER_VOTE_MAP,
        'answer_status': ANSWER_STATUS_MAP,
        'question': QUESTION_MAP,
        'question_edit': QUESTION_EDIT_MAP,
        'question_vote': QUESTION_VOTE_MAP,
        'question_status': QUESTION_STATUS_MAP,
        }

from menorm import DataModel, QuerySelect, QueryInsert, ModelBuilder

class User(DataModel):
    table = 'user'
    primary_key = 'user_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(User, self).__init__()

    @classmethod	
    def get_by_name(cls,name):
        query = QuerySelect(cls, where=('user_name', name))

        model = ModelBuilder(cls, query.execute())
        return model.build()
    
    def answers(self):
       answers = Answer.get(where=('user_id',self.id))
       return answers

class Question(DataModel):
    table = 'question'
    primary_key = 'question_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(Question, self).__init__()
        self.body = None
        self.title = None

    def insert(self):
        super(Question, self).insert()

        #create first edit
        new_edit = QuestionEdit()
        new_edit.title = self.title
        new_edit.body = self.body
        new_edit.question_id = self.id

        new_edit.insert()

        #create first status
        new_status = QuestionStatus()
        new_status.status = 'unsolved'
        new_status.question_id = self.id

        new_status.insert()

    def new_edit(self):
        edit = QuestionEdit()
        edit.question_id = self.id
        return edit

    def answers(self):
       answers = Answer.get(where=('question_id',self.id))
       return answers

    @classmethod	
    def get_latest(cls, lim=None):
        if not lim:
            query = QuerySelect(cls, order=('date_created','asc'))
        else:
            query = QuerySelect(cls,
                    order=('date_created','asc'),
                    limit=lim,
                    )
        models = ModelBuilder(cls, query.execute())
        return models.build()

    def latest_edit(self):
        edit = QuestionEdit.latest(self.id)
        return edit

    def latest_status(self):
        status = QuestionStatus.latest(self.id)
        return status

    @classmethod
    def search(cls, sterm):
        q_list = Question.get_all()
        s_list = []
        for q in q_list:
            title = q.latest_edit()[0].title
            if sterm.lower().strip("<>,.?/:;'{}[]|\+=-_()*&^%$#@!~`") in  title:
                s_list.append(q)
        return s_list

class QuestionEdit(DataModel):
    table = 'question_edit'
    primary_key = 'edit_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(QuestionEdit, self).__init__()

    @classmethod
    def latest(cls, qid):
        query = QuerySelect(cls, 
                where=('question_id',qid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class QuestionVote(DataModel):
    table = 'question_vote'
    primary_key = 'question_vote_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(QuestionVote, self).__init__()

    @classmethod
    def latest(cls, qid):
        query = QuerySelect(cls, 
                where=('question_id',qid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class QuestionStatus(DataModel):
    table = 'question_status'
    primary_key = 'status_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(QuestionStatus, self).__init__()

    @classmethod
    def latest(cls, qid):
        query = QuerySelect(cls, 
                where=('question_id',qid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class Answer(DataModel):
    table = 'answer'
    primary_key = 'answer_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(Answer, self).__init__()

    def insert(self):
        super(Answer, self).insert()

        #create first edit
        new_edit = AnswerEdit()
        new_edit.title = self.title
        new_edit.body = self.body
        new_edit.question_id = self.id
        new_edit.insert()

        #create first status
        new_status = AnswerStatus()
        new_status.status = 'unsolved'
        new_status.answer_id = self.id
        new_status.insert()

    def new_edit(self):
        edit = QuestionEdit()
        edit.question_id = self.id
        return edit

    def latest_edit(self):
        edit = AnswerEdit.latest(self.id)
        return edit

class AnswerEdit(DataModel):
    table = 'answer_edit'
    primary_key = 'edit_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(AnswerEdit, self).__init__()

    @classmethod
    def latest(cls, aid):
        query = QuerySelect(cls, 
                where=('answer_id',aid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class AnswerVote(DataModel):
    table = 'answer_vote'
    primary_key = 'answer_vote_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(AnswerVote, self).__init__()

    @classmethod
    def latest(cls, qid):
        query = QuerySelect(cls, 
                where=('answer_id',qid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class AnswerStatus(DataModel):
    table = 'answer_status'
    primary_key = 'status_id'
    field_map = FIELD_MAPS[table]

    def __init__(self):
        super(AnswerStatus, self).__init__()

    @classmethod
    def latest(cls, qid):
        query = QuerySelect(cls, 
                where=('answer_id',qid),
                order=('date_created','desc'),
                limit=1,
                )

        model = ModelBuilder(cls, query.execute())
        return model.build()		

class Session(DataModel):
    table = 'session'
    primary_key = 'session_id'
    field_map = FIELD_MAPS[table]
    
class Category(DataModel):
    table = 'category'
    primary_key = 'category_id'
    field_map = FIELD_MAPS[table]

