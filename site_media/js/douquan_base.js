/*
 * base js
 * @author: zhang.xiaoye@gmail.com
 */

document.domain = 'douquan.com';

/* main url */
var base_root = 'douquan.com';
var site_root = 'http://www.' + base_root;
var url_i = 'http://i.' + base_root;
var url_passport = 'http://passport.' + base_root;


function _log(msg) {
	alert(msg)
}
function _msg(msg) {
	alert(msg)
}

function _chk_search() {
	var keyword = $("#search_keyword")
	var city = g_city
	var url = "/" + city + "/s_" + keyword + ".html"
	window.location = url
}
function changeCity() {
	if($("#city_list").css("display") == "none") {
		$("#city_list").show()
	} else {
		window.setTimeout(function() {
			$("#city_list").hide()
		}, 200)
	}
}
function init_event() {
	$("#change_city_link").bind("click", changeCity)
	$("#change_city_link").bind("blur", changeCity)
}

function init_dialog(div, trigger) {
	$('#' + trigger).click(function(e){open_dialog(div, $('#'+trigger).attr('href'));return false;})
}
/*
 * div: container
 * deal_id: pk of deal
 * mydeal_id: pk of mydeal
 * type: 0,up;1,down;2,need to select
 * act:paid;used;wish
 */
function review_dialog(div, deal_id, mydeal_id, type, act){
	var attr = {}
	
	if (!deal_id) {
		return
	}
	
	show_msg();
	
	attr['deal_id'] = deal_id;
	if (mydeal_id) {
		attr['mydeal_id'] = mydeal_id;
	}
	
	attr['type'] = type
	attr['act'] = act
	
	$.ajaxSetup({'async':false})
	var url = mydeal_id?url_i + '/deal_review_info_' + deal_id + '.html' : site_root + '/deal_review_info_' + deal_id + '.html'
	$.getJSON(url, function(e){
		attr['is_login'] = e.is_login
		if(attr['is_login'] == true) {
			attr['voted'] = e.voted
		} else {
			attr['voted'] = false
		}
		attr['up_count'] = e.up_count
		attr['dw_count'] = e.dw_count
		attr['my_tags'] = e.my_tags
		attr['deal_tags'] = e.deal_tags
	})
	
	close_msg('dialog_loading');
	
	if (set_dialog(div, attr) == true) {
		open_dialog(div, attr)
	}
}
function set_dialog(div, attr) {
	if(attr['is_login'] == false) {
		window.location = url_passport + '/login/?goto=' + window.location
		return false
	}
	
	if(attr['voted'] == true && !attr['mydeal_id']) {
		show_msg({'msg':'您已经评价过了：）'})
		return false
	}
	
	$("li[class='zs']").html('已有<span>'+attr['up_count']+'</span>人顶，<span>'+attr['dw_count']+'</span>人踩')
	
	$('#r_deal_id').attr('value', attr['deal_id'])
	if(attr['mydeal_id']){
		$('#r_mydeal_id').attr('value', attr['mydeal_id'])
	}
	$('#r_type').attr('value', attr['type'])
	$('#r_act').attr('value', attr['act'])
	
	tags = attr['deal_tags'].split(',')
	if (tags.length != 0 && tags[0] != ''){
		var tags_html = ''
		jQuery.each(tags, function(index, value) {
			tags_html += '<li><a class="bluew" href="javascript:add_tags(\''+value+'\', \'id_tags\')">'+value+'</a></li>'
		})
	} else {
		var tags_html = '<li><a class="bluew" href="javascript:add_tags(\'美食\', \'id_tags\')">美食</a></li>'
		tags_html += '<li><a class="bluew" href="javascript:add_tags(\'娱乐\', \'id_tags\')">娱乐</a></li>'
		tags_html += '<li><a class="bluew" href="javascript:add_tags(\'美容美发\', \'id_tags\')">美容美发</a></li>'
		tags_html += '<li><a class="bluew" href="javascript:add_tags(\'泡温泉\', \'id_tags\')">泡温泉</a></li>'
	}
	$('#id_recommend_tags').html(tags_html)
	$('#id_tags').attr('value', '')
	$('#' + div + '_close').bind('click', {'div':div}, function(e){close_dialog(e.data.div)})
	$('#' + div + '_cancel').bind('click', {'div':div}, function(e){close_dialog(e.data.div)})
	
	return true
}
function open_dialog(div, attr) {
	$('#' + div).show()
}
function close_dialog(div) {
	$('#' + div).hide()
}

function show_msg(attr) {
	if(attr) {
		if(attr['msg']) {
			$('#warning_msg').html(attr['msg'])
		}
	}
	$('#warning_close').bind('click', function(e){close_msg()})
	$('#warning').show()
}
function close_msg(){
	$('#warning').hide()
}
function add_tags(tag, id) {
	tags = $('#' + id).attr('value')
	if (tags != '') {
		$('#' + id).attr('value', tags + ' ' + tag) 
	} else {
		$('#' + id).attr('value', tag)
	}
}
function chk_form(id) {
	v = $('#' + id).attr('value')
	if (v == '') {
		_msg('请输入评论内容。')
		return false
	} else {
		return true
	}
}
function require_login(id) {
	$('#'+id).bind('click', function(e){chk_login()})
}
function chk_login() {
	if (is_login == 0) {
		if (confirm('发表评论需要登录，是否登录？')) {
			window.location = url_passport + '/login/?goto=' + window.location
		}
	}
}