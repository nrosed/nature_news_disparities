Fig3\_name\_origin
================
Natalie Davidson
5/3/2021

## Overview

This notebook generates figure 3 and additional supplemental figures.

The **data** it uses to build the plots are here:

This document compares two "foreground" datasets (estimated name origin of authors quoted + cited in nature news articles) and compares it to two possible "background" datasets (random sampling of 2.4K Springer articles, and all nature articles)

The quote data file is: `./data/author_data/all_speaker_fullname_pred.tsv` The bg data file is: `./data/author_data/all_author_fullname_pred.tsv`

The three corpi are indexed by the `corpus` column:

1.  `news_quotes`: **foreground** est. name origin of Nature News quoted speaker

2.  `nature_last`: **background** est. name origin of last author of Nature articles.

3.  `springer_last`: **background** est. name origin of last author of a random subset of Springer articles.

The **pdfs** included in the plots are here:

1.  `/figure_notebooks/illustrator_pdfs/`

The **setting + helper functions** to generate the plots are here:

1.  plotting related functions: `/utils/plotting_utils.R`

2.  reading + data processing related functions: `/utils/scraper_processing_utils.R` and `/analysis_scripts/analysis_utils.R`

3.  nautre research article and springer specific data processing functions: `/process_doi_data/springer_scripts/springer_scrape_utils.R`

## Read in the data

``` r
# first read in the quote data
name_pred_file = file.path(proj_dir, 
                             "/data/author_data/all_speaker_fullname_pred.tsv")
name_info_file = file.path(proj_dir, 
                             "/data/author_data/all_speaker_fullname.tsv")

quote_name_df = read_name_origin(name_pred_file, name_info_file)

# now read in the BG data
name_pred_file = file.path(proj_dir, 
                         "/data/author_data/all_author_fullname_pred.tsv")
name_info_file = file.path(proj_dir, 
                         "/data/author_data/all_author_fullname.tsv")
cite_name_df = read_name_origin(name_pred_file, name_info_file)

# we will only use last authors in the citations
cite_name_df = subset(cite_name_df, author_pos == "last")

# format the corpus for consistent naming across figures
cite_name_df$corpus[cite_name_df$corpus == "springer_articles"] = "springer_last"
cite_name_df$corpus[cite_name_df$corpus == "naturenews_citations"] = "citation"
cite_name_df$corpus[cite_name_df$corpus == "nature_articles"] = "nature_last"


# now we want to join these two datasets together
# we assume a quote is comparable to a publication
# so we will have a quote set as a doi
quote_name_df$doi = quote_name_df$quote
quote_name_df$corpus = "quote"


col_ids = c("author", "year", "name_origin", "corpus", "doi")
name_df = rbind(cite_name_df[,col_ids], quote_name_df[,col_ids])

head(name_df)
```

    ##                   author year name_origin        corpus
    ## 5           A A Bidokhti 2018   EastAsian springer_last
    ## 11            A Banerjee 2006  SouthAsian springer_last
    ## 20 A Cecile J W Janssens 2009    European      citation
    ## 22              A Cuxart 2005    European springer_last
    ## 23              A Cuxart 2005    European springer_last
    ## 24              A Cuxart 2005    European springer_last
    ##                                 doi
    ## 5     doi:10.1007/s12040-018-1013-5
    ## 11       doi:10.1038/sj.onc.1209944
    ## 20 doi:10.1097/GIM.0b013e3181b13a4f
    ## 22   doi:10.1186/1743-8454-2-S1-S51
    ## 23   doi:10.1186/1743-8454-2-S1-S29
    ## 24   doi:10.1186/1743-8454-2-S1-S28

## Process Data

### summarize the number of articles/quotes/citations considered in each corpus

``` r
citation_total = unique(subset(name_df, corpus == "citation", select=c(doi, year)) )
tot_prop_citation = citation_total %>% 
                group_by(year) %>% 
                summarise(n()) 
tot_prop_citation$corpus = "citation"

quote_total = unique(subset(name_df, corpus == "quote", select=c(doi, year)) )
tot_prop_quote = quote_total %>% 
                group_by(year) %>% 
                summarise(n()) 
tot_prop_quote$corpus = "quote"

springer_total = unique(subset(name_df, corpus == "springer_last", select=c(doi, year)) )
tot_prop_springer = springer_total %>% 
                group_by(year) %>% 
                summarise(n()) 
tot_prop_springer$corpus = "springer_last"

nature_total = unique(subset(name_df, corpus == "nature_last", select=c(doi, year)) )
tot_prop_nature = nature_total %>% 
                group_by(year) %>% 
                summarise(n()) 
tot_prop_nature$corpus = "nature_last"

num_art_tot = Reduce(rbind, list(tot_prop_citation, 
                                 tot_prop_quote,
                                 tot_prop_springer, 
                                 tot_prop_nature))
num_art_tot = data.frame(num_art_tot)
colnames(num_art_tot)[2] = "tot_articles"
```

