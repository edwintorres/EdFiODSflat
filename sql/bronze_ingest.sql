-- This creates a view of students
CREATE OR REPLACE TEMP VIEW bronze_students AS
SELECT * FROM student_raw; -- pulling all columns
