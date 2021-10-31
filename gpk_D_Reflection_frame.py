#Packages
import pickle
import GPK_PROFILE
import datetime
from gpk_utilities import *
import random 
import numpy as np
from gpk_Score import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from PIL import ImageTk,Image
import os

##
class D_Reflection():
    def __init__(self,Profile,df,
                 last_n_day = 0,figsize = (10,5) ):#Last n day is set to be 0, fetching data of today
        self.set_df(df,figsize) 
        self.set_last_n_day(last_n_day) 
        self.Set_Profile(Profile)
        
    def Set_Profile(self,Profile):
        self.Profile = Profile
        
    def Get_Profile(self):
        return self.Profile
    
    def set_last_n_day(self,last_n_day):
        self.last_n_day = last_n_day
        
    def set_df(self,df,figsize):
        self._df = df 
        self.Analysis = DF_Analysis(self._df,figsize)
        
    1 == 1   
### Quadrant Analysis:
####Example Code:
    # fig = plt.Figure(figsize=(10,5))
    # fig = Plot_Q4(fig,Q4_lst,121)
    # fig = Q4_Radar(fig,Q4_lst,122)
    # display(fig)
    # _type = Quadrant_Which(Q4_lst)
    # Sugguestion_img = Image.open(os.getcwd() + f'/Q4_Type{_type}.png')#/Pictures/Q4_Types
    # Sugguestion_img.resize((550,260))
    def Fetch_Q4_lst(self):
        "Return Q4_lst based on current df and last_n_day"
        Q4_dict = {1:0,2:0,3:0,4:0}
        df = self.Analysis.SEARCH('date_done',
                             lambda date:DATE(date) == datetime.datetime.today().date() 
                             - datetime.timedelta(days = self.last_n_day))
        #df_temp = df.drop(['description','time_stamp','ObjectID','Task Category'],axis = 1)
        
        #t_Q1 and t_Q2:
        Q4_time = df.groupby('Quadrant').Time.agg(sum)
        for quadrant in Q4_time.index:
            Q4_dict[int(quadrant)] = Q4_time[quadrant]
        #t_Q3:
        try:
            t_Q3 = sum(self.Analysis.SEARCH(df = self.Profile.Q3_todo.Archive, section = 'date_done' ,
                        predict = lambda date:DATE(date) == datetime.datetime.today().date() 
                                   - datetime.timedelta(days = self.last_n_day)).Time)
        except:
            t_Q3 = 0 #If the archive is empty 
        Q4_dict[3] = t_Q3
        #t_Q4:
        base = 24 - 8 - 3 - 2 
        Tot = base * len(set(df.date_done))
        t_Q4 = max(0,Tot - sum(Q4_dict.values()))
        Q4_dict[4]  = t_Q4
        #Finally:
        Q4_lst = list(Q4_dict.values()) 
        return Q4_lst 
    


    def Quadrant_Which(self,Q4_lst):
        "Determine Which Type of Q4 Category do you belong to"
        D = {idx+1:value for idx,value in enumerate(Q4_lst)}
        order = sorted(D,key = lambda k:D[k], reverse= True)
        if order[0] == 1:
            return 1
        elif D[1]+D[2] < D[3]+D[4]:
            return 3
        elif order[0] == 3:
            return 2 
        elif order[0] == 2:
            return 4 
        else:
            return 5
        
    def Q4_Radar(self,fig,stats,dim,kargs = {}):
        #Start:
        ax = fig.add_subplot(dim,**kargs,polar=True)
        #Data Prep:
        labels = np.array(['Q1','Q2','Q3','Q4'])
        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        stats = np.concatenate((stats,[stats[0]]))
        angles = np.concatenate((angles,[angles[0]]))
        ax.plot(angles, stats, 'o-', linewidth=2)
        ax.fill(angles, stats, alpha=0.25)
        ax.set_thetagrids((angles * 180/np.pi) [:-1], labels)
        ax.set_title('Quadrant Analysis')
        ax.grid(True)
        
        return fig

