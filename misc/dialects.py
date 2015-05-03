import sys
from keyword import kwlist as keywords

DICTIONARY = dict((keyword, keyword) for keyword in keywords)
characters = ['\t', ":", ',', '.', "(", ")", "\n", "#", "=", "+", "-", "*", "&", "%", "!", '[', ']', '{', '}', '"', "'", "\\", '/', "'''", '"""', '<', '>']
for x in xrange(10):
    characters.append(chr(x))
for character in characters:
    DICTIONARY[character] = character
DICTIONARY[""] = ""

for module_name in sys.builtin_module_names:
    DICTIONARY[module_name] = module_name

"""
    dialect = dict((keyword, keyword) for keyword in keywords)

The above programmatically populates a dictionary using CPythons keywords. The
following dictionary would be equivalent:

    dialect = {"and" : "and",
               "as" : "as",
               "assert" : "assert",
               "break" : "break",
               "class" : "class",
               ... and so on

You may redefine any keyword by reassigning it's value in this dictionary.
Some examples:

    dialect["def"] = "define a function", # a more verbose syntax
    dialect["yield"] = "return and continue", # an alternative syntax
    dialect["with"] = "@c#*(&DI9" # an obfuscated syntax
  
Any word in the dictionary can either be modified manually or automatically.
If done automatically, the default mode will not transpose any token names. This can
be changed to produce a random unique per name token name.
"""
    
verbose_dialect = DICTIONARY.copy()
verbose_dialect["and"] = "and"
verbose_dialect["as"] = "But call it"
verbose_dialect["assert"] = "Make sure that"
verbose_dialect["break"] = "Move on from this loop"
verbose_dialect["class"] = "What is a"
verbose_dialect["continue"] = "Handle the next iteration"
verbose_dialect["def"] = "How does it"
verbose_dialect["del"] = "Decrement the reference counter of"
verbose_dialect["elif"] = "If not and"
verbose_dialect["else"] = "If not then"
verbose_dialect["except"] = "So prepare for the exception(s)"
verbose_dialect["exec"] = "Execute"
verbose_dialect["finally"] = "Ensure this happens"
verbose_dialect["for"] = "For each"
verbose_dialect["from"] = "From the idea"
verbose_dialect["global"] = "Using the global value for"
verbose_dialect["if"] = "Supposing that"
verbose_dialect["import"] = "Import the idea of"
verbose_dialect["is"] = "Literally is"
verbose_dialect["lambda"] = "Short instruction"
verbose_dialect["not"] = "not"
verbose_dialect["or"] = "or"
verbose_dialect["pass"] = "Don't worry about it"
verbose_dialect["print"] = "Print to console"
verbose_dialect["raise"] = "Stop because there might be a problem"
verbose_dialect["return"] = "The result is"
verbose_dialect["try"] = "This might not work"
verbose_dialect["while"] = "While"
verbose_dialect["with"] = "In a new context, with"
verbose_dialect["yield"] = "Remember this context for later, lets work on"
#verbose_dialect["#"] = "Sidenote:" # does not work
verbose_dialect["="] = "="
verbose_dialect["!="] = "does not equal"
verbose_dialect[":"] = ":"
verbose_dialect[">="] = "is greater then or equal to"
verbose_dialect[">="] = "is less then or equal to"
verbose_dialect["=="] = "is equal to"