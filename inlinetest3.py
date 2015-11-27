import pride

class Test(object):
    @pride.preprocess
    def inline_me():
        return """x = 1
        y = 2
        z = 3
        a = 'idek'"""
        