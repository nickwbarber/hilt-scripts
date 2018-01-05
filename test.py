import os 
from nltk.parse import stanford 


os.environ['STANFORD_PARSER'] = '/home/nick/resources/stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0.jar'
os.environ['STANFORD_MODELS'] = '/home/nick/resources/stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0-models.jar' 
parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?")) 
print(sentences) 
# GUI 
for line in sentences: 
    for sentence in line: 
        sentence.draw()
