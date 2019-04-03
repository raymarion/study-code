# coding=utf-8
import csv
import datetime
import Tkinter
from Tkinter import *
import tkinter.filedialog
import xlrd
import xlwt
# from xlwt import Worksheet
import sys
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')



def read_schedule_file(schedule_file_name):
    # TODO: consider the day and night works back to back
    workbook = xlrd.open_workbook(schedule_file_name)

    sheet_names = workbook.sheet_names()

    # sheet_name = sheet_names[0]

    schedule_sheet = workbook.sheet_by_index(0)

    # print schedule_sheet.nrows
    schedule_dict = {}
    # change dict to 2 leyer dict with key of user and date

    for r in range(1, schedule_sheet.nrows-1):
        row = schedule_sheet.row_values(r)
        name = row[3].replace(" ", "")
        if name not in schedule_dict:
            schedule_dict[name] = {}
        row_clean = []
        for c in row:
            if type(c) == float:
                row_clean.append(parse_time_from_float(c))
            else:
                row_clean.append(c)
        if row_clean[5] < row_clean[4]:
            row_clean.append("N")
        else:
            row_clean.append("D")

        schedule_dict[name][row[0]] = row_clean
    #{name:{date:[row clean]}}
    # print schedule_list
    #
    return schedule_dict
    #  dict is good





def parse_time_from_float(f_time):
    hour = int(f_time * 24)
    minute = int(round((f_time * 24 - hour)*60))
    if minute == 60:
        hour = hour + 1
        minute = 0
    return u'{:0=2}'.format(hour) + u":" + u'{:0=2}'.format(minute)


def read_file(filename):
    with codecs.open(filename, 'r', encoding='gb2312') as csvfile:
        reader = csv.reader(csvfile)
        list = []
        for row in reader:
            if row.__len__() == 5 and row[3].__len__() > 15:
                list.append(row)
        return list



def read_records_file(filename):
    #  read records file and output 2 dict of user info and user records with key of name
    row_list = read_file(filename)
    users_records = {}
    users_info = {}
    for row in row_list:
        name = unicode(row[2]).replace(" ", "")
        if not name in users_info:
            users_info[name] = (row[0], row[1])
    for row in row_list:
        name = unicode(row[2]).replace(" ", "")
        if not name in users_records:
            users_records[name] = []
        users_records[name].append(parse_date_time(row[3]))
    # users_records: {name: [date, date_time]}
    return users_info, users_records


def parse_time(time_str):
    time_format = "%m/%d/%Y %I:%M:%S %p"
    return datetime.datetime.strptime(time_str, time_format)


def parse_date_time(time_str):
    time_format = "%m/%d/%Y %I:%M:%S %p"
    date_time = datetime.datetime.strptime(time_str, time_format)
    date_format = "%Y-%m-%d"
    return date_time.strftime(date_format), date_time


def time_str(time):
    time_format = "%m/%d/%Y %I:%M:%S %p"
    return time.strftime(time_format)


def day_before(date):
    date_format = "%Y-%m-%d"
    return (datetime.datetime.strptime(date, date_format)-datetime.timedelta(days=1)).strftime(date_format)


def time_span(start, end):
    time_format = "%Y-%m-%d %H:%M:%S"
    return (datetime.datetime.strptime(end, time_format) - datetime.datetime.strptime(start, time_format)).total_seconds()/3600


def is_normal_work(start_time, end_time):
    timespan = (end_time - start_time).total_seconds()
    # print(end_time.date())
    dayspan = (end_time.date() - start_time.date()).days
    # print(dayspan)
    if timespan > 24*3600:
        return -2
    if timespan < 3600:
        return -1
    if dayspan == 0:
        return 1
    if dayspan == 1:
        return 2
    return 0


def compute_work_hours(start_time, end_time, work_type):
    if work_type == 1:
        return ((end_time - start_time).total_seconds()-3600)/3600.0
    if work_type == 2:
        return ((end_time - start_time).total_seconds() + 3600) / 3600.0
    return 0


def process_records(records):
    processed_list = []
    records.sort()
    last_time = None
    for r in records:
        if last_time is None:
            last_time = r
            continue
        work_type = is_normal_work(last_time, r)
        if work_type <= 0:
            processed_list.append((last_time, last_time, 0, work_type))
            last_time = r
            continue
        if work_type > 0:
            processed_list.append((last_time, r, compute_work_hours(last_time, r, work_type), work_type))
            last_time = None
    return processed_list


def match_schedule_time(date, schedule_time, record_time):
    schedule_format = "%Y-%m-%d %H:%M"
    schedule_time = datetime.datetime.strptime(date + " " + schedule_time, schedule_format)
    minutes_gap = (record_time - schedule_time).total_seconds()/60
    return minutes_gap


