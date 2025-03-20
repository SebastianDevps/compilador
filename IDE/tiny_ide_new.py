import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, Canvas
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
            'bg': '#ffffff',               # Fondo principal (blanco)
            'activity_bar': '#f3f3f3',     # Barra de actividad (gris muy claro)
            'sidebar': '#f8f8f8',          # Panel lateral (casi blanco)
            'editor': '#ffffff',           # Editor (blanco)
            'panel': '#f8f8f8',            # Panel inferior
            'statusbar': '#0078d4',        # Barra de estado (azul más suave)
            'tab_active': '#ffffff',       # Pestaña activa
            'tab_inactive': '#f3f3f3',     # Pestaña inactiva
            'tab_border': '#e4e4e4',       # Borde de pestañas
            'fg': '#000000',               # Texto general (negro)
            'fg_inactive': '#666666',      # Texto inactivo
            'accent': '#0078d4',           # Color de acento (azul)
            'list_active': '#e8e8e8',      # Item activo en lista
            'list_hover': '#f0f0f0',       # Item hover en lista
            'editor_line': '#999999',      # Números de línea
            'keyword': '#0000ff',          # Palabras clave (azul)
            'comment': '#008000',          # Comentarios (verde)
            'string': '#a31515',           # Strings (rojo oscuro)
            'number': '#098658',           # Números (verde oscuro)
            'border': '#e4e4e4'            # Bordes
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configurar fuentes
        self.code_font = tkfont.Font(family='Consolas', size=11)
        self.ui_font = tkfont.Font(family='Segoe UI', size=9)
        self.title_font = tkfont.Font(family='Segoe UI', size=20, weight='bold')
        self.subtitle_font = tkfont.Font(family='Segoe UI', size=12)
        
        # Crear layout principal
        self.create_layout()
        
        # Keywords de TINY
        self.keywords = ['if', 'then', 'else', 'end', 'repeat', 'until', 'read', 'write']
        
        # Configurar estilos
        self.setup_styles()
        
    def create_layout(self):
        # Barra de menú
        self.create_menu()
        
        # Layout principal
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Barra lateral izquierda con iconos
        self.create_sidebar()
        
        # Panel del explorador
        self.explorer_frame = ttk.Frame(self.main_paned, style='Sidebar.TFrame', width=250)
        self.main_paned.add(self.explorer_frame)
        
        # Área principal
        self.editor_frame = ttk.Frame(self.main_paned, style='Editor.TFrame')
        self.main_paned.add(self.editor_frame, weight=1)
        
        # Crear componentes
        self.create_explorer()
        self.create_editor_area()
        self.create_bottom_panel()
        self.create_status_bar()
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.colors['bg'], fg=self.colors['fg'])
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo archivo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir archivo...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Deshacer", command=lambda: self.text_editor.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rehacer", command=lambda: self.text_editor.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cortar", command=lambda: self.text_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=lambda: self.text_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Pegar", command=lambda: self.text_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        
        # Menú Ejecutar
        run_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['fg'])
        menubar.add_cascade(label="Ejecutar", menu=run_menu)
        run_menu.add_command(label="Compilar y Ejecutar", command=self.compile_and_run, accelerator="F5")
        
    def create_sidebar(self):
        sidebar = ttk.Frame(self.root, style='Activity.TFrame', width=48)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Botones de la barra lateral
        self.create_sidebar_button(sidebar, "📂", "Explorador", 0, lambda: self.show_explorer())
        self.create_sidebar_button(sidebar, "🔍", "Buscar", 1, lambda: None)
        self.create_sidebar_button(sidebar, "⑂", "Control de código", 2, lambda: None)
        self.create_sidebar_button(sidebar, "▶", "Ejecutar", 3, self.compile_and_run)
        
        # Botón de configuración en la parte inferior
        self.create_sidebar_button(sidebar, "⚙", "Configuración", -1, lambda: None)
        
    def create_sidebar_button(self, parent, icon, tooltip, position, command):
        btn = ttk.Label(
            parent,
            text=icon,
            style='Activity.TLabel',
            cursor='hand2'
        )
        btn.bind('<Button-1>', lambda e: command())
        if position < 0:
            btn.pack(side=tk.BOTTOM, pady=5)
        else:
            btn.pack(side=tk.TOP, pady=5)
            
    def create_explorer(self):
        # Título del explorador
        header = ttk.Frame(self.explorer_frame, style='SidebarHeader.TFrame')
        header.pack(fill=tk.X, padx=2, pady=(2,0))
        
        ttk.Label(
            header,
            text="EXPLORADOR",
            style='SidebarHeader.TLabel'
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Árbol de archivos
        self.file_tree = ttk.Treeview(
            self.explorer_frame,
            style='Sidebar.Treeview',
            show='tree',
            selectmode='browse'
        )
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Configurar el estilo del árbol
        style = ttk.Style()
        style.configure('Sidebar.Treeview',
                       background=self.colors['sidebar'],
                       foreground=self.colors['fg'],
                       fieldbackground=self.colors['sidebar'])
        
        # Vincular eventos
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Cargar archivos
        self.load_directory()
        
    def load_directory(self):
        # Limpiar árbol
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Obtener directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Insertar directorio raíz
        root_node = self.file_tree.insert('', 'end', text=os.path.basename(parent_dir), open=True)
        
        # Cargar archivos
        self.load_files(parent_dir, root_node)
        
    def load_files(self, path, parent):
        try:
            # Listar archivos y directorios
            items = os.listdir(path)
            
            # Ordenar: primero directorios, luego archivos
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for item in items:
                item_path = os.path.join(path, item)
                
                # Ignorar archivos y carpetas ocultos
                if item.startswith('.'):
                    continue
                    
                if os.path.isdir(item_path):
                    # Es un directorio
                    folder = self.file_tree.insert(parent, 'end', text=item, open=False)
                    self.load_files(item_path, folder)
                else:
                    # Es un archivo
                    if item.endswith('.tny'):
                        self.file_tree.insert(parent, 'end', text=item, values=(item_path,))
                        
        except Exception as e:
            print(f"Error al cargar directorio: {str(e)}")
            
    def on_file_double_click(self, event):
        # Obtener el item seleccionado
        item = self.file_tree.selection()[0]
        values = self.file_tree.item(item)['values']
        
        # Si es un archivo (tiene values con la ruta)
        if values:
            file_path = values[0]
            if os.path.isfile(file_path):
                self.open_file_from_path(file_path)
                
    def open_file_from_path(self, file_path):
        # Crear nueva pestaña
        editor_frame = ttk.Frame(self.tab_container, style='Editor.TFrame')
        self.tab_container.add(editor_frame, text=os.path.basename(file_path))
        self.create_editor(editor_frame)
        self.tab_container.select(editor_frame)
        
        # Cargar contenido
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, content)
                self.filename = file_path
                self.highlight_syntax()
                self.status_text.config(text=f"Archivo abierto: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
        
    def create_editor_area(self):
        # Contenedor de pestañas
        self.tab_container = ttk.Notebook(
            self.editor_frame,
            style='Editor.TNotebook'
        )
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        
        # Página de bienvenida
        self.create_welcome_page()
        
    def create_welcome_page(self):
        welcome_frame = ttk.Frame(self.tab_container, style='Editor.TFrame')
        self.tab_container.add(welcome_frame, text='Bienvenido')
        
        # Contenedor central
        center_frame = ttk.Frame(welcome_frame, style='Editor.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        title = ttk.Label(
            center_frame,
            text="TINY IDE",
            font=self.title_font,
            foreground=self.colors['fg'],
            background=self.colors['editor']
        )
        title.pack(pady=(0,20))
        
        # Acciones comunes
        actions_frame = ttk.Frame(center_frame, style='Editor.TFrame')
        actions_frame.pack(fill=tk.X, pady=10)
        
        self.create_welcome_button(actions_frame, "Nuevo archivo", "Ctrl+N", self.new_file)
        self.create_welcome_button(actions_frame, "Abrir archivo", "Ctrl+O", self.open_file)
        self.create_welcome_button(actions_frame, "Ejecutar programa", "F5", self.compile_and_run)
        
    def create_welcome_button(self, parent, text, shortcut, command):
        button_frame = ttk.Frame(parent, style='Editor.TFrame')
        button_frame.pack(fill=tk.X, pady=5)
        
        btn = ttk.Label(
            button_frame,
            text=text,
            font=self.subtitle_font,
            foreground=self.colors['accent'],
            background=self.colors['editor'],
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT)
        btn.bind('<Button-1>', lambda e: command())
        
        shortcut_label = ttk.Label(
            button_frame,
            text=shortcut,
            font=self.ui_font,
            foreground=self.colors['fg_inactive'],
            background=self.colors['editor']
        )
        shortcut_label.pack(side=tk.RIGHT)
        
    def create_editor(self, parent):
        editor_container = ttk.Frame(parent, style='Editor.TFrame')
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Números de línea
        self.line_numbers = Canvas(
            editor_container,
            width=45,
            bg=self.colors['editor'],
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            bg=self.colors['editor'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['fg'],
            font=self.code_font,
            padx=10,
            pady=5,
            undo=True
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Eventos
        self.text_editor.bind('<KeyRelease>', self.on_editor_change)
        self.text_editor.bind('<Configure>', self.update_line_numbers)
        
    def create_bottom_panel(self):
        self.bottom_panel = ttk.Notebook(
            self.root,
            style='Panel.TNotebook',
            height=150
        )
        self.bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Terminal
        terminal_frame = ttk.Frame(self.bottom_panel, style='Panel.TFrame')
        self.bottom_panel.add(terminal_frame, text='Terminal')
        
        self.console = scrolledtext.ScrolledText(
            terminal_frame,
            wrap=tk.NONE,
            bg=self.colors['panel'],
            fg=self.colors['fg'],
            font=self.code_font,
            padx=5,
            pady=5
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style='Status.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(
            status_frame,
            text="TINY",
            style='Status.TLabel'
        ).pack(side=tk.LEFT, padx=5)
        
        self.status_text = ttk.Label(
            status_frame,
            text="Listo",
            style='Status.TLabel'
        )
        self.status_text.pack(side=tk.RIGHT, padx=5)
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Frames
        style.configure('Activity.TFrame', background=self.colors['activity_bar'])
        style.configure('Sidebar.TFrame', background=self.colors['sidebar'])
        style.configure('Editor.TFrame', background=self.colors['editor'])
        style.configure('Panel.TFrame', background=self.colors['panel'])
        style.configure('Status.TFrame', background=self.colors['statusbar'])
        
        # Labels
        style.configure('Activity.TLabel',
                       background=self.colors['activity_bar'],
                       foreground=self.colors['fg_inactive'],
                       font=self.ui_font)
        style.configure('SidebarHeader.TLabel',
                       background=self.colors['sidebar'],
                       foreground=self.colors['fg_inactive'],
                       font=self.ui_font)
        style.configure('Status.TLabel',
                       background=self.colors['statusbar'],
                       foreground='white',
                       font=self.ui_font)
        
        # Notebook
        style.configure('Editor.TNotebook',
                       background=self.colors['tab_border'],
                       borderwidth=0)
        style.configure('Editor.TNotebook.Tab',
                       background=self.colors['tab_inactive'],
                       foreground=self.colors['fg_inactive'],
                       padding=[10, 3],
                       font=self.ui_font)
        style.map('Editor.TNotebook.Tab',
                 background=[('selected', self.colors['tab_active'])],
                 foreground=[('selected', self.colors['fg'])])
        
        # Panel inferior
        style.configure('Panel.TNotebook',
                       background=self.colors['panel'],
                       borderwidth=0)
        style.configure('Panel.TNotebook.Tab',
                       background=self.colors['panel'],
                       foreground=self.colors['fg_inactive'],
                       padding=[10, 3],
                       font=self.ui_font)
        
    def new_file(self):
        # Crear nueva pestaña
        editor_frame = ttk.Frame(self.tab_container, style='Editor.TFrame')
        self.tab_container.add(editor_frame, text='Sin título')
        self.create_editor(editor_frame)
        self.tab_container.select(editor_frame)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos TINY", "*.tny"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            # Crear nueva pestaña
            editor_frame = ttk.Frame(self.tab_container, style='Editor.TFrame')
            self.tab_container.add(editor_frame, text=os.path.basename(file_path))
            self.create_editor(editor_frame)
            self.tab_container.select(editor_frame)
            
            # Cargar contenido
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(1.0, content)
                    self.filename = file_path
                    self.highlight_syntax()
                    self.status_text.config(text=f"Archivo abierto: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
                
    def save_file(self):
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(
                defaultextension=".tny",
                filetypes=[("Archivos TINY", "*.tny"), ("Todos los archivos", "*.*")]
            )
        if self.filename:
            try:
                content = self.text_editor.get(1.0, tk.END)
                with open(self.filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_text.config(text=f"Archivo guardado: {os.path.basename(self.filename)}")
                # Actualizar título de la pestaña
                current_tab = self.tab_container.select()
                self.tab_container.tab(current_tab, text=os.path.basename(self.filename))
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
                
    def show_explorer(self):
        # Toggle del panel explorador
        if self.explorer_frame.winfo_ismapped():
            self.explorer_frame.pack_forget()
        else:
            self.explorer_frame.pack(side=tk.LEFT, fill=tk.Y)
            
    def on_editor_change(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()
        
    def update_line_numbers(self, event=None):
        self.line_numbers.delete('all')
        line_count = int(self.text_editor.index('end-1c').split('.')[0])
        
        for i in range(1, line_count + 1):
            y = int(self.text_editor.dlineinfo(f"{i}.0")[1])
            self.line_numbers.create_text(
                35, y + 10,
                text=str(i),
                fill=self.colors['editor_line'],
                anchor='e',
                font=self.code_font
            )
            
    def highlight_syntax(self):
        # Eliminar resaltado existente
        for tag in self.text_editor.tag_names():
            self.text_editor.tag_remove(tag, "1.0", tk.END)
            
        content = self.text_editor.get("1.0", tk.END)
        
        # Resaltar palabras clave
        for keyword in self.keywords:
            start = "1.0"
            while True:
                start = self.text_editor.search(r'\b' + keyword + r'\b', start, tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.text_editor.tag_add("keyword", start, end)
                start = end
                
        # Resaltar comentarios
        start = "1.0"
        while True:
            start = self.text_editor.search(r'{', start, tk.END)
            if not start:
                break
            end = self.text_editor.search(r'}', start, tk.END)
            if not end:
                break
            end = f"{end}+1c"
            self.text_editor.tag_add("comment", start, end)
            start = end
            
        # Resaltar strings
        start = "1.0"
        while True:
            start = self.text_editor.search(r'"', start, tk.END)
            if not start:
                break
            end = self.text_editor.search(r'"', f"{start}+1c", tk.END)
            if not end:
                break
            end = f"{end}+1c"
            self.text_editor.tag_add("string", start, end)
            start = end
            
        # Resaltar números
        start = "1.0"
        while True:
            start = self.text_editor.search(r'\b\d+\b', start, tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+1c"
            while self.text_editor.get(end).isdigit():
                end = f"{end}+1c"
            self.text_editor.tag_add("number", start, end)
            start = end
            
        # Configurar colores
        self.text_editor.tag_config("keyword", foreground=self.colors['keyword'])
        self.text_editor.tag_config("comment", foreground=self.colors['comment'])
        self.text_editor.tag_config("string", foreground=self.colors['string'])
        self.text_editor.tag_config("number", foreground=self.colors['number'])
        
    def compile_and_run(self):
        if not self.filename:
            messagebox.showwarning("Advertencia", "Guarde el archivo antes de compilar")
            return
            
        try:
            self.save_file()
            self.console.delete(1.0, tk.END)
            self.status_text.config(text="Compilando...")
            
            # Verificar compilador y TM
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            compiler_path = os.path.join(parent_dir, "tiny.exe")
            tm_path = os.path.join(parent_dir, "tm.exe")
            
            if not os.path.exists(compiler_path):
                self.console.insert(tk.END, "Error: No se encuentra el compilador\n")
                self.status_text.config(text="Error de compilación")
                return
                
            if not os.path.exists(tm_path):
                self.console.insert(tk.END, "Error: No se encuentra el intérprete TM\n")
                self.status_text.config(text="Error de compilación")
                return
            
            # Compilar
            compile_process = subprocess.Popen(
                [compiler_path, self.filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='latin1'
            )
            
            compile_stdout, compile_stderr = compile_process.communicate()
            
            if compile_stdout:
                self.console.insert(tk.END, compile_stdout)
            if compile_stderr:
                self.console.insert(tk.END, "Errores de compilación:\n" + compile_stderr)
                self.status_text.config(text="Error de compilación")
                return
                
            # Ejecutar
            tm_file = os.path.splitext(self.filename)[0] + ".tm"
            if os.path.exists(tm_file):
                self.status_text.config(text="Ejecutando...")
                run_process = subprocess.Popen(
                    [tm_path, tm_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='latin1'
                )
                
                run_stdout, run_stderr = run_process.communicate()
                
                if run_stdout:
                    lines = run_stdout.split('\n')
                    output_buffer = []
                    current_line = ""
                    
                    for line in lines:
                        if "RESULTADO:" in line:
                            value = line.split("RESULTADO:")[1].strip()
                            value = value.split("=")[0].strip()
                            try:
                                char_value = chr(int(value))
                                current_line += char_value
                            except ValueError:
                                if current_line:
                                    output_buffer.append(current_line)
                                    current_line = ""
                                output_buffer.append(value)
                    
                    if current_line:
                        output_buffer.append(current_line)
                    
                    self.console.insert(tk.END, "\nResultado:\n")
                    for line in output_buffer:
                        self.console.insert(tk.END, line + "\n")
                    
                    self.status_text.config(text="Listo")
                
                if run_stderr:
                    self.console.insert(tk.END, "\nErrores de ejecución:\n" + run_stderr)
                    self.status_text.config(text="Error en la ejecución")
            else:
                self.console.insert(tk.END, "\nError: No se generó el archivo .tm\n")
                self.status_text.config(text="Error de compilación")
                
        except Exception as e:
            self.console.insert(tk.END, f"Error: {str(e)}\n")
            self.status_text.config(text="Error en la ejecución")

if __name__ == "__main__":
    root = tk.Tk()
    app = TinyIDE(root)
    root.geometry("1200x800")
    root.mainloop() 