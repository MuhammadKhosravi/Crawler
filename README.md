# Crawler
This is the answer to HW3 of Modern Information Retrieval, Fall 2022.

`scraper.py` is the implementation of a scraper that will get the news of Hamshahri website, in the specified interval. The result is stored in `dataset.csv`.

`Indexing.ipynb` is a jupyter-notebook that is responsible for storing the data in `dataset.csv` in an Elasitcsearch index.

`Query.ipynb` is a jupyter-notebook, in which I implemented a bunch of retrieval methods, inclueding boolean, tf-idf, fasttext, and also storing in elasticsearch.
