class User:
    def __init__(self,name,password ,role="user"):
        self.name = name
        self.password = password
        self.role = role
        self.borrowed_books = []


    def borrow_book(self,book):
        if book and book.available:
            book.available = False
            self.borrowed_books.append(book)
            print(f"{self.name} borrowed {book.title}")
        else:
            print("Book is not available for borrowing")

            
    def return_book(self,book):
        if book in self.borrowed_books:
            book.available = True
            self.borrowed_books.remove(book)
            print(f"{self.name} returned {book.title}")
        else:
            print("You don't have this book")

# Here we store the user details
        
