server {
  listen       80;
  server_name  img.douquan.com;
  root /home/website/douquan;
  index  index.html;
  access_log  /data1/logs/nginx/img.douquan.com.access.log;
  error_log  /data1/logs/nginx/img.douquan.com.error.log;

  charset utf-8;
  set $django 1;
  set $my_url $request_uri;
  if ($is_args = "?") {
	set $args_old ?$args;
  }
  if ($is_args = "") {
	set $args_old "";
  }
						  
  default_type image/png;
  location /media/deal_pic {
	#alias /home/website/douquan/site_media/deal_pic/;
	expires max;
	fastcgi_param REMOTE_ADDR $remote_addr;
	fastcgi_param PATH_INFO $fastcgi_script_name;
	fastcgi_param REQUEST_METHOD $request_method;
	fastcgi_param QUERY_STRING $query_string;
	fastcgi_param CONTENT_TYPE $content_type;
	fastcgi_param CONTENT_LENGTH $content_length;
	fastcgi_param SERVER_PROTOCOL $server_protocol;
	fastcgi_param SERVER_PORT $server_port;
	fastcgi_param SERVER_NAME $server_name;
	fastcgi_param CACHE_PATH $static;
	fastcgi_param FILE_NAME $request_filename;
	fastcgi_pass_header Authorization;
	fastcgi_intercept_errors off;
	if (-f $request_filename$args_old) {
		set $django 0;
	}
		
	if ($django = 0) {
		rewrite (.*) $1$args_old break;
	}

	if ($django = 1) {
		fastcgi_pass   127.0.0.1:3036;
		break;
	}
  }

  location @fastcgi {
  perl hello::handler;
  }
}

