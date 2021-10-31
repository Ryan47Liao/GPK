import tkinter as tk

class gpk_setting:
    def __init__(self):
        #1.Full Screen 
        self.FS_status = False
        #2.Rec Window Size
        self.change_size()#Set By Deafault 
        self.screen_auto = False

        
    def change_size(self,width = 2560 ,height = 1600,ratio = 1.5):
        self.zoom_ratio = ratio
        self.screen_width = width
        self.screen_height = height
        
    def Auto_adjust(self,root):
        screen_width = root.winfo_vrootwidth()#root.winfo_screenwidth() 
        screen_height = root.winfo_vrootheight()#root.winfo_screenheight()
        self.change_size(width = screen_width, height = screen_height, ratio = 1)
        
    def Fetch_Resolutions(self):
        self.res_opt = ['2560 x 1600','2560 x 1440','2560 x 1080','2048 x 1536','1920 x 1200','1920 x 1080',
                '1680 x 1050','1600 x 1200','1600 x 900','1440 x 900']
        current_res = f'{self.screen_width} x {self.screen_height}'
        if current_res not in self.res_opt:
            self.res_opt.append(current_res)
        
    