###

    def Plot_Q4(self, fig, Q4_lst, dim ,
                fill = True,normalize = False,color = ['r','g','m','c'] , kargs = {}):
        def f(x,r,idx):
            D = {1:(-1,1),2:(1,1),3:(-1,-1),4:(1,-1)}
            # x^2 + y^2 = r^2 
            a,b = D[idx]
            y = b*(r**2-(a*x)**2)**0.5
            return y 
        #Prep Data
            #Normalize Data into a scale of 100
        if normalize:
            c = sum(Q4_lst)/100
            Q4_lst = [Qi/c for Qi in Q4_lst]
        #
        Xs = [np.linspace(0,Qi,1000) for Qi in Q4_lst]
        Ys = []
        for idx,(X,Qi) in enumerate(zip(Xs,Q4_lst)):
            Ys.append([f(x,Qi,idx+1) for x in X]) 
        #Plotting
        ax = fig.add_subplot(dim,**kargs)
        #plt.figure()
        idx = 1
        for X,Y in zip(Xs,Ys):
            if idx in [1,3]:
                a = -1
            else:
                a = 1
            idx += 1
            ax.plot(a*X,Y,color[idx-2])
            if fill:
                Y[0] = 0
                Y[-1] = 0
                ax.fill(a*X,Y,color[idx-2])
        ax.set_title('Quadrant Analysis')
        ax.legend(['Q1','Q2','Q3','Q4'])
        return fig

    1 == 1
###Daily Statistic Compare to the average
####Example Code:
    # fig = plt.Figure()
    # Plot_Comparison(fig,Profile)
    
    def Plot_Comparison(self,fig,sec = 'Time', dim = 111 ,  kargs = {}):
        Profile = copy.deepcopy(self.Profile)
        #1.Get avg
        Analysis = self.Analysis#DF_Analysis(Profile.todos.Archive,(10,5))
        df_hist = Analysis.SEARCH('date_done',lambda date:DATE(date) < datetime.datetime.today().date() 
                                  - datetime.timedelta(days = self.last_n_day))
        sec_avg =  np.average(eval(f'df_hist.groupby("date_done").{sec}.agg(sum)'))
        #2.Get Today
        df_today = Analysis.SEARCH('date_done',
                   lambda date:DATE(date) == datetime.datetime.today().date() -
                    datetime.timedelta(days = self.last_n_day))
        sec_today =  sum(df_today[sec])
        #4.Plot 
    
        ax = fig.add_subplot(dim,**kargs)
    
        ax.barh(['Today','Average'],[sec_today,round(sec_avg,2)],color = ['orange','blue'])
        ax.set_title(f"Today's {sec}  is {100*round(sec_today/sec_avg,1)}% of the avg ")
        return fig

    1 == 1
###Week Progress Changes
####Example Code:
    # Load_yesterday,DICT= Get_Scores(df = Profile.todos.Archive,Loaded = Profile.todos.Load_backup,
    #                      target = str(datetime.datetime.today().date()),RETURN_null=1)
    # Progress = Progress_Collect(Load_yesterday)
    # print(Progress)
    @staticmethod
    def Progress_Collect(Load_yesterday,DICT):
        try: 
            IDs = DICT[str(datetime.datetime.today().date())]
        except:
            IDs = []
        def temp():
            for ID in IDs:
                try:
                    print(Task_Find(Load_yesterday,ID))
                    Load_yesterday.complete(ID)
                    print(progress(Task_Find(Load_yesterday,ID).PG))
                except:
                    print(ID)
                    pass
        return print_collector(temp)
    
    1 == 1
###Week Plan Progress View as Bar
###Example Code:
    # fig = plt.Figure(figsize = (10,5))
    # Plot_progress_bar(Profile,fig,sec = 'Reward')
    def Plot_progress_bar(self,fig,dim = 111,sec = 'Reward',kargs = {}):
        Profile = copy.deepcopy(self.Profile)
        DONE,TODO,DONE_t,TODO_t = Plan_Sep(Profile,sec)
        labels = list(Profile.okr_plan.keys())
        lst_done = list(DONE_t.values())#Done
        lst_todo = list(TODO_t.values())#Todo
        # men_std = [2, 3, 4, 1, 2]
        # women_std = [3, 5, 2, 3, 3]
        width = 0.5       # the width of the bars: can also be len(x) sequence
    
    
        ax = fig.add_subplot(dim,**kargs)
            
        ax.bar(labels, lst_todo, width, bottom=lst_done,label='Planned')#, yerr=women_std
        ax.bar(labels, lst_done, width,  label='Complete',color = 'orange')#yerr=men_std
    
    
        ax.set_ylabel(sec)
        ax.set_title('Week Progress Bar')
        ax.legend()
    
        return fig
    
    1 == 1
