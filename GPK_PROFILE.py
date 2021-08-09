#!/usr/bin/env python
# coding: utf-8

# In[209]:


# PROFILE REQUIRED COSTUME MODs:
from RSA import *
from file_exp import *
import pickle
import pandas as pd
import datetime
import copy
from gpkTask import gpk_task
from GPK_MTK import GPK_MTK
from mtk_planning import GPK_MTK_Plan
# In[10]:
from gpk_utilities import *

class PROFILE:
    def __init__(self, username, password, bio = None):
        #________________________ATTRIBUTES_____________________________#
        self.username = username
        self.bio = bio #Optional
        self.Reward_Options = {}
        self.__keychain = {}
        self.__balance = 0
        self.PASSWORD = 'Whatthehell'
        #ENCRYPTION INTIALIZATION
        self.RSA_init(password)
        
        #________________________Other Features__________________________#
        self.todos = GPk_Mtk_todoList()
        # self.OKR = OKR_Plan()
        # self.inventory = Inventory()
        
    def RSA_init(self,password:int)->None:
        "Generate a pair of Random Keys"
        N,e,d = RSA_sys(200)
        d_hat = self.__d_mutate(password,N,e,d) # A Bijective Transformation
        self.__keychain = {"N":N,"e":e,"d_hat": d_hat}
        
    def __d_mutate(self,password,N,e,d):
        self.PASSCODE = ENC(self.PASSWORD,N,e)
        return d - password
    
    def __d_mutate_inv(self,password,d_hat)->int:
        return d_hat + password
        
    def Verified(self,password:int)->bool:
        "Verifies if the Pass Word is Correct"
        d_hat = self.__keychain['d_hat']
        N = self.__keychain['N']
        d_tempt = self.__d_mutate_inv(password,d_hat)
        if DEC(C = self.PASSCODE,d = d_tempt,N=N) == self.PASSWORD:
            return True
        else:
            return False

    def Save(self,file_path)->None:
        if file_path.split(".")[-1] == "gpk":
            OUTfile = open(file_path ,"wb")
            pickle.dump(self,OUTfile)
            OUTfile.close()
        else:
            print("Error.File must be gpk file.")
            
        

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
        try:
            ddl = str(DATE(Gtask.Deadline))
        except:
            #If Gtask has no Deadline, Add it as tmr 
            ddl = str((datetime.datetime.now()+ datetime.timedelta(days = 1)).date())
        self.add(task_name = Gtask.name,task_ID = Gtask.ID,
                 task_time = float(Gtask.Time) ,
                 task_diff = float(Gtask.Difficulty),
                 task_des = Gtask.Description , ddl = ddl)
      
    
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
        
    def complete(self,task_ID,Quadrant:int = 1):
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
#***0.04:
    ##Introducing Q4 Analysis 
        #1.If In Current Load, Add as Q2 
        og_task.insert(12,"Quadrant",Quadrant)
        #2.If NOT In Current Load, Add as Q1 
        #3. Q3/4 are not recorded here 
##END###
        self.Archive = self.Archive.append(og_task)
        self.Archive = self.idx_reset(self.Archive)
        self.delete(task_ID)
        
        
class GPk_Mtk_todoList(Gpk_ToDoList,GPK_MTK_Plan):
    def __init__(self,token = None,project_id=None):
        Gpk_ToDoList.__init__(self)
        GPK_MTK_Plan.__init__(self,api_token = token,project_id=project_id)
        
    #From GPK -> MTK
    def mtk_add(self,name,notes):
        "Add an task based on GPK notes"
        Gtask= gpk_task(name,notes)
        self.add(task_name = name,task_ID = Gtask.ID,
                 task_time = Gtask.Time ,task_diff = Gtask.Difficulty ,task_des = Gtask.Description)
        sec_id = self.Get_Sec_ID(Gtask.section) 
        try:
            self.Post_task(section_id = sec_id, name = name, notes = notes) #Post Task using GPK_MTK's method 
        except Exception as e:
            print("Fail to Upload to MTK due to the following exception:\n",e)  
            
    
    #From MTK -> GPK        
class GPk_Notion_todoList(Gpk_ToDoList,GPK_MTK_Plan):
    def __init__(self,token = None,project_id=None):
        Gpk_ToDoList.__init__(self)
        GPK_MTK_Plan.__init__(self,api_token = token,project_id=project_id)
        
class OKR_Plan:
    def __inti__(self):
        pass


# In[ ]:


class Inventory:
    def __inti__(self):
        pass
    

