import docx
import random 
from dateutil import tz
import requests
import urllib, json
from time import sleep
from tkinter import messagebox

def Lst_to_str(Lst):
    out = ""
    for i in Lst:
        out += i 
    return out 

def weekday_today(timezone = tz.gettz("Asia/Shanghai")):
    from datetime import datetime
    from datetime import date
    year = int(datetime.now(timezone).year)
    month = int(datetime.now(timezone).month)
    day = int(datetime.now(timezone).day)
    return(date(year, month, day).isocalendar()[2])

def getText(filename):
    "This function reads all plain text within a docx document"
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def box_print(text,thickness=1,syms_h ="~",syms_v ="|",to_print = True,n_unicode = 0):
    def place_holder(n):
        return("{:"+str(n)+"}")

    def sandwhich(n,text,thickness,syms = "*"):
        return("{}".format(syms*thickness)+place_holder(n).format(text)+"{}".format(syms*thickness))
    "Print Text surronded by boxes"
    max_len = 0
    for i in text.split("\n"):
        if len(i) > max_len:
            max_len = len(i)
    box_length = round(max_len + 2*thickness + n_unicode*1.5)
    string = syms_h*box_length
    for line in text.split("\n"):
        string += "\n"+sandwhich(max_len,line,thickness,syms_v)
    string += "\n"+syms_h*box_length
    if to_print:
        print(string)
        return
    return string

class Load:
    "This class is dedicated to load information of OKR weekly logs"
    def __init__(self,file_path):
        self.Authorized = True
        text = getText(file_path)
        self.log_list = []
        self.week_log = []
        for i in text.split("\n"):
            self.log_list.append(i.strip())  
            
    def Task_Find(self,ID,Load = None):
        "Return the Goal Object based on ID"
        if Load is None:
            Load = self
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
    
    def add_okr(self,text_in_format):
        try:
            self.WeekObjective.set_Special_Task(text_in_format)
        except:
            print("WeekObjective not loaded")
        
    def get_week_objective(self):
        "Load WeekObjectives into self.WeekObjective"
        self.WeekObjective = Day()
        try:
            start = "Priority Objectives:"
            finish = "Special Objectives:"
            self.WeekObjective.set_Priority_Task(
                self.log_list[self.log_list.index(start):self.log_list.index(finish)])
        except :
            print("For WeekObjective, Priority_Task is not logged")
            self.Authorized = False
        try:
            start = "Special Objectives:"
            finish = "Daily (Recursive) Objectives:"
            self.WeekObjective.set_Special_Task(self.log_list[self.log_list.index(start):
                                                                self.log_list.index(finish)])
        except :
            print("For WeekObjective, Recursive_Task is not logged")
            self.Authorized = False
        try:
            start = "Daily (Recursive) Objectives:"
            finish = "ANCHOR"
            self.WeekObjective.set_Recursive_Task(self.log_list[self.log_list.index(start):self.log_list.index(finish)])
        except :
            print("For WeekObjective, Special_Task is not logged")
            self.Authorized = False

    def week_okr_show(self):
        self.WeekObjective.show()

    def log_day(self,n):
        "Get the data for specific day of log; n = number of day in the week"
        idx_head = self.log_list.index("Day " + str(n))
        if n < 7:
            idx_tail = self.log_list.index("Day " + str(n+1))
        else: 
            idx_tail = self.log_list.index(str("Week_Summary"))
        self.log_of_day = self.log_list[idx_head:idx_tail]
        n_day = self.log_of_day[0]
        date = self.log_of_day[1]
        new_day_log = Day()
        try:
            new_day_log.set_Priority_Task(self.log_of_day[self.log_of_day.index("Priority Task:"):self.log_of_day.index("Special OKR:")])
        except ValueError:
            print("For day {}, Priority_Task is not logged".format(n))
            self.Authorized = False
        try:
            new_day_log.set_Special_Task(self.log_of_day[self.log_of_day.index("Special OKR:"):self.log_of_day.index("Recursive OKR:")])
        except ValueError:
            print("For day {}, Special_Task is not logged".format(n))
            self.Authorized = False
        try:
            new_day_log.set_Recursive_Task(self.log_of_day[self.log_of_day.index("Recursive OKR:"):self.log_of_day.index("Daily Summary:")])
        except ValueError:
            print("For day {}, Recursive_Task is not logged".format(n))
            self.Authorized = False
        return new_day_log

    def log_all(self):
        "Get the data for all 7 days in a week"
        for i in range(7):
            i = i + 1
            self.week_log.append(self.log_day(i))


    def logs_show(self,day = "all"):
        "Input: show weekday's tasks, show all tasks by default"
        if self.week_log == []:
            print("Load the weekly logs first!")
        else:
            if day == "all":
                for days in range(len(self.week_log)):
                    print("Day:",days+1)
                    self.week_log[days].show(progress = False)
                    print("\n")
            else:
                self.week_log[day-1].show(progress = False)


    def task_progress(self,Task_ID):
        task_type = Task_ID.split("_")[0]
        Objective_ID = Task_ID.split("_")[1]
        KR_ID = Task_ID.split("_")[2]
        if task_type == "R":
            for i in range(len(self.WeekObjective.Recursive_Task)):
                if self.WeekObjective.Recursive_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Recursive_Task[i].progress_show()
        if task_type == "S":
            for i in range(len(self.WeekObjective.Special_Task)):
                if self.WeekObjective.Special_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Special_Task[i].progress_show()
            for i in range(len(self.week_log[weekday_today()-1].Priority_Task)):
                if self.WeekObjective.Priority_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Priority_Task[i].progress_show()
    
    def complete(self,Task_ID,tk_pop = False,PRINT = False):
        task_type = Task_ID.split("_")[0]
        Objective_ID = Task_ID.split("_")[1]
        KR_ID = Task_ID.split("_")[2]
        if task_type == "R":
            for i in range(len(self.WeekObjective.Recursive_Task)):
                if self.WeekObjective.Recursive_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Recursive_Task[i].complete(KR_ID,False,tk_pop = tk_pop,PRINT=PRINT)

        elif task_type == "S":
            for i in range(len(self.WeekObjective.Special_Task)):
                if self.WeekObjective.Special_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Special_Task[i].complete(KR_ID,tk_pop = tk_pop,PRINT = PRINT)

        elif task_type == "P":
            for i in range(len(self.WeekObjective.Priority_Task)):
                if self.WeekObjective.Priority_Task[i].Objective.split(":")[0] == Objective_ID:
                    self.WeekObjective.Priority_Task[i].complete(KR_ID, tk_pop = tk_pop,PRINT = PRINT)
                    
                    
