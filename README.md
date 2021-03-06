# Analysis Pipeline for Nature News Articles

This README contains a description of all the data and code within this git.
It also contains the instructions on how to re-run the analyses using Docker.

## Contents
- [Overview](#overview)
- [Requirements](#Requirements)
- [Data overview](#Quick-data-folder-overview)
- [Code overview](#quick-code-overview)
- [Scraping](#Scraping)
- [Analysis Description](#Analysis-and-Results)
- [Running Docker](#Running-Docker)


## Overview

The code consists of scraping, text processing, and analysis sections.
An overview of the process is shown in the figure below.

**Overview of type of text extracted**
![Overview Text Extracted](figure_notebooks/illustrator_pdfs/nature_news_ex_fig1a.png)

**Overview of processing**
![Overview Processing](figure_notebooks/illustrator_pdfs/nature_news_ex_fig1b.png)

To run our code, we provide a docker container that has the required packages, reference data, and processed data.
Due to copyright issues, we can not provide the scraped text, but we do provide our scraping code in `./nature_news_scraper`.
We do provide the coreNLP processed data, word frequencies for each article, and further downstream derived data in our github repo and in the docker container.

## Requirements

To run re-run the analyses, you will need the following:

- 50GB of disk space (22GB for the data, 22GB for git-lfs cache, ~5GB for additional processes)
- At least 8G of RAM

## Quick data folder overview

-  `./data/reference_data/*`

     - has all annotation data and cached API data. 

- `./benchmark_data/*`

     - this contains the generated benchmark scraped output (`*_raw.tsv`) and the hand annotated benchmark `*_hand_annotated.tsv`

     - all links considered for scraping can be found here in `links.json`

     - all text scraped is in `links_crawled.json`

     - coreNLP output for each article is in `./coreNLP_output.json`

- `./author_data/*`

     - contains gender, name origin, and affiliations of the authors of either cited or background articles (Springer / Nature)
     
     - For Figure 2, the key files are the following:

          1) `./data/author_data/springer_author_gender.tsv` has the gender of first and last authors from a randomly selected 36K Springer articles from 2005-2020.

          2) `./data/author_data/nature_author_gender.tsv` has the gender of first and last authors from all Nature articles from 2005-2020.

          3) `./data/author_data/all_author_fullname.tsv` is the output after scraping and processing the citations from nature news articles for the first and last author information.

     - For figure 3, the key files are the following:

          - The quote data file is: `./data/author_data/all_speaker_fullname_pred.tsv`
          
          - The bg data file is: `./data/author_data/all_author_fullname_pred.tsv`

               - The three corpi are indexed by the `corpus` column:

                    1) `news_quotes`: __foreground__ est. name origin of Nature News quoted speaker 

                    2) `nature_last`: __background__ est. name origin of last author of Nature articles. 

                    3) `springer_last`: __background__ est. name origin of last author of a random subset of Springer articles. 

     - For Figure 4, the key files are the following:

          - `./data/author_data/all_author_country.tsv`

               - The four corpi are indexed by the `corpus` column:

               1) `nature_news`: __foreground__ country of a location mentioned in any Nature News article

               2) `news_citation`: __foreground__ country of Nature News cited authors affiliation. 

               3) `nature_articles`: __background__ country of author affiliation from Nature articles. 

               4) `springer`: __background__ country of author affiliation from random subset of Springer articles. 

               - The `num_entries` column denotes the number of articles with at least ONE author from a particular country

               - The `address.country_code` column denotes the UN 2-digit country code

          - `/data/author_data/all_author_country_95CI.tsv`

               - Bootstrap estimate of country mentions and citations


- `./scraped_data/*`

     - This contains all the scraped and processed data from the Nature News articles. This consists of coreNLP output, and processed quote and locations files. 

     - For Figure 2, the key files are the following:

          - `./data/scraped_data/quote_table_raw_20*.tsv` has all quotes with estimated gender for the speaker

     - For Figure 4, the key files are the following:

          - 3) `/data/scraped_data/location_table_raw_[YEAR]_[ARTICLE-TYPE].tsv`, which maps a country mention to a source articles id 





## Quick code overview

- `./utils/*` 

     - has all R helper functions for processing scraped text and plotting

- `./nature_news_scraper/*`

     - This contains all scraping code. Most is auto-generated by scrapy. The code relies upon [scrapy](https://docs.scrapy.org/en/latest/index.html) to crawl links and process the articles. 
     This code is found in [here](https://github.com/nrosed/nature_news_disparities/tree/main/nature_news_scraper), and most of which is automatically generated. 

     - To re-run all scraped processing, you will need to run 4 shell scripts described below.
     
          1) To run the scraper tool on the benchmark dataset, you run the shell script `./nature_news_scraper/run_scrape_benchmark.sh`.
          This runs an initial scrape to identify all articles in 2020, 2015, and 2010, then randomly chooses 10 from each year to write to a file. 

          2) To run the scraper tool on the full dataset, you run the shell script `./nature_news_scraper/run_target_year_scrape.sh`

          3) To get the author information for Nature research articles, you run the shell script `./nature_news_scraper/run_article_author_scrape.sh`

          4) To get the doi's of all cited articles in Nature News, you run the shell script `./nature_news_scraper/run_doi_scrape.sh`