###Week Plan Sectional Progress View as Radar
###Example code:
    # fig = plt.Figure()
    # Plot_progress_radar(Profile,fig,'Reward')
    def Plot_progress_radar(self,fig,sec = 'Reward',dim = 111,kargs = {}):
    ##Suppress_Print##
        old_stdout = sys.stdout # Memorize the default stdout stream
        sys.stdout = buffer = io.StringIO()
    ##
        Profile = copy.deepcopy(self.Profile)
        #Start:
        ax = fig.add_subplot(dim,**kargs,polar=True)
        #Data Prep:
        stats_In,stats_out = Progress_Stat(Profile,sec)
        assert all(i<=j for i,j in zip(stats_In , stats_out)),'Error,stats_in must be smaller than stats_out'
        
        labels = np.array(['Family','Health','Personal\nDev','Career'])
        angles_out = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        stats_out = np.concatenate((stats_out,[stats_out[0]]))
        angles_out = np.concatenate((angles_out,[angles_out[0]]))
    
        angles_In = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        stats_In = np.concatenate((stats_In,[stats_In[0]]))
        angles_In = np.concatenate((angles_In,[angles_In[0]]))
    
        #Out
        ax.plot(angles_out, stats_out, 'o-', linewidth=2)
        ax.fill(angles_out, stats_out, alpha=0.25)
        #In
        ax.plot(angles_In, stats_In, 'o-', linewidth=2)
        ax.fill(angles_In, stats_In, alpha=0.5)
    
        ax.set_thetagrids( (angles_out * 180/np.pi) [:-1] ,labels)
        ax.legend(['Planned Progress','Actual Progress'])
        ###
        ax.set_title(f'Week Progress by {sec}')
        ax.grid(True)
    ##
        sys.stdout = old_stdout
        return fig

    1 == 1
