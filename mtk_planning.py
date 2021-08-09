from GPK_MTK import GPK_MTK
from gpkTask import gpk_task
from Plan_load import Load
from gpkTask import gpk_task
from time import sleep
import copy
from tkinter import messagebox

from gpk_utilities import *

class GPK_MTK_Plan(GPK_MTK):
    def __init__(self,plan_path = None,api_token = None,
                 project_id = 'Null',Post = False,nap = 1):
        if plan_path is not None:
            self.get_Load(plan_path)
            
        GPK_MTK.__init__(self,api_token,project_id)
        print(f"GPK_MTK Initialized with Project_id:{project_id}")
        sleep(nap)
        if project_id == 'Null':
            #Create Project and Settings 
            self.Planner_SetUp()
        try:
            self.Sync()
            print('GPK Sync Complete')
        except:
            pass 
        
        if Post:
            sleep(nap)
            print("Posting All Tasks from the Loaded Plan")
            self.Post_All() #Post all Scheduled Task into the meistertask Planner 
              
    def get_Load(self,path):
        Loaded = Load_Notion(file_path = path)
        Loaded.get_week_objective()
        if Plan_Legit(Loaded):
            self.Load = Loaded
            self.Load_backup = copy.deepcopy(Loaded)
        else:
            Warning =  print_collector(lambda : Plan_Legit(Loaded))
            messagebox.showwarning('Import Error',Warning)
            

        
    def Planner_SetUp(self):
        self.RESET(name = 'OKR_Planner',
                       sections = ['Inbox','monday','tuesday','wednesday',
                                  'thursday','friday','saturday','sunday'], 
                  colors = ['orange','red','grass green','turquoise','purple','grass green',
                           'orange','blue'],
                  features = ["enable_timetracking","enable_taskrelationships"])
        
    def Incubent_tasks(self):
        df = self.View_df('Inbox')
        if len(df) == 0 :
            return []
        tasks = []
        for idx in df.index:
            try:
                tsk = gpk_task(df.loc[idx]['name'],df.loc[idx]['notes'])
                tasks.append(tsk)
            except Exception as e:
                print(f"Fail to include task:{df.loc[idx]}\n due to Exception{e}")
        return [task.ID for task in tasks]
        
    def Post_All(self):
        sec_id = self.Get_Sec_ID('Inbox')
        Incubent_tasks = set(self.Incubent_tasks())
        for category in ['Priority_Task','Special_Task']:#Recursive_Task are Irrelevant
            List_of_objectives = eval(f"self.Load.WeekObjective.{category}")
            for Obj in List_of_objectives:
                O_id = Obj.Objective.split(':')[0]
                for Kr_id in Obj.KeyResults:
                    task_name,task_obj = Obj.KeyResults[Kr_id][0],Obj.KeyResults[Kr_id][1]
                    #S_G4-3_K1
                    task_id = category[0] + '_' + Obj.Objective.split(':')[0] + '_' + Kr_id
                    if task_id not in Incubent_tasks:
                        note_og = f" ID:{task_id}\n\n[Reward]\n{task_obj.reward}\n[Time]\n\
                        {task_obj.time}\n[Difficulty]\n{task_obj.difficulty}\n\
                        [Description]\n{task_obj.description}"
                        #Change Notes Appearance 
                        try:
                            g_task = gpk_task(task_name,note_og)
                            note = g_task.Get_notes()
                            #Post the Task:
                            self.Post_task(sec_id,task_name,note)
                            print(f'task {task_id} posted')
                        except Exception as e:
                            print(f"Fail to POST task:{task_name,note_og}\n\n due to Exception{e}")
                            print("PLEASE WAIT for 3 sec")
                            sleep(3)
                            try:
                                self.Post_task(sec_id,task_name,note)
                            except Exception as e:
                                print(f"Unable to POST task {task_name,note_og}")
        
        print(f'All Tasks were Sent to Project {self.project_id}')

        
    def Task_today(self):
        "Return a data frame of the tasks of today"
        
        if self.PROJECTs[int(self.project_id)] == 'OKR_Plannng':
            self.Get_info()
            weekday = list(self.SECTIONs.values())[weekday_today()]
            self.Sync()
            return self.View_df(weekday)
        else:
            if 'OKR_Plannng' in self.PROJECTs.values():
                for project_id,pro_name in self.PROJECTs.items():
                    if pro_name == 'OKR_Plannng':
                        self.set_project_id(project_id) #Try to Set Project ID
                self.Task_today()
            else:
                print("ERROR,OKR_Planning Project Set_UP Required")
                    
if __name__ == '__main__':
    test = GPK_MTK_Plan(plan_path='OKRLOG_S3_W1.docx',
                        api_token='u1IqrMvqjFA99sNL9_RnipaYnXKd9cc7wUZXHCUhJ-I',
                        project_id= '6277887', Post= False)
    df = test.Task_today()
    tasks = [gpk_task(df.loc[idx]['name'],df.loc[idx]['notes']) for idx in df.index]
    print(tasks)
    print("DONE")
        