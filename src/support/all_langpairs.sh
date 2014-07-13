for langpair in de_en en_de de_es es_de en_cs cs_en de_fr fr_de
do 
   python support/evaluation/interannotator.py --label $langpair  --files /home/elav01/taraxu_data/r2/results/*$langpair*.xml --systems rbmt1 rbmt2 moses jane google >  /home/elav01/taraxu_data/r2/results/interannotator.$langpair.tex
done
