from tkinter import *
import datetime
import time as t
import sqlite3 as s3
import os
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.animation as animation
style.use("dark_background")

class App:
    def __init__(self, master):
        self.db = Database(r"./tasktimer.db")
        self.master = master
        self.master.title("Task Timer")
        self.master.configure(bg="#333")
        self.master.resizable(False, False)
        self.tool = Tools(self.master)
        self.run_timer = False
        self.task = None
        self.now = datetime.datetime.now()
        self.day = self.now.day
        self.month = self.now.month
        self.year = self.now.year

        main_frame = Frame(self.master, bg="#333")
        main_frame.grid(row=0, column=0, padx=20, pady=15)

        # Main Frame ===================================================
        left_frame = Frame(main_frame, bg="#333")
        right_frame = Frame(main_frame, bg="#333")

        left_frame.pack(side=LEFT, padx=(0,16))
        right_frame.pack()

        # Left Frame ===================================================
        select_task_label = Label(left_frame, text="Select Task", font=('Arial', 14, 'bold'), bg="#333", fg="#efefef")
        task_picker_frame = Frame(left_frame)
        task_picker_scrollbar = Scrollbar(task_picker_frame)
        self.task_picker = Listbox(task_picker_frame, height=15, width=20, font=('Arial', 13), justify=CENTER, yscrollcommand=task_picker_scrollbar.set)
        task_picker_scrollbar.config(command=self.task_picker.yview)
        task_picker_button_frame = Frame(left_frame)

        width = 8
        add_task_button = Button(task_picker_button_frame, text="Add", width=width)
        rename_task_button = Button(task_picker_button_frame, text="Rename", width=width)
        remove_task_button = Button(task_picker_button_frame, text="Remove", width=width)

        # Bind
        add_task_button.bind('<Button-1>', self.add_task)
        rename_task_button.bind('<Button-1>', self.rename_task)
        remove_task_button.bind('<Button-1>', self.remove_task)
        self.task_picker.bind('<<ListboxSelect>>', self.change_task_info)

        select_task_label.grid(row=0, column=0, pady=(0,5))
        task_picker_frame.grid(row=1, column=0)
        self.task_picker.pack(side=LEFT, fill=BOTH)
        task_picker_scrollbar.pack(side=RIGHT, fill=Y)
        task_picker_button_frame.grid(row=2, column=0, pady=(15,0))
        add_task_button.grid(row=0, column=0)
        rename_task_button.grid(row=0, column=1)
        remove_task_button.grid(row=0, column=2)

        # Right Frame ===================================================
        timer_frame = Frame(right_frame, bg="#333")
        graph_frame = Frame(right_frame, bg="#333")

        timer_frame.grid(row=0, column=0)
        graph_frame.grid(row=1, column=0)

        # Right Top Frame ==================
        self.task_info = StringVar()
        self.task_info.set("Task Info: Select Task")
        self.timer_count = StringVar()
        self.timer_count.set("00:00:00")
        self.total_time = StringVar()
        self.total_time.set("Total Time: ")
        self.monthly_time = StringVar()
        self.monthly_time.set("Monthly Time: ")
        self.last_used = StringVar()
        self.last_used.set("Last Used: ")
        self.monthly_rank = StringVar()
        self.monthly_rank.set("Monthly Rank: ")

        task_info_label = Label(timer_frame, textvariable=self.task_info, font=('Arial', 14, 'bold'), bg="#333", foreground="#efefef")
        timer_count_frame = Frame(timer_frame, bg="#333")
        self.start_button = Button(timer_count_frame, width=8, text="START", font=('Arial', 11), command=self.start_timer)
        pause_button = Button(timer_count_frame, width=6, text="STOP", font=('Arial', 11), command=self.stop_timer)
        self.reset_button = Button(timer_count_frame, width=6, text="RESET", font=('Arial', 11), command=self.reset_timer)
        timer_counter_label = Label(timer_count_frame, textvariable=self.timer_count, font=('Arial', 19), bg="#333", foreground="#efefef")
        self.save_button = Button(timer_count_frame, width=6, text="SAVE", font=('Arial', 11), command=self.save_timer)
        task_info_frame = Frame(timer_frame, bg="#333")
        total_time_label = Label(task_info_frame, textvariable=self.total_time, font=('Arial', 13), bg="#333", foreground="#efefef")
        monthly_time_label = Label(task_info_frame, textvariable=self.monthly_time, font=('Arial', 13), bg="#333", foreground="#efefef")
        last_used_label = Label(task_info_frame, textvariable=self.last_used, font=('Arial', 13), bg="#333", foreground="#efefef")
        monthly_rank_label = Label(task_info_frame, textvariable=self.monthly_rank, font=('Arial', 13), bg="#333", foreground="#efefef")

        task_info_label.grid(row=0, column=0, pady=(0,5))
        timer_count_frame.grid(row=1, column=0, pady=(5,10))
        self.start_button.grid(row=0, column=0, padx=5)
        pause_button.grid(row=0, column=1, padx=5)
        self.reset_button.grid(row=0, column=2, padx=5)
        timer_counter_label.grid(row=0, column=3, padx=10)
        self.save_button.grid(row=0, column=4, padx=5)
        task_info_frame.grid(row=2, column=0)
        total_time_label.grid(row=0,column=0, padx=(0,50), pady=(0,5))
        monthly_time_label.grid(row=0, column=1, pady=(0,5))
        last_used_label.grid(row=1, column=0, padx=(0,50))
        monthly_rank_label.grid(row=1, column=1)

        # Right Bottom Frame ==================
        graph_label = Label(graph_frame, text="Monthly Progress Graph", font=('Arial', 14, 'bold'), bg="#333", foreground="#efefef")

        self.monthly_time_fig = Figure(figsize=(6.03, 3.01), dpi=75)
        self.monthly_time_graph = self.monthly_time_fig.add_subplot(111)
        self.monthly_time_fig.subplots_adjust(left=0.096, right=0.97, top=0.92, bottom=0.17)
        self.monthly_time_fig.patch.set_facecolor(('#333333'))
        time_canvas = FigureCanvasTkAgg(self.monthly_time_fig, graph_frame)
        time_canvas.draw()

        graph_label.grid(row=0, column=0, pady=(10,0))
        time_canvas.get_tk_widget().grid(row=1, column=0, sticky=W+E+N+S)

        self.initialize()

        # self.tool.set_window_size(900, 500)

    def initialize(self):
        self.task_picker.insert(END,'')

        self.db.raw_execute("SELECT taskName FROM taskList ORDER BY taskId ASC")
        all_tasks = self.db.fetchall()
        task_list = []
        for task in all_tasks:
            task_list.append(str(task[0]))

        for task in task_list:
            self.task_picker.insert(END, self.tool.from_database(task))
            self.task_picker.insert(END, '')

    def change_task_info(self, event=""):
        if len(self.task_picker.curselection()) > 0:
            picked_task_index = self.task_picker.curselection()
            task_name = self.task_picker.get(picked_task_index)
            self.task = task_name

            if len(task_name) < 1:
                task_name = "Select Task"
                self.total_time.set("Total Time: ")
                self.monthly_time.set("Monthly Time: ")
                self.last_used.set("Last Used: ")
                self.monthly_rank.set("Monthly Rank: ")

            self.task_info.set("Task Info: %s" % task_name)

        if self.task is not "Select Task" and self.task is not "":
            self.total_time.set("Total Time: %s" % self.get_total_time())
            self.monthly_time.set("Monthly Time: %s" % self.get_monthly_time())
            self.last_used.set("Last Used: %s" % self.get_last_used())
            self.monthly_rank.set("Monthly Rank: %d" % self.get_monthly_rank())


    def get_total_time(self):
        task_id = self.get_id(self.task)

        self.db.select("log", "time", "taskId = %d" % task_id)

        seconds_list = self.db.fetchall()
        total_seconds = 0

        for seconds in seconds_list:
            total_seconds += seconds[0]

        return self.tool.to_time(total_seconds)

    def get_monthly_time(self):
        task_id = self.get_id(self.task)

        #Get logs in the current month only
        latest_month_dates = self.get_dates_month()

        #Get total time for a task
        seconds = 0
        for date in latest_month_dates:
            self.db.select('log', 'time', "logDate='%s' AND taskId='%s'" % (date[0], task_id))
            times = self.db.fetchall()
            for time in times:
                seconds += time[0]

        return self.tool.to_time(seconds)

    def get_last_used(self):
        task_id = self.get_id(self.task)

        self.db.select('log', 'logDate', "taskId = %d" % task_id)
        raw_date_list = self.db.fetchall()
        date_list = [d[0] for d in raw_date_list]
        datetime_list = []
        for date in date_list:
            time_split = date.split("-")
            datetime_list.append(datetime.date(int(time_split[0]), int(time_split[1]), int(time_split[2])))

        if len(datetime_list) < 1:
            last_date = "Never Used"
        else:
            last_date = max(d for d in datetime_list if isinstance(d, datetime.date))

        return last_date

    def get_monthly_rank(self):
        self.db.raw_execute("SELECT taskName FROM taskList ORDER BY taskId ASC")
        all_tasks = self.db.fetchall()
        task_list = []
        for task in all_tasks:
            task_list.append(str(task[0]))

        task_id = self.get_id(self.task)

        latest_month_dates = self.get_dates_month()

        all_task_time = {}

        for task in task_list:
            seconds = 0
            for date in latest_month_dates:
                self.db.select('log', 'time', "logDate='%s' AND taskId=%d" % (date[0], self.get_id(task)))
                times = self.db.fetchall()
                for time in times:
                    seconds += time[0]
            all_task_time[task] = seconds


        sorted_task = sorted(all_task_time, key=lambda x: all_task_time[x], reverse=True)

        monthly_rank = {}
        rank = 1

        if len(sorted_task) > 0:
            monthly_rank[sorted_task[0]] = rank
            for i in range(1, len(sorted_task)):
                if all_task_time[sorted_task[i-1]] > all_task_time[sorted_task[i]]:
                    rank += 1
                monthly_rank[sorted_task[i]] = rank


        if len(monthly_rank) == 0:
            return 0
        else:
            return monthly_rank[self.tool.to_database(self.task)]

    def start_timer(self):
        self.run_timer = True
        self.first_second = True
        self.start_button.config(state=DISABLED)
        self.task_picker.config(state=DISABLED)
        self.reset_button.config(state=DISABLED)
        self.save_button.config(state=DISABLED)
        self.start_button.config(text='RESUME')
        self.loop_timer()

    def loop_timer(self):
        self.timer_on = True
        self.timer()

    def stop_timer(self):
        self.run_timer = False
        self.start_button.config(state=NORMAL)
        self.reset_button.config(state=NORMAL)
        self.save_button.config(state=NORMAL)
        self.start_button.config(text='RESUME')

    def reset_timer(self):
        self.run_timer = False
        self.timer_count.set("00:00:00")
        self.start_button.config(state=NORMAL)
        self.task_picker.config(state=NORMAL)
        self.start_button.config(text='START')

    def timer(self):
        if self.run_timer == True:
            time = self.timer_count.get()
            h, m, s = map(int, time.split(":"))

            if not self.first_second:
                if s < 59:
                    s += 1
                else:
                    s = 0
                    if m < 59:
                        m += 1
                    else:
                        m = 0
                        h += 1
            else:
                t.sleep(0.09)
                self.first_second = False

            if h < 10:
                h = str(0) + str(h)
            else:
                h = str(h)

            if m < 10:
                m = str(0) + str(m)
            else:
                m = str(m)

            if s < 10:
                s = str(0) + str(s)
            else:
                s = str(s)

            time = "%s:%s:%s" % (h, m, s)
            self.timer_count.set(time)

            if self.run_timer == True:
                self.master.after(999, self.loop_timer)

    def save_timer(self):
        if self.run_timer == False:
            time = self.timer_count.get()

            self.save_time_popup = Toplevel(self.master)
            self.save_time_popup.title("Save Time")
            self.save_time_popup.config(bg="#333")
            self.tool.center(self.save_time_popup)

            save_task_label = Label(self.save_time_popup, text="Save %s to %s" % (time, self.task), bg="#333", foreground="#efefef", font=('Arial', 13))

            hms_frame = Frame(self.save_time_popup, bg="#333")
            self.hour_var = StringVar()
            self.min_var = StringVar()
            self.sec_var = StringVar()

            hour_entry = Entry(hms_frame, textvariable=self.hour_var, width=2, font=('Arial', 13))
            min_entry = Entry(hms_frame, textvariable=self.min_var, width=2, font=('Arial', 13))
            sec_entry = Entry(hms_frame, textvariable=self.sec_var, width=2, font=('Arial', 13))

            hour_label = Label(hms_frame, text="h", bg="#333", foreground="#efefef", font=('Arial', 13))
            min_label = Label(hms_frame, text="m", bg="#333", foreground="#efefef", font=('Arial', 13))
            sec_label = Label(hms_frame, text="s", bg="#333", foreground="#efefef", font=('Arial', 13))

            time_split = time.split(':')

            self.hour_var.set(time_split[0])
            self.min_var.set(time_split[1])
            self.sec_var.set(time_split[2])

            save_button = Button(self.save_time_popup, text='Save Time', width=20, command=self.save_time_to_app)

            save_task_label.grid(row=0, column=0, pady=10, padx=15)
            hms_frame.grid(row=1, column=0, pady=(0,10), padx=50)
            hour_entry.grid(row=0, column=0)
            hour_label.grid(row=0, column=1, padx=(0,10))
            min_entry.grid(row=0, column=2)
            min_label.grid(row=0, column=3, padx=(0,10))
            sec_entry.grid(row=0, column=4)
            sec_label.grid(row=0, column=5)
            save_button.grid(row=2, column=0, pady=(10))

            self.save_time_popup.resizable(False, False)

    def save_time_to_app(self):
        try:
            time = self.hour_var.get() + ":" + self.min_var.get() + ":" + self.sec_var.get()
            seconds = self.tool.to_seconds(time)

            self.db.select('taskList', 'taskId', "taskName = '%s'" % self.tool.to_database(self.task))
            task_id = int(self.db.fetchone()[0])

            self.db.select('log', 'MAX(logId)')
            logId = self.db.fetchone()[0]

            if logId == None:
                self.db.insert('log', 'taskId, logId, time, logDate', "%d, %d, %d, '%s'" % (task_id, 1, seconds, datetime.date.today()))
            else:
                self.db.insert('log', 'taskId, logId, time, logDate', "%d, %d, %d, '%s'" % (task_id, logId+1, seconds, datetime.date.today()))

            self.save_time_popup.destroy()
            self.task_picker.config(state=NORMAL)
            self.start_button.config(text='START')
            self.change_task_info()
            self.timer_count.set("00:00:00")
        except Exception as e:
            print(str(e))

    def add_task(self, event):
        self.add_task_popup = Toplevel(self.master)
        self.add_task_popup.title("Add Task")
        self.tool.center(self.add_task_popup)
        self.add_task_popup.config(bg="#333")

        add_task_label = Label(self.add_task_popup, text="Enter Task Name", bg="#333", foreground="#efefef", font=('Arial', 13))
        self.add_task_entry = Entry(self.add_task_popup, width=30, justify=CENTER)
        add_task_button = Button(self.add_task_popup, text="Add Task", width=18)

        self.add_task_entry.bind('<Return>', self.add_task_to_app)
        add_task_button.bind('<Button-1>', self.add_task_to_app)

        add_task_label.pack(pady=10)
        self.add_task_entry.pack()
        add_task_button.pack(padx=50, pady=(12,10))

        self.add_task_popup.resizable(False, False)

    def add_task_to_app(self, event):
        task_name = self.add_task_entry.get()
        self.add_task_entry.delete(0, END)
        self.add_task_popup.destroy()
        self.task_picker.insert(END, task_name)
        self.task_picker.insert(END, '')

        self.db.select('taskList', 'MAX(taskId)')
        max_id = self.db.fetchone()[0]

        if max_id == None:
            self.db.insert('taskList', 'taskId, taskName', "1, '%s'" % (self.tool.to_database(task_name)))
        else:
            self.db.insert('taskList', 'taskId, taskName', "%d, '%s'" % (max_id+1, self.tool.to_database(task_name)))

    def rename_task(self, event):
        self.rename_task_popup = Toplevel(self.master)
        self.rename_task_popup.title("Rename Task")
        self.tool.center(self.rename_task_popup)
        self.rename_task_popup.config(bg="#333")

        picked_task_index = self.task_picker.curselection()
        task_name = self.task_picker.get(picked_task_index)

        rename_task_label = Label(self.rename_task_popup, text="Rename %s to" % task_name, bg="#333", foreground="#efefef", font=('Arial', 13))
        self.rename_task_entry = Entry(self.rename_task_popup, width=30, justify=CENTER)
        rename_task_button = Button(self.rename_task_popup, text="Rename Task", width=20)

        self.rename_task_entry.bind('<Return>', self.rename_task_to_app)
        rename_task_button.bind('<Button-1>', self.rename_task_to_app)

        rename_task_label.pack(pady=10)
        self.rename_task_entry.pack()
        rename_task_button.pack(padx=50, pady=(12,10))

        self.rename_task_popup.resizable(False, False)

    def rename_task_to_app(self, event):
        picked_task_index = self.task_picker.curselection()
        task_name = self.task_picker.get(picked_task_index)
        renamed_task_name = self.rename_task_entry.get()

        self.task_picker.delete(picked_task_index)
        self.task_picker.insert(picked_task_index, renamed_task_name)

        self.db.update('taskList', "taskName = '%s'" % self.tool.to_database(renamed_task_name), "taskName = '%s'" % self.tool.to_database(task_name))

        self.rename_task_popup.destroy()

    def remove_task(self, event):
        picked_task_index = self.task_picker.curselection()
        task_name = self.task_picker.get(picked_task_index)

        if len(task_name) >= 1:
            self.remove_task_popup = Toplevel(self.master)
            self.remove_task_popup.title("Remove Task")
            self.tool.center(self.remove_task_popup)
            self.remove_task_popup.config(bg="#333")

            remove_task_label = Label(self.remove_task_popup, text="Are you sure you would like to remove %s?" % task_name, bg="#333", foreground="#efefef", font=('Arial', 13))

            remove_task_button_frame = Frame(self.remove_task_popup, bg="#333")
            remove_task_button_yes = Button(remove_task_button_frame, text="Yes", width=10)
            remove_task_button_no = Button(remove_task_button_frame, text="No", width=10)

            remove_task_button_yes.bind('<Button-1>', self.remove_task_yes)
            remove_task_button_no.bind('<Button-1>', self.remove_task_no)

            remove_task_label.grid(row=0, column=0, padx=(10,10), pady=(10,10))
            remove_task_button_frame.grid(row=1, column=0, pady=(0,15))
            remove_task_button_yes.grid(row=0,column=0, padx=(0,20))
            remove_task_button_no.grid(row=0,column=1)

            self.remove_task_popup.resizable(False, False)

    def remove_task_yes(self, event):
        picked_task_index = self.task_picker.curselection()[0]
        # task_name = self.task_picker.get(picked_task_index)

        self.task_picker.delete(picked_task_index)
        self.task_picker.delete(picked_task_index)

        self.db.delete('log', "taskId = %d" % self.get_id(self.tool.to_database(self.task)))
        self.db.delete('taskList', "taskName = '%s'" % self.tool.to_database(self.task))

        self.remove_task_popup.destroy()

    def remove_task_no(self, event):
        self.remove_task_popup.destroy()

    def update_monthly_time_graph(self, i):
        self.monthly_time_graph.clear()

        latest_month_dates = self.get_dates_month()
        # print(latest_month_dates)

        # date_time_dict = {}
        day_list = []
        time_list = []

        try:
            for date in latest_month_dates:
                seconds = 0
                self.db.select('log', 'time', "logDate='%s' AND taskId=%d" % (date[0], self.get_id(self.task)))
                times = self.db.fetchall()
                for time in times:
                    seconds += time[0]
                date_split = date[0].split('-')
                day = date_split[2]
                day_list.append(day)
                time_list.append(seconds/60)
                # date_time_dict[day] = seconds
        except Exception as e:
            pass

        self.monthly_time_graph.set_xlabel("Time (Day)")
        self.monthly_time_graph.set_ylabel("Time (min)")
        self.monthly_time_graph.plot(day_list, time_list, marker='+')

    def get_id(self, task_name):
        self.db.select('taskList', 'taskId', "taskName = '%s'" % self.tool.to_database(task_name))
        task_id = int(self.db.fetchone()[0])

        return task_id

    def get_dates_month(self):
        self.db.raw_execute('SELECT DISTINCT logDate FROM log ORDER BY logId ASC LIMIT 31')
        raw_latest_dates = self.db.fetchall()
        latest_month_dates = []

        for date in raw_latest_dates:
            time_split = date[0].split('-')
            if int(time_split[0]) == self.year and int(time_split[1]) == self.month:
                latest_month_dates.append(date)

        return latest_month_dates

