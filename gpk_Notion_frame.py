import tkinter as tk
from PIL import ImageTk,Image
from tkinter import messagebox
import os
from Plan_load import *
import copy
#gpk mods
from gpk_utilities import *
from GPK_Notion import GPK_Notion

class gpk_notion_frame(tk.Frame):
    def __init__(self,root,call_back = None,MAIN = None):
        super().__init__() 
        self.callback = call_back 
        self.Main = MAIN 
        Profile = self.callback(Return = True)
        #Eventually: 
        self._draw()
        #Try to Fill Entry for token:
        try:
            token = Profile.todos.Load.token
            print(f"set Notion token: {token} ")
            self.token_entry.insert(0, token)
        except AttributeError:
            token = None 
        #Consider Initialize Profile with GPK_Notion
        try:
            GPKTODO_LinkID = Profile.Notion.GPKTODO_LinkID
            MISC_LinkID = Profile.Notion.MISC_LinkID
        except:
            Profile.Notion = GPK_Notion(token,None)
            self.callback(Profile,Update = True)
                
    def SAVE(self,New_Load = False):
        Profile = self.callback(Return = True)
        #Fetch Info From Entries 
        token = self.token_entry.get()
        link  = self.Link_entry.get()
        if New_Load:
            Profile.todos.Load = Load_Notion(token = token, share_link = link)
        try:
            Profile.todos.Load.token = str(token)
            Profile.Notion.token = str(self.token_entry_notionapi.get())
            print(f'Setting Token to: {token}')
        except:
            pass 
        try:
            GPKTODO_LinkID = self.GPK_db_link_entry.get()
            MISC_LinkID = self.misc_db_link_entry.get()
            Profile.Notion.GPKTODO_LinkID = GPKTODO_LinkID
            Profile.Notion.MISC_LinkID = MISC_LinkID
        except:
            print('GPKTODO_LinkID or MISC_LinkID Fail to Save')
            pass 
        #Update Profile 
        self.callback(Profile,Update = True) 
    
    def IMPORT(self):
        #Fetch Info From Entries 
        link  = self.Link_entry.get()
        if link == "":
            messagebox.showerror('Enter ShareLink for <WeekLog> Import',
                                 'Please first Get the GPKLOG share link of a <OKRLOG> from Notion')
        else:
            #Fetch Profile
            Profile = self.callback(Return = True)
            #Update Load 
            try:
                Load = Profile.todos.Load 
            except AttributeError:  
                self.SAVE(New_Load = True)
                Profile = self.callback(Return = True)
                Load = Profile.todos.Load 
            Load.set_token(self.token_entry.get())
            Load.set_link(link)
            Load.Notion_Load_WeekObjective(link)
            Profile.todos.Load_backup = copy.copy(Load)
            if Plan_Legit(Load):
                #Update Profile 
                self.callback(Profile,Update = True)
                #Update WeekView Frames Before Taking to it
                self.Main.gpk_weekView.REFRESH()
                self.Main.gpk_weekPlanning.REFRESH()
                #Re_init the Recur setting frame
                self.Main.gpk_Recur_frame.Ref(True,True)
                #Finally:
                self.callback(call_frame_name = 'gpk_weekView')
            else:
                Warning =  print_collector(lambda : Plan_Legit(Load))
                messagebox.showwarning('Import Error',Warning)
                
    #GPK Notion Settings
    def Create_db(self,Misc = False):
        #1.Fetch Parent Share link
        parent_link =  tk.simpledialog.askstring(title = 'Which Page do you want the database to be created under?',
                                                 prompt = 'Paste the <Share_link> of the parent page')
        print('Trying to Create database under:\n',parent_link)
        #2.Try to create DB
        Profile = self.callback(Return = True)
        if Misc: 
            res = Profile.Notion.Post_MiscDB(parent_link)
        else:#GPK_todo
            res = Profile.Notion.Post_DataBase(parent_link)
        #3.Give Feedback and update Entry.
        try:
            Id = res['id']
            print(f'Database succesfully created with id: {Id}')
            if Misc:
                self.misc_db_link_entry.delete(0, tk.END)
                self.misc_db_link_entry.insert(0, Id)
            else:
                self.GPK_db_link_entry.delete(0, tk.END)
                self.GPK_db_link_entry.insert(0, Id)
            self.SAVE()
            tk.messagebox.showinfo('Success', f'{"Misc Database" if Misc else "GPKTODO Database"} Created')
        except:
            tk.messagebox.showerror('Error', 
                                    f'Fail to Create {"Misc Database" if Misc else "GPKTODO Database"}')
            
        
        
    
    def GPK_Notion_Frame(self):
        Profile = self.callback(Return = True)
        ###
        new_window = tk.Toplevel()
        base = 40
        new_window.geometry(f'{16*base}x{9*base}')
        #Token Entry
        Lab = tk.Label(new_window,text = 'Enter Internal Integration Token')
        Lab.pack()
        self.token_entry_notionapi = tk.Entry(new_window,font = ('times new roman',10),
                                    width = 100)
        self.token_entry_notionapi.delete(0, tk.END)
        self.token_entry_notionapi.insert(0, Profile.Notion.token)
        self.token_entry_notionapi.pack(padx = 10, pady = 5)
        #GPK_Todo_Database Link
        Lab = tk.Label(new_window,text = 'Enter ShareLink (or ID) for <OKR TODO> Data Base')
        Lab.pack()
        self.GPK_db_link_entry = tk.Entry(new_window,font = ('times new roman',10),
                                    width = 100)
        self.GPK_db_link_entry.pack(padx = 10,pady = 5)
        ## Create GPKTODO-DataBase Button
        self.GPK_db_C_btn = tk.Button(new_window,text = 'Create <OKR TODO> Data Base',
                                      font = ('times new roman',14))
        self.GPK_db_C_btn.config(command = lambda: self.Create_db(Misc = False))
        self.GPK_db_C_btn.pack(padx = 10,pady = 10)
        #Misc Todo Database Link     
        Lab = tk.Label(new_window,text = 'Enter ShareLink (or ID) for <OKR MISC> Data Base')
        Lab.pack()
        self.misc_db_link_entry = tk.Entry(new_window,font = ('times new roman',10),
                                    width = 100)
        self.misc_db_link_entry.pack(padx = 10,pady = 5)
        ## Create MISC-DataBase Button
        self.Misc_db_C_btn = tk.Button(new_window,
                                       text = 'Create <MISC> Data Base',font = ('times new roman',14))
        self.Misc_db_C_btn.config(command  = lambda: self.Create_db(Misc = True))
        self.Misc_db_C_btn.pack(padx = 10,pady = 10)
        ##Save Btn
        Save_btn = tk.Button(new_window,image  = self.save_img)
        Save_btn.pack(padx = 10,pady = 5)
        Save_btn.config(command = self.SAVE)
        
        ###Insert:
        try:
            self.GPK_db_link_entry.insert(0, Profile.Notion.GPKTODO_LinkID)
        except:
            print('<GPK_db_link_entry> Fail to Load')
        try:
            self.misc_db_link_entry.insert(0, Profile.Notion.MISC_LinkID)
        except:
            print('<misc_db_link_entry> Fail to Load')
        
    def _draw(self):
        #Label:
        self.Notion_img = Image.open(os.getcwd() + '/Pictures/Notion.png')
        # self.Notion_img = self.Notion_img.resize((1000,500), Image.ANTIALIAS)
        self.Notion_img = ImageTk.PhotoImage(self.Notion_img)
        self.Lab = tk.Label(self,image = self.Notion_img)
        self.Lab.pack()
        #Token Entry
        Lab = tk.Label(self,text = 'Enter Internal Integration Token')
        Lab.pack()
        self.token_entry = tk.Entry(self,font = ('times new roman',10),
                                    width = 100)
        self.token_entry.pack(padx = 10,pady = 5)
        #ShareLink
        Lab = tk.Label(self,text = 'Enter ShareLink for <WeekLog> Import')
        Lab.pack()
        self.Link_entry = tk.Entry(self,font = ('times new roman',10),
                                   width = 100)
        self.Link_entry.pack(padx = 10,pady = 5)
        #Save Button
        self.save_img = Image.open(os.getcwd() + '/Pictures/Save_btn.png')
        self.save_img = ImageTk.PhotoImage(self.save_img)
        self.Save_btn = tk.Button(self,image  = self.save_img)
        self.Save_btn.pack(padx = 10,pady = 5)
        self.Save_btn.config(command = self.SAVE)
        #OKRLOG IMPORT Button 
        self.Import_img = Image.open(os.getcwd() + '/Pictures/Import_icon.png')
        self.Import_img = ImageTk.PhotoImage(self.Import_img)
        self.Import_btn = tk.Button(self,image = self.Import_img)
        self.Import_btn.pack(padx = 10,pady = 5)
        self.Import_btn.config(command = self.IMPORT)
        #Advanced Setting Button
        self.Setting_img =  Image.open(os.getcwd() + '/Pictures/Setting.png')
        self.Setting_img = self.Setting_img.resize((100,100), Image.ANTIALIAS)
        self.Setting_img = ImageTk.PhotoImage(self.Setting_img)
        self.Setting_btn = tk.Button(self,image = self.Setting_img)
        self.Setting_btn.pack(padx = 10,pady = 5)
        self.Setting_btn.config(command = self.GPK_Notion_Frame)
          
