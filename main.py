import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import logging
import os
import csv

# Konfiguracja logowania
log_file = os.path.join(os.path.expanduser("~"), "multi_timer_log.txt")
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Ustawienie daty wygaśnięcia na 31 sierpnia 2024
expiry = datetime(2024, 8, 13)

# Funkcja sprawdzająca datę wygaśnięcia
def is_trial_expired():
    current_date = datetime.now()
    if current_date > expiry:
        return True  # Zwróć True, jeśli wersja próbna wygasła
    else:
        return False  # Zwróć False, jeśli wersja próbna jest nadal aktywna

# Przykład użycia funkcji
if is_trial_expired():
    print("Wersja próbna wygasła")
    messagebox.showerror("Błąd", "Wersja próbna wygasła")
else:
    class TimerApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Multi Timer App")
            self.process_names = set()  # Zbiór przechowujący unikalne nazwy procesów

            self.name_frame = tk.Frame(root)
            self.name_frame.pack(padx=10, pady=5)

            tk.Label(self.name_frame, text="Imię:").grid(row=0, column=0)
            self.first_name_entry = tk.Entry(self.name_frame)
            self.first_name_entry.grid(row=0, column=1)

            tk.Label(self.name_frame, text="Nazwisko:").grid(row=1, column=0)
            self.last_name_entry = tk.Entry(self.name_frame)
            self.last_name_entry.grid(row=1, column=1)

            self.timers_frame = tk.Frame(root)
            self.timers_frame.pack(padx=10, pady=5)

            self.timers = []
            for i in range(8):
                self.create_timer(i)

            self.report_button = tk.Button(root, text="Generuj Raport", command=self.generate_report)
            self.report_button.pack(pady=10)

        def create_timer(self, index):
            frame = tk.Frame(self.timers_frame)
            frame.pack(padx=10, pady=5)

            process_entry = tk.Entry(frame)
            process_entry.insert(0, f"Proces {index+1}")
            process_entry.grid(row=0, column=0, padx=5)

            time_label = tk.Label(frame, text="0:00:00", font=("Helvetica", 24))
            time_label.grid(row=0, column=1, columnspan=4)

            start_button = tk.Button(frame, text="Start", command=lambda idx=index: self.start_timer(idx))
            start_button.grid(row=1, column=0)

            stop_button = tk.Button(frame, text="Stop", command=lambda idx=index: self.stop_timer(idx))
            stop_button.grid(row=1, column=1)

            reset_button = tk.Button(frame, text="Reset", command=lambda idx=index: self.reset_timer(idx))
            reset_button.grid(row=1, column=2)

            timer = {
                'frame': frame,
                'process_entry': process_entry,
                'time_label': time_label,
                'start_button': start_button,
                'stop_button': stop_button,
                'reset_button': reset_button,
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

        def reset_timer(self, index):
            timer = self.timers[index]
            if timer['running']:
                self.root.after_cancel(timer['after_id'])
                timer['running'] = False
            timer['elapsed_time'] = timedelta()
            timer['time_label'].config(text="0:00:00")
            self.set_timer_color(index, "white")  # Przywrócenie koloru czcionki dla resetowanego timera

        def set_active_timer_color(self, index, color):
            timer = self.timers[index]
            timer['process_entry'].config(fg=color)  # Zmiana koloru czcionki nazwy procesu
            timer['time_label'].config(fg=color)  # Zmiana koloru czcionki czasu timera

        def set_timer_color(self, index, color):
            timer = self.timers[index]
            timer['process_entry'].config(fg=color)  # Zmiana koloru czcionki nazwy procesu
            timer['time_label'].config(fg=color)  # Zmiana koloru czcionki czasu timera

        def generate_report(self):
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()

            if not first_name or not last_name:
                messagebox.showerror("Błąd", "Proszę wprowadzić imię i nazwisko.")
                return

            report_lines = [["Imię i nazwisko", f"{first_name} {last_name}"]]
            process_names_set = set()  # Zbiór pomocniczy do sprawdzania unikalności nazw procesów

            for i, timer in enumerate(self.timers):
                process_name = timer['process_entry'].get().strip()  # Pobieramy nazwę i usuwamy białe znaki z końców
                if not process_name:
                    continue  # Pomijamy puste nazwy procesów
                if process_name in process_names_set:
                    messagebox.showerror("Błąd", f"Nie można użyć dwóch takich samych nazw procesów: {process_name}.")
                    return
                process_names_set.add(process_name)
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
                return

            messagebox.showinfo("Raport", f"Raport został zapisany jako '{report_file_name}' w katalogu domowym użytkownika.")

    if __name__ == "__main__":
        root = tk.Tk()
        app = TimerApp(root)
        root.mainloop()

        

