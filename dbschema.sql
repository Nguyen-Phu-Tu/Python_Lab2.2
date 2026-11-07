CREATE DATABASE IF NOT EXISTS Library;
USE Library;
DROP TABLE IF EXISTS borrowing;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    pages INT NOT NULL,
    year_published INT NOT NULL,
    status INT NOT NULL, 
    category VARCHAR(255) NOT NULL 
);

CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE borrowing (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

INSERT INTO books (title, author, pages, year_published, status, category) VALUES
('Dế Mèn Phiêu Lưu Ký', 'Tô Hoài', 150, 1941, 1, 'Tiểu thuyết'),
('Giải Tích 1', 'Nguyễn Đình Trí', 280, 2020, 1, 'Giáo khoa'),
('Lược Sử Thời Gian', 'Stephen Hawking', 256, 1988, 1, 'Khoa học'),
('Lập Trình Python Cơ Bản', 'Phạm Quang Hiển', 320, 2022, 0, 'Giáo khoa'),
('Số Đỏ', 'Vũ Trọng Phụng', 215, 1936, 0, 'Tiểu thuyết');

INSERT INTO members (name) VALUES
('Nguyễn Văn An'),
('Trần Thị Bích'),
('Lê Hoàng Long'),
('Phạm Minh Đức'),
('Hoàng Thảo My');

INSERT INTO borrowing (member_id, book_id, borrow_date, due_date, return_date) VALUES
(1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 25 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 11 DAY), NULL),
(2, 2, DATE_SUB(CURRENT_DATE, INTERVAL 20 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 6 DAY), NULL),
(3, 3, DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), DATE_ADD(CURRENT_DATE, INTERVAL 11 DAY), NULL),
(4, 4, DATE_SUB(CURRENT_DATE, INTERVAL 40 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 26 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 27 DAY)),
(5, 1, DATE_SUB(CURRENT_DATE, INTERVAL 60 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 45 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 46 DAY));