#@title Day Class {display-mode: "form"}
class Day:
    def __init__(self):
        self.Priority_Task = []
        self.Special_Task = []
        self.Recursive_Task = []
        global Authorized

    def set_Priority_Task(self,list_of_tasks):
        global Authorized 
        for string in list_of_tasks:
            if len(string) > 0:
                try:
                    if string[0] == "G":
                        a_task = okr_task()
                        self.Priority_Task.append(a_task)
                        a_task.set_Objective(string)
                    elif string[0].upper() == "K":
                        a_task.set_KeyResult(string)
                    else:
                        pass
                except UnboundLocalError: 
                    Authorized = False
                    print("Failed to load, Check docx format.(If all goals start with G)")

    
    def set_Special_Task(self,list_of_tasks):
        global Authorized 
        for string in list_of_tasks:
            if len(string) > 1:
                try:
                    if string[0] == "G":
                        a_task = okr_task()
                        self.Special_Task.append(a_task)
                        a_task.set_Objective(string)
                    elif string[0].upper() == "K":
                        a_task.set_KeyResult(string)
                    else:
                        pass
                except UnboundLocalError: 
                    Authorized = False
                    print("Failed to load, Check docx format.(If all goals start with G)")

    def set_Recursive_Task(self,list_of_tasks):
        global Authorized 
        for string in list_of_tasks:
            if len(string) > 1:
                try:
                    if string[0] == "G":
                        a_task = okr_task()
                        self.Recursive_Task.append(a_task)
                        a_task.set_Objective(string)
                    elif string[0].upper() == "K":
                        a_task.set_KeyResult(string)
                    else:
                        pass
                except UnboundLocalError: 
                    Authorized = False
                    print("Failed to load, Check docx format.(If all goals start with G)")

    def show(self,sections = ['Priority_Task','Special_Task','Recursive_Task'], progress = True):
        if not isinstance(sections,list):
            sections = [sections]
        for sec in sections: 
            box_print(f"{sec}:")
            if eval(f"self.{sec}") != []:
                for tasks in eval(f"self.{sec}"):
                    if tasks.KeyResults != {} or progress :
                        print(tasks)
                        if progress:
                            pass 
            else:
                print('Empty')
            
