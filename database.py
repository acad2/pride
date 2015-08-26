""" Provides a Database object for working with sqlite3 databases """

import sqlite3

import mpre.base

def create_where_string(where):
    keys = []
    values = []
    for key, value in where.items():
        keys.append(key)
        values.append(value)
        
    condition_string = "WHERE " + "AND ".join("{} = ?".format(key) for 
                                              key in keys)
    return condition_string, values
    
class Database(mpre.base.Wrapper):
    """ An object with methods for dispatching sqlite3 commands. 
        Database objects may be simpler and safer then directly
        working with sqlite3 queries. Note that database methods
        do not commit automatically."""
        
    defaults = mpre.base.Wrapper.defaults.copy()
    defaults.update({"database_name" : '',
                     "connection" : None,
                     "cursor" : None,
                     "text_factory" : str})
        
    wrapped_object_name = "connection"
    
    def __init__(self, **kwargs):
        super(Database, self).__init__(**kwargs)
        connection, self.cursor = self.open_database(self.database_name, 
                                                     self.text_factory)
        self.wraps(connection)
        
    def open_database(self, database_name, text_factory=None):
        """ Opens database_name and obtain a sqlite3 connection and cursor.
            Database objects call this implicitly when initializing.
            Database objects wrap the connection and store the cursor
            as Database.cursor. """
        connection = sqlite3.connect(database_name)
        if text_factory:
            connection.text_factory = text_factory
        return connection, connection.cursor()
        
    def create_table(self, table_name, fields, if_not_exists=True):
        """ Creates a table in the underlying sqlite3 database. 
            fields is an iterable containing field names. The if_not_exists
            flag, which defaults to True, will only create the table
            if it does not exist already. """
        query = "CREATE TABLE{}{}({})".format(" IF NOT EXISTS " if 
                                              if_not_exists else ' ',
                                              table_name, ', '.join(fields))
        return self.cursor.execute(query)
                                                    
    def query(self, table_name, retrieve_fields=tuple(), where=None):
        """ Retrieves information from the named database table.
            retrieve_fileds is an iterable containing string names of
            the fields that should be returned. The where argument
            is a dictionary of field name:value pairs. """
        retrieve_fields = ", ".join(retrieve_fields)
        if where:
            condition_string, values = create_where_string(where)
            query_format = (retrieve_fields, table_name, condition_string)
            query = "SELECT {} FROM {} {}".format(*query_format)
            result = self.cursor.execute(query, values)
        else:
            query = "SELECT {} FROM {}".format(retrieve_fields, table_name)
            result = self.cursor.execute(query)
        return result
                                        
    def insert_into(self, table_name, values):
        """ Inserts values into the specified table. The values must
            be the correct type and the correct amount. Value types
            and quantity can be introspected via the table_info method."""
        insert_format = (table_name, 
                         ", ".join('?' for count in range(len(values))))
        query = "INSERT INTO {} VALUES({})".format(*insert_format)
        return self.cursor.execute(query, values)
    
    def delete_from(self, table_name, where=None):
        """ Removes an entry from the specified table. The where
            argument is a dictionary containing field name:value pairs."""
        if not where:
            raise ArgumentError("Failed to specify where condition(s) for {}.delete_from".format(self))
        else:
            condition_string, values = create_where_string(where)
            query = "DELETE FROM {} {}".format(table_name, condition_string)   
            return self.cursor.execute(query, values)
                                             
    def drop_table(self, table_name):
        """ Removes a table from the underlying sqlite3 database. Note
            that this will remove all entries in the specified table, and
            the data cannot be recovered."""
        self.cursor.execute("DROP TABLE {}", (table_name, ))
                
    def table_info(self, table_name):
        """ Returns a generator which yields field information for the
            specified table. Entries consist of the field index, field name,
            field type, and more."""
        return self.cursor.execute("PRAGMA table_info({})".format(table_name))
        
    def __getstate__(self):
        state = super(Database, self).__getstate__()
        del state["cursor"]
        del state["wrapped_object"]
        del state["connection"]
        state["text_factory"] = state["text_factory"].__name__
        return state
        
    def on_load(self, state):
        super(Database, self).on_load(state)
        text_factory = self.text_factory
        if text_factory == "str":
            self.text_factory = str
        elif text_factory == "unicode":
            self.text_factory = unicode
        else:
            self.text_factory = None
        connection, self.cursor = self.open_database(self.database_name, 
                                                     self.text_factory)
        self.wraps(connection)
        
    def delete(self):
        super(Database, self).delete()
        self.commit()
        self.close()        