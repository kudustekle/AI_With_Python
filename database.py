import pyodbc
from datetime import datetime, timedelta

def get_repair_history(phone_number=None, year=None, status_filter=None, date_range=None):
    try:
        conn = pyodbc.connect("DRIVER={SQL Server};SERVER=ZX291003130-2\ERITEL961;DATABASE=Cable2;UID=sa;PWD=123")
        cursor = conn.cursor()

        query = """
        SELECT CCC.[Telephone No], Complaint.Complaint_ID, Complaint.Registered_Date, Complaint.Status_type,
               Complaint.Problem_Description, Complaint.Priority, CCC.CCC, CCC.[CCC Address], CCC.[TB Address]
        FROM CCC
        INNER JOIN Complaint ON CCC.id = Complaint.Cust_ID_CCC
        WHERE 1=1
        """

        params = []

        if phone_number:
            query += " AND CCC.[Telephone No] = ?"
            params.append(phone_number)

        if status_filter:
            query += " AND Complaint.Status_type = ?"
            params.append(status_filter)

        if year:
            query += " AND YEAR(Complaint.Registered_Date) = ?"
            params.append(year)

        if date_range:
            start_date, end_date = date_range
            query += " AND Complaint.Registered_Date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        query += " ORDER BY Complaint.Registered_Date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        history = []
        for row in rows:
            registered_date = row[2].strftime("%Y-%m-%d") if isinstance(row[2], datetime) else row[2]
            history.append({
                "Telephone No": row[0],
                "Complaint ID": row[1],
                "Registered Date": registered_date,
                "Status": row[3],
                "Problem Description": row[4],
                "Priority": row[5],
                "CCC": row[6],
                "CCC Address": row[7],
                "TB Address": row[8]
            })

        conn.close()
        return history if history else []

    except Exception as e:
        return {"error": str(e)}

def get_complaint_stats(date_range):
    try:
        conn = pyodbc.connect("DRIVER={SQL Server};SERVER=ZX291003130-2\ERITEL961;DATABASE=Cable2;UID=sa;PWD=123")
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM Complaint WHERE Registered_Date BETWEEN ? AND ?"
        cursor.execute(query, date_range)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    except Exception as e:
        return {"error": str(e)}
