# QUANTUMBLACK CONFIDENTIAL
#
# Copyright (c) 2016 - present QuantumBlack Visual Analytics Ltd. All
# Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property of
# QuantumBlack Visual Analytics Ltd. and its suppliers, if any. The
# intellectual and technical concepts contained herein are proprietary to
# QuantumBlack Visual Analytics Ltd. and its suppliers and may be covered
# by UK and Foreign Patents, patents in process, and are protected by trade
# secret or copyright law. Dissemination of this information or
# reproduction of this material is strictly forbidden unless prior written
# permission is obtained from QuantumBlack Visual Analytics Ltd.

"""Pipeline construction."""

from typing import Dict

from kedro.pipeline import Pipeline, node

from .nodes.lda import (corpus_creation,
                        tf_idf, explore_topic_number,
                        select_topic_number,
                        explore_topic_number_all_data, dtm_lda)

from .nodes.processing import clean_lower, create_processed
from .nodes.scraping import get_journal_links, get_all_links, extract_article_data


def create_pipelines(**kwargs) -> Dict[str, Pipeline]:  # pylint:disable=unused-argument
    """Create the project's pipeline.

    Args:
        kwargs: Ignore any additional arguments added in the future.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """

    pipeline = Pipeline(
        [
            # node(
            #     get_journal_links,
            #     inputs=[
            #         "params:publisher_link",
            #         "params:journal_id",
            #         "params:journal_volumes",
            #         "params:journal_max_issues",
            #         "params:start_year",
            #     ],
            #     outputs=["journal_links", "journal_years"],
            #     name="get all journal links",
            #     tags=["create links"],
            # ),
            # node(
            #     get_all_links,
            #     inputs=[
            #         "params:publisher_link",
            #         "params:period_start",
            #         "params:period_end",
            #         "journal_links",
            #         "journal_years",
            #     ],
            #     outputs=["articles_links", "articles_years"],
            #     name="get all articles links",
            #     tags=["scrapping"],
            # ),
            # node(
            #     extract_article_data,
            #     inputs=["articles_links", "articles_years"],
            #     outputs=["parsed_data", "unparsed_articles"],
            #     name="parse articles",
            #     tags=["scrapping", "parsing"],
            # ),
            node(
                clean_lower,
                inputs=["parsed_data", "params:var_list_text"],
                outputs="cleaned_data",
                name="clean text",
                tags=["clean", "lower", "process"],
            ),
            node(
                create_processed,
                inputs=[
                    "cleaned_data",
                    "params:var_title",
                    "params:time_var",
                    "params:stop_words",
                ],
                outputs=[
                    "time_intervals_title",
                    "time_slices_title",
                    "processed_title_data",
                ],
                name="tokenize and lemmatize title",
                tags=["lemma", "token", "time_slice", "process"],
            ),
            node(
                create_processed,
                inputs=[
                    "cleaned_data",
                    "params:var_abstract",
                    "params:time_var",
                    "params:stop_words",
                ],
                outputs=[
                    "time_intervals_abstract",
                    "time_slices_abstract",
                    "processed_abstract_data",
                ],
                name="tokenize and lemmatization of abstract",
                tags=["lemma", "token", "time_slice", "process"],
            ),
            node(
                corpus_creation,
                inputs="processed_abstract_data",
                outputs=["abstract_corpus", "abstract_dictionary"],
                name="create corpus and dictionary for abstract",
                tags=["corpus", "dictionary"],
            ),
            node(
                tf_idf,
                inputs="abstract_corpus",
                outputs="transformed_abstract_corpus",
                name="transform corpus for abstract with td-idf",
                tags=["corpus", "tf-idf", "transform"],
            ),  # Uncomment the below nodes in case of new data or re-assessment of topics number
            # node(
            #     explore_topic_number_all_data,
            #     inputs=[
            #         "transformed_abstract_corpus",
            #         "abstract_dictionary",
            #         "params:num_words_topic",
            #         "time_slices_abstract",
            #         "time_intervals_abstract",
            #         "params:min_articles",
            #     ],
            #     outputs="topics_overview",
            #     name="explore number of topics each period",
            #     tags=["topic", "evaluate"],
            # ),
            # node(
            #     select_topic_number,
            #     inputs="topics_overview",
            #     outputs="recommended_number_topics",
            #     name="select number of topics for dtm",
            #     tags=["topic", "evaluate"],
            # ),
            node(
                dtm_lda,
                inputs=[
                    "transformed_abstract_corpus",
                    "abstract_dictionary",
                    "time_slices_abstract",
                    "params:num_topics",
                ],
                outputs="dtm",
                name="dtm topic modelling",
                tags=["topic"],
            ),

        ]
    )

    return {"__default__": pipeline}
