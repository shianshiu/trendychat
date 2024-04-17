# Trendychat

Trendychat is a core library designed to support applications utilizing large language models (LLMs). It includes comprehensive functionalities such as CMS, scheduled ETL processes, and bot-based interactions.

## Features

- **Content Management System (CMS)**: For organizing and managing digital content.
- **ETL Scheduling**: Automate the extraction, transformation, and loading of data.
- **Bot Interactions**: Facilitate automated responses and user interaction through bots.

## Installation

Install Trendychat using pip:

```bash
pip install trendychat
```
If you need to process PDF files, the unstructured package with PDF support must be installed separately due to its large size:

```bash
pip install unstructured"[pdf]"
```

## Design Philosophy

Inspired by the design principles of Langchain, Trendychat focuses on efficient data handling and processing. However, due to the rapid iteration in model API applications and the challenges of high dependency and maintenance in such environments, Trendychat has been architected with a redesigned approach to reduce dependency issues and ease maintenance.