#@title Task Class {display-mode: "form"}
class okr_task():
    def __init__(self):
        self.Objective = ""
        self.KeyResults = {}
        self.PG = 0
        self.weight = 0
        self.num_KR = len(list(self.KeyResults.keys()))
        self.completed_KR = 0
        self.unchanged = True
        global Authorized

    def set_Objective(self,obj):
        global Authorized 
        try:
            self.Objective = obj.split("[")[0].strip()
            self.weight = int(obj.split("[")[1].strip("]").split(":")[-1])
        except:
            Authorized = False
            print("task_set up failed: {} has wrong format".format(obj))
            

    def set_KeyResult(self,KeyResult):
        global Authorized 
        try:
            code = KeyResult.split("{")[0].split(":")[0]
            content = KeyResult.split("{")[0].split(":")[1]
            try: 
                a_task = task()
                deadline,time,difficulty = self.get_task_info(KeyResult)
                a_task.set_difficulty(difficulty)
                a_task.set_time(time)
                a_task.set_deadline(deadline)
                a_task.set_reward()
            except:
                Authorized = False
                print("task_set up failed: {} has wrong format".format(KeyResult))

            self.KeyResults[code] = [content,a_task]
            
        except:
            Authorized = False
            print("okr_task KeyResult set up failed, {} has wrong format".format(KeyResult))

    def complete(self,KeyResult_ID,Special=True,tk_pop = False,PRINT = False):
        from tkinter import messagebox
        if self.unchanged:
            self.num_KR = len(list(self.KeyResults.keys()))
            self.unchanged = False
        try:  
            if Special:
                self.KeyResults.pop(KeyResult_ID)
                self.completed_KR += 1
                self.PG = self.completed_KR/self.num_KR
                bar = progress(self.PG)
            else: 
                self.PG += 1/(7*self.num_KR)
                self.KeyResults[KeyResult_ID][1].COUNT += 1
            msg = f"{str(self)}"
            if tk_pop:
                try:
                    messagebox.showinfo(title = 'Objective Updated', 
                           message = msg)
                except:
                    pass 
            else:
                if PRINT:
                    print(msg)
            
        except KeyError:
            print("{} no longer belong to this objective".format(KeyResult_ID))
            print("Current Key Results:")
            for ks in self.KeyResults.keys():
                print(ks, end = ";")
                
        
        

    def progress_show(self):
        return progress(self.PG)

    def __repr__(self):
        rep = self.Objective + "\nweight:" + str(self.weight)
        for k in self.KeyResults:
            rep += "\n"+ "\t" + k + ":{:60}".format(str(self.KeyResults[k][0]))
            if self.KeyResults[k][1]["COUNT"] > 0:
                rep += "  |Counts:{}".format(self.KeyResults[k][1].COUNT)
                
        rep += '\n\n' + progress(self.PG) + '\n'
        return rep

    def get_task_info(self,KeyResult):
        deadline = None
        time = None
        difficulty = None
        line = KeyResult
        temp = line.replace("}","").split("{")[-1].split(",")
        for i in temp:
            if i.split(":")[0].strip() == "deadline":
                deadline = i.split(":")[1].strip()
            elif i.split(":")[0].strip() == "time":
                time = i.split(":")[1].strip()
            elif i.split(":")[0].strip() == "difficulty":
                difficulty = i.split(":")[1].strip()
        return deadline,time,difficulty

