import getpass

import pride.gui.gui
import pride.datatransfer

class Client(pride.datatransfer.Data_Transfer_Client):
    
    def receive(self, messages):
        for sender, message in messages:
            self.parent.receive_message(sender, message)            
            
             
class Contact_Button(pride.gui.gui.Button): 

    def left_click(self, mouse):    
        self.parent_application.current_contact = self.text
        
    
class Popup_Menu(pride.gui.gui.Window):
                
    defaults = {"pack_mode" : "popup_menu", "background_color" : (125, 125, 125, 255),
                "h_range" : (0, 300), "w_range" : (0, 400)}
    
    def __init__(self, **kwargs):
        super(Popup_Menu, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Dialog_Box", text=self.text,
                    callback=(self.reference, "handle_input"))
        
    def handle_input(self, text):
        self.parent_application.contacts.create(Contact_Button, text=text)
        self.delete()
        
        
class Add_Contact_Button(pride.gui.gui.Button):     

    defaults = {"text" : "add contact..."}
    
    def left_click(self, mouse):
        self.parent_application.create(Popup_Menu, text="Enter the contacts username: ")
        self.parent_application.pack()
        
         
class Contacts(pride.gui.gui.Window):
                
    def __init__(self, **kwargs):
        super(Contacts, self).__init__(**kwargs)
        self.create(Add_Contact_Button)        
        
        
class Messenger(pride.gui.gui.Application):
    
    defaults = {"password_prompt" : "{}: Please enter the password: ", "password" : '',
                "current_contact" : ''}
    
    def __init__(self, **kwargs):
        super(Messenger, self).__init__(**kwargs)
        self.contacts = self.application_window.create(Contacts, pack_mode="left")
        self.application_window.create("pride.gui.widgetlibrary.Dialog_Box", pack_mode="right",
                                       callback=(self.reference, "send_message"))        
        self.client = self.create(Client, username=self.username, 
                                  password=self.password or 
                                           getpass.getpass(self.password_prompt.format(self.reference)))
        self.children.remove(self.client)
        
        self.current_contact = self.username
        
    def send_message(self, message):
        assert self.current_contact
        self.client.send_to(self.current_contact, message)
        self.application_window.objects["Dialog_Box"][0].objects["Text_Box"][0].text += "\n" + message
        
    def receive_message(self, sender, message):
        self.alert("{}: {}".format(sender, message), level=self.verbosity.get(sender, 0))
        