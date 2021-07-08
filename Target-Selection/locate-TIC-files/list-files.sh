localDIR=/mnt_home/noahf/BL-TESSsearch/TIC-query/locate-TIC-files

cat $localDIR/target-list.csv | while read line 
do
    echo 'Starting to search for' $line
    find . *$line* > $localDIR/targets-location.csv;
    echo 'Done Searching For' $line
done
