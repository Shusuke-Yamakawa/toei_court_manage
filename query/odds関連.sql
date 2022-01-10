select * from odds_court order by odds_court.day, court, from_time;




delete from odds_court;
select * from odds_court where month = 7;
delete from odds_court where month = 7;

select
  day
  , from_time
  , case 
    when court = '0' 
      then '•{’†‚ÌX' 
    when court = '1' 
      then '¬‹àˆäŒö‰€' 
    when court = '2' 
      then '–ììŒö‰€' 
    when court = '3' 
      then 'ˆä‚Ì“ªŒö‰€' 
    end
  , odds
  , apply_court
  , empty_court 
from
  odds_court
where month = 10
and day in(3,4,10,11,17,18,24,25,31)
order by
  odds_court.day
  , court
  , from_time;



select
  day
  , from_time
  , case 
    when court = '0' 
      then '•{’†‚ÌX' 
    when court = '1' 
      then '¬‹àˆäŒö‰€' 
    when court = '2' 
      then '–ììŒö‰€' 
    when court = '3' 
      then 'ˆä‚Ì“ªŒö‰€' 
    end
  , odds
  , apply_court
  , empty_court 
from
  odds_court
where court = '3'
order by
  odds_court.day
  , court
  , from_time;
  
  
  
