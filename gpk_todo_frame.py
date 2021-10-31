import tkinter as tk
import pickle
from tkinter import messagebox
from PIL import ImageTk,Image
import datetime
import os
from tkinter import simpledialog


from gpk_utilities import *
from GPK_PROFILE import PROFILE
from GPK_PROFILE import Gpk_ToDoList
from gpkTask import gpk_task
from gpk_Score import score_okr
from gpk_recurrent import gpk_Recurrent

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

class gpk_to_do(tk.Frame):
    def __init__(self,root,geometry,callback  = None,MAIN = None):
        _tk_pop = True
        super().__init__()
        self.root = root
        self.callback = callback
        self.height = geometry['height']
        self.width = geometry['width']
        self.Main = MAIN
        self.Analysis = DF_Analysis(df = self.Main_Profile().todos.todos,
                                    figsize = (12,3))
        self._draw()
        try:
            self.todo_summary()
        except:
            pass
        
    def Main_Profile(self):
        if self.callback is not None:
            return self.callback(Return = True)
        
    def todo_tree_update(self):
        try:
            self.treeview.destroy()
        except:
            pass
        Profile = self.Main_Profile()
        self.treeview = df_to_Treeview(master=self.treeFrame, data = Profile.todos.todos)
        self.treeview.pack(pady = 20, ipady = 120)
        self.treeview.bind("<<TreeviewSelect>>", self.node_select)
        
    def node_select(self,event = None):
        self.tree_index = int(self.treeview.selection()[0]) 
        self.task_info_update() # "Update the Enties of Task info based on tree index"
        
    def set_text_entry(self, text:str):
        self.description_editor.delete('1.0',tk.END)
        self.description_editor.insert(tk.END, text)
    
    def get_text_entry(self) -> str:
        return self.description_editor.get('1.0', 'end').rstrip()
    
    def entry_clear(self):
        if True:
            self.Id_entry.delete(0, 'end')

            self.name_entry.delete(0, 'end')

            self.time_entry.delete(0, 'end')

            self.Dif_entry.delete(0, 'end')
            
            self.deadline_entry.delete(0, 'end')
            
            self.set_text_entry("")
        
    def task_info_update(self):
        "Update the Entry of Task info based on tree index"
        Profile = self.Main_Profile()
        
        self.entry_clear()
        
        ID = Profile.todos.todos['ID'][self.tree_index]
        
        self.Id_entry.insert(tk.END, ID)

        self.name_entry.insert(tk.END, Profile.todos.todos['TaskName'][self.tree_index])

        self.time_entry.insert(tk.END, Profile.todos.todos['Time'][self.tree_index])

        self.Dif_entry.insert(tk.END, Profile.todos.todos['Difficulty'][self.tree_index])
        
        self.deadline_entry.insert(tk.END, str(Profile.todos.todos['Deadline'][self.tree_index]) )
        
        self.set_text_entry(Profile.todos.task_descriptions[ID] )
        
    def If_Valid(self,ID,Name,Time,Diff,Description,ddl,title = "Fail to Create Task"):
        Profile_temp = self.Main_Profile()
        try:
            Reward = Profile_temp.todos.Reward(Time,Diff)
        except Exception as e :
            getattr(messagebox,'showwarning')(title,
                        f"Time and Diff must be numbers of form: 3.4 or 4")
            print(e)
          
            return False
        try:
            gpk_task(name = Name,ID = ID,Reward = Reward,Time = Time,Difficulty = Diff,
                             Description = Description)
        except:
            getattr(messagebox,'showwarning')(title,
                        f"ID must be of form S_G1-1_K3")
          
            return False
        try:
            DATE(ddl)
        except:
            getattr(messagebox,'showwarning')(title,
                        f"Current deadline is {ddl}.\n Please Enter in format 2020-01-01")
          
            return False
        return True

        
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
            print("Task Valid, Creating Task")
            #1.5:Update File
            Profile_temp = self.Main_Profile()
            try:
                Profile_temp.todos.delete("S_G0-0_K0") #In case of creating a new task
            except:
                pass 
            #R_G0-0_K0
            try:
                Profile_temp.todos.delete("R_G0-0_K0") #In case of creating a new RECURSIVE task
            except:
                pass 
            Profile_temp.todos.edit(Name,ID,Time,Diff,Description,ddl)
            if ID[0] == 'R':
                #Add Task to the recursive setting: 
                Reward = Profile_temp.todos.Reward(Time,Diff)
                Gtask = gpk_task(name = Name,ID = ID, 
                                 Time = Time, Reward = Reward, Difficulty = Diff ,Description = Description)
                try:
                    Profile_temp.gpk_Recur.add_gpkTask(Gtask)
                except AttributeError:
                    print("Recursive Task Initializing...")
                    Profile_temp.gpk_Recur = gpk_Recurrent()
                    Profile_temp.gpk_Recur.add_gpkTask(Gtask)
                finally:
                    self.callback(Profile = Profile_temp, Update = True)
                    self.Main.gpk_Recur_frame.Refresh_cb()
                    self.callback(call_frame_name = 'gpk_Recur_frame')
                    
            else:
                self.callback(Profile = Profile_temp, Update = True)
            #2.Reload Tree
            self.todo_tree_update()
            #3.Update Summary
            self.todo_summary()
            
            #4. If applicable, Send the Task to MTK 
            Reward = Profile_temp.todos.Reward(Time,Diff)
            if self.sync_status.get():
                current_project = Profile_temp.todos.PROJECTs[Profile_temp.todos.project_id]
                if  current_project == 'MTK_OKR':
                    Gtask = gpk_task(name = Name,ID = ID,Reward = Reward,Time = Time,Difficulty = Diff,
                                 Description = Description)
                    sec_id = Profile_temp.todos.Get_Sec_ID(Gtask.section) 
                    Profile_temp.todos.Post_task(section_id = sec_id, name = Name, notes = str(Gtask))
                else:
                    getattr(messagebox,'showwarning')("Wrong Project",
                            f"Current Project is {current_project}.\n Please first select (or create) Project MTK_OKR in the Week Panel first.")
                    self.callback(call_frame_name = 'gpk_mtk_frame')
        
    
    def add(self):
        #1.Create a New Task
        Profile_temp = self.Main_Profile()
        Profile_temp.todos.delete("S_G0-0_K0")
        Profile_temp.todos.add(task_name="",task_ID="S_G0-0_K0",task_time=0,task_diff=0 ,task_des="")
        self.callback(Profile = Profile_temp, Update = True)
        #2.Update the Tree Index
        self.todo_tree_update()
        self.tree_index = len(self.treeview.get_children())-1
        self.task_info_update() 
        #5.Update Summary
        self.todo_summary()
        #6.If Syncing, also PUSH it to Meister Task 
        if self.sync_status.get():
            print("Push Task to Meister Task")
            
        
    def delete(self):
        #1.Get ID
        ID = self.Id_entry.get()        
        #2.Fetch Profile
        Profile_temp = self.Main_Profile()
        #3.Delete Task
        Profile_temp.todos.delete(ID)
        self.callback(Profile = Profile_temp, Update = True)
        #4.Update Tree
        self.todo_tree_update()
        #5.Update Summary
        self.todo_summary()
        
        
    def complete(self):
        #1.Get ID
        ID = self.Id_entry.get()
        #2.Fetch Profile
        Profile_temp = self.Main_Profile()
        #2.5: Update Time 
        Time_took = float(simpledialog.askstring("Input", f"How many hours does Task {ID} Took?",
                                parent=self))
        df = Profile_temp.todos.todos 
        idx = df[df['ID'] == ID].index[0]
        df.at[idx,'Time'] = Time_took 
        if not self.If_Valid(ID = ID,
                             Name = df.at[idx,'TaskName'],
                             Time = df.at[idx,'Time'],
                             Diff = df.at[idx,'Difficulty'],
                             Description = Profile_temp.todos.task_descriptions[ID],
                             ddl = df.at[idx,'Deadline'],
                             title= 'ILLEGAL Task, Fail to complete'):
            return 
