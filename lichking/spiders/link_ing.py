# import urllib2
#
# data = open('./all_buy.txt', 'rb').read()
# req = urllib2.Request('http://10.100.124.226:9200/test/test/_bulk', data)
# req.add_header('Content-Length', '%d' % len(data))
# req.add_header('Content-Type', 'application/octet-stream')
# res = urllib2.urlopen(req)
