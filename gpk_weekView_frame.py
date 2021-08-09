from gpk_utilities import *
import tkinter as tk
from tkinter import ttk,messagebox
import pandas as pd
from PIL import ImageTk,Image
import os
from tkinter import messagebox
from time import sleep

from gpkTask import gpk_task
from tkList import tkLIST 
from gpk_recurrent import gpk_Recur_frame
from gpk_Report import gpk_Report

#New:
from gpk_D_Reflection_frame import *

class gpk_weekView(tk.Frame):
    def __init__(self,root,geometry,callback  = None,Main = None):
        super().__init__()
        self.root = root
        self.callback = callback
        self.height = geometry['height']
        self.width = geometry['width']
        self.MAIN = Main
        PROFILE = self.callback(Return = True)
        try:
            df = OKRLOG_to_df(PROFILE.todos.Load.WeekObjective) 
        except:
            df = pd.DataFrame()
        self.Analysis = DF_Analysis(df,(3,6))
        self._draw()
    
    def CF_create(self,master,hc = 2/3, wc = 2/5,side = None):
        "Create a Canvas Frame"
        self.Canvas_height_coef = 1/2 
        self.Canvas_width_coef = 2/3
        self.Canvas_Frame = tk.Frame( master = master, bd = 30 )##, bg = 'green')
        self.Canvas_Frame.configure(height = self.Canvas_height_coef*self.height,
                                  width = self.Canvas_width_coef*self.width)
        self.Canvas_Frame.config(highlightbackground="black" , highlightthickness=2)
        self.Canvas_Frame.pack(side = tk.TOP)
        
    def CF_update(self):
        PROFILE = self.callback(Return = True)
        df = OKRLOG_to_df(PROFILE.todos.Load.WeekObjective) 
        try:
            self.Canvas_Frame.destroy()
        except AttributeError:
            pass 
        self.CF_create(master = self.CF)
        #Plotting 
        self.Analysis.Rest_fig((4,6)) 
        self.Analysis.Plot_Sec(sec = 'weight', dim = 211, title = 'Weight Distribution')
        self.Analysis.Plot_Sec(sec = 'weight', df = df[df['Task_Type'] == self.View.get()],
                               dim = 212 ,  title = f'Weight Dist of {self.View.get()}')
        #Finally:
        self.fig = self.Analysis.get_fig()
        self.canvas = FigureCanvasTkAgg(self.fig,self.Canvas_Frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP, anchor = 'n')
        
    def REFRESH(self):
        #Refresh Everything Based on Current Profile
        PROFILE = self.callback(Return = True)
