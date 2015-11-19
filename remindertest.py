import time

import pride
import pride.shell
import pride.base
import pride.utilities

def date_to_epoch(time_string):
    return time.mktime(time.strptime(time_string))

class Reminder(Program):
    
    def select_date(self):
        
        
    def handle_input(self, input):
        when, message = 
        now = time.time()
        pride.Instruction(self.instance_name, "alert", 
                          message).execute(priority=date_to_epoch(when) - now)
        print "Added reminder: ", date_to_epoch(when), now, date_to_epoch(when) - now
                    
if __name__ == "__main__":
    when = "Wed Nov 18 12:29:00 2015"
    reminder = Reminder()
    reminder.add_reminder(when, "hi")