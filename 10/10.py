import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем базовый класс для моделей
Base = declarative_base()


# Определяем модель Product
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class SQLAlchemyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLAlchemy ORM - Управление товарами")
        self.root.geometry("900x600")

        # Создаем engine и сессию SQLAlchemy
        self.engine = create_engine('sqlite:///products.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Добавляем тестовые данные, если таблица пуста
        self.add_sample_data()

        # Создаем GUI
        self.create_gui()

        # Загружаем данные
        self.load_products()

    def add_sample_data(self):
        """Добавляем тестовые данные, если таблица пуста"""
        count = self.session.query(Product).count()
        if count == 0:
            sample_products = [
                Product(name="Ноутбук", category="Электроника", price=45000, quantity=10),
                Product(name="Смартфон", category="Электроника", price=25000, quantity=25),
                Product(name="Наушники", category="Аксессуары", price=3500, quantity=50),
                Product(name="Книга Python", category="Книги", price=1200, quantity=30),
                Product(name="Футболка", category="Одежда", price=800, quantity=100),
                Product(name="Кофеварка", category="Бытовая техника", price=5000, quantity=15),
                Product(name="Мышь компьютерная", category="Аксессуары", price=800, quantity=40),
                Product(name="Монитор", category="Электроника", price=18000, quantity=8),
            ]
            self.session.add_all(sample_products)
            self.session.commit()

    def create_gui(self):
        """Создаем интерфейс"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Конфигурация веса строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление товарами", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Поля ввода данных
        ttk.Label(control_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.name_entry = ttk.Entry(control_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(control_frame, text="Категория:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.category_entry = ttk.Entry(control_frame, width=20)
        self.category_entry.grid(row=0, column=3, padx=(0, 10))

        ttk.Label(control_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.price_entry = ttk.Entry(control_frame, width=15)
        self.price_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))

        ttk.Label(control_frame, text="Количество:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.quantity_entry = ttk.Entry(control_frame, width=15)
        self.quantity_entry.grid(row=1, column=3, padx=(0, 10), pady=(10, 0))

        # Кнопки управления
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=(15, 5))

        ttk.Button(buttons_frame, text="Добавить", command=self.add_product, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Обновить", command=self.update_product, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Удалить", command=self.delete_product, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить", command=self.clear_form, width=15).pack(side=tk.LEFT, padx=5)

        # Панель фильтрации и поиска
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация и поиск", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Категория:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.category_filter.pack(side=tk.LEFT, padx=(0, 15))
        self.category_filter.bind("<<ComboboxSelected>>", self.filter_by_category)

        ttk.Label(filter_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(filter_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="Найти", command=self.search_products, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.load_products, width=10).pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        table_frame = ttk.LabelFrame(main_frame, text="Список товаров", padding="10")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создаем Treeview с прокруткой
        self.tree = ttk.Treeview(table_frame, columns=("id", "name", "category", "price", "quantity"), show="headings")

        # Настраиваем столбцы
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("category", text="Категория")
        self.tree.heading("price", text="Цена")
        self.tree.heading("quantity", text="Количество")

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("category", width=150, anchor=tk.W)
        self.tree.column("price", width=100, anchor=tk.E)
        self.tree.column("quantity", width=100, anchor=tk.E)

        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Привязываем двойной клик для редактирования
        self.tree.bind("<Double-1>", self.on_item_double_click)

        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack(side=tk.LEFT)

        # Загружаем категории для фильтра
        self.load_categories()

    def load_categories(self):
        """Загружаем список категорий для фильтра"""
        categories = self.session.query(Product.category).distinct().all()
        category_list = ["Все категории"] + [cat[0] for cat in categories if cat[0]]
        self.category_filter["values"] = category_list
        self.category_filter.current(0)

    def load_products(self, products=None):
        """Загружаем товары в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Если не переданы товары, загружаем все
        if products is None:
            products = self.session.query(Product).order_by(Product.name).all()

        # Добавляем товары в таблицу
        for product in products:
            self.tree.insert("", "end", values=(
                product.id,
                product.name,
                product.category,
                f"{product.price:,.2f}",
                product.quantity
            ))

        # Обновляем статистику
        self.update_stats(products)

    def update_stats(self, products):
        """Обновляем статистику"""
        total_count = len(products)
        total_value = sum(p.price * p.quantity for p in products)
        avg_price = sum(p.price for p in products) / total_count if total_count > 0 else 0

        self.stats_label.config(
            text=f"Товаров: {total_count} | "
                 f"Общая стоимость: {total_value:,.2f} руб. | "
                 f"Средняя цена: {avg_price:,.2f} руб."
        )

    def add_product(self):
        """Добавляем новый товар"""
        try:
            name = self.name_entry.get().strip()
            category = self.category_entry.get().strip()

            if not name:
                messagebox.showwarning("Ошибка", "Введите название товара")
                return

            price = float(self.price_entry.get().strip() or 0)
            quantity = int(self.quantity_entry.get().strip() or 0)

            # Создаем новый продукт
            new_product = Product(
                name=name,
                category=category if category else None,
                price=price,
                quantity=quantity
            )

            # Добавляем в БД
            self.session.add(new_product)
            self.session.commit()

            # Обновляем таблицу
            self.load_products()
            self.clear_form()
            self.load_categories()  # Обновляем список категорий

            messagebox.showinfo("Успех", f"Товар '{name}' добавлен успешно!")

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат цены или количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")

    def get_selected_product(self):
        """Получаем выбранный товар"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар из таблицы")
            return None

        item = self.tree.item(selection[0])
        product_id = item["values"][0]

        # Находим продукт в БД
        product = self.session.query(Product).filter(Product.id == product_id).first()
        return product

    def update_product(self):
        """Обновляем выбранный товар"""
        product = self.get_selected_product()
        if not product:
            return

        try:
            # Обновляем данные продукта
            product.name = self.name_entry.get().strip()
            product.category = self.category_entry.get().strip() or None

            price_str = self.price_entry.get().strip()
            quantity_str = self.quantity_entry.get().strip()

            if price_str:
                product.price = float(price_str)
            if quantity_str:
                product.quantity = int(quantity_str)

            # Сохраняем изменения
            self.session.commit()

            # Обновляем таблицу
            self.load_products()
            self.load_categories()  # Обновляем список категорий

            messagebox.showinfo("Успех", "Товар обновлен успешно!")

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат цены или количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")

    def delete_product(self):
        """Удаляем выбранный товар"""
        product = self.get_selected_product()
        if not product:
            return

        if messagebox.askyesno("Подтверждение", f"Удалить товар '{product.name}'?"):
            try:
                self.session.delete(product)
                self.session.commit()

                # Обновляем таблицу
                self.load_products()
                self.load_categories()  # Обновляем список категорий

                messagebox.showinfo("Успех", "Товар удален успешно!")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    def on_item_double_click(self, event):
        """Обработка двойного клика по товару"""
        product = self.get_selected_product()
        if product:
            self.fill_form(product)

    def fill_form(self, product):
        """Заполняем форму данными товара"""
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

        self.name_entry.insert(0, product.name)
        self.category_entry.insert(0, product.category or "")
        self.price_entry.insert(0, str(product.price))
        self.quantity_entry.insert(0, str(product.quantity))

    def clear_form(self):
        """Очищаем форму"""
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def filter_by_category(self, event=None):
        """Фильтруем товары по категории"""
        category = self.category_filter.get()
        if category == "Все категории":
            self.load_products()
        else:
            products = self.session.query(Product).filter(
                Product.category == category
            ).order_by(Product.name).all()
            self.load_products(products)

    def search_products(self):
        """Ищем товары по названию"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Предупреждение", "Введите текст для поиска")
            return

        products = self.session.query(Product).filter(
            Product.name.ilike(f"%{search_term}%")
        ).order_by(Product.name).all()

        self.load_products(products)

        if not products:
            messagebox.showinfo("Результат", "Товары не найдены")

    def on_closing(self):
        """Закрываем сессию при выходе"""
        self.session.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SQLAlchemyApp(root)

    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()