import mpre.base as base

def metapython_main():
    constructor = base.Base()

    options = {"parse_args" : True,
           "exit_when_finished" : True}
    constructor.create("mpre.network2.Download", **options)
           
if __name__ == "__main__":
    metapython_main()
