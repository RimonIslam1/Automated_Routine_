import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from collections import defaultdict
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
SLOTS = [1, 2, 3, 4, 5, 6, 7, 8]  # Removed 9

class CourseSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Course Scheduler")

        # Initialize data files
        self.teachers_file = "teachers.txt"
        self.courses_file = "courses.txt"
        self.priority_file = "priority.txt"
        
        # Load data
        self.teachers = self.load_teachers()
        self.teacher_priorities = self.load_teacher_priorities()
        self.courses = self.load_courses()

        # Setup GUI
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.setup_input_tab()
        self.setup_teacher_tab()
        self.setup_courses_tab()
        self.setup_schedule_tab()

        self.update_teacher_combo()
        ttk.Button(root, text="Generate Routine PDF", command=self.generate_pdf).pack(pady=10)

    # Data Loading/Saving Methods
    def load_teachers(self):
        if os.path.exists(self.teachers_file):
            with open(self.teachers_file, "r") as file:
                return [line.strip() for line in file.readlines()]
        return []

    def load_teacher_priorities(self):
        if os.path.exists(self.priority_file):
            priorities = {}
            with open(self.priority_file, "r") as file:
                for line in file.readlines():
                    try:
                        parts = line.strip().split(",")
                        if len(parts) >= 3:
                            teacher = parts[0].strip()
                            priority = int(parts[1].strip())
                            slots = [s.strip().strip("'") for s in parts[2:]]
                            priorities[teacher] = {"priority": priority, "slots": slots}
                    except (ValueError, IndexError) as e:
                        print(f"Skipping invalid line: {line.strip()} (Error: {e})")
            return priorities
        return {}

    def save_teacher_priorities(self):
        with open(self.priority_file, "w") as file:
            for teacher, data in self.teacher_priorities.items():
                file.write(f"{teacher},{data['priority']}," + ",".join(f"'{s}'" for s in data["slots"]) + "\n")

    def save_teachers(self):
        with open(self.teachers_file, "w") as file:
            file.writelines(f"{teacher}\n" for teacher in self.teachers)

    def load_courses(self):
        if os.path.exists(self.courses_file):
            with open(self.courses_file, "r") as file:
                return [json.loads(line.strip()) for line in file.readlines()]
        return []

    def save_courses(self):
        with open(self.courses_file, "w") as file:
            file.writelines(f"{json.dumps(course)}\n" for course in self.courses)

    # GUI Setup Methods
    def setup_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input")
        ttk.Label(input_frame, text="(Input tab can be used for consolidated data or initial options.)").pack(pady=20)

    def setup_teacher_tab(self):
        teacher_frame = ttk.Frame(self.notebook)
        self.notebook.add(teacher_frame, text="Teachers")

        ttk.Label(teacher_frame, text="Teacher Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.teacher_name_entry = ttk.Entry(teacher_frame)
        self.teacher_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(teacher_frame, text="Teacher Department:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.teacher_dept_entry = ttk.Entry(teacher_frame)
        self.teacher_dept_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(teacher_frame, text="Teacher Priority:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.teacher_priority_entry = ttk.Entry(teacher_frame)
        self.teacher_priority_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(teacher_frame, text="Slot Preferences (e.g., Monday 10am-1pm, Tuesday 2pm-5pm):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.teacher_slot_entry = ttk.Entry(teacher_frame)
        self.teacher_slot_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(teacher_frame, text="Add Teacher", command=self.add_teacher).grid(row=4, column=0, columnspan=2, pady=10)

    def setup_courses_tab(self):
        course_frame = ttk.Frame(self.notebook)
        self.notebook.add(course_frame, text="Courses")

        ttk.Label(course_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.course_code_entry = ttk.Entry(course_frame)
        self.course_code_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Course Name:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.course_name_entry = ttk.Entry(course_frame)
        self.course_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.year_spinbox = ttk.Spinbox(course_frame, from_=1, to=4, increment=1)
        self.year_spinbox.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Credit:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        validate_float = self.root.register(self.validate_float_input)
        self.credit_spinbox = ttk.Entry(course_frame, validate="key", validatecommand=(validate_float, "%P"))
        self.credit_spinbox.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Teacher:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.teacher_combo = ttk.Combobox(course_frame)
        self.teacher_combo.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(course_frame, text="Add Course", command=self.add_course).grid(row=5, column=0, padx=5, pady=10)
        ttk.Button(course_frame, text="Remove Course", command=self.remove_course).grid(row=5, column=1, padx=5, pady=10)
        ttk.Button(course_frame, text="Clear", command=self.clear_course_entries).grid(row=5, column=2, padx=5, pady=10)

        self.course_log = tk.Text(course_frame, height=8, width=60)
        self.course_log.grid(row=6, column=0, columnspan=3, padx=5, pady=10)

    def setup_schedule_tab(self):
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Schedule Info")
        self.schedule_label = ttk.Label(schedule_frame, text="Schedule Information will appear here after generating the schedule.", wraplength=600, justify="left")
        self.schedule_label.pack(padx=10, pady=10)

    # Core Functionality Methods
    def add_teacher(self):
        name = self.teacher_name_entry.get().strip()
        dept = self.teacher_dept_entry.get().strip()
        priority = self.teacher_priority_entry.get().strip()
        slot_prefs = [s.strip() for s in self.teacher_slot_entry.get().split(",") if s.strip()]

        if name and dept and priority:
            try:
                priority = int(priority)
                if name not in self.teachers:
                    self.teachers.append(name)
                    self.teacher_priorities[name] = {"priority": priority, "slots": slot_prefs}
                    self.save_teachers()
                    self.save_teacher_priorities()
                    self.update_teacher_combo()
                    messagebox.showinfo("Success", f"Teacher {name} added successfully!")
                else:
                    messagebox.showwarning("Warning", f"Teacher {name} already exists.")
                self.teacher_name_entry.delete(0, tk.END)
                self.teacher_dept_entry.delete(0, tk.END)
                self.teacher_priority_entry.delete(0, tk.END)
                self.teacher_slot_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Priority must be an integer.")
        else:
            messagebox.showerror("Error", "Please fill all teacher fields.")

    def add_course(self):
        code = self.course_code_entry.get().strip()
        name = self.course_name_entry.get().strip()
        year = self.year_spinbox.get()
        credit = self.credit_spinbox.get().strip()
        teacher = self.teacher_combo.get().strip()

        if all([code, name, year, credit, teacher]):
            try:
                course = {
                    "code": code,
                    "name": name,
                    "year": int(year),
                    "credit": float(credit),
                    "teacher": teacher,
                }
                self.courses.append(course)
                self.save_courses()
                log = f"Course added: {code} ({name}) for Year {year} with {credit} credit(s), Teacher: {teacher}\n"
                self.course_log.insert(tk.END, log)
                self.clear_course_entries()
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input for year or credit.")
        else:
            messagebox.showerror("Error", "Please fill all course fields.")

    def generate_pdf(self):
        """Main scheduling function with backtracking"""
        self.courses = self.load_courses()
        if not self.courses:
            messagebox.showerror("Error", "No courses available to generate schedule.")
            return

        # Initialize data structures
        teacher_schedule = defaultdict(lambda: {day: set() for day in DAYS})
        routine = {year: {day: {slot: None for slot in SLOTS} for day in DAYS} 
                  for year in [1, 2, 3, 4]}
        teacher_short_names = self._generate_teacher_short_names()

        # Sort by priorities
        sorted_teachers = sorted(self.teacher_priorities.items(), 
                               key=lambda x: x[1]["priority"])
        teacher_rank = {teacher: idx for idx, (teacher, _) in enumerate(sorted_teachers)}
        self.courses.sort(key=lambda c: teacher_rank.get(c["teacher"], float("inf")))
        
        # Process even courses with backtracking
        self._process_even_courses(routine, teacher_schedule, teacher_short_names)
        
        # Process odd courses
        self._process_odd_courses(routine, teacher_schedule, teacher_short_names)
        
        # Generate output
        schedule_text = self._generate_schedule_text(routine)
        self.update_schedule_info(schedule_text)
        self._create_pdf(routine, teacher_short_names)

    def _process_even_courses(self, routine, teacher_schedule, teacher_short_names):
        """Backtracking implementation for even courses"""
        for course in [c for c in self.courses if self._is_even_course(c["code"])]:
            assigned = False
            teacher = course["teacher"]
            year = course["year"]
            code = course["code"]
            
            # Try preferences first
            if teacher in self.teacher_priorities:
                for pref in self.teacher_priorities[teacher]["slots"]:
                    try:
                        day, time_range = pref.split(" ", 1)
                        slots = self._parse_time_range(time_range)
                        if self._assign_consecutive_slots(teacher, year, day, slots[0], code, 
                                                        routine, teacher_schedule, 
                                                        teacher_short_names):
                            assigned = True
                            break
                    except (ValueError, IndexError):
                        continue
            
            # If preferences failed, try all possible slots
            if not assigned:
                for day in DAYS:
                    for slot in SLOTS:
                        if slot <= max(SLOTS) - 2:  # Need 3 consecutive slots
                            if self._assign_consecutive_slots(teacher, year, day, slot, code,
                                                            routine, teacher_schedule,
                                                            teacher_short_names):
                                assigned = True
                                break
                    if assigned:
                        break
            
            if not assigned:
                print(f"Warning: Could not assign even course {code}")

    def _process_odd_courses(self, routine, teacher_schedule, teacher_short_names):
        """Sequential assignment for odd courses"""
        for course in [c for c in self.courses if not self._is_even_course(c["code"])]:
            teacher = course["teacher"]
            year = course["year"]
            code = course["code"]
            credit = course["credit"]
            assigned_slots = 0
            
            # Try preferences first
            if teacher in self.teacher_priorities:
                for pref in self.teacher_priorities[teacher]["slots"]:
                    try:
                        day, time_range = pref.split(" ", 1)
                        slots = self._parse_time_range(time_range)
                        for slot in slots:
                            if assigned_slots >= credit:
                                break
                            if self._can_assign(teacher, year, day, slot, routine, teacher_schedule):
                                routine[year][day][slot] = (code, teacher_short_names[teacher])
                                teacher_schedule[teacher][day].add(slot)
                                assigned_slots += 1
                    except (ValueError, IndexError):
                        continue
            
            # Fill remaining slots if needed
            if assigned_slots < credit:
                for day in DAYS:
                    for slot in SLOTS:
                        if assigned_slots >= credit:
                            break
                        if self._can_assign(teacher, year, day, slot, routine, teacher_schedule):
                            routine[year][day][slot] = (code, teacher_short_names[teacher])
                            teacher_schedule[teacher][day].add(slot)
                            assigned_slots += 1
            
            if assigned_slots < credit:
                print(f"Warning: Only assigned {assigned_slots}/{credit} slots for {code}")

    # Helper Methods
    def _is_even_course(self, code):
        numeric_part = ''.join(filter(str.isdigit, code))
        return int(numeric_part) % 2 == 0 if numeric_part else False

    def _assign_consecutive_slots(self, teacher, year, day, start_slot, code, 
                                routine, teacher_schedule, teacher_short_names):
        """Try to assign 3 consecutive slots"""
        for slot in range(start_slot, start_slot + 3):
            if not self._can_assign(teacher, year, day, slot, routine, teacher_schedule):
                return False
        
        for slot in range(start_slot, start_slot + 3):
            routine[year][day][slot] = (code, teacher_short_names[teacher])
            teacher_schedule[teacher][day].add(slot)
        return True

    def _can_assign(self, teacher, year, day, slot, routine, teacher_schedule):
        """Check if slot is available"""
        return (slot in SLOTS and 
                routine[year][day][slot] is None and 
                slot not in teacher_schedule[teacher][day])

    def _generate_teacher_short_names(self):
        return {teacher: ''.join([name[0].upper() for name in teacher.split()])
                for teacher in self.teachers}

    def _generate_schedule_text(self, routine):
        text = "Generated Schedule:\n\n"
        for year, days in routine.items():
            text += f"Year {year}:\n"
            for day, slots in days.items():
                text += f"  {day}:\n"
                for slot, data in slots.items():
                    if data:
                        text += f"    Slot {slot}: {data[0]} (Teacher: {data[1]})\n"
                    else:
                        text += f"    Slot {slot}: Free\n"
            text += "\n"
        return text

    def _create_pdf(self, routine, teacher_short_names):
        slot_times = {
            1: "9-10",
            2: "10-11",
            3: "11-12",
            4: "12-1",
            5: "1-2",
            6: "2-3",
            7: "3-4",
            8: "4-5"
        }
        
        # Main table data
        table_data = [["Day", "Year"] + [slot_times[s] for s in SLOTS]]
        year_names = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

        for day in DAYS:
            for yr in [1, 2, 3, 4]:
                row = [day if yr == 1 else "", year_names[yr - 1]]
                for s in SLOTS:
                    if s == 5:
                        row.append("Break")
                    else:
                        data = routine[yr][day][s]
                        row.append(f"{data[0]}\n({data[1]})" if data else "")
                table_data.append(row)

        # Teacher reference table
        teacher_table_data = [["Short Name", "Full Name"]]
        for teacher, short_name in teacher_short_names.items():
            teacher_table_data.append([short_name, teacher])

        # Create PDF
        pdf = SimpleDocTemplate("routine_final.pdf", pagesize=landscape(letter))
        
        # Style main table
        main_table = Table(table_data, colWidths=[70, 90] + [80] * len(SLOTS))
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.whitesmoke]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Style teacher table
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

        spacer = Spacer(1, 20)
        pdf.build([main_table, spacer, teacher_table])
        messagebox.showinfo("PDF Generated", "Routine saved as 'routine_final.pdf'.")

    # Utility Methods
    def validate_float_input(self, value):
        try:
            if value == "":
                return True
            float(value)
            return True
        except ValueError:
            return False

    def update_teacher_combo(self):
        self.teacher_combo["values"] = self.teachers

    def remove_course(self):
        messagebox.showinfo("Remove Course", "Feature not implemented yet.")

    def clear_course_entries(self):
        self.course_code_entry.delete(0, tk.END)
        self.course_name_entry.delete(0, tk.END)
        self.year_spinbox.set(1)
        self.credit_spinbox.delete(0, tk.END)
        self.teacher_combo.set('')

    def update_schedule_info(self, schedule_text):
        self.schedule_label.config(text=schedule_text)

    def _parse_time_range(self, time_range):
        time_map = {
            "9am-10am": 1,
            "10am-11am": 2,
            "11am-12pm": 3,
            "12pm-1pm": 4,
            "1pm-2pm": 5,
            "2pm-3pm": 6,
            "3pm-4pm": 7,
            "4pm-5pm": 8
        }
        try:
            start, end = time_range.split("-")
            slots = [slot for time, slot in time_map.items() 
                    if time.startswith(start) or time.endswith(end)]
            if not slots:
                raise KeyError(f"Invalid time range: {time_range}")
            return slots
        except KeyError as e:
            messagebox.showerror("Error", f"Invalid time range: {e}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSchedulerApp(root)
    root.mainloop()