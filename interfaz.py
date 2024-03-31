import tkinter as tk
from Main import Circuit

bgcolor = "#141414"



class Interfaz(tk.Tk):
    def __init__(self):
        super().__init__()

        
        self.botones = Frame(self, 0)
        self.name = Frame(self, 1)
        self.bloqueImagen = Frame(self, 2)
        self.bloqueValor = Frame(self, 3)
        self.bloqueAccion = Frame(self, 4)

        self.buttonCalc = tk.Button(self, text="Calcular", bg="#035EAD", activebackground="#011c34", padx=30, pady=20, font=("Arial", 11), command=self.calcular)
        self.buttonCalc.place(relx=1, rely=0, anchor='ne')

        self.output = ""

        self.txtOutput = tk.Label(self, text=self.output, bg=bgcolor, fg="#1EAB30", font=("Arial", 16), justify="left")
        self.txtOutput.place(x=0, y=0)
        self.circuit = Circuit()

    def show_image(self, boton):
        self.name.show_widgets_h()
        self.name.pack()

        self.botones._off_all()
        tipo = (boton.type if boton.type != "VCI" else "VCV"   ) 
        tipo = (tipo if boton.type != "ICV" else "ICI"   )
        self.bloqueImagen.image = tk.PhotoImage(file=f"imagenes/{tipo}.png")
        self.bloqueImagen.imageLabel.config(image=self.bloqueImagen.image)
        self.bloqueImagen.pack()
        self.bloqueImagen.show_widgets_h()

        self.bloqueValor.pack()
        self.bloqueValor.show_widgets_v()

        self.bloqueAccion.pack()
        self.bloqueAccion.show_widgets_v()
    
    def _clean(self):
        self.botones._off_all()
        self.name.pack_forget()
        self.name.inName.delete(0, tk.END)
        self.bloqueImagen.pack_forget()
        self.bloqueImagen.inN1.delete(0, tk.END)
        self.bloqueImagen.inN2.delete(0, tk.END)
        self.bloqueValor.pack_forget()
        self.bloqueValor.inValor.delete(0, tk.END)
        self.bloqueAccion.pack_forget()

    def _reset(self):
        self._clean()
        self.output = ""
        self.txtOutput.config(text="")
        self.circuit.reset()
    
    def add_component(self):
        type = self.botones._get_active().type
        reference = self.name.inName.get()
        value = self.bloqueValor.inValor.get()
        node1 = self.bloqueImagen.inN1.get()
        node2 = self.bloqueImagen.inN2.get()
        txt = type + reference + " " + value + " " + node1 + " " + node2 + "\n"

        self.output += txt
        self.txtOutput.config(text=self.output)
        self._clean()

    def calcular(self):
        if self.output[-1] == '\n': self.output = self.output[:-1]
        self.circuit.read(self.output)
        self.circuit.calculate()

        result = tk.Tk()
        result.config(bg=bgcolor)
        result.title("Solución")
        result.geometry("800x800")
        text = self.circuit.get_branches_txt() + self.circuit.get_nodes_txt() + self.__get_solve_txt()
        solucion = tk.Label(result, text=text, bg=bgcolor, fg="white", font=("Times new roman", 18))
        solucion.pack()
        self.circuit.reset()
    
    def __get_solve_txt(self):
        txt = ""
        if self.circuit.solve.size <= 0: return "No hay solución"
        else: 
            index = 0
            txt += "\n Corriente en cada rama\n"
            for i in range(len(self.circuit.branches)):
                txt += str(self.circuit.solve[index][0]) + " Ampers " + str(self.circuit.branches[i])+"\n"
                index += 1
            txt += "\n Tensión en cada rama \n"
            for i in range(len(self.circuit.branches)):
                txt += str(self.circuit.solve[index][0]) + " Volts " + str(self.circuit.branches[i]) + "\n"
                index += 1
            txt += "\n Tensión en cada nodo\n"
            for i in range(len(self.circuit.nodes)-1):
                txt += str(self.circuit.solve[index][0]) + " Volts " + str(self.circuit.nodes[i]) + "\n"
                index += 1

        return txt
        



