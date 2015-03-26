
INSERT INTO `deal_city` (`id`, `name`, `abbreviation`) VALUES
(1, '全国', 'cn'),
(2, '北京', 'bj'),
(3, '上海', 'sh'),
(4, '武汉', 'wh'),
(5, '广州', 'gz');


INSERT INTO `deal_site` (`id`, `name`, `url`, `default_promotion`) VALUES
(1, '美团', 'http://www.meituan.com/', 'http://www.bankrate.com.cn'),
(2, '拉手', 'http://www.lashou.com', 'http://www.bankrate.com.cn'),
(3, '优享团', 'http://tuan.yoka.com', 'http://www.bankrate.com.cn'),
(4, '饭统网', 'http://www.fantong.com', 'http://www.bankrate.com.cn');

INSERT INTO `crawler_task` (`id`, `name`, `site_id`, `charset`) VALUES
(1, '美团当日团购', 1, 'utf8'),
(2, '优享团当日团购', 3, 'gbk'),
(3, '拉手', 2, 'utf8'),
(4, '饭统网', 4, 'utf8');

INSERT INTO `crawler_entry` (`id`, `task_id`, `source`, `type`, `cookie`) VALUES
(1, 1, 'http://www.meituan.com/api/v1/beijing/deals', 1, ''),
(2, 2, 'http://tuan.yoka.com/list', 1, NULL),
(3, 3, 'http://open.client.lashou.com/list/goods/cityid/2419', 1, 'city=2419'),
(4, 1, 'http://www.meituan.com/api/v1/shanghai/deals', 1, ''),
(5, 1, 'http://www.meituan.com/api/v1/wuhan/deals', 1, ''),
(6, 3, 'http://open.client.lashou.com/list/goods/cityid/2421', 1, 'city=2421'),
(7, 4, 'http://tuan.fantong.com/shanghai', 1, ''),
(8, 4, 'http://tuan.fantong.com/beijing', 1, ''),
(9, 4, 'http://tuan.fantong.com/guangzhou', 1, '');

INSERT INTO `crawler_publishrule` (`id`, `task_id`, `name`, `process`, `auto_update`, `default_value`) VALUES
(1, 1, 'detail', '', 0, ''),
(2, 1, 'name', '', 1, ''),
(3, 1, 'category_id', '', 0, '1'),
(4, 1, 'site_id', '', 0, '1'),
(5, 1, 'current_price', '', 1, ''),
(6, 1, 'original_price', '', 1, ''),
(7, 1, 'company_name', '', 0, ''),
(8, 1, 'company_detail', '', 0, ''),
(9, 1, 'volunteer', '', 1, '0'),
(10, 1, 'min_actor', '', 0, '0'),
(11, 1, 'city_id', '', 0, '2'),
(12, 2, 'name', '', 1, ''),
(13, 2, 'detail', '', 0, ''),
(14, 2, 'site_id', '', 0, '3'),
(15, 2, 'current_price', '', 1, '0'),
(16, 2, 'original_price', '', 1, '0'),
(17, 2, 'category_id', '', 0, '1'),
(18, 2, 'company_name', '', 1, ''),
(19, 2, 'company_detail', '', 1, ''),
(20, 2, 'volunteer', '', 1, '0'),
(21, 2, 'min_actor', '', 0, '0'),
(22, 2, 'logo', '', 0, ''),
(23, 2, 'city_id', '', 0, '1'),
(24, 1, 'buy_url', '', 0, 'http://www.bankrate.com.cn'),
(25, 4, 'buy_url', '', 0, 'http://www.bankrate.com.cn'),
(26, 4, 'company_detail', '', 1, ''),
(27, 4, 'company_name', '', 1, ''),
(28, 4, 'name', '', 1, ''),
(29, 4, 'current_price', '', 1, ''),
(30, 4, 'original_price', '', 1, ''),
(31, 4, 'detail', '', 1, ''),
(32, 4, 'city_id', '', 1, '1'),
(33, 4, 'logo', '', 1, ''),
(34, 4, 'end_at', '', 0, ''),
(35, 4, 'site_id', '', 0, '4'),
(36, 4, 'category_id', '', 0, '1'),
(37, 4, 'volunteer', '', 0, '0'),
(38, 4, 'min_actor', '', 0, '0');


