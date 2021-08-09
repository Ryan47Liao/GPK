import pandas as pd 
import  tkinter as tk 
from tkinter import ttk
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
import copy
import numpy as np
import io
import sys

#
from gpk_Score import *
from GPK_Notion import GPK_Notion
from Plan_load import *
     
D = {1:'monday',2:'tuesday',3:'wednesday',4:'thursday',5:'friday',6:'saturday',7:'sunday'}
D_rev = {v:k for k,v in D.items()}

def Fetch_Plain_test(rich_text):
    return Lst_to_str([i['plain_text'] for i in rich_text])

def Lst_to_str(Lst):
    out = ""
    for i in Lst:
        out += i 
    return out 

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
        step = 1/len(todo_stack)
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
        res = Profile.Notion.Query_DataBase(share_link,Parent_id)
        n_tasks =   len(res['results'])
        if True:
            df =self.DB_to_df(res,Profile)
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
            #->Fetching From Notion:
            #Push all into the todo list:
            for Gtask in List_of_Gtasks:
                #1.Determines Completion:
                try :
                    _Completed = list(df[df['ID'] == Gtask.ID]['Status'] == '✅Completed')[0]
                except IndexError:
                    _Completed = False 
                if _Completed:
                    #Check if Exist:
                    if Gtask.ID in Existing_Tasks_IDs:
                        print(f'Task {Gtask.name} completed')
                        #Delete the Original Task 
                        TODO.delete(Gtask.ID)
                        #Add it back with New One:
                        TODO.add_gpkTask(Gtask)
                        #Determine Quadrant 
                        Quadrant = 1 if Load.Task_Find(Gtask.ID) is None else 2
                        TODO.complete(Gtask.ID,Quadrant)
                        self.Completed.append((Gtask.ID,Gtask.name,f"Q{Quadrant}"))
                    else:
                        pass 
                else:#Not Completed
                    TODO.delete(Gtask.ID)
                    TODO.add_gpkTask(Gtask)
            #<-Pushing To Notion:
            Notion_IDs = [Gtask.ID for Gtask in List_of_Gtasks]
            Existing_Tasks = Df_to_Gtask(TODO.todos)
            for Gtask_Gpk in Existing_Tasks:
                if Gtask_Gpk.ID  not in Notion_IDs:
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
                self.description.set( f"Task ID {Gtask_Gpk.ID} pushed to notion" + '\n' + str(Gtask_Gpk))
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

    

class remember:
    def __init__(self,f,*args,**kargs):
        self._f = f 
        self.args = args
        self.kargs = kargs 
    
    def __call__(self):
        return self._f(*self.args,**self.kargs)
    
def Notion_sync(share_link,Profile,TODO,Misc = False):
    if share_link[:5] != 'https': #If id avaliable 
        Parent_id = share_link
        share_link = None
    else:#if sharelink avaliable
        Parent_id = None
    TODO = copy.deepcopy(TODO)
    Profile = copy.deepcopy(Profile)
    Load = Profile.todos.Load
###Program
    res = Profile.Notion.Query_DataBase(share_link,Parent_id)
    n_tasks =   len(res['results'])
    if tk.messagebox.askokcancel('Database Connection Established',
    f'You have {n_tasks} Non-Archived tasks,\n expected to be done in {2*n_tasks}\
    seconds do you wish to fetch all?'):
        df = Profile.Notion.DB_to_df(res)#,PG_show= True) #Show Progress
        List_of_Gtasks = Df_to_Gtask(df)
        #
        Completed = []
        Posted = []
    
    ###Sync:
        Existing_Tasks_IDs = list(TODO.todos['ID'])
        #->Fetching From Notion:
        #Push all into the todo list:
        for Gtask in List_of_Gtasks:
            #1.Determines Completion:
            if list(df[df['ID'] == Gtask.ID]['Status'] == '✅Completed')[0]:
                #Check if Exist:
                if Gtask.ID in Existing_Tasks_IDs:
                    print(f'Task {Gtask.name} completed')
                    #Delete the Original Task 
                    TODO.delete(Gtask.ID)
                    #Add it back with New One:
                    TODO.add_gpkTask(Gtask)
                    #Determine Quadrant 
                    Quadrant = 1 if Load.Task_Find(Gtask.ID) is None else 2
                    TODO.complete(Gtask.ID,Quadrant)
                    Completed.append((Gtask.ID,Gtask.name,f"Q{Quadrant}"))
                else:
                    pass 
            else:#Not Completed
                TODO.delete(Gtask.ID)
                TODO.add_gpkTask(Gtask)
        #<-Pushing To Notion:
        Notion_IDs = [Gtask.ID for Gtask in List_of_Gtasks]
        for Gtask_Gpk in Df_to_Gtask(TODO.todos):
            if Gtask_Gpk.ID  not in Notion_IDs:
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
                        Posted.append((Gtask_Gpk.ID,Gtask_Gpk.name))
                except:
                    print(f"Fail to Post Task {Gtask_Gpk.ID}")
            
        #Finally,Provide Feedback
        str_completed = ""
        str_Posted = ""
        for i in Completed:
            str_completed += f'{i}\n'
        for j in Posted:
            str_Posted += f'{j}\n'
        feedback = f"""
        <Sync Complete>
        The following tasks were completed:
        {str_completed}
        The following tasks were pushed to specified Notion Database:
        {str_Posted}
                   """
        tk.messagebox.showinfo('Sync Result:', feedback)
        for task_tuple in Completed:
            ID,Name,Qt = task_tuple[0],task_tuple[1],task_tuple[2]
            if int(Qt[1]) == 2:
                TODO.Load.complete(ID,tk_pop=True)
        
        if Misc:
            Profile.Q3_todo = TODO
        else:
            Profile.todos = TODO
            
        return Profile
    else:
        return Profile
        
        
