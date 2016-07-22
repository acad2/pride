pride.site_config
==============

 pride.site_config - site configuration module.

    Site specific defaults, mutable_defaults, flags, and verbosity may be set
    here. Entries take the form of the full name of the object, meaning the
    name of the class, the module the class resides in, and any packages the
    module resides in. Because the '.' symbol denotes attribute access, names
    must have the '.' symbol replaced with '_'. For example:
        
        pride_user_User_defaults = {'username' : 'localhost'}
        
    The above line effectively does the following at runtime, before the class
    is constructed:
    
        pride.user.User.defaults["username"] = "localhost"
        
    This feature is facilitated by the Base metaclass and will work for all
    objects that inherit from Base.
    
    Note that these are the class defaults, meaning that all instances will
    use these values when instantiated (unless the attributes were specified
    explicitly).
    
    For more information on Base objects and default attributes, please see the
    documentation for pride.base.Base 
    
    Temporary customization
    ---------
    The site_config file can be modified temporarily for a single execution via
    command line argument. Simply enter the --site_config flag followed by the
    desired entries, like so:
        
        python -m pride.main --site_config pride_user_User_defaults['username']='Ella'
        
    This will use a different default username for a single execution of the program.
    
    Multiple changes can be made with multiple statements, separated via semicolons:
        
        python -m pride.main --site_config pride_user_User_verbosity['password_verified']=0;pride_user_User_defaults['username']='Ella'            
    

write_to
--------------

**write_to**(entry, **values):

				No documentation available
