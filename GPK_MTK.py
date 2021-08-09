#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import datetime
import pandas as pd
from IPython.core.display import display


# In[2]:


class Limit_call:
    def __init__(self,f, cmax = 120, time = 60):
        self._f = f
        self.counter = 0
        self.cycle = time
        self.counter_max = cmax
        
    def __call__(self,*args,**kargs):
        if self.counter == 0:
            self.start = datetime.datetime.now()
        if datetime.datetime.now() - self.start > datetime.timedelta(seconds = self.cycle):
            self.counter = 0 #Reset after a cycle 
            self.start = datetime.datetime.now()
        if self.counter+1 >= self.counter_max:
            remain = (self.start + datetime.timedelta(seconds = self.cycle) - datetime.datetime.now()).seconds
            raise Exception(f"Calling Celiling reached. Counter will RESET in {remain} seconds")
        else:
            self.counter += 1 
            return self._f(*args,**kargs)
            
@Limit_call
def Request(*args,**kargs):
    return requests.request(*args,**kargs)


# In[157]:

    
class MTK:
    def __init__(self,token = None, project_id = None,info_show = True):
        """
        Initialize the class with Token obtained @ 
        https://developers.meistertask.com/docs/authentication
        """
        self.set_token(token)
        self.url = "https://www.meistertask.com/api/"
        self.set_project_id(project_id)
        if info_show:
            self.info()
        
    def get_token(self):
        return self.__token
    
    def set_token(self,token):
        self.__token = token
        self.headers_get =  self.Get_Header()
        self.headers_post = self.Get_Header('Post')
        
    def set_project_id(self,ID):
        self.project_id = ID
        
    def Get_Header(self,method = "Get", length = '69'):
        header = {'Accept' : '*/*',
          'Authorization': f'Bearer {self.__token}',
           'accept-encoding' : 'gzip, deflate'}
        if method == "Get":
            return header 
        elif method == "Post":
            header['content-type'] = 'application/json'
            header['content-length'] = length
            return header 
        else:
            raise Exception("Invalid Method. Must either be [Get] or [Post]")
            
    def _QUERY(self,url,params = {},headers = None):
        """
        General Query Function.Deafult GET header 
        """
        if headers is None:
            return Request(method = "GET", url = url,
                                headers = self.headers_get,params = params).json()
        else:
            return Request(method = "GET", url = url,
                                headers = headers,params = params).json()
        
    def Get_info(self):
        self.PROJECTs = {d['id']:d['name'] for d in self.Get_projects()}
        if self.project_id is not None:
            self.SECTIONs = {d['id']:d['name'] for d in self.Get_secs()}
        
    def info(self):
        self.Get_info()
        try:
            print(f"[Projects]:")
            print("   ID   |Name")
            for ID,name in self.PROJECTs.items():
                print(f"{ID}|{name}")
            print(f"[Sections under Proejct {self.PROJECTs[int(self.project_id)]}]")
            print("   ID   |Name")
            for ID,name in self.SECTIONs.items():
                print(f"{ID}|{name}")
        except:
            pass 
        
    def Get_labs(self,project_id = None):
        if project_id is None:
            project_id = self.project_id
        return self._QUERY(f"https://www.meistertask.com/api/projects/{self.project_id}/labels")
        
    def Get_projects(self):
        return self._QUERY("https://www.meistertask.com/api/projects")
    
    def Get_secs(self,project_id = None):
        if project_id is None:
            project_id = self.project_id
        return self._QUERY(f"https://www.meistertask.com/api/projects/{self.project_id}/sections")
        
    def Get_task(self,task_id = "",project_id = None,params={}):
        """
        [Params]
        @project_id: id of the project of which the task belongs to
        @id: the id of the task. If blank, return all avaliable tasks
        ### https://developers.meistertask.com/docs/get-task
        [Query params]:
        @assigned_to_me:	string
            If set to true, 1 or yes, returns only tasks that are assigned to the current person.
        @focused_by_me:	string
            If set to true, 1 or yes, returns only tasks that are focused by the current person.
        @status:	string
            Filters the tasks based on their status. Any of: open, completed, completed_archived, trashed.
        @items:	integer
            Controls how many items should be shown on each page.
        @page:	integer
            Controls which page to view.
        @sort:	string
            Controls how to sort results.
        """
        try:
            if project_id is not None:
                return self._QUERY(url = f"https://www.meistertask.com/api/projects/{project_id}/tasks/{task_id}",
                                  params = params)
            else:
                return self._QUERY(url = f"https://www.meistertask.com/api/projects/{self.project_id}/tasks/{task_id}",
                                  params = params)
        except:
            return self._QUERY(url = f"https://www.meistertask.com/api/tasks/{task_id}",
                                  params = params)
    
    #Use Lower Case to Distinguish between the two
    def _Post_task(self,section_id,name:str,notes:str = "",
                  label_ids:[str] = [],custom_fields:[{str:str}] = [],
                 checklists:[{str:str}] = []):
        """
        [Params] (Requred)
        @section_id: the id of the section of which the task is posted under 
        @name: name of the task to be posted 
        ###https://developers.meistertask.com/docs/post-task
        [Body Params] (Optional)
        """
        data = {"name": name,"notes": notes,
                "label_ids": label_ids, "custom_fields": custom_fields, "checklists": checklists} 
        data = json.dumps(data, indent = 4)  
        return Request(method = "POST", url = f"https://www.meistertask.com/api/sections/{section_id}/tasks",
                                headers = self.headers_post ,params = {},data = data).json()
    
    def Post_project(self,name,description):
        data = json.dumps({"name":name,"notes" : description},indent = 4)
        return Request(method = "POST", url = "https://www.meistertask.com/api/projects",
                                headers = self.headers_post ,params = {},data = data).json()
    
    def Post_section(self,name,project_id = None):
        if project_id is None:
            project_id = self.project_id
        data = json.dumps({"name":name},indent = 4)
        headers = dict(self.headers_post)
        headers['content-length'] = '21'
        return Request(method = "POST", url = f"https://www.meistertask.com/api/projects/{project_id}/sections",
                                headers = headers ,params = {},data = data).json()
 