def Plan_sep_to_dict(plan_dict):
    TEMP =  {'Family':[],'Health':[],'Personal Development':[],'Carrer':[]}
    for day in plan_dict:
        for sec in TEMP:
            TEMP[sec].append(plan_dict[day][sec])
    df = pd.DataFrame(TEMP,index=plan_dict.keys())
    return df


def SEC_Stat(Plan,sec = 'Time', agg = True, 
         sections = {1:'Health',2:'Family',3:'Personal Development',4:'Carrer',5:'other'}):
    "Return a Dict of days that Reflects the Time Distribution by Sections"
    if agg:
        TEMP = {'Family':0,'Health':0,'Personal Development':0,'Carrer':0}
    else:
        TEMP = {Day:{'Family':0,'Health':0,'Personal Development':0,'Carrer':0} for Day in Plan}
#     print(TEMP)
    for day in Plan:
        for task in Plan[day]:
            #print(task.ID)
            sec_id = int(task.ID.split("_")[1][1])
            section = sections[sec_id]
            if agg:
                TEMP[section] += float(eval(f'task.{sec}'))
            else:
                TEMP[day][section] += float(eval(f'task.{sec}'))
    return TEMP


def Progress_Stat(Profile,sec = 'Time'):
    #Step 1: Decide What's Done and What's NOT
    DONE,TODO,DONE_t,TODO_t = Plan_Sep(Profile,sec)
    #Step 2: Get Stats_OUT which is total time by Category
    Plan_Null = Fetch_plan_null(Profile.todos.Load_backup)
    Q2_ID = {Task.ID for Task in Plan_Null['Inbox']}
    for day in DONE:
        for task in DONE[day]:
            if task not in Q2_ID:
#                 print(task.ID)
                DONE[day].remove(task)
    #print(SEC_Stat(Plan_Null,sec))
    stats_out = list(SEC_Stat(Plan_Null,sec).values())
    #Step 3: Get Stats_In which is total time done by Category
    #print(SEC_Stat(DONE,sec))
    stats_In =  list(SEC_Stat(DONE,sec).values())
    return stats_In,stats_out
    

def Plan_Sep(Profile,sec = 'Time',RETURN_new_plan = False):
    "Seperate Plan distinguished by Completion Status"
    old_stdout = sys.stdout # Memorize the default stdout stream
    sys.stdout = buffer = io.StringIO()
    #
    DONE = {}
    TODO = {}
    DONE_t = {}
    TODO_t = {}
    Profile = copy.deepcopy(Profile)
    Analysis = DF_Analysis(Profile.todos.Archive)
    Archive = list(Analysis.Last_n_week(1)['ID'])
    ##
    Null_Plan = Fetch_plan_null(Profile.todos.Load_backup)
    Gtask_Find('S_G3-3_K1',Null_Plan)
    ## Update okr_plan based on Archive 
    Analysis = DF_Analysis(Profile.todos.Archive)
    df = Analysis.Last_n_week(1)
    Dict = dict(df.groupby('week_day').ID.apply(lambda x: [x]))
    #Get a set of IDs in the current plan
    planned_Task_IDs = set()
    for wkday in Profile.okr_plan:
        for Gtask in Profile.okr_plan[wkday]:
            planned_Task_IDs.add(Gtask.ID)
    for i in range(7):
        try:
