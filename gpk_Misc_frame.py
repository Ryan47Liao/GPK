import tkinter as tk
import pickle
from tkinter import messagebox
from PIL import ImageTk,Image
import datetime
import os
from tkinter import simpledialog
import random


from gpk_utilities import *
from GPK_PROFILE import PROFILE,Gpk_ToDoList,GPk_Notion_todoList
from gpkTask import gpk_task
from gpk_Score import score_okr
from gpk_recurrent import gpk_Recurrent
from gpk_todo_frame import gpk_to_do

from tkProgress import TkProgress #2021/8/2

class Profile_Test:
    def __init__(self,path = None, name = None):
        if path is not None:
            self.file_path = path
            INfile = open( self.file_path ,"rb")
            self.Profile = pickle.load(INfile)
            INfile.close()
        else:
            self.Profile = PROFILE(name,321890)
            self.file_path = f'D:/GPK/gpk_saves/{name}_TEST.gpk'
            self.Profile.Save(self.file_path)
        
    def profile_save(self):
        self.Profile.Save(self.file_path)
        
    def Profile_call_back(self,Profile = None, Update = False, Return = False):
            """
            Interact with subFrames and modify the Profile in the Main APP.
            Toggle Return to Get Profile 
            input Profile and Toggle update to update Profile
            """
            if Update:
                self.Profile = Profile #Update the Profile
                self.profile_save()
            elif Return:
                return self.Profile 
            else:
                pass


