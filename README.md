\# Zepto Data \& AI Platform



\## Capstone Project



This repository contains the capstone project for the Certificate Program in Artificial Intelligence and Machine Learning.



The project demonstrates an end-to-end Data and AI workflow through three modules:



1\. Data Pipeline

2\. Analytics and Machine Learning

3\. GenAI Policy Support Assistant



\## Repository Structure



```text

zepto-data-ai-platform/

├── data\_pipeline/

├── analytics/

├── support\_assistant/

├── .gitignore

└── README.md

```



\## Module 1: Data Pipeline



The `data\_pipeline` module implements a complete data engineering workflow using data scraped from Books to Scrape.



It includes:



\- Web scraping using Requests and BeautifulSoup

\- Data cleaning and type conversion

\- GBP to INR conversion using the fixed project rate of 1 GBP = 105.50 INR

\- Normalized SQLite database with primary and foreign key relationships

\- SQL queries using SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, IN/BETWEEN, and JOIN

\- Query results loaded into pandas using `pd.read\_sql()`

\- SQL JOIN results reproduced using `pd.merge()`

\- Generated query and analysis outputs



Detailed setup and execution instructions are available in `data\_pipeline/README.md`.



\## Module 2: Analytics and Machine Learning



The `analytics` module performs exploratory data analysis and machine learning using the Titanic dataset.



It includes:



\- Data profiling

\- Missing-value analysis

\- Data cleaning

\- Outlier handling

\- Exploratory data analysis

\- Data visualization

\- Feature engineering

\- Logistic Regression

\- Decision Tree

\- Random Forest

\- Model evaluation using Accuracy, Precision, Recall, F1 Score, and ROC-AUC

\- Class imbalance handling

\- SMOTE

\- Random Forest hyperparameter tuning

\- Regression analysis

\- Model persistence using Joblib



Detailed setup and execution instructions are available in `analytics/README.md`.



\## Module 3: GenAI Policy Support Assistant



The `support\_assistant` module implements a Zepto policy support assistant using local retrieval and a LangGraph workflow.



It includes:



\- 8 Zepto policy documents

\- Local embeddings using `all-MiniLM-L6-v2`

\- ChromaDB vector storage

\- Semantic document retrieval

\- LangGraph workflow

\- Intent classification

\- Conditional routing

\- Policy retrieval and answer generation

\- Direct-answer route for non-policy questions

\- Structured prompt engineering

\- Pydantic response validation

\- FastAPI `/ask` endpoint

\- Dockerfile for containerization



The default graded configuration uses:



```text

MOCK\_LLM=1

```



Mock mode does not require an external LLM API key. Policy questions still perform real ChromaDB retrieval.



Detailed setup, API usage, and architecture information are available in `support\_assistant/README.md`.



\## Technologies Used



\- Python

\- pandas

\- NumPy

\- Requests

\- BeautifulSoup

\- SQLite

\- scikit-learn

\- Matplotlib

\- Seaborn

\- imbalanced-learn

\- Joblib

\- LangGraph

\- ChromaDB

\- Sentence Transformers

\- FastAPI

\- Pydantic

\- Uvicorn

\- Docker



\## Running the Project



Each module contains its own README and dependency information.



Follow the instructions inside the corresponding module:



```text

data\_pipeline/README.md

analytics/README.md

support\_assistant/README.md

```



\## Git Workflow



The project uses Git for version control.



A feature branch was created for development, multiple commits were made during development, and the completed work was merged back into the `main` branch.



The repository preserves the commit history required for the capstone submission.

