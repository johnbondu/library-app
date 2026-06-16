class Book:
    def __init__(self,book_id,title,author):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.available = True
    def display_info(self):
        status = "Available" if self.available else "Not Available "
        print(f"{self.book_id} - {self.title} by {self.author}[{status}]") 


#this shows books details
