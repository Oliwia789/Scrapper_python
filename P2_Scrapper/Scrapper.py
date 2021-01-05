import requests
from bs4 import BeautifulSoup
import csv
import re

from P2_Book.Book import Book
from P2_Category.Category import Category


def getSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text,features="html.parser")
    return (soup)


class Scrapper:

    def __init__(self):
        self.categories = []

    def getCategories(self):
        soup = getSoup("http://books.toscrape.com/")
        books_category = soup.find("ul", {"class": "nav nav-list"}).find_all("li")[1:]
        for li in books_category:
            category = Category(li.find("a")["href"].split('/')[3])
            self.categories.append(category)

    def getBooks(self):
        for category in self.categories:
            soup = getSoup("https://books.toscrape.com/catalogue/category/books/" + category.name + "/index.html")
            pager = (soup.find("li", {"class": "current"}))
            if pager is None:
                books = soup.find("div", {"class": "col-sm-8 col-md-9"}).find_all("h3")
                for h3 in books:
                    a = h3.find("a")
                    link_books = a["href"]
                    link_book = "https://books.toscrape.com/catalogue/" + link_books[9:]
                    category.addBook(self.createBook(link_book))
            else:
                pager = str(pager)
                pager = pager.split()[5]
                nbPages = int(pager)
                for i in range(nbPages + 1):
                    url = "https://books.toscrape.com/catalogue/category/books/" + category.name + "/page-" + str(i) + ".html"
                    response = requests.get(url)
                    if response.ok:
                        soup = BeautifulSoup(response.text,features="html.parser")
                        books = soup.find("div", {"class": "col-sm-8 col-md-9"}).find_all("h3")
                        for h3 in books:
                            a = h3.find("a")
                            link_books = a["href"]
                            links_book = "https://books.toscrape.com/catalogue/" + link_books[9:]
                            category.addBook(self.createBook(links_book))

    def createBook(self, link_book):
        book_url = link_book.strip()
        book_response = requests.get(book_url)
        book_soup = BeautifulSoup(book_response.text,features="html.parser")
        book_colonne = book_soup.find("table", {"class": "table table-striped"}).find_all("td")
        book_universal_product_code = book_colonne[0]
        book_title = book_soup.find("h1")
        book_price_including_tax = book_colonne[3]
        book_price_excluding_tax = book_colonne[2]
        book_number_available = book_colonne[5]
        book_product_description = book_soup.find("article", {"class": "product_page"}).find_all("p")[3]
        book_review_rating = book_soup.find('p', class_='star-rating').get('class')[1]
        book_images = book_soup.find("div", class_='item active').find_all("img")
        book_image_url = ""
        for book_image_url in book_images:
            book_image_url = "http://books.toscrape.com/" + (book_image_url.get('src')[5:])            
        # Downloading picture
        url = link_book.strip()
        soup = getSoup(url)
        title = soup.find("h1").text
        title_clean = re.sub('[^a-zA-Z0-9 \n\.]', '', title)
        with open(title_clean + ".jpg", "wb") as file:
            images = soup.find("div", class_='item active').find_all("img")
            for image_url in images:
                image_url = "http://books.toscrape.com/" + (image_url.get('src')[5:])
                response = requests.get(image_url)
            file.write(response.content)

        return Book(book_url, book_universal_product_code.text, book_title.text, book_price_including_tax.text[2:],
                    book_price_excluding_tax.text[2:],
                    book_number_available.text, book_product_description.text, book_review_rating, book_image_url)

    def createCsv(self):
        for category in self.categories:
            with open(category.name + ".csv", "a", encoding='utf-8') as file:
                writer = csv.writer(file)
                file.write(
                    "product_page_url,universal_product_code,title,price_including_tax,price_excluding_tax,number_available,product_description,review_rating,images\n")
                for book in category.books:
                    writer.writerow([book.url, book.productCode, book.title, book.priceTTC, book.priceHT, book.availableCount, book.description, book.reviewRating, book.imageUrl]) 