#             print(D[i+1])
#             print(list(Dict[str(i)][0]))
            for ID in list(Dict[str(i)][0]):
                res = Gtask_Find(ID,Null_Plan)
                if res is not None and ID not in planned_Task_IDs:#If belong to Plan and NOT included
                    Profile.okr_plan[D[i+1]].append(res) 
        except KeyError:
            pass
    ##
    if RETURN_new_plan:
        return Profile.okr_plan
    for day in Profile.okr_plan:
        DONE[day] = []
        DONE_t[day] = 0
        TODO[day] = []
        TODO_t[day] = 0
        TASKs = Profile.okr_plan[day]
        for task in TASKs:
            if task.ID in Archive:
                #print(f"{task.Time}  done")
                DONE[day].append(task)
                DONE_t[day] += float(eval(f'task.{sec}'))
            else:
                #print(f"{task.Time} not done")
                TODO[day].append(task)
                TODO_t[day] += float(eval(f'task.{sec}'))
    ###
    sys.stdout = old_stdout
    return DONE,TODO,DONE_t,TODO_t

def Task_Find(Load,ID):
    def find(G_ID,category):
        nonlocal Load
        for task in eval(f'Load.WeekObjective.{category}'):
            if G_ID == task.Objective.split(':')[0]:
                return task
    Category = ID[0]
    G_ID = ID.split("_")[1]
    if Category == 'P':
        return find(G_ID,'Priority_Task')
    elif Category == 'S':
        return find(G_ID,'Special_Task')
    elif Category == 'R':
        return find(G_ID,'Recursive_Task')

def Gtask_Find(ID, Null_Plan = None, Profile = None):
    "Given Load Object and ID, return the corresponding Gtask"
    import sys
    assert Null_Plan is not None or Profile is not None, 'either Null_plan or Profile must not be none'
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    if Null_Plan is None:
        Null_Plan = Fetch_plan_null(Profile.todos.Load_backup)
    TEMP = Null_Plan['Inbox']
    sys.stdout = old_stdout # Put the old stream back in place
    for task in TEMP:
        #print(task.ID)
        if task.ID == ID:
            return task
        
def Plan_Legit(Load):
    def KR_Check(KR):
        ERROR = []
        KR_Dict = KR[1]
        for attr in ['difficulty','time','reward']:
            try:
                float(KR_Dict[attr])
            except:
                ERROR.append( (attr,KR_Dict[attr]) )
        return ERROR
    ERROR_ALL = []
    for Cat in ['Priority_Task','Special_Task','Recursive_Task']:
        try:
            CAT = eval(f"Load.WeekObjective.{Cat}")
            
            for task in CAT:
                for KR in task.KeyResults:
                    ERR = KR_Check(task.KeyResults[KR])
                    Name = task.KeyResults[KR][0]
                    if ERR != []:#Exist Error
                        ERROR_ALL.append(ERR)
                        print(f"""
        ERROR FOUND:
        ->Under Objective: {task.Objective}
            ->KR : {KR}
            Format Error: {ERR}
                               """)
        except AttributeError:
            print(f"!!!Category {Cat} not set up.!!!")
    instruction = """
        Potential Import Error occurred due to Wrong formats. 
        Please make sure that:
        1. All time are numbers 
        2. All difficulty are numbers 
        3. Standard Format: {time:xx,difficulty:xx,deadline:yyyy-mm-dd} is followed after each KR
                      """
    if len(ERROR_ALL) > 0:
        print(instruction)
        return False
    else:
        return True
    
def Df_to_Gtask(df):
    "Transform a GPK_todo.todos df into a list of Gtasks"
    OUT = []
    for idx in df.index:
        row = df.loc[idx]
        if 'ID' not in row:
            ID = f"S_G{random.randint(1,4)}-{random.randint(0,99)}_K{random.randint(0,99)}"
        else:
            ID = row['ID']
        if ID == "":
            ID = f"S_G{random.randint(1,4)}-{random.randint(0,99)}_K{random.randint(0,99)}"
        if 'Description' in row:
            des = row['Description']
        else:
            des = ''
        if 'Time' in row:
            time = row['Time']
        else:
            time = row['Hours']
        if 'Reward' not in row:
            Reward = 0 
        else:
            Reward = row['Reward']
        if 'Deadline' not in row:
            ddl = str(datetime.datetime.today().date())
        else:
            ddl = row['Deadline']
        Gtask = gpk_task(name = row['TaskName'], ID = ID , Reward = Reward ,
                Time = time, Difficulty = row['Difficulty'], Description = des,Deadline = ddl)
        OUT.append(Gtask)
    return OUT 

def Fill_date(Dict,start = None,base_line = 0):
    if start is None:
        start = str(Last_monday())
    most_recent = min(Dict.keys(),key = DATE)#lambda L:[DATE(i) for i in L])
    if DATE(start) <= DATE(most_recent):
        date = start 
        OUT = {start:base_line}
        while DATE(date) < DATE(most_recent):
            date = str(tmr(date)) #
            OUT[date] = base_line
        OUT = {**OUT,**Dict}
        return OUT
    else:
        return Dict
        