- ` ./process_scraped_data/*`

     - this contains the scripts to pre-process the output from coreNLP into a format that will be used for comparison. 
     To run the scripts in this folder, you must run the scraper yourself in order to get the Nature News text.

     - to make the benchmark quote and location data, you run `run_process_all_years.sh` which runs the other scripts in the folder in the following order

          1. `process_scrape.R` processes the scrapy output before running coreNLP, if coreNLP output is not found

          2. coreNLP is run on the output if it doesn't already exist

          3. `process_scraped_data/process_corenlp_locations_corenlp_output.R` is run on coreNLP output for country comparisons. Generates `location_table_raw_[YEAR]_[ARTICLE-TYPE].tsv` files in `./data/scraped_data`

          4. `process_scraped_data/process_corenlp_quotes_corenlp_output.R` is run on coreNLP output for quote comparisons. Generates `quote_table_raw_[YEAR]_[ARTICLE-TYPE].tsv` files in `./data/scraped_data`

          5. `process_scraped_data/process_corenlp_freq_corenlp_output.R` is run on coreNLP output to report word frequencies for each article. Generates `freq_table_raw.tsv` in `./data/scraped_data`

- `./process_doi_data/*`

     - this contains all Springer API calls and processing scripts for articles from the background set or that were cited by a Nature News article. To re-run these scripts, you only need to run `process_doi_data/run_background_scrapes.sh`. However, you will need to provide your personal Springer API key. You can get a key by registering here: [https://dev.springernature.com/](https://dev.springernature.com/). Also note that this script may exceed your API key allocation and require manual re-run.

- `./analysis_scripts/*`

     - this contains all in-depth analysis scripts. Each analysis is summarized in an R markdown notebook. The analysis may be out of date and need to be re-run. The most up-to-date analyses are located in `./figure_notebooks/`

- `./figure_notebooks/*`

     - this contains all analysis scripts to generate the main and supplemental figures. Each analysis is summarized in an R markdown notebook.

- `./analyze_benchmark_data/*`

     - this contains all benchmark analysis scripts. To view the analysis on github you can view it in `supp_fig1.md`

- `./name_lstm_models/*`

     - this contains the models for predicting name origin. This model is taken from the following github repository: [github repo](https://github.com/greenelab/wiki-nationality-estimate/raw/7425af1021f8a5c00aad789ebcaef67c5fe427bb/models/). It is described in this manuscript: [Analysis of ISCB honorees and keynotes reveals disparities](https://doi.org/ggr64p)



## Scraping

To re-run all scraping, you will need to run the code in `./nature_news_scraper/*`.
Refer to the description of this code folder above for instrictions on how to re-run it.
It should be noted that scraping is a fragile process and as websites updates, scraping code will fail.
Furthermore, articles may no longer be indexed in the same way.
To ensure reproducability without violating copyright, we provide the coreNLP output and the word frequencies of all the news articles.

  
## Analysis and Results
  
All analyses are described in detail in our manuscript on github which was created using [Manubot](https://manubot.org/): [manuscript github repo](https://github.com/greenelab/nature_news_manuscript).

All main and supplemental figures can be re-created by re-running the associated R markdown file in `./figure_notebooks/*`.

## Running Docker

### set-up environment
1) You must have git-lfs and docker installed.
2) (optional) You will need to obtain a _Springer_ API key if you want to re-run the processing code after scraping. Once you have a key, update the `.env_template` with your _Springer_ API key (or you can keep the dummy key if you will not run the API calls)
3) rename the .env_template to .env

### build image
1) run `./build_image.sh`. 
This may take a while, building the r packages can take 30 minutes to an hour.

### remake figures
1) To recreate figures, run the entrypoint script, described below 
```
./run_docker.sh figures [--rerun-bootstrap] <figure_name|clean>

     --rerun-bootstrap: (optional) recomputes bootstrap estimates 
                        from scratch (expensive)

     figure_name: recreates a specific figure, or if 
                  "all" is specified all of them.
                  available options: 'figure1', 'figure2',
                                    'figure3', 'figure4', 
                                    'supplemental1', 'all'

     clean: removes all intermediate and final figure artifacts,
            and the bootstrap data cache"
```

If you would like to re-run the scraper and therefore all downstream processing, you will need to re-run the shell scripts in the following folders:

     ./nature_news_scraper/*
     ./process_scraped_data/*
     ./process_doi_data/*

The directions on how to run them are provided in the [Quick code overview](#quick-code-overview) section above.
Once the scraping and pre-processing has completed successfully, you can run `./run_docker.sh figures all` to recreate all the figures.