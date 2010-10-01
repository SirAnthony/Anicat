#!select
#####
SELECT DISTINCT $select. FROM `$tbl.` $joins. $wclause. $order. $limit.
#!insert
#####
INSERT INTO `$tbl.` ($fields.) VALUES("$values.") $update.
#!update
########
UPDATE `$tbl.` SET $update $wclause 
#!count
######
SELECT COUNT(*) FROM `$tbl.` $wclause.
#!join
######
LEFT JOIN (
SELECT $elm.bun.mainid, $elm..name
FROM $elm.,$elm.bun 
WHERE 
    $elm..id = $elm.bun.elemid AND $elm.bun.job = (SELECT id FROM credit WHERE name = '$job.') 
GROUP BY $elm.bun.mainid
) $tnum. on ($tnum..mainid=catalog.id)
