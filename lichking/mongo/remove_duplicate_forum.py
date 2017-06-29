# coding=utf-8

import re

f = open('D:\source\lichking\\test', 'r')
dict = {}
for line in f:
    line = line.replace('\n', '')
    print "db." + line + '.createIndex({time:1})'
    # s = line
    # line = line.strip()
    # try:
    #     line = re.search('thread-[\d]+', line).group(0)
    #     if line in dict:
    #         dict[line] += 1
    #     else:
    #         dict[line] = 1
    # except:
    #     print line
f.close()
# i = 0
# for key in dict:
#     i = i+1
#     if dict[key] == 1:
#         print key + '.......' + str(dict[key])

# f = open('D:\source\lichking\\ihei5_forum_list_file', 'w')
# for key in dict:
#     f.write(key+'\n')
# f.close()