#***:Update the Load Progress with current Archive 
        PROFILE.todos.Load,_ = Get_Scores(df = PROFILE.todos.Archive,
                                        Loaded = PROFILE.todos.Load,
                                        RETURN_null = True)
        self.callback(PROFILE,Update = True)
        
        #Re_init the DF_Analysis
        try:    
            df = OKRLOG_to_df(PROFILE.todos.Load.WeekObjective) 
        except:
            df = pd.DataFrame()
        self.Analysis = DF_Analysis(df,(3,6))
        
        self.Show_View() 

        
        
    def Load_Plan(self):
        filename = tk.filedialog.askopenfile(filetypes=[('OKRLOG', '*.docx')])                                 
        self.file_path = filename.name
        PROFILE = self.callback(Return = True)
        try:
            token = self.todos.Load.Get_token()
        except:
            pass 
        PROFILE.todos.get_Load(self.file_path)
        try:
            PROFILE.todos.Load.set_token(token)
        except:
            print("NO TOKEN Accessible")
        self.callback(PROFILE,Update = True)
        self.REFRESH()
        self.MAIN.gpk_weekPlanning.REFRESH()
        #Re_init the Recur setting frame
        self.MAIN.gpk_Recur_frame.Ref(True,True)
        
    def Show_View(self):
        PROFILE = self.callback(Return = True)
        whatWasPrinted = print_collector(PROFILE.todos.Load.WeekObjective.show,
                                         sections = [self.View.get()])
        self.OKRVIEW.set(whatWasPrinted) 
        self.Text_refresh()
        self.CF_update()
    
    def Text_refresh(self):
        self.OKRLOG_Text.delete("1.0","end")
        self.OKRLOG_Text.insert("1.0", self.OKRVIEW.get())
        
    def Report_Gen(self):
        title = tk.simpledialog.askstring(title = 'Generate Week Report',
                                                prompt = 'Please Specify Season and Date.E.g: Season3_Week2')
        if title is not None:
            Report = gpk_Report(self.callback(Return = True),"OKR_"+title+"Report")
            Report.OKR_report(title)            
        
    def _draw(self):
        #__________________LeftFrame_____________________#
        self.LeftFrame = tk.Frame(master = self)#, bg = 'blue')
        self.LeftFrame.config(width = 4*self.width/5, height = self.height)
        self.LeftFrame.config(highlightbackground="black" , highlightthickness=2)
        self.LeftFrame.grid(row = 0, column = 0 ,padx=200, pady=20
                            )#.pack(side = tk.LEFT,fill="y", expand=True, padx=20, pady=20)
            ##_________Text_Display___________##
        self.OKRVIEW = tk.StringVar()
        self.OKRLOG_Text = tk.Text(self.LeftFrame,
                                   height = 50, width = 75, 
              bg = "light cyan")
        self.OKRLOG_Text.configure(font=("Times New Roman", 14, "bold"))
        self.OKRLOG_Text.pack()
        #__________________RightFrame_____________________#
        self.RightFrame = tk.Frame(master = self)#, bg = 'green')
        self.RightFrame.config(width = 2*self.width/5, height = self.height)
        self.RightFrame.grid(row = 0, column = 1)#.pack(side = tk.LEFT)
        
                            ##_________Canvas Frame________##
        self.CF = tk.Frame(master = self.RightFrame)#, bg = 'orange')
        self.CF.config(width = 2*self.width/5, height = (2/3)*self.height)
        self.CF.pack()

        
            ##_________Interaction Frame________##
        self.InterFrame = tk.Frame(master = self.RightFrame)#, bg = 'orange')
        self.InterFrame.config(width = 2*self.width/5, height = (1/3)*self.height)
        self.InterFrame.pack()
                ###___Radio Buttons___###
        self.View = tk.StringVar()
        self.View.set("Priority_Task")
        self.PT_Rbtn = tk.Radiobutton(self.InterFrame, text = "Priority_Task", variable = self.View,
                                        value = 'Priority_Task',command = self.Show_View)
        self.ST_Rbtn = tk.Radiobutton(self.InterFrame, text = "Special_Task", variable = self.View,
                                        value = 'Special_Task',command = self.Show_View)
        self.RT_Rbtn = tk.Radiobutton(self.InterFrame, text = "Recursive_Task", variable = self.View,
                                        value = 'Recursive_Task',command = self.Show_View)
        
        self.PT_Rbtn.pack(padx = 5, pady = 5)#.gird(row = 1, column = 1,padx = 5, pady = 5)
        self.ST_Rbtn.pack(padx = 5, pady = 5)#.gird(row = 2, column = 1,padx = 5, pady = 5)
        self.RT_Rbtn.pack(padx = 5, pady = 5)#.gird(row = 3, column = 1,padx = 5, pady = 5)
                ###___Buttons___###
        self.RT_setting_btn = tk.Button(self.InterFrame,text = 'Recursive_Task Settings')
        self.RT_setting_btn.config(command = lambda : self.callback(call_frame_name = 'gpk_Recur_frame'))
        
        self.Import_btn = tk.Button(self.InterFrame,text = 'Import OKR Week Agenda',
                                    command = self.Load_Plan)
        self.Report_btn = tk.Button(self.InterFrame,text = 'Export Report',command = self.Report_Gen)

        
        self.RT_setting_btn.pack(padx = 5, pady = 5)#.gird(row = 4, column = 0,padx = 5, pady = 5)
        self.Import_btn.pack(padx = 5, pady = 5)#.gird(row = 5, column = 1,padx = 5, pady = 5)
        self.Report_btn.pack(padx = 5, pady = 5)#.gird(row = 6, column = 2,padx = 5, pady = 5)

        #
        try:
            self.Show_View()
        except AttributeError:
            print("OKRLOG not Loaded")
        try:
            self.CF_update()
        except AttributeError:
            pass 
        
        
