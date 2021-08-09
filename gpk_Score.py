import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tkinter import messagebox
import pickle
from GPK_PROFILE import *
import datetime
import random
from Plan_load import progress

def DATE(String):
    import datetime
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
  
  
def score_okr(Load):
    "Evaluate the weekly performance based on completion progress and pre-assigned weight "
    weight_total = 0
    PG_list = []
    Wt_list = []
    try:
        for objective in Load.WeekObjective.Priority_Task:
            weight_total += objective.weight
            PG_list.append(objective.PG)
            Wt_list.append(objective.weight)
        for objective in Load.WeekObjective.Special_Task:
            weight_total += objective.weight
            PG_list.append(objective.PG)
            Wt_list.append(objective.weight)
        for objective in Load.WeekObjective.Recursive_Task:
            weight_total += objective.weight
            PG_list.append(objective.PG)
            Wt_list.append(objective.weight)
    except Exception as e:
        print(f"ERROR,Fail to calculate the score due to...{e}")
        return 0
    return  100*sum(np.array(Wt_list)*np.array(PG_list))/weight_total

def grade_okr(score):
    "Convert the score into letter grade"
    if score > 95:
        grade = "S"
    elif 85 < score < 95:
        grade = "A" 
    elif 75 < score < 85:
        grade = "B"
    elif 65 < score < 75:
        grade = "C"
    elif 55 < score < 65:
        grade = "D"
    else:
        grade = "F"
    return grade 

def letter_grade_reward(grade):
    "Return Reward Corresponding to the letter Grade"
    Reward_Table = {"D":"🍑🍑","C":"🍒","B":"🍇","A":"🍇🍇","S":"👑"}
    if grade in Reward_Table:
        return(Reward_Table[grade])
    else:
        print("Error,Invalid Grade")

def grade_tracker(Load,last_score = None):
    score_table = {"S":95,"A":85,"B":75,"C":65,"D":55,"F":0}
    "Track if you have gained next level"
    if last_score == None:
        last_score = score_okr(Load)
    last_letter_grade = grade_okr(last_score)
    score = score_okr(Load)
    print(score)
    current_letter_grade = grade_okr(score)
    next_level = chr(ord(current_letter_grade) - 1)
    gap = 10
    if next_level == "@":
        next_level = "S"
    elif next_level == "E":
        next_level = "D"
        gap = 55
    if current_letter_grade != last_letter_grade:#If Get into the next level
        try:
            print("CONGRATS!\nYour Current Grade is:{}".format((current_letter_grade)))
        except:
            print("Your Current Grade is:{}".format(current_letter_grade))
        if True:
            img_print(awesome_img)
            print("Prize: {}".format(letter_grade_reward(current_letter_grade)))
            data["balance"] += token_list_reverse(letter_grade_reward(current_letter_grade))
    print("Prize for Next Level {}:{}".format(next_level,letter_grade_reward(next_level)))
    progress(1 - ((score_table[next_level]-score)/gap))


# In[39]:

#@title Score Projection Plot mod {display-mode: "form"}


# #@title Score Projection Plot mod {display-mode: "form"}
def Score_trend(Dict):
    "Given Past Score Level, Project the score level"
    first_day = list(Dict)[0]
    Pred = trend(list(Dict.values()))
    OUT = {}
    day = first_day
    for idx in range(7):
        OUT[day] = Pred[idx]
        day = str(tmr(str(day)))
    return OUT

def trend(L,n=7):
    "trend takes in a list and if it's no longer than n, it makes a projection based on its previous values"
    if L == []:
        L = [0]
    try:
        while len(L)< n:
            L.append(L[-1]+(L[-1]/len(L)))
        return(L)
    except IndexError as ie:
        print("{} has wrong format".format(L))
        print(ie)

def now(L,n=7):
    "now takes in a list and if it's no longer than n, it fills with the last item untill it's length n"
    if L == []:
        L = [0]
    while len(L) < n:
        L.append(L[-1])
    return L

def constant_line(n):
    return [n,n,n,n,n,n,n]

