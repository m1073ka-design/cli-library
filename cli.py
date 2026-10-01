import sqlite3

class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

class Member:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

class Library:
    def __init__(self):
        self.db = sqlite3.connect("library.db")
        self.create_tables()

    def create_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                available INTEGER DEFAULT 1
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                book_id INTEGER,
                member_id INTEGER
            )
        """)

        self.db.commit()

    def add_book(self, book):
        self.db.execute(
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            (book.title, book.author, book.year)
        )
        self.db.commit()

    def show_books(self):
        books = self.db.execute(
            "SELECT id, title, author, available FROM books"
        ).fetchall()

        for book in books:
            status = "bor" if book[3] else "berilgan"
            print(book[0], book[1], "-", book[2], "-", status)

    def search_book(self, word):
        books = self.db.execute(
            """
            SELECT id, title, author, available
            FROM books
            WHERE title LIKE ? OR author LIKE ?
            """,
            (f"%{word}%", f"%{word}%")
        ).fetchall()

        for book in books:
            status = "bor" if book[3] else "berilgan"
            print(book[0], book[1], "-", book[2], "-", status)

    def add_member(self, member):
        self.db.execute(
            "INSERT INTO members (name, phone) VALUES (?, ?)",
            (member.name, member.phone)
        )
        self.db.commit()

    def give_book(self, member_id, book_id):
        book = self.db.execute(
            "SELECT available FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        member = self.db.execute(
            "SELECT id FROM members WHERE id = ?",
            (member_id,)
        ).fetchone()

        if not book:
            print("Kitob topilmadi.")
            return

        if not member:
            print("A'zo topilmadi.")
            return

        if book[0] == 0:
            print("Bu kitob allaqachon berilgan.")
            return

        self.db.execute(
            "UPDATE books SET available = 0 WHERE id = ?",
            (book_id,)
        )

        self.db.execute(
            "INSERT INTO loans VALUES (?, ?)",
            (book_id, member_id)
        )

        self.db.commit()
        print("Kitob berildi.")

    def return_book(self, book_id):
        book = self.db.execute(
            "SELECT available FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if not book:
            print("Kitob topilmadi.")
            return

        if book[0] == 1:
            print("Bu kitob berilmagan.")
            return

        self.db.execute(
            "UPDATE books SET available = 1 WHERE id = ?",
            (book_id,)
        )

        self.db.execute(
            "DELETE FROM loans WHERE book_id = ?",
            (book_id,)
        )

        self.db.commit()
        print("Kitob qaytarildi.")

    def show_loans(self):
        data = self.db.execute("""
            SELECT books.title, members.name
            FROM loans
            JOIN books ON books.id = loans.book_id
            JOIN members ON members.id = loans.member_id
        """).fetchall()

        if not data:
            print("Hozir berilgan kitob yo'q.")
            return

        for book, member in data:
            print(f"{member} - {book}")


library = Library()

while True:
    print("""
1. Kitob qo'shish
2. Barcha kitoblar
3. Kitob qidirish
4. A'zo qo'shish
5. Kitob berish
6. Kitobni qaytarish
7. Kimda qaysi kitob bor
0. Chiqish
""")

    try:
        choice = int(input("Tanlang: "))

        if choice == 1:
            title = input("Kitob nomi: ")
            author = input("Muallif: ")
            year = int(input("Yili: "))
            library.add_book(Book(title, author, year))
            print("Kitob qo'shildi.")

        elif choice == 2:
            library.show_books()

        elif choice == 3:
            word = input("Qidirish: ")
            library.search_book(word)

        elif choice == 4:
            name = input("Ism: ")
            phone = input("Telefon: ")
            library.add_member(Member(name, phone))
            print("A'zo qo'shildi.")

        elif choice == 5:
            member_id = int(input("A'zo ID: "))
            book_id = int(input("Kitob ID: "))
            library.give_book(member_id, book_id)

        elif choice == 6:
            book_id = int(input("Kitob ID: "))
            library.return_book(book_id)

        elif choice == 7:
            library.show_loans()

        elif choice == 0:
            print("Dastur tugadi.")
            break

        else:
            print("Noto'g'ri tanlov.")

    except ValueError:
        print("Raqam kiriting.")
    except Exception as e:
        print("Xatolik:", e)