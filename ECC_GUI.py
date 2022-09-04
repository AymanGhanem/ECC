#!/usr/bin/env python
# coding: utf-8

# In[5]:


import math
import sympy
from sympy import mod_inverse
import random
from tkinter import *
import tkinter as tk
random.seed(30)

class Point(object):
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def __str__(self):
        return f"Point({self.a},{self.b})"
    
    def __repr__(self):
        return f"Point({self.a},{self.b})"
    
    def __eq__(self, other):
        if(not(isinstance(other, Point))):
            raise NotImplementedError(f"Can not perform equality check between a Point object and {type(other)} object.")
        if(self.a == other.a and self.b == other.b):
            return True
        return False
    
    def __hash__(self):
        return hash(repr(self))
    
    def get_x(self):
        return self.a
    
    def get_y(self):
        return self.b
    
    
class EC(object):
    
    def __init__(self, a, b, p):
        print("---------------Initializing the curve---------------")
        self.a = a
        self.b = b
        self.p = p
        print("The curve is : ", self)
        print("---------------Curve is initialized-----------------")
        
    def __str__(self):
        return f"(x3 + {self.a} x + {self.b}) mod {self.p}"
    
    def __repr__(self):
        return f"(x3 + {self.a} x + {self.b}) mod {self.p}"
    
    def get_y_of_x(self, x):
        y_squared = (x**3 + x * self.a + self.b) % self.p
        while(True):
            for y in range(self.p):
                if(((y*y) % self.p) == y_squared):
                    return Point(x, y)
            x += 1
            y_squared = (x**3 + x * self.a + self.b) % self.p
            
    def is_point(self, point):
        eq1 = (point.get_x() ** 3 + self.a * point.get_x() + self.b) % self.p
        eq2 = (point.get_y() ** 2) % self.p
        if(eq1 == eq2):
            print("POint : ", point)
        return eq1 == eq2
    
    def get_ECC_points(self):
        points = set()
        length = range(self.p)
        for x in length:
            value1 = (x**3 + self.a * x + self.b) % self.p
            for y in length:
                value2 = (y * y) % self.p
                if(value1 == value2):
                    points.add(Point(x,y))
                    points.add(Point(x, -y % self.p))
        return points
    
    
    def add_points(self, point1, point2):
        o = Point(None,None)
        if(o == point1):
            return point2
        if(o == point2):
            return point1
        if((point1.get_y() == (-point2.get_y() % self.p)) and (point1.get_x() == point2.get_x())):
            return Point(None, None)
        if(point1 != point2):
            delta = (point2.get_y() - point1.get_y()) * mod_inverse((point2.get_x() - point1.get_x()), self.p) % self.p
            x3 = (delta**2 - point1.get_x() - point2.get_x()) % self.p
            y3 = ((point1.get_x() - x3) * delta - point1.get_y()) % self.p
            return Point(x3, y3)
        else:
            delta = ((3 * point1.get_x()**2 + self.a) * mod_inverse(2*point1.get_y(), self.p)) % self.p
            x3 = (delta**2 - 2*point1.get_x()) % self.p
            y3 = ((point1.get_x() - x3) * delta - point1.get_y()) % self.p
            return Point(x3, y3)
        
    def reverse_point(self, point):
        return Point(point.get_x(), (-point.get_y()) % self.p)
    
    def multiply_point(self,point,k):
        if(not(isinstance(k,int)) or (not(isinstance(point, Point)))):
            print("K ", k, type(k))
            print("P ", point, type(point))
            raise NotImplementedError("This operation is not implemented")
        result_point = Point(None,None)
        for _ in range(k):
            result_point = self.add_points(result_point,point)
        return result_point
    
    def double_point(self, point):
        return self.add_points(point,point)
    
    def fast_multiply_point(self, point, k):
        if(not(isinstance(k,int)) or (not(isinstance(point, Point)))):
            raise NotImplementedError("This operation is not implemented")
        binary_k = bin(k)[3:]
        result_point = point
        for i in binary_k:
            if(i=='0'):
                result_point = self.double_point(result_point)
            else:
                result_point = self.double_point(result_point)
                result_point = self.add_points(result_point, point)
        return result_point
    
