


ss = "2019-03-19T19:12:56.372+03:00"
import datetime

s = ss[0:19]
timestamp = datetime.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%S")

timestamp = timestamp + datetime.timedelta(hours=-int(ss[-6:-3]), minutes=-int(ss[-6:-5]+ss[-2:]))

print timestamp