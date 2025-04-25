import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import defaultdict

PROCESS_STATES = {
    "NEW": "Nuevo",
    "READY": "Listo",
    "RUNNING": "Ejecutando",
    "WAITING": "Esperando",
    "TERMINATED": "Terminado"
}

STATE_COLORS = {
    "Nuevo": "#BBDEFB",  # Azul claro
    "Listo": "#C8E6C9",  # Verde claro
    "Ejecutando": "#4CAF50",  # Verde
    "Esperando": "#FFECB3",  # Amarillo claro
    "Terminado": "#FFCDD2"   # Rojo claro
}

class Process:
    def __init__(self, id, priority, execution_time, execution_cycle):
        self.id = id
        self.priority = priority
        self.execution_time = execution_time
        self.execution_cycle = execution_cycle
        self.initial_execution_time = execution_time  # Para seguimiento del progreso
        self.current_state = PROCESS_STATES["NEW"]
        self.memory_usage = random.randint(100, 600)  # 100-600 MB
        self.core = random.randint(0, 3)  # 0-3 núcleos
        self.thread = random.randint(0, 7)  # 0-7 hilos
        self.state_history = [PROCESS_STATES["NEW"]]  # Historial de estados
        self.time_in_states = {state: 0 for state in PROCESS_STATES.values()}
        self.time_in_states[PROCESS_STATES["NEW"]] = 1
        self.cpu_usage_history = [random.randint(10, 30)]  # Historial de uso de CPU

class ProcessSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Procesos")
        self.geometry("1200x750")
        self.configure(bg="#f0f0f0")
        
        self.cycle_count = 0
        self.state_counts = {state: 0 for state in PROCESS_STATES.values()}
        self.state_counts[PROCESS_STATES["NEW"]] = 3  # Inicialmente 3 procesos nuevos
        
        self.processes = [
            Process(1, "Alta", 10, 5),
            Process(2, "Media", 15, 7),
            Process(3, "Baja", 20, 10)
        ]
        
        self.selected_process = None
        self.history_data = []
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_frame = tk.Frame(main_frame, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(title_frame, text="📊 Simulador de Procesos", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack()
        
        # Panel superior: Procesos y controles
        top_panel = tk.Frame(main_frame, bg="#f0f0f0")
        top_panel.pack(fill=tk.X, pady=10)
        
        # Contenedor para procesos
        processes_frame = tk.Frame(top_panel, bg="#f0f0f0")
        processes_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.process_frames = []
        for i, process in enumerate(self.processes):
            process_frame = tk.Frame(processes_frame, bg="white", relief=tk.RAISED, bd=1)
            process_frame.grid(row=0, column=i, padx=10)
            
            process_frame.bind("<Button-1>", lambda e, p=process: self.select_process(p))
            
            process_title = tk.Label(process_frame, text=f"Proceso {process.id}", font=("Arial", 12, "bold"), bg="white")
            process_title.pack(fill=tk.X, pady=5, padx=10)
            
            separator = ttk.Separator(process_frame, orient="horizontal")
            separator.pack(fill=tk.X, padx=5)
            
            content_frame = tk.Frame(process_frame, bg="white")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(content_frame, text=f" Prioridad: {process.priority}", bg="white", anchor="w").pack(fill=tk.X, pady=2)
            tk.Label(content_frame, text=f" Núcleo: {process.core}", bg="white", anchor="w").pack(fill=tk.X, pady=2)
            tk.Label(content_frame, text=f" Memoria: {process.memory_usage} MB", bg="white", anchor="w").pack(fill=tk.X, pady=2)
            
            # Barra de progreso para tiempo de ejecución restante
            progress_frame = tk.Frame(content_frame, bg="white")
            progress_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(progress_frame, text="Progreso:", bg="white").pack(anchor="w")
            
            progress_var = tk.DoubleVar()
            progress_var.set(0)
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=process.initial_execution_time)
            progress_bar.pack(fill=tk.X, pady=2)
            
            state_var = tk.StringVar()
            state_var.set(f"Estado: {process.current_state}")
            state_label = tk.Label(content_frame, textvariable=state_var, bg="white", anchor="w")
            state_label.pack(fill=tk.X, pady=2)
            
            process_frame.process = process
            process_frame.state_var = state_var
            process_frame.progress_var = progress_var
            self.process_frames.append(process_frame)
        
        # Panel de detalles para el proceso seleccionado
        self.details_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=1)
        self.details_frame.pack(fill=tk.X, pady=10)
        self.details_frame.pack_forget()  
        
        # Panel inferior con visualizaciones
        viz_panel = tk.Frame(main_frame, bg="#f0f0f0")
        viz_panel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestañas para diferentes visualizaciones
        self.tab_control = ttk.Notebook(viz_panel)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Distribución de estados
        self.states_tab = tk.Frame(self.tab_control, bg="white")
        self.tab_control.add(self.states_tab, text="Distribución de Estados")
        
        # Pestaña 2: Línea de tiempo de procesos
        self.timeline_tab = tk.Frame(self.tab_control, bg="white")
        self.tab_control.add(self.timeline_tab, text="Línea de Tiempo")
        
        # Pestaña 3: Uso de recursos
        self.resources_tab = tk.Frame(self.tab_control, bg="white")
        self.tab_control.add(self.resources_tab, text="Uso de Recursos")
        
        # Inicializar gráficos
        self.init_state_distribution_chart()
        self.init_timeline_chart()
        self.init_resource_usage_chart()
        
        # Controles de simulación
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Contador de ciclos
        self.cycle_counter_var = tk.StringVar()
        self.cycle_counter_var.set("Ciclo: 0")
        cycle_counter = tk.Label(buttons_frame, textvariable=self.cycle_counter_var, 
                                font=("Arial", 10, "bold"), bg="#f0f0f0")
        cycle_counter.pack(side=tk.LEFT, padx=5)
        
        simulate_btn = tk.Button(buttons_frame, text="▶️ Simular Ciclo", 
                                command=self.simulate_process_cycle, bg="#4CAF50", fg="white", 
                                font=("Arial", 10, "bold"), padx=10, pady=5)
        simulate_btn.pack(side=tk.LEFT, padx=5)
        
        auto_simulate_btn = tk.Button(buttons_frame, text="⏩ Auto Simular (5 ciclos)", 
                                    command=lambda: self.auto_simulate(5), bg="#2196F3", fg="white", 
                                    font=("Arial", 10, "bold"), padx=10, pady=5)
        auto_simulate_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(buttons_frame, text="🔄 Reiniciar Simulación", 
                             command=self.reset_simulation, bg="#F44336", fg="white", 
                             font=("Arial", 10, "bold"), padx=10, pady=5)
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def init_state_distribution_chart(self):
        fig, self.states_ax = plt.subplots(figsize=(5, 4))
        plt.subplots_adjust(left=0.2)
        
        self.states_canvas = FigureCanvasTkAgg(fig, self.states_tab)
        self.states_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_state_distribution_chart()
    
    def update_state_distribution_chart(self):
        self.states_ax.clear()
        
        states = list(PROCESS_STATES.values())
        values = [self.state_counts[state] for state in states]
        colors = [STATE_COLORS[state] for state in states]
        
        bars = self.states_ax.barh(states, values, color=colors)
        self.states_ax.set_title('Distribución de Procesos por Estado')
        self.states_ax.set_xlabel('Número de Procesos')
        
        # Añadir valores a las barras
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                self.states_ax.text(width + 0.1, 
                                   bar.get_y() + bar.get_height()/2, 
                                   f'{int(width)}', 
                                   ha='left', va='center')
        
        self.states_canvas.draw()
    
    def init_timeline_chart(self):
        fig, self.timeline_ax = plt.subplots(figsize=(5, 4))
        
        self.timeline_canvas = FigureCanvasTkAgg(fig, self.timeline_tab)
        self.timeline_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.timeline_ax.set_title('Línea de Tiempo de Procesos')
        self.timeline_ax.set_xlabel('Ciclo')
        self.timeline_ax.set_ylabel('Proceso')
        
        self.update_timeline_chart()
    
    def update_timeline_chart(self):
        self.timeline_ax.clear()
        
        # Colores para cada estado
        cmap = {'Nuevo': '#BBDEFB', 'Listo': '#C8E6C9', 
                'Ejecutando': '#4CAF50', 'Esperando': '#FFECB3', 
                'Terminado': '#FFCDD2'}
        
        y_ticks = []
        y_labels = []
        
        for i, process in enumerate(self.processes):
            y_pos = i
            y_ticks.append(y_pos)
            y_labels.append(f"P{process.id}")
            
            for t, state in enumerate(process.state_history):
                self.timeline_ax.add_patch(plt.Rectangle((t, y_pos - 0.4), 1, 0.8, 
                                                      color=cmap[state]))
                
                # Añadir etiqueta de estado (solo para el primer y último estado)
                if t == 0 or t == len(process.state_history) - 1:
                    first_char = state[0]
                    self.timeline_ax.text(t + 0.5, y_pos, first_char, 
                                       ha='center', va='center', fontsize=8)
        
        # Configurar ejes
        self.timeline_ax.set_yticks(y_ticks)
        self.timeline_ax.set_yticklabels(y_labels)
        self.timeline_ax.set_xlim(0, max(1, self.cycle_count))
        self.timeline_ax.set_ylim(-0.5, len(self.processes) - 0.5)
        self.timeline_ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Leyenda
        legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color, label=state)
                          for state, color in cmap.items()]
        self.timeline_ax.legend(handles=legend_elements, loc='upper center', 
                              bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        self.timeline_ax.set_title('Línea de Tiempo de Procesos')
        self.timeline_ax.set_xlabel('Ciclo')
        
        plt.tight_layout()
        self.timeline_canvas.draw()
    
    def init_resource_usage_chart(self):
        fig = plt.figure(figsize=(5, 4))
        
        # Gráfico de memoria
        self.memory_ax = plt.subplot(211)
        self.memory_ax.set_title('Uso de Memoria por Proceso')
        self.memory_ax.set_ylabel('MB')
        
        # Gráfico de CPU
        self.cpu_ax = plt.subplot(212)
        self.cpu_ax.set_title('Uso de CPU a lo largo del tiempo')
        self.cpu_ax.set_xlabel('Ciclo')
        self.cpu_ax.set_ylabel('% CPU')
        
        self.resource_canvas = FigureCanvasTkAgg(fig, self.resources_tab)
        self.resource_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.tight_layout()
        self.update_resource_usage_chart()
    
    def update_resource_usage_chart(self):
        # Actualizar gráfico de memoria
        self.memory_ax.clear()
        
        process_ids = [f"P{p.id}" for p in self.processes]
        memory_usage = [p.memory_usage for p in self.processes]
        colors = [STATE_COLORS[p.current_state] for p in self.processes]
        
        bars = self.memory_ax.bar(process_ids, memory_usage, color=colors)
        
        for bar in bars:
            height = bar.get_height()
            self.memory_ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                             f'{int(height)}MB', ha='center', va='bottom')
        
        self.memory_ax.set_title('Uso de Memoria por Proceso')
        self.memory_ax.set_ylabel('MB')
        
        # Actualizar gráfico de CPU
        self.cpu_ax.clear()
        
        cycles = list(range(self.cycle_count + 1))
        
        for process in self.processes:
            cpu_data = process.cpu_usage_history
            # Asegurar que hay datos para todos los ciclos
            while len(cpu_data) < len(cycles):
                cpu_data.append(cpu_data[-1] if cpu_data else 0)
            
            self.cpu_ax.plot(cycles[:len(cpu_data)], cpu_data, 
                           marker='o', label=f"P{process.id}")
        
        self.cpu_ax.set_title('Uso de CPU a lo largo del tiempo')
        self.cpu_ax.set_xlabel('Ciclo')
        self.cpu_ax.set_ylabel('% CPU')
        self.cpu_ax.legend()
        self.cpu_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Establecer límites del eje y
        self.cpu_ax.set_ylim(0, 100)
        
        plt.tight_layout()
        self.resource_canvas.draw()
    
    def select_process(self, process):
        self.selected_process = process
        self.update_details_frame()
    
    def update_details_frame(self):
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_process:
            self.details_frame.pack_forget()
            return
        
        self.details_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(self.details_frame, text=f"Detalles del Proceso {self.selected_process.id}", 
                              font=("Arial", 12, "bold"), bg="white")
        title_label.pack(fill=tk.X, padx=10, pady=5)
        
        separator = ttk.Separator(self.details_frame, orient="horizontal")
        separator.pack(fill=tk.X, padx=5)
        
        content_frame = tk.Frame(self.details_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo con información básica
        left_frame = tk.Frame(content_frame, bg="white")
        left_frame.grid(row=0, column=0, sticky="nw", padx=10)
        
        tk.Label(left_frame, text="Información Detallada:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        tk.Label(left_frame, text=f"Tiempo de Ejecución: {self.selected_process.execution_time}/{self.selected_process.initial_execution_time}", bg="white").pack(anchor="w", pady=2)
        tk.Label(left_frame, text=f"Ciclo de Ejecución: {self.selected_process.execution_cycle}", bg="white").pack(anchor="w", pady=2)
        tk.Label(left_frame, text=f"Hilo: {self.selected_process.thread}", bg="white").pack(anchor="w", pady=2)
        
        # Panel central con estados del proceso
        center_frame = tk.Frame(content_frame, bg="white")
        center_frame.grid(row=0, column=1, sticky="nw", padx=10)
        
        tk.Label(center_frame, text="Estados del Proceso:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        
        states_frame = tk.Frame(center_frame, bg="white")
        states_frame.pack(fill=tk.X, pady=5)
        
        for state in PROCESS_STATES.values():
            state_frame = tk.Frame(states_frame, bg=STATE_COLORS[state] if state == self.selected_process.current_state else "#e0e0e0",
                                 padx=5, pady=5, bd=1, relief=tk.RAISED)
            state_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(state_frame, text=f"{state} ({self.selected_process.time_in_states[state]} ciclos)", 
                    bg=STATE_COLORS[state] if state == self.selected_process.current_state else "#e0e0e0").pack()
        
        # Panel derecho con gráfico de tiempo en estados
        right_frame = tk.Frame(content_frame, bg="white")
        right_frame.grid(row=0, column=2, sticky="nw", padx=10)
        
        tk.Label(right_frame, text="Tiempo en Estados:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        
        fig, ax = plt.subplots(figsize=(3, 2))
        
        states = list(PROCESS_STATES.values())
        times = [self.selected_process.time_in_states[state] for state in states]
        colors = [STATE_COLORS[state] for state in states]
        
        wedges, texts, autotexts = ax.pie(times, labels=None, autopct='%1.1f%%', 
                                        startangle=90, colors=colors)
        
        # Leyenda
        ax.legend(wedges, states, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        canvas = FigureCanvasTkAgg(fig, right_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def simulate_process_cycle(self):
        self.cycle_count += 1
        self.cycle_counter_var.set(f"Ciclo: {self.cycle_count}")
        
        # Actualizar conteo de estados
        self.state_counts = {state: 0 for state in PROCESS_STATES.values()}
        
        for process in self.processes:
            old_state = process.current_state
            
            # Lógica de transición de estados
            if process.current_state == PROCESS_STATES["NEW"]:
                process.current_state = PROCESS_STATES["READY"]
            elif process.current_state == PROCESS_STATES["READY"]:
                process.current_state = PROCESS_STATES["RUNNING"]
            elif process.current_state == PROCESS_STATES["RUNNING"]:
                if process.execution_time > 0:
                    process.current_state = PROCESS_STATES["WAITING"]
                else:
                    process.current_state = PROCESS_STATES["TERMINATED"]
            elif process.current_state == PROCESS_STATES["WAITING"]:
                process.current_state = PROCESS_STATES["READY"]
                process.execution_time -= 1
            
            # No cambiar estado si ya está terminado
            if old_state == PROCESS_STATES["TERMINATED"]:
                process.current_state = PROCESS_STATES["TERMINATED"]
            
            # Actualizar conteo de estados
            self.state_counts[process.current_state] += 1
            
            # Actualizar historial de estados
            process.state_history.append(process.current_state)
            
            # Incrementar tiempo en el estado actual
            process.time_in_states[process.current_state] += 1
            
            # Generar datos de uso de CPU
            if process.current_state == PROCESS_STATES["RUNNING"]:
                cpu = random.randint(70, 100)
            elif process.current_state == PROCESS_STATES["WAITING"]:
                cpu = random.randint(20, 40)
            elif process.current_state == PROCESS_STATES["READY"]:
                cpu = random.randint(5, 15)
            elif process.current_state == PROCESS_STATES["TERMINATED"]:
                cpu = 0
            else:
                cpu = random.randint(1, 10)
            
            process.cpu_usage_history.append(cpu)
        
        # Actualizar interfaz de usuario
        self.update_process_frames()
        if self.selected_process:
            self.update_details_frame()
        
        # Actualizar visualizaciones
        self.update_state_distribution_chart()
        self.update_timeline_chart()
        self.update_resource_usage_chart()
    
    def auto_simulate(self, cycles):
        """Ejecuta varios ciclos de simulación automáticamente"""
        for _ in range(cycles):
            self.simulate_process_cycle()
            self.update()  # Actualizar interfaz
            time.sleep(0.5)  # Pequeña pausa entre ciclos
    
    def reset_simulation(self):
        self.cycle_count = 0
        self.cycle_counter_var.set("Ciclo: 0")
        
        self.processes = [
            Process(1, "Alta", 10, 5),
            Process(2, "Media", 15, 7),
            Process(3, "Baja", 20, 10)
        ]
        
        # Restablecer conteo de estados
        self.state_counts = {state: 0 for state in PROCESS_STATES.values()}
        self.state_counts[PROCESS_STATES["NEW"]] = 3  # Inicialmente 3 procesos nuevos
        
        self.selected_process = None
        self.details_frame.pack_forget()
        
        # Actualizar interfaz y visualizaciones
        self.update_process_frames()
        self.update_state_distribution_chart()
        self.update_timeline_chart()
        self.update_resource_usage_chart()
    
    def update_process_frames(self):
        for frame in self.process_frames:
            process = frame.process
            frame.state_var.set(f"Estado: {process.current_state}")
            
            # Actualizar barra de progreso
            progress = (process.initial_execution_time - process.execution_time) / process.initial_execution_time
            frame.progress_var.set(process.initial_execution_time - process.execution_time)
            
            # Actualizar referencia del proceso
            for p in self.processes:
                if p.id == process.id:
                    frame.process = p
                    break

if __name__ == "__main__":
    app = ProcessSimulator()
    app.mainloop()