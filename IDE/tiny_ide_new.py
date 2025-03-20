import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import os
import re
from tkinter import font as tkfont

class TinyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("TINY IDE")
        self.filename = None
        
        # Configurar el tema de colores
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'secondary': '#2d2d2d',
            'text': '#d4d4d4',
            'keyword': '#569cd6',
            'comment': '#608b4e',
            'string': '#ce9178',
            'number': '#b5cea8',
            'error': '#f44747',
            'success': '#4ec9b0'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configurar fuente
        self.default_font = tkfont.Font(family='Consolas', size=11)
        self.title_font = tkfont.Font(family='Segoe UI', size=12, weight='bold')
        
        # Obtener la ruta del compilador y el intérprete
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.compiler_path = os.path.join(parent_dir, "tiny.exe")
        self.tm_path = os.path.join(parent_dir, "tm.exe")
        
        # Crear el menú
        self.create_menu()
        
        # Crear la barra de herramientas
        self.create_toolbar()
        
        # Crear el área principal
        self.create_main_area()
        
        # Crear la barra de estado
        self.create_status_bar()
        
        # Crear la consola
        self.create_console()
        
        # Configurar los atajos de teclado
        self.setup_shortcuts()
        
        # Keywords de TINY para resaltado
        self.keywords = ['if', 'then', 'else', 'end', 'repeat', 'until', 'read', 'write']
        
        # Configurar el estilo de ttk
        self.setup_ttk_style()
        
    def setup_ttk_style(self):
        style = ttk.Style()
        style.configure('Toolbar.TButton', 
                       padding=5, 
                       background=self.colors['accent'],
                       foreground=self.colors['fg'])
        style.configure('Status.TLabel',
                       background=self.colors['secondary'],
                       foreground=self.colors['text'],
                       padding=5)
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=2)
        
        # Botones de la barra de herramientas
        ttk.Button(toolbar, text="Nuevo", command=self.new_file, style='Toolbar.TButton').pack(side='left', padx=2)
        ttk.Button(toolbar, text="Abrir", command=self.open_file, style='Toolbar.TButton').pack(side='left', padx=2)
        ttk.Button(toolbar, text="Guardar", command=self.save_file, style='Toolbar.TButton').pack(side='left', padx=2)
        ttk.Button(toolbar, text="Compilar y Ejecutar", command=self.compile_and_run, style='Toolbar.TButton').pack(side='left', padx=2)
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.colors['bg'], fg=self.colors['fg'])
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Cortar", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Pegar", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        
        # Menú Ejecutar
        run_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Ejecutar", menu=run_menu)
        run_menu.add_command(label="Compilar y Ejecutar", command=self.compile_and_run)
        
    def create_main_area(self):
        # Frame principal con paneles
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Panel izquierdo (editor)
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(side='left', expand=True, fill='both')
        
        # Título del editor
        editor_label = ttk.Label(editor_frame, text="Editor", font=self.title_font)
        editor_label.pack(anchor='w')
        
        # Editor de texto
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            insertbackground='white',
            font=self.default_font,
            padx=10,
            pady=10
        )
        self.text_editor.pack(expand=True, fill='both')
        
        # Vincular eventos para el resaltado de sintaxis
        self.text_editor.bind('<KeyRelease>', self.highlight_syntax)
        
    def create_console(self):
        # Panel derecho (consola)
        console_frame = ttk.Frame(self.root)
        console_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Título de la consola
        console_label = ttk.Label(console_frame, text="Consola", font=self.title_font)
        console_label.pack(anchor='w')
        
        # Consola
        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=self.default_font,
            padx=10,
            pady=10
        )
        self.console.pack(expand=True, fill='both')
        
    def create_status_bar(self):
        self.status_bar = ttk.Label(
            self.root,
            text="Listo",
            style='Status.TLabel',
            anchor='w'
        )
        self.status_bar.pack(fill='x', side='bottom')
        
    def update_status(self, message):
        self.status_bar.config(text=message)
        
    def setup_shortcuts(self):
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<F5>', lambda e: self.compile_and_run())
        
    def new_file(self):
        self.text_editor.delete(1.0, tk.END)
        self.filename = None
        self.root.title("TINY IDE - Nuevo archivo")
        self.update_status("Nuevo archivo")
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("TINY files", "*.tny"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(1.0, content)
                    self.filename = file_path
                    self.root.title(f"TINY IDE - {os.path.basename(file_path)}")
                    self.highlight_syntax(None)
                    self.update_status(f"Archivo abierto: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
                
    def save_file(self):
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(
                defaultextension=".tny",
                filetypes=[("TINY files", "*.tny"), ("All files", "*.*")]
            )
        if self.filename:
            try:
                content = self.text_editor.get(1.0, tk.END)
                with open(self.filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.root.title(f"TINY IDE - {os.path.basename(self.filename)}")
                self.update_status(f"Archivo guardado: {os.path.basename(self.filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
                
    def compile_and_run(self):
        if not self.filename:
            messagebox.showwarning("Advertencia", "Guarde el archivo antes de compilar")
            return
            
        try:
            # Guardar el archivo actual
            self.save_file()
            
            # Limpiar la consola
            self.console.delete(1.0, tk.END)
            self.update_status("Compilando...")
            
            # Verificar que existe el compilador
            if not os.path.exists(self.compiler_path):
                self.console.insert(tk.END, f"Error: No se encuentra el compilador en {self.compiler_path}\n")
                self.update_status("Error de compilación")
                return
                
            if not os.path.exists(self.tm_path):
                self.console.insert(tk.END, f"Error: No se encuentra el intérprete TM en {self.tm_path}\n")
                self.update_status("Error de compilación")
                return
            
            # Compilar el archivo
            compile_process = subprocess.Popen(
                [self.compiler_path, self.filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='latin1'
            )
            
            compile_stdout, compile_stderr = compile_process.communicate()
            
            # Mostrar la salida de la compilación
            if compile_stdout:
                self.console.insert(tk.END, compile_stdout)
            if compile_stderr:
                self.console.insert(tk.END, "Errores de compilación:\n" + compile_stderr)
                self.update_status("Error de compilación")
                return
                
            # Si la compilación fue exitosa, ejecutar el código
            tm_file = os.path.splitext(self.filename)[0] + ".tm"
            if os.path.exists(tm_file):
                self.update_status("Ejecutando...")
                run_process = subprocess.Popen(
                    [self.tm_path, tm_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='latin1'
                )
                
                run_stdout, run_stderr = run_process.communicate()
                
                # Procesar la salida para mostrar solo los resultados
                if run_stdout:
                    # Dividir la salida en líneas
                    lines = run_stdout.split('\n')
                    output_buffer = []
                    current_line = ""
                    
                    for line in lines:
                        if "RESULTADO:" in line:
                            # Extraer el valor numérico
                            value = line.split("RESULTADO:")[1].strip()
                            value = value.split("=")[0].strip()
                            try:
                                # Convertir el valor a carácter si es un número
                                char_value = chr(int(value))
                                current_line += char_value
                            except ValueError:
                                # Si no es un carácter, es un número
                                if current_line:
                                    output_buffer.append(current_line)
                                    current_line = ""
                                output_buffer.append(value)
                    
                    # Agregar la última línea si existe
                    if current_line:
                        output_buffer.append(current_line)
                    
                    # Mostrar la salida procesada
                    self.console.insert(tk.END, "\nResultado de la ejecución:\n")
                    for line in output_buffer:
                        self.console.insert(tk.END, line + "\n")
                    
                    self.update_status("Ejecución completada")
                
                if run_stderr:
                    self.console.insert(tk.END, "\nErrores de ejecución:\n" + run_stderr)
                    self.update_status("Error en la ejecución")
            else:
                self.console.insert(tk.END, "\nError: No se generó el archivo .tm\n")
                self.update_status("Error de compilación")
                
        except Exception as e:
            self.console.insert(tk.END, f"Error al compilar/ejecutar: {str(e)}\n")
            self.update_status("Error en la ejecución")
            
    def highlight_syntax(self, event):
        # Eliminar el resaltado existente
        for tag in self.text_editor.tag_names():
            self.text_editor.tag_remove(tag, "1.0", tk.END)
            
        # Resaltar palabras clave
        content = self.text_editor.get("1.0", tk.END)
        for keyword in self.keywords:
            start_index = "1.0"
            while True:
                start_index = self.text_editor.search(r'\b' + keyword + r'\b', start_index, tk.END, regexp=True)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(keyword)}c"
                self.text_editor.tag_add("keyword", start_index, end_index)
                start_index = end_index
                
        # Resaltar comentarios
        start_index = "1.0"
        while True:
            start_index = self.text_editor.search(r'{', start_index, tk.END)
            if not start_index:
                break
            end_index = self.text_editor.search(r'}', start_index, tk.END)
            if not end_index:
                break
            end_index = f"{end_index}+1c"
            self.text_editor.tag_add("comment", start_index, end_index)
            start_index = end_index
            
        # Resaltar strings
        start_index = "1.0"
        while True:
            start_index = self.text_editor.search(r'"', start_index, tk.END)
            if not start_index:
                break
            end_index = self.text_editor.search(r'"', f"{start_index}+1c", tk.END)
            if not end_index:
                break
            end_index = f"{end_index}+1c"
            self.text_editor.tag_add("string", start_index, end_index)
            start_index = end_index
            
        # Resaltar números
        start_index = "1.0"
        while True:
            start_index = self.text_editor.search(r'\b\d+\b', start_index, tk.END, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+1c"
            while self.text_editor.get(end_index).isdigit():
                end_index = f"{end_index}+1c"
            self.text_editor.tag_add("number", start_index, end_index)
            start_index = end_index
            
        # Configurar colores de resaltado
        self.text_editor.tag_config("keyword", foreground=self.colors['keyword'])
        self.text_editor.tag_config("comment", foreground=self.colors['comment'])
        self.text_editor.tag_config("string", foreground=self.colors['string'])
        self.text_editor.tag_config("number", foreground=self.colors['number'])

if __name__ == "__main__":
    root = tk.Tk()
    app = TinyIDE(root)
    root.geometry("1200x800")
    root.mainloop() 