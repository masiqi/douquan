#!/bin/sh
rm /tmp/manzuo.cookie
curl http://www.manzuo.com/beijing/index.htm -c manzuo.cookie >> /dev/null
cat manzuo.cookie | awk -F '\t' '{if(NF == 7) printf("%s=%s;", $6, $7)}' > /tmp/manzuo.cookie
echo "" >> /tmp/manzuo.cookie
curl http://www.manzuo.com/shanghai/index.htm -c manzuo.cookie >> /dev/null
cat manzuo.cookie | awk -F '\t' '{if(NF == 7) printf("%s=%s;", $6, $7)}' >> /tmp/manzuo.cookie
echo "" >> /tmp/manzuo.cookie
curl http://www.manzuo.com/qingdao/index.htm -c manzuo.cookie >> /dev/null
cat manzuo.cookie | awk -F '\t' '{if(NF == 7) printf("%s=%s;", $6, $7)}' >> /tmp/manzuo.cookie
echo "" >> /tmp/manzuo.cookie
rm manzuo.cookie
cd /home/website/douquan
/usr/local/bin/python /home/website/douquan/manage.py crawler_task update_cookie manzuo --settings=server
