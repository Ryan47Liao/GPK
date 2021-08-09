"""
This mod is dedicated to RSA encryption      

@author: Leonidas Liao
Creation Date: 
"""
import random 
from random import randrange
import numpy as np

class RSA:
    def __init__(self, keychain = None, n = None, D = None):
        #Initialization
        if D is None:
            self.__DICT_sd = {"a":"01","b":"02","c":"03","d":"04","e":"05","f":"06","g":"07","h":"08","i":"09","j":"10","k":"11",
      "l":"12","m":"13","n":"14","o":"15","p":"16","q":"17","r":"18","s":"19","t":"20","u":"21","v":"22",
       "w":"23","x":"24","y":"25","z":"26"," ":"27",",":"28","!":"29",".":"30","?":"31",":":"32","@":"33"}
            for d in dict(self.__DICT_sd).keys():
                d_u = d.upper()
                if d_u in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.__DICT_sd[d_u] = str( len(self.__DICT_sd) + 1 )
        else:
            self.__DICT_sd = D
        self.__DICT_ds = {d:s for d,s in zip(self.__DICT_sd.values(),self.__DICT_sd.keys())}
        #Generate Key Pairs 
        if keychain is not None:
            self.N = keychain['N']
            self.e = keychain['e']
            self.d = keychain['d']
        else:
            if n is not None:
                self.N,self.e,self.d = RSA.RSA_sys(n)
        
    def _showKeys(self):
        print(f"N:{self.N},\ne:{self.e},\nd:{self.d}")
        
    class RSA_Exception(Exception):
        pass
    
    @staticmethod  
    def IsDigit(entry):
        try:
            int(entry)
            return True
        except ValueError:
            return False
        
    def digit_translate(self,IN):
        "Take input IN as either a letter or a digit, return the corresponding code"
        if self.IsDigit(IN):
            #Input is digit
            if len(str(IN)) == 1:
                IN = '0' + str(IN)
            if str(IN) in self.__DICT_ds:

                return self.__DICT_ds[str(IN)]
            else:
                raise self.RSA_Exception(f"String {IN} is INVALID. To be implemented in the future")
        else:
            #Input is string 
            if IN in self.__DICT_sd:
                return self.__DICT_sd[str(IN)]
            else:
                print("!")
                return random.randint(a = 1, b = len(self.__DICT_ds))
                
    def translate(self,STR):
        if self.IsDigit(STR):
            #If Digit 
            #Check missing header:
            STR = str(STR)
            if len(STR) % 2 == 1:
                STR = '0' + STR
            STR = [STR[idx]+STR[idx+1] for idx in range(0,len(str(STR))-1,2)]
        Lst = [self.digit_translate(IN) for IN in STR]
        Out = ""
        for digit in Lst:
            Out += str(digit) 
        return Out
    
    @staticmethod 
    def RSA_sys(n):
        print("Generating Public Keys and Private Keys")
        #finds p,q that are two prime numbers with many digits 
        p = Prime_gen.prime_gen(n)
        q = Prime_gen.prime_gen(n)
        #Generate Public_key_1:N
        N = p*q
        phi = (p-1)*(q-1)
        #Generate Public_key_2:e
        e = Prime_gen.get_e(phi)
        #Generate Private_key:d
        d = Prime_gen.get_mul_inv(e,phi)
        return N,e,d
    
    def ENC(self,message):
        "Message is plain test, return encrypted digit"
        m = int(self.translate(message))
        C = pow(m,self.e,self.N)
        return(C)
    
    def DEC(self,C):
        "C is encrypted digit, return plain text"
        m = pow(C,self.d,self.N)
        return(self.translate(m))
    
class Prime_gen:
    def __init__(self):
        pass 
    
    @staticmethod 
    def is_prime(n, k=128):
        """ Test if a number is prime
            Args:
                n -- int -- the number to test
                k -- int -- the number of tests to do
            return True if n is prime
        Credit to: https://medium.com/@prudywsh/how-to-generate-big-prime-numbers-miller-rabin-49e6e6af32fb
        """
        # Test if n is not even.
        # But care, 2 is prime !
        if n == 2 or n == 3:
            return True
        if n <= 1 or n % 2 == 0:
            return False
        # find r and s
        s = 0
        r = n - 1
        while r & 1 == 0:
            s += 1
            r //= 2
        # do k tests
        for _ in range(k):
            a = randrange(2, n - 1)
            x = pow(a,r,n)
            if x != 1 and x != n - 1:
                j = 1
                while j < s and x != n - 1:
                    x = pow(x, 2, n)
                    if x == 1:
                        return False
                    j += 1
                if x != n - 1:
                    return False
        return True
    
    @staticmethod
    def prime_gen(n):
        def num_gen(n):
            output = "0"
            num = np.random.randint(10, size=(1, n))
            num = num[0]
            for i in range(len(num)):
                output = output + str(num[i])
            output = output[1::]
            if output[0]== "0":
                output = str(np.random.randint(1,10))+output[1::]
            return(int(output))
        p = 4
        while 1*(Prime_gen.is_prime(p))==0: 
            p = num_gen(n)
        return(p)   
    
    @staticmethod
    def GCD(a,b):
        if a < b:
            temp_b = a
            temp_a = b
            a = temp_a 
            b = temp_b
        if a % b == 0:
            return(b)
        else: 
            return(Prime_gen.GCD(b,a % b))
    
    @staticmethod
    def get_e(n):
        for i in range(int(n)):
            i = i + 2
            if Prime_gen.GCD(i,n)==1:
                return(i)
            
    @staticmethod
    def gcdExtended(a, b):  
        # Base Case  
        if a == 0 :   
            return b, 0, 1
                     
        gcd, x1, y1 = Prime_gen.gcdExtended(b%a, a)  
         
        # Update x and y using results of recursive  
        # call  
        x = y1 - (b//a) * x1  
        y = x1  
        return gcd, x, y 
    
    @staticmethod
    def get_mul_inv(e,phi):
        _, x, _ = Prime_gen.gcdExtended(e,phi) #gcd,x,y
        return(x%phi)
    
    
    
if __name__ == '__main__':
    print("___Start___")
    Test = RSA(n = 50)
    Test._showKeys()
    C = Test.ENC("hello, my Name is Leonidas Liao.")
    print(C)
    M = Test.DEC(C)
    print(M)
    print("___Done___")