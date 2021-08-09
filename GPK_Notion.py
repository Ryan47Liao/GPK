import requests
import urllib, json

#
from Plan_load import *
from gpkTask import *
import pandas as pd
#
import tkinter as tk

# In[2]:
class remember:
    def __init__(self,f,*args,**kargs):
        self._f = f 
        self.args = args
        self.kargs = kargs 
    
    def __call__(self):
        return self._f(*self.args,**self.kargs)
    
def Fetch_Plain_test(rich_text):
    return Lst_to_str([i['plain_text'] for i in rich_text])

def Lst_to_str(Lst):
    out = ""
    for i in Lst:
        out += i 
    return out 

def fetch_db_id(share_link):
    temp = share_link.split('/')[-1].split('?')[0]
    out = f"{temp[:8]}-{temp[8:12]}-{temp[12:16]}-{temp[16:20]}-{temp[20:]}"
    return out


# In[4]:


class API_retry:
    "Decorator Class that retries the function for 3 times"
    def __init__(self,f,n_retry = 3,wait = 3):
        self._f = f 
        self.COMPLETE = False 
        self.n_retry = n_retry
        self.Reset(wait)

    def Reset(self,wait):
        self.Retries = int(self.n_retry)
        self.wait = wait

        
    def __call__(self,*args,**kargs):
        from time import sleep 
        while self.Retries > 0 and not self.COMPLETE:
            try:
                OUT = self._f(*args,**kargs)
                self.COMPLETE = True
                self.Reset(self.wait)
            except:
                print(f"Function {self._f} failed, Retry in {self.wait} secs...")
                self.Retries -= 1
                sleep(self.wait) 
        if self.Retries <= 0:
            print(f'Function {self._f} FAILED after {self.n_retry} retries')
            self.Reset(self.wait)
            self._f(*args,**kargs) #One Last Time to REPORT Error
            
        else:
            self.COMPLETE = False
            return  OUT
        
@API_retry
def Request(*args,**kargs):
    return requests.request(*args,**kargs)


