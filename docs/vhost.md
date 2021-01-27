# virtualhost 用の conf ファイルの設定例

## 1. 目次

<!-- TOC depthFrom:2 -->

- [1. 目次](#1-目次)
- [2. 概要](#2-概要)
- [3. 前提](#3-前提)
- [4. vhost の設定例](#4-vhost-の設定例)
    - [4.1. 簡単な vhost](#41-簡単な-vhost)
    - [4.2. SSL 証明書を設定する vhost](#42-ssl-証明書を設定する-vhost)
    - [4.3. php-fpm を設定する例](#43-php-fpm-を設定する例)

<!-- /TOC -->

<br>

## 2. 概要

virtualhost 用の conf ファイルの書き方例を載せています.

また, 以下についても確認してください.

1. conf ファイルは [nginxv3_vhost_src_dir](../README.md#nginxv3_vhost_src_dir) で設定された変数のディレクトリに用意してください.

2. デプロイする conf ファイル名の一覧は変数 [nginxv3_vhost_list](../README.md#nginxv3_vhost_list) に定義しておいて下さい.

<br>

## 3. 前提

前提として以下の変数が設定されているものとします.

```yaml
nginxv3_ssl_confs:
  test_example_com:
    src_dir: null
    dest_dir: "{{ nginxv3_ssl_dir }}/test.example.com/"
    dhparam:
      file: "dhparam.pem"
      size: "2048"
    certificate_list:
      - crt_file: "ec/fullchain.pem"
        key_file: "ec/privkey.pem"
      - crt_file: "rsa/fullchain.pem"
        key_file: "rsa/privkey.pem"
```

<br>

## 4. vhost の設定例

### 4.1. 簡単な vhost

```
server {
    listen 80;
    server_name localhost;

    location / {
        root   /usr/share/nginx/html/;
        index  index.html;
    }
}
```

<br>

### 4.2. SSL 証明書を設定する vhost

```
server {
    listen 443 ssl http2;
    server_name test.example.com;

{% set dest_dir = nginxv3_ssl_confs.test_example_com.dest_dir %}
{% for item in nginxv3_ssl_confs.test_example_com.certificate_list %}
    ssl_certificate      {{ (dest_dir ~ '/' ~ item.crt_file) | realpath }};
    ssl_certificate_key  {{ (dest_dir ~ '/' ~ item.key_file) | realpath }};
{% endfor %}
    ssl_dhparam          {{ (dest_dir ~ '/' ~ nginxv3_ssl_confs.test_example_com.dhparam.file) | realpath }};

    location / {
        root   /usr/share/nginx/html/;
        index  index.html;
    }
}
```

これがデプロイされると, 

```
server {
    listen 443 ssl http2;
    server_name test.example.com;

    ssl_certificate      /etc/nginx/ssl/test.example.com/ec/fullchain.pem;
    ssl_certificate_key  /etc/nginx/ssl/test.example.com/ec/privkey.pem;
    ssl_certificate      /etc/nginx/ssl/test.example.com/rsa/fullchain.pem;
    ssl_certificate_key  /etc/nginx/ssl/test.example.com/rsa/privkey.pem;
    ssl_dhparam          /etc/nginx/ssl/test.example.com/dhparam.pem;

    location / {
        root   /usr/share/nginx/html/;
        index  index.html;
    }
}
```

となります.

<br>

### 4.3. php-fpm を設定する例

```
server {
    listen 443 ssl http2;
    server_name test.example.com;

{% set dest_dir = nginxv3_ssl_confs.test_example_com.dest_dir %}
{% for item in nginxv3_ssl_confs.test_example_com.certificate_list %}
    ssl_certificate      {{ (dest_dir ~ '/' ~ item.crt_file) | realpath }};
    ssl_certificate_key  {{ (dest_dir ~ '/' ~ item.key_file) | realpath }};
{% endfor %}
    ssl_dhparam          {{ (dest_dir ~ '/' ~ nginxv3_ssl_confs.test_example_com.dhparam.file) | realpath }};

    index index.html index.php;
    root /var/www/php_apps;

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_index index.php;
        fastcgi_pass unix:/run/php/php{{ php7_version | default('7.4') }}-fpm.sock;
        fastcgi_param SCRIPT_FILENAME  $realpath_root$fastcgi_script_name;
        fastcgi_hide_header "X-APP-INFO";
    }
}
```