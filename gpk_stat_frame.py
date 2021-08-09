from gpk_utilities import *
from tkinter import ttk
from PIL import ImageTk,Image
import os
import pickle
import copy
from  tkinter import messagebox
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)

from gpk_archive_frame import gpk_archive

class gpk_analysis(gpk_archive):
    def __init__(self,root,geometry,call_back = None):
        tk.Frame.__init__(self)#,bg = 'blue')
        self.root = root
        self.call_back = call_back 
        self.Profile = call_back(Return = True)
        self.height = geometry['height']
        self.width = geometry['width']
        self.Search =  DF_Search(self.Profile.todos.Archive)
        self.Analysis = DF_Analysis(df = self.Profile.todos.Archive,figsize = (10,5))
        self.NEW_DF = False
        self._draw()
        
        
    def CF_create(self):
        "Create a Canvas Frame"
        self.Canvas_height_coef = 2/3 
        self.Canvas_width_coef = 2/3
        self.Canvas_Frame = tk.Frame( master = self.FrameUPPER, bd = 30)#, bg = 'green')
        self.Canvas_Frame.configure(height = self.Canvas_height_coef*self.height,
                                  width = self.Canvas_width_coef*self.width)
        self.Canvas_Frame.config(highlightbackground="black" , highlightthickness=2)
        self.Canvas_Frame.pack(side = tk.LEFT)
        
    def CF_refresh(self):
        self.Canvas_Frame.destroy()
        self.CF_create()
        
    
    def Submit(self):
        self.CF_refresh()
        #_____PLOTING______#
        self.Analysis.Rest_fig()
        if not self.NEW_DF:
            self.Analysis.Set_df(self.call_back(Return = True).todos.Archive)
        if self.Combo.get() == 'Pick an Option':
            getattr(messagebox,'showwarning')("Option Error","You must Select an Option first (Time/Reward)") 
        else:
            if self.By_Section.get():
                self.Analysis.Plot_Sec( n = int(self.NUM.get()) , time_frame = self.plot_option.get(),
                                sec = self.Combo.get(), shreshold = 0.2)
            else:
                #Deafault:Last 7 Days
                if self.plot_option.get() == 'Day':
                    self.Analysis.Plot_Date(int(self.NUM.get()),
                                                       sec = self.Combo.get())
                elif self.plot_option.get() == 'Week': 
                    self.Analysis.Plot_Week(int(self.NUM.get()),
                                                       sec = self.Combo.get())
                elif self.plot_option.get() == 'Month':
                    self.Analysis.Plot_Month(int(self.NUM.get()),
                                                       sec = self.Combo.get())  
            #_____PLOTING______#
            self.fig = self.Analysis.get_fig()
            self.canvas = FigureCanvasTkAgg(self.fig,self.Canvas_Frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row = 0, column = 0)        
            
    def Apply_df(self,df):
        self.Analysis.Set_df(df)
        
    def pop_df(self,df):
        res_temp = gpk_archive.pop_df(self,df)
        save_btn = tk.Button(master = res_temp,text = 'Apply Filter')
        save_btn.configure(command = lambda :self.Apply_df(df))
        save_btn.pack()
        self.NEW_DF = True
    
    def _draw(self):
    #____Upper Frame___
        self.FrameUPPER = tk.Frame(master = self, bd =20)#, bg = 'blue')
        self.FrameUPPER.configure(height = 4*self.height/5 ,width = self.width)
        self.FrameUPPER.pack()
        #Canvas Frame 
        self.CF_create()

        
        
    #____Lower Frame___ 
        self.FrameLOWER = tk.Frame(master = self, bd = 2)#, bg = 'orange')
        self.FrameLOWER.configure(height = self.height/2 ,width = self.width)
        self.FrameLOWER.pack( )
        
        #______Quick Plot Frame___________ 
        self.QP_Frame = tk.Frame(master = self.FrameLOWER, bd = 10)#, bg = 'Yellow')
        self.QP_Frame.configure(height = self.Canvas_height_coef*self.height,
                                  width = (1-self.Canvas_width_coef)*self.width)
        self.QP_Frame.pack(side = tk.LEFT)
        
        ##__________Radio Buttons__________:
        self.plot_option = tk.StringVar()
        self.plot_option.set('Day')
        self.BD_7_Rbtn = tk.Radiobutton(self.QP_Frame, text = "By Day", variable = self.plot_option,
                                        value = 'Day')
        self.BD_w_Rbtn = tk.Radiobutton(self.QP_Frame, text = "By Week", variable = self.plot_option,
                                        value = 'Week')
        self.BD_m_Rbtn = tk.Radiobutton(self.QP_Frame, text = "By Month", variable = self.plot_option,
                                        value = 'Month')
        # self.BD_a_Rbtn = tk.Radiobutton(self.QP_Frame, text = "--ALL--", variable = self.plot_option,
        #                         value = 4)
        self.BD_7_Rbtn.grid(row = 0, column = 1, padx = 5, pady = 5)
        self.BD_w_Rbtn.grid(row = 1, column = 1,padx = 5, pady = 5)
        self.BD_m_Rbtn.grid(row = 2, column = 1,padx = 5, pady = 5)
        # self.BD_a_Rbtn.grid(row = 3, column = 1,padx = 5, pady = 5)
        
        
        #Combo Box 
        Option = ['Time','Reward']
        self.Combo = ttk.Combobox(self.QP_Frame, values = Option)
        self.Combo.set("Pick an Option")
        self.Combo.grid(row = 4, column = 1,padx = 5, pady = 5)
        #Section Check Box:

        self.By_Section = tk.IntVar()
        self.SEC_ChkBttn = tk.Checkbutton(self.QP_Frame, text = 'By Section',width = 15, variable = self.By_Section,
                                       onvalue=1, offvalue=0)
        self.SEC_ChkBttn.grid(row = 5, column = 1)
        
        #Advanced Setting 
        self.adv_set_btn = tk.Button(self.QP_Frame,text='Advanced Setting',
                                     command = self.archive_Search)
        self.adv_set_btn.grid(row = 6,column = 1, pady = 10)
        
        #Filter Frame 
        self.Filter_Frame = tk.Frame(master = self.FrameLOWER, bd = 10)#, bg = 'red')
        self.Filter_Frame.configure(height = (1-self.Canvas_height_coef)*self.height,
                                  width = (1-self.Canvas_width_coef)*self.width)
        self.Filter_Frame.pack(side = tk.LEFT)
        ##Query Summary:
        self.FF_upper = tk.Frame(master = self.Filter_Frame, bd = 10)
        self.FF_upper.pack()
        ###Entry BOX
        font = ("Courier", 14)
        self.option_lab = tk.Label(self.FF_upper, textvariable = self.plot_option,font=font)
        self.NUM = tk.IntVar()
        self.NUM.set(7)
        self.NUM_Entry = tk.Entry(self.FF_upper,textvariable = self.NUM, width = 2, font=font)
        tk.Label(self.FF_upper, text = 'Last ',font=font).grid(row = 3, column = 0)
        self.NUM_Entry.grid(row = 3, column = 1)
        self.option_lab.grid(row = 3, column = 2)
        ##Submit Button
        self.img_complete = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/Confirm.png"))
        self.Submit_btn = tk.Button(master =self.Filter_Frame, image  =  self.img_complete , command = self.Submit)
        self.Submit_btn.pack()
        
        
        

if __name__ == '__main__':
    with  open( 'D:\GPK\gpk_saves\MrFAKE_user_file.gpk' ,"rb") as INfile:
        Profile = pickle.load(INfile)
    df = Profile.todos.Archive 
    T = DF_Analysis(df)
    # fig = T.Plot_Week(7,figsize = (10, 5))
    # T.fig_preview(fig,'1000x500')
    fig = T.Plot_Month(7,figsize = (10, 5))
    T.fig_preview(fig,'1000x500')