def wkday_to_date(wkday):
    "Convert a Wkday of this week into its date"
    DICT = {}
    date = str(Last_monday())
    while str(date) != str(Next_Sunday()):
        DICT[str(date)] = D[int(DATE(date).weekday()+1)]
        date = str(tmr(date))
    DICT[str(date)] = D[int(DATE(date).weekday()+1)]
    DICT_new = {k:v for v,k in DICT.items()}
    if wkday == 'Inbox':
        return str(yesterday(str(Last_monday())))
    return DICT_new[wkday]

def weekday_today(timezone = "Asia/Shanghai"):
    "Return the weekday number of today"
    from datetime import datetime
    from datetime import date
    from dateutil import tz

    timezone = tz.gettz(timezone)
    year = int(datetime.now(timezone).year)
    month = int(datetime.now(timezone).month)
    day = int(datetime.now(timezone).day)
    return(date(year, month, day).isocalendar()[2])
        
def Plan_to_df(Profile):
    plan = Profile.okr_plan
    try:
        print(f'Plan Loaded:\n {plan}')
    except:
        print(f"Plan Fail to Load,Reset Default Plan")
        plan = Profile.okr_plan = Fetch_plan_null(Profile.todos.Load)
    todo = Gpk_ToDoList()
    TEMP = []
    for sec in plan: 
        for Gtask in plan[sec]:
            todo.add_gpkTask(Gtask)
            TEMP.append(wkday_to_date(sec))
    todo.todos['Plan_at'] = TEMP
    return todo.todos

def OKRLOG_to_df(DayObject):
    out = {'Task_Type' : [],'Objective' : [],'Section': [], 'ID' : [], 'weight' : [], 'progress' : []}
    sections = ['Priority_Task','Special_Task','Recursive_Task']
    for sec in sections: 
        if eval(f"DayObject.{sec}") != []:
            for okr_task in eval(f"DayObject.{sec}"):
                out['Task_Type'].append(sec)
                out['Objective'].append(okr_task.Objective)
                out['weight'].append(okr_task.weight)
                out['progress'].append(okr_task.PG)
                ID = okr_task.Objective.split(':')[0]
                out['ID'] .append(f"{sec[0]}_{ID}_K-??")
                Sec = ID[1]
                out['Section'].append(Sec)
    return pd.DataFrame(out)
                

def print_collector(function,*args,**kargs):
    "Collect the stuff that's going to be printed"
    old_stdout = sys.stdout # Memorize the default stdout stream
    sys.stdout = buffer = io.StringIO()
    function(*args,**kargs)#Call Function
    sys.stdout = old_stdout # Put the old stream back in place
    whatWasPrinted = buffer.getvalue() # Return a str containing the entire contents of the buffer.
    return whatWasPrinted

def perfect_match(df,target)-> int :
    "Return the index of the best match of the df "
    Conditions = [df[idx] == target[idx] for idx in target.index]
    return np.argmax(sum([np.array(condition*1) for condition in Conditions]))


def df_to_Treeview(master, data:pd.core.frame.DataFrame, col_width = 120,col_minwidth = 25,col_anchor = tk.CENTER
              ,LABEL = False) :
    from tkinter import ttk
    if LABEL:
        label_text = "Parent"
        label_bool = tk.YES
        label_width = col_width
    else:
        label_text = ""
        label_bool = tk.NO
        label_width = 0
        
    my_tree = ttk.Treeview(master)
    #Define Our Columns
    my_tree ['columns'] = list(data.columns)
    #Format the columns & Create Headings (Bar at the very TOP):
    my_tree.column("#0",width = label_width, stretch = label_bool)
    my_tree.heading("#0", text = label_text)
    for col_name in list(data.columns):
        my_tree.column(col_name,anchor = col_anchor , width = col_width)
        my_tree.heading(col_name,text = col_name,anchor = col_anchor)
    #Add Data 
    iid = 0 #Item ID(UNIQUE)
    for row in range(data.shape[0]):
        data_i = list(data.iloc[row,])
        my_tree.insert(parent = "", index = 'end', iid = iid, text = label_text, values = data_i)
        iid += 1

    return my_tree    

def DATE(String):
    assert String is not None, 'Can not convert None into date'    
    STR = String.split("-")
    Y = int(STR[0])
    M = int(STR[1])
    D = int(STR[2])
    return(datetime.date(Y,M,D))
        
class DF_Search:
    def __init__(self,df):
        self.df = df 

    def Search_ID(self,id_pat,df = None):
        import re
        pat = re.compile(f"{id_pat}")
        return self.SEARCH('ID',lambda ID: pat.search(ID) is not None,df)
    
    def SEARCH(self,section,predict,df = None):
        if df is None:
            df = self.df 
        OUT = []
        for idx in df.index:
            entry = df.loc[idx][section]
            if predict(entry):
                OUT.append(idx)
        return df.loc[OUT]
    
    def Stack_Search(self,Sec_Preds: [(str,str)]):
        "Perform Search in Sequence"
        df = self.df 
        for sec,pred in Sec_Preds:
            df = self.SEARCH(sec,pred,df)    
        return df 
    
