# RingScope — Financial Fraud Network Detection & Risk Intelligence

RingScope is a data analytics project that uses transaction-network analysis to identify recurring transaction-cycle structures and prioritize candidate networks for further investigation.

The project combines Python, SQL, NetworkX, and Power BI to transform transactional data into structured investigation insights.

> **Important:** The dataset used in this project is synthetic. Fraud labels are used for analytical evaluation and do not represent confirmed real-world fraud.

---

## Problem Statement

Traditional transaction analysis often examines accounts and transactions individually. This can make it difficult to identify recurring relationships where multiple accounts repeatedly transact with one another.

RingScope approaches the problem as a network-analysis task:

- Accounts are represented as **nodes**
- Transactions are represented as **directed edges**
- Recurring three-account transaction cycles are identified
- Overlapping cycles are grouped into candidate networks
- Structural and transaction-level features are engineered for investigation
- Results are presented through an interactive Power BI dashboard

---

## Dataset

RingScope uses the **AMLSim `aml_20k_combined` synthetic transaction dataset**.

### Dataset size

| Dataset | Records |
|---|---:|
| Accounts | 20,000 |
| Transactions | 120,558 |
| Fraud-labeled accounts | 1,804 |
| Fraud-label rate | 9.02% |

The dataset contains account-level information such as fraud labels, initial balances, and fraud-step information, along with transaction-level source accounts, target accounts, transaction values, and timestamps.

---

## Methodology

### 1. Data Validation

The raw account and transaction data were inspected for:

- Missing values
- Duplicate transactions
- Self-transactions
- Account-label consistency
- Transaction structure and ranges

---

### 2. SQL Analysis and EDA

SQL and Python-based analysis were used to understand:

- Transaction volumes
- Account activity
- Incoming and outgoing transaction behaviour
- Fraud-label distributions
- Transaction-value patterns
- Basic account-level differences

---

### 3. Transaction Network Construction

The transaction data was transformed into a directed graph using NetworkX.

- **Nodes** → accounts
- **Edges** → transactions
- **Edge values** → transaction amounts

This representation makes it possible to study relationships between accounts rather than treating every transaction independently.

---

### 4. Transaction-Cycle Detection

RingScope identifies recurring **three-account transaction cycles**.

Each detected cycle was subsequently validated against the transaction data to ensure that the required directed relationships actually existed.

**548 valid three-account transaction cycles** were identified.

---

### 5. Candidate Network Formation

Validated cycles that shared accounts were grouped into candidate networks.

This resulted in:

- **548 validated transaction cycles**
- **374 candidate network groups**
- **66 multi-cycle candidate groups**

The candidate groups provide a structured way to investigate recurring and overlapping transaction relationships.

---

### 6. Feature Engineering

Candidate-level analytical features were created, including:

- Account count
- Cycle count
- Internal transaction count
- Internal transaction value
- Incoming transaction value
- Outgoing transaction value
- Internal value ratio
- Repeated account count
- Repeated account ratio
- Highest account participation
- Highest participation share
- Fraud-label count
- Fraud-label rate

These features are used to describe the structure and transaction activity of candidate networks.

---

### 7. Structural Analysis

Multi-cycle candidate networks were examined based on how repeatedly accounts participated across overlapping cycles.

The analysis provides an exploratory structural classification such as:

- Highly concentrated
- Moderately concentrated
- Not applicable — single cycle

These classifications are intended as **investigative signals**, not definitive fraud classifications.

---

## Key Findings

RingScope identified **374 candidate network groups** from **548 validated three-account transaction cycles**.

Most candidate groups consisted of a single validated cycle, while **66 groups contained multiple overlapping cycles**.

The largest identified candidate group, **Candidate 11**, contained:

- **44 accounts**
- **45 validated transaction cycles**
- **140 internal transactions**
- Approximately **35.99K** in internal transaction value
- **21 fraud-labeled accounts**
- An exploratory structure classification of **Moderately concentrated**

These results demonstrate how graph-based analysis can surface recurring transaction structures that may warrant further investigation.

---

## Power BI Dashboard

The project includes a three-page Power BI dashboard.

### 1. Network Overview

Provides a high-level view of:

- Ring candidate groups
- Validated transaction cycles
- Cycles containing fraud labels
- Candidate-group distribution
- Fraud-label distribution across cycles

### 2. Candidate Investigation

Allows users to select a candidate network and examine:

- Accounts involved
- Validated cycles
- Transaction activity
- Internal transaction value
- Fraud-label count
- Account participation across overlapping cycles
- Exploratory structure type

### 3. Candidate 11 Case Study

Provides a focused investigation view of the largest identified candidate group, showing its:

- Account count
- Cycle count
- Internal transaction count
- Internal transaction value
- Structural classification
- Investigation summary

---

## Project Structure

```text
RingScope/
│
├── data/
│   └── raw/
│       ├── aml_20k_combined/
│       │   ├── nodes.csv
│       │   ├── transactions.csv
│       │   └── metadata.txt
│       │
│       └── archive/
│
├── dashboards/
│   └── RingScope_Dashboard.pbix
│
├── notebooks/
│   └── 01_data_understanding.ipynb
│
├── outputs/
│   ├── final_candidate_features.csv
│   ├── candidate_investigation_analysis.csv
│   ├── candidate_structure_analysis.csv
│   ├── cycle_investigation_table.csv
│   └── ...
│
├── src/
│   ├── build_graph.py
│   ├── detect_cycles.py
│   ├── validate_cycles.py
│   ├── extract_ring_candidates.py
│   ├── create_final_candidate_features.py
│   └── ...
│
├── requirements.txt
└── README.md