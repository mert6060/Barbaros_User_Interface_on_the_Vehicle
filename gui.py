import time
import firebase_admin
from firebase_admin import credentials, firestore
import tkinter as tk
from tkinter import PhotoImage
import tkintermapview
from PIL import Image, ImageTk, ImageSequence    # Pillow library
import requests
import random
from datetime import datetime
from itertools import cycle

cred = credentials.Certificate('barbaros-402c7-firebase-adminsdk-t8rdm-8317868b9e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
API_KEY = "4f8ca64578d9ccd2ce41d985d751aaaf"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

root = tk.Tk()
root.title("Barbaros User Interfaces")
root.geometry("800x480")

# Global olarak tanımlanan widgetlar
message_label = None
safety_message = None
canvas = None
map_widget = None
panel = None
profile_img = None
profile_label = None
profile_button = None
temperature_label = None
depht_label = None
speed_label = None
battery_label = None
datetime_label = None
elapsed_time_label = None
start_time = None 
gif_frames = None
gif_label = None



def update_gui(status):
    global message_label, safety_message, canvas, map_widget, panel, profile_img, profile_label, profile_button
    global temperature_label, depht_label, speed_label, battery_label, datetime_label, elapsed_time_label, start_time
    global gif_frames, gif_label
    
    for widget in root.winfo_children():
        widget.destroy()
    
    if status is False:
        gif_file = "indir.gif"
        img = Image.open(gif_file)

        gif_frames = [
            ImageTk.PhotoImage(frame.copy().resize((800, 480), Image.Resampling.LANCZOS))
            for frame in ImageSequence.Iterator(img)
        ]
        
        gif_label = tk.Label(root)
        gif_label.pack()

        def animate_gif(index):
            frame = gif_frames[index]
            gif_label.configure(image=frame)
            index = (index + 1) % len(gif_frames)  # Loop through frames
            root.after(35, animate_gif, index)  # Adjust the delay as needed

        animate_gif(0) 
        
        
        start_time = None
        

    elif status is True:
        root.configure(bg="#2c3e50")
    
        message_label = tk.Label(root, text="Sürüş Başlatılıyor...", font=("Helvetica", 45), fg="white", bg="#2c3e50")
        message_label.pack(pady=50)

        safety_message = tk.Label(root, text="Can yeleğini takınız...\nGüvenli sınırlar oluşturuluyor...", font=("Helvetica", 28), fg="white", bg="#2c3e50")
        safety_message.pack(pady=70)

        canvas = tk.Canvas(root, width=200, height=100, bg="#2c3e50", highlightthickness=0)
        canvas.pack(pady=90)

        circle1 = canvas.create_oval(10, 40, 30, 60, fill="white", outline="white")
        circle2 = canvas.create_oval(50, 40, 70, 60, fill="white", outline="white")
        circle3 = canvas.create_oval(90, 40, 110, 60, fill="white", outline="white")

        map_width = 570
        map_height = 440
        map_widget = tkintermapview.TkinterMapView(root, width=map_width, height=map_height, corner_radius=25)

        panel_width = 350
        panel_height = map_height
        panel = tk.Frame(root, width=panel_width, height=panel_height, bg="#2c3e50")
        panel.place(x=map_width + 30, y=10)

        def load_profile_image(file_path, size=(100, 100)):
            image = Image.open(file_path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)

        profile_img = load_profile_image("profile.jpg")
        profile_label = tk.Label(panel, image=profile_img, bg="#2c3e50")
        time.sleep(1)
        profile_label.pack(pady=10)
        
        data_frame = tk.Frame(panel, bg="#2c3e50")
        data_frame.pack(pady=(20, 10))

        datetime_label = tk.Label(panel, font=("Helvetica", 16), fg="white", bg="#2c3e50")
        datetime_label.pack(pady=5)

        temperature_label = tk.Label(panel, text="Sıcaklık: -- °C", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        temperature_label.pack(pady=5)
        
        elapsed_time_label = tk.Label(panel, text="00:00:00", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        elapsed_time_label.pack(pady=5)

        def get_weather_data(lat, lon):
            url = BASE_URL + f"lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                temperature = data["main"]["temp"]
                return temperature
            else:
                return None

        depht_label = tk.Label(panel, text="Derinlik: -- m", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        depht_label.pack(pady=5)

        speed_label = tk.Label(panel, text="Hız: -- knot", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        speed_label.pack(pady=5)

        battery_label = tk.Label(panel, text="Pil Durumu:% --", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        battery_label.pack(pady=5)

        map_widget.place_forget()
        panel.place_forget()

        def get_location_from_firestore():
            dolphins_ref = db.collection('dolphins')
            docs = dolphins_ref.stream()
            for doc in docs:
                data = doc.to_dict()
                print(data)
                current_location = data['current_location']
                latitude = current_location.latitude
                longitude = current_location.longitude
                return (latitude, longitude)
            return None

        def show_map_and_panel():
            location = get_location_from_firestore()
            if location:
                latitude, longitude = location
                map_widget.set_position(latitude, longitude)
                map_widget.set_marker(latitude, longitude)
                map_widget.set_zoom(13)
                temperature = get_weather_data(latitude, longitude)
                if temperature is not None:
                    temperature_label.config(text=f"Sıcaklık: {temperature:.1f} °C")
            
            map_widget.place(x=10, y=10)
            panel.place(x=map_width + 30, y=10)

        def show_map_after_delay():
            root.after(2000, show_map_and_panel)
            message_label.destroy()
            safety_message.destroy()

        def update_temperature():
            location = get_location_from_firestore()
            if location:
                latitude, longitude = location
                temperature = get_weather_data(latitude, longitude)
                if temperature is not None:
                    temperature_label.config(text=f"Sıcaklık: {temperature:.1f} °C")
            root.after(60000, update_temperature)

        def update_speed():
            speed = random.uniform(0,0)
            speed_label.config(text=f"Hız: {speed:.1f} knot")
            root.after(2000, update_speed)

        def update_depth():
            depth = random.uniform(0.1, 0.2)
            depht_label.config(text=f"Derinlik: {depth:.1f} m")
            root.after(2000, update_depth)

        def update_battery():
            battery = random.uniform(85.0, 85.0)
            battery_label.config(text=f"Pil:% {battery:.1f}")
            root.after(2000, update_battery)

        def update_datetime():
            global start_time
            current_datetime = datetime.now().strftime("%d-%m-%Y\n%H:%M:%S")
            datetime_label.config(text=current_datetime)
            
            if start_time:
                elapsed_time = datetime.now() - start_time
                elapsed_hours = elapsed_time.seconds // 3600
                elapsed_minutes = (elapsed_time.seconds % 3600) // 60
                elapsed_seconds = elapsed_time.seconds % 60
                elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"
                elapsed_time_label.config(text=elapsed_time_str)
            else:
                elapsed_time_label.config(text="00:00:00")
                
            root.after(1000, update_datetime)

        def animate_circles(step=0):
            if step == 0:
                canvas.itemconfig(circle1, fill="white")
                canvas.itemconfig(circle2, fill="#2c3e50")
                canvas.itemconfig(circle3, fill="#2c3e50")
            elif step == 1:
                canvas.itemconfig(circle1, fill="#2c3e50")
                canvas.itemconfig(circle2, fill="white")
                canvas.itemconfig(circle3, fill="#2c3e50")
            elif step == 2:
                canvas.itemconfig(circle1, fill="#2c3e50")
                canvas.itemconfig(circle2, fill="#2c3e50")
                canvas.itemconfig(circle3, fill="white")

            root.update()
            next_step = (step + 1) % 3
            if canvas.winfo_exists():
                root.after(300, animate_circles, next_step)

        def start_animation():
            animate_circles()
            root.after(1700, show_map_after_delay)

        update_temperature()
        update_speed()
        update_depth()
        update_battery()
        update_datetime()

        start_time = datetime.now()  # Süreyi başlat
        start_animation()

def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        status = doc.to_dict().get('status')
        for change in changes:
            print(change)
        if status is not None:
            print(f"Status:{status}")
            update_gui(status)
        else:
            print('Status bulunamadı.')

dolp_ref = db.collection("dolphins").document("VS7KKfoqRL3ApkhzLDwD")
dolp_ref.on_snapshot(on_snapshot)
root.mainloop()