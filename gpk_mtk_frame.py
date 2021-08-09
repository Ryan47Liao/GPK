import tkinter as tk
import pickle
import GPK_PROFILE 
import pandas as pd
from PIL import ImageTk,Image
import os
from gpk_utilities import *

class Profile_Test:
    def __init__(self,path = None, name = None):
        if path is not None:
            self.file_path = path
            INfile = open( self.file_path ,"rb")
            self.Profile = pickle.load(INfile)
            INfile.close()
        else:
            self.Profile = GPK_PROFILE.PROFILE(name,321890)
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
    

class gpk_mtk_frame(tk.Frame):
    def __init__(self,root,call_back=None):
        super().__init__()
        self.root = root
        
        if call_back is not None:
            self.call_back = call_back 
            self.Profile = self.call_back(Return = True)
        else:
            def PASS(*args,**kargs):
                return 
            self.call_back = PASS
            self.Profile  = None 
        self._draw()
        
    def update_token(self):
        self.get_token()
        self.Key_entry.delete(0,tk.END)
        self.Key_entry.insert(0,str(self.token) )
        
    def get_token(self):
        self.Profile = self.call_back(Return = True)
        try:
            self.token = self.Profile.todos.get_token()
        except AttributeError as e:
            print("Token not found at the current profile")
            print(e)
    
    def set_token(self,token):
        self.Profile = self.call_back(Return = True)
        self.token = token 
        self.Profile.todos.set_token(token) 
        self.call_back(Profile = self.Profile,Update = True)
        
        
    def project_df(self):
        Profile = self.call_back(Return = True)
        TEST = Profile.todos 
        try:
            TEST.Get_info()
            return pd.DataFrame({'Project Name':list(TEST.PROJECTs.values()),
                          'Project ID':list(TEST.PROJECTs.keys())})
        except Exception as e:
            print(e)
            return pd.DataFrame({'Project Name':list( ),
                          'Project ID':list( )})
    
    def tree_update(self):
        try:
            self.treeview.destroy()
        except:
            pass 
        Profile = self.call_back(Return = True)
        self.treeview = df_to_Treeview(master=self, data = self.project_df())
        self.treeview.pack(pady = 20)
        self.treeview.bind("<<TreeviewSelect>>", self.node_select)
    
    def node_select(self,event = None):
        self.tree_index = int(self.treeview.selection()[0]) 
        self.update_project() # "Update the Current Project ID"
        
    def update_project(self):
        Profile = self.call_back(Return = True)
        ID = list(Profile.todos.PROJECTs.keys())[self.tree_index]
        print(f"ID {ID} selected.")
        Profile.todos.set_project_id(ID)
        Profile.todos.info()
        self.call_back(Profile,Update = True)
        
    def _draw(self):
        #Welcome Pic
        #MeisterTask.png
        self.MeisterTask_img = Image.open(os.getcwd() + '/Pictures/MeisterTask.png')
        self.MeisterTask_img = ImageTk.PhotoImage(self.MeisterTask_img)
        self.Lab = tk.Label(self,image = self.MeisterTask_img)
        self.Lab.pack()
        #Token Set Up
        self.Key_label = tk.Label(master = self,text = 'Personal access tokens:')
        self.Key_entry = tk.Entry(master = self)
        self.submit_btn = tk.Button(master = self, text = 'Save', 
                               command = lambda: self.set_token(self.Key_entry.get()) )
        #Project SetUp
        self.treeview = df_to_Treeview(master=self, data = pd.DataFrame({'Project Name':[],
                                                                         'Project ID':[]}))
        self.treeview.pack(pady = 20)
        self.treeview.bind("<<TreeviewSelect>>", self.node_select)
        #Packing...
        self.Key_label.pack()
        self.Key_entry.pack()
        self.submit_btn.pack()
        #Refresh Btn 
        self.sync_ref_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.SYNC_btn = tk.Button(master =self, image  =  self.sync_ref_img , 
                                  command = self.tree_update)
        self.SYNC_btn.pack()
        try:
            self.update_token()
        except AttributeError:
            pass 
        #Create GPK_MTK Project 
        self.gm_create_btn = tk.Button(master = self, text = 'Create MTK_OKR')
        self.gm_create_btn.config(command = self.Profile.todos.RESET)
        self.gm_create_btn.pack()
        #Create OKR_Planning Project
        self.op_create_btn = tk.Button(master = self, text = 'Create OKR_Planning')
        self.gm_create_btn.config(command = self.Profile.todos.Planner_SetUp)
        self.op_create_btn.pack()
    
if __name__ == '__main__':
    root = tk.Tk()
    T = Profile_Test(path = 'D:/GPK/gpk_saves/Ryan_TEST.gpk')#D:/GPK/gpk_saves/
    temp = gpk_mtk_frame(root,T.Profile_call_back)
    temp.pack()
    root.mainloop()