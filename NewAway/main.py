import tkinter as tk
from tkinter import messagebox
import json, os
from collections import defaultdict

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
import tkinter as tk
from tkinter import ttk, messagebox

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
SLOTS = [1, 2, 3, 4, 5, 6, 7, 8]  # Removed 9

class CourseSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Course Scheduler")

        # Initialize teacher and course data
        self.teachers_file = "teachers.txt"
        self.courses_file = "courses.txt"
        self.priority_file = "priority.txt"  # New file for teacher priorities
        self.teachers = self.load_teachers()
        self.teacher_priorities = self.load_teacher_priorities()  # Load priorities
        self.courses = self.load_courses()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.setup_input_tab()
        self.setup_teacher_tab()
        self.setup_courses_tab()
        self.setup_schedule_tab()  # Add a new tab for schedule information

        # Initialize the teacher dropdown with the current teacher list
        self.update_teacher_combo()

        # Add button for PDF generation
        ttk.Button(root, text="Generate Routine PDF", command=self.generate_pdf).pack(pady=10)

    def load_teachers(self):
        """Load teachers from the teachers.txt file."""
        if os.path.exists(self.teachers_file):
            with open(self.teachers_file, "r") as file:
                return [line.strip() for line in file.readlines()]
        return []

    def load_teacher_priorities(self):
        """Load teacher priorities and slot preferences from the priority.txt file."""
        if os.path.exists(self.priority_file):
            with open(self.priority_file, "r") as file:
                return {
                    line.split(",")[0].strip(): {
                        "priority": int(line.split(",")[1].strip()),
                        "slots": [slot.strip() for slot in line.split(",")[2:]]
                    }
                    for line in file.readlines()
                }
        return {}

    def save_teacher_priorities(self):
        """Save teacher priorities and slot preferences to the priority.txt file."""
        with open(self.priority_file, "w") as file:
            for teacher, data in self.teacher_priorities.items():
                file.write(f"{teacher},{data['priority']},{data['slots']}\n")

    def save_teachers(self):
        """Save teachers to the teachers.txt file."""
        with open(self.teachers_file, "w") as file:
            file.writelines(f"{teacher}\n" for teacher in self.teachers)

    def load_courses(self):
        """Load courses from the courses.txt file."""
        if os.path.exists(self.courses_file):
            with open(self.courses_file, "r") as file:
                return [json.loads(line.strip()) for line in file.readlines()]
        return []

    def save_courses(self):
        """Save courses to the courses.txt file."""
        with open(self.courses_file, "w") as file:
            file.writelines(f"{json.dumps(course)}\n" for course in self.courses)

    def setup_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input")
        ttk.Label(input_frame, text="(Input tab can be used for consolidated data or initial options.)").pack(pady=20)

    def setup_teacher_tab(self):
        teacher_frame = ttk.Frame(self.notebook)
        self.notebook.add(teacher_frame, text="Teachers")

        # Teacher Name
        ttk.Label(teacher_frame, text="Teacher Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.teacher_name_entry = ttk.Entry(teacher_frame)
        self.teacher_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Teacher Department
        ttk.Label(teacher_frame, text="Teacher Department:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.teacher_dept_entry = ttk.Entry(teacher_frame)
        self.teacher_dept_entry.grid(row=1, column=1, padx=5, pady=5)

        # Teacher Priority
        ttk.Label(teacher_frame, text="Teacher Priority:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.teacher_priority_entry = ttk.Entry(teacher_frame)
        self.teacher_priority_entry.grid(row=2, column=1, padx=5, pady=5)

        # Teacher Slot Preferences
        ttk.Label(teacher_frame, text="Slot Preferences (e.g., Monday 10am-1pm, Tuesday 2pm-5pm):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.teacher_slot_entry = ttk.Entry(teacher_frame)
        self.teacher_slot_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add Teacher Button
        ttk.Button(teacher_frame, text="Add Teacher", command=self.add_teacher).grid(row=4, column=0, columnspan=2, pady=10)

    def setup_courses_tab(self):
        course_frame = ttk.Frame(self.notebook)
        self.notebook.add(course_frame, text="Courses")

        # Course Code
        ttk.Label(course_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.course_code_entry = ttk.Entry(course_frame)
        self.course_code_entry.grid(row=0, column=1, padx=5, pady=5)

        # Course Name
        ttk.Label(course_frame, text="Course Name:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.course_name_entry = ttk.Entry(course_frame)
        self.course_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Year
        ttk.Label(course_frame, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.year_spinbox = ttk.Spinbox(course_frame, from_=1, to=4, increment=1)
        self.year_spinbox.grid(row=2, column=1, padx=5, pady=5)

        # Credit
        ttk.Label(course_frame, text="Credit:").grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Validation for fractional credit input
        validate_float = self.root.register(self.validate_float_input)
        self.credit_spinbox = ttk.Entry(course_frame, validate="key", validatecommand=(validate_float, "%P"))
        self.credit_spinbox.grid(row=3, column=1, padx=5, pady=5)

        # Teacher
        ttk.Label(course_frame, text="Teacher:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.teacher_combo = ttk.Combobox(course_frame)
        self.teacher_combo.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        ttk.Button(course_frame, text="Add Course", command=self.add_course).grid(row=5, column=0, padx=5, pady=10)
        ttk.Button(course_frame, text="Remove Course", command=self.remove_course).grid(row=5, column=1, padx=5, pady=10)
        ttk.Button(course_frame, text="Clear", command=self.clear_course_entries).grid(row=5, column=2, padx=5, pady=10)

        # Course Log
        self.course_log = tk.Text(course_frame, height=8, width=60)
        self.course_log.grid(row=6, column=0, columnspan=3, padx=5, pady=10)

    def setup_schedule_tab(self):
        """Setup the Schedule Information tab."""
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Schedule Info")

        # Add a label to display schedule information
        self.schedule_label = ttk.Label(
            schedule_frame,
            text="Schedule Information will appear here after generating the schedule.",
            wraplength=600,
            justify="left"
        )
        self.schedule_label.pack(padx=10, pady=10)

    def update_schedule_info(self, schedule_text):
        """Update the schedule information label with the generated schedule."""
        self.schedule_label.config(text=schedule_text)

    def add_teacher(self):
        name = self.teacher_name_entry.get().strip()
        dept = self.teacher_dept_entry.get().strip()
        priority = self.teacher_priority_entry.get().strip()
        slot_preferences = self.teacher_slot_entry.get().strip()  # Get slot preferences

        if name and dept and priority:
            try:
                priority = int(priority)  # Ensure priority is an integer
            except ValueError:
                messagebox.showerror("Error", "Priority must be an integer.")
                return

            if name not in self.teachers:  # Avoid duplicate entries
                self.teachers.append(name)  # Add the teacher to the dynamic list
                self.teacher_priorities[name] = {"priority": priority, "slots": slot_preferences}  # Save priority and slots
                self.save_teachers()  # Save to teachers.txt
                self.save_teacher_priorities()  # Save to priority.txt
                self.update_teacher_combo()  # Update the dropdown
                messagebox.showinfo("Success", f"Teacher {name} added successfully with priority {priority} and slot preferences: {slot_preferences}.")
            else:
                messagebox.showwarning("Warning", f"Teacher {name} already exists.")
            self.teacher_name_entry.delete(0, tk.END)
            self.teacher_dept_entry.delete(0, tk.END)
            self.teacher_priority_entry.delete(0, tk.END)
            self.teacher_slot_entry.delete(0, tk.END)  # Clear the slot preferences field
        else:
            messagebox.showerror("Error", "Please fill all teacher fields.")

    def add_course(self):
        code = self.course_code_entry.get().strip()
        name = self.course_name_entry.get().strip()
        year = self.year_spinbox.get()
        credit = self.credit_spinbox.get()
        teacher = self.teacher_combo.get()

        if all([code, name, year, credit, teacher]):
            course = {
                "code": code,
                "name": name,
                "year": int(year),
                "credit": float(credit),
                "teacher": teacher,
            }
            self.courses.append(course)  # Add to the course list
            self.save_courses()  # Save to file
            log = f"Course added: {code} ({name}) for Year {year} with {credit} credit(s), Teacher: {teacher}\n"
            self.course_log.insert(tk.END, log)
            self.clear_course_entries()
        else:
            messagebox.showerror("Error", "Please fill all course fields.")

    def validate_float_input(self, value):
        """Validate that the input is a valid float."""
        try:
            if value == "":
                return True
            float(value)
            return True
        except ValueError:
            return False

    def update_teacher_combo(self):
        """Update the teacher dropdown with the current teacher list."""
        self.teacher_combo["values"] = self.teachers

    def remove_course(self):
        messagebox.showinfo("Remove Course", "Feature not implemented yet.")

    def clear_course_entries(self):
        self.course_code_entry.delete(0, tk.END)
        self.course_name_entry.delete(0, tk.END)
        self.year_spinbox.set(1)
        self.credit_spinbox.delete(0, tk.END)
        self.teacher_combo.set('')

    def generate_pdf(self):
        """Generate a PDF file for the course schedule."""
        # Ensure courses are loaded from the file
        self.courses = self.load_courses()

        if not self.courses:
            messagebox.showerror("Error", "No courses available to generate the schedule.")
            return

        # Validate each course entry
        required_keys = {"code", "teacher", "year", "credit"}
        for course in self.courses:
            if not isinstance(course, dict) or not required_keys.issubset(course.keys()):
                messagebox.showerror("Error", "Each course must be a dictionary with keys: 'code', 'teacher', 'year', 'credit'.")
                return

        # Initialize schedule data structures
        teacher_schedule = defaultdict(lambda: {day: set() for day in DAYS})
        routine = {year: {day: {slot: None for slot in SLOTS} for day in DAYS} for year in [1, 2, 3, 4]}

        # Generate short names for teachers
        teacher_short_names = {
            teacher: ''.join([name[0].upper() for name in teacher.split()])
            for teacher in self.teachers
        }

        # Sort teachers by priority
        teacher_priority = sorted(self.teacher_priorities.items(), key=lambda x: x[1]["priority"])  # Sort by priority value
        sorted_teachers = [teacher for teacher, _ in teacher_priority]

        # Sort courses by teacher priority
        teacher_rank = {teacher: idx for idx, teacher in enumerate(sorted_teachers)}
        self.courses.sort(key=lambda c: teacher_rank.get(c["teacher"], float("inf")))

        def parse_time_range(time_range):
            """Parse a time range like '10am-1pm' into slot indices."""
            time_map = {
                "9am-10am": 1,
                "10am-11am": 2,
                "11am-12pm": 3,
                "12pm-1pm": 4,
                "1pm-2pm": 5,  # Break slot
                "2pm-3pm": 6,
                "3pm-4pm": 7,
                "4pm-5pm": 8
            }
            try:
                start, end = time_range.split("-")
                # Find the corresponding slot indices for the given time range
                slots = [slot for time, slot in time_map.items() if time.startswith(start) or time.endswith(end)]
                if not slots:
                    raise KeyError(f"Invalid time range: {time_range}")
                return slots
            except KeyError as e:
                messagebox.showerror("Error", f"Invalid time range: {e}")
                return []

        def can_assign(teacher, year, day, slot):
            """Check if a slot can be assigned to a teacher."""
            return routine[year][day][slot] is None and slot not in teacher_schedule[teacher][day]

        def assign_consecutive_slots(teacher, year, day, start_slot, code):
            """Try to assign three consecutive slots starting from start_slot."""
            for slot in range(start_slot, start_slot + 3):
                if slot > max(SLOTS) or not can_assign(teacher, year, day, slot):
                    return False
            for slot in range(start_slot, start_slot + 3):
                routine[year][day][slot] = (code, teacher_short_names[teacher])
                teacher_schedule[teacher][day].add(slot)
            return True

        # Assign courses to the schedule
        for c in self.courses:
            year, code, teacher, credit = c["year"], c["code"], c["teacher"], c["credit"]
            assigned = 0
            prefs = self.teacher_priorities[teacher]["slots"]  # Get slot preferences

            # Safely extract numeric part of the course code and check if it's odd or even
            try:
                numeric_part = ''.join(filter(str.isdigit, code))
                is_even_code = int(numeric_part) % 2 == 0 if numeric_part else False
            except ValueError:
                is_even_code = False

            for pref in prefs:
                day, time_range = pref.split(" ")
                slots = parse_time_range(time_range)
                for slot in slots:
                    if assigned >= credit:
                        break
                    if is_even_code and (credit == 1 or credit == 1.5):
                        # Assign three consecutive slots for even course codes with credit 1 or 1.5
                        if assign_consecutive_slots(teacher, year, day, slot, code):
                            assigned += 3
                            break
                    else:
                        # Assign a single slot for odd courses (only one class per day)
                        if can_assign(teacher, year, day, slot) and slot not in teacher_schedule[teacher][day]:
                            routine[year][day][slot] = (code, teacher_short_names[teacher])
                            teacher_schedule[teacher][day].add(slot)
                            assigned += 1
                            break  # Ensure only one class per day for odd courses

        # Generate schedule text for the GUI
        schedule_text = "Generated Schedule:\n\n"
        for year, days in routine.items():
            schedule_text += f"Year {year}:\n"
            for day, slots in days.items():
                schedule_text += f"  {day}:\n"
                for slot, data in slots.items():
                    if data:
                        schedule_text += f"    Slot {slot}: {data[0]} (Teacher: {data[1]})\n"
                    else:
                        schedule_text += f"    Slot {slot}: Free\n"
            schedule_text += "\n"

        # Update the schedule information label
        self.update_schedule_info(schedule_text)

        # Generate PDF
        slot_times = {
            1: "9-10",
            2: "10-11",
            3: "11-12",
            4: "12-1",
            5: "1-2",  # Break slot
            6: "2-3",
            7: "3-4",
            8: "4-5"
        }
        table_data = [["Day", "Year"] + [slot_times[s] for s in SLOTS]]
        year_names = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

        for day in DAYS:
            for yr in [1, 2, 3, 4]:
                row = [day if yr == 1 else "", year_names[yr - 1]]
                for s in SLOTS:
                    if s == 5:
                        # Mark slot 5 as "Break" in the table
                        row.append("Break")
                    else:
                        data = routine[yr][day][s]
                        row.append(f"{data[0]}\n({data[1]})" if data else "")
                table_data.append(row)

        # Generate the teacher short name and full name table
        teacher_table_data = [["Short Name", "Full Name"]]
        for teacher, short_name in teacher_short_names.items():
            teacher_table_data.append([short_name, teacher])

        pdf = SimpleDocTemplate("routine_final.pdf", pagesize=landscape(letter))
        main_table = Table(table_data, colWidths=[70, 90] + [80] * len(SLOTS))
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.whitesmoke]),  # Alternating row colors
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        teacher_table = Table(teacher_table_data, colWidths=[150, 300])
        teacher_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.whitesmoke]), 
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Add a spacer between the main table and the teacher table
        spacer = Spacer(1, 20)  # 20 units of vertical space

        pdf.build([main_table, spacer, teacher_table])  # Add spacer between tables
        messagebox.showinfo("PDF Generated", "Routine saved as 'routine_final.pdf'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSchedulerApp(root)
    root.mainloop()
