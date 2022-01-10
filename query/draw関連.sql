select * from draw;
delete from draw;

--delete from draw where card_id in('87911144', '85913101', '85536617') and month = 9;

--���I��������Ώێ҂𒊏o����
SELECT * FROM toei
WHERE user_id='2' AND available_flg='1' and delete_flg = '0'
AND card_id NOT IN(SELECT card_id FROM draw WHERE year = 2020 AND month = 9 AND delete_flg='0')
order by created_at ;

SELECT count(*) FROM toei
WHERE user_id='2' AND available_flg='1' and delete_flg = '0'
AND card_id NOT IN(SELECT card_id FROM draw WHERE year = 2020 AND month = 10 AND delete_flg='0')
;

--���I�������̂̂܂Ƃ߁iDraw list��ʂ̃N�G���j
select a.year, a.month, a.day, a.from_time, a.to_time, a.court,count(*) * 2 as ���I����, b.odds
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

--���I�ꗗ
select * from draw a inner join toei b
on a.card_id = b.card_id
where b.user_id = '2' and a.delete_flg = '0';

update draw set delete_flg = '1' where id = 25;

--���I�m��ꗗ
select * from draw a inner join toei b
on a.card_id = b.card_id
where b.user_id = '1' and a.delete_flg = '0' and a.draw_conf_flg = '0'
and b.user_nm_kn like '�T�N�}%';


--���K�Ǘ��\��Ƃ��s�����߂�CSV�o��
select
  concat(year, '/', month, '/',day)
  , case 
    when court = '0' 
      then '�{���̐X' 
    when court = '1' 
      then '���������' 
    when court = '2' 
      then '������' 
    when court = '3' 
      then '��̓�����' 
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

