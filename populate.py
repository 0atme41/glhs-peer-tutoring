import csv
import sqlite3

with open ('formatted.csv') as file:
    reader = csv.reader(file, delimiter = ',')
    connection = sqlite3.connect("tutoring.db")
    cursor = connection.cursor()
    for line in reader:
        name = line[0].split(",")[0].strip().split(" ")
        if (name[0] != "Student"):
            email = line[1].strip()
            focus_classes = [line[2], line[3], line[4]]
            if (len(name) > 2):
                cursor.execute("INSERT INTO tutors (t_ln, t_fn, email, subject1, subject2, subject3, capacity, t_capacity) VALUES (?, ?, ?, ?, ?, ?, 3, 3)", (name[2], name[0] + name[1], email, focus_classes[0], focus_classes[1], focus_classes[2]))
            elif (len(name) > 1):
                cursor.execute("INSERT INTO tutors (t_ln, t_fn, email, subject1, subject2, subject3, capacity, t_capacity) VALUES (?, ?, ?, ?, ?, ?, 3, 3)", (name[1], name[0], email, focus_classes[0], focus_classes[1], focus_classes[2]))
            connection.commit()