###View Week Plan by Orientation (Color Coding Sections)
###Example Code:
    # fig = plt.Figure(figsize=(12,6))
    # Plot_plan_color(fig,Profile,section = 'Reward')
    def Recur_Stat(self , Dict = None ,sec = 'Time', 
           Orientation = {1:'Health',2:'Family',3:'Personal Development',4:'Career'}):
        if Dict is None:
            Dict = {i:{'Family': 0, 'Health': 0, 'Personal Development': 0, 'Career': 0} for i in D.values()}
        else:
            Dict = copy.copy(Dict)
        Profile = copy.deepcopy(self.Profile)
        df = copy.copy(Profile.gpk_Recur.todos)
        for i in range(1,8):
            for idx in df.index:
                row = df.iloc[idx]
                if i in row['Recur_At']:
                    ORI = Orientation[ int ( row['Task Category'] ) ]
                    Day = Dict[D[i]]
                    Day [ORI]+= row[sec]
        return Dict

    def Plot_plan_color(self,fig,df = None,section = 'Reward',
                        dim = 111,width = 0.5, RECUR_show = True, Completed_show = True,
                        Orientation = {1:'Health',2:'Family',3:'Personal Development',4:'Career'},
                        kargs = {}):
        ##Suppress_Print##
            old_stdout = sys.stdout # Memorize the default stdout stream
            sys.stdout = buffer = io.StringIO()
        ##      
            Profile = copy.deepcopy(self.Profile)
            #Data Prep
            if df is None:
                if Completed_show:
                    plan = Plan_Sep(Profile,section,RETURN_new_plan=1)
                else:
                    plan = Profile.okr_plan
                plan_dict = SEC_Stat(plan,agg = 0,sec = section)
                if RECUR_show:
                    plan_dict = self.Recur_Stat(plan_dict,section,Orientation)
                df = Plan_sep_to_dict(plan_dict)
                #display(df)
            #
            labels = list(df.index)
            ax = fig.add_subplot(dim,**kargs)
        
            bottom = np.array([0.0 for _ in df.index])
        
            for sec in df.keys():
                ax.bar(x = labels, height = list(df[sec]) , width = width, label=sec,
                      bottom = bottom)
                bottom += np.array(df[sec]) #Get Prev as bottom
        
            ax.set_ylabel(section)
            ax.set_title(f'Week Plan Section Bar by {section}')
            ax.legend()
        ##
            sys.stdout = old_stdout
            return fig
        
    def RADAR_DPD(self,weekday,fig = plt.Figure(),sec = 'Time',dim = 111,Recur_Show = True,
                  NORMALIZE = True, title = None, kargs = {}):
        if title is None:
            title = f'Week Progress by {sec}' 
            if not Recur_Show: 
                title += ' Recur_Excluded'
        ##Suppress_Print##
        old_stdout = sys.stdout # Memorize the default stdout stream
        sys.stdout = buffer = io.StringIO()
        Profile = copy.deepcopy(self.Profile)
        ###Part 1: 
        #0.Initialize a dict by days
        Dict_date_status = {wkday_to_date(D[wkday]) : {'done':[],'plan':[],'ddl':[]} for wkday in range(1,8)}
        plan_null = Fetch_plan_null(Profile.todos.Load_backup)
    
        #1.Fetch Done 
        Analysis = DF_Analysis(Profile.todos.Archive)
        for date in Dict_date_status:
            conditions = [('date_done',lambda d: d == date),
                                                  ('Quadrant',lambda Q: Q == 2)]
            if not Recur_Show:
                conditions.append(('ID',lambda ID: ID[0] != 'R')) #Filter OUT Recursive Tasks 
                
            temp_df = Analysis.Stack_Search(conditions) 
            Dict_date_status[date]['done'] = Df_to_Gtask(temp_df)
    
        #2.Fetch Plan: 
        planned_Task_IDs = set()
        for wkday in Profile.okr_plan:
            for Gtask in Profile.okr_plan[wkday]:
                planned_Task_IDs.add(Gtask.ID)
                    
        for wkday in Profile.okr_plan:
            if wkday != 'Inbox':
                Dict_date_status[wkday_to_date(wkday)]['plan'] = Profile.okr_plan[wkday]
                if Recur_Show: 
                    List_of_RTask = Df_to_Gtask(Profile.gpk_Recur.task_recur_at(D_rev[wkday]))
                    Dict_date_status[wkday_to_date(wkday)]['plan'] += List_of_RTask
                    #Add It to Deadline Too
                    Dict_date_status[wkday_to_date(wkday)]['ddl'] += List_of_RTask
    
        #3. Fetch Deadline:
        for Gtask in plan_null['Inbox']:
            if Gtask.Deadline is not None:
                if Gtask.Deadline in Dict_date_status.keys():
                    Dict_date_status[Gtask.Deadline]['ddl'].append(Gtask)
                elif DATE(Gtask.Deadline) < DATE(wkday_to_date(D[1])):
                    Dict_date_status[wkday_to_date(D[1])]['ddl'].append(Gtask)
                elif  DATE(Gtask.Deadline) > DATE(wkday_to_date(D[7])):
                    Dict_date_status[wkday_to_date(D[7])]['ddl'].append(Gtask)
            else:
                Dict_date_status[wkday_to_date(D[7])]['ddl'].append(Gtask)
            #Remedy for missing plans (completed)
            if Gtask.ID not in planned_Task_IDs: #Consider Completed 
                print(Gtask.ID)
                #Assume it's PLANNed Monday
                Dict_date_status[wkday_to_date(D[1])]['plan'].append(Gtask)
        ###Part 2:
        #So, In order to plot this, 3 lists would be required: (At given weekday)
        # 1.Actual Progess by Orientation
        # 2.Planned Progress by Orientation
        # 3.Deadline by Orientation 
    
        #1.Calculate total Progress
        total = {1:0,2:0,3:0,4:0}
        for date in Dict_date_status:
            for Gtask in Dict_date_status[date]['ddl']:
                Ori_id = int(Gtask.ID.split('_')[1][1])
                total[Ori_id] += float(eval(f'Gtask.{sec}'))
    
        #2.Calcuate progress for each:
        OUT = {'done':{1:0,2:0,3:0,4:0}, 'plan':{1:0,2:0,3:0,4:0}, 'ddl':{1:0,2:0,3:0,4:0}}
        for tp in ['done', 'plan', 'ddl']:
            for date in Dict_date_status:
                if   DATE(date) <= DATE(wkday_to_date(D[weekday])):
                    for Gtask in Dict_date_status[date][tp]:
                        Ori_id = int(Gtask.ID.split('_')[1][1])
                        OUT[tp][Ori_id] += float(eval(f'Gtask.{sec}'))
    
        #Finally:Normalize by Total (Deadline)
        if NORMALIZE:
            for tp in OUT:
                for i in range(1,5):
                    try:
                        OUT[tp][i] = 100*OUT[tp][i]/total[i]
                    except ZeroDivisionError:
                        OUT[tp][i] = 0
            
        ###Part 3:
        #Start:
        ax = fig.add_subplot(dim,**kargs,polar=True)
        #Data Prep:
        actual = list(OUT['done'].values())
        planned = list(OUT['plan'].values())
        deadline = list(OUT['ddl'].values())
        #assert all(i<=j for i,j in zip(stats_In , stats_out)),'Error,stats_in must be smaller than stats_out'
    
        labels = np.array(['Health','Family','Personal\nDev','Career'])
        angles_out = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        actual = np.concatenate((actual,[actual[0]]))
        planned = np.concatenate((planned,[planned[0]]))
        deadline = np.concatenate((deadline,[deadline[0]]))
    
        angles_In = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        #stats_In = np.concatenate((actual,[actual[0]]))
        angles_In = np.concatenate((angles_In,[angles_In[0]]))
        print(actual)
        print(angles_In)
        
        #Deadline
        ax.plot(angles_In, deadline, '*-', linewidth=2 , color = 'red')
        ax.fill(angles_In, deadline, alpha= 0.25 ,  color = 'red')
        
        #Planned
        ax.plot(angles_In, planned, 'x--', linewidth=2 ,  color = 'blue')
        ax.fill(angles_In, planned, alpha=0.5 ,  color = 'blue')

        #Actual
        ax.plot(angles_In, actual, 'o-', linewidth=2, color = 'orange')
        ax.fill(angles_In, actual, alpha= 0.75 , color = 'orange')
        
        ax.set_thetagrids( (angles_In * 180/np.pi) [:-1] ,labels)
        ax.legend(['Deadline','Planned Progress','Actual Progress'])
        ###
        ax.set_title(title)
        ax.grid(True)
        ##
        sys.stdout = old_stdout
        return fig

