import json
from book import Book


class Library:
    def __init__(self):
        self.books = []
    def add_book(self, book):
        for b in self.books:
            if b.book_id == book.book_id:
                print("Book ID already exists")
                return
        self.books.append(book)
        print("Book added successfully")

    def remove_book(self,book_id):
        for book in self.books:
            if book.book_id == book_id:
                self.books.remove(book)
                print(f"Book  With Title {book.title} removed successfully")
                return
        print("Book not found")
    def show_books(self):
        if not self.books:
            print("No books in the Library")
        else:
            for book in self.books:
                book.display_info()
    def find_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                return book
        return None
    
    def search_book(self, title):
        found = False
        for book in self.books:
            if title.lower() in book.title.lower():
                book.display_info()
                found = True
        if not found:
            print("No matching book found")
    
    def save_books(self):
        data = []
        for book in self.books:
            data.append({
                "id": book.book_id,
                "title":book.title,
                "author": book.author,
                "available": book.available
            })
        
        with open("data.json", "w") as f:
            json.dump(data,f)

    def load_books(self):
        try:
            with open("data.json", "r") as f:
                data = json.load(f)

                self.books = []

                for item in data:
                    book = Book(item["id"], item["title"], item["author"])
                    book.available = item["available"]
                    self.books.append(book)

        except FileNotFoundError:
            pass
    
    def show_available_books(self):
        found = False
        for book in self.books:
            if book.available:
                book.display_info()
                found= True
        if not found:
            print("No available books at the moment")

    def show_borrowed_books(self):
        found = False
        for book in self.books:
            if not book.available:
                book.display_info()
                found = True

        if not found:
            print("No borrowed books")
        
    