### Get bootstrap estimates

``` r
# helper method for calling the bootstrap
get_subboot <- function(origin_id, curr_corpus, in_df, bootstrap_col_id="doi"){
    bootstrap_res = compute_bootstrap_location(subset(in_df, 
                                                      corpus==curr_corpus), 
                                              year_col_id = "year", 
                                              article_col_id = bootstrap_col_id, 
                                              country_col_id = "name_origin",
                                              country_agg = origin_id, 
                                              conf_int = 0.95)
    bootstrap_res$name_origin = origin_id
    
    # add a label for plotting later
    bootstrap_res$label = ""
    bootstrap_res$label[bootstrap_res$year == 2020] = 
        bootstrap_res$name_origin[bootstrap_res$year == 2020]
        

    return(bootstrap_res)

}

if(RERUN_BOOTSTRAP){
    
    # get the bootstrapped CI for each source data type
    citation_origin_df = NA
    for(curr_origin in unique(name_df$name_origin)){
        print(curr_origin)
        res = get_subboot(curr_origin, 
                          curr_corpus="citation",
                          name_df)
        citation_origin_df = rbind(citation_origin_df, res)
    }
    citation_origin_df = citation_origin_df[-1,]
    
    quote_origin_df = NA
    for(curr_origin in unique(name_df$name_origin)){
        print(curr_origin)
        res = get_subboot(curr_origin, 
                          curr_corpus="quote",
                          name_df)
        quote_origin_df = rbind(quote_origin_df, res)
    }
    quote_origin_df = quote_origin_df[-1,]
    
    
    springer_origin_df = NA
    for(curr_origin in unique(name_df$name_origin)){
        print(curr_origin)
        res = get_subboot(curr_origin, 
                          curr_corpus="springer_last",
                          name_df)
        springer_origin_df = rbind(springer_origin_df, res)
    }
    springer_origin_df = springer_origin_df[-1,]
    
    nature_origin_df = NA
    for(curr_origin in unique(name_df$name_origin)){
        print(curr_origin)
        res = get_subboot(curr_origin, 
                          curr_corpus="nature_last",
                          name_df)
        nature_origin_df = rbind(nature_origin_df, res)
    }
    nature_origin_df = nature_origin_df[-1,]
    
    
    # re-add corpus column for easy reference later
    citation_origin_df$corpus = "citation"
    quote_origin_df$corpus = "quote"
    springer_origin_df$corpus = "springer_last"
    nature_origin_df$corpus = "nature_last"
    
    all_bootstrap_df = Reduce(rbind, list(quote_origin_df,
                                       citation_origin_df,
                                       nature_origin_df,
                                       springer_origin_df))
    all_bootstrap_df$corpus = factor(all_bootstrap_df$corpus, levels = QUOTE_ANALYSIS_ORDER)
    
    outfile = file.path(proj_dir,"/figure_notebooks/tmp_files/fig3_tmp/all_bootstrap_df.tsv")
    write.table(all_bootstrap_df, outfile, sep="\t", quote=F, row.names=F)
}else{
    
    all_bootstrap_file = file.path(proj_dir,
                                      "/figure_notebooks/tmp_files/fig3_tmp/all_bootstrap_df.tsv")
    all_bootstrap_df = data.frame(fread(all_bootstrap_file))
    
    citation_origin_df = subset(all_bootstrap_df, corpus == "citation")
    quote_origin_df = subset(all_bootstrap_df, corpus == "quote")
    springer_origin_df = subset(all_bootstrap_df, corpus == "springer_last")
    nature_origin_df = subset(all_bootstrap_df, corpus == "nature_last")
    
}
```

## Make the Figures

### generate the overview plot

``` r
#### Overview plot of the number of considered "articles" by type
num_art_tot$corpus = factor(num_art_tot$corpus, levels = QUOTE_ANALYSIS_ORDER)
tot_art_gg = ggplot(num_art_tot, aes(x=as.numeric(year), y=tot_articles,
                              fill=corpus, color=corpus)) +
    geom_point() + geom_line() + theme_bw() + 
    xlab("Year of Article") + ylab("Number of Total Articles/Quotes/Citations") +
    ggtitle("Total number of Articles/Quotes/Citations per Corpus") + 
    scale_color_manual(values=QUOTE_ANALYSIS_COLOR) +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/tot_art_gg.pdf"),
       tot_art_gg, width = 5, height = 5, units = "in", device = "pdf")
```

