from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DB_URL = "postgresql://neondb_owner:npg_XcRNYF1Qlnu4@ep-summer-star-ahliu2y9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            DB_URL, 
            cursor_factory=RealDictCursor, 
            connect_timeout=10
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

class Student(BaseModel):
    name: str
    age: int
    rollnumber: int

@app.get("/")
def read_root():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, age, rollnumber FROM students")
        students = cursor.fetchall()
        if not students:
            return {"message": "Database is connected but empty!", "data": []}
        return {"status": "Connected to Neon.tech", "total_students": len(students), "all_data": students}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/students")
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, age, rollnumber FROM students")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.post("/students")
def create_student(student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO students (name, age, rollnumber) VALUES (%s, %s, %s)"
        cursor.execute(query, (student.name, student.age, student.rollnumber))
        conn.commit()
        return {"message": "Student added successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# File ke bilkul aakhir mein ye add kar dein agar nahi hai
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
