import sys
import Orange

training_file = sys.argv[1]
test_file = sys.argv[2]
new_training_file = sys.argv[3]
new_test_file = sys.argv[4]

training_data = Orange.data.Table(training_file)
training_data.remove_meta_attribute("src")
training_data.domain.remove_meta("src")
training_data.remove_meta_attribute("tgt-1")
training_data.domain.remove_meta("tgt-1")
training_data.save(new_training_file)
test_data = Orange.data.Table(test_file)

training_domain = training_data.domain
new_test_data = test_data.translate(training_domain)

new_test_data.save(new_test_file)
