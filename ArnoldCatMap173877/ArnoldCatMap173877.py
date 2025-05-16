import os
import math
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

class ArnoldCatMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arnold Cat Map - Estados Clave")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # Variables
        self.image_path = ""
        self.iterations = tk.IntVar(value=1)
        self.original_image = None
        self.transformed_images = []
        self.period = None
        self.min_correlation_index = 0
        self.max_diff = 0
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para seleccionar imagen
        tk.Button(control_frame, text="Seleccionar Imagen", command=self.load_image).pack(side=tk.LEFT, padx=(0, 10))
        
        # Entrada para número de iteraciones
        iter_frame = tk.Frame(control_frame)
        iter_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(iter_frame, text="Iteraciones máx:").pack(side=tk.LEFT)
        tk.Entry(iter_frame, textvariable=self.iterations, width=5).pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón para aplicar transformación
        tk.Button(control_frame, text="Iterar", command=self.apply_transform).pack(side=tk.LEFT, padx=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="No hay imagen cargada")
        tk.Label(control_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Frame para mostrar las imágenes
        self.images_frame = tk.Frame(main_frame)
        self.images_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear frames para cada imagen
        self.create_image_frames()
    
    def create_image_frames(self):
        """Crea los frames para mostrar las tres imágenes clave"""
        # Frame para imagen original
        self.original_frame = tk.Frame(self.images_frame, bd=2, relief=tk.GROOVE)
        self.original_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        tk.Label(self.original_frame, text="Original", font=('Arial', 10, 'bold')).pack(pady=(5, 0))
        self.original_img_container = tk.Frame(self.original_frame, bg='white', width=300, height=300)
        self.original_img_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.original_label = tk.Label(self.original_img_container, bg='white')
        self.original_label.pack(fill=tk.BOTH, expand=True)
        self.original_info = tk.StringVar()
        tk.Label(self.original_frame, textvariable=self.original_info, font=('Arial', 8)).pack(pady=(0, 5))
        
        # Frame para imagen recuperada
        self.recovered_frame = tk.Frame(self.images_frame, bd=2, relief=tk.GROOVE)
        self.recovered_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        tk.Label(self.recovered_frame, text="Recuperada", font=('Arial', 10, 'bold')).pack(pady=(5, 0))
        self.recovered_img_container = tk.Frame(self.recovered_frame, bg='white', width=300, height=300)
        self.recovered_img_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recovered_label = tk.Label(self.recovered_img_container, bg='white')
        self.recovered_label.pack(fill=tk.BOTH, expand=True)
        self.recovered_info = tk.StringVar()
        tk.Label(self.recovered_frame, textvariable=self.recovered_info, font=('Arial', 8)).pack(pady=(0, 5))
        
        # Frame para imagen con menor correlación
        self.min_corr_frame = tk.Frame(self.images_frame, bd=2, relief=tk.GROOVE)
        self.min_corr_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        tk.Label(self.min_corr_frame, text="Menor Correlación", font=('Arial', 10, 'bold')).pack(pady=(5, 0))
        self.min_corr_img_container = tk.Frame(self.min_corr_frame, bg='white', width=300, height=300)
        self.min_corr_img_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.min_corr_label = tk.Label(self.min_corr_img_container, bg='white')
        self.min_corr_label.pack(fill=tk.BOTH, expand=True)
        self.min_corr_info = tk.StringVar()
        tk.Label(self.min_corr_frame, textvariable=self.min_corr_info, font=('Arial', 8)).pack(pady=(0, 5))
        
        # Configurar grid
        self.images_frame.grid_columnconfigure(0, weight=1)
        self.images_frame.grid_columnconfigure(1, weight=1)
        self.images_frame.grid_columnconfigure(2, weight=1)
        self.images_frame.grid_rowconfigure(0, weight=1)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            self.image_path = file_path
            try:
                self.original_image = Image.open(file_path)
                self.transformed_images = [self.original_image.copy()]
                self.period = None
                self.max_diff = 0
                self.min_correlation_index = 0
                self.show_original_image()
                self.status_var.set(f"Imagen cargada: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def apply_transform(self):
        if not self.image_path:
            messagebox.showwarning("Advertencia", "Por favor seleccione una imagen primero.")
            return
        
        try:
            max_iterations = self.iterations.get()
            if max_iterations <= 0:
                messagebox.showwarning("Advertencia", "El número de iteraciones debe ser mayor que 0.")
                return
            
            self.transformed_images = [self.original_image.copy()]
            self.period = None
            self.max_diff = 0
            self.min_correlation_index = 0
            
            # Convertir imagen original a array para comparación
            original_array = np.array(self.original_image)
            
            for i in range(1, max_iterations + 1):
                # Aplicar transformación
                transformed = self.arnold_cat_map(self.transformed_images[-1])
                self.transformed_images.append(transformed)
                
                # Calcular diferencia con la original
                current_array = np.array(transformed)
                diff = np.sum(np.abs(current_array - original_array))
                
                # Actualizar imagen con menor correlación
                if diff > self.max_diff:
                    self.max_diff = diff
                    self.min_correlation_index = i
                
                # Verificar si hemos vuelto al estado original
                if diff == 0 and self.period is None:
                    self.period = i
                    break
            
            # Mostrar resultados
            self.show_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la transformación: {str(e)}")
    
    def arnold_cat_map(self, image):
        """Aplica la transformación Arnold Cat Map a una imagen"""
        width, height = image.size
        new_image = Image.new(image.mode, (width, height))
        
        for x in range(width):
            for y in range(height):
                nx = (2 * x + y) % width
                ny = (x + y) % height
                new_image.putpixel((nx, height - ny - 1), image.getpixel((x, height - y - 1)))
        
        return new_image
    
    def show_original_image(self):
        """Muestra la imagen original"""
        self.display_image(self.original_label, self.original_image, self.original_info, "Original")
    
    def show_results(self):
        """Muestra los tres estados clave"""
        # Mostrar imagen original
        self.display_image(self.original_label, self.original_image, self.original_info, "Original")
        
        # Mostrar imagen recuperada (si se encontró el período)
        if self.period is not None:
            recovered_image = self.transformed_images[self.period]
            info = f"Recuperada (iteración {self.period})"
            self.display_image(self.recovered_label, recovered_image, self.recovered_info, info)
        else:
            self.recovered_info.set("No se recuperó en las iteraciones calculadas")
            self.recovered_label.config(image=None)
        
        # Mostrar imagen con menor correlación
        if len(self.transformed_images) > 1:
            min_corr_image = self.transformed_images[self.min_correlation_index]
            info = f"Menor correlación (iteración {self.min_correlation_index})"
            self.display_image(self.min_corr_label, min_corr_image, self.min_corr_info, info)
    
    def display_image(self, label, image, info_var, info_text):
        """Muestra una imagen en el label especificado"""
        # Redimensionar manteniendo relación de aspecto
        width, height = 300, 300  # Tamaño fijo para los frames
        
        img_ratio = image.width / image.height
        if img_ratio > 1:
            new_width = width
            new_height = int(width / img_ratio)
        else:
            new_height = height
            new_width = int(height * img_ratio)
        
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        # Actualizar el label
        label.config(image=photo)
        label.image = photo  # Guardar referencia
        info_var.set(info_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArnoldCatMapApp(root)
    root.mainloop()