class gpk_weekPlanning(tk.Frame):
    def __init__(self,root,geometry,callback  = None,main = None):
        super().__init__()
        self.callback = callback
        self.MAIN = main 
        self.height = geometry['height']
        self.width = geometry['width']
        self.root = root
        try:
            df = Plan_to_df(self.callback(Return = True))
        except:
            df = pd.DataFrame()
        self.Analysis = DF_Analysis(df, (10,7))
        #Finally 
        self._draw()
        
    
        
    def If_OKR_Planner(self,PROFILE):
        PROFILE = self.callback(Return = True)
        return list(PROFILE.todos.SECTIONs.values()) == [
        'Inbox','monday','tuesday','wednesday',
         'thursday','friday','saturday','sunday']
        
    def Locate(self,Loaded,ID):
            "Given Load Object and ID, return the corresponding Goal"
            sec = {'S':'Special_Task','R':'Recursive_Task','P':"Priority_Task"}
            for task in eval(f'Loaded.WeekObjective.{sec[ID.split("_")[0]]}'):
                if ID .split("_")[1] == task.Objective.split(":")[0]:
                    return task 
            return None
        
    def show_detail(self,event = None):
        PROFILE = self.callback(Return = True)
        self.PlanView.retrieve() #Update the selected 
        ID = self.PlanView.selected.get().split(":")[1].strip(" ")
        Gtask = self.Locate(PROFILE.todos.Load,ID)
        Info = str(Gtask)
        try:
            self.PlanView.Text_refresh(Info)
        except:
            pass 
        
    def _SEND(self):
        "Regular Planning Procedure"
        if self.sync_status.get():
            self.ReLoad()
            self.callback(Profile,Update = True)
            if not self.If_OKR_Planner():
                if messagebox.askokcancel(
                    "Create New Project",
                    "Current Selected is NOT valid Planner,do you wish to create a New one?"):
                    Profile.todos.Planner_SetUp()
                    Profile.todos.Post_All()
                else:
                    if messagebox.askokcancel(
                    "Create New Project",
                    "Current Selected is NOT valid Planner,do you wish to create a New one?"):
                        self.callback(call_frame_name = gpk_mtk_frame)
            else:
                Profile.todos.Post_All()
        else:
            getattr(messagebox,'showwarning')("Sync Not Enabled",
            "Please first Check the Sync checkbox.")    
            
        
    def mtk_sync(self):
        #1.Check Sync Status 
        if self.sync_status.get():
            #2.Check if Project Match 'OKR_Planner'
            PROFILE = self.callback(Return = True)
            if not self.If_OKR_Planner(PROFILE):
                getattr(messagebox,'showwarning')("Wrong Project",
                              "Make 'OKR_Planner' is selected")
                self.callback(call_frame_name = 'gpk_mtk_frame')
            else:
                #3.Call GPK_MTK.Sync
                count_down = 3
                Synced = False
                while not Synced and count_down >= 0:
                    try:
                        PROFILE.todos.Sync() 
                        Synced = True 
                    except:
                        count_down -= 1
                        print(f"SYNC Failed, Try again in 3 seconds") 
                        sleep(3)
                #4.Convert Data into Dictionary
                if not Synced:
                    getattr(messagebox,'showwarning')("Sync Failure",
                              "Server Busy, Please check internet and Try again later")
                Dict = {}
                    #Create a dict 
                for sec in PROFILE.todos.SECTIONs.values():
                    try:
                        Dict[sec] = PROFILE.todos.View_df(sec)
                    except KeyError:
                        pass 
                OUT = {}
                for sec in Dict:
                    OUT[sec]  = []
                    if isinstance(Dict[sec],pd.DataFrame):
                        for idx in Dict[sec].index:
                            row = Dict[sec].iloc[idx]
                            Gtask = gpk_task(row['name'],row['notes'])
                            OUT[sec].append(Gtask)
                #5.updated PROFILE 
                PROFILE.okr_plan = OUT 
                self.callback(PROFILE,Update = True)
                #6:
                self.LB_Ref()
        else:
            getattr(messagebox,'showwarning')("Sync Not Enabled",
              "Please first Check the Sync checkbox.")    
            
                
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
            
    def LB_Ref(self):
        Plan = self.callback(Return = True).okr_plan
        #Clear ALL
        self.PlanView.LB_Clear()
        #Fetch Data 
        for sec in Plan:
            IDs = [Gtask.ID for Gtask in Plan[sec]]
            self.PlanView.INSERT(sec,IDs)
    
    def ReLoad(self):
        "Load Again from raw"
        filename = tk.filedialog.askopenfile(filetypes=[('OKRLOG', '*.docx')])                                 
        self.file_path = filename.name
        Profile = self.callback(Return = True)
        try:
            token = self.todos.Load.Get_token()
        except:
            token = "Register Notion API and paste the token here"
        Profile.todos.get_Load(self.file_path)
        Profile.todos.Load.set_token(token)
        Profile.todos.Load,_ = Get_Scores(df = Profile.todos.Archive,
                                Loaded = Profile.todos.Load,
                                RETURN_null = True) #Update the progress
        self.callback(Profile,Update = True) 
        
        
    def REFRESH(self):
        Profile = self.callback(Return = True)
        Loaded = Profile.todos.Load
        Plan = Fetch_plan_null(Loaded)
        Profile.okr_plan = Plan
        self.callback(Profile,Update = True)
        self.Get_Option()
        self.LB_Ref()
        self.CF_update(master = self.CF ) 
        
    def IMPORT(self):
        #Update Profile
        self.ReLoad()
        # self.PlanView.INSERT('Inbox',ids)
        #1. Create New Plan:
        self.REFRESH()
        #2. Update Recurs 
        self.MAIN.gpk_Recur_frame.Ref(True,True)
        #3.Refresh the weekview 
        self.MAIN.gpk_weekView.REFRESH()
        
    def move_to(self,ID,Section):
        Profile = self.callback(Return = True) 
        found = False
        if Section != 'Plan Not Loaded':
            assert Section in  Profile.okr_plan , f'Section {Section} not found '
        #1.Locate The Gtask:
        for sec in Profile.okr_plan :
            for Gtask in Profile.okr_plan[sec]:
                if Gtask.ID == ID:
                    Profile.okr_plan[Section].append(Gtask)
                    Profile.okr_plan[sec].remove(Gtask)
                    found = True 
        if not found:
            print(f"ERROR,Task with ID:{ID} not found at Profile.okr_plan")
        #Finally Update the Profile:
        self.callback(Profile,Update = True)
        
        #Reflecting On LB and CF:
        self.LB_Ref()
        #TRY to Plot
        self.CF_update(master = self.CF)
        
    def MOVE(self):
        ID = self.PlanView.selected.get().split(':')[1]
        Sec = self.day_option.get()
        if ID == 'Select and Submit to update':
            messagebox.showinfo("Task not Selected","Select the task from the listbox you wish to move")
        if Sec == '':
            messagebox.showinfo("Section not Selected","Please first select section from the com box")

        self.move_to(ID,Sec)

    
    def Get_Option(self):
        try:
            self.Options = list(self.callback(Return = True).okr_plan.keys())
            self.day_option = ttk.Combobox(self.Control_Frame, values = self.Options)
            self.day_option.grid(row = 2,column = 2)
        except:
            self.Options = ['Plan Not Loaded']
            print('Plan Not Loaded')
            
    ## Adding Canvas Mods:
    def CF_create(self,master,hc = 2/3, wc = 2/5,side = None):
        "Create a Canvas Frame"
        self.Canvas_height_coef = 3/4 
        self.Canvas_width_coef = 2/3
        self.Canvas_Frame = tk.Frame( master = master, bd = 0 )##, bg = 'green')
        self.Canvas_Frame.configure(height = self.Canvas_height_coef*self.height,
                                  width = self.Canvas_width_coef*self.width)
        self.Canvas_Frame.config(highlightbackground="black" , highlightthickness= 2)
        self.Canvas_Frame.pack(side = tk.TOP, anchor = 'n')
        
    def CF_update(self , master ):
        try:
            self.Canvas_Frame.destroy()
        except AttributeError:
            pass 
        self.CF_create(master = master)
        #Plotting 
        PROFILE = self.callback(Return = True)
        df = Plan_to_df(PROFILE) 
        self.Analysis.Set_df(df)
        self.Analysis.Rest_fig() 
    ##OLD
        # self.Analysis.Plot_DateFrame(Group = 'Plan_at',
        #                              title = 'Time(Top)/Reward(Buttom) Dist of Current Plan',dim = 211,short = True)
        # self.Analysis.Plot_DateFrame(Group = 'Plan_at',sec = 'Reward',
        #                              title = '',dim = 212,short = True)
        # self.Analysis.Plot_Sec(sec = 'weight', dim = 211, title = 'Weight Distribution')
        # self.Analysis.Plot_Sec(sec = 'weight', df = df[df['Task_Type'] == self.View.get()],
        #                        dim = 212 ,  title = f'Weight Dist of {self.View.get()}')
        #Finally:
        #self.fig = self.Analysis.get_fig()
    ###NEW:Agg Plot
        T = D_Reflection(PROFILE, PROFILE.todos.Archive)
        fig = plt.Figure(figsize = (11,4))
        self.fig = T.Plot_plan_color(fig,section = 'Time', 
                                     RECUR_show= self.Recur_show.get(),
                                     Completed_show = self.Completed_show.get())
    ###Finally:
        self.canvas = FigureCanvasTkAgg(self.fig,self.Canvas_Frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP, anchor = 'n')
            
    def _draw(self):
        #___________LeftFrame______________#
        self.LeftFrame = tk.Frame(master = self)#, bg = 'orange')
        self.LeftFrame.config(width = self.width/2, height = self.height,
                              padx = 15)
        self.LeftFrame.pack(side = tk.LEFT, fill = 'x')
        ##PlanOverview (Plan Box) 
        self.Plan_BOX = tk.Frame(self.LeftFrame)
        self.Plan_BOX.pack(side = tk.TOP)
        ## Objective Details
        self.Oview = tk.Frame(master= self.LeftFrame)#, bg = 'blue')
        self.Oview.config(width = self.width/2, height = self.height/2)
        self.Oview.pack(side = tk.BOTTOM, fill = 'x')
        
        
        ##_PlanView under Plan_BOX##
        self.PlanView = tkLIST(self.Plan_BOX,n=8,bg = 'green',show_sub = True,
                               view_frame = self.Oview , header = [
        'Inbox','monday','tuesday','wednesday',
         'thursday','friday','saturday','sunday'])
        for listbox in self.PlanView.LISTBOXes:
            listbox.bind("<<ListboxSelect>>", self.show_detail)
        try:
            self.LB_Ref()
        except AttributeError:
            pass 
        
        #___________RightFrame______________#
        self.RightFrame = tk.Frame(master = self)#, bg = 'pink')
        self.RightFrame.config(width = self.width/2, height = self.height)
        self.RightFrame.pack(side = tk.LEFT, fill = 'x')
        
            ## Canvas Frame
        self.CF = tk.Frame(master= self.RightFrame)#, bg = 'purple')
        self.CF.config(width = self.width/2, height = (3/4)*self.height)
        self.CF.pack(side = tk.TOP, fill = 'both')                
                
            ## Control Frame 

        self.Control_Frame = tk.Frame(master= self.RightFrame)#, bg = 'purple')
        self.Control_Frame.config(width = self.width/2, height = self.height/4)
        self.Control_Frame.pack(side = tk.TOP, fill = 'both')                
                ### Buttons 