### generate the citation plots

``` r
#### plot the overview of name origin by citation
citation_overview_gg = ggplot(citation_origin_df, aes(x=as.numeric(year), y=mean,
                          ymin=bottom_CI, ymax=top_CI,
                          fill=name_origin, label=label)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + geom_text_repel() + xlim(c(2005,2021))  +
    xlab("Year of Article") + ylab("Proportion of Citations") +
    ggtitle("Est. Proportion of the Cited Last Author Name Origin") + 
    scale_fill_brewer(palette="Set2") +
    theme(legend.position = "none")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/citation_overview_gg.pdf"),
       citation_overview_gg, width = 7, height = 5, units = "in", device = "pdf")

# plot by each name origin individually
citation_nature_indiv_full_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("nature_last", "citation")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Citations or Articles") +
    ggtitle(paste("Percentage Citations vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap(~ name_origin, scales = "free_y") +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/citation_nature_indiv_full_gg.pdf"),
       citation_nature_indiv_full_gg, width = 7, height = 5, units = "in", device = "pdf")


# plot by each name origin individually
citation_springer_indiv_full_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("springer_last", "citation")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Citations or Articles") +
    ggtitle(paste("Percentage Citations vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap(~ name_origin, scales = "free_y") +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/citation_springer_indiv_full_gg.pdf"),
       citation_springer_indiv_full_gg, width = 7, height = 5, units = "in", device = "pdf")



citation_nature_indiv_sub_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("nature_last", "citation") &
                                         name_origin %in% c("CelticEnglish", "EastAsian", "European")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Citations or Articles") +
    ggtitle(paste("Percentage Citations vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap(~ name_origin) +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/citation_nature_indiv_sub_gg.pdf"),
       citation_nature_indiv_sub_gg, width = 7, height = 5, units = "in", device = "pdf")
```

### generate the quote plots

``` r
#### plot the overview of name origin by quoted speaker
quote_overview_gg = ggplot(quote_origin_df, aes(x=as.numeric(year), y=mean,
                          ymin=bottom_CI, ymax=top_CI,
                          fill=name_origin, label=label)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + geom_text_repel() + xlim(c(2005,2021))  +
    xlab("Year of Article") + ylab("Proportion of Quotes") +
    ggtitle("Est. Proportion of Quoted Speakers' Name Origin") + 
    scale_fill_brewer(palette="Set2") +
    theme(legend.position = "none")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/quote_overview_gg.pdf"),
       quote_overview_gg, width = 7, height = 5, units = "in", device = "pdf")


# plot by each name origin individually
quote_nature_indiv_full_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("nature_last", "quote")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Quotes or Articles") +
    ggtitle(paste("Percentage Quotes vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap( ~ name_origin, scales = "free_y") +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/quote_nature_indiv_full_gg.pdf"),
       quote_nature_indiv_full_gg, width = 7, height = 5, units = "in", device = "pdf")

quote_springer_indiv_full_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("springer_last", "quote")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Quotes or Articles") +
    ggtitle(paste("Percentage Quotes vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap( ~ name_origin, scales = "free_y") +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/quote_springer_indiv_full_gg.pdf"),
       quote_springer_indiv_full_gg, width = 7, height = 5, units = "in", device = "pdf")


quote_nature_indiv_sub_gg = ggplot(subset(all_bootstrap_df, 
                                         corpus %in% c("nature_last", "quote") &
                                         name_origin %in% c("CelticEnglish", "EastAsian", "European")), 
                                aes(x=as.numeric(year), y=mean,
                                      ymin=bottom_CI, ymax=top_CI,
                                      fill=corpus)) +
    geom_point() + geom_ribbon(alpha=0.5) + geom_line(alpha=0.5) +
    theme_bw() + 
    xlab("Year of Article") + ylab("Percentage Quotes or Articles") +
    ggtitle(paste("Percentage Quotes vs Last Authorship by Name Origin")) + 
    scale_fill_manual(values=QUOTE_ANALYSIS_COLOR) +
    facet_wrap(~ name_origin) +
    theme(legend.position="bottom")

ggsave(file.path(proj_dir, "/figure_notebooks/tmp_files/fig3_tmp/quote_nature_indiv_sub_gg.pdf"),
       quote_nature_indiv_sub_gg, width = 7, height = 5, units = "in", device = "pdf")
```