class task():
    def __init__(self):
        global Authorized
        self.difficulty = 0
        self.time = 0
        self.reward = 0
        self.completed = False
        self.deadline = None
        self.description = None
        self.COUNT = 0
        
    def set_desc(self,desc):
        self.description = desc 
        
    def set_deadline(self,deadline):
        self.deadline = deadline
        
    def set_time(self,time):
        self.time = time

    def set_difficulty(self,difficulty):
        self.difficulty = difficulty
    
    def complete(self):
        self.completed = True

    def __repr__(self):
        return(str({"difficulty":self.difficulty,"time":self.time,"reward":self.reward,"completed":self.completed,"deadline":self.deadline,"COUNT":self.COUNT}))
    
    def __getitem__(self,name):
        return(getattr(self,name))

    def set_reward(self):
        global Authorized 
        "Calculate Reward based on time and difficulty"
        try:
            time = abs(float(self.time))
            difficulty = abs(float(self.difficulty))
        except TypeError: 
            Authorized = False
            print("Fail to calculate reward, task has wrong format")
        time_lower_bound = 0.25
        time_upper_bound = 4
        difficulty_upper_bound = 10
        if time < time_lower_bound:
            time = time_lower_bound
        if time > time_upper_bound:
            time = time_upper_bound
        if difficulty > difficulty_upper_bound:
            difficulty = difficulty_upper_bound
        difficulty = abs(difficulty)
        reward = 3*(time**0.5*difficulty**0.5) + random.choice([-1,-0.5,0,0.5,1,1.5,2])
        self.reward = round(reward)



# In[32]:


#@title Progress Mod {display-mode: "form"}
# -----------------------------------------------------------------------------
# Copyright (c) 2016, Nicolas P. Rougier
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import sys, math

def progress(value,  length=40, title = " ", vmin=0.0, vmax=1.0, blank = '_'):
    """
    Text progress bar
    Parameters
    ----------
    value : float
        Current value to be displayed as progress
    vmin : float
        Minimum value
    vmax : float
        Maximum value
    length: int
        Bar length (in character)
    title: string
        Text to be prepend to the bar
    """
    # Block progression is 1/8
    blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
    vmin = vmin or 0.0
    vmax = vmax or 1.0
    lsep, rsep = "▏", "▕"

    # Normalize value
    value = min(max(value, vmin), vmax)
    value = (value-vmin)/float(vmax-vmin)
    
    v = value*length
    x = math.floor(v) # integer part
    y = v - x         # fractional part
    base = 0.125      # 0.125 = 1/8
    prec = 3
    i = int(round(base*math.floor(float(y)/base),prec)/base)
    bar = "█"*x + blocks[i]
    n = length-len(bar)
    bar = lsep + bar + blank*n + rsep    
    return "\r" + title + bar + " %.1f%%" % (value*100)

