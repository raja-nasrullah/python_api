from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# --- NEON CONFIGURATION ---
# Neon Dashboard se copy ki gayi URL yahan paste karein. 
# Yaad rakhein: Password ke baad '@' aur aakhir mein '?sslmode=require' hona chahiye.
DB_URL = "postgresql://neondb_owner:npg_XcRNYF1Qlnu4@ep-summer-star-ahliu2y9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
def get_db_connection():
    try:
        # Neon ke liye hum direct connect kar sakte hain
        conn = psycopg2.connect(
            DB_URL, 
            cursor_factory=RealDictCursor, 
            connect_timeout=10
        )
        return conn
    except Exception as e:
        print(f"NEON CONNECTION ERROR: {e}")
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
        # Saara data nikalne ki query
        cursor.execute("SELECT id, name, age, rollnumber FROM students")
        students = cursor.fetchall()
        
        # Agar data khali ho toh message show karein, warna data return karein
        if not students:
            return {"message": "Database is connected but empty!", "data": []}
            
        return {
            "status": "Connected to Neon.tech",
            "total_students": len(students),
            "all_data": students
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

# 1. Saare students get karne ke liye (Ab ye Neon se data layega)
@app.get("/students")
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, age, rollnumber FROM students")
        students = cursor.fetchall()
        return students
    finally:
        cursor.close()
        conn.close()

# 2. Naya student add karne ke liye
@app.post("/students")
def create_student(student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO students (name, age, rollnumber) VALUES (%s, %s, %s)"
        values = (student.name, student.age, student.rollnumber)
        cursor.execute(query, values)
        conn.commit()
        return {"message": "Student added successfully to Neon!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# 3. Kisi ek student ko ID ke zariye dhundne ke liye
@app.get("/students/{id}")
def get_student_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, age, rollnumber FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        if student:
            return student
        raise HTTPException(status_code=404, detail="Student not found")
    finally:
        cursor.close()
        conn.close()

# 4. Student delete karne ke liye
@app.delete("/students/{id}")
def delete_student(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        conn.commit()
        return {"message": "Student deleted successfully"}
    finally:
        cursor.close()
        conn.close()

# 5. Student ka data update karne ke liye
@app.put("/students/{id}")
def update_student(id: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE students SET name = %s, age = %s, rollnumber = %s WHERE id = %s"
        values = (student.name, student.age, student.rollnumber, id)
        cursor.execute(query, values)
        conn.commit()
        return {"message": "Student updated successfully"}
    finally:
        cursor.close()
        conn.close()