class Tools:
    def __init__(self, master):
        self.master = master

    def set_window_size(self, width, height, window=None):
        if window is not None:
            self.master = window
        w = width
        h = height
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.master.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def center(self, window):
        w = window.winfo_reqwidth()
        h = window.winfo_reqheight()
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws / 2) - w / 2
        y = (hs / 2) - h / 2
        window.geometry("+%d+%d" % (x, y))

    def to_database(self, string):
        string_split = string.split(' ')

        for i in range(len(string_split)):
            string_split[i] = string_split[i].lower()

        new_string = '_'.join(string_split)
        return new_string

    def from_database(self, string):
        string_split = string.split('_')

        for i in range(len(string_split)):
            string_split[i] = string_split[i][0].upper() + string_split[i][1:]

        new_string = ' '.join(string_split)
        return new_string

    def to_seconds(self, string):
        time_split = string.split(':')
        seconds = int(time_split[0]) * 3600 + int(time_split[1]) * 60 + int(time_split[2])
        return seconds

    def to_time(self, seconds):
        time = seconds
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        return "%d:%d:%d:%d" % (day, hour, minutes, seconds)

class Database:
    def __init__(self, database):
        self.connection = s3.connect(database)
        self.cursor = self.connection.cursor()

        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS taskList(taskId INT PRIMARY KEY, taskName VARCHAR(20));")

            self.cursor.execute("CREATE TABLE IF NOT EXISTS log(taskId INT, logId INT, time INT, logDate TEXT);")

            self.connection.commit()
            print("Connection Successful")
        except:
            self.connection.rollback()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, query, command):
        try:
            self.cursor.execute(query)
            self.connection.commit()

        except Exception as e:
            if command == "select":
                print("Select Failed:", str(e))
            elif command == "insert":
                print("Insert Failed:", str(e))
            elif command == "update":
                print("Update Failed:", str(e))
            elif command == "delete":
                print("Delete Failed:", str(e))
            else:
                pass
            self.connection.rollback()

    def raw_execute(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def select(self, table, columns, conditions=""):
        query = ""
        if conditions != "":
        	query = "SELECT %s FROM %s WHERE %s;" % (columns, table, conditions)
        else:
        	query = "SELECT %s FROM %s;" % (columns, table)
        self.execute(query, "select")

    def insert(self, table, columns, arguments):
        query = "INSERT INTO %s (%s) VALUES (%s);" % (table, columns, arguments)
        self.execute(query, "insert")

    def update(self, table, change, conditions=""):
        query = ""
        if conditions != "":
            query = "UPDATE %s SET %s WHERE %s" % (table, change, conditions)
        else:
            query = "UPDATE %s SET %s" % (table, change)
        self.execute(query, "update")

    def delete(self, table, conditions=""):
        query = ""
        if conditions != "":
            query = "DELETE FROM %s WHERE %s" % (table, conditions)
        else:
            query = "DELETE FROM %s" % (table)
        self.execute(query, "delete")

    def __del__(self):
        self.connection.close()

if __name__ ==  "__main__":
    root = Tk()
    app = App(root)
    monthly_time_graph = animation.FuncAnimation(app.monthly_time_fig, app.update_monthly_time_graph, interval=1000)
    root.mainloop()
