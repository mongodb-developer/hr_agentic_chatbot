# HR Agentic Chatbot

This project implements an HR Chatbot using LangChain, MongoDB, and OpenAI's language models. It includes synthetic data generation, embedding creation, and a chatbot interface for querying HR-related information.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Synthetic Data Generation](#synthetic-data-generation)
5. [Data Ingestion and Embedding Generation](#data-ingestion-and-embedding-generation)
6. [Running the Chatbot](#running-the-chatbot)
7. [Project Structure](#project-structure)
8. [Contributing](#contributing)
9. [License](#license)

## Prerequisites

- Python 3.8+
- MongoDB
- OpenAI API key
- Git (for version control)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/hr-agentic-chatbot.git
   cd hr-agentic-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root and add the following variables:
   ```
   MONGO_URI=your_mongodb_connection_string
   OPENAI_API_KEY=your_openai_api_key
   ```

2. Replace `your_mongodb_connection_string` with your actual MongoDB connection string and `your_openai_api_key` with your OpenAI API key.

## Synthetic Data Generation

To generate synthetic data for companies, workforce, and employees:

1. Navigate to the `data` directory:
   ```bash
   cd data
   ```

2. Run the synthetic data generation script:
   ```bash
   python synthetic_data_generation.py
   ```

This will create JSON files (`companies.json`, `workforce.json`, `employees.json`) in the `data` directory.

## Data Ingestion and Embedding Generation

To ingest the synthetic data into MongoDB and generate embeddings for employees:

1. Ensure you're in the project root directory.

2. Run the data ingestion script:
   ```bash
   python ingestion.py
   ```

This script will:
- Read the JSON files from the `data` directory
- Generate embeddings for employee data using OpenAI's API
- Insert the data (including embeddings) into MongoDB

## Running the Chatbot

To start the HR Chatbot:

1. Ensure you're in the project root directory.

2. Run the main script:
   ```bash
   chainlit run app.py -w
   ```

3. Open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:8000`).

4. Interact with the chatbot through the web interface.

## Project Structure

```
HR_AGENTIC_CHATBOT/
│
├── .chainlit/
├── .files/
├── data/
│   ├── __init__.py
│   ├── companies.json
│   ├── employees.json
│   ├── ingestion.py
│   ├── synthetic_data_generation.py
│   └── workforce.json
│
├── mongodb/
│   ├── __init__.py
│   ├── checkpointer.py
│   └── connect.py
│
├── tools/
│   ├── google_tools.py
│   └── mongodb_tools.py
│
├── .env
├── .gitignore
├── agent.py
├── app.py
├── chainlit.md
├── config.py
├── credentials.json
├── db_utils.py
├── graph.py
├── README.md
├── requirements.txt
├── temp.py
├── token.json
└── utilities.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.