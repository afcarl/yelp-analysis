__author__ = 'Tony'
from myconfig import *
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models



def main():

    # open one of documents
    target_dir = result_root+'review/'+"active" + '_reviews.csv'
    target = open(target_dir, 'r')
    all_reviews = target.readlines()
    all_reviews = [".".join(all_reviews)]
    all_token_text = []
    all_stop_text = []
    texts = []

    # tokenize
    print "begin tokenizing"
    tokenizer = RegexpTokenizer(r'\w+')
    for review in all_reviews:
        tokens = tokenizer.tokenize(review.lower())
        all_token_text.append(tokens)
    # clean
    all_reviews = None


    # remove stop words
    print "begin removing stop words"
    en_stop = get_stop_words('en')
    for tokens in all_token_text:
        stopped_tokens = [i for i in tokens if i not in en_stop]
        all_stop_text.append(stopped_tokens)

    # clean
    all_token_text = None
    # stemming
    print "begin stemming "
    p_stemmer = PorterStemmer()
    for stop_tokens in all_stop_text:
        text = [p_stemmer.stem(i) for i in stop_tokens]
        texts.append(text)


    # begin to use LDA
    dictionary = corpora.Dictionary(texts)
    print "unique token type size " + str(len(dictionary))
    corpus = [dictionary.doc2bow(text) for text in texts]

    # run LDA model
    num_topics = 10
    top_words = 10
    print "begin training LDA"
    lda_model = models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=2000)

    # print stats
    print(lda_model.print_topics(num_topics=num_topics, num_words=top_words))

if __name__ == '__main__':
    main()