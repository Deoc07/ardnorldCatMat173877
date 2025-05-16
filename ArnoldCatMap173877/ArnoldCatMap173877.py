import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

class ArnoldCatMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arnold Cat Map")
        self.root.geometry("900x700")  # Tamaño fijo
        self.root.resizable(False, False)  # Deshabilitar redimensionamiento
        
        # Variables
        self.image_path = ""
        self.iterations = tk.IntVar(value=1)
        self.current_image = None
        self.photo = None
        self.transformed_images = []
        self.current_index = 0
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles (parte superior)
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para seleccionar imagen
        tk.Button(control_frame, text="Seleccionar Imagen", command=self.load_image).pack(side=tk.LEFT, padx=(0, 10))
        
        # Entrada para número de iteraciones
        iter_frame = tk.Frame(control_frame)
        iter_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(iter_frame, text="Iteraciones:").pack(side=tk.LEFT)
        tk.Entry(iter_frame, textvariable=self.iterations, width=5).pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón para aplicar transformación
        tk.Button(control_frame, text="Aplicar Transformación", command=self.apply_transform).pack(side=tk.LEFT, padx=10)
        
        # Botones de navegación
        self.prev_button = tk.Button(control_frame, text="Anterior", state=tk.DISABLED, command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=(10, 5))
        
        self.next_button = tk.Button(control_frame, text="Siguiente", state=tk.DISABLED, command=self.show_next)
        self.next_button.pack(side=tk.LEFT)
        
        # Status bar (en la misma línea)
        self.status_var = tk.StringVar(value="No hay imagen cargada")
        status_label = tk.Label(control_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Frame para mostrar la imagen (parte inferior)
        self.image_frame = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label para la imagen con tamaño fijo
        self.image_label = tk.Label(self.image_frame, bg='white')
        self.image_label.pack(fill=tk.BOTH, expand=True)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            self.image_path = file_path
            try:
                self.current_image = Image.open(file_path)
                self.transformed_images = [self.current_image.copy()]
                self.current_index = 0
                self.show_image(0)
                self.update_controls()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def apply_transform(self):
        if not self.image_path:
            messagebox.showwarning("Advertencia", "Por favor seleccione una imagen primero.")
            return
        
        try:
            iterations = self.iterations.get()
            if iterations <= 0:
                messagebox.showwarning("Advertencia", "El número de iteraciones debe ser mayor que 0.")
                return
            
            self.period_detected = False
            
            for i in range(iterations):
                transformed = self.arnold_cat_map(self.transformed_images[-1])
                self.transformed_images.append(transformed)
                
                if self.period_detected:
                    messagebox.showinfo("Período detectado", 
                                    f"La imagen ha vuelto a su estado original después de {i+1} iteraciones")
                    break
            
            self.current_index = len(self.transformed_images) - 1
            self.show_image(self.current_index)
            self.update_controls()
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la transformación: {str(e)}")
    
    def arnold_cat_map(self, image):
        """Aplica la transformación Arnold Cat Map a una imagen y detecta si vuelve a la original"""
        width, height = image.size
        new_image = Image.new(image.mode, (width, height))
    
        # Guardar los píxeles originales para comparación
        original_pixels = image.load()
    
        identical = True  # Bandera para detectar si es igual a la original
        
        for x in range(width):
            for y in range(height):
                nx = (2 * x + y) % width
                ny = (x + y) % height
                
                # Obtener el píxel original y el transformado
                original_pixel = original_pixels[x, height - y - 1]
                new_image.putpixel((nx, height - ny - 1), original_pixel)
                
                # Verificar si el píxel queda en su posición original
                if identical and (nx != x or ny != y):
                    identical = False
        
        # Si todos los píxeles volvieron a su posición original
        self.period_detected = identical
        return new_image
    
    def show_image(self, index):
        if 0 <= index < len(self.transformed_images):
            image = self.transformed_images[index]
            
            # Redimensionar manteniendo relación de aspecto para el área de visualización
            frame_width = self.image_frame.winfo_width() - 20
            frame_height = self.image_frame.winfo_height() - 20
            
            if frame_width > 1 and frame_height > 1:
                img_ratio = image.width / image.height
                frame_ratio = frame_width / frame_height
                
                if img_ratio > frame_ratio:
                    new_width = frame_width
                    new_height = int(frame_width / img_ratio)
                else:
                    new_height = frame_height
                    new_width = int(frame_height * img_ratio)
                
                image = image.resize((new_width, new_height), Image.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)
            self.update_status()
    
    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
            self.update_controls()
    
    def show_next(self):
        if self.current_index < len(self.transformed_images) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
            self.update_controls()
    
    def update_controls(self):
        # Actualizar botones de navegación
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.transformed_images) - 1 else tk.DISABLED)
        
        # Actualizar barra de estado
        self.update_status()
    
    def update_status(self):
        if not self.transformed_images:
            status = "No hay imagen cargada"
        else:
            original = self.transformed_images[0]
            current = self.transformed_images[self.current_index]
            status = f"Imagen: {os.path.basename(self.image_path)} | " \
                    f"Tamaño: {original.width}x{original.height} | " \
                    f"Iteración: {self.current_index}/{len(self.transformed_images)-1}"
        self.status_var.set(status)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArnoldCatMapApp(root)
    root.mainloop()