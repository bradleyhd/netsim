import csv, datetime

def gt(dt_str):
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us= int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)

logs = []

with open('sf_10000_test_1.csv', newline='\n') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

  last_date = None
  total = 0
  car = 0
  i = 0
  for row in spamreader:

    d = gt(row[2].strip())

    if last_date is not None:

      diff = (d - last_date).total_seconds()
      # print('car %s' % car)
      # print('diff %s' % diff)

      if diff != 1:
        i = 0
        car += 1
        last_date = None

    last_date = d

    if i % 10 == 0:
      logs.append(row)
      # print(gt(row[2].strip()))

    # if total > 1000: break
    # total += 1

    i += 1

with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in logs:
      spamwriter.writerow(row)