### format main figure

``` r
plot_overview = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/illustrator_pdfs/nature_news_name_origin_schematic.pdf"))
plot_overview = image_annotate(plot_overview, "a", size = 20)

citation_overview_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/citation_overview_gg.pdf"))
citation_overview_gg = image_annotate(citation_overview_gg, "b", size = 30)

citation_nature_indiv_sub_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/citation_nature_indiv_sub_gg.pdf"))
citation_nature_indiv_sub_gg = image_annotate(citation_nature_indiv_sub_gg, "c", size = 30)


quote_overview_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/quote_overview_gg.pdf"))
quote_overview_gg = image_annotate(quote_overview_gg, "d", size = 30)

quote_nature_indiv_sub_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/quote_nature_indiv_sub_gg.pdf"))
quote_nature_indiv_sub_gg = image_annotate(quote_nature_indiv_sub_gg, "e", size = 30)


bottom_image <- image_append(image_scale(c(quote_overview_gg, quote_nature_indiv_sub_gg),3000), stack = FALSE)
middle_image <- image_append(image_scale(c(citation_overview_gg, citation_nature_indiv_sub_gg),3000), stack = FALSE)
full_image <- image_append(image_scale(c(plot_overview, middle_image, bottom_image), 3000), stack = TRUE)

print(full_image)
```

    ## # A tibble: 1 x 7
    ##   format width height colorspace matte filesize density
    ##   <chr>  <int>  <int> <chr>      <lgl>    <int> <chr>  
    ## 1 PNG     3000   3140 sRGB       TRUE         0 300x300

<img src="figure3_files/figure-markdown_github/make_fig1-1.png" width="3000" />

``` r
outfile = file.path(proj_dir,"/figure_notebooks/tmp_files/fig3_tmp/fig3_main.pdf")
image_write(full_image, format = "pdf", outfile)

outfile = file.path(proj_dir,"/figure_notebooks/tmp_files/fig3_tmp/fig3_main.png")
image_write(full_image, format = "png", outfile)
```

### format supp. figure

``` r
tot_art_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/tot_art_gg.pdf"))
tot_art_gg = image_annotate(tot_art_gg, "a", size = 20)

citation_nature_indiv_full_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/citation_nature_indiv_full_gg.pdf"))
citation_nature_indiv_full_gg = image_annotate(citation_nature_indiv_full_gg, "b", size = 30)

citation_springer_indiv_full_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/citation_springer_indiv_full_gg.pdf"))
citation_springer_indiv_full_gg = image_annotate(citation_springer_indiv_full_gg, "c", size = 30)

quote_nature_indiv_full_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/quote_nature_indiv_full_gg.pdf"))
quote_nature_indiv_full_gg = image_annotate(quote_nature_indiv_full_gg, "d", size = 30)

quote_springer_indiv_full_gg = image_read_pdf(file.path(proj_dir,
                                  "/figure_notebooks/tmp_files/fig3_tmp/quote_springer_indiv_full_gg.pdf"))
quote_springer_indiv_full_gg = image_annotate(quote_springer_indiv_full_gg, "e", size = 30)

springer_left = image_append(image_scale(c(citation_nature_indiv_full_gg, 
                                         quote_nature_indiv_full_gg), 3000), 
                           stack = TRUE)
nature_right = image_append(image_scale(c(citation_springer_indiv_full_gg, 
                                         quote_springer_indiv_full_gg), 3000), 
                           stack = TRUE)
bottom_panel = image_append(c(springer_left, nature_right), stack = FALSE)

full_image <- image_append(c(image_scale(tot_art_gg, 1500),  image_scale(bottom_panel, 3000)), 
                           stack = TRUE)
print(full_image)
```

    ## # A tibble: 1 x 7
    ##   format width height colorspace matte filesize density
    ##   <chr>  <int>  <int> <chr>      <lgl>    <int> <chr>  
    ## 1 PNG     3000   3643 sRGB       TRUE         0 300x300

<img src="figure3_files/figure-markdown_github/make_supp_fig-1.png" width="3000" />

``` r
outfile = file.path(proj_dir,"/figure_notebooks/tmp_files/fig3_tmp/fig3_supp.pdf")
image_write(full_image, format = "pdf", outfile)
outfile = file.path(proj_dir,"/figure_notebooks/tmp_files/fig3_tmp/fig3_supp.png")
image_write(full_image, format = "png", outfile)
```