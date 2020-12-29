
class Category:

    def __init__(self, name):
        self.name = name
        self.books = []

    def addBook(self, book):
        self.books.append(book)
