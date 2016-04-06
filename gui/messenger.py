import getpass

import pride.gui.gui
import pride.datatransfer

class Client(pride.datatransfer.Data_Transfer_Client):
    
    pass
            
              
class Popup_Menu(pride.gui.gui.Window):
                
    defaults = {"pack_mode" : "popup_menu"}
    
    
class Add_Contact_Button(pride.gui.gui.Button):     

    defaults = {"text" : "add contact..."}
    
    def left_click(self, mouse):
        self.parent_application.create(Popup_Menu)
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
        self.application_window.create(Contacts, pack_mode="left")
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
        