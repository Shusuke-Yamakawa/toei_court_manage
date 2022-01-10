bash << EOS
#!/bin/bash
echo "リストア開始"
psql toei_court < ./toei_court.pgdmp
echo "リストア終了"
EOS
