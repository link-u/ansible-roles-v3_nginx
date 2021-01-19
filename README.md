# Nginx 用の role (v3版)

![ansible ci](https://github.com/link-u/ansible-roles-v3_nginx/workflows/ansible%20ci/badge.svg)

## 1. 目次

<!-- TOC depthFrom:2 -->

- [1. 目次](#1-目次)
- [2. 概要](#2-概要)
- [3. 動作確認バージョン](#3-動作確認バージョン)
- [4. Role 変数](#4-role-変数)
    - [4.1. エイリアス用の変数 (Read only な変数)](#41-エイリアス用の変数-read-only-な変数)
    - [4.2. インストールに関する基本設定用の変数](#42-インストールに関する基本設定用の変数)
        - [4.2.1. 変数の概要](#421-変数の概要)
        - [4.2.2. 変数の詳細な説明](#422-変数の詳細な説明)
    - [4.3. nginx.conf の設定用の変数](#43-nginxconf-の設定用の変数)
        - [4.3.1. 変数の概要](#431-変数の概要)
        - [4.3.2. コンテキストを設定する変数の書き方](#432-コンテキストを設定する変数の書き方)
        - [4.3.3. コンテキストを直接設定する変数の書き方](#433-コンテキストを直接設定する変数の書き方)
        - [4.3.4. 各コンテキストを設定変数のデフォルト値](#434-各コンテキストを設定変数のデフォルト値)
- [5. Licence](#5-licence)

<!-- /TOC -->

<br>

## 2. 概要

nginx をインストールする role です.

[v2 版の role](https://github.com/link-u/ansible-roles-v2_nginx) 大幅修正したものです.

※ 注意: v2版とは互換性がありません.

<br>

## 3. 動作確認バージョン

* Ubuntu: 18.04, 20.04
* ansible: 2.8, 2.9

<br>

## 4. Role 変数

### 4.1. エイリアス用の変数 (Read only な変数)

本 role ではリストと辞書を組み合わせた変数で設定を定義するため, 
このままでは特定の変数 (Ex. nginx user や ssl, conf.d のディレクトリパス等) を呼び出しづらい問題があります. 
それを緩和するために, 書き換え不可のエイリアス用の変数を定義してあります.

| 変数 | 説明 |
| :-- | :-- |
| `nginxv3_conf_dir` | [`nginxv3_defaults_create_directories` or `nginxv3_all_create_directories`](#nginxv3_extra_directories) に定義されている `conf.d` を格納するディレクトリパスです.<br>`name = 'conf_dir'` で最初にヒットした `path`.<br>デフォルト値: `'/etc/nginx/conf.d/'` |
| `nginxv3_ssl_dir` | [`nginxv3_defaults_create_directories` or `nginxv3_all_create_directories`](#nginxv3_extra_directories) に定義されている `conf.d` を格納するディレクトリパスです.<br>`name = 'ssl_dir'` で最初にヒットした `path`.<br>デフォルト値: `'/etc/nginx/ssl/'` |
| `nginxv3_user` | [`main コンテキスト`](#main_context) に定義されている nginx のワーカープロセスを実行するユーザ名です.<br>`key = 'user'` で最初にヒットした `value`<br>デフォルト値: `www-data` |

<br>

### 4.2. インストールに関する基本設定用の変数

#### 4.2.1. 変数の概要

| 変数 | 説明 |
| :-- | :-- |
| [`nginxv3_install_flag`](#nginxv3_install_flag) |  デフォルト値: `yes` <br> インストールフラグ (no 場合, [configure.yml](tasks/configure.yml) タスクのみ実行) |
| [`nginxv3_use_dummy_vhost`](#nginxv3_use_dummy_vhost) |  デフォルト値: `no` <br> [dummy の vhost](templates/vhost_dummy.conf.j2) を使用するかどうか  |
| [`nginxv3_extra_directories`](#nginxv3_extra_directories) | デフォルト値はリンク先参照 <br> 追加で作成するディレクトリリスト |
| [`nginxv3_ssl_confs`](#nginxv3_ssl_confs) | デフォルト値はリンク先参照 <br> SSL 証明書に関する設定 |
| [`nginxv3_backlog`](#nginxv3_backlog) | デフォルト値はリンク先参照 <br> nginx の backlog の設定 |
| [`nginxv3_vhost_src_dir`](#nginxv3_vhost_src_dir) |  デフォルト値: `{{ playbook_dir }}/files/nginx/conf.d` <br> ユーザ定義の nginx の vhost ファイルのソースディレクトリ  |
| [`nginxv3_vhost_list`](#nginxv3_vhost_list) | デフォルト値: `[]` <br> ユーザ定義の nginx の vhost ファイル名リスト |

<br>

#### 4.2.2. 変数の詳細な説明

* **nginxv3_install_flag**<a name="nginxv3_install_flag"></a>

  `yes` の時は [install.yml](tasks/install.yml) と [configure.yml](tasks/configure.yml) の両方が実行されます.<br>
  `no` の時は [configure.yml](tasks/configure.yml) のみ実行されます.<br>
  基本的に `yes` で問題ないです. 主に, `apt install` 系のタスクを実行したくない時に一時的に `no` に設定することが多いです.<br>

<br>

* **nginxv3_use_dummy_vhost**<a name="nginxv3_use_dummy_vhost"></a>

  `yes` の時, [dummy の vhost](templates/vhost_dummy.conf.j2) が設定されます.<br>
  dummy の vhost は80,443番ポートに対する `default_server` が設定されており, nginx のステータスコード444を返します.<br>
  未定義の `server_name` や IP アドレスでのアクセスを拒否したいときに使います.<br>

<br>

* **nginxv3_extra_directories**<a name="nginxv3_extra_directories"></a>

  Syntax
  ```yaml
  nginxv3_extra_directories:
    - path: "<directory path>"          # 必須
      mode: "<directory permission>"    # オプション (default: '0755')
      owner: "<owner>"                  # オプション (default: 'root')
      group: "<group>"                  # オプション (default: 'root')
      name: "<name for reference>"      # オプション (default: undefined)
                                        # * リスト内のこのアイテムを参照するための変数
                                        # * ユーザがこの変数を設定する必要はない.
  ```

  Default value<br><a name="nginxv3_defaults_create_directories"></a>
  デフォルト値は [vars/main.yml](vars/main.yml) の `nginxv3_defaults_create_directories` に書かれている値.
  ```yaml
  nginxv3_defaults_create_directories:
    - { path: "/etc/nginx/conf.d/", mode: "0755", name: "conf_dir" }
    - { path: "/etc/nginx/ssl/", mode: "0755", name: "ssl_dir" }
  ```

  Example<br>
  複数のディレクトリを作成したい場合は以下のような書き方をおすすめします.
  ```yaml
  nginxv3_extra_directories:
    - { path: "/tmp/hoge" }
    - { path: "/tmp/fuga", mode: "0755" }
    - { path: "/tmp/piyo", mode: "0755", owner: "test", group: "test" }
  ```

<br>

* **nginxv3_ssl_confs**<a name="nginxv3_ssl_confs"></a>

  Syntax
  ```yaml
  nginxv3_ssl_confs:
    test:
      src_dir: "<src directory>"        # ソースディレクトリ (null の場合自己証明書を作成する)
      dest_dir: "<dest directory>"      # 設置先ディレクトリ
      dhparam:                          # DH パラメータに関する設定 (null のとき作成しない.)
        file: "<dhparam file name>"     #  * DH パラメータファイル名
        size: "<dhparam size>"          #  * DH パラメータサイズ (オプション (default value: '2048'))
      certificate_list:                 # 証明書と秘密鍵のリスト
        - crt_file: "<crt file name>"   #  * 証明書ファイル名. dest_dir からの相対パスで指定.
          key_file: "<key file name>"   #  * 秘密鍵ファイル名. dest_dir からの相対パスで指定.
  ```

  Default value<br>
  デフォルト値は [vars/main.yml](vars/main.yml) の `nginxv3_defaults_ssl_confs` に書かれている値.
  ```yaml
  nginxv3_defaults_ssl_confs:
    dummy_example_com:
      src_dir: null
      dest_dir: "{{ nginxv3_ssl_dir }}/dummy_example_com/"
      dhparam:
        file: "dhparam2048.pem"
        size: "2048"
      certificate_list:
        - crt_file: "rsa/fullchain.pem"
          key_file: "rsa/privkey.pem"
  ```

  デフォルト値に `nginxv3_ssl_confs` がマージされます.

  Example
  ```yaml
  nginxv3_ssl_confs:
    hoge:
      src_dir: null
      dest_dir: "{{ nginxv3_ssl_dir }}/hoge/"
      dhparam:
        file: "dhparam.pem"
      certificate_list:
        - crt_file: "rsa/fullchain.pem"
          key_file: "rsa/privkey.pem"

    fuga:
      src_dir: "{{ playbook_dir }}/files/nginx/ssl/"
      dest_dir: "{{ nginxv3_ssl_dir }}/fuga/"
      dhparam:
        file: "dhparam.pem"
        size: "4096"
      certificate_list:
        - crt_file: "rsa/fullchain.pem"
          key_file: "rsa/privkey.pem"
  ```


<br>

* **nginxv3_backlog**<a name="nginxv3_backlog"></a>

  Syntax
  ```yaml
  ## IPv4 の backlog 設定
  nginxv3_backlog_ipv4:
    - ip_and_port: "[<IP address>:]<port number>"   # IP アドレスとポート番号の組を設定する (IP アドレスを省略すると 0.0.0.0 となる.).
      backlog: <backlog>                            # backlog の値
    ...
  ```

  Default value<br>
  デフォルト値は [vars/main.yml](vars/main.yml) の `nginxv3_defaults_backlog` に書かれている値.
  ```yaml
  nginxv3_defaults_backlog:
    - { ip_and_port: "80", backlog: 511 }
    - { ip_and_port: "443", backlog: 511 }
    - { ip_and_port: "[::]:80", backlog: 511 }
    - { ip_and_port: "[::]:443", backlog: 511 }
  ```

  Example
  ```yaml
  nginxv3_backlog:
    - { ip_and_port: "443", backlog: 60000 }
    - { ip_and_port: "127.0.0.1:8080", backlog: 100 }
    - { ip_and_port: "[::1]:8080", backlog: 100 }
  ```

<br>

* **nginxv3_vhost_src_dir**<a name="nginxv3_vhost_src_dir"></a>

  ユーザ定義の nginx の vhost ファイルのソースディレクトリパスです.<br>
  デフォルトは `"{{ playbook_dir }}/files/nginx/conf.d"` に保存されます.

  ※ `playbook_dir` は ansible のマジック変数. playbook があるディレクトリ.

<br>

* **nginxv3_vhost_list**<a name="nginxv3_vhost_list"></a>

  ansible の template でデプロイします.<br>
  そのため conf ファイル内で Jinja2 が使えます.<br>
  `{{ nginxv3_vhost_src_dir }}/{{ nginxv3_vhost_list[n] }}` というファイルパスに用意してください.

  Syntax
  ```yaml
  ## vhost のファイル名のリスト
  nginxv3_vhost_list:
    - "<vhsot conf file 1>"
    - "<vhsot conf file 2>"
    ...
  ```

  Example
  ```yaml
  nginxv3_vhost_list:
    - "hoge.conf"
    - "fuga.conf"
    - "piyo.conf"
  ```

<br>

### 4.3. nginx.conf の設定用の変数

#### 4.3.1. 変数の概要

| 変数 | 説明 |
| :-- | :-- |
| [`nginxv3_conf_main`](#432-コンテキストを設定する変数の書き方) | [デフォルト値](#main_context)<br>main コンテキストを設定する辞書のリスト変数 |
| [`nginxv3_conf_main_raw`](#) | デフォルト値: `null`<br>main コンテキストに直接設定を書き込むための変数 |
| [`nginxv3_conf_events`](#432-コンテキストを設定する変数の書き方) | [デフォルト値](#events_context)<br>events コンテキストを設定する辞書のリスト変数 |
| [`nginxv3_conf_events_raw`](#) | デフォルト値: `null`<br>events コンテキストに直接設定を書き込むための変数 |
| [`nginxv3_conf_http`](#432-コンテキストを設定する変数の書き方) | [デフォルト値](#http_context)<br>http コンテキストを設定する辞書のリスト変数 |
| [`nginxv3_conf_http_raw`](#) | デフォルト値: `null`<br>http コンテキストに直接設定を書き込むための変数 |
| [`nginxv3_conf_mail`](#432-コンテキストを設定する変数の書き方) | [デフォルト値](#mail_context)<br>mail コンテキストを設定する辞書のリスト変数 |
| [`nginxv3_conf_mail_raw`](#) | デフォルト値: `null`<br>mail コンテキストに直接設定を書き込むための変数 |
| [`nginxv3_conf_stream`](#432-コンテキストを設定する変数の書き方) | [デフォルト値](#stream_context)<br>stream コンテキストを設定する辞書のリスト変数 |
| [`nginxv3_conf_stream_raw`](#) | デフォルト値: `null`<br>stream コンテキストに直接設定を書き込むための変数 |

<br>

#### 4.3.2. コンテキストを設定する変数の書き方

該当する変数は以下のとおりです.

* `nginxv3_conf_main`
* `nginxv3_conf_events`
* `nginxv3_conf_http`
* `nginxv3_conf_mail`
* `nginxv3_conf_stream`

コンンテキストを設定する変数は辞書をリストとして持つ変数です.<br>
`key: value` な構造を順番に保持します.<br>
また, 後述する `merge_mode` によって, 既存の `key` を update するか重複を許してリストの最後に append するかを選べます.

<br>

Syntax
```yaml
<var name>:                      # コンテキストを設定する変数名
  - key: "<key name>"            # (必須) main コンテキストの key
    value: "<value name>"        # (必須) main コンテキストの value
    merge_mode: "<merge mode>"   # (オプション) 設定を追加するときの動作モード. デフォルトでは 'update'
                                 #             'update': 該当する key について
                                 #                       存在すれば設定をを上書きし,
                                 #                       存在しなければ設定をリストの最後に付け足す.
                                 #             'append': 設定をリストの最後に付け足す. (key の重複が可能)
    eol: "<end of line>"         # (オプション) 末尾につける文字列. デフォルトでは ';'
                                 #             殆どの場合デフォルトのままで良い.
```

<br>

**Example 1. : 基本的な書き方**<br>
all グループの下に production グループがいるとします.
```yaml
## group_vars/all.yml で定義
_nginxv3_conf_main: []
_all_nginxv3_conf_main:
  - { key: "worker_processes", value: "4" }
  - { key: "pcre_jit", value: "on" }
nginxv3_conf_main: "{{ _all_nginxv3_conf_main + _nginxv3_conf_main }}"

## group_vars/production.yml で定義
_nginxv3_conf_main:
  - { key: "worker_processes", value: "200" }
  - { key: "worker_rlimit_nofile", value: "1000000" }
```

この時, production に所属していない all グループの nginx.conf は
```
worker_processes  4;
pcre_jit  on;

events {
...
```

となるのに対して, production グループでは
```
worker_processes  200;
pcre_jit  on;
worker_rlimit_nofile  1000000;

events {
...
```
となります.

<br>

**Example 2. : merge_mode='append' を使う**<br>
all グループの下に production グループがいるとします.
```yaml
## group_vars/all.yml で定義
_nginxv3_conf_http: []
_all_nginxv3_conf_http:
  - { key: "include", value: "/etc/nginx/conf.d/*.conf", merge_mode: "append" }
nginxv3_conf_http: "{{ _all_nginxv3_conf_http + _nginxv3_conf_http }}"

## group_vars/production.yml で定義
_nginxv3_conf_http:
  - { key: "include", value: "/etc/nginx/site.d/*.conf", merge_mode: "append" }
```

この時, production に所属していない all グループの nginx.conf は
```
http {
    ...

    include  /etc/nginx/conf.d/*.conf;

    ...
}
```

となるのに対して, production グループでは
```
http {
    ...

    include  /etc/nginx/conf.d/*.conf;
    include  /etc/nginx/site.d/*.conf;

    ...
}
```
となります.

<br>

**Example 3. : eol を使う**<br>
例えば, 新たなディレクティブを作る場合は行末の `';'` は不要です. その場合は `eol=''` とすることで対応できます.
```yaml
nginxv3_conf_http:
  - key: "types"
    value: |-
      {
        image/avif avif;
      }
    eol: ""
```

とすると, nginx.conf は

```
http {
    ...
    
    types  {
      image/avif avif;
    }

    ...
}
```

として出力され, 行末である `}` の後に `;` が入っていないことがわかります.

<br>

#### 4.3.3. コンテキストを直接設定する変数の書き方

名前の末尾に `_raw` とついている変数群です.<br>
[上記の変数](#432-コンテキストを設定する変数の書き方)で設定を書くことが困難な場合これらの `_raw` で終わる変数を使います.<br>

これらの変数に書かれた文字列は直接 nginx.conf に反映されます.

**Example**<br>
```yaml
nginxv3_conf_http_raw: |
  log_format ltsv 'time:$time_iso8601\t'
                  'status:$status\t'
                  'remote_addr:$remote_addr\t'
                  'request_method:$request_method\t'
                  'request_uri:$request_uri\t'
                  'host:$host\t'
                  'request_time:$request_time\t'
                  'upstream_response_time:$upstream_response_time\t'
                  'bytes_sent:$bytes_sent\t'
                  'referer:$http_referer\t'
                  'useragent:$http_user_agent\t'
                  'app_info:$upstream_http_x_app_info';
```

と設定すると, 

```
http {
    ...

    log_format ltsv 'time:$time_iso8601\t'
                    'status:$status\t'
                    'remote_addr:$remote_addr\t'
                    'request_method:$request_method\t'
                    'request_uri:$request_uri\t'
                    'host:$host\t'
                    'request_time:$request_time\t'
                    'upstream_response_time:$upstream_response_time\t'
                    'bytes_sent:$bytes_sent\t'
                    'referer:$http_referer\t'
                    'useragent:$http_user_agent\t'
                    'app_info:$upstream_http_x_app_info';

    ...
}
```

のように nginx.conf 反映される.

<br>


#### 4.3.4. 各コンテキストを設定変数のデフォルト値

* **main コンテキスト**<a name="main_context"></a>

  Default value<br>
  [vars/main.yml](vars/main.yml) の `nginxv3_defaults_conf_main` に書かれている値.
  ```yaml
  nginxv3_defaults_conf_main:
    - { key: "user", value: "www-data" }
    - { key: "worker_processes", value: "auto" }
    - { key: "worker_rlimit_nofile", value: "1000000" }
    - { key: "error_log", value: "/var/log/nginx/error.log  warn" }
    - { key: "pid", value: "/var/run/nginx.pid" }
    - { key: "pcre_jit", value: "on" }
  ```

<br>

* **events コンテキスト**<a name="events_context"></a>

  Default value<br>
  [vars/main.yml](vars/main.yml) の `nginxv3_defaults_conf_events` に書かれている値.
  ```yaml
  nginxv3_defaults_conf_events:
    - { key: "worker_connections", value: "65535" }
    - { key: "use", value: "epoll" }
  ```

<br>

* **http コンテキスト**<a name="http_context"></a>

  Default value<br>
  [vars/main.yml](vars/main.yml) の `nginxv3_defaults_conf_http` に書かれている値.
  ```yaml
  nginxv3_defaults_conf_http:
    - { key: "sendfile", value: "on" }
    - { key: "tcp_nopush", value: "on" }
    - { key: "tcp_nodelay", value: "on" }
    - { key: "charset", value: "UTF-8" }
    - { key: "keepalive_timeout", value: "300" }
    - { key: "keepalive_requests", value: "1000000" }
    - { key: "keepalive_disable", value: "none" }
    - { key: "msie_padding", value: "off" }
    - { key: "client_max_body_size", value: "64m" }
    - { key: "types_hash_max_size", value: "2048" }
    - { key: "server_tokens", value: "off" }
    - { key: "include", value: "/etc/nginx/mime.types", merge_mode: "append" }
    - key: "types"
      value: |-
        {
          image/avif avif;
        }
      eol: ""
    - { key: "default_type", value: "application/octet-stream" }
    - { key: "access_log", value: "/var/log/nginx/access.log" }
    - { key: "gzip", value: "on" }
    - { key: "gzip_min_length", value: "1024" }
    - { key: "gzip_comp_level", value: "6" }
    - key: "gzip_types"
      value: >-
        text/plain
        text/css
        application/json
        application/x-javascript
        text/javascript
        application/javascript
        application/protobuf
        application/x-protobuf
    - { key: "brotli", value: "on" }
    - key: "brotli_types"
      value: >-
        text/css
        text/javascript
        application/javascript
    - { key: "brotli_min_length", value: "1024" }
    - { key: "brotli_comp_level", value: "6" }
    - { key: "open_file_cache", value: "max=1000000" }
    - { key: "include", value: "{{ nginxv3_conf_dir | realpath }}/*.conf", merge_mode: "append" }
    - { key: "vhost_traffic_status_zone", value: "" }
  ```

<br>

* **mail コンテキスト**<a name="mail_context"></a>

  Default value<br>
  [vars/main.yml](vars/main.yml) の `nginxv3_defaults_conf_mail` に書かれている値.
  ```yaml
  nginxv3_defaults_conf_mail: []
  ```

<br>

* **stream コンテキスト**<a name="stream_context"></a>

  Default value<br>
  [vars/main.yml](vars/main.yml) の `nginxv3_defaults_conf_stream` に書かれている値.
  ```yaml
  nginxv3_defaults_conf_stream: []
  ```

<br>

## 5. Licence
MIT
