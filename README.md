# Trendychat

Trendychat is a core library designed to support applications utilizing large language models (LLMs). It includes comprehensive functionalities such as CMS, scheduled ETL processes, and bot-based interactions.

## Features

Trendychat powers several key services by providing the necessary backend support:
- **Content Management System (CMS)**: Facilitates the organization and management of digital content, which is crucial for dynamic LLM applications.
- **ETL Scheduling**: Automates the extraction, transformation, and loading of data to ensure that the LLMs have timely and relevant data feeds.
- **Bot Interactions**: Supports automated responses and user interactions through intelligent bots, enhancing the user experience and engagement.

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


## Architecture Diagram

Below is the architectural diagram illustrating the supported structure and flow of interactions within Trendychat. This visualization helps in understanding how different components are integrated.

![Architecture Diagram](pic/architecture.png)

