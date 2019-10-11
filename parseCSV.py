
import csv

with open('bar.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        # row is a list of strings
        # use string.join to put them together
        print (row)