class Frame(tk.Frame):
    def __init__(self, where, n=0):
        super().__init__(where)
        self.config(bg=bgcolor)
        self.widgets = []


        if n == 0:
            self.widgets = []
        
        elif n == 1:
            self.txtName = tk.Label(self, text="Número de referencia", fg="white", font=("Arial", 16), bg=bgcolor)
            self.inName = tk.Entry(self, justify="center", font=("Arial", 16), width=10)
            self.widgets = [self.txtName, self.inName]

        elif n == 2:
            self.image = None
            self.imageLabel = tk.Label(self, bg=bgcolor)
            self.subFrame1 = tk.Frame(self, bg=bgcolor)
            self.subFrame2 = tk.Frame(self, bg=bgcolor)

            txtN1 = tk.Label(self.subFrame1, text="Node +", fg="white", bg=bgcolor, font=("Arial", 16))
            txtN1.pack()
            txtN2 = tk.Label(self.subFrame2, text="Node -", fg="white", bg=bgcolor, font=("Arial", 16))
            txtN2.pack()

            self.inN1 = tk.Entry(self.subFrame1, justify="center", font=("Arial", 16), width=10)
            self.inN1.pack()
            self.inN2 = tk.Entry(self.subFrame2, justify="center", font=("Arial", 16), width=10)
            self.inN2.pack()

            self.widgets = [self.subFrame1, self.imageLabel, self.subFrame2]

        elif n == 3:
            self.image = tk.PhotoImage(file="imagenes/flecha.png")
            self.flecha = tk.Label(self, image=self.image, bg=bgcolor)
            self.subFrame = Frame(self)
            self.inValor = tk.Entry(self.subFrame, justify="center", font=("Arial", 18), width=10)
            self.txtValor = tk.Label(self.subFrame, text="Valor", fg="white", font=("Arial", 16), bg=bgcolor)

            self.subFrame.widgets.append(self.txtValor)
            self.subFrame.widgets.append(self.inValor)
            self.subFrame.show_widgets_h()
            self.widgets = [self.flecha, self.subFrame]

        elif n == 4:
            margen = tk.Label(self, pady=10, bg=bgcolor)
            buttonAdd = tk.Button(self, text="Añadir", bg="#1C8C62", activebackground="#0e4631", padx=30, pady=20, font=("Arial", 11), command=where.add_component)
            buttonClean = tk.Button(self, text="Limpiar", bg="#E8f9c5", activebackground="#5d644f", padx=10, pady=7, font=("Arial", 11), command=where._reset)
            self.widgets = [margen, buttonAdd, buttonClean]


    def add_button(self, txt, type):
        self.widgets.append(Button(txt, type))

    def show_widgets_h(self):
        for i in range(len(self.widgets)):
            self.widgets[i].grid(row=0, column=i)
    def show_widgets_v(self):
        for i in range(len(self.widgets)):
            self.widgets[i].grid(row=i, column=0)

    def _off_all(self):
        for boton in self.widgets:
            boton.config(bg="#536F8C")
            boton.active = False

    def _get_active(self):
        for boton in self.widgets:
            if boton.active:
                return boton

screen = Interfaz()

screen.config(bg=bgcolor)
screen.geometry("1300x720")
screen.title("Circuitos")






class Button(tk.Button):
    def __init__(self, txt, type=None):
        super().__init__(screen.botones, text=txt, command=self.clic)
        self.config(bg="#536F8C", activebackground="#283543")
        self.config(wraplength=70, height=5)
        self.config(padx=12)
        self.config(font=("Arial", 11), fg="black")

        self.type = type
        self.active = False


    def clic(self):
        screen.show_image(self)
        self.config(bg="#988921")
        self.active = True





screen.botones.pack()

screen.botones.add_button("Fuente de corriente", "I")
screen.botones.add_button("Fuente de tensión", "V")
screen.botones.add_button("Resistor", "R")
screen.botones.add_button("Tensíon controlada por tensión", "VCV")
screen.botones.add_button("Corriente controlada por corriente", "ICI")
screen.botones.add_button("Tensión controlada por corriente", "VCI")
screen.botones.add_button("Corriente controlada por tensión", "ICV")



screen.botones.show_widgets_h()




screen.mainloop()