#########
class Load_Notion(Load):
    def __init__(self,**kargs):
        #token,share_link,file_path
        if 'token' in kargs and 'share_link' in kargs:
            token = kargs['token']
            share_link = kargs['share_link']
            self.set_token(token) 
            self.set_link(share_link)
        elif 'file_path' in kargs:
            file_path = kargs['file_path']
            Load.__init__(self,file_path)
         
    def set_token(self,token):
        self.token = token
        
    def Get_token(self):
        return self.token 
    
    def set_link(self,link):
        self.page_link = link
    
    @staticmethod
    def Get_ID(link):
        out = link.split('-')[-1]
        #print(out)
        assert len(out) == 32, 'The length of the ID MUST be 32'
        return out

    def Get_Block_children(self,share_link = None,token = None,block_id = None, retry = 3):
        assert not all([share_link is None,block_id is None]),'Either Share_link or Block_Id need not to be none'
        if block_id is None:
            block_id = self.Get_ID(share_link)
        #
        if token is None:
            token = self.token 
        header = {'Authorization':f'Bearer {token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        url = f'https://api.notion.com/v1/blocks/{block_id}/children?page_size=100'
        COMPLETE = False
        while retry > 0 and not COMPLETE:
            try:
                OUT = requests.request(method = 'GET', url = url , headers = header, ).json()
                COMPLETE = True
            except:
                print("Fail to Fetch, Retry in 3 sec")
                retry -= 1
                sleep(3) 
        return  OUT
    
    def Fetch_Page(self,share_link):
        RES1 = self.Get_Block_children(share_link) 
        #dict_keys(['object', 'results', 'next_cursor', 'has_more'])
        OUT = {}
        try:
            print(f"Status: {RES1['status']}")
        except:
            print('Connection Established')
        for D in  RES1['results']  :
            try:
                #Identify if D has toggle:
                (D['toggle'])
                #Print Category
                section = D['toggle']['text'][0]['plain_text'] ### [Section Layer] 
                print(section) 
                #print(D['id']) #<-Id of the Category Toggel
                RES2 = self.Get_Block_children(block_id = D['id'])                        
                #print(res['results'][0]['id'])
                list_of_tasks = []
                for res_goal in RES2['results']: ### [Goal Layer] 
                    try:
                        type = res_goal['type']
                        all_texts = [i['plain_text'] for i in res_goal[type]['text']] 
                        G_str = Lst_to_str(all_texts)
                        print("\t"+G_str)
                        list_of_tasks.append(G_str)
                        RES3 = self.Get_Block_children(block_id = res_goal['id']) 
                        for res_kr in RES3['results']: ### [KeyResults Layer] 
                            type = res_kr['type']
                            all_texts = [i['plain_text'] for i in res_kr[type]['text']] 
                            Kr_str = Lst_to_str(all_texts)
                            print("\t\t"+Kr_str)
                            list_of_tasks.append(Kr_str)
                    except Exception as e:
                        print(f'Error under Goal: {e}')
                #Eventually
                OUT[section] = list_of_tasks
            except Exception as e:
                print('Unexpected Error:',e) 
            print(OUT.keys())
        return OUT
        
    def Notion_Load_WeekObjective(self,share_link = None):
        if share_link is None:
            share_link = str(self.page_link)
        self.WeekObjective = Day()
        try:
            DICT = self.Fetch_Page(share_link)
            for Category in DICT:
                if Category[0] == 'P':
                    self.WeekObjective.set_Priority_Task(DICT[Category])
                elif Category[0] == 'S':
                    self.WeekObjective.set_Special_Task(DICT[Category])
                elif Category[0] == 'D':
                    self.WeekObjective.set_Recursive_Task(DICT[Category])
        except Exception as e:
            print(f"Load ERROR due to : {e}")
            messagebox.showwarning('Notion Load ERROR', 'ERROR,Notion Fail to Load.Please check connection and try again later')          
        
                


if __name__ == '__main__':
    # path = 'OKRLOG test.docx'
    # L = Load(path)
    # L.get_week_objective()
    # L.week_okr_show()
    token = 'secret_VvobxKycNDREw5sws3VhfIb5V2MRYLgOKZlAm5a0S7p'
    share_link = 'https://www.notion.so/TEST-761b88a6d6de48a791654433d0da1c46'
    
    Load = Load_Notion(token = token,share_link = share_link)
    Load.Notion_Load_WeekObjective()
    Load.week_okr_show()
    
    # #Test：
    # share_link = 'https://www.notion.so/TEST-761b88a6d6de48a791654433d0da1c46'
    # Load = Load_Notion(token = token,share_link = share_link)
    # RES1 = Load.Get_Block_children(share_link) 
    # #dict_keys(['object', 'results', 'next_cursor', 'has_more'])
    # OUT = {}
    # try:    
    #     print(f"Status: {RES1['status']}")
    # except:
    #     print('Connection Established')
    # for D in  RES1['results']  :
    #     try:
    #         #Identify if D has toggle:
    #         (D['toggle'])
    #         #Print Category
    #         print(D['toggle']['text'][0]['plain_text']) ### [Section Layer] 
    #         #print(D['id']) #<-Id of the Category Toggel
    #         RES2 = Load.Get_Block_children(block_id = D['id'])                        
    #         #print(res['results'][0]['id'])
    #         list_of_tasks = []
    #         for res_goal in RES2['results']: ### [Goal Layer] 
    #             try:
    #                 type = res_goal['type']
    #                 all_texts = [i['plain_text'] for i in res_goal[type]['text']] 
    #                 G_str = Lst_to_str(all_texts)
    #                 print("\t"+G_str)
    #                 list_of_tasks.append(G_str)
    #                 RES3 = Load.Get_Block_children(block_id = res_goal['id']) 
    #                 for res_kr in RES3['results']: ### [KeyResults Layer] 
    #                     type = res_kr['type']
    #                     all_texts = [i['plain_text'] for i in res_kr[type]['text']] 
    #                     Kr_str = Lst_to_str(all_texts)
    #                     print("\t\t"+Kr_str)
    #                     list_of_tasks.append(Kr_str)
    #             except Exception as e:
    #                 print('Error:',e)
    #         #Eventually
    #         OUT[D['toggle']['text'][0]['plain_text']] = list_of_tasks
    #     except Exception as e:
    #         pass 
    #
    #
    #     print(OUT.items())
    