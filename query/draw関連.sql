select * from draw;
delete from draw;

--delete from draw where card_id in('87911144', '85913101', '85536617') and month = 9;

--抽選かけられる対象者を抽出する
SELECT * FROM toei
WHERE user_id='2' AND available_flg='1' and delete_flg = '0'
AND card_id NOT IN(SELECT card_id FROM draw WHERE year = 2020 AND month = 9 AND delete_flg='0')
order by created_at ;

SELECT count(*) FROM toei
WHERE user_id='2' AND available_flg='1' and delete_flg = '0'
AND card_id NOT IN(SELECT card_id FROM draw WHERE year = 2020 AND month = 10 AND delete_flg='0')
;

--抽選したもののまとめ（Draw list画面のクエリ）
select a.year, a.month, a.day, a.from_time, a.to_time, a.court,count(*) * 2 as 抽選件数, b.odds
from draw a
INNER JOIN odds_court b 
on a.year = b.year
and a.month = b.month
and a.day = b.day
and a.from_time = b.from_time
and a.court = b.court
where a.year = 2020 AND a.month = 7 And a.delete_flg = '0'
AND a.card_id in (select card_id from toei where user_id = 1)
group by a.year, a.month, a.day, a.from_time, a.to_time, a.court, b.odds;

select * from draw order by updated_at desc;

--抽選一覧
select * from draw a inner join toei b
on a.card_id = b.card_id
where b.user_id = '2' and a.delete_flg = '0';

update draw set delete_flg = '1' where id = 25;

--抽選確定一覧
select * from draw a inner join toei b
on a.card_id = b.card_id
where b.user_id = '1' and a.delete_flg = '0' and a.draw_conf_flg = '0'
and b.user_nm_kn like 'サクマ%';


--練習管理表作業を行うためのCSV出力
select
  concat(year, '/', month, '/',day)
  , case 
    when court = '0' 
      then '府中の森' 
    when court = '1' 
      then '小金井公園' 
    when court = '2' 
      then '野川公園' 
    when court = '3' 
      then '井の頭公園' 
    end court
  , from_time
  , to_time 
  ,count(*) count
from
  get_court 
where
  card_id in (select card_id from toei where user_id = '1')
  and month = 9
group by year, month, day, court, from_time, to_time
order by month, day, from_time
  ;

