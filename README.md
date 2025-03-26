## Overview ## 
This project implements the methodology presented in 
https://doi.org/10.48550/arXiv.2406.10541, aimed at automating the identification of High-Value Datasets (HVDs) on Open Government Data (OGD) portals. The methodology employs a quantitative approach based on a detailed analysis of user interest, derived from data usage statistics, thereby minimizing the need for human intervention.

## Methodology ##
The proposed method involves extracting download data, analyzing metrics to identify high-value categories, and comparing HVD datasets across portals. The workflow consists of four main steps:

- Download dataset metadata from selected portals and extract usage information for the assigned categories.
- Calculate metrics (i.e., $HVD_i$) for each portal.
- Standardize and align the categories.
- Compute $HVD_{i,c}$ for the aligned categories.

## Input Data ##
The methodology is exemplified using two input datasets:
- A list of 100 U.S. citizen portals [portals.json](portals.json), containing dataset categorization information.
- A list of target portals where the identification of high-value datasets is to be performed.
The notebook [US_HVD_Report.ipynb](code/US_HVD_Report.ipynb) provides an implementation example of the methodology.

## Requirements ##
- Python >= 3.8
- Required packages listed in requirements.txt
