

import xmlrpclib, socket, sys

# Connect to the server
s = xmlrpclib.Server("http://localhost:8585")
    
# Make the remote procedure calls on the server
try:
    # How many n-grams of different order are there in this LM ?
    n1grams = s.howManyNgrams(1)
    n2grams = s.howManyNgrams(2)
    n3grams = s.howManyNgrams(3)

    # Get some n-gram log probs. Note that a SRI language model uses backoff smoothing, 
    # so if an n-gram is not present in the LM, it will compute it using a smoothed lower-order
    # n-gram distribution.
    p1 = s.getUnigramProb('good')
    p2 = s.getBigramProb('nitin madnani')
    p3 = s.getTrigramProb('there are some');
    
    # Query the LM to get the final log probability for an entire sentence.
    # Note that this is  different from a n-gram probability because
    #  (1) For a sentence, SRILM appends <s> and </s> to its beginning
    #     and the end respectively
    #  (2) The log prob of a probability is the sum of all individual
    #     n-gram log probabilities
    # Also note that you have to pass the number of words in the sentence
    # because the SRILM API requires you to. 
    sprob = s.getSentenceProb('there are some good',4)

    # Query the LM to get the total log probability for the file named 'corpus'
    corpus = 'test.txt'
    corpus_prob = s.getCorpusProb(corpus)

    # Query the LM to get the perplexity for the file named 'corpus'
    corpus_ppl = s.getCorpusPpl(corpus);

except socket.error:
    sys.stderr.write('Error: could not connect to the server.\n')
    sys.exit(1)

# Print out all our results    
print "There are", n1grams, "unigrams in this LM."
print "There are", n2grams, "bigrams in this LM."
print "There are", n3grams, "trigrams in this LM."

print "p('good') =", p1
print "p('nitin madnani') =", p2
print "p('there are some') =", p3
print

print "p ('there are some good') =" , sprob
print

print "Logprob for the file" , corpus , "=" , corpus_prob

print "Perplexity for the file" , corpus , "=" , corpus_ppl

# Stop the server
# NOTE: You will probably do this in the last client (if you know 
# which one that is) or in a clean-up script when you are absolutely sure
# that all clients are finished.
s.stop_server()
