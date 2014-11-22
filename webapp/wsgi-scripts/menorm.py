"""

    ++++++
    model.py 
    ++++++

    Object-Relational Mapping for Meno webapp.

    Provides an interface between the application layer of the app and MySQL tables.

"""

#Operators
EQ = 0
GT = 1
LT = 2
GTE = 3
LTE = 4

#SQL query templates
ST = """SELECT {cols} FROM {tbl}{WHERE}{ORDER}{LIMIT}"""
UT = """UPDATE {tbl} SET {updates} WHERE {col} = {id}"""
IT = """INSERT INTO {tbl} ({cols}) VALUES({vals})"""    

#:: Field Mappings :: (Data model attributes and their correspond table column names)



import MySQLdb
import datetime

# Class for connecting to database via MySQLdb and executing queries
class Database(object):
    # Default settings for connecting to MySQL database
    settings = {'host': 'mysql.server','port':3306,'user': 'lmarks', 'password' : 'dbtime', 'db': 'meno'}

    #MySQLdb.connect() object
    def __init__(self):
        self.connection = None
        self.cursor = None


    # Return the PRIMARY KEY of the last row inserted
    def insert_id(self):
        return self.cursor.lastrowid

    # Return the row(s) from a 'SELECT' query in as either None or a list of dict(s)) 
    def return_rows(self, cols):
        cursor = self.cursor

        if not cursor:
            return None

        try:
            rows = cursor.fetchall()
        except:
            return None

        if not rows:
            return None

        else:
            return [dict(zip(cols, r)) for r in rows]

    # Connect to MySQL database
    def connect(self):
        self.connection = MySQLdb.connect(**self.settings)

    def execute_query(self, query, params=None):

        if not self.connection or not self.connection.open:
            try:
                self.connect()

            except MySQLdb.Error:
                return None

        self.cursor = self.connection.cursor()  

        try:
            if params is not None:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()

        except MySQLdb.Error as e:
            self.connection.rollback()
            return None

#build queries from column/table names and SQL clauses
class QueryBuilder(object):
    OP_MAP = {
            EQ: '=',
            GT: '>',
            LT: '<',
            GTE: '>=',
            LTE: '<=',
            }

    def update(self, primary, table, columns, values):
        params = None
        del values[columns.index('date_created')]
   
        q = UT.format(
                tbl = table,
                updates = ', '.join(["%s=%s" % (c, '%s') for c in columns if c != 'date_created']),
                col = primary[0],
                id = primary[1], 
                )
        
        return q, tuple(values)	

    def select(self, table, columns, **kwargs):
        params = None
        if 'where' in kwargs:
            params = kwargs['where'][1]
        if 'like' in kwargs:
            params = kwargs['like'][1]

        def _limit():
            if 'limit' in kwargs:
                return " LIMIT {0}".format(kwargs['limit'])
            return ''

        def _order():
            if 'order' in kwargs:
                try:
                    return " ORDER BY {0} {1}".format(kwargs['order'][0], kwargs['order'][1])

                except IndexError:
                    return " ORDER BY {0}".format(kwargs['order'])

            return ''

        def _where():
            if 'where' in kwargs:
                try:
                    op = kwargs['where'][2]
                except IndexError:
                    op = EQ

                return " WHERE {0} {1} %s".format(kwargs['where'][0], self.OP_MAP[op])

            if 'like' in kwargs:
                return " WHERE {0} LIKE %s".format(kwargs['like'][0]) 

            return ''

        q = ST.format(
                cols = ', '.join(columns),
                tbl = table,
                WHERE = _where(), 
                ORDER = _order(),
                LIMIT = _limit(),
                )
        return q, params

    def insert(self, table, columns, values):

        q = IT.format(
                tbl = table,
                cols = ', '.join(columns),
                vals = ', '.join(['%s' for v in values]),
                )

        return q, tuple(values)	

querybuilder = QueryBuilder()

class QuerySelect(object):
    def __init__(self, model, **kwargs):
        self.params = None
        self.columns = model.fields()

        self.query, self.params = querybuilder.select(model.table, self.columns, **kwargs)

    def execute(self):
        database = Database()

        if self.params:
            self.params = (self.params,)

        database.execute_query(self.query, self.params)
        return database.return_rows(self.columns) 

class QueryUpdate(object):
    def __init__(self, model, **kwargs):
        self.params = None
        self.table = model.table
        value_dict = model.values()
        primary = (model.primary_key, model.id)

        self.query, self.params = querybuilder.update(primary, model.table, value_dict.keys(), value_dict.values())

    def execute(self):
        database = Database()
        database.execute_query(self.query, self.params)
        return database.insert_id()

class QueryInsert(object):
    def __init__(self, model):
        self.params = None
        self.table = model.table
        value_dict = model.values()

        self.query, self.params = querybuilder.insert(model.table, value_dict.keys(), value_dict.values())

    def execute(self):
        database = Database()
        database.execute_query(self.query, self.params)
        return database.insert_id()

class ModelBuilder(object):
    def __init__(self, model, lst):
        self.model = model
        self.lst = lst

    def build(self):
        field_map = self.model.field_map
        model_list = []

        if not self.lst:
            return None

        for dct in self.lst:
            new_model = self.model()
            for key in dct:
                setattr(new_model, field_map[key], dct[key]) 
            model_list.append(new_model)	

        #if len(model_list) == 1:
        #    return model_list[0]

        return model_list

class DataModel(object):
    def __init__(self):
        for f in self.field_map:
            setattr(self, self.field_map[f], None)

    @classmethod
    def fields(cls):
        flds = [f for f in cls.field_map]
        return flds

    def values(self):
        flds = [f for f in self.field_map if self.field_map[f] != 'id']
        vals = dict(zip(flds, [getattr(self, self.field_map[f]) for f in flds]))
        return vals

    def insert(self):
        query = QueryInsert(self)
        self.id = query.execute() #link current data model to inserted row via primary key

    def update(self):
        query = QueryUpdate(self)
        return query.execute()

    def age(self):
        if not getattr(self, 'created', None):
            return None
        seconds = (datetime.datetime.now() - self.created).seconds
        h, r = divmod(seconds, 3600)
        m, s = divmod(r, 60)
        return (h, m, s)

    @classmethod
    def get_all(cls):
        query = QuerySelect(cls)
        models = ModelBuilder(cls, query.execute())
        return models.build()

    @classmethod
    def get(cls,**kwargs):
        query = QuerySelect(cls, **kwargs)
        models = ModelBuilder(cls, query.execute())
        return models.build()

    @classmethod
    def get_by_id(cls,i):
        query = QuerySelect(cls, where = (cls.primary_key, i))
        models = ModelBuilder(cls, query.execute())
        return models.build()

