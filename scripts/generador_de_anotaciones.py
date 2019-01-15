# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
Created on Wed Jan  9 17:46:19 2019

@author: Core i7
"""
import tkinter as tk
import cv2
from PIL import ImageTk, Image
import glob
import os


class App(tk.Frame):
    """ 
    Clase que crea los bounding box. 
    """
    def __init__( self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self._createCanvasBinding()

    def _createVariables(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None
        self.move = False

    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width = 800, height = 200,
                                bg = "white" )
        self.canvas.grid(row=1, column=0, columnspan=4, sticky='nsew')
        
        
    def _createCanvasBinding(self):
        self.canvas.bind( "<Button-1>", self.startRect )
        self.canvas.bind( "<ButtonRelease-1>", self.stopRect )
        self.canvas.bind( "<Motion>", self.movingRect )

    def startRect(self, event):
        #self.canvas.delete("all")
        self.move = True
        #Translate mouse screen x0,y0 coordinates to canvas coordinates
        self.rectx0 = self.canvas.canvasx(event.x)
        self.recty0 = self.canvas.canvasy(event.y) 
        #Create rectangle
        self.rect = self.canvas.create_rectangle(
            self.rectx0, self.recty0, self.rectx0, self.recty0, outline='red', fill='', width=2)
        #Get rectangle's canvas object ID
        self.rectid = self.canvas.find_closest(self.rectx0, self.recty0, halo=2)
        """print('Rectangle {0} started at {1} {2} {3} {4} '.
              format(self.rect, self.rectx0, self.recty0, self.rectx0,
                     self.recty0))"""

    def movingRect(self, event):
        if self.move: 
            #Translate mouse screen x1,y1 coordinates to canvas coordinates
            self.rectx1 = self.canvas.canvasx(event.x)
            self.recty1 = self.canvas.canvasy(event.y)
            #Modify rectangle x1, y1 coordinates
            self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                          self.rectx1, self.recty1)
            #print('Rectangle x1, y1 = ', self.rectx1, self.recty1)

    def stopRect(self, event):
        self.move = False
        #Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y) 
        #Modify rectangle x1, y1 coordinates (final)
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1)
        #print('Rectangle ended')
        global doubled
        scale = 1
        if doubled:
            scale = 0.5
        x = int(self.rectx0 * scale)
        y = int(self.recty0 * scale)
        w = int(abs(self.rectx0-self.rectx1) * scale)
        h = int(abs(self.recty0-self.recty1) * scale)
        rect = Rect(x, y, w, h)
        rect_lst.append(rect)


def generar_anotacion(ents):
    """Genera la anotación (output)

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    
    Returns:
        void
   """
    try:
        _input = ents[0].get().strip()
    except:
        err = "Error: ingrese un input"
        print(err)
        ents[1].delete('1.0', tk.END)
        ents[1].insert('1.0', err)
        return
    if len(_input) != len(rect_lst):
        err = "Error: número de bounding box no coincide con el número de dígitos"
        print(err)
        ents[1].delete('1.0', tk.END)
        ents[1].insert('1.0', err)
        return
    text = ''
    for i, digit in enumerate(_input):
        text = text + '%s: %s\n' % (digit, rect_lst[i].to_string())        
    ents[1].delete('1.0', tk.END)
    ents[1].insert('1.0', text)
    
    
def reset(ents, filename):
    """Resetea y carga una nueva imagen en el canvas.

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    filename (string): nombre del archivo de la imagen
    
    Returns:
        void
   """
    app.canvas.delete("all")
    if filename == '':
        root.mainloop()
        return
    in_path = ents[2].get().strip()
    global rect_lst
    rect_lst = []
    path_file = os.path.join(in_path, filename)
    image = cv2.imread(path_file,0)
    width = image.shape[1]
    height = image.shape[0]
    global doubled
    if width < 400 and height < 100: 
        doubled = True
        dim = (width * 2, height * 2)
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    else:
        doubled = False
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    app.canvas.create_image(0, 0, image = image, anchor = "nw")
    ents[0].delete(0, tk.END)
    ents[1].delete('1.0', tk.END)
    root.mainloop()
    
def save_res(ents):
    """Guarda la anotación en el directorio especificado 
     (path de salida)

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    
    Returns:
        void
   """
    global counter, total
    if total == 0:
        return
    filename = current_filename.split('.')[0] + '.txt'
    file_path = ents[3].get()
    path = os.path.join(file_path, filename)
    with open(path, 'w') as f: 
        f.write(ents[1].get("1.0", tk.END))
    counter = 0
    next_file(ents)
      
class Rect:
    """ 
    Clase que representa un bounding box 
    """
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def reduce(self, factor):
        self.x = self.x * factor
        self.y = self.y * factor
        self.w = self.w * factor
        self.h = self.h * factor
        
    def to_string(self):
        return '%s, %s, %s, %s' % (self.x, self.y, self.w, self.h)
    

def get_faltantes(in_path, out_path):
    """Obtiene una lista de las imagenes sin anotación en la 
    carpeta de salida

    Parameters:
    in_path (string): carpeta con imagenes
    out_path (string): carpeta con anotaciones
    
    Returns:
        faltantes ([string]): lista de imagenes faltantes sin anotacion
   """
    faltantes = []
    cwd_root = os.getcwd()
    os.chdir(in_path)
    types = ('*.png', '*.bmp', '*jpg', '*tif')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))
    img_all = files_grabbed
    
    os.chdir(out_path)
    ready = glob.glob("*.txt")
    
    ready_name = [f.split('.')[0] for f in ready]
    
    faltantes = []
    for f in img_all:
        filename = f.split('.')[0]
        if filename not in ready_name:
            faltantes.append(f)
    os.chdir(cwd_root)
    return faltantes

def next_file(ents):
    """Procesa la siguiente imagen

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    
    Returns:
        void
   """
    global counter, total
    in_path = ents[2].get().strip()
    out_path = ents[3].get().strip()
    if in_path == '' or out_path == '':
        print('Error: Seleccione carpeta de entrada y salida')
        return
    faltantes = get_faltantes(in_path, out_path)
    total = len(faltantes)
    if len(faltantes) == 0:
        filename = ''
        txt_label = 'Procesadas todas las imágenes'
    else:
        filename = faltantes[counter]
        txt_label = filename
        counter += 1 
        if counter == total:
            counter = 0
    global current_filename
    current_filename = filename
    label3.config(text= txt_label)
    if total != 0:
        botton1.config(state=tk.NORMAL)
        botton2.config(state=tk.NORMAL)
        botton3.config(state=tk.NORMAL)
    reset(ents, filename)

def clear(ents):
    """Limpia la imagen actual

    Parameters:
    ents ([]): arreglo de las entradas (inputs) de usuario
    
    Returns:
        void
   """
    reset(ents, current_filename)

root = tk.Tk()
root.title("Select ROI")
root.geometry( "800x600" )
app = App(root)

rect_lst = [] # lista de rectangulos
current_filename = '' # nombre de la imagen que se está mostrando en el canvas
counter = 0 # indice de la imagen actual respecto a todas las imagenes faltantes sin anotación
doubled = False # indica si la imagen actual está escalada al doble
total = 0 # total de imágenes sin anotación

label3 = tk.Label(root, text= 'Seleccione carpetas de entrada y salida', font = "16")
label3.grid(row=0, column=0, columnspan=4)

in_path_label = tk.Label(root, text= 'Path de entrada:', font = "16")
in_path_label.grid(row=2, column=0, sticky='w', padx=10)

in_path = tk.Entry(root)
in_path.grid(row=2, column=1, columnspan=4, sticky='nsew')

out_path_label = tk.Label(root, text= 'Path de salida:', font = "16")
out_path_label.grid(row=3, column=0, sticky='w', padx=10)

out_path = tk.Entry(root)
out_path.grid(row=3, column=1, columnspan=4, sticky='nsew')

label1 = tk.Label(root, text= 'Input:', font = "16")
label1.grid(row=4, column=0, sticky='w', padx=10)

ent = tk.Entry(root)
ent.grid(row=4, column=1, columnspan=4, sticky='nsew')

label2 = tk.Label(root, text= 'Output:', font = "16")
label2.grid(row=6, column=0, columnspan=4, sticky='nsew')

res = tk.Text(root)
res.grid(row=7, column=0, columnspan=4, sticky='nsew')

ents = [ent, res, in_path, out_path]

botton1 = tk.Button(root, text='Generar anotación', fg="blue", font = "bold 16", command=(lambda e= ents: generar_anotacion(e)))
botton1.grid(row=5, column=1, sticky='nsew', pady=10)
botton1.config(state=tk.DISABLED)

botton2 = tk.Button(root, text='Limpiar', fg="red", font = "bold 16", command=(lambda e= ents: clear(e)))
botton2.grid(row=5, column=2, sticky='nsew', pady=10)
botton2.config(state=tk.DISABLED)

botton3 = tk.Button(root, text='Guardar anotación', fg="green", font = "bold 16", command=(lambda e= ents: save_res(e)))
botton3.grid(row=5, column=3, sticky='nsew', pady=10)
botton3.config(state=tk.DISABLED)

botton4 = tk.Button(root, text='Siguiente', fg="black", font = "bold 16", command=(lambda e= ents: next_file(e)))
botton4.grid(row=5, column=0, sticky='nsew', pady=10)

reset(ents, '')



