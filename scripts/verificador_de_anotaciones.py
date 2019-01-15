# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
Created on Wed Jan  9 17:46:19 2019

@author: Core i7
"""
import tkinter as tk
import cv2
from PIL import ImageTk, Image
from math import *


class Rect:
    """ 
    Clase que representa un bounding box
    """
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def to_string(self):
        return '%s, %s, %s, %s' % (self.x, self.y, self.w, self.h)
    

def parse_txt(txt):
    """Parsea la anotación de entrada

    Parameters:
    txt (string): string que contiene la anotación de la 
    imagen de entrada
    
    Returns:
        digits ([string]): lista de símbolos o etiquetas de la imagen
        rect_lst ([Rect]): lista de los bounding box
   """
    tokens = txt.strip().split('\n')
    print(len(tokens))
    digits = []
    rect_lst = []
    for t in tokens:
        digits.append(t[0])
        s = [int(x.strip()) for x in t[2:].split(',')]    
        rect = Rect(s[0], s[1], s[2], s[3])
        rect_lst.append(rect)
    return digits, rect_lst

    
def fetch(ents):
    """Muestra la imagen con sus correspondientes anotaciones

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    
    Returns:
        void
   """
    path_image = ents[0].get().strip()
    path_txt = ents[1].get().strip()
    if path_image == '' or path_txt == '':
        root.mainloop()
        return
    with open(path_txt, 'r') as f: 
        txt = f.read()
    digits, rect_lst = parse_txt(txt)
    image = cv2.imread(path_image, 0)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image = image, anchor = "nw")
    for rect in rect_lst:
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        canvas.create_rectangle(x, y, x+w, y+h, outline='red', fill='', width=2)
    num = ''
    for digit in digits:
        num += digit
    ents[2].delete(0, tk.END)
    ents[2].insert(0, num)
    root.mainloop()

root = tk.Tk()
root.title("Show ROI")
root.geometry("600x350")

canvas = tk.Canvas(root, width=600, height=200)
canvas.grid(row=0, column=0, columnspan=4, sticky='nsew')

label1 = tk.Label(root, text= 'Path imagen:', font = "16")
label1.grid(row=1, column=0, sticky='w', padx=10)

ent1 = tk.Entry(root)
ent1.grid(row=1, column=1, columnspan=3, sticky='nsew', padx=10)

label2 = tk.Label(root, text= 'Path anotación:', font = "16")
label2.grid(row=2, column=0, sticky='w', padx=10)

ent2 = tk.Entry(root)
ent2.grid(row=2, column=1, columnspan=3, sticky='nsew', padx=10)

label3 = tk.Label(root, text= 'Número:', font = "16")
label3.grid(row=4, column=0, sticky='w', padx=10)

ent3 = tk.Entry(root)
ent3.grid(row=4, column=1, columnspan=3, sticky='nsew', padx=10)

ents = [ent1, ent2, ent3]

botton = tk.Button(root, text='Verificar anotación', font = "bold 16", command=(lambda e= ents: fetch(e)))
botton.grid(row=3, column=0, columnspan=4, sticky='nsew', pady=10)

root.mainloop()

