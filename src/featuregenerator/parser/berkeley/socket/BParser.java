
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import edu.berkeley.nlp.PCFGLA.BerkeleyParser;
import edu.berkeley.nlp.PCFGLA.CoarseToFineMaxRuleParser;
import edu.berkeley.nlp.PCFGLA.CoarseToFineNBestParser;
import edu.berkeley.nlp.PCFGLA.Grammar;
import edu.berkeley.nlp.PCFGLA.Lexicon;
import edu.berkeley.nlp.PCFGLA.ParserData;
import edu.berkeley.nlp.PCFGLA.TreeAnnotations;
import edu.berkeley.nlp.io.PTBLineLexer;
import edu.berkeley.nlp.syntax.Tree;
import edu.berkeley.nlp.util.Numberer;


public class BParser {
		PTBLineLexer tokenizer;
		Boolean tokenize;
		CoarseToFineMaxRuleParser parser;
		int kbest;
		
		public BParser( String inFileName ){		
			//String inFileName = "/home/lefterav/tools/berkeley/eng_sm6.gr";
			//String inFileName = "/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr";
			ParserData pData = ParserData.Load(inFileName);
			Grammar grammar = pData.getGrammar();
		    Lexicon lexicon = pData.getLexicon();
		    Numberer.setNumberers(pData.getNumbs());
		    
		    kbest = 1000;
		    //if (opts.chinese) Corpus.myTreebank = Corpus.TreeBankType.CHINESE;
		    double threshold = 1.0;
		    
		    //kbest parser
		    parser = new CoarseToFineNBestParser(grammar, lexicon, kbest ,threshold,-1, false , false , false , false, false, false, true);
		    parser.binarization = pData.getBinarization();
		    tokenizer = new PTBLineLexer();
		    System.err.print("Server initialized\n");
		}
		
		public void initialiaze( String inFileName ){
			//String inFileName = "/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr";
			ParserData pData = ParserData.Load(inFileName);
			Grammar grammar = pData.getGrammar();
		    Lexicon lexicon = pData.getLexicon();
		    Numberer.setNumberers(pData.getNumbs());
		    
		    kbest = 1000;
		    //if (opts.chinese) Corpus.myTreebank = Corpus.TreeBankType.CHINESE;
		    double threshold = 1.0;
		    
		    //kbest parser
		    parser = new CoarseToFineNBestParser(grammar, lexicon, kbest ,threshold,-1, false , false , false , false, false, false, true);
		    parser.binarization = pData.getBinarization();
		    tokenizer = new PTBLineLexer();

		}
		
		public Map<String, Object> parse (String line){
			return this.parse(line, false);
		}
		
		
		public Map<String, Object> parse (String line, Boolean tokenize){
			System.out.println("Parsing... " +line);
			try {
				System.out.println ("parsing first string");
				
				List<String> sentence;
				
				if (!tokenize) sentence = Arrays.asList(line.split(" "));
				  else sentence = tokenizer.tokenizeLine(line);
						
				if (sentence.size()>=80)  
	    			System.err.println("Skipping sentence with "+sentence.size()+" words since it is too long."); 
	    		
				List<Tree<String>> parsedTrees = parser.getKBestConstrainedParses(sentence, null, kbest);	
				
				Map<String, Object> output = new HashMap<String, Object>();
				output.put("nbest", this.outputTrees(parsedTrees, parser));
				output.put("loglikelihood", this.getLogLikelihood() );
				
				return output;
				
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				return null;
			}
		}
		
		public Map<String, String> getParseFeatures(String line){
			return this.getParseFeatures(line, false);
		}
		
