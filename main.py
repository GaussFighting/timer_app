import os
import sys
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import logging
import csv

# Konfiguracja logowania
log_file = os.path.join(os.path.expanduser("~"), "multi_timer_log.txt")
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Ustawienie daty wygaśnięcia na 31 sierpnia 2024
expiry = datetime(2024, 8, 31)

# Funkcja sprawdzająca datę wygaśnięcia
def is_trial_expired():
    current_date = datetime.now()
    return current_date > expiry

# Funkcja do wczytywania konfiguracji z pliku config.txt
def load_config():
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(sys._MEIPASS, 'config.txt')
    else:
        config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
        
    if not os.path.exists(config_path):
        messagebox.showerror("Błąd", "Plik konfiguracyjny 'config.txt' nie został znaleziony.")
        return None, None

    with open(config_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if len(lines) < 2:  # Sprawdzenie czy są co najmniej 1 linia dla imienia i nazwiska i co najmniej jedna dla nazw procesów
        messagebox.showerror("Błąd", "Plik konfiguracyjny 'config.txt' jest niekompletny.")
        return None, None

    name = lines[0].strip()
    process_names = [line.strip() for line in lines[1:] if line.strip()]  # Wczytanie nazw procesów i usunięcie pustych linii

    return name, process_names

# Przykład użycia funkcji
if is_trial_expired():
    messagebox.showerror("Błąd", "Wersja próbna wygasła")
else:
    class TimerApp:
        def __init__(self, root, name, process_names):
            self.root = root
            self.root.title("Multi Timer App")
            self.name = name
            self.process_names = process_names[:8]  # Ograniczenie liczby procesów do 8

            self.name_frame = tk.Frame(root)
            self.name_frame.pack(padx=10, pady=5)

            tk.Label(self.name_frame, text=f"{self.name}").pack()

            self.timers_frame = tk.Frame(root)
            self.timers_frame.pack(padx=10, pady=5)

            self.timers = []

            # Dodanie procesu "Przerwa"
            self.create_timer("Przerwa")

            for process_name in self.process_names:
                self.create_timer(process_name)

            self.report_button = tk.Button(root, text="Koniec pracy", command=self.end_work)
            self.report_button.pack(pady=10)

            # Startowanie timera "Przerwa"
            self.start_timer(0)

        def create_timer(self, process_name):
            frame = tk.Frame(self.timers_frame)
            frame.pack(padx=10, pady=5)

            time_label = tk.Label(frame, text="0:00:00", font=("Helvetica", 24))
            time_label.grid(row=0, column=1, columnspan=4)

            start_button = tk.Button(frame, text=process_name, command=lambda name=process_name: self.start_timer_by_name(name))
            start_button.grid(row=0, column=0, padx=5)

            timer = {
                'frame': frame,
                'process_name': process_name,
                'time_label': time_label,
                'start_button': start_button,
                'running': False,
                'start_time': None,
                'elapsed_time': timedelta(),
                'after_id': None
            }
            self.timers.append(timer)

        def update_time(self, index):
            timer = self.timers[index]
            if timer['running']:
                timer['elapsed_time'] = datetime.now() - timer['start_time']
                timer['time_label'].config(text=str(timer['elapsed_time']).split(".")[0])
                timer['after_id'] = self.root.after(1000, self.update_time, index)

        def start_timer_by_name(self, process_name):
            for i, timer in enumerate(self.timers):
                if timer['process_name'] == process_name:
                    self.start_timer(i)
                else:
                    self.stop_timer(i)

        def start_timer(self, index):
            for i, timer in enumerate(self.timers):
                if i != index:
                    self.stop_timer(i)
                    self.set_timer_color(i, "white")  # Przywrócenie koloru czcionki dla nieaktywnych timerów
            timer = self.timers[index]
            if not timer['running']:
                timer['start_time'] = datetime.now() - timer['elapsed_time']
                timer['running'] = True
                self.update_time(index)
                self.set_active_timer_color(index, "green")  # Ustawienie koloru zielonego dla aktywnego timera

        def stop_timer(self, index):
            timer = self.timers[index]
            if timer['running']:
                self.root.after_cancel(timer['after_id'])
                timer['running'] = False
                self.set_timer_color(index, "white")  # Przywrócenie koloru czcionki dla nieaktywnego timera

        def set_active_timer_color(self, index, color):
            timer = self.timers[index]
            timer['start_button'].config(fg=color)  # Zmiana koloru czcionki przycisku procesu
            timer['time_label'].config(fg=color)  # Zmiana koloru czcionki czasu timera

        def set_timer_color(self, index, color):
            timer = self.timers[index]
            timer['start_button'].config(fg=color)  # Zmiana koloru czcionki przycisku procesu
            timer['time_label'].config(fg=color)  # Zmiana koloru czcionki czasu timera

        def end_work(self):
            for i in range(len(self.timers)):
                self.stop_timer(i)
            self.generate_report()
            self.root.destroy()

        def generate_report(self):
            report_lines = [["Imię i nazwisko", self.name]]

            for timer in self.timers:
                process_name = timer['process_name']
                elapsed_time = str(timer['elapsed_time']).split(".")[0]
                report_lines.append([process_name, elapsed_time])

            current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            report_file_name = f"raport-{current_time}.csv"
            report_file_path = os.path.join(os.path.expanduser("~"), report_file_name)

            try:
                with open(report_file_path, "w", newline='', encoding='utf-8') as report_file:
                    writer = csv.writer(report_file)
                    writer.writerows(report_lines)
                logging.info(f"Raport zapisany w: {report_file_path}")
            except Exception as e:
                logging.error(f"Błąd podczas zapisywania raportu: {e}")
                messagebox.showerror("Błąd", f"Błąd podczas zapisywania raportu: {e}")

    if __name__ == "__main__":
        root = tk.Tk()
        name, process_names = load_config()
        if name and process_names:
            app = TimerApp(root, name, process_names)
            root.mainloop()
