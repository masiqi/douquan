#!/bin/sh
/usr/local/bin/indexer --merge tuangou_deals_main tuangou_deals_delta --merge-dst-range delete 0 0 --rotate
