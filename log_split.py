import csv, datetime

def gt(dt_str):
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us= int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)

logs = []

name = 'sf_10000_test_1_5s'
with open(name + '.csv', newline='\n') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

  for row in spamreader:

    logs.append(row)

lens = [len(logs)/2, len(logs)]

num = 0
for i in range(len(lens)):

  with open('%s_%s.csv' % (name, i), 'w', newline='') as csvfile:
      
      spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

      while num < lens[i]:
        spamwriter.writerow(logs[num])
        num += 1

      