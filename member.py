class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name

    def add_member(self, db):
        query = "INSERT INTO members (name) VALUES (%s)"
        db.execute_query(query, (self.name,))

    def delete_member(self, db):
        # SV code: Xóa thành viên theo member_id
        query = "DELETE FROM members WHERE member_id = %s"
        db.execute_query(query, (self.member_id,))

    @staticmethod
    def delete_member_by_id(db, member_id):
        """Hỗ trợ xóa thành viên trực tiếp qua member_id."""
        query = "DELETE FROM members WHERE member_id = %s"
        db.execute_query(query, (member_id,))

    def update_member_info(self, db):
        # SV code: Cập nhật thông tin thành viên (tên)
        query = "UPDATE members SET name = %s WHERE member_id = %s"
        db.execute_query(query, (self.name, self.member_id))

    @staticmethod
    def search_member(db, member_id):
        query = "SELECT * FROM members WHERE member_id = %s"
        return db.fetch_one(query, (member_id,))

    @staticmethod
    def search_member_by_name(db, name):
        """Tìm kiếm thành viên theo họ tên (dùng LIKE %s)."""
        query = "SELECT * FROM members WHERE name LIKE %s"
        pattern = f"%{name}%"
        return db.fetch_all(query, (pattern,))

    @staticmethod
    def get_all_members(db):
        query = "SELECT * FROM members"
        return db.fetch_all(query)