class GPK_MTK(MTK):
    def __init__(self,token = None,project_id=None):
        self.SECTIONs = {}
        self.SEC_Labs = {}
        MTK.__init__(self,token = token, project_id = None ,info_show = False)
        if "__Created" not in self.__dict__ and project_id is None:
            if token is not None:
                print("CREATING PROJECT")
                self.RESET()
        else:
            try:
                project_id = int(project_id)
                self.project_id = project_id
            except:
                self.project_id = None 
            finally:
                self.Get_info() #Collect Info about the account 

        
    def RESET(self,name = 'MTK_OKR', sections = ['Upcoming','In Progress','Done Today','Personal Development',
                              'Carrer','Health','Family','Other'], 
              colors = ['orange','red','grass green','turquoise','purple','grass green',
                       'orange','blue'],
              features = ["enable_timetracking","enable_taskrelationships"]):
        """
        Create a New Project with specified Sections 
        """
        def Response_Pass(Response):
            assert Response.status_code == 200,f'Error {Response.status_code}'
        class Color_Labels:
            def __init__(self):
                self.color_code = {'red':'d93651','orange':'ff9f1a','yellow':'ffd500',
                                  'grass green':'8acc47','moss green':'47cc8a','turquoise':
                                  '30bfbf','blue':'00aaff','purple':"8f7ee6",'grey':'98aab3'}
            def Pair_color(self,Label_lst,Color_lst):
                assert len(Label_lst) == len(Color_lst),"Label list and Color list must have same length"
                out = {}
                for l,c in zip(Label_lst,Color_lst):
                    out[l] = self.color_code[c]
                return out 
            
        Color = Color_Labels()
        Color_code = Color.Pair_color(sections,colors)
        self.project_info = self.Post_project(name,"Objective and KeyResults Management")
        print("Project Initialized")
        self.set_project_id(self.project_info['id']) #Set the project id to the one that's generated 
        for sec in sections:
            section = MTK.Post_section(self,sec,self.project_id) #Create Section
            label = Request(method = "Post",url = f"https://www.meistertask.com/api/projects/{self.project_id}/labels",
                   data = json.dumps({'name':sec ,'color':Color_code[sec]},indent=4),
                    headers = self.Get_Header("Post","32")) #Create Corresponding Label
            Response_Pass(label)
            self.SEC_Labs[sec] = label.json()['id']
            print(f"Section {sec} Initialized with color {Color_code[sec]}")
        #Enable Features:
        for feature in features:
            f = Request(method = "Post",url = f"https://www.meistertask.com/api/projects/{self.project_id}/project_settings",
                   data = json.dumps({"name":feature},indent=4),headers = self.Get_Header("Post","30"))
            Response_Pass(f)
            print(f"Feature {feature} enabled")
        print("RESET Complete")
        self.__Created = True
        
    def Sync(self):
        self.SEC_task = {}
        Tasks = self.Get_task(params = {"status":'open'})
        for task in Tasks:
            sec =  task['section_name']
            if sec in self.SEC_task:
                self.SEC_task[sec].append (task)
            else:
                self.SEC_task[sec] = [task]
        self.match_labs()
        
    def View_df(self,section):
        TEMP = {}
        try:
            for feature in self.SEC_task[section][0].keys():
                TEMP[feature] = []
                for task in self.SEC_task[section]:
                    TEMP[feature].append(task[feature])
            return pd.DataFrame(TEMP)
        except KeyError as e:
            print(e)
        return TEMP
    
    def match_labs(self):
        Labs = self.Get_labs(self.project_id)
        #print(Labs)
        Sec_Labs = {}
        for lab in Labs:
            Sec_Labs[lab['name']] = lab['id']
        self.SECTIONs_Labs = Sec_Labs
        #print('label matched')
        
    def Post_task(self,section_id,name:str,notes:str = "",
                  custom_fields:[{str:str}] = [],checklists:[{str:str}] = []):
        self.match_labs()
        return MTK._Post_task(self,section_id,name,notes,[self.SECTIONs_Labs[
            self.SECTIONs[section_id]
        ]],custom_fields,checklists)
    
    def Get_Sec_ID(self,sec_name):
            for sec_id,sec in self.SECTIONs.items():
                if sec == sec_name:
                    return sec_id 
                
    
        


    
if __name__ == '__main__': #Main Project 4963813
    #Main Server Secrete: u1IqrMvqjFA99sNL9_RnipaYnXKd9cc7wUZXHCUhJ-I
    #Test Server Secrete: zMruEfyp-ECixuwC1uhfEc9i4s1Bvhb2n7tyY6FO4EI
    TEST = GPK_MTK('u1IqrMvqjFA99sNL9_RnipaYnXKd9cc7wUZXHCUhJ-I','4963813') 
    TEST.Sync()
    TEST.SEC_task.keys()
    display(TEST.View_df('Planed_Today'))
    print('done')
