import cv2
import os
from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog

bt_open = "\u23CF"  # Подпись кнопки открыть файл
bt_play = "\u23F5"  # Подпись кнопки Play
bt_pause = "\u23F8" # Подпись кнопки Пауза
bt_stop = "\u23F9"  # Подпись кнопки Стоп
bt_save = "\uF4BE"  # Подпись кнопки Сохранить кадр
separator = "_"     # Разделитель имени файла и номера кадра
y_pad = 10
buttons_height = 28
buttons_width = 600

class VideoPlayer:
    def __init__(self):
        self.root = Tk()
        self.root.title("FineFrameController v.1.3")

        # Основная канва для показа текущего кадра
        self.canvas = Canvas(self.root)
        self.canvas.pack(fill=BOTH, expand=True)

        # Панель инструментов
        toolbar = Frame(self.root)
        toolbar.pack(pady=y_pad)

        # Кнопки управления
        Button(toolbar, text=bt_open, command=self.open_video, padx=5).pack(side=LEFT, padx=10)

        # Кнопка Play/Pause объединённая
        self.play_pause_button = Button(toolbar, text=bt_play, command=self.play, padx=10)
        self.play_pause_button.pack(side=LEFT, padx=(30, 10))

        # Кнопка сохранения кадра
        self.save_button = Button(toolbar, text=bt_save, command=self.save, padx=5)
        self.save_button.pack(side=LEFT, padx=(0, 10))

        # Кнопки управления покадровым воспроизведением
        self.prev_button = Button(toolbar, text='-', command=self.prev, padx=4)
        self.prev_button.pack(side=LEFT)
        self.stop_button = Button(toolbar, text=bt_stop, command=self.stop, padx=2)
        self.stop_button.pack(side=LEFT)
        self.next_button = Button(toolbar, text='+', command=self.next, padx=2)
        self.next_button.pack(side=LEFT)

        # Показываем позицию текущего кадра
        Label(toolbar, text="Кадр №:").pack(side=LEFT, padx=10)
        self.current_frame_entry = Entry(toolbar, width=5, justify="right")
        self.current_frame_entry.insert(END, " ")  # Значение по умолчанию
        self.current_frame_entry.pack(side=LEFT)

        # Показываем позицию текущего кадра
        Label(toolbar, text=" из").pack(side=LEFT)
        self.total_frames_var = StringVar(value=' ')
        self.total_frames_label = Label(toolbar, textvariable=self.total_frames_var)
        self.total_frames_label.pack(side=LEFT)

        # Управление частотой кадров
        Label(toolbar, text="Задержка кадров (мс):").pack(side=LEFT,padx=(30,0))
        self.delay_entry = Entry(toolbar, width=5, justify="right")
        self.delay_entry.insert(END, "15")  # Значение по умолчанию
        self.delay_entry.pack(side=LEFT, padx=(0,10))

        # Статус воспроизведения
        self.is_playing = False
        self.video_path = None
        self.cap = None
        self.frame_width = None
        self.frame_height = None
        self.total_frames = 0
        self.current_frame = 0

        # Переменная для хранения кадра
        self.saved_frame = []

        # Привязка горячих клавиш
        self.root.bind("<Control-o>", lambda event: self.open_video())      # Ctrl + O — открыть видео
        self.root.bind("<space>", lambda event: self.play())                # Пробел — воспроизведение/пауза
        self.root.bind("<w>", lambda event: self.save())                    # w — сохранить кадр
        self.root.bind("<s>", lambda event: self.stop())                    # s — воспроизведение/пауза
        self.root.bind("<Left>", lambda event: self.prev())                 # ← — предыдущий кадр
        self.root.bind("<Right>", lambda event: self.next())                # → — следующий кадр
        self.root.bind("<a>", lambda event: self.prev())                    # a — предыдущий кадр
        self.root.bind("<d>", lambda event: self.next())                    # d — следующий кадр

    def prepare_frame(self):
        # Читаем кадр
        ret, frame = self.cap.read()

        # Сохраняем кадр
        self.saved_frame.clear()
        self.saved_frame.append(frame)

        if ret:
            self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            self.current_frame_entry.delete(0, END)
            self.current_frame_entry.insert(END, str(self.current_frame))
            resized_frame = self.resize_frame(frame)
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.canvas.create_image(0, 0, anchor=NW, image=photo)
            self.canvas.image = photo

    def open_video(self):
        self.is_playing = False
        self.play_pause_button.config(text=bt_play)
        """ Открывает диалог выбора файла """
        file_path = filedialog.askopenfilename(filetypes=[('Все видео файлы',['*.mp4','*.avi']),('MPEG', '*.mp4'), ('AVI', '*.avi')])
        if file_path:
            self.video_path = file_path
            self.cap = cv2.VideoCapture(file_path)
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # Устанавливаем размер окна
            self.set_window_size(width, height)

            # Готовим кадр
            self.prepare_frame()

            # Определяем стартовую частоту кадров (FPS) и количество из метаданных видео
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.total_frames_var.set(str(self.total_frames))
            initial_delay = int(1000 / fps)  # Преобразование FPS в мс
            self.delay_entry.delete(0, END)
            self.delay_entry.insert(END, str(initial_delay))  # Устанавливаем начальное значение задержки

    # Метод для изменения зазмера окна приложения
    def set_window_size(self, width, height):
        # Определяем размеры экрана
        screen_width = self.root.winfo_screenwidth() * 0.9
        screen_height = self.root.winfo_screenheight() * 0.9 - (2*y_pad+buttons_height)
        # Вычисляем необходимый размер уменьшения кадра
        scale_factor = min(1, screen_width/width, screen_height/height)
        max_width = int(width * scale_factor)
        max_height = int(height * scale_factor)
        print(screen_width/width, screen_height/width)
        print(width, screen_height/width)
        print(screen_width, screen_height)
        print(max_width,max_height)

        if max_width < buttons_width and scale_factor == 1:
            zoom_factor = min(buttons_width/width, screen_height/height)
            max_width = int(max_width * zoom_factor)
            max_height = int(max_height * zoom_factor)

        # Принудительно увеличиваем ширину до размера интерфейса по необходимости и конфигурируем отступы
        if max_width < buttons_width:
            pad_x = (buttons_width - max_width)//2
            self.canvas.pack_configure(padx=pad_x)
            max_width = buttons_width
        else:
            self.canvas.pack_configure(padx=0)

        self.root.geometry(f"{max_width}x{max_height+2*y_pad+buttons_height}")  # Устанавливаем размер окна и положение
        self.frame_width = max_width
        self.frame_height = max_height

    def play(self):
        if not self.is_playing and self.video_path:
            self.is_playing = True
            self.play_pause_button.config(text=bt_pause)
            self.jump_to_frame()
            self.update_frame()
        else:
            self.is_playing = False
            self.play_pause_button.config(text=bt_play)

    def stop(self):
        self.is_playing = False
        self.play_pause_button.config(text=bt_play)
        self.jump_to_frame()

    def prev(self):
        self.is_playing = False
        self.play_pause_button.config(text=bt_play)
        current_frame = ''.join(i for i in self.current_frame_entry.get().strip() if i.isdigit()) # Оставляем только цифры
        try:
            frame_num = int(current_frame)  # Получаем значение номера кадра из поля ввода
            if frame_num <= 0:
                frame_num = 1
        except ValueError:
            frame_num = 1
        if frame_num > 0:
            frame_num -= 1
        self.current_frame_entry.delete(0, END)
        self.current_frame_entry.insert(END, str(frame_num))
        self.jump_to_frame()

    def save(self):
        self.stop()
        if len(self.saved_frame) > 0:
            dir_name, f_name = os.path.split(self.video_path)
            save_path = os.path.join(dir_name, f_name[:f_name.rfind('.')]+separator+str(self.current_frame)+'.png')

            try:
                # Преобразование массива NumPy (OpenCV читает в таком формате) в объект Image
                Image.fromarray(cv2.cvtColor(self.saved_frame[0], cv2.COLOR_BGR2RGB)).save(save_path, format="PNG", compress_level=0)
            except OSError as err:
                print(f"Ошибка при сохранении изображения: {err}")

        self.next()

    def next(self):
        self.is_playing = False
        self.play_pause_button.config(text=bt_play)
        # Готовим следующий кадр
        self.prepare_frame()

    def jump_to_frame(self):
        """ Переходим на заданный кадр """
        target_frame_number = ''.join(i for i in self.current_frame_entry.get().strip() if i.isdigit()) # Оставляем только цифры
        if target_frame_number and self.cap is not None:
            target_frame_number = int(target_frame_number)
            if 0 <= target_frame_number < self.total_frames:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_number)
                # Готовим адр
                self.prepare_frame()


    def resize_frame(self, frame):
        h, w = frame.shape[:2]
        scale_factor = min(self.frame_width / w, self.frame_height / h)
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        return cv2.resize(frame, (new_w, new_h))

    def update_frame(self):
        delay = ''.join(i for i in self.delay_entry.get().strip() if i.isdigit()) # Оставляем только цифры
        try:
            delay_ms = int(delay)  # Получаем значение задержки из поля ввода
            if delay_ms <= 0:
                delay_ms = 1
        except ValueError:
            delay_ms = 1
        if self.is_playing and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))-1
                self.current_frame_entry.delete(0,END)
                self.current_frame_entry.insert(END, str(self.current_frame))
                resized_frame = self.resize_frame(frame)
                frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
                self.canvas.create_image(0, 0, anchor='NW',  image=img)
                self.canvas.image = img
            else:
                self.play_pause_button.config(text=bt_play)

            self.root.after(delay_ms, self.update_frame)  # Установили задержку согласно значению из поля ввода

    def run(self):
        self.root.mainloop()


# Запускаем приложение
player = VideoPlayer()
player.run()