import mpv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class RadioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Your Personal Online Radio Player")
        self.root.geometry("350x400")  # Smaller window
        self.root.minsize(350, 400)    # Minimum size
        self.root.bind("<Configure>", lambda event: self.draw_gradient())  # Redraw on resize

        self.player = None
        self.stations = []
        self.current_station = None

        self.style = ttk.Style()
        self.style.configure("Custom.TButton", background="#1a73e8", foreground="white", font=('Arial', 10, 'bold'), padding=5)
        self.style.configure("Custom.TFrame", background="#f0f0f0")
        self.style.configure("Custom.TLabel", background="#f0f0f0", font=('Arial', 10))


        self.create_widgets()  # Ensure widgets are created before using them

        self.default_station = "http://derti.live24.gr/derty1000"
        self.stations.append(("Derti Radio", self.default_station))
        
        self.update_station_list()  # Now safe to call

    def stop(self):
        if self.player is not None:
            self.player.stop()
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.update_status("Stopped")

    
    def create_widgets(self):
        # Create a Canvas for the gradient
        self.canvas = tk.Canvas(self.root, width=350, height=400, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw the gradient
        self.draw_gradient()

        # Create a frame *inside* the Canvas and make it blend with the background
        self.main_frame = ttk.Frame(self.canvas, style="Custom.TFrame")
        self.canvas.create_window(175, 200, window=self.main_frame)  # Center the frame

        # Logo area
        self.logo_label = ttk.Label(self.main_frame, background="")  # Transparent
        self.logo_label.pack(pady=5)

        # Station list
        self.station_list = ttk.Combobox(self.main_frame, state='readonly')
        self.station_list.pack(fill=tk.X, pady=5)
        self.station_list.bind('<<ComboboxSelected>>', self.select_station)

        # Load stations button
        load_btn = ttk.Button(self.main_frame, text="Load Stations File", command=self.load_stations, style="Custom.TButton")
        load_btn.pack(pady=5)

        # Control buttons
        btn_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
        btn_frame.pack(pady=10)

        self.play_btn = ttk.Button(btn_frame, text="Play", command=self.play, style="Custom.TButton")
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, style="Custom.TButton")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state=tk.DISABLED)

        # Volume control
        volume_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
        volume_frame.pack(pady=5)

        ttk.Label(volume_frame, text="Volume:", style="Custom.TLabel").pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.set(55)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN, style="Custom.TLabel")
        self.status.pack(fill=tk.X, pady=5)


    def draw_gradient(self):
        """Draws a gradient background from dark blue to light blue."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        self.canvas.delete("gradient")  # Clear previous gradient

        for i in range(height):
            color = f"#{int(20 + (i / height) * 100):02x}{int(50 + (i / height) * 100):02x}{int(200 - (i / height) * 50):02x}"
            self.canvas.create_line(0, i, width, i, fill=color, width=1, tags="gradient")

        self.root.update_idletasks()



    
    def load_stations(self):
        file_path = filedialog.askopenfilename(
            title="Select Stations File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                self.stations = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) < 2:
                            continue  # Skip invalid lines
                        
                        name = parts[0].strip()
                        url = parts[1].strip()
                        logo = parts[2].strip() if len(parts) > 2 else "default-logo.png"

                        self.stations.append((name, url, logo))

                self.update_station_list()
                self.update_status(f"Loaded {len(self.stations)} stations from file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stations:\n{str(e)}")



    
    def update_station_list(self):
        names = [station[0] for station in self.stations]  # Extract names safely
        self.station_list['values'] = names

        if names:
            self.station_list.current(0)
            self.current_station = self.stations[0][1]  # URL
            logo = self.stations[0][2] if len(self.stations[0]) > 2 else "default-logo.png"
            self.update_logo(logo)



    def update_logo(self, logo_filename):
        try:
            self.logo_image = tk.PhotoImage(file=logo_filename)
            self.logo_label.config(image=self.logo_image)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load logo: {logo_filename}")


    
    def select_station(self, event=None):
        selection = self.station_list.current()
        if 0 <= selection < len(self.stations):
            self.current_station = self.stations[selection][1]  # URL
            logo = self.stations[selection][2] if len(self.stations[selection]) > 2 else "default-logo.png"
            self.update_logo(logo)
            self.stop()
            self.play()



    
    def play(self):
        if not self.current_station:
            messagebox.showwarning("Warning", "No station selected")
            return
            
        if self.player is None:
            self.player = mpv.MPV(
                ytdl=True,
                input_default_bindings=True,
                input_vo_keyboard=True,
                vid=False,  # Disable video output
                audio_display=False,  # Disable video-related audio display
                audio_client_name='Your Personal Online Radio Player'
            )
            self.player.volume = self.volume_slider.get()
        
        try:
            self.player.play(self.current_station)
            self.play_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_status(f"Playing: {self.station_list.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play stream:\n{str(e)}")
    
    def set_volume(self, value):
        if self.player is not None:
            self.player.volume = float(value)
    
    def update_status(self, message):
        self.status.config(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = RadioPlayer(root)
    root.mainloop()
