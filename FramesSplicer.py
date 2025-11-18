from tkinter import filedialog, Tk, Label
from tkinter.ttk import Progressbar
import os
import cv2

sep = '_'

def split_file_path(file_path):
    # Разделяем полный путь на каталог и полное имя файла
    directory = os.path.dirname(file_path)

    # Извлекаем имя файла вместе с расширением
    filename_with_extension = os.path.basename(file_path)

    # Разделяем имя файла и расширение
    name, extension = os.path.splitext(filename_with_extension)

    # Деление имени файла на две части перед символом подчеркивания (sep='_')
    name_parts = name.split(sep)
    if len(name_parts) < 2:
        print(f"Имя файла не содержит символ '{sep}'")
        return None
    if len(name_parts) == 2:
        main_part, number_part = name_parts
        postfix = ''
    else:
        main_part, number_part, postfix = name_parts
        print(f'Имя файла содержит постфикс {postfix}')

    return {
        'directory': directory,
        'filename': filename_with_extension,
        'extension': extension.lstrip('.'),
        'main_name': main_part,
        'number': number_part,
        'postfix': postfix
    }

def collect_and_sort_files(directory, base_name):
    """
    Функция собирает файлы в указанном каталоге, фильтрует по указанному базовому имени и порядку номеров.
    :param directory: Каталог, в котором искать файлы
    :param base_name: Базовая часть имени файла
    :return: Отсортированный список полных путей к файлам
    """
    files = []

    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if not os.path.isfile(full_path):
            continue

        name, ext = os.path.splitext(os.path.basename(file))

        # Проверяем, соответствует ли файл формату: "<базовое имя>_<номер>.<расширение>"
        parts = name.split('_')
        if len(parts) < 2 or parts[0] != base_name:
            continue

        try:
            # Вторая часть должна быть числом
            num = int(parts[1])
        except ValueError:
            continue

        # Добавляем файл в список с сохранением порядка сортировки
        files.append((num, full_path))

    # Сортируем файлы по численному значению второго элемента
    sorted_files = sorted(files, key=lambda x: x[0])

    # Возвращаем только пути к файлам
    return [path for _, path in sorted_files]

def create_video_from_images(root, progress_bar, image_paths, output_path, fps=30, frame_size=None):
    """
    Создаем видео из последовательности изображений.
    :param root: Объект окна Tkinter для обновления состояния
    :param image_paths: Список путей к изображениям
    :param output_path: Выходной путь для сохранения видео
    :param fps: Частота кадров в секунду
    :param frame_size: Размер кадра (width, height); если None, берется размер первого изображения
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек сжатия видео

    first_image = cv2.imread(image_paths[0])
    h, w, _ = first_image.shape

    # Устанавливаем размер кадра либо автоматически по первому изображению
    if frame_size is None:
        frame_size = (w, h)

    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    total_frames = len(image_paths)

    for i, img_path in enumerate(image_paths):
        img = cv2.imread(img_path)
        resized_img = cv2.resize(img, frame_size)
        out.write(resized_img)

        # Обновление прогресса
        progress_bar["value"] = ((i + 1) / total_frames) * 100
        root.update_idletasks()  # Перерисовка интерфейса

    out.release()


root = Tk()
root.title("FrameSplicer")
progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(padx = (10,10), pady=(10, 10))  # Показываем прогресс бар в окне
label_status = Label(root, text="Идет создание видео...")
label_status.pack(pady=(10, 10))

f_path = filedialog.askopenfilename(filetypes=[('Изображения',['*.jpg','*.png']),('Все файлы',['*.*'])])
if f_path:
    result = split_file_path(f_path)
    if result:

        open_dir = result['directory']
        b_name = result['main_name']
        p_name = result['postfix']
        frames_list = collect_and_sort_files(open_dir, b_name)
        #print(frames_list)

        # Создаем видео с частотой кадров 24 FPS
        fps = 24
        output_path = f"{open_dir}/{b_name}.mp4"
        create_video_from_images(root, progress_bar, frames_list, output_path, fps=fps)
        label_status.config(text="Видео успешно создано!")

    else:
        root.destroy()
root.mainloop()
