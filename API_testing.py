'''
Created on Jun 14, 2021

@author: alienware
'''
import requests 

class MTK:
    def __init__(self,token = None):
        self.set_token(token)
        
    def set_token(self,token):
        self.__token = token 
        self.headers =  {'Accept' : '*/*',
          'Authorization': f'Bearer {self.__token}',
           'accept-encoding' : 'gzip, deflate'}
        
    def Get_task(self,id = ""):
        return requests.request(method = "GET", url = f"https://www.meistertask.com/api/tasks/{id}",
                                headers = self.headers).text
    
if __name__ == '__main__':
    TST = MTK('u1IqrMvqjFA99sNL9_RnipaYnXKd9cc7wUZXHCUhJ-I')
    print(TST.Get_task())