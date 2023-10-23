import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from scipy.integrate import quad
from tkinter import messagebox

grid_size = 49  # Definisikan ukuran grid

# Inisialisasi koordinat kepala, kaki, dan titik ketiga
x1, y1, x2, y2 = None, None, None, None

def set_background():
    global x1, y1, x2, y2
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
    if file_path:
        img = Image.open(file_path)
        img_width, img_height = img.size
        window_width, window_height = root.winfo_screenwidth(), root.winfo_screenheight()
        aspect_ratio = img_width / img_height

        if (window_width / aspect_ratio) > window_height:
            new_width = int(window_height * aspect_ratio * 0.9)
            new_height = int(window_height * 0.9)
        else:
            new_width = int(window_width * 0.9)
            new_height = int(window_width / aspect_ratio * 0.9)

        img = img.resize((new_width, new_height))

        photo = ImageTk.PhotoImage(img)
        background_canvas.create_image(0, 0, image=photo, anchor='nw')
        background_canvas.image = photo

        background_canvas.config(scrollregion=background_canvas.bbox("all"), width=new_width, height=new_height)

        draw_grid(new_width, new_height)

        # Aktifkan scrollbar
        canvas_vscrollbar.config(command=background_canvas.yview)
        canvas_hscrollbar.config(command=background_canvas.xview)
        background_canvas.config(yscrollcommand=canvas_vscrollbar.set, xscrollcommand=canvas_hscrollbar.set)

def draw_grid(width, height):
    background_canvas.delete('grid_line')
    scale_factor = 1  # Faktor skala (1 pixel dalam grid setara dengan satu satuan)
    for i in range(0, width, grid_size):
        background_canvas.create_line(i, 0, i, height, tag='grid_line', fill='red')
        background_canvas.create_text(i+grid_size//2+18, height-grid_size//2, text=str(i//grid_size*scale_factor), fill='white')
    for i in range(0, height, grid_size):
        background_canvas.create_line(0, i, width, i, tag='grid_line', fill='red')
        background_canvas.create_text(grid_size//2+18, height-i-grid_size//2, text=str(i//grid_size*scale_factor), fill='white')

def mark_coordinate(event):
    global x1, y1, x2, y2
    x, y = event.x, event.y
    x_grid = (x - grid_size) / grid_size  # Memulai dari -1

    # Get the current scroll position
    scroll_pos = background_canvas.yview()

    # Calculate the total height of the canvas
    total_height = background_canvas.winfo_height() / (scroll_pos[1] - scroll_pos[0])

    # Adjust the y-coordinate for the scroll position
    y = y + scroll_pos[0] * total_height

    y_grid = (background_canvas.winfo_height() - y) / grid_size + 1.1
    if x1 is None:
        x1, y1 = x_grid, y_grid
        background_canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill='white', outline='white')
    elif x2 is None:
        x2, y2 = x_grid, y_grid
        background_canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill='yellow', outline='yellow')

def show_marked_coordinates():
    if x1 is not None and x2 is not None:
        coordinates_text = f"Titik 1 (x1, y1): ({x1}, {y1})\nTitik 2 (x2, y2): ({x2}, {y2})"
        
        # Create a new Toplevel window
        dialog = tk.Toplevel(root)
        dialog.title("Coordinates")

        # Create a label with the coordinates text
        label = tk.Label(dialog, text=coordinates_text)
        label.pack()

        # Create a button to close the dialog
        button = tk.Button(dialog, text="Close", command=dialog.destroy)
        button.pack()
    else:
        messagebox.showwarning("Warning", "No coordinates marked")

def reset_coordinates():
    global x1, y1, x2, y2
    x1, y1, x2, y2 = None, None, None, None
    background_canvas.delete('all')
    messagebox.showinfo("Reset", "Program telah direset")
    

def calculate_volume_integral():
    if x1 is not None and x2 is not None:
        try:
            # Mengambil nilai diameter kepala dari entry widget
            diameterKepala = float(diameterKepala_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Diameter harus berupa angka")
            return

        # Menghitung tinggi bayi dari perbedaan y antara kepala dan kaki bayi
        panjangBayi = abs(x2 - x1)

        # Menghitung berat janin menggunakan rumus integral
        def berat(x):
            y = diameterKepala / panjangBayi
            return (y * x) ** 2

        # Batas bawah dan batas atas integral
        a = 0
        b = panjangBayi

        # Menghitung integral menggunakan quad dari scipy
        integral_result, _ = quad(berat, a, b)
        import math
        integral_result = math.pi * integral_result  # Berat dalam cm^3
    
        result_text = f"Berat Bayi: {integral_result:.2f} gram\nJarak antara kepala dan kaki: {panjangBayi:.2f} cm\nDiameter Kepala: {diameterKepala:.2f} cm"

        # Menampilkan pop up hasil perhitungan
        messagebox.showinfo("Hasil Perhitungan", result_text)
    else:
        messagebox.showerror("Kesalahan", "Diperlukan setidaknya dua koordinat (x1, y1, x2, y2) dan diameter untuk menghitung berat bayi berdasarkan fungsi.")

root = tk.Tk()
root.title("Program Perhitungan Estimasi Berat Janin")

bg_button = tk.Button(root, text="Upload Gambar", command=set_background)
bg_button.grid(row=0, column=3)

background_canvas = tk.Canvas(root)
background_canvas.grid(row=0, column=1)
background_canvas.bind("<Button-1>", mark_coordinate)

show_button = tk.Button(root, text="Tampilkan Koordinat yang ditandai", command=show_marked_coordinates)
show_button.grid(row=2, column=3, padx=(10, 0))

volume_button = tk.Button(root, text="Hitung Berat Bayi (Integral)", command=calculate_volume_integral)
volume_button.grid(row=1, column=3, pady=(10, 0))

diameterKepala_frame = tk.Frame(root)
diameterKepala_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

reset_button = tk.Button(root, text="Reset", command=reset_coordinates)
reset_button.grid(row=3, column=3, padx=(10, 0))

diameterKepala_entry_label = tk.Label(diameterKepala_frame, text="Diameter (cm):")
diameterKepala_entry_label.pack(side='left')

diameterKepala_entry = tk.Entry(diameterKepala_frame)
diameterKepala_entry.pack(side='left')

coordinates_label = tk.Label(root, justify='left', anchor='e', font=('Arial', 12))
coordinates_label.grid(row=0, column=4, rowspan=2, sticky='nsew', padx=(0, 10), pady=(10, 0))

canvas_vscrollbar = tk.Scrollbar(root, orient='vertical')
canvas_hscrollbar = tk.Scrollbar(root, orient='horizontal')
canvas_vscrollbar.grid(row=0, column=6, sticky='ns')
canvas_hscrollbar.grid(row=8, column=1, sticky='ew')

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.geometry("1000x1000")
root.mainloop()