INSERT INTO `crawler_taskvar` (`id`, `task_id`, `name`, `regular`, `process`, `type`) VALUES
(1, 1, 'company_detail', '<div id="side-business"><h2>([^<>]*)</h2>(?P<detail>[\\w\\W]*?)</div>', 'download_picture_and_delete_tags', 2),
(2, 1, 'end_at', '<div class="deal-box deal-timeleft deal-on" id="deal-timeleft" diff="(?P<lefttime>\\d+)">', 'calculate_lefttime', 2),
(3, 1, 'company_name', '<div id="side-business"><h2>(?P<company>[^<>]*)</h2>', 'download_picture_and_delete_tags', 2),
(4, 1, 'detail', '<div class="box-content cf">(?P<depict>[\\w\\W]*)<div class="side">', 'download_picture_and_delete_tags', 2),
(5, 1, 'min_actor', '<p class="deal-buy-tip-btm">([^<>]*)<strong>(?P<min_actor>\\d+)</strong>', '', 2),
(6, 1, 'volunteer', '(<p class="deal-buy-tip-top">|<p class="deal-buy-tip-total">([^<>]*))<strong>(?P<volunteer>\\d+)</strong>', '', 2),
(7, 1, 'original_price', '<tr>[^<>]*<td>([^0-9\\-]+)(?P<price>.*)</td>', '', 2),
(8, 1, 'logo', '<div class="deal-buy-cover-img">(?P<img>.*)</div>', 'download_picture_and_delete_tags', 2),
(9, 1, 'name', '<h1>(<[^>]+>[^<>]+</[^>]>)*(?P<title>.*)</h1>', '', 2),
(10, 1, 'current_price', '<p class="deal-price"><strong>([^0-9\\-]+)(?P<price>.*)</strong>', '', 2),
(11, 1, 'buy_url', '<span><a href="(?P<url>[\\w\\W].*?)"><img src="http://s1.meituan.com/css/i/button-deal-buy.gif" /></a></span>', 'complate_url', 2),
(12, 4, 'name', '<h1>(.*)</h1>', '', 2),
(13, 4, 'current_price', '<p class="deal-price"><strong>([^0-9\\-]+)(?P<price>.*)</strong>', '', 2),
(14, 4, 'original_price', '<tr>[^<>]*<td>([^0-9\\-]+)(?P<price>[0-9\\-.]*)</td>', '', 2),
(15, 4, 'end_at', 'diff="(?P<lefttime>\\d+)">', 'calculate_lefttime', 2),
(16, 4, 'logo', '<li class="first">(?P<img>.*)</li>', 'download_picture_and_delete_tags', 2),
(17, 4, 'company_name', '<div id="side-business">([^<>].*)<h2>(?P<company>[^<>]*)</h2>', '', 2),
(18, 4, 'company_detail', '<div id="side-business">([^<>].*)<h2>([\\W\\w].*)</h2>(?P<detail>[\\W\\w]*)<div style="margin-top:10px;">', 'download_picture_and_delete_tags', 2),
(19, 4, 'detail', '<div class="main">([^<>]*)<h2 id="detail">本单详情</h2>(?P<detail>[\\W\\w]*)</div>([^<>]*)<div class="clear">', 'download_picture_and_delete_tags', 2),
(20, 4, 'buy_url', '<a href="(?P<url>[\\w\\W].*?)"><img src="/images/icons/button-deal-buy.gif"', 'complate_url', 2);


INSERT INTO `crawler_univar` (`id`, `entry_id`, `name`, `regular`, `process`, `type`) VALUES
(2, 1, 'current_price', '<p class="deal-price"><strong>([^0-9\\-]+)(?P<price>.*)</strong>', '', 2),
(3, 1, 'name', '<h1>(<[^>]+>[^<>]+</[^>]>)*(?P<title>.*)</h1>', '', 2),
(4, 1, 'logo', '<div class="deal-buy-cover-img">(?P<img>.*)</div>', 'download_picture_and_delete_tags', 2),
(5, 1, 'original_price', '<tr>[^<>]*<td>([^0-9\\-]+)(?P<price>.*)</td>', '', 2),
(6, 1, 'volunteer', '(<p class="deal-buy-tip-top">|<p class="deal-buy-tip-total">([^<>]*))<strong>(?P<volunteer>\\d+)</strong>', '', 2),
(7, 1, 'min_actor', '<p class="deal-buy-tip-btm">([^<>]*)<strong>(?P<min_actor>\\d+)</strong>', '', 2),
(8, 1, 'detail', '<div class="box-content cf">(?P<depict>[\\w\\W]*)<div class="side">', 'download_picture_and_delete_tags', 2),
(9, 1, 'company_name', '<div id="side-business"><h2>(?P<company>[^<>]*)</h2>', 'download_picture_and_delete_tags', 2),
(10, 1, 'end_at', '<div class="deal-box deal-timeleft deal-on" id="deal-timeleft" diff="(?P<lefttime>\\d+)">', 'calculate_lefttime', 2),
(11, 2, 'name', '<h2>([^<>]*)</h2>', '', 2),
(12, 2, 'logo', '<div class="gorL"([^<>]*)>(?P<img>[\\w\\W]*)<dl class="news cL">', 'download_picture_and_delete_tags', 2),
(13, 2, 'detail', '<div class="bx6_cnt fo">(?P<depict>[\\w\\W]*)<div clickname="stick_12">', 'download_picture_and_delete_tags', 2),
(18, 1, 'company_detail', '<div id="side-business"><h2>([^<>]*)</h2>(?P<detail>[\\w\\W]*?)</div>', 'download_picture_and_delete_tags', 2),
(19, 1, 'city_id', 'city_id=2', '', 3),
(20, 4, 'city_id', 'city_id=3', '', 3),
(21, 5, 'city_id', 'city_id=4', '', 3),
(22, 7, 'city_id', 'city_id=3', '', 3),
(23, 8, 'city_id', 'city_id=2', '', 3),
(24, 9, 'city_id', 'city_id=5', '', 3);

INSERT INTO `crawler_urlrule` (`id`, `entry_id`, `regular`, `process`) VALUES
(1, 1, '<deal_url>([^<>]+)</deal_url>', ''),
(2, 2, '<td class="tdImg"><a href="([^<>]+)">', ''),
(3, 3, '<goods_site_url>([^<>]*)</goods_site_url>', ''),
(4, 4, '<deal_url>([^<>]+)</deal_url>', ''),
(5, 5, '<deal_url>([^<>]+)</deal_url>', ''),
(6, 7, 'rurl=([\\w\\W].*?)\\?', ''),
(7, 8, 'rurl=([\\w\\W].*?)\\?', ''),
(8, 9, 'rurl=([\\w\\W].*?)\\?', '');
