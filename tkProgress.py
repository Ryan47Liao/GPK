import tkinter as tk 
from time import sleep
from tkinter import ttk
import pandas as pd 
import copy
import pickle
#
from Plan_load import *
from gpk_utilities import *
    
class TkProgress(tk.Toplevel):
    def __init__(self,
                 title:str,
                 header: str,
                 description:str,
                 f_name:'function',
                 kargs: {},
                 step = 0.01 , rps = 10, 
                 base = 40, blank = "  ", 
                 font = ('times new roman',14),
                 cnf = {}):
        #Initialize
        super().__init__( **cnf )
        #Set Up
        self.title( title ) 
        self.geometry(f'{16*base}x{9*base}')
        #Attributes 
        self.count = 0
        self.step = step 
        self.font = font
        self.header = tk.StringVar()
        self.header.set(header)
        self.description = tk.StringVar()
        self.description.set(description)
        self.rps = rps 
        #Drawing
        self._draw()
        #UPDATE:
        self.UPDATE(f_name,kargs)
        
    def UPDATE(self,_f,kargs):
        f = eval(f'self.{_f}')
        f(**kargs)
        
    def todo_IMPORT(self,PROFILE,PUSHLIST):
        self.header.set("Pushing Tasks to Notion...")
        Succ = [] 
        Fail = []
        share_link = PROFILE.Notion.GPKTODO_LinkID
        if share_link[:5] != 'https':
            Parent_id = share_link
        else:
            Parent_id = None
        for Gtask in PUSHLIST: #A Great Place to add Progress Bar 
            for attr in ['Time','Reward','Difficulty']:
                exec(f"Gtask.{attr} = float(Gtask.{attr})")
            Description = Gtask.Description if Gtask.Description != "" else None
            #Check For Deadline:
            Gtask.Deadline = str(datetime.datetime.today().date()) if Gtask.Deadline is None else Gtask.Deadline
            res = PROFILE.Notion.Post_Gtask(Gtask,Description = Description, 
                                        share_link = share_link,
                                        Parent_id = Parent_id,Misc = False)
            if res['object'] == 'page':
                print(f"Task ID {Gtask.ID} pushed to notion")
                Succ.append((Gtask.ID,Gtask.name))
            else:
                Fail.append((Gtask.ID,Gtask.name))
            ###Update Progress 
            self.description.set( f"Task ID {Gtask.ID} pushed to notion" + '\n' + str(Gtask))
            self.count += 1/len(PUSHLIST)
            self.PG_ref()
            
        #Finally,Provide Feedback
        str_succ = ""
        str_fail = ""
        for i in Succ:
            str_succ += f'{i}\n'
        for j in Fail:
            str_fail += f'{j}\n'
        feedback = f"""
        -The following tasks were Pushed to Notion:
            {str_succ}
        -The following tasks Was UNABLE to be Pushed to Notion:
            {str_fail}
                   """
        #tk.messagebox.showinfo('Push Result:', feedback)
        self.header.set("--Push Complete--")
        self.description.set(feedback)
        self.PG_ref()
        
    def DB_to_df(self,tasks_res,Profile):
        _Dict = {'TaskName' : [],'Description':[]}
        ###
        Properties = set()
        for i in [task['properties'].keys() for task in tasks_res['results']]:
            for j in i:
                Properties.add(j)
        ### Stack 
        def temp_f(task,PRINT = True):
            nonlocal _Dict
            task_name = Lst_to_str([i['plain_text'] for i in task['properties']['Name']['title']])
            if task_name != "":
                if PRINT:
                    print(task_name)
                _Dict['TaskName'].append(task_name)
                D_temp = task['properties']
                #Task Properties:
                for p in Properties:
                    if p in D_temp:
                        if D_temp[p]['type'] == 'number':
                            content = D_temp[p]['number']
                            try:
                                content = float(content)
                            except:
                                content = 0
                        elif D_temp[p]['type'] == 'select':
                            content = D_temp[p]['select']['name']
                        elif D_temp[p]['type'] == 'rich_text':
                            content = Fetch_Plain_test(D_temp[p]['rich_text'])
                        elif D_temp[p]['type'] == 'date':
                            start = D_temp[p]['date']['start']
                            end = D_temp[p]['date']['end']
                            content = start
                        else:
                            content = None 
                        if content is not None:
                            if p not in _Dict:
                                _Dict[p] = [content]
                            else:
                                _Dict[p].append(content)
                            if PRINT:
                                print(f'{p}:{content}')
                    else:
                        if p not in _Dict:
                            _Dict[p] = [None]
                        else:
                            _Dict[p].append(None)
                #Task Details 
                task_detail = Profile.Notion.Get_Block_children(block_id= task['id'])
                str_detail = ""
                if 'results' in task_detail:
                    for todo in task_detail['results']:
                        det_type = todo['type']
                        try:
                            all_contest = [i['plain_text'] for i in todo[det_type]['text']]
                            text = Lst_to_str(all_contest)
                            status = ""
                            try:
                                checked = todo['to_do']['checked']
                                status = '[√]' if checked  else '[X]'
                            except:
                                pass
                            str_detail += (f'\t-{status} {text}\n')
                        except:
                            pass
                _Dict['Description'].append(str_detail)
                str_detail = ""
            
        ###
        todo_stack = []
        for task in tasks_res['results']:
            todo_stack.append(remember(temp_f,task))
        try:
            step = 1/len(todo_stack)
        except ZeroDivisionError: 
            pass 
        ###Execution:
        for f in todo_stack:
            f()
