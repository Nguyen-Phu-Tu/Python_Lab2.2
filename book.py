class Book:
    def __init__(self, book_id, title, author, pages, year_published, status, category):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.pages = pages
        self.year_published = year_published
        self.status = status  
        self.category = category

    def add_book(self, db):
        query = "INSERT INTO books (title, author, pages, year_published, status, category) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (self.title, self.author, self.pages, self.year_published, self.status, self.category)
        db.execute_query(query, params)

    def update_book(self, db):
      
        query = """
        UPDATE books 
        SET title = %s, author = %s, pages = %s, year_published = %s, status = %s, category = %s 
        WHERE book_id = %s
        """
        params = (self.title, self.author, self.pages, self.year_published, self.status, self.category, self.book_id)
        db.execute_query(query, params)

    def delete_book(self, db):
        query = "DELETE FROM books WHERE book_id = %s"
        db.execute_query(query, (self.book_id,))

    @staticmethod
    def delete_book_by_id(db, book_id):
        """Hỗ trợ xóa sách trực tiếp qua book_id."""
        query = "DELETE FROM books WHERE book_id = %s"
        db.execute_query(query, (book_id,))

    @staticmethod
    def search_book(db, book_id):
        query = "SELECT * FROM books WHERE book_id = %s"
        return db.fetch_one(query, (book_id,))

    @staticmethod
    def get_all_books(db):
        query = "SELECT * FROM books"
        return db.fetch_all(query)

    @staticmethod
    def search_book_by_title(db, title):

        query = "SELECT * FROM books WHERE title LIKE %s"
        pattern = f"%{title}%"
        return db.fetch_all(query, (pattern,))

    @staticmethod
    def update_status(db, book_id, status):
        """Cập nhật trạng thái sách (0: có sẵn, 1: đã mượn, 2: trạng thái khác)."""
        query = "UPDATE books SET status = %s WHERE book_id = %s"
        db.execute_query(query, (status, book_id))
