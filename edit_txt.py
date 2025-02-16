import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import keyword
import os
from tkinter import font
import configparser  # Импортируем модуль configparser

class TextEditor:
    def __init__(self, master):
        self.master = master
        master.title("Простой текстовый редактор с сохранением настроек")

        # Настройки по умолчанию (если файл настроек не найден)
        self.default_font_family = "Courier New"
        self.default_font_size = 12
        self.default_font = font.Font(family=self.default_font_family, size=self.default_font_size)

        self.text_area = tk.Text(master, wrap=tk.WORD, undo=True, font=self.default_font)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<Tab>", self.indent)

        # Меню
        self.menu_bar = tk.Menu(master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Новый", command=self.new_file)
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить", command=self.save_file)
        self.file_menu.add_command(label="Сохранить как...", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=self.exit_editor)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Найти", command=self.find_text)
        self.edit_menu.add_command(label="Заменить", command=self.replace_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Отменить", command=self.undo)
        self.edit_menu.add_command(label="Повторить", command=self.redo)

        self.format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.format_menu.add_command(label="Шрифт...", command=self.change_font)

        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Правка", menu=self.edit_menu)
        self.menu_bar.add_cascade(label="Формат", menu=self.format_menu)

        master.config(menu=self.menu_bar)

        # Статус-бар
        self.status_bar = tk.Label(master, text="Строка: 1, Символов: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Настройка тегов для подсветки синтаксиса
        self.text_area.tag_config("keyword", foreground="orange")
        self.text_area.tag_config("string", foreground="green")
        self.text_area.tag_config("comment", foreground="gray")

        self.keywords = keyword.kwlist

        self.current_file = None
        self.highlight_syntax()
        self.update_status_bar()

        # Автосохранение
        self.autosave_interval = 60000
        self.autosave()

        # Настройки
        self.config_file = "editor_config.ini"  # Имя файла конфигурации
        self.load_settings() # Загружаем настройки при запуске

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.master.title("Простой текстовый редактор с сохранением настроек")
        self.highlight_syntax()
        self.update_status_bar()

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".py",
                                             filetypes=[("Python файлы", "*.py"),
                                                        ("Текстовые файлы", "*.txt"),
                                                        ("Все файлы", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, text)
                    self.current_file = file_path
                    self.master.title(f"{os.path.basename(file_path)} - Простой текстовый редактор")
                    self.highlight_syntax()
                    self.update_status_bar()
            except FileNotFoundError:
                messagebox.showerror("Ошибка", "Файл не найден.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def save_file(self):
        if self.current_file:
            try:
                text = self.text_area.get(1.0, tk.END)
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(text)
                self.highlight_syntax()
                self.update_status_bar()
                self.master.title(f"{os.path.basename(self.current_file)} - Простой текстовый редактор")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                filetypes=[("Python файлы", "*.py"),
                                                           ("Текстовые файлы", "*.txt"),
                                                           ("Все файлы", "*.*")])
        if file_path:
            try:
                text = self.text_area.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text)
                self.current_file = file_path
                self.master.title(f"{os.path.basename(file_path)} - Простой текстовый редактор")
                self.highlight_syntax()
                self.update_status_bar()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def exit_editor(self):
        self.save_settings() # Сохраняем настройки перед выходом
        self.master.destroy()

    def update_status_bar(self, event=None):
        text = self.text_area.get(1.0, tk.END)
        line_count = text.count('\n') + 1
        char_count = len(text) - 1 if text else 0
        self.status_bar.config(text=f"Строка: {line_count}, Символов: {char_count}")

    def find_text(self):
        """Открывает диалоговое окно для поиска текста."""
        search_dialog = tk.Toplevel(self.master)
        search_dialog.title("Найти")

        tk.Label(search_dialog, text="Что искать:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        search_entry = tk.Entry(search_dialog, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.focus_set()

        def perform_search():
            """Выполняет поиск текста."""
            try:
                text_to_find = search_entry.get()
                if not text_to_find:
                    return

                start_index = "1.0"
                self.text_area.tag_remove("found", "1.0", tk.END)

                while True:
                    start_index = self.text_area.search(text_to_find, start_index, stopindex=tk.END)
                    if not start_index:
                        break

                    end_index = f"{start_index}+{len(text_to_find)}c"
                    self.text_area.tag_add("found", start_index, end_index)
                    start_index = end_index

                self.text_area.tag_config("found", background="yellow")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при поиске: {e}")

        tk.Button(search_dialog, text="Найти", command=perform_search).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def replace_text(self):
        """Открывает диалоговое окно для замены текста."""
        replace_dialog = tk.Toplevel(self.master)
        replace_dialog.title("Заменить")

        tk.Label(replace_dialog, text="Что искать:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        search_entry = tk.Entry(replace_dialog, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(replace_dialog, text="На что заменить:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        replace_entry = tk.Entry(replace_dialog, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        def perform_replace():
            """Выполняет замену текста."""
            try:
                text_to_find = search_entry.get()
                text_to_replace = replace_entry.get()

                if not text_to_find:
                    return

                start_index = "1.0"
                self.text_area.tag_remove("found", "1.0", tk.END)

                while True:
                    start_index = self.text_area.search(text_to_find, start_index, stopindex=tk.END)
                    if not start_index:
                        break

                    end_index = f"{start_index}+{len(text_to_find)}c"
                    self.text_area.delete(start_index, end_index)
                    self.text_area.insert(start_index, text_to_replace)

                    # Сдвигаем start_index на длину вставленного текста
                    start_index = f"{start_index}+{len(text_to_replace)}c"


            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при замене: {e}")


        tk.Button(replace_dialog, text="Заменить все", command=perform_replace).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def highlight_syntax(self, event=None):
        """Выполняет подсветку синтаксиса Python."""
        try:
            # Удаляем все предыдущие теги
            self.text_area.tag_remove("keyword", "1.0", tk.END)
            self.text_area.tag_remove("string", "1.0", tk.END)
            self.text_area.tag_remove("comment", "1.0", tk.END)

            text = self.text_area.get("1.0", tk.END)

            # Подсветка ключевых слов
            for keyword_word in self.keywords:
                start_index = "1.0"
                while True:
                    start_index = self.text_area.search(r'\m' + keyword_word + r'\M', start_index, stopindex=tk.END, regexp=True) # \m и \M для поиска целых слов
                    if not start_index:
                        break
                    end_index = f"{start_index}+{len(keyword_word)}c"
                    self.text_area.tag_add("keyword", start_index, end_index)
                    start_index = end_index

            # Подсветка строк (одинарные и двойные кавычки)
            start_index = "1.0"
            while True:
                start_index = self.text_area.search(r'("([^"]*)")|(\'([^\']*)\')', start_index, stopindex=tk.END, regexp=True)
                if not start_index:
                    break
                end_index = f"{start_index}+1c"  # Move past the quote
                string_start = start_index
                quote_char = self.text_area.get(string_start, end_index)
                string_end = self.text_area.search(quote_char, end_index, stopindex=tk.END, regexp=False)

                if not string_end: # Invalid syntax
                    break

                string_end = f"{string_end}+1c"
                self.text_area.tag_add("string", string_start, string_end)
                start_index = string_end


            # Подсветка комментариев
            start_index = "1.0"
            while True:
                start_index = self.text_area.search(r"#.*", start_index, stopindex=tk.END, regexp=True)
                if not start_index:
                    break
                end_index = f"{start_index} lineend"
                self.text_area.tag_add("comment", start_index, end_index)
                start_index = end_index


        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при подсветке синтаксиса: {e}")

    def indent(self, event):
        """Вставляет 4 пробела вместо символа табуляции."""
        self.text_area.insert(tk.INSERT, "    ")
        return 'break' # Предотвращаем стандартное поведение Tab

    def autosave(self):
        """Автоматически сохраняет файл."""
        if self.current_file:
            try:
                text = self.text_area.get(1.0, tk.END)
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(text)
            except Exception as e:
                print(f"Ошибка при автосохранении: {e}")

        self.master.after(self.autosave_interval, self.autosave)

    def change_font(self):
        """Открывает диалоговое окно для выбора шрифта."""
        font_dialog = tk.Toplevel(self.master)
        font_dialog.title("Выбор шрифта")

        # Список шрифтов
        font_list = sorted(font.families())
        font_variable = tk.StringVar(value=self.default_font.actual()["family"]) # Текущий шрифт
        font_listbox = tk.Listbox(font_dialog, listvariable=tk.Variable(value=font_list), height=10) # Выводим только 10 шрифтов
        font_listbox.pack(padx=10, pady=10)
        font_listbox.select_set(font_list.index(self.default_font.actual()["family"])) # Выделяем текущий шрифт

        # Список размеров шрифта
        size_list = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        size_variable = tk.IntVar(value=self.default_font.actual()["size"])
        size_listbox = tk.Listbox(font_dialog, listvariable=tk.Variable(value=size_list), height=10)
        size_listbox.pack(padx=10, pady=10)
        size_listbox.select_set(size_list.index(self.default_font.actual()["size"]))

        def apply_font():
            """Применяет выбранный шрифт."""
            try:
                selected_font = font_listbox.get(font_listbox.curselection())
                selected_size = size_listbox.get(size_listbox.curselection())
                new_font = font.Font(family=selected_font, size=selected_size)

                self.text_area.config(font=new_font)
                self.default_font = new_font # Обновляем шрифт по умолчанию
                self.highlight_syntax() # Обновляем подсветку, чтобы она корректно отображалась
                self.save_settings()  # Сохраняем настройки шрифта
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить шрифт: {e}")

        # Кнопки
        apply_button = tk.Button(font_dialog, text="Применить", command=apply_font)
        apply_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = tk.Button(font_dialog, text="Отмена", command=font_dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Захват фокуса
        font_dialog.focus_set()

    def undo(self):
        """Отменяет последнее действие."""
        try:
            self.text_area.edit_undo()
            self.highlight_syntax()  # Обновляем подсветку
        except Exception as e:
            messagebox.showerror("Ошибка", f"Нечего отменять: {e}")

    def redo(self):
        """Повторяет последнее отмененное действие."""
        try:
            self.text_area.edit_redo()
            self.highlight_syntax()  # Обновляем подсветку
        except Exception as e:
            messagebox.showerror("Ошибка", f"Нечего повторять: {e}")

    def load_settings(self):
        """Загружает настройки из файла."""
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file)
            font_family = config.get("Font", "family", fallback=self.default_font_family)  # Используем fallback для значений по умолчанию
            font_size = config.getint("Font", "size", fallback=self.default_font_size)
            self.default_font = font.Font(family=font_family, size=font_size)
            self.text_area.config(font=self.default_font)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            print("Не удалось загрузить настройки. Используются настройки по умолчанию.")
            self.save_settings()  # Если что-то пошло не так, сохраняем текущие настройки (которые являются настройками по умолчанию)

    def save_settings(self):
        """Сохраняет настройки в файл."""
        config = configparser.ConfigParser()
        config.add_section("Font")
        config.set("Font", "family", self.default_font.actual()["family"])
        config.set("Font", "size", str(self.default_font.actual()["size"]))  # Преобразуем int в строку
        try:
            with open(self.config_file, "w") as configfile:
                config.write(configfile)
            #print("Настройки сохранены.") # Для отладки
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()

#version 0.1