class gpk_misc(gpk_to_do):
    def __init__(self,root,geometry,callback  = None,MAIN = None):
        _tk_pop = True
        self.callback = callback
        PROFILE = self.Main_Profile()
        if 'Q3_todo' not in dir(PROFILE):
            PROFILE.Q3_todo = GPk_Notion_todoList()
        self.callback(PROFILE,Update = True)
        gpk_to_do.__init__(self,root,geometry,callback,MAIN)
        
    ###
    #Instead of <Profile.Q3_todo.todo>, use <Profile.Q3_todo> instead
    #Redefine The following functions:
        #0.TreeView Update
        
    def todo_tree_update(self):
        try:
            self.treeview.destroy()
        except:
            pass
        Profile = self.Main_Profile()
        self.treeview = df_to_Treeview(master=self.treeFrame, data = Profile.Q3_todo.todos)
        self.treeview.pack(pady = 20, ipady = 120)
        self.treeview.bind("<<TreeviewSelect>>", self.node_select)
    
    #1.Add
    def add(self):
        #1.Create a New Task
        Profile_temp = self.Main_Profile()
        self.last_ID = f"S_G0-{random.randint(0,99)}_K{random.randint(0,99)}"
        Profile_temp.Q3_todo.delete(self.last_ID)
        Profile_temp.Q3_todo.add(task_name="",task_ID= self.last_ID ,task_time=0,task_diff=0 
                                 ,task_des="", ddl = str(datetime.datetime.now().date()) )
        self.callback(Profile = Profile_temp, Update = True)
        #2.Update the Tree Index
        self.todo_tree_update()
        self.tree_index = len(self.treeview.get_children())-1
        self.task_info_update() 
        #5.Update Summary
        self.todo_summary()
        #6.If Syncing, also PUSH it to NOTION Task 
        if self.sync_status.get():
            print("Push Task to NOTION")
    #2.Delete
    def delete(self):
        #1.Get ID
        ID = self.Id_entry.get()        
        #2.Fetch Profile
        Profile_temp = self.Main_Profile()
        #3.Delete Task
        Profile_temp.Q3_todo.delete(ID)
        self.callback(Profile = Profile_temp, Update = True)
        #4.Update Tree
        self.todo_tree_update()
        #5.Update Summary
        self.todo_summary()
    #3.Submit
    def submit(self):
        #1.Save file
        ID = self.Id_entry.get()
        Name =  self.name_entry.get()
        Time = float(self.time_entry.get())
        Diff = float(self.Dif_entry.get())
        try:
            ddl  = str(DATE(self.deadline_entry.get()))
        except:
            messagebox.showerror('Wrong Date format', 
                                 f'deadline {self.deadline_entry.get()} was of wrong format,must be: yyyy-mm-dd')
            return
        Description = self.get_text_entry()
        if self.If_Valid(ID,Name,Time,Diff,Description,ddl):
            print(f"Task Valid, Creating Task {ID}")
            #1.5:Update File
            Profile_temp = self.Main_Profile()
            try:
                Profile_temp.Q3_todo.delete(self.last_ID) #In case of creating a new task
            except:
                pass 
            Profile_temp.Q3_todo.edit(Name,ID,Time,Diff,Description,ddl)
            Profile_temp.Q3_todo.task_descriptions[ID] = Description
            #Finally:
            self.callback(Profile_temp,Update = True)
        #2.Reload Tree
        self.todo_tree_update()
            
    #4.Complete
    def complete(self):
        #1.Get ID
        ID = self.Id_entry.get()
        #2.Fetch Profile
        Profile_temp = self.Main_Profile()
        #2.5: Update Time 
        Time_took = float(simpledialog.askstring("Input", f"How many hours does Task {ID} Took?",
                                parent=self))
        df = Profile_temp.Q3_todo.todos 
        idx = df[df['ID'] == ID].index[0]
        df.at[idx,'Time'] = Time_took
        #3.Complete Task
        Profile_temp.Q3_todo.complete(ID,Quadrant = 3)
        self.callback(Profile = Profile_temp, Update = True)
        #4.Update Tree
        self.todo_tree_update()
        #5.Update Summary
        self.todo_summary()
    #5.Check 
    #6.Sync 
    
    #OTHER
    def task_info_update(self):
        "Update the Entry of Task info based on tree index"
        Profile = self.Main_Profile()
        
        self.entry_clear()
        
        ID = Profile.Q3_todo.todos['ID'][self.tree_index]
        
        self.Id_entry.insert(tk.END, ID)

        self.name_entry.insert(tk.END, Profile.Q3_todo.todos['TaskName'][self.tree_index])

        self.time_entry.insert(tk.END, Profile.Q3_todo.todos['Time'][self.tree_index])

        self.Dif_entry.insert(tk.END, Profile.Q3_todo.todos['Difficulty'][self.tree_index])
        
        self.deadline_entry.insert(tk.END, str(Profile.Q3_todo.todos['Deadline'][self.tree_index]) )
        
        self.set_text_entry(Profile.Q3_todo.task_descriptions[ID] )
        
    def todo_summary(self):
        pass     
    
    def CF_refresh(self):
        pass 
    ###Notion Sync
    def check_notion_sync_status(self):
        "Check if Notion is set up for Misc"
        Profile = self.callback(Return = True)
        #1. See if Notion is Created
        try:
            share_link = Profile.Notion.MISC_LinkID
            if share_link[:5] != 'https':
                database_id = share_link
                share_link = None
            else:
                database_id = None
            database_id
            res = Profile.Notion.Get_DataBase(share_link,database_id) 
            print(res)
            if res['object'] != 'database':
                self.sync_status.set(0)
                tk.messagebox.showerror('Misc fail to set up','1.Make sure token is valid;\n 2. Make sure the misc-sharelink is correctly set up') 
                self.callback(call_frame_name = 'gpk_notion_frame')
                self.Main.gpk_notion_frame.GPK_Notion_Frame()
        except:
            self.sync_status.set(0)
            tk.messagebox.showerror('Misc Not Set up','Please set up Notion API first') 
            self.callback(call_frame_name = 'gpk_notion_frame')
            self.Main.gpk_notion_frame.GPK_Notion_Frame()
        
    def notion_sync(self):
        "Sync with Notion"
        if self.sync_status.get():
            Profile = self.callback(Return = True)
            share_link = Profile.Notion.MISC_LinkID
            kargs = {"share_link":share_link,"Profile":Profile ,
                 "callback": self.callback , 'Misc':True}
            TkProgress('Syncing With Notion Misc',
                       'Initiatingn Sync',
                       'Description',
                       'Notion_Sync',
                       kargs)
            #Refresh 
            self.todo_tree_update()
        else:
            tk.messagebox.showwarning("Notion Sync Offline",
                                              "Check the Box on the left to enable it")
                     
    
    def _draw(self):
        ###Upper Frame###
        self.FrameUPPER = tk.Frame(master = self, bd = 0 )#, bg = 'Blue')
        self.FrameUPPER.configure(height = self.height/2 ,width = self.width)
        self.FrameUPPER.pack()
        #____Tree View_Frame___
        self.tree_height_coef = 1 
        self.tree_width_coef = 1/2
        self.treeFrame = tk.Frame( master = self.FrameUPPER, bd = 10)# , bg = 'green')
        self.treeFrame.configure(height = self.tree_height_coef*self.height,
                                  width = self.tree_width_coef*self.width)
        self.treeFrame.grid_propagate(0)
        self.treeFrame.pack(side = tk.LEFT, pady = 0,fill = 'y' ,padx = 50)
        #GET Tree#
        self.todo_tree_update()
            
        ###Lower Frame### (Middle) 
        self.FrameLOWER = tk.Frame(master = self, bd = 2 )#, bg = 'Red')
        self.FrameLOWER.configure(height = self.height/2 ,width = self.width)
        self.FrameLOWER.pack( )        
        
        #____Editing_Frame___
        self.editingFrame = tk.Frame(master = self.FrameLOWER, bd = 10)# , bg = 'Yellow')
        self.editingFrame.configure(height = 1/2*self.height ,
                                    width = (1-self.tree_width_coef)*self.width)
        self.editingFrame.grid_propagate(0)
        self.editingFrame.pack(side = tk.LEFT)#side = tk.LEFT
        #
        self.Id_label = tk.Label(master = self.editingFrame, text = 'Task-ID:')
        self.Id_entry = tk.Entry(master = self.editingFrame )
        
        self.name_label = tk.Label(master = self.editingFrame, text = 'Task-Name:')
        self.name_entry = tk.Entry(master = self.editingFrame )
        
        self.time_label = tk.Label(master = self.editingFrame, text = 'Time in Hours:')
        self.time_entry = tk.Entry(master = self.editingFrame )
        
        self.Dif_label = tk.Label(master = self.editingFrame, text = 'Difficulty 1 to 10:')
        self.Dif_entry = tk.Entry(master = self.editingFrame )
        
        self.deadline_label = tk.Label(master = self.editingFrame, text = 'Deadline:')
        self.deadline_entry = tk.Entry(self.editingFrame)
        
        self.description_editor_label =  tk.Label(master = self.editingFrame, text = 'Description:')
        self.description_editor = tk.Text(self.editingFrame,height = 15, width = 60)
        
        
        ##Spacer
        self.spacer = tk.Label(master = self.editingFrame, text = '')
        self.spacer.grid(row = 0,column = 0 , padx = 200)
        ##
        base = 1
        self.Id_label.grid(padx = 5, pady = 10, row = base + 0, column = 1)
        self.Id_entry.grid(padx = 5, pady = 10,row = base +0, column = 2 )
        self.name_label.grid(padx = 5, pady = 10,row = base +1, column = 1)
        self.name_entry.grid(padx = 5, pady = 10,row =base + 1, column = 2,ipadx = 30)
        self.time_label .grid(padx = 5, pady = 10,row = base +2, column = 1)
        self.time_entry.grid(padx = 5, pady = 10,row = base +2, column = 2)
        self.Dif_label.grid(padx = 5, pady = 10,row = base +3, column = 1)
        self.Dif_entry.grid(padx = 5, pady = 10,row = base +3, column = 2)
        #self.deadline_label.grid(padx = 5, pady = 10,row = base +4, column = 1)
        #self.deadline_entry.grid(padx = 5, pady = 10,row = base +4, column = 2)
        
        self.description_editor_label.grid(padx = 5, pady = 15,row = base +5, column = 1)
        self.description_editor.grid(row = base +6, column = 1, columnspan = 3)
        #____Buttons_Frame___
        self.controlFrame = tk.Frame(master = self.FrameLOWER,  bd = 2 )#,bg = 'Purple')
        self.controlFrame.configure(height = self.height/2 ,width = (46/100)*self.width)
        self.controlFrame.grid_propagate(0)
        self.controlFrame.pack(side = tk.LEFT )#side = tk.LEFT 
        # 
        self.spacer2 = tk.Label(master = self.controlFrame, text = '')
        self.spacer2.grid(row = 0,column = 0 , padx = 60 ,pady = 60 )
    
        ###
        self.img_submit = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sumbit_icon_p8d_icon.ico"))
        self.Submit_btn = tk.Button(bd = 2, master =self.controlFrame, image =  self.img_submit, command = self.submit)
        self.img_add = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/add_task_GGR_icon.ico"))
        self.Add_btn = tk.Button(master =self.controlFrame, image = self.img_add, command = self.add)
        self.img_del = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/delete_task_li6_icon.ico"))
        self.Delete_btn = tk.Button(master =self.controlFrame, image = self.img_del, command = self.delete)
        self.img_complete = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/task_complete.png"))
        self.Complete_btn = tk.Button(master =self.controlFrame, image  =  self.img_complete , command = self.complete)
        #Set Location for the buttons         
        self.Submit_btn.grid(padx = 20, row = 1, column = 3)
        self.Add_btn.grid(padx = 20,row = 1, column = 2)
        self.Delete_btn.grid(padx = 20,row = 1, column = 1)
        self.Complete_btn.grid(pady = 20, row = 2, column = 1,columnspan = 3)
        
        #Add Notion Sync Status 
        self.sync_status = tk.IntVar()
        self.sync_chbx = tk.Checkbutton(self.controlFrame, variable =self.sync_status,
                                        onvalue=1, offvalue=0, command = self.check_notion_sync_status)
        self.sync_chbx.grid(padx = 20,row = 4, column = 1)
        self.rmchbox_label = tk.Label (self.controlFrame,text = "NOTION SYNC")
        self.rmchbox_label.grid(row = 4, column = 2)
        #Add Sync Button 
        self.sync_ref_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.SYNC_btn = tk.Button(master =self.controlFrame, image  =  self.sync_ref_img , 
                                  command = self.notion_sync)
        self.SYNC_btn.grid(pady = 20, row = 4, column = 3)
        
        
if __name__ == '__main__':
    root = tk.Tk()
    T = Profile_Test('D:/GPK/gpk_saves/Leo_TEST.gpk')
    #Geom
    base = 100
    width = base*16
    height = base*9
    geometry = {'width':width,'height':height}
    ###
    temp = gpk_misc(root,geometry ,T.Profile_call_back)
    temp.pack()
    root.mainloop()