import tkinter as tk
from datetime import datetime, timedelta

class TimerApp:
    # __init__ jest specjalna metoda w pythonie ktora dziala jako konstruktor klasy, jest automatycznie wywolywana,
    # gdy tworzymy nowa instajce klasy. Sluzy do inicjalizacji atrybutow klasy
    # w metodzie init wszystkie atrybuty i widzety przypisujemy do self, aby mogly byc dostepne we wszystkich metodach klasy
    def __init__(self, root):

    # self jest konwencją w Pythonie, która odnosi się do bieżącej instancji klasy. Używając self, możemy definiować i
    # uzyskiwać dostęp do atrybutów i metod związanych z tą instancją.
        self.root = root
        self.root.title("Timer")

        self.create_name_fields() #dodanie pól na imię i nazwisko

        self.timers = []
        for i in range(8):
            self.create_timer(i)

    def create_name_fields(self):
        name_frame = tk.Frame(self.root)
        name_frame.pack(padx=10, pady=5)

        # name_label = tk.Label(name_frame, text="Imię i nazwisko:")
        # name_label.grid(row=0, column=0, padx=5)

        self.name_entry = tk.Entry(name_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5)
        self.name_entry.insert(0, "Imię Nazwisko")  # Placeholder

    def create_timer(self, index):
        frame = tk.Frame(self.root) #tworzy ramke frame dla kazdego stopera
        frame.pack(padx=10, pady=5) #metoda pack umieszcza ramke w oknie glownym

        # process_label = tk.Label(frame, text=f"Proces {index+1}:")
        # process_label.pack(side="left")

        process_entry = tk.Entry(frame, width=15)
        process_entry.pack(side="left")
        process_entry.insert(0, f"Proces {index+1}")  # Placeholder
        time_label = tk.Label(frame, text="0:00:00", font=("Helvetica", 36))
        time_label.pack()

        #lamba tworzy anonimowa funkcje, ktora wywoluje self.start_timer(index), bez niej nie mozna przekac index i natychmiast wywolac. Uzytkownika naciska button start, Tkinter wywoluje funkcje lambda przypisana do funkcji command, a ta anonimowa funkcja wywoluje self.start_timer z przekazanym argumentem index, lambda pozwala na dynamiczne przekazywanie argumentow do funkcji ktore maja byc wywolane po nacisnieciu przycisku. Bez lambdy funkja zostalaby wywolana natychmiast po utworzeniu przycisku i zwrocilaby None, lambda zawiera przepis na funkcja bez jej wywolania, sama definicja nie powoduje natychmiastowego wywolania, ale sprytne choc zawile :D bez lambdy przycisk na command ma wywolac funkcje, a tak ma tylko jej wynik wiec nic nie wywola xD labda pozwala na przekazanie przepisu, ktory mozna wywolac
        # bez lambdy i tak trzebaby stworzyc funkcje pomocnicza tworzaca funkcje i zwracajaca jej definicje z indeksem i dopiero to przekazac do command :D
        start_button = tk.Button(frame, text="Start", command=lambda: self.start_timer(index) )
        start_button.pack(side="left")

        stop_button = tk.Button(frame, text="Stop", command=lambda: self.stop_timer(index) )
        stop_button.pack(side="left")

        reset_button = tk.Button(frame, text="Reset", command=lambda: self.reset_timer(index) )
        reset_button.pack(side="left")

        #przechowywanie informacji o stoperze
        timer = {
            'time_label': time_label,
            'running': False,
            'start_time': None,
            'elapsed_time': timedelta(),
            'after_id': None
        }

        self.timers.append(timer)
        # print(self.timers)

        # self.running = False
        # self.start_time = None
        # self.elapsed_time = timedelta()
    
    def update_time(self, index):
        timer = self.timers[index]
        if timer['running']:
            timer['elapsed_time'] = datetime.now() - timer['start_time']
            # timer['elapsed_time'] oblicza czas, ktory uplynal od startu do teraz
            # nastepnie str() zwraca string np '1days, 02:30:15.123456' DD,HH:MM:SS.ssssss
            # dzieki split(".") pozbywamy sie mikrosekund, a ponizszy zapis ignoruje dni :D dlatego zostanie
            # ['1days, 02:30:15', '12345'] a ze nie ma dni i bierzemy pierwszy wyraz [0] to zostaje '02:30:15'
            # config ustawia tekst etykiety timer['timer_label]
            # generalnie config pozwala na modyfikowanie dynamiczne atrybutow widzeta takich jak tekst, kolor, czcionka itp.
            # zeby nie wyswietlac dni potrzebna bylaby dodatkowa logika
            timer['time_label'].config(text=str(timer['elapsed_time']).split(".")[0])
            #metoda after  z tkinter sluzy do zaplanowania wywolania funkcji po okreslonym czasie w postaci
            #root.after(ms, func, *args) zwraca identyfikator (ID) zaplanowanego zadania, ktory jest pozniej uzywany do anulowania zadania
            # ponizej aktualizauje czas po jednej sekundzie
            timer['after_id'] = self.root.after(1000, self.update_time, index)
            # print(self.timers)


    def start_timer(self, index):
        #enumerate sluzy do iteracji po liscie timerow, zwraca timer i jego indeks. Tworzy iterator, ktory interuje przez liste self.timers zwraajac indeks i oraz timer dla kazdego elementu. W petli for sprawdza czy dany timer nie jest wybranym timerem i czy nie jest aktualnie uruchomionym, jesli tak jest to zatrzymuje dany timer
        for i, timer in enumerate(self.timers):
            if i != index and timer['running']:
                self.stop_timer(i)
        timer = self.timers[index]
        if not timer['running']:
            timer['start_time'] = datetime.now() - timer['elapsed_time']
            timer['running'] = True
            self.update_time(index)

    def stop_timer(self, index):
        timer = self.timers[index]
        if timer['running']:
            #after_cancel anuluje zaplanowane zadanie korzystajac z identyfikatora zwroconego przez after
            self.root.after_cancel(timer['after_id'])
            timer['running'] = False

    def reset_timer(self, index):
        timer = self.timers[index]
        if timer['running']:
            #tutaj tez anuluje zaplanowane wywolanie update_time
            self.root.after_cancel(timer['after_id'])
            timer['running'] = False
        timer['elapsed_time'] = timedelta()
        timer['time_label'].config(text="00:00:00")

if __name__ == "__main__":
    root = tk.Tk() 
#Argument root w aplikacji Tkinter jest niezbędny do utworzenia głównego okna aplikacji. 
#Jest to podstawowy kontener dla wszystkich widżetów, takich jak etykiety, przyciski, itp.
    app = TimerApp(root)
#Tworzenie instancji TimerApp z root jako argumentem pozwala na przypisanie tego głównego okna do naszej aplikacji 
#i zarządzanie nim w kontekście klasy TimerApp.
    root.mainloop() 
#powoduje, ze aplikacja działa i czeka na interakcje uzytkownika
