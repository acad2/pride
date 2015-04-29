import pickle

class DeleteError(ReferenceError):
    meaning = "An attempt was made to delete an object that has already been deleted."

class AddError(ReferenceError):
    meaning = "An attempt was made to add an object that has already been added."
    
class UpdateError(BaseException):
    meaning = "Could not acquire source to reconstruct requested class"
    
class CorruptPickleError(pickle.UnpicklingError):
    meaning = "The message authentication code of this pickle did not match the hash"
    
class ArgumentError(TypeError):
    meaning = "Required argument(s) not supplied"