#1.If In Current Load, Add as Q2 
        if Profile_temp.todos.Load.Task_Find(ID) is not None:
            Quadrant = 2
        else:
            Quadrant = 1
#2.If NOT In Current Load, Add as Q1 
#3. Q3/4 are not recorded here 
        #3.Complete Task
        Profile_temp.todos.complete(ID,Quadrant)
        try:
            Profile_temp.todos.Load.complete(ID,tk_pop = True)
        except Exception as e:
            print(f"\nFail to Update the WeekLog due to:\n{e}")
        
        self.callback(Profile = Profile_temp, Update = True)
        #4.Update Tree
        self.todo_tree_update()
        #5.Update Summary
        self.todo_summary()
        
        
    def todo_summary(self):
        Profile_temp = self.callback(Return = True)
        try:
            score = score_okr(self.callback(Return = True).todos.Load)
        except AttributeError:
            score = 0
        self.summary.set(f"""
                    Total Time:  {sum(Profile_temp.todos.todos['Time'])},\
\tTotal Rewards:  {sum(Profile_temp.todos.todos['Reward'])}\
\tSCORE: {score}
                          """)
        self.CF_refresh()

    def check_mtk_sync_status(self):
        "Check if the program is ready to connect to MTK"
        Profile = self.callback(Return = True)
        if Profile.todos.project_id is None:
            self.sync_status.set(0)
            getattr(messagebox,'showwarning')("No Project Selected",
                                          "Please Go to the 'MTK SYNC' and select [OKR_Plannng]")
        try:
            Profile.todos.info()
        except: 
            getattr(messagebox,'showwarning')("Fail to Connect",
                                          "Internet Failure and Fail to Connect to Meistertask,\n\
                                          please check your internet and try again later...")
            self.sync_status.set(0)

    def mtk_sync(self):
        if self.sync_status.get():
            #Syncing with Meister Task 
            print("Syncing with MTK")
            #0.Fetch Profile 
            Profile_temp = self.Main_Profile()
            #1.Get Data Frame of Today's Plan from MTK methods 
            #try:
            df = Profile_temp.todos.Task_today()
            
            #2.Modify Profile 
            for idx in df.index:
                row = df.loc[idx]
                task = gpk_task(row['name'],row['notes'])
                print(f"Adding Task: \n{task}")
                try:
                    ddl = row['due'].split("T")[0]
                except AttributeError:
                    ddl = 'None'
                Profile_temp.todos.add(task.name,task.ID,float(task.Time),float(task.Difficulty),
                       task.Description,ddl)
            #3.Update Profile
            self.callback(Profile = Profile_temp, Update = True)
            #4.Reload Tree
            self.todo_tree_update()
            #5.Update Summary
            self.todo_summary()
            
        else:
            getattr(messagebox,'showwarning')("Mtk Sync Offline",
                                              "Check the Box on the left to enable it")
                     
    
    ### Canvas Frame Mods                  
    def CF_create(self,master,hc = 2/3, wc = 2/3,side = None):
        "Create a Canvas Frame"
        self.Canvas_height_coef = 1/2 
        self.Canvas_width_coef = 2/3
        self.Canvas_Frame = tk.Frame( master = master, bd = 30 )#, bg = 'green')
        self.Canvas_Frame.configure(height = self.Canvas_height_coef*self.height,
                                  width = self.Canvas_width_coef*self.width)
        self.Canvas_Frame.config(highlightbackground="black" , highlightthickness=2)
        self.Canvas_Frame.pack(side = side)
        
    def CF_refresh(self):
        try:
            self.Canvas_Frame.destroy()
        except AttributeError:
            pass 
        self.CF_create(master= self.summaryFrame, hc = 1/4, wc = 1/2)
        self.CF_draw()
        #Finally:
        self.fig = self.Analysis.get_fig()
        self.canvas = FigureCanvasTkAgg(self.fig,self.Canvas_Frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 0, column = 0)        
            
        
    def CF_draw(self):
        PROFILE = self.Main_Profile()
        self.Analysis.fig.clear()
        try:
            self.Analysis.Plot_Sec(sec = 'Time', df = PROFILE.todos.todos, dim = 131 , title = 'Current Time Distribution')
        except:
            pass 
        try:
            self.Analysis.Plot_Sec(sec = 'Time', df = PROFILE.todos.Archive, dim = 133,title = 'History Time Distribution')
        except:
            pass 
        try:
            self.Analysis.Plot_Score(df = PROFILE.todos.Archive,Loaded = PROFILE.todos.Load_backup,
                                 dim = 132)
        except AttributeError:
            pass 
        
    def IMPORT(self):
        "Fetch Tasks from okr_plan"
        try:
            #1.Check if okr_plan is setup, warn otherwise
            try:
                PROFILE = self.callback(Return = True)
                Plan = PROFILE.okr_plan 
            except AttributeError:
                if getattr(messagebox,'askokcancel()')("Error!OKR Plan Not Set Up",
                f"Would you like to set up the Plan for this week?"):
                    self.callback(call_frame_name  = 'gpk_weekPlanning')
                return     
            #2.Fetch tasks planned today as PUSHLIST
            D = {1:'monday',2:'tuesday',3:'wednesday',4:'thursday',5:'friday',6:'saturday',7:'sunday'}
            wkday = D[weekday_today()]
            self.PUSHLIST = copy.deepcopy(Plan[wkday]) #a List of Gtasks 
    #***2.5 Add Recursive Tasks to PUSHLIST
    #!!!2.6 Check if Profile.Recur is defined: 
            try:
                RECUR = PROFILE.gpk_Recur
                List_recur = Df_to_Gtask(RECUR.task_recur_at(weekday_today()).drop('Recur_At',axis = 1)) 
                self.PUSHLIST = [*self.PUSHLIST, *List_recur]
            except AttributeError: 
                Plan_recur = Fetch_plan_null(PROFILE.todos.Load,'Recursive_Task') 
                self.PUSHLIST = [*self.PUSHLIST, *Plan_recur['Inbox']]
            #3.Identify the tasks in the Archive, remove them from the PUSHLIST
            Analysis = DF_Analysis(PROFILE.todos.Archive)
            #Filter the Special Tasks:
            try:
                IDs_Done = list(Analysis.Last_n_week(1)['ID']) 
                for Gtask in copy.copy(self.PUSHLIST):
                    if Gtask.ID[0] != 'R' and Gtask.ID in IDs_Done:
                        self.PUSHLIST.remove(Gtask)
                        print(f'Task ID {Gtask.ID} removed since recent completion')
                #Filter the Recursive Tasks:
                IDs_Done = list(Analysis.Last_n_day(0)['ID']) #Done Today
                for Gtask in copy.copy(self.PUSHLIST):
                    if Gtask.ID in IDs_Done:
                        self.PUSHLIST.remove(Gtask)
                        print(f'Task ID {Gtask.ID} removed since recent completion')
            except: #When the archive is empty 
                IDs_Done = []               
            #3.5: Identify the tasks in the todolist ,remove them from the PUSHLIST
            try:
                IDs_exist = list(PROFILE.todos.todos['ID'])
                for Gtask in copy.copy(self.PUSHLIST):
                    if Gtask.ID in IDs_exist:
                        self.PUSHLIST.remove(Gtask)
                        print(f'Task ID {Gtask.ID} removed since Existing Task')
            except:#When there is Nothing in the todo
                IDs_exist = [ ] 
            #4.Push all tasks from PUSHLIST into todo list (The method automatically filter same ID) 
            for Gtask in self.PUSHLIST:
                PROFILE.todos.add_gpkTask(Gtask)
            self.callback(PROFILE,Update = True)
            #5.Reload Tree
            self.todo_tree_update()
            #6.Update Summary
            self.todo_summary()
        except Exception as e:
            #Unexpected:
            messagebox.showerror('Import Error', f'Fail to Import due to unknown errors: \n {e}')
        
        #7.If Applicable,Sync with MTK:
        if self.sync_status.get():
            PROFILE = self.callback(Return = True)
            current_project = PROFILE.todos.PROJECTs[PROFILE.todos.project_id]
            if  current_project == 'MTK_OKR':
                for Gtask in self.PUSHLIST:
                    sec_id = PROFILE.todos.Get_Sec_ID(Gtask.section) 
                    print(f"POST Task {Gtask} \nto Section {Gtask.section} with sec_id:{sec_id}")
                    count_down = 3
                    Posted = False
                    while count_down>= 0 and not Posted:
                        try:
                            PROFILE.todos.Post_task(section_id = sec_id, 
                                                    name = Gtask.name, notes = str(Gtask))
                            Posted = True
                        except Exception as e:
                            print(f"Error,Try again in 3 secs.\n Exception:{e}")
                            count_down -= 1
                            sleep(3)
                    if not Posted:
                        getattr(messagebox,'showwarning')("Sync Error",
                        f"Due to internet connection,Sync of Task {Gtask.ID} Failed.\nPlease delete task you wish to sync and [IMPORT] again later.")
            else:
                getattr(messagebox,'showwarning')("Wrong Project",
                        f"Current Project is {current_project}.\n Please first select (or create) Project MTK_OKR in the Week Panel first.")
                self.callback(call_frame_name = 'gpk_mtk_frame')
        #8. If Applicable, Push to Notion:
        if self.sync_status2.get():
            kargs = {"PROFILE":PROFILE,"PUSHLIST":self.PUSHLIST}
            Progress = TkProgress("Importing Tasks",
                                  "Wait for response...",
                                  "Description of Gtasks",
                                  "todo_IMPORT",
                                  kargs)
                
                
    ###Notion Sync Mods
    def check_notion_sync_status(self):
        "Check if Notion is set up for Misc"
        Profile = self.callback(Return = True)
        #1. See if Notion is Created
        try:
            share_link = Profile.Notion.GPKTODO_LinkID
            if share_link[:5] != 'https':
                database_id = share_link
                share_link = None
            else:
                database_id = None
            database_id
            res = Profile.Notion.Get_DataBase(share_link,database_id) 
            print(res)
            if res['object'] == 'error':
                self.sync_status2.set(0)
                tk.messagebox.showerror('GPKTODO fail to set up','1.Make sure token is valid;\n 2. Make sure the GPKTODO-sharelink is correctly set up') 
                self.callback(call_frame_name = 'gpk_notion_frame')
                self.Main.gpk_notion_frame.GPK_Notion_Frame()
        except:
            self.sync_status2.set(0)
            tk.messagebox.showerror('Misc Not Set up','Please set up GPKTODO first') 
            self.callback(call_frame_name = 'gpk_notion_frame')
            self.Main.gpk_notion_frame.GPK_Notion_Frame()
        
    def notion_sync(self):
        "Sync with Notion"
        if self.sync_status2.get():
            #try:
            Profile = self.callback(Return = True)
            share_link = Profile.Notion.GPKTODO_LinkID
            # Profile_Updated = Notion_sync(share_link,
            #                                    Profile,Profile.todos,Misc = False)
            kargs = {"share_link":share_link,"Profile":Profile ,
                     "callback": self.callback , 'Misc':False}
            TkProgress('Syncing With Notion GPKTODO',
                       'Initiatingn Sync',
                       'Description',
                       'Notion_Sync',
                       kargs)
            #Update Profile
            #self.callback(Profile_Updated,Update = True)
            #Refresh 
            self.todo_tree_update()
            self.todo_summary()
            #except:
                #pass  
        else:
            tk.messagebox.showwarning("Notion Sync Offline",
                                      "Check the Box on the left to enable it")
                     
    
            
    
    def _draw(self):
        ###Upper Frame###
        self.FrameUPPER = tk.Frame(master = self, bd = 20 )#, bg = 'Blue')
        self.FrameUPPER.configure(height = self.height/2 ,width = self.width)
        self.FrameUPPER.pack()
        #____Tree View_Frame___
        self.tree_height_coef = 1 
        self.tree_width_coef = 1/2
        self.treeFrame = tk.Frame( master = self.FrameUPPER, bd = 10)# , bg = 'green')
        self.treeFrame.configure(height = self.tree_height_coef*self.height,
                                  width = self.tree_width_coef*self.width)
        self.treeFrame.grid_propagate(0)
        self.treeFrame.pack(side = tk.LEFT, pady = 10,fill = 'y' ,padx = 50)
        #GET Tree#
        self.todo_tree_update()
        #____Editing_Frame___
        self.editingFrame = tk.Frame(master = self.FrameUPPER, bd = 10)# , bg = 'Yellow')
        self.editingFrame.configure(height = 1/2*self.height ,
                                    width = (1-self.tree_width_coef)*self.width)
        self.editingFrame.grid_propagate(0)
        self.editingFrame.pack(side = tk.LEFT)
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
        self.description_editor = tk.Text(self.editingFrame, width=0)
        
        

        base = 1
        self.Id_label.grid(padx = 5, pady = 10, row = base + 0, column = 0)
        self.Id_entry.grid(padx = 5, pady = 10,row = base +0, column = 1 )
        self.name_label.grid(padx = 5, pady = 10,row = base +1, column = 0)
        self.name_entry.grid(padx = 5, pady = 10,row =base + 1, column = 1,ipadx = 100)
        self.time_label .grid(padx = 5, pady = 10,row = base +2, column = 0)
        self.time_entry.grid(padx = 5, pady = 10,row = base +2, column = 1)
        self.Dif_label.grid(padx = 5, pady = 10,row = base +3, column = 0)
        self.Dif_entry.grid(padx = 5, pady = 10,row = base +3, column = 1)
        self.deadline_label.grid(padx = 5, pady = 10,row = base +4, column = 0)
        self.deadline_entry.grid(padx = 5, pady = 10,row = base +4, column = 1)
        
        self.description_editor_label.grid(padx = 5, pady = 15,row = base +5, column = 0)
        self.description_editor.grid(row = base +6, column = 0, columnspan = 3, ipadx=200, pady=5)
            
        ###Lower Frame### (Middle) 
        self.FrameLOWER = tk.Frame(master = self, bd = 2 )#, bg = 'Red')
        self.FrameLOWER.configure(height = self.height/2 ,width = self.width)
        self.FrameLOWER.pack( )
        #____Summary_Frame___
        self.summary = tk.StringVar()
        self.summaryFrame = tk.Frame(master = self.FrameLOWER, bd = 2 )#, bg = 'Orange')
        self.summaryFrame.configure(height = self.height/2 , width = (80/100)*self.width)
        self.summaryFrame.grid_propagate(0)
        self.summaryFrame.pack(side = tk.LEFT)
        self.summary_label = tk.Label(master = self.summaryFrame, textvariable =  self.summary,
                                      font = ('times new roman',14))

        self.summary_label.pack()
        try:
            self.todo_summary()
        except Exception as e:
            print(e) 
        ##Canvas_Frame 
        #self.CF_create(master= self.summaryFrame, hc = 1/4, wc = 1/2)
        
        
        #____Buttons_Frame___
        self.controlFrame = tk.Frame(master = self.FrameLOWER,  bd = 2 )#,bg = 'Purple')
        self.controlFrame.configure(height = self.height/2 ,width = (46/100)*self.width)
        self.controlFrame.grid_propagate(0)
        self.controlFrame.pack(side = tk.LEFT )
        # 
