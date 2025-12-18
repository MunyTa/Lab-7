import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class SimpleJoinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JOIN Запросы - Упрощенная версия")
        self.root.geometry("800x500")

        # Подключение к БД
        self.conn = sqlite3.connect(":memory:")  # В памяти для простоты
        self.cursor = self.conn.cursor()

        # Создаем простые таблицы
        self.create_simple_tables()

        # GUI
        self.create_gui()

    def create_simple_tables(self):
        """Создаем две простые таблицы для демонстрации JOIN"""
        # Таблица пользователей
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                department_id INTEGER
            )
        """)

        # Таблица отделов
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                dept_id INTEGER PRIMARY KEY,
                dept_name TEXT NOT NULL
            )
        """)

        # Вставляем тестовые данные
        departments = [
            (1, 'Разработка'),
            (2, 'Маркетинг'),
            (3, 'Продажи')
        ]
        self.cursor.executemany("INSERT INTO departments VALUES (?, ?)", departments)

        users = [
            (1, 'Иван', 1),
            (2, 'Мария', 2),
            (3, 'Алексей', 1),
            (4, 'Ольга', None),  # Нет отдела
            (5, 'Петр', 3),
            (6, 'Анна', 2)
        ]
        self.cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)

        self.conn.commit()

    def create_gui(self):
        """Создаем упрощенный интерфейс"""
        # Верхняя панель с кнопками запросов
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top_frame, text="Выберите тип JOIN:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))

        # Кнопки для разных JOIN
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=tk.LEFT)

        ttk.Button(buttons_frame, text="INNER JOIN",
                   command=self.inner_join, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="LEFT JOIN",
                   command=self.left_join, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Показать таблицы",
                   command=self.show_tables, width=15).pack(side=tk.LEFT, padx=5)

        # Область для результатов
        results_frame = ttk.LabelFrame(self.root, text="Результаты", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем Treeview для отображения таблицы
        self.tree = ttk.Treeview(results_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Статус бар
        self.status_label = ttk.Label(self.root, text="Готово. Выберите тип JOIN.",
                                      relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Инициализация
        self.show_tables()

    def execute_query(self, query, query_name):
        """Выполнить запрос и показать результаты"""
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]

            # Очищаем предыдущие результаты
            self.tree.delete(*self.tree.get_children())

            # Настраиваем колонки
            self.tree["columns"] = columns

            # Устанавливаем ширину колонок
            column_widths = {
                'ID': 80,
                'Имя': 150,
                'Отдел': 150,
                'Таблица': 120,
                'Название': 150,
                'ID отдела': 100
            }

            for col in columns:
                width = column_widths.get(col, 120)
                self.tree.heading(col, text=col)
                self.tree.column(col, width=width, minwidth=80, anchor=tk.W)

            # Добавляем данные
            for row in results:
                self.tree.insert("", "end", values=row)

            # Обновляем статус
            self.status_label.config(
                text=f"{query_name}: найдено {len(results)} записей"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
            self.status_label.config(text="Ошибка выполнения запроса")

    def inner_join(self):
        """INNER JOIN - только совпадающие записи"""
        query = """
        SELECT 
            u.user_id as ID,
            u.username as Имя,
            d.dept_name as Отдел
        FROM users u
        INNER JOIN departments d ON u.department_id = d.dept_id
        ORDER BY u.user_id
        """
        self.execute_query(query, "INNER JOIN")

    def left_join(self):
        """LEFT JOIN - все пользователи, даже без отдела"""
        query = """
        SELECT 
            u.user_id as ID,
            u.username as Имя,
            COALESCE(d.dept_name, 'Нет отдела') as Отдел
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.dept_id
        ORDER BY u.user_id
        """
        self.execute_query(query, "LEFT JOIN")

    def show_tables(self):
        """Показать содержимое обеих таблиц"""
        query = """
        SELECT 'Пользователи' as Таблица, user_id as ID, username as Имя, 
               department_id as 'ID отдела' FROM users
        UNION ALL
        SELECT 'Отделы' as Таблица, dept_id as ID, dept_name as Название, 
               NULL as 'ID отдела' FROM departments
        ORDER BY Таблица, ID
        """
        self.execute_query(query, "Просмотр таблиц")


def main():
    root = tk.Tk()
    app = SimpleJoinApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()