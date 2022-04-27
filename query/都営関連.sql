select * from toei where user_id = '2';
update toei set user_id = '1' where card_id = '84808001';

select * from users;


select * from toei order by created_at ;
select * from toei order by updated_at desc ;
update toei set delete_flg = '0' where card_id = '87242690';
update toei set user_id = '2' where card_id = '86949751';

select * from toei where card_id = '85536617';
select * from toei where give_nm = '日向　竜馬';

select * from toei where delete_flg = '1';

--抽選かけられる対象者を抽出する
select count(*) from toei where user_id='1' AND available_flg='1' AND card_id
 NOT IN(select card_id from draw where year='2020' AND month='2' AND delete_flg='0')
 ;