class Encyption(object):
    
    def __init__(self, ec):
        self.ec = ec
        self.n = 8
        self.p_bits = len(bin(ec.p)[2:])
        
    def convert_message_to_points(self, message):
        print("----------------Start converting message to a list of points--------------------")
        block_size = (self.p_bits - self.n) // 8
        if(block_size <= 0):
            raise Exception(f"p = {self.ec.p} is too small!")
        print("Block Size M : ", block_size)
        num_blocks = math.ceil(len(message) / block_size)
        print("Number of Blocks : ",num_blocks)
        point_list = []
        for i in range(num_blocks):
            print("----------------------------------------------------------")
            message_block = message[i*block_size:(i+1)*block_size]
            print("Message Block ",message_block)
            print("Length of message Block : ", len(message_block))
            binary_block = ''.join([('0' * (8 - len(bin(ord(char))[2:])) + bin(ord(char))[2:]) for char in message_block])
            print("Binary Block ", binary_block)
            extended_binary_block = binary_block + '0' *self.n
            print("Extended Binary Block : ", extended_binary_block)
            x = int(extended_binary_block, 2)
            point = self.ec.get_y_of_x(x)
            print("The Point corresponds to this block is : ", point)
            point_list.append(point)
            print("----------------------------------------------------------")
        print("---------------The end of converting process-----------------------")
        print("The Points that represents the message are :", point_list)
        return point_list
    
    def decrypt(self, d_receiver, decrypted_points_list):
        print("------------------------------Start the decryption process---------------------")
        print("-----------------Start decrypting point----------------------------------------")
        plain_points_list = []
        for point in decrypted_points_list:
            c1 = point[0]
            c2 = point[1]
            plain_point = self.decrypt_point(d_receiver, c1, c2)
            plain_points_list.append(plain_point)
        print("The decrypted points are : ", plain_points_list)
        message = ''
        for point in plain_points_list:
            x, y = point.get_x(), point.get_y()
            binary_x = bin(x)[2:len(bin(x))-8]
            while(len(binary_x) % 8 != 0 ):
                binary_x = '0' + binary_x
            iterations = len(binary_x) // 8
            for i in range(iterations):
                block = binary_x[i*8:i*8+8]
                decimal = int(block, 2)
                char = chr(decimal)
                message += char
        print("The resulted message of decryption is : ", message)
        print("The End of decryption")
        return message
    
    def encrypt_point(self, start, d_sender, e_receiver, plain_point):
        print(f"c1 = {start} * {d_sender}")
        c1 = self.ec.fast_multiply_point(start, d_sender)
        c2 = self.ec.add_points(plain_point, self.ec.fast_multiply_point(e_receiver,d_sender))
        print("c1, c2 = ", c1, c2)
        return c1, c2
    
    def encrypt(self, start, d_sender, e_receiver, message):
        print("----------------Start Encryption Process-------------------------")
        plain_point_list = self.convert_message_to_points(message)
        print("----------------Start Encrypting the points one by one-----------")
        encrypted_point_list = []
        for point in plain_point_list:
            encrypted_point = self.encrypt_point(start, d_sender, e_receiver, point)
            encrypted_point_list.append(encrypted_point)
        print("The encrypted Points are : ", encrypted_point_list)
        print("-----------------------The end of encryption process---------------")
        return encrypted_point_list

    def decrypt_point(self, d_receiver, c1, c2):
        temp1 = self.ec.fast_multiply_point(c1, d_receiver)
        temp2 = self.ec.reverse_point(temp1)
        p = self.ec.add_points(c2, temp2)
        print("p = ", p)
        return p


