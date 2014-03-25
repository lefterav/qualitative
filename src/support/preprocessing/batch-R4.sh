for USER in beo1 beo2
do
    for i in 'de-en',DE,EN 'en-de',EN,DE 'de-es',DE,ES 'es-de',ES,DE 'de-fr',DE,FR 'fr-de',FR,DE
    do
        IFS=","
        set $i
        echo ./esmt add document /wizard/appraise/data/r4/$USER/$USER.newstest2012.$1.src -l $2 --idfile /wizard/appraise/data/r4/$USER/$USER.newstest2012.$1.ids
        echo ./esmt add corpus -i $2-R4news -l $2 $USER.newstest2012.$1.src

        for SYSTEM in moses,lucy,trados
        do
            echo ./esmt add translation -i R4news -s $SYSTEM-R4 /wizard/appraise/data/r4/$USER/$USER.newstest2012.$1.$SYSTEM -l $3
        done
        
        
        echo ./esmt add task -t ranking -c $USER.newstest2012.$1.src -s 'moses-r4,lucy-r4,trados-r4' -n 'Evaluation Round 4: Ranking evaluation task for $1' -u $USER-$1-R4 -l $3 -R
        echo ./esmt add task -t select-and-post-edit -c $USER.newstest2012.$1.src -s moses-r4,lucy-r4,trados-r4 -n 'Evaluation Round 4: Select and post-edit task task for $1' -u wizard -l $3 -R
    done
done