def GAP_Filler(dates,freq):
    "Take a list of date Strs (Potentially Gapped),and return a patched one, assuming the are in dec order (Recent to Last)"
    og_dates = copy.copy(dates)
    og_freq = copy.copy(freq)
    def yesterday(date_str):
        return (DATE(date_str) - datetime.timedelta(days = 1))
    
    def tmr(date_str):
        return (DATE(date_str) + datetime.timedelta(days = 1))
    
    def ascending(dates):
        out = [DATE(dates[idx]) >= DATE(dates[idx+1 ]) for idx in range(len(dates)-1)]
        return all(out)
    
    def decending(dates):
        out = [DATE(dates[idx]) <= DATE(dates[idx+1 ]) for idx in range(len(dates)-1)]
        return all(out)  
     
    if len(dates) == 1:
        return dates,freq
    
    if ascending(dates):
        print('Dates are Backward Ordered')
        NEXT = yesterday 
    elif decending(dates):
        NEXT = tmr
        print('Dates are Forward Ordered')
    else:
        raise Exception(f"The dates are not ordered. {dates}")

    
    dates_out = []
    freq_out = []
    for idx in range(len(dates)-1):
        gap = DATE(dates[idx]) - DATE(dates[idx+1])
        date = dates[idx]
        dates_out.append(date)
        freq_out.append(freq[idx])
        for _ in range(abs(gap.days)-1):
            date = str(NEXT(date))
            dates_out.append(date)
            freq_out.append(0)
    dates_out.append(og_dates[-1])
    freq_out.append(og_freq[-1])
    return dates_out,freq_out

class DF_Analysis(DF_Search):
    def __init__(self,df,figsize = (5,10)):
        super().__init__(df)
        self.fig = Figure(figsize =figsize , dpi = 100)
    
    def Set_df(self,df):
        self.df = df 
        
        
    def Last_n_day(self,n,df = None,Group = 'date_done'):
        return self.SEARCH(Group,lambda date: DATE(date) >= (datetime.datetime.now() - datetime.timedelta(days = n)).date(),df = df)
    
    def Last_n_week(self,n,df = None,Group = 'date_done'):
        #1.Identify Last Monday,Count as last 1 week:
        monday = str(Last_monday())
        if n <= 1:
            return self.SEARCH(Group,lambda date: DATE(date) >= DATE(monday),df = df)
        else:
            n = n-1 
        #2.Fetch the rest 
        return self.SEARCH(Group,lambda date: DATE(date) >= (DATE(monday) - datetime.timedelta(weeks = n)),df = df)
    
    def Last_n_month(self,n,df = None,Group = 'date_done'):
        return self.SEARCH(Group,lambda date: DATE(date) >= (datetime.datetime.now() - datetime.timedelta(days = n*30)).date(),df = df)
    
    def fig_preview(self,fig = None, geom = '1000x1000'):
        if fig is None:
            fig = self.fig
        window = tk.Tk()
        window.geometry(geom)
        canvas = FigureCanvasTkAgg(fig,window)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        window.mainloop()
        
    def Plot_DateFrame(self, n = None, sec = 'Time', df = None ,dim = 111,title = None,
                       short = False, Group = 'date_done', 
                       key = lambda L: [DATE(i) for i in L]):
        if df is None:
            df = copy.deepcopy( self.df )  
        df = copy.deepcopy(df)
        plot_id = str(dim)[-1]
        if Group == 'date_done':
            DateFrame = 'Day'
        else:
            DateFrame = Group
        if title is None:
            title = f'{sec} distribution for the Last {n} {DateFrame}s'
        exec(f"plot{plot_id} = self.fig.add_subplot(dim,title = title)") 
        ###
        #
        if n is not None:
            Last_n_df = self.Last_n_day(n,df,Group)
        else:
            Last_n_df = df 
        #print(Last_n_df)
        temp = eval(f"Last_n_df.groupby(Group).{sec}.agg(sum)")
        res = pd.DataFrame(temp).sort_values(by = Group, key = key,ascending = True)
        #Finally:
        dates = [i for i in res.index]
        freq = res[sec]
        dates,freq = GAP_Filler(dates,freq)#Fill the potential Gaps
        if short:
            dates = [date.split('-')[1]+'.'+date.split('-')[2] for date in dates]
        eval(f'plot{plot_id}.bar(dates,freq)')
        eval(f'plot{plot_id}.set_xlabel(Group)')
        eval(f'plot{plot_id}.set_ylabel(sec)')
        
        
    def Plot_Date(self, n = None, sec = 'Time', df = None ,dim = 111,title = None,short = False,
                  Group = 'date_done'):
        if df is None:
            df = copy.deepcopy( self.df )  
        df = copy.deepcopy(df)
        plot_id = str(dim)[-1]
        if title is None:
            title = f'{sec} distribution for the Last {n} days'
        exec(f"plot{plot_id} = self.fig.add_subplot(dim,title = title)") 
        #
        if n is not None:
            Last_n_df = self.Last_n_day(n,df,Group)
        else:
            Last_n_df = df 
        #print(Last_n_df)
        temp = eval(f"Last_n_df.groupby(Group).{sec}.agg(sum)")
        res = pd.DataFrame(temp).sort_values(by = 'date_done', key = lambda L: [DATE(i) for i in L],ascending = True)
        #print(res)
        #Finally:
        dates = [i for i in res.index]
        freq = res[sec]
        dates,freq = GAP_Filler(dates,freq)#Fill the potential Gaps
        if short:
            dates = [date.split('-')[1]+'.'+date.split('-')[2] for date in dates]
        eval(f'plot{plot_id}.bar(dates,freq)')
        eval(f'plot{plot_id}.set_xlabel("Date")')
        eval(f'plot{plot_id}.set_ylabel(sec)')
    
    def Plot_Week(self,n = None, sec = 'Time', df = None,dim = 111 ,title = None,Group = 'Week'):
        def Cal_Week(Date_0,date):
            delta = DATE(Date_0) - DATE(date)
            return -round((delta.days/7))
        n = n-1
        plot_id = str(dim)[-1]
        if title is None:
            title = f'{sec} distribution for the Last {n} weeks'
        if df is None:
            df = copy.deepcopy( self.df ) 
        df = copy.deepcopy(df) 
        ###
        exec(f"plot{plot_id} = self.fig.add_subplot(dim,title = title)") 
        ###
        if n is not None:
            Last_n_df = self.Last_n_week(n,df)
        else:
            Last_n_df = df 
        
        
        Most_recent = df.sort_values(by = 'date_done', key = lambda L: [DATE(i) for i in L],ascending = False).iloc[0]['date_done']
        Last_n_df['Week'] = [Cal_Week(Most_recent, date) for date in list(Last_n_df['date_done'])] 
        
        temp = eval(f"Last_n_df.groupby(Group).{sec}.agg(sum)")
        res = pd.DataFrame(temp).sort_values(by = 'Week', key = lambda L: [int(i) for i in L],ascending = False)
        #Finally:
        weeks = [i for i in res.index]
        freq = res[sec]