def validate_input(a, b, p, sender_key, receiver_key):
    if(not((a.isdigit() and b.isdigit() and p.isdigit() and sender_key.isdigit() and receiver_key.isdigit()))):
        return False, "Invalid Input type - Not Numbers!", []
    else:
        a = int(a)
        b = int(b)
        p = int(p)
        sender_key = int(sender_key)
        receiver_key = int(receiver_key)
        if((p >= 1000000) and (p <= 10000000) and (sympy.isprime(p))):
            pass
        else:
            counter = 0
            p = random.randint(1000000, 10000000)
            while(not sympy.isprime(p)):
                if(counter == 0):
                    print("Inputted value of p is not prime!")
                    counter = 1
                p = p + 1
            p_entry.delete(0, tk.END)
            p_entry.insert(0,string = str(p))
        p = int(p_entry.get())
        if(a >= p):
            a = a % p
            a_entry.delete(0, tk.END)
            a_entry.insert(0,string = str(a))
            a = int(a)
        if(b >= p):
            b = b % p
            b_entry.delete(0, tk.END)
            b_entry.insert(0,string = str(b))
            b = int(b)
        if(sender_key >= p):
            sender_key = sender_key % p 
            d_sender_entry.delete(0, tk.END)
            d_sender_entry.insert(0,string = str(sender_key))
            sender_key = int(sender_key)
        if(receiver_key >= p):
            receiver_key = receiver_key %  p
            d_receiver_entry.delete(0, tk.END)
            d_receiver_entry.insert(0,string = str(receiver_key))
            receiver_key = int(receiver_key)

        while(a**3 + 27*b**2) % p == 0 :
            print("The curve is singular.")
            print("The process of changing a and b")
            a = random.randint(1000,1000000)
            b = random.randint(1000,1000000)
            b_entry.delete(0, tk.END)
            b_entry.insert(0,string = str(b))
            b = int(b)
            a_entry.delete(0, tk.END)
            a_entry.insert(0,string = str(a))
            a = int(a)
            print("The new values of a and b as follows : ", a, b)

        ec = EC(a, b, p)
        start = ec.get_y_of_x(random.randint(1000,1000000))
        receiver_key = d_receiver_entry.get()
        e_receiver = ec.fast_multiply_point(start,int(receiver_key))
        receiver_public_key_label = tk.Label(window, text= f"Receiver's Public Key : {str(e_receiver)} .          \nInitail Point : {str(start)} .      " , bg='lightgray')
        public_keys_label.place(x = 10, y = 410)
        receiver_public_key_label.place(x = 30, y = 450)
        return True, "Valid Input!", [start, e_receiver]

def encrypt():
    global enc
    encrypt_button['state'] = tk.DISABLED
    a = a_entry.get()
    b = b_entry.get()
    p = p_entry.get()
    sender_key = d_sender_entry.get()
    # receiver_key = d_receiver_entry.get()
    print("Submit", a, b, p)
    test, message, li = validate_input(a, b, p, sender_key, "6")
    if(test):
        global start, e_receiver
        start = li[0]
        e_receiver = li[1]
        a = a_entry.get()
        b = b_entry.get()
        p = p_entry.get()
        sender_key = d_sender_entry.get()
        receiver_key = d_receiver_entry.get()
        ec = EC(int(a), int(b), int(p))
        enc = Encyption(ec)
        message = plain_text_entry.get().strip()
        global points_to_decrypt
        points_to_decrypt = enc.encrypt(start, int(sender_key), e_receiver, message)
        encrypt_button['state'] = tk.DISABLED
        decrypt_button['state'] = tk.ACTIVE
        string_points = 'Points = \n'
        for p in points_to_decrypt[0:6]:
            temp = str(p)
            temp = temp.center(100) + '\n'
            string_points += temp
        global points_result_label
        points_result_label.place_forget()
        points_result_label = tk.Label(window,     text= f"{string_points}",bg='lightgray', fg= 'black')
        points_result_label.place(x = 240, y = 250)
        print(points_to_decrypt)
    else:
        print("Bad Input!")
        encrypt_button['state'] = tk.ACTIVE
        decrypt_button['state'] = tk.DISABLED

def decrypt():
    global points_to_decrypt, enc, decryption_result, final_result_label
    decrypt_button['state'] = tk.DISABLED
    receiver_key = d_receiver_entry.get()
    decrytpted_message = enc.decrypt(int(receiver_key), points_to_decrypt)
    print(decrytpted_message)
    final_result_label.place_forget()
    final_result_label = final_result_label = tk.Label(window, text= decrytpted_message, bg='lightgray', fg= 'black')
    final_result_label.place(x = 300, y = 450 )
    decrypt_button['state'] = tk.DISABLED

