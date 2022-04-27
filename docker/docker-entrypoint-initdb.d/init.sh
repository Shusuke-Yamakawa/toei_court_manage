bash << EOS
#!/bin/bash
echo "リストア開始"
psql toei_court < '/docker-entrypoint-initdb.d/toei_court.pgdmp'
echo "リストア終了"
EOS
