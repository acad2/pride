import utilities
import vmlibrary
import defaults
from base import Event

args = dict(defaults.Download)
args.update({"exit_when_finished" : 1})
        
options = utilities.get_options(args, description="File Downloader")
machine = vmlibrary.Machine()
Event("Asynchronous_Network0", "create", "networklibrary.Download", **options).post()

if __name__ == "__main__":
    machine.run()