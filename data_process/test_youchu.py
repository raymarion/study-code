import datetime

import youchu_attendance




def test_time_parse():
    time = youchu_attendance.parse_time("12/1/2018 7:49:00 PM")
    print(time)


def test_is_normal_work():
    print(youchu_attendance.is_normal_work(
        youchu_attendance.parse_time("11/30/2018 7:49:00 PM"),
        youchu_attendance.parse_time("12/1/2018 7:47:00 PM"))
    )

# test_time_parse()
test_is_normal_work()


# youchu_attendance.match_start_time("2019-03-04", "08:22", datetime.datetime.now())
print datetime.datetime.now()


dit = {"1": 1234, "2": 2131321}
dit['sds'] is None
print "i" in dit