#         weeks,freq = GAP_Filler(dates,freq)#Fill the potential Gaps
        eval(f'plot{plot_id}.bar(weeks,freq)')
        eval(f'plot{plot_id}.set_xlabel("Week")')
        eval(f'plot{plot_id}.set_ylabel(sec)')
    
    def Plot_Month(self,n = None, sec = 'Time', df = None,dim = 111,title = None,Group = 'Month'):
        def Cal_Month(Date_0,date):
            from math import floor
            year_d = DATE(Date_0).year - DATE(date).year
            month_d = DATE(Date_0).month - DATE(date).month
            delta = -(year_d*12 + month_d)
            return delta
        if title is None:
            title = f'{sec} distribution for the Last {n} months'
        n = n-1
        plot_id = str(dim)[-1]
        if df is None:
            df = copy.deepcopy( self.df )  
        df = copy.deepcopy(df)
        ###
        exec(f"plot{plot_id} = self.fig.add_subplot(dim,title = title)") 
        ###
        if n is not None:
            Last_n_df = self.Last_n_month(n,df)
        else:
            Last_n_df = df 
        Most_recent = df.sort_values(by = 'date_done', key = lambda L: [DATE(i) for i in L],ascending = False).iloc[0]['date_done']
        Last_n_df['Month'] = [Cal_Month(Most_recent, date) for date in list(Last_n_df['date_done'])] 
        
        temp = eval(f"Last_n_df.groupby(Group).{sec}.agg(sum)")
        res = pd.DataFrame(temp).sort_values(by = 'Month', key = lambda L: [int(i) for i in L],ascending = False)
        #Finally:
        months = [i for i in res.index]
        freq = res[sec]
