#!/usr/bin/env python
# coding: utf-8

# In[1]:


#@title Fundamental Module of RSA system {display-mode: "form"}

# This code will be hidden when the notebook is loaded.
#Other Mods:
import numpy as np
import random

def Ecp(L):
    DICT = {"a":"01","b":"02","c":"03","d":"04","e":"05","f":"06","g":"07","h":"08","i":"09","j":"10","k":"11",
      "l":"12","m":"13","n":"14","o":"15","p":"16","q":"17","r":"18","s":"19","t":"20","u":"21","v":"22",
       "w":"23","x":"24","y":"25","z":"26"," ":"27",",":"28","!":"29",".":"30","?":"31",":":"32","@":"33"}
    if L.isupper():
        L = str.lower(L)
    return DICT[str(L)]
    
#
def Decp(L):
    DICT = {"a":"01","b":"02","c":"03","d":"04","e":"05","f":"06","g":"07","h":"08","i":"09","j":"10","k":"11",
      "l":"12","m":"13","n":"14","o":"15","p":"16","q":"17","r":"18","s":"19","t":"20","u":"21","v":"22",
       "w":"23","x":"24","y":"25","z":"26"," ":"27",",":"28","!":"29",".":"30","?":"31",":":"32","@":"33"}
    Items = list(DICT.items())
    for i in range(len(Items)):
        if str(L) == Items[i][1]:
            return Items[i][0]
    return(str.lower(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
#
def Encrptor(string):
    code = []
    for i in range(len(string)):
        code = np.append(code,Ecp(string[i]))
    return(code)

def Decrptor(string):
    message = []
    for i in range(len(string)):
        message = np.append(message,Decp(string[i]))
    return(message)   
#
def Concat (arr):
    output = "1"
    for i in range(len(arr)): 
        output = output + arr[i]
    return(int(output[1::]))

def translate(num):
    arr = []
    NUM = str((num))
    if len(NUM)%2 != 0:
        NUM = "0"+NUM
    N = int(len(NUM)/2)
    for i in range(N):
        arr = np.append(arr,NUM[2*i:2*i+2])
    return(arr)

def read(num_string):
    arr = translate(num_string)
    arr = Decrptor(arr)
    output = "~"
    for i in range(len(arr)): 
        output =  output + arr[i]
    return(str.capitalize(output[1::]))

def encode(plaintext):
    plaintext  = Encrptor(plaintext)
    return(Concat(plaintext))

#Credit to: https://medium.com/@prudywsh/how-to-generate-big-prime-numbers-miller-rabin-49e6e6af32fb
from random import randrange, getrandbits
def is_prime(n, k=128):
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
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
        x = mod(a,r,n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = mod(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

# Module1: Prime Generator 
def isprime(N):
    if N % 2 == 0:
        return False
    for x in range(3,int(sqrt(N))+1,2):
        if N % x == 0:
            return False 
    return True

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

def prime_gen(n):
    p = 4
    while 1*(is_prime(p))==0: 
        p = num_gen(n)
    return(p)    
    
#Gcd Module
def GCD(a,b):
    if a < b:
        temp_b = a
        temp_a = b
        a = temp_a 
        b = temp_b
    if a % b == 0:
        return(b)
    else: 
        return(GCD(b,a % b))
    
# Python program to demonstrate working of extended  
# Euclidean Algorithm  
     
# function for extended Euclidean Algorithm  
def gcdExtended(a, b):  
    # Base Case  
    if a == 0 :   
        return b, 0, 1
                 
    gcd, x1, y1 = gcdExtended(b%a, a)  
     
    # Update x and y using results of recursive  
    # call  
    x = y1 - (b//a) * x1  
    y = x1  
    return gcd, x, y 

# mod calculates (x**y%n)
def mod(x,y,n):
    p = 1
    s = x
    r = y
    while r > 0:
        if r % 2 == 1:
            p = p*s % n
        s = s*s % n 
        r = r // 2 
    return(p)

#RSA Module 
def get_e(n):
    for i in range(int(n)):
        i = i + 2
        if GCD(i,n)==1:
            return(i)
        
def get_mul_inv(e,phi):
    gcd, x, y = gcdExtended(e,phi)
    return(x%phi)

def RSA_sys(n):
    print("Generating Public Keys and Private Keys")
    #finds p,q that are two prime numbers with many digits 
    p = prime_gen(n)
    q = prime_gen(n)
    #Generate Public_key_1:N
    N = p*q
    phi = (p-1)*(q-1)
    #Generate Public_key_2:e
    e = get_e(phi)
    #Generate Private_key:d
    d = get_mul_inv(e,phi)
    return N,e,d

def ENC(message,N,e):
    m = encode(message)
    C = mod(encode(message),e,N)
    return(C)

def DEC(C,N,d):
    m = mod(C,d,N)
    return(read(m))


# In[ ]:




