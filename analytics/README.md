# Analytics Pipeline

## Overview

This module performs an end-to-end analysis of the Titanic dataset. The workflow includes data profiling, cleaning, exploratory data analysis, feature engineering, classification, class-imbalance handling, hyperparameter tuning, regression analysis, and model persistence.

The objective of the classification task is to predict passenger survival. A separate regression task is used to predict passenger fare.

## Dataset

The Titanic dataset is loaded using Seaborn and saved locally as `titanic.csv` so that the analysis can be reproduced without downloading the dataset again.

The dataset contains passenger information including age, sex, passenger class, fare, family information, embarkation location, and survival status.

## Project Files

- `01_eda.ipynb` - data loading, profiling, cleaning, feature engineering, and exploratory analysis
- `02_modeling.ipynb` - classification, model evaluation, imbalance handling, tuning, regression, and model persistence
- `titanic.csv` - locally saved raw dataset
- `titanic_cleaned.csv` - cleaned dataset
- `outputs/` - generated model evaluation results
- `models/` - saved fitted machine-learning pipeline

## Data Cleaning

Missing-value percentages were calculated before cleaning.

The following strategy was used:

- Columns with less than 5% missing data were handled by removing the affected rows.
- `age`, which had moderate missingness, was imputed using the median.
- `deck` was removed because it contained a very high proportion of missing values.
- Duplicate rows were checked and removed where necessary.
- Numeric variables were examined for outliers using the IQR method.
- Extreme fare values were capped rather than removing passenger records.

These decisions were made to preserve useful observations while reducing the effect of missing and extreme values.

## Feature Engineering

An `age_band` feature was created to group passengers into interpretable age categories.

Categorical features used for modeling are handled through one-hot encoding inside the machine-learning preprocessing pipeline.

Numeric variables are imputed and scaled as part of the pipeline.

## Exploratory Data Analysis

The analysis includes both univariate and bivariate exploration.

Key visualizations include:

- Survival by sex
- Survival by passenger class
- Age distribution split by survival
- Fare distribution by passenger class
- Correlation heatmap
- Survival across engineered age bands

Each visualization is followed by a written interpretation in the EDA notebook.

## Classification

Three classification algorithms were evaluated:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The data was split into training and testing sets before preprocessing. Stratified sampling was used to preserve the target-class distribution.

Preprocessing was implemented using scikit-learn `ColumnTransformer` and `Pipeline` so preprocessing steps are learned from the training data rather than the test data.

Models were evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- ROC curve
- ROC-AUC

The final model recommendation is based primarily on F1-score while also considering the other evaluation metrics.

## Class Imbalance

Three Logistic Regression training approaches were compared:

- Baseline model
- `class_weight="balanced"`
- SMOTE

SMOTE was applied only to the training data. The original test set was kept unchanged.

Precision, recall, and F1-score were compared to determine the effect of each imbalance-handling approach.

## Random Forest Tuning

Random Forest hyperparameters were tuned using `GridSearchCV`.

The search included:

- `n_estimators`
- `max_depth`
- `max_features`

The tuned Random Forest was also configured with `oob_score=True`, and its out-of-bag score was reported.

## Regression

A separate multivariate Linear Regression task was performed using `fare` as the target variable.

The regression model was evaluated using:

- MAE
- RMSE
- R²
- Adjusted R²

A residual plot was also examined to assess the pattern and spread of prediction errors.

## Model Persistence

The selected classification pipeline is saved using `joblib`.

The complete pipeline is stored rather than only the classifier. This preserves preprocessing and model logic together and allows raw passenger data to be passed directly to the reloaded model.

## Installation

From the project root, install the required packages:

```bash
pip install pandas numpy seaborn matplotlib scikit-learn imbalanced-learn joblib notebook ipykernelS