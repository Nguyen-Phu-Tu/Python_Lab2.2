import mysql.connector
from datetime import datetime, date, timedelta
from database import Database
from book import Book
from member import Member
from borrowing import Borrowing


def validate_date(date_str):
    """Kiểm tra định dạng ngày YYYY-MM-DD. Trả về True nếu hợp lệ."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_date(d):
    """Định dạng ngày thành chuỗi DD-MM-YYYY trực quan."""
    if d is None:
        return ""
    if hasattr(d, "strftime"):
        return d.strftime("%d-%m-%Y")
    try:
        dt = datetime.strptime(str(d), "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return str(d)


def format_book_status(status):
    """Chuyển mã số trạng thái sách thành nhãn văn bản tiếng Việt."""
    if status == 0:
        return "Có sẵn"
    elif status == 1:
        return "Đang mượn"
    return f"Khác ({status})"


def print_book_table(books):
    """In danh sách sách dạng bảng căn cột ASCII (| và +)."""
    if not books:
        print("  (Không có dữ liệu)")
        return
    header = ("Mã sách", "Tên sách", "Tác giả", "Số trang", "Năm XB", "Trạng thái", "Thể loại")


    display_rows = []
    for row in books:
        r = (row[0], row[1], row[2], row[3], row[4], format_book_status(row[5]), row[6])
        display_rows.append(r)

    widths = [len(h) for h in header]
    for row in display_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val if val is not None else "")))

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)
    print("  " + fmt.format(*header))
    print("  " + sep)
    for row in display_rows:
        print("  " + fmt.format(*[str(v) if v is not None else "" for v in row]))


def print_member_table(members):
    """In danh sách thành viên dạng bảng căn cột ASCII (| và +)."""
    if not members:
        print("  (Không có dữ liệu)")
        return
    header = ("Mã TV", "Họ tên thành viên")
    widths = [len(h) for h in header]
    for row in members:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val if val is not None else "")))

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)
    print("  " + fmt.format(*header))
    print("  " + sep)
    for row in members:
        print("  " + fmt.format(*[str(v) if v is not None else "" for v in row]))


def print_borrowing_table(borrowings):
    """In danh sách phiếu mượn dạng bảng căn cột ASCII (JOIN 3 bảng)."""
    if not borrowings:
        print("  (Không có dữ liệu)")
        return
    header = ("Mã PM", "Mã TV", "Tên thành viên", "Mã sách", "Tên sách", "Ngày mượn", "Hạn trả", "Ngày trả", "Tình trạng")
    today = date.today()
    display_rows = []
    for row in borrowings:
        pm_id, m_id, m_name, b_id, b_title, b_date, d_date, r_date = row
        b_str = format_date(b_date)
        d_str = format_date(d_date)
        r_str = format_date(r_date) if r_date else "Chưa trả"

        if r_date:
            status_str = "Đã trả"
        else:
            d_compare = d_date.date() if isinstance(d_date, datetime) else d_date
            if isinstance(d_compare, date) and d_compare < today:
                status_str = "Quá hạn ⚠️"
            else:
                status_str = "Đang mượn"

        display_rows.append((pm_id, m_id, m_name, b_id, b_title, b_str, d_str, r_str, status_str))

    widths = [len(h) for h in header]
    for row in display_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val if val is not None else "")))

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)
    print("  " + fmt.format(*header))
    print("  " + sep)
    for row in display_rows:
        print("  " + fmt.format(*[str(v) if v is not None else "" for v in row]))


def print_overdue_table(overdues):
    """In danh sách sách mượn quá hạn dạng bảng căn cột ASCII."""
    if not overdues:
        print("  (Không có dữ liệu)")
        return
    header = ("Mã PM", "Mã sách", "Tên sách", "Mã TV", "Tên độc giả", "Ngày mượn", "Hạn trả", "Số ngày trễ")
    today = date.today()
    display_rows = []
    for row in overdues:
        pm_id, b_id, b_title, m_id, m_name, b_date, d_date = row
        b_str = format_date(b_date)
        d_str = format_date(d_date)

        late_days = 0
        if isinstance(d_date, datetime):
            late_days = (today - d_date.date()).days
        elif isinstance(d_date, date):
            late_days = (today - d_date).days
        elif d_date:
            try:
                parsed = datetime.strptime(str(d_date), "%Y-%m-%d").date()
                late_days = (today - parsed).days
            except Exception:
                late_days = "?"

        display_rows.append((pm_id, b_id, b_title, m_id, m_name, b_str, d_str, f"{late_days} ngày"))

    widths = [len(h) for h in header]
    for row in display_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val if val is not None else "")))

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)
    print("  " + fmt.format(*header))
    print("  " + sep)
    for row in display_rows:
        print("  " + fmt.format(*[str(v) if v is not None else "" for v in row]))


def print_statistics_table(stats):
    """In bảng thống kê số lượt mượn theo từng cuốn sách."""
    if not stats:
        print("  (Không có dữ liệu)")
        return
    header = ("Mã sách", "Tên sách", "Tác giả", "Thể loại", "Số lượt mượn")
    widths = [len(h) for h in header]
    for row in stats:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val if val is not None else "")))

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)
    print("  " + fmt.format(*header))
    print("  " + sep)
    for row in stats:
        print("  " + fmt.format(*[str(v) if v is not None else "" for v in row]))


def main():
    db = Database()
    while True:
        print("\n" + "=" * 55)
        print("               HỆ THỐNG QUẢN LÝ THƯ VIỆN")
        print("=" * 55)
        print("--- Quản lý Sách ---")
        print("  1.  Thêm sách")
        print("  2.  Sửa thông tin sách")
        print("  3.  Xóa sách")
        print("  4.  Tìm kiếm sách theo ID/Tên")
        print("  5.  Hiển thị danh sách sách")
        print("--- Quản lý Thành viên ---")
        print("  6.  Thêm thành viên")
        print("  7.  Sửa thông tin thành viên")
        print("  8.  Xóa thành viên")
        print("  9.  Tìm kiếm thành viên")
        print("  10. Hiển thị danh sách thành viên")
        print("--- Quản lý Mượn/Trả & Thống kê ---")
        print("  11. Mượn sách")
        print("  12. Trả sách")
        print("  13. Hiển thị danh sách phiếu mượn")
        print("  14. Hiển thị sách mượn quá hạn")
        print("  15. Thống kê sách mượn nhiều nhất")
        print("  0.  Thoát")
        print("-" * 55)

        choice = input("Chọn chức năng: ").strip()

  
        if choice == "1":
            try:
                title = input("Nhập tên sách: ").strip()
                if not title:
                    print("❌ Lỗi: Tên sách không được để trống!")
                    continue
                author = input("Nhập tác giả: ").strip()
                if not author:
                    print("❌ Lỗi: Tác giả không được để trống!")
                    continue
                pages_str = input("Nhập số trang: ").strip()
                pages = int(pages_str)
                if pages <= 0:
                    print("❌ Lỗi: Số trang phải lớn hơn 0!")
                    continue
                year_str = input("Nhập năm xuất bản: ").strip()
                year_published = int(year_str)
                if year_published <= 0:
                    print("❌ Lỗi: Năm xuất bản không hợp lệ!")
                    continue
                status_str = input("Nhập trạng thái sách (0: có sẵn, 1: đã mượn, 2: khác) [0]: ").strip()
                if status_str == "":
                    status = 0
                else:
                    status = int(status_str)
                    if status not in (0, 1, 2):
                        print("❌ Lỗi: Trạng thái chỉ nhận giá trị 0 (có sẵn), 1 (đã mượn) hoặc 2 (trạng thái khác)!")
                        continue
                category = input("Nhập chủng loại sách (Tiểu thuyết, Giáo khoa, Khoa học,...): ").strip()
                if not category:
                    print("❌ Lỗi: Chủng loại sách không được để trống!")
                    continue

                book = Book(None, title, author, pages, year_published, status, category)
                book.add_book(db)
                print("✅ Thêm sách thành công!")
            except ValueError:
                print("❌ Lỗi: Số trang, năm xuất bản và trạng thái phải là số nguyên!")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "2":
            try:
                book_id_str = input("Nhập ID sách cần sửa: ").strip()
                if not book_id_str.isdigit():
                    print("❌ Lỗi: ID sách phải là số nguyên!")
                    continue
                book_id = int(book_id_str)
                book = Book.search_book(db, book_id)
                if book:
                    old = book  
                    print(f"  Thông tin hiện tại:")
                    print_book_table([book])
                    print("  (Nhấn Enter để giữ nguyên giá trị cũ)")

                    title = input(f"  Tên sách mới [{old[1]}]: ").strip() or old[1]
                    author = input(f"  Tác giả mới [{old[2]}]: ").strip() or old[2]

                    pages_str = input(f"  Số trang mới [{old[3]}]: ").strip()
                    if pages_str == "":
                        pages = old[3]
                    else:
                        pages = int(pages_str)
                        if pages <= 0:
                            print("❌ Lỗi: Số trang phải lớn hơn 0!")
                            continue

                    year_str = input(f"  Năm xuất bản mới [{old[4]}]: ").strip()
                    if year_str == "":
                        year_published = old[4]
                    else:
                        year_published = int(year_str)
                        if year_published <= 0:
                            print("❌ Lỗi: Năm xuất bản không hợp lệ!")
                            continue

                    status_str = input(f"  Trạng thái mới (0: có sẵn, 1: đã mượn, 2: khác) [{old[5]}]: ").strip()
                    if status_str == "":
                        status = old[5]
                    else:
                        status = int(status_str)
                        if status not in (0, 1, 2):
                            print("❌ Lỗi: Trạng thái chỉ nhận giá trị 0, 1 hoặc 2!")
                            continue

                    category = input(f"  Chủng loại mới [{old[6]}]: ").strip() or old[6]

                    updated_book = Book(book_id, title, author, pages, year_published, status, category)
                    updated_book.update_book(db)
                    print("✅ Cập nhật thông tin sách thành công!")
                else:
                    print("❌ Sách không tồn tại.")
            except ValueError:
                print("❌ Lỗi: Giá trị nhập vào không hợp lệ!")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "3":
            try:
                book_id_str = input("Nhập ID sách cần xóa: ").strip()
                if not book_id_str.isdigit():
                    print("❌ Lỗi: ID sách phải là số nguyên!")
                    continue
                book_id = int(book_id_str)
                book = Book.search_book(db, book_id)
                if book:
                    print(f"  Thông tin sách sẽ bị xóa:")
                    print_book_table([book])
                    borrowings = Borrowing.get_borrowings_by_book(db, book_id)
                    if borrowings:
                        print(f"  ⚠️ CẢNH BÁO: Cuốn sách này đang có {len(borrowings)} bản ghi mượn sách liên quan.")
                        print(f"  Các bản ghi mượn sách sau sẽ bị XÓA TỰ ĐỘNG (ON DELETE CASCADE):")
                        print_borrowing_table(borrowings)
                    confirm = input("  Bạn có chắc muốn xóa? (y/n): ").strip().lower()
                    if confirm == "y":
                        Book.delete_book_by_id(db, book_id)
                        print("✅ Xóa sách thành công!")
                    else:
                        print("  Đã hủy thao tác xóa.")
                else:
                    print("❌ Sách không tồn tại.")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "4":
            print("  --- Tìm kiếm sách ---")
            print("  a. Tìm theo ID sách")
            print("  b. Tìm theo tên sách (tương đối)")
            sub_choice = input("  Chọn cách tìm (a/b): ").strip().lower()
            if sub_choice == "a":
                book_id_str = input("  Nhập ID sách cần tìm: ").strip()
                if not book_id_str.isdigit():
                    print("  ❌ Lỗi: ID sách phải là số nguyên!")
                    continue
                book = Book.search_book(db, int(book_id_str))
                if book:
                    print("\n  Kết quả tìm kiếm:")
                    print_book_table([book])
                else:
                    print("  ❌ Sách không tồn tại.")
            elif sub_choice == "b":
                title = input("  Nhập tên sách cần tìm: ").strip()
                if not title:
                    print("  ❌ Tên sách không được để trống!")
                    continue
                books = Book.search_book_by_title(db, title)
                if books:
                    print(f"\n  Kết quả tìm kiếm ({len(books)} cuốn sách):")
                    print_book_table(books)
                else:
                    print(f"  ❌ Không tìm thấy sách nào khớp với từ khóa '{title}'.")
            else:
                print("  ❌ Lựa chọn không hợp lệ.")

        elif choice == "5":
            books = Book.get_all_books(db)
            if books:
                print(f"\n  Danh sách sách ({len(books)} cuốn sách):")
                print_book_table(books)
            else:
                print("  Không có sách nào trong thư viện.")

        elif choice == "6":
            try:
                name = input("Nhập họ tên thành viên: ").strip()
                if not name:
                    print("❌ Lỗi: Họ tên thành viên không được để trống!")
                    continue
                member = Member(None, name)
                member.add_member(db)
                print("✅ Thêm thành viên thành công!")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "7":
            try:
                member_id_str = input("Nhập ID thành viên cần sửa: ").strip()
                if not member_id_str.isdigit():
                    print("❌ Lỗi: ID thành viên phải là số nguyên!")
                    continue
                member_id = int(member_id_str)
                member = Member.search_member(db, member_id)
                if member:
                    old = member  # (member_id, name)
                    print(f"  Thông tin hiện tại:")
                    print_member_table([member])
                    print("  (Nhấn Enter để giữ nguyên giá trị cũ)")
                    name = input(f"  Họ tên mới [{old[1]}]: ").strip() or old[1]
                    updated_member = Member(member_id, name)
                    updated_member.update_member_info(db)
                    print("✅ Cập nhật thông tin thành viên thành công!")
                else:
                    print("❌ Thành viên không tồn tại.")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "8":
            try:
                member_id_str = input("Nhập ID thành viên cần xóa: ").strip()
                if not member_id_str.isdigit():
                    print("❌ Lỗi: ID thành viên phải là số nguyên!")
                    continue
                member_id = int(member_id_str)
                member = Member.search_member(db, member_id)
                if member:
                    print(f"  Thông tin thành viên sẽ bị xóa:")
                    print_member_table([member])
                    borrowings = Borrowing.get_borrowings_by_member(db, member_id)
                    if borrowings:
                        print(f"  ⚠️ CẢNH BÁO: Thành viên này đang có {len(borrowings)} bản ghi mượn sách liên quan.")
                        print(f"  Các bản ghi mượn sách sau sẽ bị XÓA TỰ ĐỘNG (ON DELETE CASCADE):")
                        print_borrowing_table(borrowings)
                    confirm = input("  Bạn có chắc muốn xóa? (y/n): ").strip().lower()
                    if confirm == "y":
                        Member.delete_member_by_id(db, member_id)
                        print("✅ Xóa thành viên thành công!")
                    else:
                        print("  Đã hủy thao tác xóa.")
                else:
                    print("❌ Thành viên không tồn tại.")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "9":
            print("  --- Tìm kiếm thành viên ---")
            print("  a. Tìm theo ID thành viên")
            print("  b. Tìm theo họ tên (tương đối)")
            sub_choice = input("  Chọn cách tìm (a/b): ").strip().lower()
            if sub_choice == "a":
                member_id_str = input("  Nhập ID thành viên cần tìm: ").strip()
                if not member_id_str.isdigit():
                    print("  ❌ Lỗi: ID thành viên phải là số nguyên!")
                    continue
                member = Member.search_member(db, int(member_id_str))
                if member:
                    print("\n  Kết quả tìm kiếm:")
                    print_member_table([member])
                else:
                    print("  ❌ Thành viên không tồn tại.")
            elif sub_choice == "b":
                name = input("  Nhập họ tên thành viên cần tìm: ").strip()
                if not name:
                    print("  ❌ Họ tên không được để trống!")
                    continue
                members = Member.search_member_by_name(db, name)
                if members:
                    print(f"\n  Kết quả tìm kiếm ({len(members)} thành viên):")
                    print_member_table(members)
                else:
                    print(f"  ❌ Không tìm thấy thành viên nào khớp với từ khóa '{name}'.")
            else:
                print("  ❌ Lựa chọn không hợp lệ.")

        elif choice == "10":
            members = Member.get_all_members(db)
            if members:
                print(f"\n  Danh sách thành viên ({len(members)} thành viên):")
                print_member_table(members)
            else:
                print("  Không có thành viên nào trong hệ thống.")


        elif choice == "11":
            try:
                member_id_str = input("Nhập ID thành viên: ").strip()
                if not member_id_str.isdigit():
                    print("❌ Lỗi: ID thành viên phải là số nguyên!")
                    continue
                member_id = int(member_id_str)
                member = Member.search_member(db, member_id)
                if not member:
                    print("❌ Lỗi: Thành viên không tồn tại trong hệ thống! Vui lòng thêm thành viên trước.")
                    continue

                book_id_str = input("Nhập ID sách cần mượn: ").strip()
                if not book_id_str.isdigit():
                    print("❌ Lỗi: ID sách phải là số nguyên!")
                    continue
                book_id = int(book_id_str)
                book = Book.search_book(db, book_id)
                if not book:
                    print("❌ Lỗi: Sách không tồn tại trong hệ thống! Vui lòng thêm sách trước.")
                    continue

        
                if book[5] == 1:
                    print(f"❌ Lỗi: Cuốn sách '{book[1]}' (Mã: {book_id}) hiện ĐÃ ĐƯỢC MƯỢN! Không thể mượn tiếp.")
                    continue
                elif book[5] != 0:
                    print(f"❌ Lỗi: Cuốn sách '{book[1]}' (Mã: {book_id}) hiện không có sẵn để cho mượn (Trạng thái: {format_book_status(book[5])})!")
                    continue

                borrow_date_str = input("Nhập ngày mượn (YYYY-MM-DD, Enter = hôm nay): ").strip()
                if borrow_date_str == "":
                    borrow_date = datetime.now().date()
                else:
                    if not validate_date(borrow_date_str):
                        print("❌ Lỗi: Ngày mượn không đúng định dạng YYYY-MM-DD!")
                        continue
                    borrow_date = datetime.strptime(borrow_date_str, "%Y-%m-%d").date()

                default_due = borrow_date + timedelta(days=14)
                due_date_str = input(f"Nhập hạn trả (YYYY-MM-DD, Enter = {default_due}): ").strip()
                if due_date_str == "":
                    due_date = default_due
                else:
                    if not validate_date(due_date_str):
                        print("❌ Lỗi: Hạn trả không đúng định dạng YYYY-MM-DD!")
                        continue
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    if due_date < borrow_date:
                        print("❌ Lỗi: Hạn trả không được trước ngày mượn!")
                        continue

                borrowing = Borrowing(None, member_id, book_id, borrow_date, due_date, None)
                borrowing.borrow_book(db)
                print(f"✅ Mượn sách thành công! Độc giả [{member[1]}] mượn sách [{book[1]}] (Hạn trả: {format_date(due_date)})")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "12":
            try:
                print("  --- Trả sách ---")
                print("  a. Trả theo Mã phiếu mượn (borrowing_id)")
                print("  b. Trả theo Mã sách (book_id)")
                sub = input("  Chọn cách trả (a/b): ").strip().lower()

                borrowing_record = None
                if sub == "a":
                    pm_id_str = input("  Nhập mã phiếu mượn: ").strip()
                    if not pm_id_str.isdigit():
                        print("  ❌ Lỗi: Mã phiếu mượn phải là số nguyên!")
                        continue
                    pm_id = int(pm_id_str)
                    borrowing_record = Borrowing.search_borrowing(db, pm_id)
                    if not borrowing_record:
                        print("  ❌ Không tìm thấy phiếu mượn với mã đã nhập.")
                        continue
                    if borrowing_record[7] is not None:
                        print(f"  ⚠️ Phiếu mượn này đã được trả vào ngày {format_date(borrowing_record[7])}!")
                        continue
                elif sub == "b":
                    book_id_str = input("  Nhập mã sách cần trả: ").strip()
                    if not book_id_str.isdigit():
                        print("  ❌ Lỗi: Mã sách phải là số nguyên!")
                        continue
                    book_id = int(book_id_str)
                    borrowing_record = Borrowing.get_active_borrowing_by_book(db, book_id)
                    if not borrowing_record:
                        print(f"  ❌ Không có bản ghi mượn sách chưa trả nào cho cuốn sách ID {book_id}.")
                        continue
                else:
                    print("  ❌ Lựa chọn không hợp lệ.")
                    continue

                print("  Thông tin phiếu mượn cần trả:")
                print_borrowing_table([borrowing_record])

                ret_date_str = input("  Nhập ngày trả (YYYY-MM-DD, Enter = hôm nay): ").strip()
                if ret_date_str == "":
                    return_date = datetime.now().date()
                else:
                    if not validate_date(ret_date_str):
                        print("  ❌ Lỗi: Ngày trả không đúng định dạng YYYY-MM-DD!")
                        continue
                    return_date = datetime.strptime(ret_date_str, "%Y-%m-%d").date()

                confirm = input("  Xác nhận trả sách? (y/n): ").strip().lower()
                if confirm == "y":
                    borrowing_id = borrowing_record[0]
                    book_id = borrowing_record[3]
                    b_obj = Borrowing(borrowing_id, borrowing_record[1], book_id, borrowing_record[5], borrowing_record[6], return_date)
                    b_obj.return_book(db)
                    print(f"✅ Trả sách thành công! Trạng thái sách [{borrowing_record[4]}] đã chuyển về 'Có sẵn'.")
                else:
                    print("  Đã hủy thao tác trả sách.")
            except mysql.connector.Error as e:
                print(f"❌ Lỗi CSDL: {e}")

        elif choice == "13":
            borrowings = Borrowing.get_all_borrowings(db)
            if borrowings:
                print(f"\n  Danh sách phiếu mượn ({len(borrowings)} bản ghi):")
                print_borrowing_table(borrowings)
            else:
                print("  Không có phiếu mượn nào trong hệ thống.")

        elif choice == "14":
            overdues = Borrowing.get_overdue_books(db)
            if overdues:
                print(f"\n  ⚠️ Danh sách sách mượn QUÁ HẠN ({len(overdues)} bản ghi):")
                print_overdue_table(overdues)
            else:
                print("  ✅ Tuyệt vời! Hiện không có sách nào bị quá hạn.")

        elif choice == "15":
            stats = Borrowing.get_most_borrowed_books(db)
            if stats:
                print("\n  Thống kê số lượt mượn theo từng cuốn sách:")
                print_statistics_table(stats)
                top = stats[0]
                if top[4] > 0:
                    print(f"\n  🏆 Sách được mượn nhiều nhất: {top[1]} (Mã: {top[0]}) — {top[4]} lượt mượn")
                else:
                    print("\n  (Chưa có cuốn sách nào được mượn)")
            else:
                print("  Không có dữ liệu để thống kê.")

        elif choice == "0":
            print("Đóng kết nối CSDL...")
            db.close()
            print("Thoát chương trình. Tạm biệt! 👋")
            break

        else:
            print("❌ Lựa chọn không hợp lệ. Vui lòng chọn lại!")


if __name__ == "__main__":
    main()