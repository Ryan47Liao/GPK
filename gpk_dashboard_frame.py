import tkinter as tk 
from tkinter import ttk
from gpk_utilities import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
from PIL import ImageTk,Image
import os

class gpk_dash(tk.Frame):
    def __init__(self,root,geometry,callback  = None):
        super().__init__()
        self.root = root
        self.callback = callback
        self.height = geometry['height']
        self.width = geometry['width']
        self._draw()
        
    def REFRESH_ALL(self):
        Updates = ['Progress_Update','CF_Update','TreeView_Update','Score_Update']
        for update in Updates:
            try:
               eval(f"self.{update}()")
            except:
                print(f"<{update}> Fail to Update")
        
    def Progress_Update(self):
        Profile = self.callback(Return = True)
        text = print_collector(Profile.todos.Load.WeekObjective.show)
        self.TEXT.delete("1.0","end")
        self.TEXT.insert("1.0", text)
        
    def CF_Update(self):
        #1.Create Canvas 
        try:
            self.CF_Plots.destroy()
        except:
            pass 
        self.CF_Plots = tk.Frame(master= self.CF)
        self.CF_Plots.pack(fill = 'both')
        #2.Draw and Update Canvas 
        PROFILE = self.callback(Return = True)
        Analysis = DF_Analysis(df = PROFILE.todos.Archive, figsize = (9,5))
        #
        Analysis.Plot_Sec(n = 30,sec = 'Time',
                          df = PROFILE.todos.Archive, dim = 221 , title = 'Sectional Time Distribution for last 30 days')
        Analysis.Plot_Date(n=7, sec = 'Time',dim = 222, df = PROFILE.todos.Archive,short = True,
                           title = 'Time/Reward Distribution for last 7 days')
        Analysis.Plot_Sec(n = 30,sec = 'Reward',
                          df = PROFILE.todos.Archive, dim = 223 , title = 'Sectional Reward Distribution for last 30 days')
        Analysis.Plot_Date(n=7, sec = 'Reward',dim = 224, df = PROFILE.todos.Archive,short = True,title = "")
        #3.Plot 
        fig = Analysis.get_fig()
        canvas = FigureCanvasTkAgg(fig,self.CF_Plots)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)   
        
    def TreeView_Update(self):
        #Create TreeView
        try:
            self.treeview.destroy()
        except:
            pass 
        #
        Profile = self.callback(Return = True)
        Analysis = DF_Analysis(Profile.todos.todos)
        df = Analysis.SEARCH("Deadline",lambda date: DATE(date)
                              <= (datetime.datetime.now() + datetime.timedelta(days = self.N.get())).date())
        if self.Task_Type_Combo.get() != 'All':
            option = self.Task_Type_Combo.get()[0] 
            df = Analysis.SEARCH('ID', lambda id: str(id).split('_')[0] == option,df = df ) 
        
        self.treeview = df_to_Treeview(master=self.TVF, col_width = 100,
                                       data = df)
        self.treeview.pack(pady = 20, ipady = 100)        
        
    def Score_Update(self):
        #1.Create Canvas 
        try:
            self.CF_S.destroy()
        except:
            pass 
        self.CF_S = tk.Frame(master= self.SF)
        self.CF_S.pack(fill = 'both')
        #2.Draw and Update Canvas 
        PROFILE = self.callback(Return = True)
        Analysis = DF_Analysis(df = PROFILE.todos.Archive, figsize = (8,4.5))
        Analysis.Plot_Score(Loaded = PROFILE.todos.Load_backup)
        #3.Plot 
        fig = Analysis.get_fig()
        canvas = FigureCanvasTkAgg(fig,self.CF_S)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)        
            
    def _draw(self):
        img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.Refresh_btn = tk.Button(master = self,text = 'Refresh DashBoard', command = self.REFRESH_ALL,
                                     font = ('times new roman',14))
        self.Refresh_btn.pack()
#___________LeftFrame______________#
        self.LeftFrame = tk.Frame(master = self)#, bg = 'orange')
        self.LeftFrame.config(width = self.width/2, height = self.height)
        self.LeftFrame.pack(side = tk.LEFT, anchor = 'w')
    ##______1.Task TreeView Frame_______##
        ###__Control_Frame__###
        self.N = tk.IntVar()
        self.N.set(3)
        self.Control_Frame = tk.Frame(self.LeftFrame)
        self.Control_Frame.grid(row = 0, column = 1,columnspan = 3)
        
        Option = ['Priority_Task','Special_Task','Recursive_Task','All']
        self.Task_Type_Combo = ttk.Combobox(self.Control_Frame, values = Option)
        self.Task_Type_Combo.grid(row = 0, column = 0)
        self.Task_Type_Combo.set("All")
        
        lab1 = tk.Label(self.Control_Frame,text = 'Due in')
        lab2 = tk.Label(self.Control_Frame,text = 'Days')
        self.N_entry = tk.Entry(self.Control_Frame,textvariable = self.N,width = 4)
        lab1.grid(row = 0, column = 1)
        self.N_entry.grid(row = 0, column = 2)
        lab2.grid(row = 0, column = 3)
        ###__TreeView###
        self.TVF = tk.Frame(master = self.LeftFrame)#, bg = 'pink')
        self.TVF.config(width = self.width/2, height = self.height/2)
        self.TVF.grid(row = 1, column = 1,padx = 20, columnspan = 3)
    ##______2.Canvas Frame_______##
        self.CF = tk.Frame(master = self.LeftFrame)#, bg = 'purple')
        self.CF.config(width = self.width/2, height = self.height/2)
        self.CF.grid(row = 2, column = 1,padx = 20, columnspan = 3)
#___________RightFrame______________#
        self.RightFrame = tk.Frame(master = self)#, bg = 'green')
        self.RightFrame.config(width = self.width/2, height = self.height)
        self.RightFrame.pack(side = tk.LEFT, anchor = 'e') 
    ##______3.Score Frame_______##
        self.SF = tk.Frame(master = self.RightFrame)#, bg = 'blue')
        self.SF.config(width = self.width/2, height = self.height/2)
        self.SF.pack(fill = 'both', pady = 20)
    ##______4.WeekProgress Frame_______##
        self.WPF = tk.Frame(master = self.RightFrame)#, bg = 'yellow')
        self.WPF.config(width = self.width/2, height = self.height/2)
        self.WPF.pack(fill = 'both')
        self.TEXT = tk.Text(self.WPF, height = 20, width = 80, 
              bg = "light cyan")
        self.TEXT.configure(font=("Times New Roman", 14, "bold"))
        self.TEXT.pack(padx = 10, pady = 20)
        #Finally:
        self.REFRESH_ALL()