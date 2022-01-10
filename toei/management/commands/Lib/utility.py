import datetime

class Utility:

    USER_JOIAS = "1"
    USER_SHU = "2"

    @staticmethod
    def get_next_year_month():
        now_year = datetime.date.today().year
        now_month = datetime.date.today().month
        year = now_year + 1 if now_month == 12 else now_year
        month = 1 if now_month == 12 else now_month + 1

        return [year, month]

    @staticmethod
    def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]