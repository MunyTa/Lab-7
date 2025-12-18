import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class DBUpdateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обновление записей в БД")
        self.root.geometry("500x400")

        # Подключение к БД
        self.conn = sqlite3.connect("employees.db")
        self.cursor = self.conn.cursor()

        # Создание таблицы (если не существует)
        self.create_table()

        # Заполняем тестовыми данными
        self.insert_test_data()

        # Создание GUI
        self.create_widgets()

    def create_table(self):
        """Создание таблицы employees"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                salary REAL
            )
        """)
        self.conn.commit()

    def insert_test_data(self):
        """Добавление тестовых данных"""
        test_data = [
            (1, 'Иван Петров', 'Разработчик', 100000),
            (2, 'Мария Сидорова', 'Дизайнер', 80000),
            (3, 'Алексей Иванов', 'Менеджер', 120000)
        ]

        for data in test_data:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO employees (id, name, position, salary) VALUES (?, ?, ?, ?)",
                    data
                )
            except:
                pass
        self.conn.commit()

    def create_widgets(self):
        """Создание элементов интерфейса"""

        # Фрейм для выбора записи
        select_frame = ttk.LabelFrame(self.root, text="Выберите запись для обновления", padding=10)
        select_frame.pack(pady=10, padx=10, fill=tk.X)

        # Выпадающий список с сотрудниками
        ttk.Label(select_frame, text="Сотрудник:").grid(row=0, column=0, sticky=tk.W)

        self.selected_id = tk.StringVar()
        self.employee_combo = ttk.Combobox(select_frame, textvariable=self.selected_id, state="readonly", width=40)
        self.employee_combo.grid(row=0, column=1, padx=5)
        self.employee_combo.bind("<<ComboboxSelected>>", self.load_employee_data)

        # Кнопка обновления списка
        ttk.Button(select_frame, text="Обновить список", command=self.load_employees).grid(row=0, column=2, padx=5)

        # Фрейм для редактирования данных
        edit_frame = ttk.LabelFrame(self.root, text="Редактирование данных", padding=15)
        edit_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Поля для ввода
        ttk.Label(edit_frame, text="ФИО:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(edit_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(edit_frame, text="Должность:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.position_entry = ttk.Entry(edit_frame, width=40)
        self.position_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(edit_frame, text="Зарплата:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.salary_entry = ttk.Entry(edit_frame, width=40)
        self.salary_entry.grid(row=2, column=1, pady=5, padx=5)

        # Кнопки
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Обновить запись", command=self.update_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Просмотреть все записи", command=self.view_all_records).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(button_frame, text="Очистить поля", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Загружаем список сотрудников при запуске
        self.load_employees()

    def load_employees(self):
        """Загрузка списка сотрудников в выпадающий список"""
        try:
            self.cursor.execute("SELECT id, name FROM employees ORDER BY name")
            employees = self.cursor.fetchall()

            if employees:
                # Форматируем для отображения: "ID. ФИО"
                employee_list = [f"{emp[0]}. {emp[1]}" for emp in employees]
                self.employee_combo['values'] = employee_list
                self.employee_combo.current(0)
                self.load_employee_data(None)
                self.status_bar.config(text=f"Загружено записей: {len(employees)}")
            else:
                self.employee_combo['values'] = []
                self.status_bar.config(text="Нет записей в базе данных")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def load_employee_data(self, event):
        """Загрузка данных выбранного сотрудника в поля формы"""
        try:
            selected = self.selected_id.get()
            if not selected:
                return

            # Извлекаем ID из строки вида "1. Иван Петров"
            emp_id = int(selected.split('.')[0])

            # Получаем данные сотрудника
            self.cursor.execute("SELECT name, position, salary FROM employees WHERE id = ?", (emp_id,))
            employee = self.cursor.fetchone()

            if employee:
                self.name_entry.delete(0, tk.END)
                self.position_entry.delete(0, tk.END)
                self.salary_entry.delete(0, tk.END)

                self.name_entry.insert(0, employee[0])
                self.position_entry.insert(0, employee[1])
                self.salary_entry.insert(0, str(employee[2]))

                self.status_bar.config(text=f"Загружена запись ID: {emp_id}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных сотрудника: {str(e)}")

    def update_record(self):
        """Обновление записи в БД"""
        try:
            # Проверяем, выбран ли сотрудник
            selected = self.selected_id.get()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите сотрудника для обновления")
                return

            # Извлекаем ID
            emp_id = int(selected.split('.')[0])

            # Получаем данные из полей
            name = self.name_entry.get().strip()
            position = self.position_entry.get().strip()

            # Проверяем зарплату
            try:
                salary = float(self.salary_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Зарплата должна быть числом")
                return

            # Проверяем заполнение обязательных полей
            if not name:
                messagebox.showerror("Ошибка", "Поле 'ФИО' обязательно для заполнения")
                return

            # Выполняем обновление
            self.cursor.execute(
                "UPDATE employees SET name = ?, position = ?, salary = ? WHERE id = ?",
                (name, position, salary, emp_id)
            )
            self.conn.commit()

            # Обновляем список сотрудников
            self.load_employees()

            messagebox.showinfo("Успех", f"Запись ID:{emp_id} успешно обновлена!")
            self.status_bar.config(text=f"Запись ID:{emp_id} обновлена")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления: {str(e)}")

    def view_all_records(self):
        """Просмотр всех записей в отдельном окне"""
        try:
            self.cursor.execute("SELECT * FROM employees ORDER BY id")
            records = self.cursor.fetchall()

            if not records:
                messagebox.showinfo("Информация", "Нет записей в базе данных")
                return

            # Создаем новое окно
            view_window = tk.Toplevel(self.root)
            view_window.title("Все записи в БД")
            view_window.geometry("600x300")

            # Создаем Treeview (таблицу)
            tree = ttk.Treeview(view_window, columns=("ID", "ФИО", "Должность", "Зарплата"), show="headings")

            # Настраиваем заголовки
            tree.heading("ID", text="ID")
            tree.heading("ФИО", text="ФИО")
            tree.heading("Должность", text="Должность")
            tree.heading("Зарплата", text="Зарплата")

            tree.column("ID", width=50)
            tree.column("ФИО", width=200)
            tree.column("Должность", width=150)
            tree.column("Зарплата", width=100)

            # Добавляем данные
            for record in records:
                tree.insert("", tk.END, values=record)

            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Статус
            ttk.Label(view_window, text=f"Всего записей: {len(records)}").pack(pady=5)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка просмотра записей: {str(e)}")

    def clear_fields(self):
        """Очистка полей ввода"""
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)
        self.status_bar.config(text="Поля очищены")

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = DBUpdateApp(root)

    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()