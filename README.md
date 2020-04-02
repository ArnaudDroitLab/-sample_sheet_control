---
title: "sample sheet control"
author: "NGS Team"
date: "`r format(Sys.time(), '%d %B, %Y')`"
output:
  html_document:
    toc: true # table of content true
    toc_depth: 3 # upto three depths of heading (specified by #, ## and ###)
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo=T, eval=T, include=T, message=F, warning=F)
```

## Installation

* Requires:
    - python 3.7
    - <font size="4">[pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)</font>  library

## Running

* In the main directory:
    - python3 sample_sheet_control.py -s *Path/sample_sheet_to_verify_format*

## What is he doing

* General verification:
    - no other characters than numeric and dot for '*Concentration*' and '*Volume fourni*' columns
    - no other characters than **ATCG** in '*Indexseq*' column
    - no other characters than alphabetic for '*SampleName*', '*Index1*', '*Index2*' columns
    - no blank cells for all of these columns except '*Indexseq*'

* Sequence index verification:
    - for each lines groups (refering to *FlowCell* lines)
        - each sequences identifiers need to be unique
        - the couple of identifier (*I7 I5*) for one specific sample need to have the same length
        - no different length of sequences within the same columns
        - no blank cells for column *I7* sequences index column
        - blank cells are allowed in *I5* sequences index column only if all of these cells are empty for the line group

## Test

* Test verification:
    - in the test directory, several files are available for efficiency testing
        - sample_sheet_correct_format.xlsx **-->** correct format
        - sample_sheet_not_num_format.xlsx **-->** no numeric characters in '*Concentration*' and '*Volume fourni*' columns
        - sample_sheet_empty_cells_format.xlsx **-->** several blank cells through the file
        - sample_sheet_index_diff_len_by_lane_format.xlsx **-->**  several couple of identifier do not have the same length for group of lines one and two
        - sample_sheet_index_empty_cells_format.xlsx **-->** several blank cells for group of line one, two and three. the error occur only for groups one and two because the third group have all of is cells empty for *I5* column (*Paired or Single*).
        - sample_sheet_index_not_ATCG_format.xlsx **-->** several other characters than **ATCG** in '*Indexseq*'.
        - sample_sheet_index_not_listed_and_not_unique_format.xlsx **-->** several sequences index are not unique within the same group. several sequences are not listed by IDI and NEB index files.