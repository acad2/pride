
class SecurityError(Exception): pass
class InvalidPassword(SecurityError): pass
class InvalidSignature(SecurityError): pass
class InvalidTag(SecurityError): pass
    
class UnauthorizedError(SecurityError): 
    meaning = "An attempt was made to access a resource with improper credentials"

class DeleteError(ReferenceError):
    meaning = "An attempt was made to delete an object that has already been deleted."

class AddError(ReferenceError):
    meaning = "An attempt was made to add an object that has already been added."
    
class UpdateError(BaseException):
    meaning = "Could not acquire source to reconstruct requested class"
    
class ArgumentError(TypeError):
    meaning = "Required argument(s) not supplied"
    
    
 