# In[34]:
class GPK_Notion:
    def __init__(self,token,share_link):
        self.token = token
        self.share_link = share_link
        
    def Set_token(token):
        self.token = token
        
    @staticmethod
    def Get_ID(link):
        out = link.split('-')[-1]
        print(out)
        assert len(out) == 32, 'The length of the ID MUST be 32'
        return out
        
    def Get_Page(self,share_link = None,token = None,page_id = None):
        assert not all([share_link is None,page_id is None]),'Either Share_link or Block_Id need not to be none'
        if page_id is None:
            page_id = self.Get_ID(share_link)
        if token is None:
            token = self.token 
        url = f'https://api.notion.com/v1/pages/{page_id}'
        header = {'Authorization':f'Bearer {token}','Notion-Version':'2021-05-13'}
        return Request(method = 'GET', url = url , headers = header ).json()
        
    def Get_Block_children(self,share_link = None,token = None,block_id = None):
        "Get children blocks from a Block"
        assert not all([share_link is None,block_id is None]),'Either Share_link or Block_Id need not to be none'
        if block_id is None:
            block_id = self.Get_ID(share_link)
        if token is None:
            token = self.token 
        header = {'Authorization':f'Bearer {token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        url = f'https://api.notion.com/v1/blocks/{block_id}/children?page_size=100'
        return Request(method = 'GET', url = url , headers = header ).json()
        
    def Get_DataBase_all(self,token = None):
        "Get DataBases that is shared with given token"
        if token is None:
            token = str(self.token)
        url =  'https://api.notion.com/v1/databases'
        header = {'Authorization':f'Bearer {token}','Notion-Version':'2021-05-13'}
        data = {'page_size':100}
        DBs_res = Request(method = 'GET', url = url , headers = header ,data = json.dumps(data)).json()
        return DBs_res
    
    def Get_DataBase(self,share_link = None , database_id = None ,token = None):
        "Get DataBases that is shared with given token"
        if token is None:
            token = str(self.token)
        assert not all([share_link is None,database_id is None]),'Either Share_link or Block_Id need not to be none'
        if database_id is None:
            database_id = fetch_db_id(share_link)
        url = f'https://api.notion.com/v1/databases/{database_id}'
        header = {'Authorization':f'Bearer {token}','Notion-Version':'2021-05-13'}
        DB_res = Request(method = 'GET', url = url , headers = header).json()
        return DB_res
    
    def Query_DataBase(self,share_link = None,database_id = None,
                       filter_dict = {"or": [{"property": "Status","select": {"does_not_equal": "📥Archived"}  }]}):
        #Filter and Sorts are currently not supported
        "Get data from DataBase given id"
        assert not all([share_link is None,database_id is None]),'Either Share_link or Block_Id need not to be none'
        if database_id is None:
            database_id = fetch_db_id(share_link)
        header = {'Authorization':f'Bearer {self.token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        url = f'https://api.notion.com/v1/databases/{database_id}/query'
        data = {"filter": filter_dict }
        tasks_res = Request(method = 'POST', url = url , headers = header , data = json.dumps(data)).json() 
        return tasks_res
    
    def DB_Preview(self,tasks_res):
        for task in tasks_res['results']:
            task_name = Lst_to_str([i['plain_text'] for i in task['properties']['Name']['title']])
            print(task_name)
            D_temp = task['properties']
            #Task Properties:
            for p in D_temp.keys():
                if D_temp[p]['type'] == 'number':
                    content = D_temp[p]['number']
                elif D_temp[p]['type'] == 'select':
                    content = D_temp[p]['select']['name']
                elif D_temp[p]['type'] == 'rich_text':
                    content = Fetch_Plain_test(D_temp[p]['rich_text'])
                elif D_temp[p]['type'] == 'date':
                    start = D_temp[p]['date']['start']
                    end = D_temp[p]['date']['end']
                    content = f'{start} -> {end}'
                print(f'{p}:{content}')
            task_detail = self.Get_Block_children(self,block_id= task['id'])
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
                        print(f'\t-{status} {text}')
                        print('\n')
                    except:
                        pass
                    

    def Post_MiscDB(self,parent_link,title = '📝OKR Miscs', Status_options = [
                            {
                                "name": "⏰Not started",
                                "color": "red"
                            },
                            {
                                "name": "⏳In Progress",
                                "color": "green"
                            },
                            {
                                "name": '✅Completed',
                                "color": "purple"
                            },
                            {
                                "name": "📥Archived",
                                "color": "yellow"
                            }
                        ]):
        #Basic Info
        token = str(self.token)
        header = {'Authorization':f'Bearer {token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        page_id = self.Get_ID(parent_link)
        url = 'https://api.notion.com/v1/databases'
        #1.Parent Value
        parent_value = {"type": "page_id", "page_id": page_id }
        #2.Specify Title Value, can be rich text:
        title_value = [{"type": "text","text": {"content": title}}]
        #3.Specify Properties:
        properties_value = {
                    "Name": {"title": {}},
                    "Status": {"select": {"options": Status_options}},
                    "Deadline": {"date": {}},
                    "Hours": {"number": {"format": "number"}},
                    "Difficulty": {"number": {"format": "number"}},
                    "ID": {"rich_text": {}}
                           }
        #Finally:
        data = {}
        data['parent'] = parent_value
        data['title'] = title_value
        data['properties'] = properties_value
        return Request(method = 'POST', url = url , headers = header, data = json.dumps(data) ).json()
        
        
                    

    def Post_DataBase(self,parent_link,title = '🚀OKR Todos',
                      Status_options = [
                            {
                                "name": "⏰Not started",
                                "color": "red"
                            },
                            {
                                "name": "⏳In Progress",
                                "color": "green"
                            },
                            {
                                "name": '✅Completed',
                                "color": "purple"
                            },
                            {
                                "name": "📥Archived",
                                "color": "yellow"
                            }
                        ], 
                     Orientation_options = [
                            {
                                "name": "🏃🏻‍♂️Health",
                                "color": "red"
                            },
                            {
                                "name": "👪Family",
                                "color": "green"
                            },
                            {
                                "name": '🧗🏻‍♀️Self Development',
                                "color": "purple"
                            },
                            {
                                "name": "💼Career",
                                "color": "yellow"
                            }
                        ]):
        "Create a DataBase given parent"
        #Basic Info
        token = str(self.token)
        header = {'Authorization':f'Bearer {token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        page_id = self.Get_ID(parent_link)
        url = 'https://api.notion.com/v1/databases'
        #1.Parent Value
        parent_value = {"type": "page_id", "page_id": page_id }
        #2.Specify Title Value, can be rich text:
        title_value = [{"type": "text","text": {"content": title}}]
        #3.Specify Properties:
        properties_value = {
                "Name": {"title": {}},
                "Status": {"select": {"options": Status_options}},
                "Orientation": {"select": {"options": Orientation_options}},
                "Category": {
                    "select": {
                        "options": [{"name": "🎯Priority","color": "red"},{"name": "✨Special","color": "purple"}
                                   ,{"name": "🔄Recursive","color": "blue"}]
                    }
                },
                "Hours": {"number": {"format": "number"}},
                "Difficulty": {"number": {"format": "number"}},
                "Reward": {"number": {"format": "dollar"}},
                "Deadline": {"date": {}},
                "ID": {"rich_text": {}}
            }
        #Finally:
        data = {}
        data['parent'] = parent_value
        data['title'] = title_value
        data['properties'] = properties_value
        return Request(method = 'POST', url = url , headers = header, data = json.dumps(data) ).json()


    def Post_page(self,Parent_id,title,properties_value,children_value):
        "Create a Page given parent"
        #Basic Info
        header = {'Authorization':f'Bearer {self.token}','Content-Type':'application/json','Notion-Version':'2021-05-13'}
        url = 'https://api.notion.com/v1/pages'
        # --data
        data = {}
        parent_value = {"database_id": Parent_id }
        #Finally
        data['parent'] = parent_value
        data['properties'] = properties_value
        if children_value is not None:
            data['children'] = children_value
        return Request(method = 'POST', url = url , headers = header, data = json.dumps(data) ).json()
        
    def Post_MiscTask(self,ID,Task_Name,Time,Difficulty,Due_Date,Descriptions = None, Status='⏰Not started',
                      Parent_id = None, share_link = None):
        assert not all([share_link is None,Parent_id is None]),'Either Share_link or Block_Id need not to be none'
        if Parent_id is None:
            Parent_id = fetch_db_id(share_link)
        properties_value = {
                "Name": {"title": [{"text": {"content": Task_Name}}]},
                "Hours": { "number": Time },
                "Difficulty": { "number": Difficulty },
                "Deadline": { "date": {'start': Due_Date ,'end':None} },
                "Status" : {"select": {"name": Status}},
                "ID": {"rich_text": [ {"text": {"content": ID}}]}
            }
        #If need to add more details:
        if Descriptions is not None:
            children_value = [
                    {"object": "block","type": "heading_2","heading_2": {
                    "text": [{ "type": "text", "text": { "content": "Descriptions:" } }]}},
                    {   "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": Descriptions , }}]}}]
        else:
            children_value = None
        return self.Post_page(Parent_id,Task_Name,properties_value,children_value)
        
    def Post_Task(self,Task_Name,ID,Time,Difficulty,Reward,Due_Date,
                  Descriptions = None ,Parent_id = None, share_link = None, 
                  Status='⏰Not started',
                 Category_D = {'P':'🎯Priority','S':'✨Special','R':'🔄Recursive'},
                 Orientation_D = {'1':'🏃🏻‍♂️Health','2':'👪Family','3':'🧗🏻‍♀️Self Development','4':'💼Career'}):
        assert not all([share_link is None,Parent_id is None]),'Either Share_link or Block_Id need not to be none'
        if Parent_id is None:
            Parent_id = fetch_db_id(share_link)
        Category = Category_D[ID[0]]
        Orientation = Orientation_D[ID.split('_')[1][1]]
        properties_value = {
                "Name": {"title": [{"text": {"content": Task_Name}}]},
                "ID": {"rich_text": [ {"text": {"content": ID}}]},
                "Orientation": {"select": {"name": Orientation}},
                "Category": {"select": {"name": Category}},
                "Hours": { "number": Time },
                "Difficulty": { "number": Difficulty },
                "Reward": { "number": Difficulty },
                "Deadline": { "date": {'start': Due_Date ,'end':None} },
                "Status" : {"select": {"name": Status}}
            }
        #If need to add more details:
        if Descriptions is not None:
            children_value = [
                    {"object": "block","type": "heading_2","heading_2": {
                    "text": [{ "type": "text", "text": { "content": "Descriptions:" } }]}},
                    {   "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": Descriptions , }}]}}]
        else:
            children_value  = None
        return self.Post_page(Parent_id,Task_Name,properties_value,children_value)
    
    def DB_to_df(self,tasks_res,PRINT = False, PG_show  = False):
        
        print('Start')
        _Dict = {'TaskName' : [],'Description':[]}
        ###
        Properties = set()
        for i in [task['properties'].keys() for task in tasks_res['results']]:
            for j in i:
                Properties.add(j)
        ###
        def temp_f(task):
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
                task_detail = self.Get_Block_children(self,block_id= task['id'])
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
        
        ###Execution:
        for f in todo_stack:
            f()
        
        print(_Dict)
        return pd.DataFrame(_Dict)
    
    def Post_Gtask(self,Gtask,Description = "", share_link = None, Parent_id = None,Misc = False):
        assert not all([share_link is None,Parent_id is None]),'Either Share_link or Block_Id need not to be none'
        if Parent_id is None:
            Parent_id = fetch_db_id(share_link)
        if not Misc:#Post to GPK
            return self.Post_Task(Task_Name = Gtask.name,
                           ID = Gtask.ID,
                           Time = Gtask.Time,
                           Difficulty = Gtask.Difficulty,
                           Reward = Gtask.Reward,
                           Due_Date = Gtask.Deadline,
                           Descriptions = Description,
                           share_link = share_link,
                           Status='⏰Not started',
                           Parent_id = Parent_id)
        else:
            return self.Post_MiscTask(
                                ID = Gtask.ID,
                                Task_Name = Gtask.name,
                                 Time = Gtask.Time,
                                 Difficulty = Gtask.Difficulty,
                                 Due_Date = Gtask.Deadline,
                                 Descriptions = Description, 
                                 Status='⏰Not started',
                      Parent_id = Parent_id)
        

if __name__ == '__main__':
    share_link = 'https://www.notion.so/a29dbf7ded70414b8ecb7aa59feec315?v=ae5b4bb6711d41c1ba9453a33329a295'
    token = 'secret_n2NaWinvklG1SfsofblmjbxonwKt0kyJS2XaHZ1bM7S'
    TEST = GPK_Notion(token,share_link)
    
    filter_dict = {"or": [{"property": "Status","select": {"equals": "📥Archived"}  }]}#✅Completed
    res = TEST.Query_DataBase(share_link,filter_dict = filter_dict)
    print(res)
    print(len(res['results']))
    TEST.DB_to_df(res,True,PG_show= False)
    # root = tk.Tk()
    #
    # tbn = tk.Button(text = 'Start', command = lambda: TEST.DB_to_df(res,True,PG_show= True))
    # tbn.pack()
    # #Finally
    # root.mainloop()
    #