#Update Progress 
            self.header.set('Step 2: Fetching data from NOTION\n')
            self.description.set( str( pd.DataFrame(_Dict).iloc[-1] ))
            self.count += step
            self.PG_ref()
        return pd.DataFrame(_Dict)
       

    def PG_ref(self):
        self.PG_widget['value'] = self.count*100
        self.pg_text.set(f"Current Progress: {self.PG_widget['value']}%")
        self.update()
        
    def Notion_Sync(self,share_link,Profile,callback,Misc = False):
        if share_link[:5] != 'https': #If id avaliable 
            Parent_id = share_link
            share_link = None
        else:#if sharelink avaliable
            Parent_id = None
    
        Profile = copy.deepcopy(Profile)
        if Misc:
            TODO = Profile.Q3_todo
        else:
            TODO = Profile.todos
        Load = Profile.todos.Load
###Program:
        self.header.set('Step 1: Connecting to Notion Database    \n')
        self.description.set('Establishing Connection...')
        self.PG_ref()
        res = Profile.Notion.Query_DataBase(share_link,Parent_id)
        self.count = 1
        self.PG_ref()
        n_tasks =   len(res['results'])
        if True:
            self.count = 0
            df = self.DB_to_df(res,Profile)
            try:
                df['Hours'] = [0 if math.isnan(t) else t for t in df['Hours'] ] #Fix Nans 2021-08-25
            except KeyError: #Empty case when notion db is empty 2021-09-14
                pass 
            #Refresh Page
            self.header.set( 'Step 3: Pushing Tasks to Notion from GPK')
            self.description.set("")
            self.count = 0
            self.PG_ref()
            List_of_Gtasks = Df_to_Gtask(df)
            self.Completed = []
            self.Posted = []
                
        ###Sync:
            Existing_Tasks_IDs = list(TODO.todos['ID'])
            Existing_Tasks_Names = list(TODO.todos['TaskName'])
            #->Fetching From Notion:
            #Push all into the todo list:
            def delete_by_name(TODO,name):
                for idx in TODO.todos.index:
                    row = TODO.todos.iloc[idx]
                    if name == row['TaskName']:
                        TODO.delete(row['ID'])
                        break
            def check_exsit(Gtask):
                if not Misc:
                    return Gtask.ID in Existing_Tasks_IDs
                else:
                    return Gtask.name in Existing_Tasks_Names
            for Gtask in List_of_Gtasks:
                #1.Determines Completion:
                try :
                    if not Misc:
                        _Completed = list(df[df['ID'] == Gtask.ID]['Status'] == '✅Completed')[0]
                    else:
                        _Completed = list(df[df['TaskName'] == Gtask.name]['Status'] == '✅Completed')[0]
                except IndexError:
                    _Completed = False 
                if _Completed:
                    #Check if Exist:
                    if check_exsit(Gtask):
                        print(f'Task {Gtask.name} completed')
                        #Delete the Original Task 
                        if Misc:
                            delete_by_name(TODO,Gtask.name)
                        else:
                            TODO.delete(Gtask.ID)
                        #Add it back with New One:
                        TODO.add_gpkTask(Gtask)
                        #Determine Quadrant 
                        if not Misc:
                            Quadrant = 1 if Load.Task_Find(Gtask.ID) is None else 2
                        else:
                            Quadrant = 3
                        TODO.complete(Gtask.ID,Quadrant)
                        self.Completed.append((Gtask.ID,Gtask.name,f"Q{Quadrant}"))
                    else:
                        pass 
                else:#Not Completed
                    if Misc: #Delete by Name
                        delete_by_name(TODO,Gtask.name)
                    else:
                        TODO.delete(Gtask.ID)
                    TODO.add_gpkTask(Gtask)
                    
            #<-Pushing To Notion:
            if not Misc:
                Notion_IDs = [Gtask.ID for Gtask in List_of_Gtasks]
            else:
                Notion_Names = [Gtask.name for Gtask in List_of_Gtasks]
            Existing_Tasks = Df_to_Gtask(TODO.todos)
            def condition(Gtask_Gpk):
                if Misc:
                    return Gtask_Gpk.name  not in Notion_Names
                else:
                    return Gtask_Gpk.ID  not in Notion_IDs
                
            for Gtask_Gpk in Existing_Tasks:
                if condition(Gtask_Gpk):
                    try:
                        Description = TODO.task_descriptions[Gtask_Gpk.ID]
                    except:
                        Description = ""
                    res = Profile.Notion.Post_Gtask(Gtask_Gpk,Description = Description, 
                                                    share_link = share_link,
                                                    Parent_id = Parent_id,Misc = Misc)#If True,Push as Misc
                    try:
                        if res['object'] == 'page':
                            print(f"Task ID {Gtask_Gpk.ID} pushed to notion")
                            self.Posted.append((Gtask_Gpk.ID,Gtask_Gpk.name))
                    except:
                        print(f"Fail to Post Task {Gtask_Gpk.ID}")
                #Updating:
                try:
                    self.description.set( f"Task ID {Gtask_Gpk.ID} pushed to notion" + '\n' + str(Gtask_Gpk))
                except:
                    self.description.set('--DISPLAY ERROR--')
                self.count += 1/len(Existing_Tasks)
                self.PG_ref()
                
            #Finally,Provide Feedback
            str_completed = ""
            str_Posted = ""
            for i in self.Completed:
                str_completed += f'{i}\n'
            for j in self.Posted:
                str_Posted += f'{j}\n'
            feedback = f"""
            The following tasks were completed:
            {str_completed}
            The following tasks were pushed to specified Notion Database:
            {str_Posted}
                       """
            self.header.set('---SYNC COMPLETE---')
            self.description.set(feedback)
            self.update()
            
            for task_tuple in self.Completed:
                ID,Name,Qt = task_tuple[0],task_tuple[1],task_tuple[2]
                if int(Qt[1]) == 2:
                    TODO.Load.complete(ID,tk_pop=True)
            
            if Misc:
                Profile.Q3_todo = TODO
            else:
                Profile.todos = TODO
    
        else:
            pass 
        #Finally:Update Profile
        try:
            callback(Profile,Update = True)
            print('Profile Updated')
        except:
            self.header.set("ERROR,Fail to Save Changes")
            self.description.set("ERROR! Profile not saved.")
            self.update()
            
     
    def _draw(self):
        self._RUN = tk.IntVar()
        self._RUN.set(1)
        #Header
        header = tk.Label(self,textvariable = self.header, font = self.font)
        header.pack()
        #Progress Bar 
        # self.PG = tk.StringVar()
        # self.PG.set(progress(0))
        # self.PG_widget = tk.Label(self,textvariable = self.PG)
        
        self.PG_widget = ttk.Progressbar(
                                self,
                                orient='horizontal',
                                mode='determinate',
                                length=280
                            )
        self.PG_widget.pack()
        #label
        self.pg_text = tk.StringVar()
        self.pg_text.set(f"Current Progress: {self.PG_widget['value']}%")
        self.pg_lab = tk.Label(self,textvariable = self.pg_text)
        self.pg_lab.pack()
        #Add description:
        description = tk.Label(self,textvariable = self.description, font = self.font)
        description.pack(padx = 10, pady = 10)

    

