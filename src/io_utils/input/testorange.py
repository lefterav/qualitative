import os
from orangereader import OrangeData
from sentence.dataset import DataSet
from io_utils.input.jcmlreader import JcmlReader
from orange import ExampleTable


os.chdir("/home/lefterav/taraxu_data/ml4hmt/experiment/test")


mydata = JcmlReader("news-test2008-dev.es-en.withlang.trial.bp.en.jcml").get_dataset()

meta_attributes= "id,testset,langsrc,langtgt".split(",")
attributes= "tgt-1_sc_t3-total,tgt-1_sc_t1-total,tgt-1_t1-OOV_count,tgt-1_t2-OOV_count,tgt-1_t3-OOV_count,tgt-1_t4-OOV_count,tgt-1_t5-OOV_count,tgt-1_an_t1-t1_r1_d1-fuzz1,tgt-1_an_t1-t1_r1_d1-fuzz2,tgt-1_an_t1-t1_r1_d1-pre-pruned,tgt-1_an_t1-t1_r1_d1-added,tgt-1_an_t1-t1_r1_d1-merged,tgt-1_phrasecount,tgt-1_t2_r1_d2-cat-PHR-S,tgt-1_t2_r1_d2-cat-PHR-CLS,tgt-1_dp-0-var,tgt-1_dp-1-var,tgt-1_dp-2-var,tgt-1_dp-3-var,tgt-1_dp-4-var,tgt-1_dp-c-var,tgt-1_dp-pC-mean,tgt-1_dp-0-std,tgt-1_dp-1-std,tgt-1_dp-2-std,tgt-1_dp-3-std,tgt-1_dp-4-std,tgt-1_dp-c-std,tgt-1_dp-pC-std,tgt-2_sc_t3-total,tgt-2_sc_t1-total,tgt-2_t1-OOV_count,tgt-2_t2-OOV_count,tgt-2_t3-OOV_count,tgt-2_t4-OOV_count,tgt-2_t5-OOV_count,tgt-2_an_t1-t1_r1_d1-fuzz1,tgt-2_an_t1-t1_r1_d1-fuzz2,tgt-2_an_t1-t1_r1_d1-pre-pruned,tgt-2_an_t1-t1_r1_d1-added,tgt-2_an_t1-t1_r1_d1-merged,tgt-2_phrasecount,tgt-2_t2_r1_d2-cat-PHR-S,tgt-2_t2_r1_d2-cat-PHR-CLS,tgt-2_dp-0-var,tgt-2_dp-1-var,tgt-2_dp-2-var,tgt-2_dp-3-var,tgt-2_dp-4-var,tgt-2_dp-c-var,tgt-2_dp-pC-mean,tgt-2_dp-0-std,tgt-2_dp-1-std,tgt-2_dp-2-std,tgt-2_dp-3-std,tgt-2_dp-4-std,tgt-2_dp-c-std,tgt-2_dp-pC-std,tgt-1_berkeley-loglikelihood,tgt-1_berkeley-best-parse-confidence,tgt-1_berkeley-n,tgt-1_berkeley-loglikelihood,tgt-1_berkeley-avg-confidence,tgt-1_berkeley-loglikelihood_ratio,tgt-1_berkeley-best-parse-confidence_ratio,tgt-1_berkeley-n_ratio,tgt-1_berkeley-loglikelihood_ratio,tgt-1_berkeley-avg-confidence_ratio,tgt-1_prob,tgt-2_berkeley-loglikelihood,tgt-2_berkeley-best-parse-confidence,tgt-2_berkeley-n,tgt-2_berkeley-loglikelihood,tgt-2_berkeley-avg-confidence,tgt-2_berkeley-loglikelihood_ratio,tgt-2_berkeley-best-parse-confidence_ratio,tgt-2_berkeley-n_ratio,tgt-2_berkeley-loglikelihood_ratio,tgt-2_berkeley-avg-confidence_ratio,tgt-2_prob".split(",")

print meta_attributes

myorangedata = OrangeData(mydata, "tgt-3_rank", attributes, meta_attributes, "test.tab")
myraworangedata = myorangedata.get_data()
myraworangedata.save("testdata.noberkl.after.tab")
myraworangedata2 = ExampleTable("testdata.noberkl.after.tab")
myraworangedata3 = ExampleTable("testdata.noberkl.after.tab")


print myraworangedata2 == myraworangedata3.