		public Map<String, String> getParseFeatures(String line, Boolean tokenize){
			System.out.println("Parsing... " +line);
			try {
				System.out.println ("parsing first string");
				List<String> sentence;
				
				if (!tokenize) sentence = Arrays.asList(line.split(" "));
				  else sentence = tokenizer.tokenizeLine(line);
						
				if (sentence.size()>=80)  
	    			System.err.println("Skipping sentence with "+sentence.size()+" words since it is too long."); 
	    		
				List<Tree<String>> parsedTrees = parser.getKBestConstrainedParses(sentence, null, kbest);	
				
				HashMap<String, String> output = new HashMap<String, String>();
				output.putAll( this.getNBestTreeFeatures(parsedTrees, parser));
				output.put("berkeley-loglikelihood", Double.toString(this.getLogLikelihood()));
				
				return output;
				
			} catch (Exception e) {
				// TODO Auto-generated catch block
				System.out.println("Error parsing");
				return null;
			}
		}
		
		
		private Map<String, String> getNBestTreeFeatures(List<Tree<String>> parseTrees, CoarseToFineMaxRuleParser parser) {
			double sumConfidence = 0;
			double bestConfidence = Double.NEGATIVE_INFINITY;
			String bestParse = new String();
			
			for (Tree<String> parsedTree : parseTrees){
				
				if (! parsedTree.getChildren().isEmpty() ){
					parsedTree = TreeAnnotations.unAnnotateTree(parsedTree, false);
					double confidence = parser.getLogLikelihood(parsedTree);
					sumConfidence += confidence;
					if (confidence > bestConfidence){
						bestConfidence = confidence;
						bestParse = parsedTree.getChildren().get(0)+" )";
					}
				}
				
			}
			int n = parseTrees.size();
			double avgConfidence = sumConfidence / n;
			String strAvgConfidence = new String();
			if (avgConfidence == Double.NEGATIVE_INFINITY)
				strAvgConfidence = "-Inf";
			else
				strAvgConfidence = Double.toString(avgConfidence);
			Map<String, String> features = new HashMap<String, String>();
			features.put("berkeley-n", Integer.toString(n));
			features.put("berkeley-best-parse-confidence", Double.toString(bestConfidence));
			features.put("berkeley-avg-confidence", strAvgConfidence);
			features.put("berkeley-tree", bestParse);
			return features;
		}
		
		
		public List<List<Map<String, String>>> parse_batch(Object[] givenBatch){
			//list to carry the packed batch output
			List<List<Map<String, String>>> featuresBatch = new ArrayList<List<Map<String, String>>>();
			
			//XMLRPC can only import iterables as object arrays, so we have to cast repeatedly array contents
			for (int i=0; i < givenBatch.length; i++ ){
				Object[] row = (Object[]) givenBatch[i];
				List<Map<String, String>> featuresRow = new ArrayList<Map<String, String>>();
				for (int j=0; j<row.length ; j++ ){
					String sentence = (String) row[j];
					//return no featurs for empty string
					if (! sentence.equals(""))
						featuresRow.add(this.getParseFeatures(sentence));
					else
						featuresRow.add(new HashMap<String, String>());
				}
				featuresBatch.add(featuresRow);
			}
			return featuresBatch;
		}
		
		
		public Integer sum(String x, String y) {
			System.out.println (x + y);
		    return 1;
		 }
	
		
		public Double getLogLikelihood(){
			return parser.getLogLikelihood();
		}
		
		
		 /**
		 * @param parsedTree
		 * @param outputData
		 * @param opts
		 * @return 
		 */
		private List<Map<String,String>> outputTrees(List<Tree<String>> parseTrees, CoarseToFineMaxRuleParser parser) {
			ArrayList<Map<String, String>> treeList = new ArrayList<Map<String,String>>();
			for (Tree<String> parsedTree : parseTrees){
				Map<String,String> scoredTree =  new HashMap<String,String>();
				if (! parsedTree.getChildren().isEmpty() ){
					parsedTree = TreeAnnotations.unAnnotateTree(parsedTree, false);
					scoredTree.put("confidence",   Double.toString(parser.getLogLikelihood(parsedTree)) );
					scoredTree.put("tree", parsedTree.getChildren().get(0)+" )");
				}
				treeList.add(scoredTree);
			}
			return treeList;
		}
	
		private class ScoredTree {
			
			private double logLikelihood;
			private double confidence;
			private String tree;
			
			public ScoredTree(){
				this.confidence = Double.NEGATIVE_INFINITY;
				this.logLikelihood = Double.NEGATIVE_INFINITY;
				this.tree = "(())\n";
					 
			}
			
		}
}


