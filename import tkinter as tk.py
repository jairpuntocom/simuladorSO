import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class SimuladorProcesos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Procesos")

        # Variables de control
        self.en_ejecucion = False
        self.pausa = False
        self.tiempo = 0
        self.datos = []

        # Crear interfaz
        self.crear_interfaz()

    def crear_interfaz(self):
        # Botones
        self.btn_iniciar = ttk.Button(self.root, text="Iniciar", command=self.iniciar_simulacion)
        self.btn_iniciar.pack(pady=5)

        self.btn_pausa = ttk.Button(self.root, text="Pausar", command=self.toggle_pausa)
        self.btn_pausa.pack(pady=5)

        # Crear figura para la gráfica
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Procesos en tiempo real")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")

        # Canvas de matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

    def iniciar_simulacion(self):
        if not self.en_ejecucion:
            self.en_ejecucion = True
            self.pausa = False
            self.tiempo = 0
            self.datos = []
            self.simular()

    def toggle_pausa(self):
        if self.en_ejecucion:
            self.pausa = not self.pausa
            self.btn_pausa.config(text="Reanudar" if self.pausa else "Pausar")

    def simular(self):
        if self.en_ejecucion and not self.pausa:
            nuevo_valor = random.randint(1, 100)
            self.datos.append(nuevo_valor)
            self.tiempo += 1
            self.actualizar_grafica()

        if self.en_ejecucion:
            self.root.after(500, self.simular)

    def actualizar_grafica(self):
        self.ax.clear()
        self.ax.plot(self.datos, marker='o', linestyle='-')
        self.ax.set_title("Procesos en tiempo real")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorProcesos(root)
    root.mainloop()
  