#         weeks,freq = GAP_Filler(dates,freq)#Fill the potential Gaps
        eval(f'plot{plot_id}.bar(months,freq)' )
        eval(f'plot{plot_id}.set_xlabel("Month")')
        eval(f'plot{plot_id}.set_ylabel(sec)')
    
    def Plot_Sec(self, n = None , time_frame = 'Day',sec = 'Time', 
                 shreshold = 0.2, title = None,df = None,
                 dim = 111,Group = 'date_done', plt_method = None,kargs = {}):
        """
        -n: Number of time_frame to be plotted 
        -time_frame: type of time_frame, Day,Week,Month
        -sec: Section of Statistic: Time/Reward
        -shreshold: The lowest percentage required to cause the least section to explode
        """
        if df is None:
            df = copy.deepcopy( self.df )  
        df = copy.deepcopy(df)
        plot_id = str(dim)[-1]
        ###
        if title is None:
            title = f'{sec} distribution among sections for the past {n} {time_frame}s'
        exec(f"plot{plot_id} = self.fig.add_subplot(dim,title = title)") 
        time_frame = time_frame.lower()
        if n is not None:
            Last_n_df = eval(f'self.Last_n_{time_frame}(n,df)')
        else:
            Last_n_df = df 
        Last_n_df['Task Category'] = [str(ID).split("_")[1][1] for ID in Last_n_df['ID']]
        temp = pd.DataFrame(eval(f'Last_n_df.groupby(by = "Task Category").{sec}.agg(sum)'))#pd.DataFrame
        temp_Dict = {Goal_sec:t for Goal_sec,t in zip([i for i in temp.index],temp[sec])}
        Labs = ['Health','Family','Personal Development','Career']
        X = {1:0,2:0,3:0,4:0}
        for goal_sec in temp_Dict:
            X[int(goal_sec)] = temp_Dict[goal_sec]/sum(temp_Dict.values())
        #print(X)
        explode = [True if x == min(X.values()) and float(x) < shreshold else False for x in X.values()]
        #Labs = [Lab + '\n' + str(Percentage)+"%" for Lab,Percentage in zip(Labs,X)]
        if plt_method is None:
            eval(f'plot{plot_id}.pie(X.values(), explode = explode,labels = Labs, autopct = lambda value: str(round(value,2))+"%")') 
        else:
            X_new = list(X.values())
            kargs_new = {}
            for k,v in kargs.items():
                kargs_new[k] = eval(v)
            plt_method(**kargs_new)
            
    def get_fig(self):
        return self.fig 
    
    def Rest_fig(self, figsize = (10,5)):
        self.fig = plt.Figure(figsize = figsize)
        
    def Plot_Score(self,Loaded,Scores = None, df = None, dim =111,title = 'Score Projection',
                  grade_cutoff = {"D":(55,'r'),"C":(65,'y'),"B":(75,'b'),"A":(85,'g'),"S":(95,'m')}):
        if df is None:
            df = self.df
        if Scores is None:
            Scores = Get_Scores(df,Loaded) #A dictionary of datetime and scores
        #print(Scores)
        Scores = Fill_date(Scores)
        #print(Scores)
        LST = list(Scores.values())
        plot1 = self.fig.add_subplot(dim,title = title)
        #
        Trend = trend(list(LST))
        Now = now(list(LST))
        #Plotting
        WEEKDAYS = ["Mon","Tue","Wed","Thur","Fri","Sat","Sun"]
        plot1.plot(WEEKDAYS,Now,label = "NOW")
        plot1.plot(WEEKDAYS,Trend,label = "Projection",linestyle='dashdot')
        for grade in grade_cutoff.keys():
            plot1.plot(WEEKDAYS,constant_line(grade_cutoff[grade][0]),label = grade,linestyle='dashed',color = grade_cutoff[grade][1])
        plot1.legend()
            
            
def Fetch_plan_null(Loaded , Sections =['Priority_Task','Special_Task']):
    if not isinstance(Sections,list):
        Sections = [Sections]
    #Return a Plan from a Null Load file 
    D = {1:'monday',2:'tuesday',3:'wednesday',4:'thursday',5:'friday',6:'saturday',7:'sunday'}
    OUT = {'Inbox':[]}
    for day in D.values():
        OUT[day] = []
    for sec in Sections:
        for Objective in eval(f'Loaded.WeekObjective.{sec}'):
            O_ID = Objective.Objective.split(":")[0]
            for KR in Objective.KeyResults:
                task_id = f"{sec[0]}_{O_ID}_{KR}"
                task_name = Objective.KeyResults[KR][0]
                temp = Objective.KeyResults[KR][1]
                try:
                    ddl = temp['deadline']
                    print(f"[Fetch_plan_null] Deadline identified:{ddl} for task {task_id}")
                except:
                    ddl = None 
                    print(f'[Fetch_plan_null] Fail to fetch deadline for task {task_id}')
                Gtask = gpk_task(name = task_name,ID=task_id,
                                Difficulty = temp['difficulty'],Time = temp['time'],
                                Reward = temp['reward'],Deadline = ddl,
                                Description = "")
                OUT['Inbox'].append(Gtask)
    return OUT

