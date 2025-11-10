import os.path
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import ImageTk, Image
import shutil


class PixelDifferenceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PPC")
        #self.geometry("200x100")

        # Создаем элементы интерфейса
        frame = tk.Frame(self)
        frame.pack(pady=0)

        load_button_1 = tk.Button(frame, text="Загрузить первое изображение", command=self.load_first_image)
        load_button_1.grid(row=0, column=0, padx=3, pady=2)

        load_button_2 = tk.Button(frame, text="Загрузить второе изображение", command=self.load_second_image)
        load_button_2.grid(row=1, column=0, padx=3, pady=2)

        compare_button = tk.Button(frame, text="Сравнить изображения", command=self.compare_images)
        compare_button.grid(row=3, column=0, padx=3, pady=2)

        # Переменные для хранения изображений
        self.image1 = None
        self.image2 = None
        self.result_label = []

    def load_image(self):
        filename = filedialog.askopenfilename(filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")))
        if not filename:
            return
        _, ext = os.path.splitext(filename)
        tmp_name = 'tmp'+ ext
        print(tmp_name)
        shutil.copyfile(filename, tmp_name)
        image = cv2.imread(tmp_name)
        os.remove(tmp_name)
        return image

    def load_first_image(self):
        self.image1 = self.load_image()
        self.show_image(self.image1, "Первое изображение")

    def load_second_image(self):
        self.image2 = self.load_image()
        self.show_image(self.image2, "Второе изображение")

    def show_image(self, img, title):
        # Показываем выбранное изображение в отдельном окне
        window = tk.Toplevel(self)
        window.title(title)
        photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
        label = tk.Label(window, image=photo)
        label.image = photo
        label.pack()

    def compare_images(self):
        if self.image1 is None or self.image2 is None:
            messagebox.showwarning("Предупреждение", "Необходимо загрузить оба изображения.")
            return

        h1, w1 = self.image1.shape[:2]
        h2, w2 = self.image2.shape[:2]

        # Приведение размеров изображений к одному значению
        if h1 != h2 or w1 != w2:
            min_h = min(h1, h2)
            min_w = min(w1, w2)
            self.image1 = cv2.resize(self.image1, (min_w, min_h))
            self.image2 = cv2.resize(self.image2, (min_w, min_h))

        # Модуль разности RGB-каналов
        diff = abs(np.float32(self.image1) - np.float32(self.image2)).astype(np.uint8)

        # Разделение на отдельные окна для каждого канала
        b_diff, g_diff, r_diff = cv2.split(diff)

        # Отображаем разницу по каждому каналу отдельно
        for i, channel in enumerate([b_diff, g_diff, r_diff]):
            window = tk.Toplevel(self)
            window.title(f"Разница ({['Blue', 'Green', 'Red'][i]} канал)")
            photo = ImageTk.PhotoImage(Image.fromarray(channel))
            label = tk.Label(window, image=photo)
            label.image = photo
            label.pack()
            self.result_label.append(label)


if __name__ == "__main__":
    app = PixelDifferenceApp()
    app.mainloop()