#self.spacer2 = tk.Label(master =self.controlFrame)
        self.spacer = tk.Label(master = self.controlFrame, text = '')
        self.spacer.grid(row = 0,column = 0 , pady = 15, columnspan = 2)
        self.import_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/Import_icon.png"))
        self.Import_btn = tk.Button(self.controlFrame,image = self.import_img)
        self.Import_btn.config(command = self.IMPORT)
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
        #self.spacer2.grid(padx = 160, row =  ,column = 0 )
        
        self.Submit_btn.grid(padx = 20, row = 1, column = 3)
        self.Add_btn.grid(padx = 20,row = 1, column = 2)
        self.Delete_btn.grid(padx = 20,row = 1, column = 1)
        self.Complete_btn.grid(pady = 20, row = 2, column = 1,columnspan = 3)
        self.Import_btn.grid(padx = 20, row = 3, column = 1,columnspan = 3)
        
        #Add Mtk Sync Status 
        self.sync_status = tk.IntVar()
        self.sync_chbx = tk.Checkbutton(self.controlFrame, variable =self.sync_status,
                                        onvalue=1, offvalue=0, command = self.check_mtk_sync_status)
        self.sync_chbx.grid(padx = 20,row = 4, column = 1)
        self.rmchbox_label = tk.Label (self.controlFrame,text = "MTK SYNC")
        self.rmchbox_label.grid(row = 4, column = 2)
        #Add Sync Button 
        self.sync_ref_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.SYNC_btn = tk.Button(master =self.controlFrame, image  =  self.sync_ref_img , 
                                  command = self.mtk_sync)
        self.SYNC_btn.grid(pady = 20, row = 4, column = 3)
        
        #Add Notion Sync Status 
        self.sync_status2 = tk.IntVar()
        self.sync_chbx = tk.Checkbutton(self.controlFrame, variable =self.sync_status2,
                                        onvalue=1, offvalue=0, command = self.check_notion_sync_status)
        self.sync_chbx.grid(padx = 20,row = 5, column = 1)
        self.rmchbox_label = tk.Label (self.controlFrame,text = "NOTION SYNC")
        self.rmchbox_label.grid(row = 5, column = 2)
        #Add Sync Button 
        self.sync_ref_img2 = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.SYNC_btn = tk.Button(master =self.controlFrame, image  =  self.sync_ref_img2 , 
                                  command = self.notion_sync)
        self.SYNC_btn.grid(pady = 0, row = 5, column = 3)
        
        
if __name__ == '__main__':
    root = tk.Tk()
    T = Profile_Test('D:/GPK/gpk_saves/Leo_TEST.gpk')
    #Geom
    base = 100
    width = base*16
    height = base*9
    geometry = {'width':width,'height':height}
    ###
    temp = gpk_to_do(root,geometry ,T.Profile_call_back)
    temp.pack()
    root.mainloop()