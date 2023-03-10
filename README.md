## About
This repository contains code that pulls up-to-date publication data from OpenAlex API and the generated CSV files in the `csv` folder.

## openAlex
[openAlex](https://docs.openalex.org/) is a open source API that offers hundreds of millions of interconnected entities across the global research system.


## Setup for openAlex python files
1. cd to openAlex
2. Load the Jupyter Notebook (`jupyter notebook`)


## To obtain the up-to-date publication data

`Authors.ipynb`, `PaperAuthorAffiliations.ipynb`, and `Papers.ipynb` in the 'openAlex' folder retrieve publication data from the OpenAlex API. These programs send a request to the OpenAlex API using the requests module, extract the relevant data for each author/paper, preprocess the data to ensure accuracy, and export it into CSV files.

Running the three Python notebooks -- `Authors.ipynb`, `PaperAuthorAffiliations.ipynb`, and `Papers.ipynb` -- results in the retrieval of UW publication data from the OpenAlex API and the conversion of it into three CSV files: `author.csv` (65297 rows), `papers.csv` (332759 rows), and `paperAuthorAffiliations.csv` (1901583 rows).


## To learn more about the datasets

Check out our [data dictionary](https://docs.google.com/spreadsheets/d/1y_Jtng7HV7tWzaCAZaY8IQJ7MUMH6vxypSfgNVNuG6Y/edit#gid=0) to learn more about the details of our datasets, including a description of each field and its data type.


### Notes
By default, openAlex API only gives us the first 25 results of the list. So we used cursor paging to retrieve all author and paper data related to the University of Washington.




## CSV files
The 'openAlex/csv' folder contains `author.csv`, `papers.csv`, and `3_csv_files.zip`. Due to the large size of `paperAuthorAffiliations.csv` (1901583 rows), we compressed the 3 csv files into `3_csv_files.zip`.



## Problem Statement
How might the UW Office of Global Affairs (OGA) achieve up-to-date publication data so that faculties can build networks with international scholars to gain UW's global presence?


## Website to our MVP (Minimum Viable Product)
Link to our website with Dashboard: https://github.com/jamesjwkim/rosetta-rough


## **Teams:**
|  Name:   | Contact infomation：  |
|  ----  | ----  |
| Vivian Yu  | pwy8900@uw.edu|
| Kelly Wang | zwang28@uw.edu |
| Lucy Zhu  | xzhu22@uw.edu |
| Jiali Liu | jiali123@uw.edu |
| Jimwoo Kim | jinwoo11@uw.edu |
