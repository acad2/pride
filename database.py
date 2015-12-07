""" Provides a Database object for working with sqlite3 databases """
import sqlite3

import pride
import pride.base

def create_assignment_string(items):
    keys = items.keys()
    values = [items[key] for key in keys]
    return ", ".join("{} = ?".format(key) for key in keys), values    
    
def create_where_string(where):
    """ Helper function used by Database objects """
    keys = []
    values = []
    for key, value in where.items():
        keys.append(key)
        values.append(value)        
    condition_string = "WHERE " + "AND ".join("{} = ?".format(key) for 
                                              key in keys)
    return condition_string, values
    
class Database(pride.base.Wrapper):
    """ An object with methods for dispatching sqlite3 commands. 
        Database objects may be simpler and safer then directly
        working with sqlite3 queries. Note that database methods
        do not commit automatically."""
        
    defaults = {"database_name" : '', "connection" : None, 
                "cursor" : None, "text_factory" : str, "auto_commit" : True,
                "detect_types_flags" : sqlite3.PARSE_DECLTYPES,
                "return_cursor" : False}
        
    wrapped_object_name = "connection"
    
    verbosity = {"open_database" : 'v', "create_table" : "v",
                 "query_issued" : "vvv", "query_result" : "vvv",
                 "insert_into" : "vvv", "delete_from" : "vvv",
                 "drop_table" : "v", "table_info" : "vvv",
                 "update_table" : "vv"}
    
    mutable_defaults = {"from_memory" : dict}
    
    database_structure = {}
    primary_key = {}
        
    def __init__(self, **kwargs):
        super(Database, self).__init__(**kwargs)
        self.database_name = self.database_name or (self.instance_name.replace("->", '_') + ".db")
        connection, self.cursor = self.open_database(self.database_name, 
                                                     self.text_factory)
        self.wraps(connection)
        try:
            pride.objects["->Python->Finalizer"].add_callback((self.instance_name, "delete"))
        except KeyError:
            self.alert("Unable to queue finalizer callback", level=0)
        
        for table, structure in self.database_structure.items():
            self.create_table(table, structure)
            
    def open_database(self, database_name, text_factory=None):
        """ Opens database_name and obtain a sqlite3 connection and cursor.
            Database objects call this implicitly when initializing.
            Database objects wrap the connection and store the cursor
            as Database.cursor. """
        self.alert("Opening database name: {}".format(database_name),
                   level=self.verbosity["open_database"])
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
        self.alert("Creating table: {}".format(query), 
                   level=self.verbosity["create_table"])        
        result = self.cursor.execute(query)
        self.from_memory[table_name] = {}
        if self.auto_commit:
            self.commit()        
        return result
        
    def query(self, table_name, retrieve_fields=tuple(), where=None):
        """ Retrieves information from the named database table.
            retrieve_fileds is an iterable containing string names of
            the fields that should be returned. The where argument
            is a dictionary of field name:value pairs. """
        primary_key = self.primary_key[table_name]
        if primary_key in (where or {}) and not self.return_cursor:
            try:
                return self.from_memory[table_name][where[primary_key]]
            except KeyError:
                pass
                  
        retrieve_fields = ", ".join(retrieve_fields)
        if where:
            condition_string, values = create_where_string(where)
            query_format = (retrieve_fields, table_name, condition_string)
            query = "SELECT {} FROM {} {}".format(*query_format)
            self.alert("Making query: {}, {}".format(query, values),
                       level=self.verbosity["query_issued"])
            result = self.cursor.execute(query, values)
        else:
            query = "SELECT {} FROM {}".format(retrieve_fields, table_name)
            self.alert("Making query: {}".format(query), 
                       level=self.verbosity["query_issued"])
            result = self.cursor.execute(query)
        self.alert("Retrieved: {}".format(result), 
                   level=self.verbosity["query_result"])
        if self.return_cursor:
            return result
        else:
            result = result.fetchall()
            if result and len(result) == 1:
                result = result[0]
                if len(result) == 1:
                    result = result[0]
            return result
            
    def insert_into(self, table_name, values):
        """ Inserts values into the specified table. The values must
            be the correct type and the correct amount. Value types
            and quantity can be introspected via the table_info method."""
        insert_format = (table_name, 
                         ", ".join('?' for count in range(len(values))))
        query = "INSERT INTO {} VALUES({})".format(*insert_format)
        self.alert("Inserting data into table {}; {}, {}",
                   (table_name, query, values), level=self.verbosity["insert_into"])
        cursor = self.cursor.execute(query, values)
        #primary_key = values[[value for value in values if "primary_key" in value.lower()][0].split()[0]
        #self.from_memory[table_name][primary_key] = values
        if self.auto_commit:
            self.commit()
        return cursor            
    
    def update_table(self, table_name, where=None, arguments=None):
        assert where and arguments
        condition_string, values = create_where_string(where)
        
        _arguments = {}
        primary_key = None
        for item in self.database_structure[table_name]:
            attribute_name = item.split()[0]
            try:
                _arguments[attribute_name] = arguments[attribute_name]
            except KeyError:
                pass
            if "primary_key" in item.lower():
                primary_key = attribute_name
        #arguments = [(item, arguments[item]) for item in self.database_structure[table_name]]
        assignment_string, _values = create_assignment_string(_arguments)
        query = "UPDATE {} SET {} {}".format(table_name, assignment_string, condition_string)
        values = _values + values
        self.alert("Updating data in table {}; {} {}".format(table_name, query, values),
                   level=self.verbosity["update_table"])
        cursor = self.cursor.execute(query, values)
        self.from_memory[table_name][primary_key] = _values
        if self.auto_commit:
            self.commit()
        return cursor
        
    def delete_from(self, table_name, where=None):
        """ Removes an entry from the specified table. The where
            argument is a dictionary containing field name:value pairs."""
        if not where:
            raise ArgumentError("Failed to specify where condition(s) for {}.delete_from".format(self))
        else:
            condition_string, values = create_where_string(where)
            query = "DELETE FROM {} {}".format(table_name, condition_string)   
            self.alert("Deleting entry from table: {}; {}".format(table_name, query),
                       level=self.verbosity["delete_from"])
            cursor = self.cursor.execute(query, values)
            if self.auto_commit:
                self.commit()
            return cursor
                                             
    def drop_table(self, table_name):
        """ Removes a table from the underlying sqlite3 database. Note
            that this will remove all entries in the specified table, and
            the data cannot be recovered."""
        self.alert("Dropping table: {}".format(table_name),
                   level=self.verbosity["drop_table"])
        self.cursor.execute("DROP TABLE {}", (table_name, ))
        if self.auto_commit:
            self.commit()
     
    def alter_table(self, table_name, new_column):
        """ Adds a column to the specified table. """
        self.alert("Altering table: {}".format(table_name), level=0)
        self.cursor.execute("ALTER TABLE {} ADD COLUMN {}".format(table_name, new_column))
        if self.auto_commit:
            self.commit()
        
    def table_info(self, table_name):
        """ Returns a generator which yields field information for the
            specified table. Entries consist of the field index, field name,
            field type, and more."""
        self.alert("Retrieving table information for: {}",
                   (table_name, ), level=self.verbosity["table_info"])
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
        self.close()
        super(Database, self).delete()
        