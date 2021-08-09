#!/usr/bin/env python
# coding: utf-8

from math import floor
from IPython.core.display import display
from Plan_load import task

class gpk_task(task):
    def __init__(self,name,notes = None,
                 sections = {1:'Health',2:'Family',3:'Personal Development',4:'Carrer',5:'other'},
                 **kargs):
        """
        **kargs:
        -ID
        -Reward
        -Time
        -Difficulty
        -Description
        -Deadline 
        """
        self.Deadline = None #Default no Deadline
        self.name = name 
        self.note = notes
        self.SECTIONs = sections
        if notes != None:
            T = notes.split('\n\n')
            self.ID = T[0].split(':')[1]
            self.Reward = float_str(T[1].split('\n')[1]).getvalue()
            self.Time = float_str(T[1].split('\n')[3]).getvalue()
            self.Difficulty = float_str(T[1].split('\n')[5]).getvalue()
            self.Description= T[1].split('\n')[7]
        else:
            try:
                self.ID = kargs['ID']
                self.Reward = kargs['Reward']
                self.Time = kargs['Time']
                self.Difficulty = kargs['Difficulty']
                self.Description= kargs['Description']
                self.Deadline = kargs['Deadline']
            except Exception as e:
                print(e)
        self.ID_intepret()
        

    def ID_intepret(self):
        #ID is of format "S_G4-3_K1" #Special/Recurrent/Priority_Goal#_KeyResult#
        category = self.ID[0]
        if category.upper() == 'S':
            self.category = 'Special'
        elif category.upper() == 'R':
            self.category = 'Recurrent'
        elif category.upper() == 'P':
            self.category = 'Priority'
        section = int(self.ID.split("_")[1][1])
        self.section = self.SECTIONs[section]
        self.Kr_Id = self.ID.split("_")[2][-1]
        
    def __repr__(self):
        return f"""
ID:{self.ID}

`Reward`
{str(float_str(self.Reward,"$"))}
`Time`
{str(float_str(self.Time))}
`Difficulty`
{str(float_str(self.Difficulty))}
`Description`
{self.Description}
               """
    
    def Get_notes(self):
        "Return notes (MTK ready)"
        return self.__repr__() 




class float_str:
    "A class that represents number in a more visually intuitive way: 3 -> ***"
    from math import floor
    def __init__(self,value,token = "*"):
        try:
            self.value = float(value)
        except ValueError :
            if len(set(value)) < 3:
                if value[-1] == '%':
                    self.value = len(value) - 0.5 
                elif len(set(value)) == 1:
                    self.value = len(value)
        self.set_token(token)
        
    def getvalue(self):
        return self.value 
    
    def get_token(self):
        return self.__token 
    
    def set_token(self,token):
        self.__token = token 
        
    def __repr__(self):
        if self.getvalue() == 0:
            REP = '%'
        else:
            REP = self.get_token()*floor(self.getvalue())
            if self.getvalue() - floor(self.getvalue()) > 1e-3:
                REP += "%" 
        return REP
    
    def __float__(self):
        return self.value


# In[113]:


if __name__ == '__main__':
    note = 'ID:S_G4-3_K1\n\n[Reward]\n 5.0\n[Time]\n 1.5\n[Difficulty]\n 3.0\n[Description]\n None\n\n-Sent From Colab, Powered by Python\n'
    T = gpk_task('test',note)
    note2 = T.Get_notes()
    T2 = gpk_task('test2',note2)
    print(T2)