###SPACER
        self.spacer = tk.Label(master = self.Control_Frame,text = "",
                               padx = 35)
        self.spacer.grid(row = 0,column = 0)
    ### Plot Filter:
        self.Recur_show = tk.IntVar()
        self.Rec_show_ckbx = tk.Checkbutton(self.Control_Frame,text = 'Show Recursive Tasks', variable = self.Recur_show,
                                            command = lambda:self.CF_update(master = self.CF ) )
        self.Rec_show_ckbx.grid(row = 0,column = 1)
        self.Completed_show = tk.IntVar()
        self.Completed_show_ckbx = tk.Checkbutton(self.Control_Frame,text = 'Show Completed Goals', 
                                                  variable = self.Completed_show,
                                                  command = lambda:self.CF_update(master = self.CF ) )
        self.Completed_show_ckbx.grid(row = 0,column = 2, padx = 10)
                #### Move Buttons
        self.Import_btn = tk.Button(self.Control_Frame,text = 'Import OKRLOG',
                                    font = ('times new roman',20))
        self.Import_btn.config(command = self.IMPORT)
        self.Import_btn.grid(row = 1, column = 2,padx=10, pady=10)
        self.Move_btn = tk.Button(self.Control_Frame,text = 'Move to:',padx = 5)
        self.Move_btn.grid(row = 2, column = 1,padx=10, pady=10)
        self.Get_Option()
        self.day_option = ttk.Combobox(self.Control_Frame, values = self.Options)
        self.day_option.grid(row = 2,column = 2)
        self.Move_btn.config(command = self.MOVE)
                    #### MTK Sync Buttons 


        
        #Add Mtk Sync Status 
        self.sync_status = tk.IntVar()
        self.sync_chbx = tk.Checkbutton(self.Control_Frame, variable =self.sync_status,
                                        onvalue=1, offvalue=0, command = self.check_mtk_sync_status)
        self.sync_chbx.grid(padx = 20,row = 3, column = 1)
        self.rmchbox_label = tk.Label (self.Control_Frame,text = "MTK SYNC")
        self.rmchbox_label.grid(row = 3, column = 2)
        #Add Sync Button 
        self.sync_ref_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.SYNC_btn = tk.Button(master =self.Control_Frame, image  =  self.sync_ref_img , 
                                  command = self.mtk_sync)
        self.SYNC_btn.grid(padx = 20,row = 3, column = 3)
        
        #SEND OKRLOG
        self.SEND_btn = tk.Button(self.Control_Frame, text = 'SEND PLAN',
                                  font = ('times new roman',20))
        self.SEND_btn.config(command = self._SEND)
        self.SEND_btn.grid(row = 4,column = 2,padx=10, pady=10)
        
        ## Canvas Frame   
        try:
            self.CF_update(master= self.CF)
        except:
            pass 