def match_records_schedule(schedule_dict, users_records_dict):
    # todo: with sorted list for consider works day and night in same date
    ## schedule_dict {name:{date:[row clean]}}
    ## users_records: {name: [date, date_time]}
    result_dict = {}
    err_list = []
    for user in schedule_dict:
        if user not in result_dict:
            result_dict[user] = {}
        for date in schedule_dict[user]:
            if date not in result_dict[user]:
                work_dict = {'start': 'None', 'start_late': 'None', 'end': 'None', 'end_early': 'None', 'hours': 0.0,
                             'type': schedule_dict[user][date][6]}
                result_dict[user][date] = work_dict
    for user, records in users_records_dict.items():
        if user not in schedule_dict:
            for r in records:
                date = r[0]
                date_time = r[1]
                err_list.append((user, date, date_time.strftime("%Y-%m-%d %H:%M:%S")))
            continue

        for r in records:
            date = r[0]
            date_time = r[1]
            # find start time
            if date in schedule_dict[user]:
                if date not in result_dict[user]:
                    result_dict[user][date] = {}
                    result_dict[user][date]['type'] = schedule_dict[user][date][6]
                minute_gap_start = match_schedule_time(date, schedule_dict[user][date][4], date_time)
                if -240 <= minute_gap_start <= 240:
                    if result_dict[user][date]['start'] == 'None':
                        result_dict[user][date]['start'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                        if minute_gap_start <= 0:
                            result_dict[user][date]['start_late'] = 'N'
                        else:
                            result_dict[user][date]['start_late'] = 'Y'
                    elif result_dict[user][date]['start'] > date_time.strftime("%Y-%m-%d %H:%M:%S"):
                        result_dict[user][date]['start'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                        if minute_gap_start <= 0:
                            result_dict[user][date]['start_late'] = 'N'
                        else:
                            result_dict[user][date]['start_late'] = 'Y'
                    continue

                elif schedule_dict[user][date][6] == "D":
                    minute_gap_end = match_schedule_time(date, schedule_dict[user][date][5], date_time)
                    if -240 <= minute_gap_end <= 420:
                        if result_dict[user][date]['end'] == 'None':
                            result_dict[user][date]['end'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                            if minute_gap_end >= 0:
                                result_dict[user][date]['end_early'] = 'N'
                            else:
                                result_dict[user][date]['end_early'] = 'Y'
                        elif result_dict[user][date]['end'] < date_time.strftime("%Y-%m-%d %H:%M:%S"):
                            result_dict[user][date]['end'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                            if minute_gap_end >= 0:
                                result_dict[user][date]['end_early'] = 'N'
                            else:
                                result_dict[user][date]['end_early'] = 'Y'
                        continue
            # find end time
            if day_before(date) in schedule_dict[user] and schedule_dict[user][day_before(date)][6] == "N":
                minute_gap_end = match_schedule_time(date, schedule_dict[user][day_before(date)][5], date_time)
                if -240 <= minute_gap_end <= 240:
                    if result_dict[user][day_before(date)]['end'] == 'None':
                        result_dict[user][day_before(date)]['end'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                        if minute_gap_end >= 0:
                            result_dict[user][day_before(date)]['end_early'] = 'N'
                        else:
                            result_dict[user][day_before(date)]['end_early'] = 'Y'
                    elif result_dict[user][day_before(date)]['end'] < date_time.strftime("%Y-%m-%d %H:%M:%S"):
                        result_dict[user][day_before(date)]['end'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
                        if minute_gap_end >= 0:
                            result_dict[user][day_before(date)]['end_early'] = 'N'
                        else:
                            result_dict[user][day_before(date)]['end_early'] = 'Y'
                    continue

            err_list.append((user, date, date_time.strftime("%Y-%m-%d %H:%M:%S")))

    users_summary_dict = {}
    for user in result_dict:
        users_total = 0
        for date in result_dict[user]:
            work_dict = result_dict[user][date]
            if work_dict['start'] != 'None' and work_dict['end'] != 'None':
                timespan = time_span(work_dict['start'], work_dict['end'])
                if work_dict['type'] == "N":
                    work_dict['hours'] = timespan + 1
                else:
                    work_dict['hours'] = timespan - 1
                users_total = users_total + work_dict['hours']

        users_summary_dict[user] = users_total




    return result_dict, users_summary_dict, err_list



def output_result(result_dict, users_summary_dict, err_list, output_dir_name):
    if output_dir_name is "":
        output_dir_name = "."
    workbook = xlwt.Workbook()
    sheet_result = workbook.add_sheet("records")
    row = 1
    sheet_result.write(0, 0, u'姓名')
    sheet_result.write(0, 1, u'日期')
    sheet_result.write(0, 2, u'上班时间')
    sheet_result.write(0, 3, u'下班时间')
    sheet_result.write(0, 4, u'上班迟到')
    sheet_result.write(0, 5, u'下班早退')
    sheet_result.write(0, 6, u'早晚班')
    sheet_result.write(0, 7, u'工时')

    result_sort_list = [(k, [(d, result_dict[k][d]) for d in sorted(result_dict[k].keys())] ) for k in sorted(result_dict.keys())]
    for user in result_sort_list:
        for date in user[1]:
            sheet_result.write(row, 0, user[0])
            sheet_result.write(row, 1, date[0])
            sheet_result.write(row, 2, date[1]['start'])
            sheet_result.write(row, 3, date[1]['end'])
            sheet_result.write(row, 4, date[1]['start_late'])
            sheet_result.write(row, 5, date[1]['end_early'])
            sheet_result.write(row, 6, date[1]['type'])
            sheet_result.write(row, 7, date[1]['hours'])
            row = row + 1

    sheet_summary = workbook.add_sheet("summary")
    row = 1
    sheet_summary.write(0, 0, u'姓名')
    sheet_summary.write(0, 1, u'总工时')
    for user, total in users_summary_dict.items():
        sheet_summary.write(row, 0, user)
        sheet_summary.write(row, 1, total)
        row = row + 1

    sheet_err = workbook.add_sheet("error")
    row = 1
    sheet_err.write(0, 0, u'姓名')
    sheet_err.write(0, 1, u'日期')
    sheet_err.write(0, 2, u'打卡时间')

    for i in err_list:
        sheet_err.write(row, 0, i[0])
        sheet_err.write(row, 1, i[1])
        sheet_err.write(row, 2, i[2])
        row = row + 1

    file_name = output_dir_name + "/result_"+datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")+".xls"
    workbook.save(file_name)
    return file_name


def process_files(raw_records_file_name, schedule_file_name, output_dir_name):
    # todo load files and compare records and schedule, compute the work pair mark time and work hours
    schedule_dict = read_schedule_file(schedule_file_name)
    users_info_dict, users_records_dict = read_records_file(raw_records_file_name)
    result_dict, users_summary_dict, err_list = match_records_schedule(schedule_dict, users_records_dict)
    out_file = output_result(result_dict, users_summary_dict, err_list, output_dir_name)
    return out_file



def button_click():
    raw_records_file_name = raw_records.get()
    schedule_file_name = schedule.get()
    output_dir_name = output_dir.get()
    # if output_dir_name is "":
    #     output_dir_name = default_dir
    out = process_files(raw_records_file_name, schedule_file_name, output_dir_name)
    Message(root, text=u"结果输出在"+out).pack()



def choose_file():
    filename = tkinter.filedialog.askopenfilename(filetypes=[("csv", "csv")])
    if filename != '':
        raw_records.delete(0, END)
        raw_records.insert(0, filename)


def choose_scd():
    filename = tkinter.filedialog.askopenfilename(filetypes=[("Excel", "xlsx")])
    if filename != '':
        schedule.delete(0, END)
        schedule.insert(0, filename)


def choose_dir():
    filename = tkinter.filedialog.askdirectory()
    if filename != '':
        output_dir.delete(0, END)
        output_dir.insert(0, filename)



if __name__ == "__main__":
    root = Tkinter.Tk(className='打卡汇总工具')
    w = 600
    h = 400
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))

    Label(root, text="打卡原始数据：").grid(row=0)

    raw_records = Entry(root)
    raw_records.grid(row=0, column=1, ipadx = 130)
    choose_file_btn = Button(root, text="选择", command=choose_file)
    choose_file_btn.grid(row=0, column=2)

    Label(root, text="排班表数据：").grid(row=1)
    schedule = Entry(root)
    schedule.grid(row=1, column=1, ipadx = 130)
    choose_scd_btn = Button(root, text="选择", command=choose_scd)
    choose_scd_btn.grid(row=1, column=2)

    Label(root, text="结果输出目录：").grid(row=2)
    output_dir = Entry(root)
    output_dir.grid(row=2, column=1, ipadx = 130)
    choose_dir_btn = Button(root, text="选择", command=choose_dir)
    choose_dir_btn.grid(row=2, column=2)

    Button(root, text=u'汇总打卡', command=button_click).grid(row=3, column=1)



    # text_box = Text(root)
    # text_box.grid(row=4, column=1, ipadx=130)
    # S = Scrollbar(root)
    # S.config(command=text_box.yview)
    # text_box.config(yscrollcommand=S.set)
    # S.grid(row=4, column=2)

    # name_label = Label(root, text=u"广告关键字：")
    # name_label.pack()
    # name_entry = Entry(root)
    # name_entry.insert(END, u"京东")
    # name_entry.pack()
    # time_label = Label(root, text=u"广告日期（yyyy-MM-dd）：")
    # time_label.pack()
    # time_entry = Entry(root)
    # time_entry.insert(END, '2018-07-14')
    # time_entry.pack()
    # v = IntVar()
    # v.set(0)
    # Radiobutton(root, text=u'启动页', variable=v, value=0).pack()
    # Radiobutton(root, text=u'首页图文', variable=v, value=1).pack()

    # button = Button(root, text=u'汇总打卡', command=button_click)
    # button.pack()
    # text_box = Text(root, height=200)
    # S = Scrollbar(root)
    # S.config(command=text_box.yview)
    # text_box.config(yscrollcommand=S.set)
    # S.pack(side=RIGHT, fill=Y)
    # text_box.pack(side=LEFT, fill=Y)
    root.mainloop()


    # parse_file("Record_181219102130126909.csv")