if("__main__"):
    # Globals 
    start = None
    e_receiver = None
    points_to_decrypt = None
    points_result_label = None
    decryption_result = None
    enc = None
    # Creating a Window object
    window = Tk()

    # Setting the title and configuring window's size and background color
    window.title("ECC")
    window.configure(width=700, height=600)
    window.configure(bg='lightgray')

    # move window center
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    window.geometry("+{}+{}".format(posRight, posDown))

    # Labels
    public_params_label = tk.Label(window,   text= "Enter the Public Parameters                 ",bg='darkblue', fg= 'white')
    sender_params_label = tk.Label(window,   text= "Enter the Sender's Private Parameters       ",bg='darkblue', fg= 'white')
    receiver_params_label = tk.Label(window, text= "Enter the Receiver's Private Parameters     ",bg='darkblue', fg= 'white')
    public_keys_label = tk.Label(window,     text= "Extracted Public Parameters                 ",bg='darkblue', fg= 'white')
    plain_text_label = tk.Label(window,     text= "Enter your plain text to be encrypted                ",bg='darkblue', fg= 'white')
    points_label = tk.Label(window,     text= "Points resulted from encryption                ",bg='darkblue', fg= 'white')
    points_result_label = tk.Label(window,     text= "points = []",bg='lightgray', fg= 'black')
    decrytpted_text_label = tk.Label(window,     text= "Text resulted from decrypting the points               ",bg='darkblue', fg= 'white')

    final_result_label = tk.Label(window, text= "", bg='lightgray', fg= 'black')
    a_label = tk.Label(window, text= "Enter the a Parameter : ", bg='lightgray')
    b_label = tk.Label(window, text= "Enter the b Parameter : ", bg='lightgray')
    p_label = tk.Label(window, text= "Enter the p Parameter : ", bg='lightgray')
    d_sender_label = tk.Label(window, text= "Enter the Sender's Private Key : ", bg='lightgray')
    d_receiver_label = tk.Label(window, text= "Enter the Receiver's Private Key : ", bg='lightgray')
    receiver_public_key_label = tk.Label(window, text= "Receiver's Public Key and Initail Point : " , bg='lightgray')


    public_params_label.place(x= 10, y = 10)
    sender_params_label.place(x = 10, y = 210)
    receiver_params_label.place(x = 10, y = 310)
    plain_text_label.place(x = 300, y = 10)
    points_label.place(x = 300, y = 210)
    points_result_label.place(x = 300, y = 250)
    decrytpted_text_label.place(x=300, y = 410)
   # public_keys_label.place(x = 10, y = 410)
    final_result_label.place(x = 300, y = 450 )

    a_label.place(x = 30, y = 50)
    b_label.place(x = 30, y = 100)
    p_label.place(x = 30, y = 150)
    d_sender_label.place(x = 30 , y = 250)
    d_receiver_label.place(x = 30, y = 350)
    # receiver_public_key_label.place(x = 30, y = 450)

    # Entry
    a_entry = tk.Entry(window, bg='white')
    b_entry = tk.Entry(window, bg='white')
    p_entry = tk.Entry(window, bg='white')
    d_sender_entry = tk.Entry(window, bg='white')
    d_receiver_entry = tk.Entry(window, bg = 'white')
    plain_text_entry = tk.Entry(window, bg = 'white')
    a_entry.place(x = 40, y = 70)
    b_entry.place(x = 40, y = 120)
    p_entry.place(x = 40, y = 170)
    d_sender_entry.place(x = 40, y = 270)
    d_receiver_entry.place(x = 40, y = 370)
    plain_text_entry.place(x = 300, y = 70)


    # Button
    encrypt_button = tk.Button(window, text= "Encrypt", bg= 'darkgreen', fg='white', command= encrypt)
    encrypt_button.place(x = 50,y =  500)
    decrypt_button = tk.Button(window, text= "Decrypt", bg= 'darkred', fg='white', command= decrypt)
    decrypt_button.place(x = 100,y =  500)
    decrypt_button['state'] = tk.DISABLED


    window.mainloop()