class Gpk_ToDoList:
    def __init__(self):
        self.todos = pd.DataFrame({"ID":[ ],"TaskName":[ ],"Reward":[ ],
                            "Time":[ ],"Difficulty":[ ],
                            "ObjectID":[ ],"KeyResult ID":[ ],"Task Category":[ ]})
        self.Archive = pd.DataFrame()
        self.task_descriptions = {}
    
    def reset_des(self):
        self.task_descriptions = {}
        print("Task Descriptions Rest")
                
    def add(self,task_name,task_ID,task_time,task_diff,task_des,ddl = None, RETURN = False):
        "task_ID: S_G4-3_K1" #Special/Recurrent/Priority_Goal#_KeyResult#
        try:
            if task_ID  in list(self.todos['ID']):
                print("ERROR,ID Already Exsit")
                return 
        except KeyError: #When it's empty 
            print("Empty")
        reward = self.Reward(task_time,task_diff) #calculate reward based on tasktime and difficulty
        Category = task_ID.split("_")[1].split("-")[0][1] #Fetch Task Category Based on Task_ID format 
        KR_ID = task_ID.split("_")[2] 
        O_ID = task_ID.split("_")[1]
        task = pd.DataFrame({"ID":[task_ID],"TaskName":[task_name],"Reward":[reward],
                            "Time":[task_time],"Difficulty":[task_diff],
                            "ObjectID":[O_ID],"KeyResult ID":[KR_ID],"Task Category":[Category],
                            "Deadline":[ddl]})
        try:
            self.task_descriptions[task_ID] = task_des
        except:
            self.reset_des() 
            #self.task_descriptions[task_ID] = task_des #RESET
             
        if RETURN:
            return
        else:
            self.todos = self.todos.append(task, ignore_index=True)
            
    def add_gpkTask(self,Gtask):
        self.add(task_name = Gtask.name,task_ID = Gtask.ID,
                 task_time = float(Gtask.Time) ,
                 task_diff = float(Gtask.Difficulty),
                 task_des = Gtask.Description)
      
    
    def Reward(self,time,difficulty):
        "Return Rewards Based on Time and Difficulty"
        time_lower_bound = 0.35
        time_upper_bound = 5
        difficulty_upper_bound = 10
        if time < time_lower_bound:
            time = time_lower_bound
        if time > time_upper_bound:
            time = time_upper_bound
        if difficulty > difficulty_upper_bound:
            difficulty = difficulty_upper_bound
        difficulty = abs(difficulty)
        reward = 3*(time**0.6*difficulty**0.4) + random.choice([-0.5,0,0.5,1,1.5,2])
        return(round(reward))
    
    def idx_reset(self,df):
        df = df.reset_index()
        try:
            df =  df.drop('level_0',axis = 1)
        except KeyError:
            pass
        try:
            df =  df.drop(['index'],axis = 1)
        except KeyError:
            pass
        return df
    
        
    def delete(self,task_ID):
        "Delete A Task"
        idx = self.todos.loc[self.todos['ID'] == task_ID].index 
        self.todos = self.todos.drop(idx)
        self.todos = self.idx_reset(self.todos)
        try:
            self.task_descriptions.pop(task_ID)
        except Exception as e:
            print(f'ERROR!ID {task_ID} does not exist.')
            print(f"Exception Raised:{e}")
        
        
    def edit(self,task_name,task_ID,task_time,task_diff,task_des,ddl):
        "Edit An Existing Task"
        self.delete(task_ID)
        self.add(task_name,task_ID,task_time,task_diff,task_des,ddl)
        
    def complete(self,task_ID):
        time_stamp = str(datetime.datetime.now())
        date_today = str(datetime.datetime.now().date())    
        week_day_today = str(datetime.datetime.now().weekday())
        og_task = copy.deepcopy(self.todos.loc[self.todos['ID'] == task_ID])
        og_task.insert(8,"date_done",[date_today])
        og_task.insert(9,"week_day",[week_day_today])
        og_task.insert(10,"time_stamp",[time_stamp])
        try:
            og_task.insert(11,"description",[self.task_descriptions[task_ID]])
        except:
            pass
        self.Archive = self.Archive.append(og_task)
        self.Archive = self.idx_reset(self.Archive)
        self.delete(task_ID)
   

if __name__ == '__main__':
    # dates = ['2021-07-04', '2021-07-05', '2021-07-06', '2021-07-09', '2021-07-11']
    # freq = [1,4,6,2,5]
    # print( GAP_Filler(dates,freq) )
    # dates = ['2021-07-02','2021-06-30','2021-06-20']
    # print( GAP_Filler(dates,freq) )
    # # Loaded = Load('OKRLOG_S3_W1.docx')
    # # Loaded.get_week_objective()
    # # OUT = Fetch_plan_null(Loaded)
    # # print(OUT)
    # print(weekday_today())
    
    
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