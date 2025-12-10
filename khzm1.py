

import mysql.connector
from mysql.connector import Error
import getpass  # For secure password input

def create_connection():
    """Create a database connection"""
    try:
        # Get database credentials
        print("Enter MySQL Database Credentials:")
        host = input("Host (default: localhost): ") or "localhost"
        user = input("Username (default: root): ") or "root"
        password = getpass.getpass("Password: ")
        database = input("Database name: ")
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL database")
            return connection
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def create_students_table(connection):
    """Create students table if it doesn't exist"""
    try:
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            roll_number VARCHAR(20) UNIQUE NOT NULL,
            age INT CHECK (age > 0 AND age < 100),
            school_name VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        print("✅ Students table created/verified")
        
    except Error as e:
        print(f"❌ Error creating table: {e}")

def add_student(connection):
    """Add a new student record"""
    try:
        print("\n➕ ADD NEW STUDENT")
        name = input("Enter student name: ")
        roll_number = input("Enter roll number: ")
        age = int(input("Enter age: "))
        school_name = input("Enter school name: ")
        
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO students (name, roll_number, age, school_name)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (name, roll_number, age, school_name))
        connection.commit()
        
        print(f"✅ Student '{name}' added successfully!")
        
    except Error as e:
        print(f"❌ Error adding student: {e}")

def view_all_students(connection):
    """View all student records"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id")
        students = cursor.fetchall()
        
        print("\n📋 ALL STUDENT RECORDS")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Roll No':<15} {'Age':<5} {'School':<25} {'Created At':<20}")
        print("-" * 80)
        
        if not students:
            print("No records found!")
        else:
            for student in students:
                print(f"{student[0]:<5} {student[1]:<20} {student[2]:<15} {student[3]:<5} {student[4]:<25} {str(student[5])[:19]:<20}")
        
        print(f"\nTotal students: {len(students)}")
        
    except Error as e:
        print(f"❌ Error fetching students: {e}")

def search_student(connection):
    """Search student by roll number or name"""
    try:
        print("\n🔍 SEARCH STUDENT")
        search_term = input("Enter roll number or name to search: ")
        
        cursor = connection.cursor()
        search_query = """
        SELECT * FROM students 
        WHERE roll_number LIKE %s OR name LIKE %s
        """
        
        cursor.execute(search_query, (f'%{search_term}%', f'%{search_term}%'))
        students = cursor.fetchall()
        
        if not students:
            print("❌ No students found!")
        else:
            print("\n📋 SEARCH RESULTS")
            print("-" * 80)
            for student in students:
                print(f"ID: {student[0]}")
                print(f"Name: {student[1]}")
                print(f"Roll No: {student[2]}")
                print(f"Age: {student[3]}")
                print(f"School: {student[4]}")
                print(f"Created: {student[5]}")
                print("-" * 40)
        
    except Error as e:
        print(f"❌ Error searching student: {e}")

def update_student(connection):
    """Update student record"""
    try:
        view_all_students(connection)
        student_id = input("\nEnter student ID to update: ")
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print("❌ Student not found!")
            return
        
        print(f"\nCurrent details of Student ID {student_id}:")
        print(f"Name: {student[1]}")
        print(f"Roll No: {student[2]}")
        print(f"Age: {student[3]}")
        print(f"School: {student[4]}")
        
        print("\nEnter new details (leave blank to keep current):")
        name = input(f"Name [{student[1]}]: ") or student[1]
        roll_number = input(f"Roll No [{student[2]}]: ") or student[2]
        age = input(f"Age [{student[3]}]: ") or student[3]
        school_name = input(f"School [{student[4]}]: ") or student[4]
        
        update_query = """
        UPDATE students 
        SET name = %s, roll_number = %s, age = %s, school_name = %s
        WHERE id = %s
        """
        
        cursor.execute(update_query, (name, roll_number, int(age), school_name, student_id))
        connection.commit()
        
        print(f"✅ Student ID {student_id} updated successfully!")
        
    except Error as e:
        print(f"❌ Error updating student: {e}")

def delete_student(connection):
    """Delete student record"""
    try:
        view_all_students(connection)
        student_id = input("\nEnter student ID to delete: ")
        
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print("❌ Student not found!")
            return
        
        confirm = input(f"Are you sure you want to delete '{student[0]}'? (yes/no): ")
        
        if confirm.lower() == 'yes':
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            connection.commit()
            print(f"✅ Student '{student[0]}' deleted successfully!")
        else:
            print("❌ Deletion cancelled!")
        
    except Error as e:
        print(f"❌ Error deleting student: {e}")

def display_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("       STUDENT MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Add New Student")
    print("2. View All Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")
    print("="*50)

def main():
    """Main function"""
    print("🚀 Student Management System with MySQL")
    
    # Create database connection
    connection = create_connection()
    if not connection:
        return
    
    # Create students table
    create_students_table(connection)
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            add_student(connection)
        elif choice == '2':
            view_all_students(connection)
        elif choice == '3':
            search_student(connection)
        elif choice == '4':
            update_student(connection)
        elif choice == '5':
            delete_student(connection)
        elif choice == '6':
            print("👋 Thank you for using Student Management System!")
            break
        else:
            print("❌ Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")
    
    # Close connection
    if connection.is_connected():
        connection.close()
        print("✅ Database connection closed")

if __name__ == "__main__":
    main()