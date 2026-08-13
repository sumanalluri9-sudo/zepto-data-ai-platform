\## End-to-End Execution



\### Module 1 - Data Pipeline



Navigate to the data pipeline module:



```powershell

cd data\_pipeline

```



Install the required dependencies:



```powershell

pip install -r requirements.txt

```



Run the complete scraping, cleaning, currency conversion, database creation, SQL querying, and pandas comparison pipeline:



```powershell

python scrape\_books.py

```



The pipeline scrapes at least 60 books, cleans the dataset, converts GBP prices to INR using the fixed project rate of 1 GBP = 105.50 INR, creates the normalized SQLite database, executes the required SQL queries, and saves the generated outputs.



\### Module 2 - Analytics and Machine Learning



Navigate to the analytics module:



```powershell

cd analytics

```



Install the required dependencies:



```powershell

pip install -r requirements.txt

```



Start Jupyter Notebook:



```powershell

jupyter notebook

```



Run the notebooks in this order:



1\. `01\_eda.ipynb`

2\. `02\_modeling.ipynb`



Run all cells from top to bottom so the exploratory analysis, preprocessing, feature engineering, classification models, evaluation, imbalance handling, hyperparameter tuning, regression analysis, and model persistence steps are reproduced.



\### Module 3 - GenAI Policy Support Assistant



Navigate to the support assistant:



```powershell

cd support\_assistant

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



Create or refresh the ChromaDB vector database:



```powershell

python ingest.py

```



Start the FastAPI application:



```powershell

python -m uvicorn main:app --reload

```



The default configuration uses:



```text

MOCK\_LLM=1

```



This mode requires no external LLM API key while still performing real semantic retrieval against the local ChromaDB policy collection.



The API is available at:



```text

http://127.0.0.1:8000

```



The main endpoint is:



```text

POST /ask

```



Example request:



```json

{

&#x20; "query": "What is Zepto gift card validity?"

}

```



\### Docker



A Dockerfile is provided in `support\_assistant`.



Build the container with:



```powershell

docker build -t zepto-support-assistant .

```



Run it with:



```powershell

docker run -p 7860:7860 zepto-support-assistant

```



\## Design Decisions



\### Data Pipeline



The pipeline uses Books to Scrape as the source and performs automated scraping rather than manual data collection. Data is cleaned into appropriate numeric and boolean types. GBP prices are converted using the required fixed baseline rate of 1 GBP = 105.50 INR. Categories and books are stored separately in SQLite to maintain a normalized primary-key/foreign-key structure.



\### Analytics



The analytics workflow separates exploratory analysis from modeling using two notebooks. The EDA notebook focuses on understanding, cleaning, and visualizing the dataset. The modeling notebook performs feature preparation, classification, evaluation, class-imbalance handling, tuning, regression analysis, and model persistence.



\### Support Assistant



The support assistant uses local Sentence Transformer embeddings and ChromaDB so retrieval does not depend on a paid embedding service. LangGraph controls intent classification and conditional routing. Policy questions use retrieved Zepto policy context, while other questions follow a direct-answer route. Deterministic mock mode is the default so the graded baseline runs without an external LLM API key.

