#!/usr/local/bin/python

f = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\missing_log.txt', 'rb')
notes = f.readline()
splitter = notes.split(",")
unique = []
for item in splitter:
    if item != '' or item != "" or item != ' ' or item != " ":
        match = ''.join(item)
        unique.append(match)
f.close()
final_match = []
for item in unique:
    if item not in final_match:
        final_match.append(item)
current = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\unique.txt', 'rb')
known = current.readline()
splitter2 = known.split(",")
issues = []
for item in splitter2:
    key, value = item.split(":")
    issues.append(key)
current.close()
log = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\result_log.csv', 'wb')
log.write("Issues"+"\n")
for item in final_match:
    if item not in issues:
        log.write(item+"\n")
log.close()
current.close()