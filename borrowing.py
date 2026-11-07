from datetime import date, timedelta
from book import Book

class Borrowing:
    def __init__(self, borrowing_id, member_id, book_id, borrow_date, due_date, return_date=None):
        self.borrowing_id = borrowing_id
        self.member_id = member_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = return_date

    def borrow_book(self, db):
        query = """
        INSERT INTO borrowing (member_id, book_id, borrow_date, due_date, return_date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (self.member_id, self.book_id, self.borrow_date, self.due_date, self.return_date)
        db.execute_query(query, params)
       
        Book.update_status(db, self.book_id, 1)

    def return_book(self, db):
        query = "UPDATE borrowing SET return_date = %s WHERE borrowing_id = %s"
        params = (self.return_date, self.borrowing_id)
        db.execute_query(query, params)

        if not self.book_id:
            record = db.fetch_one("SELECT book_id FROM borrowing WHERE borrowing_id = %s", (self.borrowing_id,))
            if record:
                self.book_id = record[0]

        if self.book_id:
            Book.update_status(db, self.book_id, 0)

    @staticmethod
    def return_borrowing_by_id(db, borrowing_id, return_date):
        """Hỗ trợ trả sách trực tiếp bằng borrowing_id và tự động trả sách về status=0."""
        query = "UPDATE borrowing SET return_date = %s WHERE borrowing_id = %s"
        db.execute_query(query, (return_date, borrowing_id))
        record = db.fetch_one("SELECT book_id FROM borrowing WHERE borrowing_id = %s", (borrowing_id,))
        if record:
            Book.update_status(db, record[0], 0)

    @staticmethod
    def search_borrowing(db, borrowing_id):
        """Tìm kiếm chi tiết 1 phiếu mượn theo borrowing_id (JOIN 3 bảng)."""
        query = """
        SELECT bo.borrowing_id, m.member_id, m.name, b.book_id, b.title, bo.borrow_date, bo.due_date, bo.return_date
        FROM borrowing bo
        JOIN members m ON bo.member_id = m.member_id
        JOIN books b ON bo.book_id = b.book_id
        WHERE bo.borrowing_id = %s
        """
        return db.fetch_one(query, (borrowing_id,))

    @staticmethod
    def get_all_borrowings(db):
        """Hiển thị toàn bộ danh sách mượn/trả (JOIN 3 bảng borrowing, books, members)."""
        query = """
        SELECT bo.borrowing_id, m.member_id, m.name, b.book_id, b.title, bo.borrow_date, bo.due_date, bo.return_date
        FROM borrowing bo
        JOIN members m ON bo.member_id = m.member_id
        JOIN books b ON bo.book_id = b.book_id
        ORDER BY bo.borrowing_id ASC
        """
        return db.fetch_all(query)

    @staticmethod
    def get_overdue_books(db):
        """Lấy danh sách các sách đang mượn quá hạn (due_date < hôm nay và chưa trả)."""
        query = """
        SELECT bo.borrowing_id, b.book_id, b.title, m.member_id, m.name, bo.borrow_date, bo.due_date
        FROM borrowing bo
        JOIN books b ON bo.book_id = b.book_id
        JOIN members m ON bo.member_id = m.member_id
        WHERE bo.return_date IS NULL AND bo.due_date < %s
        ORDER BY bo.due_date ASC
        """
        today = date.today()
        return db.fetch_all(query, (today,))

    @staticmethod
    def get_borrowings_by_book(db, book_id):
        """Lấy tất cả bản ghi mượn liên quan đến 1 cuốn sách (kiểm tra trước khi xóa sách - ON DELETE CASCADE)."""
        query = """
        SELECT bo.borrowing_id, m.member_id, m.name, b.book_id, b.title, bo.borrow_date, bo.due_date, bo.return_date
        FROM borrowing bo
        JOIN members m ON bo.member_id = m.member_id
        JOIN books b ON bo.book_id = b.book_id
        WHERE bo.book_id = %s
        ORDER BY bo.borrowing_id ASC
        """
        return db.fetch_all(query, (book_id,))

    @staticmethod
    def get_borrowings_by_member(db, member_id):
        """Lấy tất cả bản ghi mượn liên quan đến 1 thành viên (kiểm tra trước khi xóa thành viên - ON DELETE CASCADE)."""
        query = """
        SELECT bo.borrowing_id, m.member_id, m.name, b.book_id, b.title, bo.borrow_date, bo.due_date, bo.return_date
        FROM borrowing bo
        JOIN members m ON bo.member_id = m.member_id
        JOIN books b ON bo.book_id = b.book_id
        WHERE bo.member_id = %s
        ORDER BY bo.borrowing_id ASC
        """
        return db.fetch_all(query, (member_id,))

    @staticmethod
    def get_active_borrowing_by_book(db, book_id):
        """Tìm bản ghi mượn sách chưa trả gần nhất của một cuốn sách."""
        query = """
        SELECT bo.borrowing_id, m.member_id, m.name, b.book_id, b.title, bo.borrow_date, bo.due_date, bo.return_date
        FROM borrowing bo
        JOIN members m ON bo.member_id = m.member_id
        JOIN books b ON bo.book_id = b.book_id
        WHERE bo.book_id = %s AND bo.return_date IS NULL
        ORDER BY bo.borrowing_id DESC
        LIMIT 1
        """
        return db.fetch_one(query, (book_id,))

    @staticmethod
    def get_most_borrowed_books(db):
        """Thống kê top sách được mượn nhiều nhất (GROUP BY + COUNT)."""
        query = """
        SELECT b.book_id, b.title, b.author, b.category, COUNT(bo.borrowing_id) AS borrow_count
        FROM books b
        LEFT JOIN borrowing bo ON b.book_id = bo.book_id
        GROUP BY b.book_id, b.title, b.author, b.category
        ORDER BY borrow_count DESC, b.book_id ASC
        """
        return db.fetch_all(query)