class D_Reflection_Frame(tk.Frame):
    def __init__(self,root,geometry,callback  = None,Main = None):
        super().__init__()
        self.root = root
        self.callback = callback
        self.height = geometry['height']
        self.width = geometry['width']
        self.MAIN = Main
        
        #Plotting
        self.Ref_Set_Up()
        
        #Finally:
        self._draw() 
        
        
    def Ref_Set_Up(self):
        Profile = self.callback(Return = True)
        self.R = D_Reflection(Profile, Profile.todos.Archive)
        
    def Frame_Forget(self,loc = [1,2,3,4]):
        self.FrameUPPER.destroy()
        self.FrameLOWER.destroy()
        self._draw()

    
    ### Presets:
    def Call_view(self,View_Num):
        #1.Refresh Data
        self.Ref_Set_Up()
        #2.Draw
        eval(f"self.View{int(View_Num)}()")
        
    def View1(self):
        "Show view of: How did I spent my time today? "
        self.Frame_Forget()
        #Plotting...
        self.Q_Analysis(loc1 = 1, loc2 = 3)
        self.Sectional_Analysis(2)
        self.Task_Done_Today(4)
        
    def View2(self):
        "Show view of: How was my performance? "
        self.Frame_Forget()
        #Plotting...
        self.Score_Changes(1)
        self.Stas_Compare(2)
        self.Week_Progress_StackBar(3)
        self.Week_Progress_Radar(4) 

    def View3(self):
        "Show view of: How did I contribute to my Goals? "
        self.Frame_Forget()
        #Plotting...
        self.Week_Progress_Changes(1)
        self.Score_Changes(2)
        self.Week_Progress_StackBar(3)
        self.Week_Progress_Radar(4) 
        
    def View4(self):
        "Show view of:Efficiency adjustment  "
        self.Frame_Forget()
        #Plotting...
        self.Q_Analysis(1)
        self.Stas_Compare(2)
        self.Week_Progress_StackBar(3)
        self.Score_Changes(4)
        
        
    def View5(self):
        "Show view of: Orientation adjustment  "
        self.Frame_Forget()
        #Plotting...
        self.Sectional_Analysis(1)
        #self.Week_Progress_Radar(2)
        self.Radar_dpd(2 , section = 'Reward')
        self.Week_PlanOrientation_StackBar(3, 'Time')
        self.Week_PlanOrientation_StackBar(4, 'Reward')
    

        
        
    ## Features: 
