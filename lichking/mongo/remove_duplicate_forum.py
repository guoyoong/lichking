# coding=utf-8

import re

f = open('D:\source\lichking\\it168_test', 'r')
dict = {}
for line in f:
    s = line
    line = line.strip()
    try:
        if line in dict:
            dict[line] += 1
        else:
            dict[line] = 1
    except:
        print s
f.close()
i = 0
for key in dict:
    i = i+1
    print str(i)+':'+key + '.......' + str(dict[key])
    if dict[key] > 1:
        print key + '.......' + str(dict[key])

# f = open('D:\source\lichking\\ihei5_forum_list_file', 'w')
# for key in dict:
#     f.write(key+'\n')
# f.close()
