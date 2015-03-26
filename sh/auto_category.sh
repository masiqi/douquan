#!/bin/sh
cd /home/website/douquan
/usr/local/bin/python /home/website/douquan/manage.py auto_category update null --settings=server