# class tkProgress(tk.Tk):
#     def __init__(self, title, description, todo_stack : list= None
#                 , auto_update = False, Control = False,
#                  step = 0.01 , rps = 10, 
#                  base = 40, blank = "  ", 
#                  font = ('times new roman',14),
#                  cnf = {} ):
#         try:
#             self._Stack = (f for f in todo_stack)
#             self.total_f = len(todo_stack)
#         except:
#             self._Stack = None
#         self.step = step 
#         self.font = font
#         self.description = description
#         self.rps = rps 
#         super().__init__( **cnf )
#         self.geometry(f'{16*base}x{9*base}')
#         self.title( title ) 
#         #DRAW
#         self._draw(Control)
#         #Pre-Set
#         self.Reset()
#         #Finally;
#         if todo_stack is not None:
#             self.after(1000, self._update)
#
#     def Reset(self):
#         self.count = 0
#         self.PG.set(progress(0))
#
#     def _update(self,step = None, auto_update = False):
#         if self._Stack is not None:
#             try:
#                 next_f = next(self._Stack)
#                 step = 1/self.total_f
#                 next_f()
#                 self.count += step
#                 #print(self.count)
#                 self.PG.set( progress(self.count) )
#                 #print(self.PG.get())
#                 self.after( 1, lambda: self._update(step) )
#             except StopIteration:
#                 # sleep(1)
#                 # self.destroy() 
#                 pass
#         else:
#             if step is None:
#                 step = self.step
#             if self.count < 1: 
#                 self.count += step
#                 #print(self.count)
#                 self.PG.set( progress(self.count) )
#                 #print(self.PG.get())
#             else:
#                 auto_update = False
#             if auto_update and self._RUN.get():
#                 self.after(int(1000/self.rps), lambda:self._update(step,auto_update))
#
#     def _draw(self,Control):
#         self._RUN = tk.IntVar()
#         self._RUN.set(1)
#         #Add description:
#         description = tk.Label(self,text = self.description, font = self.font)
#         description.pack(padx = 10, pady = 10)
#         #Progress Bar 
#         self.PG = tk.StringVar()
#         self.PG_widget = tk.Label(self,textvariable = self.PG)
#         self.PG_widget.pack()
#         if Control:
#             #Start Update
#             self.autoUpdate_btn = tk.Button(self,text = 'Start Auto',
#                                         command = lambda: self._update(auto_update=True))
#             self.autoUpdate_btn.pack(padx = 10, pady = 10)
#             #Allow Refresh:
#             self.Run_ckbx = tk.Checkbutton(self,text = 'Auto Update', variable = self._RUN)
#             self.Run_ckbx.pack()
#             #Update Manually:
#             self.Update_btn = tk.Button(self,text = 'Update',
#                                         command = self._update)
#             self.Update_btn.pack(padx = 10, pady = 10)
#             #Reset Btn 
#             self.Reset_btn = tk.Button(self,text = 'Reset',
#                             command = self.Reset)
#             self.Reset_btn.pack(padx = 10, pady = 10)
#             #Destroy Btn
#             Destory = tk.Button(self,text = 'Destroy', command = self.destroy)
#             Destory.pack()
            
if __name__ == '__main__':
    ###Progress Test:
    #1:Prep Stack
    share_link = 'https://www.notion.so/a2fd97ec08e4471682a0cd908be2c530?v=76841c16ed47444d9d29f09acba1a6de'
    #'https://www.notion.so/511539815e434eafad25f329ed55b574?v=24f7815ecbd249819744d7fbcd6c9828'
    User_name = 'Leo_TEST'##
    file_path = f"D:\GPK\gpk_saves\\{User_name}_user_file.gpk"
    with open(file_path,'rb') as INfile:
        Profile = pickle.load(INfile)
    kargs = {"share_link":share_link,"Profile":Profile ,"callback":None , 'Misc':False}
    #2:
    root = tk.Tk()
    TkProgress('Test1','Some Description','Yo','Notion_Sync',kargs)
    root.mainloop()