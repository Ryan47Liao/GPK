import pickle 

class GPK_Cache:
    def __init__(self,file_path,AC = None,PW = None):
        self.file_path = file_path
        self.gpk_save_path = None 
        self.__account = AC 
        self.__password = PW 
        self.__remember = False 
        self.save()
        
    def set_save_path(self,path):
        self.gpk_save_path = path
        
    def Re_status(self):
        return self.__remember 
    
    def get_AC(self):
        if self.Re_status():
            return self.__account 
        else:
            return ""
    
    def get_PW(self):
        if self.Re_status():
            return self.__password 
        else:
            return ""
    
    def set_info(self,ac,pw):
        self.__account = ac
        self.__password = pw
    
    def save(self):
        OUTfile = open(self.file_path ,"wb")
        pickle.dump(self,OUTfile)
        OUTfile.close()
        
    def Re_True(self):
        self.__remember = True  
        
    def Re_Fal(self):
        self.__remember = False  
        
    def Set_status(self,status):
        status = bool(status) 
        print(f'Setting Remember Status:{status}')
        if status:
            self.Re_True()
        else:
            self.Re_Fal()
        self.save()