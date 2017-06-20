# coding=utf-8


if __name__ == '__main__':
    source_arr = ['angeeks', 'cnmo_forum', 'gfan', 'hiapk', 'ihei5', 'imobile', 'it168', 'ithome',
                  'lenovo_club', 'lenovo_mobile', 'pconline', 'shayu', 'baidu_tieba', 'zhiyoo']

    for source_name in source_arr:
        print 'nohup python /home/work/spider_lenovo/cron_lichking/lichking/run_dir/' + source_name + '_run.py >> ../../spider_logs/'+source_name+'.log &'