# 1. List of Tasks done today
    def Task_Done_Today(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        master = self.FRAME[loc]
        df = self.R.Analysis.SEARCH('date_done',
                          lambda date:DATE(date) == datetime.datetime.today().date() 
                          - datetime.timedelta(days = self.R.last_n_day))
        df = df.drop(['time_stamp','ObjectID','Task Category',
                      'KeyResult ID','description','Quadrant','week_day'],axis = 1)
        TreeView = df_to_Treeview(master,df,col_width = 100)
        TreeView.pack()
# 2. Sectional Analysis (pie charts)
    def Sectional_Analysis(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        self.R.Analysis.Rest_fig((8.2,4.5))
        self.R.Analysis.Plot_Sec(n= self.R.last_n_day,dim = 121 , sec = 'Time', title = 'Time Dist') 
        self.R.Analysis.Plot_Sec(n= self.R.last_n_day, dim = 122, sec = 'Reward', title = 'Reward Dist') 
        fig = self.R.Analysis.get_fig()
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
# 3. Quadrant Analysis
    def Q_Analysis(self,loc1,loc2 = None):
        assert loc1 in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc1}'
        assert loc2 in [1,2,3,4,None],f'loc must be in one of the 4 quadrants,given loc: {loc2}'
        
        master1 = self.FRAME[loc1]
        #Plot On Canvas 
        fig = plt.Figure(figsize=(8.2,4.5))
        Q4_lst = self.R.Fetch_Q4_lst()
        fig = self.R.Plot_Q4(fig,Q4_lst,121)
        fig = self.R.Q4_Radar(fig,Q4_lst,122)
        
        canvas = FigureCanvasTkAgg(fig,master1)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        #Show Prediction 
        _type = self.R.Quadrant_Which(Q4_lst)
        self.img = Image.open(os.getcwd() + f'/Pictures/Q4_Type{_type}.png')
        img_size = (800,360)
        self.img = self.img.resize(img_size, Image.ANTIALIAS)
        self.Sugguestion_img = ImageTk.PhotoImage(self.img)
        if loc2 is not None:    
            lab = tk.Label(self.FRAME[loc2], image = self.Sugguestion_img)
            lab.pack()
           
# 4. Daily Statistic comparing to the average 
    def Stas_Compare(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        fig = plt.Figure((8.2,4.5))
        fig = self.R.Plot_Comparison(fig,dim = 121, sec = 'Time')
        fig = self.R.Plot_Comparison(fig,dim = 122, sec = 'Reward')
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
# 5. Score changes  
    def Score_Changes(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        self.R.Analysis.Rest_fig((8.2,4.5))
        self.R.Analysis.Plot_Score(self.R.Profile.todos.Load_backup)
        fig = self.R.Analysis.get_fig()
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
# 6. Week Progress Changes  
    def Week_Progress_Changes(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        Load_yesterday,DICT= Get_Scores(df = self.R.Profile.todos.Archive,
                                        Loaded = self.R.Profile.todos.Load_backup,
                         target = str(datetime.datetime.today().date()),RETURN_null=True)
        Progress = self.R.Progress_Collect(Load_yesterday,DICT)
        
        Txt = tk.Text(master,height = 20, width = 75, bg = "light cyan")
        Txt.configure(font=("Times New Roman", 14, "bold"))
        Txt.pack()
        Txt.delete("1.0","end")
        Txt.insert("1.0", Progress)
        
# 7. Week Progress Stack Bar
    def Week_Progress_StackBar(self,loc):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        fig = plt.Figure(figsize = (8.2,4.5))
        fig =  self.R.Plot_progress_bar(fig)
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
# 8. Week Progress Radar Plot
    def Week_Progress_Radar(self,loc,sec = 'Reward'):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        fig = plt.Figure(figsize = (8.2,4.5))
        fig =  self.R.Plot_progress_radar(fig,sec )
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
# 9. Week Plan Orientation Stack Bar  
    def Week_PlanOrientation_StackBar(self,loc,section = 'Reward'):
        assert loc in [1,2,3,4],f'loc must be in one of the 4 quadrants,given loc: {loc}'
        
        master = self.FRAME[loc]
        fig = plt.Figure(figsize = (8.2,4.5))
        fig =  self.R.Plot_plan_color(fig,section = section)
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
# 10. Radar plot by completion,deadline and plan:
    def Radar_dpd(self,loc,section = 'Reward'):
        master = self.FRAME[loc]
        fig = plt.Figure(figsize = (8.2,4.5))
        fig =  self.R.RADAR_DPD(weekday = weekday_today(),fig = fig , sec = section, dim = 121) 
        fig =  self.R.RADAR_DPD(weekday = weekday_today(),fig = fig , sec = section, 
                                dim = 122 , Recur_Show = False) 
        canvas = FigureCanvasTkAgg(fig,master)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 0, column = 0)
        
    def _draw(self): 
        self.FRAME = dict()
        ###Upper Frame###
        self.FrameUPPER = tk.Frame(master = self, bd = 20 )#, bg = 'Blue')
        self.FrameUPPER.configure(height = self.height/2 ,width = self.width)
        self.FrameUPPER.pack()
        ###Q1:
        self.Upper_Left = tk.Frame(master = self.FrameUPPER, bd = 20 )#, bg = 'green')
        self.Upper_Left.pack(side = tk.LEFT, fill = 'both', padx = 10, pady = 10)
        self.Upper_Left.configure(height = 1/2*self.height,
                                  width = 1/2*self.width)
        self.FRAME[1] = self.Upper_Left
        ###Q2:
        self.Upper_Right = tk.Frame(master = self.FrameUPPER, bd = 20 )#, bg = 'purple')
        self.Upper_Right.pack(side = tk.LEFT, fill = 'both', padx = 10, pady = 10)
        self.Upper_Right.configure(height = 1/2*self.height,
                                  width = 1/2*self.width)
        self.FRAME[2] = self.Upper_Right
        ###Lower Frame### (Middle) 
        self.FrameLOWER = tk.Frame(master = self, bd = 2 )#, bg = 'yellow')
        self.FrameLOWER.configure(height = self.height/2 ,width = self.width)
        self.FrameLOWER.pack()
        
        ###Q3:
        self.LOWER_Left = tk.Frame(master = self.FrameLOWER, bd = 20 )#, bg = 'pink')
        self.LOWER_Left.pack(side = tk.LEFT, fill = 'both', padx = 10, pady = 10)
        self.LOWER_Left.configure(height = 1/2*self.height,
                                  width = 1/2*self.width)
        self.FRAME[3] = self.LOWER_Left
        ###Q4:
        self.LOWER_Right = tk.Frame(master = self.FrameLOWER, bd = 20 )#, bg = 'orange')
        self.LOWER_Right.pack(side = tk.LEFT, fill = 'both', padx = 10, pady = 10)
        self.LOWER_Right.configure(height = 1/2*self.height,
                                  width = 1/2*self.width)
        self.FRAME[4] = self.LOWER_Right
    
if __name__ == '__main__':
    #Profile 
    User_name = 'LEO'#'Leo_TEST'##
    file_path = f"D:\GPK\gpk_saves\\{User_name}_user_file.gpk"
    if True:#int(input('Batch Test? 1 or 0')):
        with open(file_path,'rb') as INfile:
            Profile = pickle.load(INfile)
        T = D_Reflection(Profile, Profile.todos.Archive)
        
        # # 1. List of Tasks done today   
        # print('\n->Checking:1. List of Tasks done today  ')
        # print(T.Analysis.SEARCH('date_done',
        #                   lambda date:DATE(date) == datetime.datetime.today().date() 
        #                   - datetime.timedelta(days = T.last_n_day)).head() )
        # # 2. Sectional Analysis (pie charts)   
        # print('\n->Checking:2. Sectional Analysis (pie charts)')
        # T.Analysis.Plot_Sec(n=1)
        # #T.Analysis.fig_preview()
        # # 3. Quadrant Analysis   
        # #     1. Q4 Plots:  
        # #         a.Today  
        # #         b.This Week  
        # #         c.All Time    
        # #     2. Suggestions, which type of person you are (According to 7 Habits) 
        # print('\n->Checking:3. Quadrant Analysis   ')
        # fig = plt.Figure(figsize=(10,5))
        # Q4_lst = T.Fetch_Q4_lst()
        # fig = T.Plot_Q4(fig,Q4_lst,121)
        # fig = T.Q4_Radar(fig,Q4_lst,122)
        # #display(fig)
        # T.Analysis.fig = fig 
        # T.Analysis.fig_preview()
        # _type = T.Quadrant_Which(Q4_lst)
        # Sugguestion_img = Image.open(os.getcwd() + f'/Pictures/Q4_Type{_type}.png')
        # Sugguestion_img.resize((550,260))
        # # 4. Daily Statistic comparing to the average 
        # print('\n->Checking: 4. Daily Statistic comparing to the average   ')
        # fig = plt.Figure()
        # fig = T.Plot_Comparison(fig,Profile)
        # T.Analysis.fig = fig 
        # T.Analysis.fig_preview()
        # # 5. Score changes  
        # print('\n->Checking: 5. Score changes  ')
        # T.Analysis.fig = plt.Figure()
        # T.Analysis.Plot_Score(T.Profile.todos.Load_backup)
        # T.Analysis.fig_preview()
        # # 6. Week Progress Changes  
        # print('\n->Checking: 6. Week Progress Changes  ')
        # Load_yesterday,DICT= Get_Scores(df = T.Profile.todos.Archive,Loaded = T.Profile.todos.Load_backup,
        #                  target = str(datetime.datetime.today().date()),RETURN_null=1)
        # Progress = T.Progress_Collect(Load_yesterday)
        # print(Progress)
        # # 7. Week Progress Stack Bar
        # print('\n->Checking:  7. Week Progress Stack Bar ')
        # fig = plt.Figure()
        # T.Analysis.fig =  T.Plot_progress_bar(fig)
        # T.Analysis.fig_preview()
        # # 8. Week Progress Radar Plot
        # print('\n->Checking: 8. Week Progress Radar Plot')
        # fig = plt.Figure()
        # T.Analysis.fig =  T.Plot_progress_radar(fig,'Reward')
        # T.Analysis.fig_preview()
        # 9. Week Plan Orientation Stack Bar 
        print('\n->Checking:9. Week Plan Orientation Stack Bar ')
        fig = plt.Figure()
        T.Analysis.fig =  T.RADAR_DPD(2,fig,NORMALIZE = True,sec = 'Reward',Recur_Show=False)
        T.Analysis.fig_preview()
    else:
        root = tk.Tk()
        root.attributes("-fullscreen", True)  
        from gpk_todo_frame import Profile_Test
        T = Profile_Test(file_path)
        #Geom
        base = 100
        width = base*16
        height = base*10
        geometry = {'width':width,'height':height}
        ###
        temp = D_Reflection_Frame(root,geometry ,T.Profile_call_back,Main = T)
        temp.pack()
        root.mainloop()