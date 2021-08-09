from gpk_utilities import *
from PIL import ImageTk,Image
import os

class gpk_archive(tk.Frame):
    def __init__(self,root,call_back = None):
        super().__init__(bg = 'pink')
        self.root = root
        
        self.call_back = call_back 
        self.Profile = self.call_back(Return = True)
        #Finally:
        self._draw()
        self.tree_update()
    
    #Tree_View Methods 
    def tree_update(self):
        try:
            self.treeview.destroy()
        except:
            pass 
        Profile = self.call_back(Return = True)
        self.Search = DF_Search(Profile.todos.Archive)
        self.treeview = df_to_Treeview(master=self, data = Profile.todos.Archive)
        self.treeview.pack(pady = 20, ipady = 200)
        
    #Filter Settings
    def row_gen(self,sec_name,row):
        definition = f"""
self.{sec_name}_status = tk.IntVar()
self.{sec_name}_lab = tk.Label(self.window,text = '{sec_name}')
self.{sec_name}_chbx = tk.Checkbutton(self.window,variable = self.{sec_name}_status,onvalue=1, offvalue=0)
self.{sec_name}_entry = tk.Entry(master = self.window)

self.{sec_name}_chbx.grid(row = {row},column = 0)
self.{sec_name}_lab.grid(row = {row},column = 1)
self.{sec_name}_entry.grid(row = {row},column = 2)
                         """
        exec(definition)
        
    def archive_Search(self):
        def S_C(STR):
            temp = STR.split(" ")
            out = ""
            for i in temp:
                out += str(i) + "_"
            return out[:-1]
        
        self.window = tk.Toplevel()
        #self.window.geometry('150x150')
        
        self.submit_btn = tk.Button(master = self.window, text = 'Submit', command = self.SEARCH)

        self.SECs = [S_C(i) for i in self.Search.df.keys()]
        for row,sec in enumerate(self.SECs):
            self.row_gen(sec,row)
        #Packing
        self.submit_btn.grid(row = row+1,column = 1)
        
        
    def SEARCH(self):
        Stack = []
        for sec in self.SECs:
            if eval(f'self.{sec}_status.get()'):
                prediction = eval(f"self.{sec}_entry.get()")
                definition = f"""
def pred_{sec}(x):
    return {prediction} 
                              """
                exec(definition)
                pred = eval(f"pred_{sec}")
                Stack.append( (sec,pred) )
                
        RES_df  = self.Search.Stack_Search(Stack)
        self.pop_df(RES_df)
        
    def pop_df(self,df):
        node_select = 0 
        def node_select(event = None):
            nonlocal tree_index
            tree_index = int(treeview.selection()[0]) 
            description_update()
            
        def description_update():
            nonlocal tree_index
            des = str(df.iloc[tree_index]['description'])
            task_DES.set(des)
            
        def task_delete():
            nonlocal tree_index
            Profile = self.call_back(Return = True)
            true_idx = perfect_match(df = Profile.todos.Archive,
                                     target = df.iloc[tree_index])
            print(f"Try to delete Task at index {true_idx}")
            if not isinstance(true_idx,int):
                true_idx = int(true_idx)
            #Update the Profile 
            Profile.todos.Archive = Profile.todos.Archive.drop(
                Profile.todos.Archive.index[true_idx])
            print(f"Task at index {true_idx} DELETED")
            self.call_back(Profile,Update = True)
            #Update BOTH TreeView
            
            
        tree_index = 0
        task_DES = tk.StringVar()
        task_DES.set("Select Task To update")
        res_temp = tk.Toplevel()
        treeview = df_to_Treeview(master = res_temp, data = df)
        treeview.pack(pady = 20)
        treeview.bind("<<TreeviewSelect>>", node_select)
        task_DES_lab = tk.Label(res_temp,textvariable = task_DES)
        task_DES_lab.pack()
        #Delete Task 
        delete_button = tk.Button(res_temp,text = 'Delete', command = task_delete)
        delete_button.pack()
        
        return res_temp
            
    def _draw(self):
        #Definition
        self.sync_ref_img = ImageTk.PhotoImage(Image.open(os.getcwd() + "/Pictures/sync_refresh.ico"))
        self.show_btn = tk.Button(master = self, image  =  self.sync_ref_img ,command = self.tree_update)
        self.search_btn = tk.Button(master = self, text = 'Search', command = self.archive_Search)
        #Packing 
        self.show_btn.pack()
        self.search_btn.pack()
        
