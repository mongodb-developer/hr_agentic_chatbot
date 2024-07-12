# HR Agentic Chatbot

This project implements an HR Chatbot using LangChain, MongoDB, OpenAI's language models, and Google APIs. It includes synthetic data generation, embedding creation, and a chatbot interface for querying HR-related information and interacting with Google services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Google API Setup](#google-api-setup)
5. [Synthetic Data Generation](#synthetic-data-generation)
6. [Data Ingestion and Embedding Generation](#data-ingestion-and-embedding-generation)
7. [Running the Chatbot](#running-the-chatbot)
8. [Project Structure](#project-structure)
9. [Contributing](#contributing)
10. [License](#license)

## Prerequisites

- Python 3.8+
- MongoDB
- OpenAI API key
- Google Cloud Platform account
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

## Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the following APIs for your project:
   - Google Drive API
   - Google Docs API
   - Gmail API
4. Create credentials (OAuth 2.0 Client ID) for a Desktop application:
   - Go to "Credentials" in the left sidebar.
   - Click "Create Credentials" and select "OAuth client ID".
   - Choose "Desktop app" as the application type.
   - Download the client configuration file and rename it to `credentials.json`.
   - Place `credentials.json` in the root directory of the project.
5. The first time you run the application, it will prompt you to authorize access:
   - A browser window will open asking you to log in to your Google account.
   - Grant the requested permissions.
   - The application will then create a `token.json` file in the project root.

Note: Keep `credentials.json` and `token.json` secure and do not share them publicly.

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
   python data/ingestion.py
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
   chainlit run app.py
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
├── credentials.json  # Google OAuth 2.0 credentials
├── db_utils.py
├── graph.py
├── README.md
├── requirements.txt
├── temp.py
├── token.json  # Generated after first Google auth
└── utilities.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.