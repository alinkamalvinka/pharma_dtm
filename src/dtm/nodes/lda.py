import gensim
import numpy as np
import pandas as pd
from gensim import corpora, models
from gensim.models import ldaseqmodel
from gensim.models.coherencemodel import CoherenceModel


def corpus_creation(processed_docs):
    dictionary = corpora.Dictionary(processed_docs)
    print("dictionary shape ", len(dictionary))
    corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
    return corpus, dictionary


def tf_idf(corpus):
    tfidf = models.TfidfModel(corpus)
    transformed_corpus = tfidf[corpus]
    return transformed_corpus


def dtm_lda(corpus, dictionary, time_slice, num_topics, chain_variance=0.05):
    np.random.seed(609)
    dtm = ldaseqmodel.LdaSeqModel(
        corpus=corpus,
        id2word=dictionary,
        time_slice=time_slice,
        num_topics=num_topics,
        chain_variance=chain_variance,
        lda_inference_max_iter=2,
        em_min_iter=1,
        em_max_iter=2
    )
    return dtm


def pivot_evolution(evolution):
    topics = evolution["topic"].unique().tolist()
    for topic in topics:
        pivot= evolution[evolution["topic"]==topic].pivot(index="period", columns='terms')['importance']
        print("\n Topic --------------- ", topic)
        pivot.to_excel(f"pivot_{topic}.xlsx")
        print(pivot)
        

def extract_top_topics(cleaned_data, top_num):
    top_topics =  cleaned_data.groupby(by = ["topic"]).agg({"year":
                                                        "count"}).sort_values("year").index[-top_num:].tolist()
    return top_topics


def extract_number_trend(cleaned_data):
    agg = cleaned_data.groupby(by = ["topic", "year"]).agg({"topic":
                                                        "count"}).rename(columns={"topic":
                                                                                           "number_articles"}).reset_index()
    agg.to_excel("topics_articles_by_year.xlsx")
    return agg
    

def extract_topic_evolution(dtm, time_intervals_abstract, num_topics=85):

    df_all = pd.DataFrame()
    for topic_num in range(num_topics):
        topic_evo = dtm.print_topic_times(topic = topic_num)
        for t in range(len(topic_evo)):
            terms, importance = [], []
            period = time_intervals_abstract[t]
            for j in range(20):
                term = topic_evo[t][j][0]
                term_importance = topic_evo[t][j][1]
                terms.append(term)
                importance.append(term_importance)

            topic_slice_df = pd.DataFrame({"terms": terms,
                                          "importance": importance})
            topic_slice_df["period"] = period
            topic_slice_df["topic"] = topic_num
            
            df_all= pd.concat([df_all, topic_slice_df])
            
    df_all = df_all.reset_index(drop=True)      
    df_all.to_csv("topics_terms_evolution_all.csv")
    df_all.to_excel("topics_terms_evolution_all.xlsx")

    return df_all


def assign_topics(dtm, cleaned_data):
    topic_assignement = []
    for i in range(len(cleaned_data)):
        index = np.argmax(dtm.doc_topics(i))
        topic_assignement.append(index)
    
    cleaned_data["topic"] = topic_assignement
    return cleaned_data
   
    
def model_lda(num_topics, corpus, dictionary, num_words):
    np.random.seed(609)
    model = gensim.models.LdaMulticore(
        corpus, num_topics=num_topics, id2word=dictionary, passes=2, workers=4
    )
    topics = model.show_topics(num_words=num_words, log=False, formatted=False)
    return model, topics


def get_metrics(lda_model, corpus, dictionary):
    perplexity = lda_model.log_perplexity(corpus)

    coherence_lda = CoherenceModel(
        model=lda_model, corpus=corpus, dictionary=dictionary, coherence="u_mass"
    )
    coherence_u = coherence_lda.get_coherence()

    return perplexity, coherence_u


def explore_topic_number(
    corpus, dictionary, num_words, time_slices, time_intervals, min_articles
):

    start = 0

    columns = ["period", "num_topics", "perplexity", "coherence_u"]
    topics_overview = pd.DataFrame(columns=columns)

    for i in range(len(time_slices)):
        number_articles = time_slices[i]

        end = min(start + number_articles, len(corpus))
        max_topics = int(np.sqrt(number_articles))
        min_topics = int(np.sqrt(max_topics))

        period = time_intervals[i]

        for num_topics in range(min_topics, max_topics):
            model, topics = model_lda(
                num_topics, corpus[start:end], dictionary, num_words
            )

            perplexity, coherence_u = get_metrics(model, corpus[start:end], dictionary)

            topics_overview = topics_overview.append(
                {
                    "period": period,
                    "num_topics": num_topics,
                    "perplexity": perplexity,
                    "coherence_u": coherence_u,
                },
                ignore_index=True,
            )

        start = end

    topics_overview.to_csv("topics_overview.csv")

    return topics_overview


def explore_topic_number_all_data(
        corpus, dictionary, num_words, time_slices, time_intervals, min_articles
):

    columns = ["period", "num_topics", "perplexity", "coherence_u"]
    topics_overview = pd.DataFrame(columns=columns)

    num_alternatives = [75, 85, 95, 100, 110, 115, 120, 150, 170, 200, 250, 300]

    for num_topics in num_alternatives:
        model, topics = model_lda(
            num_topics, corpus, dictionary, num_words
        )

        perplexity, coherence_u = get_metrics(model, corpus, dictionary)

        topics_overview = topics_overview.append(
            {
                "period": "all",
                "num_topics": num_topics,
                "perplexity": perplexity,
                "coherence_u": coherence_u,
            },
            ignore_index=True,
        )
    topics_overview.to_csv("topics_overview_all_data.csv")

    return topics_overview


def select_topic_number(topics_overview):
    num_recommended_topics = topics_overview.loc[
        topics_overview.groupby("period")["perplexity"].idxmin()
    ]["num_topics"].max()

    print("Number of recommended topics       ", num_recommended_topics)
    return num_recommended_topics