def score_plt(Lst,Save=False,path = None,
              grade_cutoff = {"D":(55,'r'),"C":(65,'y'),"B":(75,'b'),"A":(85,'g'),"S":(95,'m')}):
    from matplotlib.pyplot import figure
    figure(figsize=(8,8))
    Trend = trend(list(Lst))
    Now = now(list(Lst))
    WEEKDAYS = ["Mon","Tue","Wed","Thur","Fri","Sat","Sun"]
    for grade in grade_cutoff.keys():
        plt.plot(WEEKDAYS,constant_line(grade_cutoff[grade][0]),label = grade,linestyle='dashed',color = grade_cutoff[grade][1])
    
    print(Now)
    print(Trend)
    plt.plot(WEEKDAYS,Now,label = "NOW")
    plt.plot(WEEKDAYS,Trend,label = "Projection",linestyle='dashdot')
    
    plt.legend()
    plt.title("Score Projection")
    if Save:
        plt.savefig(path)
    else:
        plt.show()
    
    
    
####NEW####2021/7/5
def yesterday(date_str):
    return (DATE(date_str) - datetime.timedelta(days = 1))

def tmr(date_str):
    return (DATE(date_str) + datetime.timedelta(days = 1))

def Last_monday(today = None):

        if today is None:
            today = datetime.datetime.now().date()
        date = DATE(str(today))
        while date.isocalendar()[2] != 1:
            date = yesterday(str(date))
        return (date)

def Next_Sunday(today = None):
    if today is None:
        today = datetime.datetime.now().date()
    date = DATE(str(today))
    while date.isocalendar()[2] != 7:
        date = tmr(str(date))
    return (date)

def NULL_WO(Loaded , set_to = 0 ):
    OUT = copy.deepcopy(Loaded)
    sections = ['Priority_Task','Special_Task','Recursive_Task']
    for sec in sections:
        for okr_task in eval(f"OUT.WeekObjective.{sec}"):
            okr_task.PG = set_to
    return OUT
    
def Get_Scores(df,Loaded,today = None, RETURN_null = False, Auto_fill = False, target = None ):
    "Takes in a df which is usually the PROFILE.todos.Archive,Out Puts"
    Analysis = DF_Search(df)
    #1.Find the date of the LAST Monday, could be today
    start = str(Last_monday(today))
    end = str(Next_Sunday(today))
    print(f"calling:Get_Score,from {start} to {end}")
    #2.Isolate the data
    df_new = Analysis.SEARCH('date_done',predict = lambda dt: DATE(dt) >= DATE(start) and  DATE(dt) <= DATE(end))
    #3.Sort the data by date_done:
    try:
        df_new = df_new.sort_values(by = 'date_done', key = lambda L: [DATE(i) for i in L],ascending = True)
    except KeyError: #Archive is empty 
        df_new = pd.DataFrame() 
    #4.Get a dictionary with key = date_done, values = list of tasks completed that day
    DICT = {}
    if Auto_fill:
        #Set Up the Dict to the fullest
        if today is None:
            today = datetime.datetime.now().date()
        date = str(today)
        while str(date) != end:
            DICT[date] = []
            date = str(tmr(date))
        DICT[str(date)] = []
            ##

    for idx in range(len(df_new)):
        row = df_new.iloc[idx]
        if row['date_done'] not in DICT:
            DICT[row['date_done']] = [row['ID']]
        else:
            DICT[row['date_done']].append( row['ID'] )

    #5.Create a NULL version of the Load, defaulting all PG for ALL tasks:
    WO_null = NULL_WO(Loaded)
    #6.For each day, complete all tasks and collect score
    OUT = {}
    for day in DICT:
        if target is None or DATE(day) < DATE(target):
            for task_id in DICT[day]:
                WO_null.complete(task_id)
            OUT[day] = score_okr(WO_null)
    if RETURN_null:
        return WO_null,DICT
    
    if OUT == {}:
        OUT = {start : 0 } #In the case when it's new week
    return OUT