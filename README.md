# CareerPilot — AI Career Intelligence Agent

CareerPilot is a **Generative AI-powered career intelligence agent** that helps candidates understand their skills, analyze job descriptions, identify skill gaps, and create personalized learning roadmaps.

Built using Google Gemini, Python, FastAPI, and React, CareerPilot combines LLM-powered analysis, AI agent tools, text embeddings, semantic search, and Retrieval-Augmented Generation (RAG) to deliver personalized career guidance.

## 🚀 Features

- **Resume Analysis:** Upload a PDF resume and extract relevant candidate information and skills.
- **Job Description Analysis:** Analyze job requirements and identify the skills needed for a role.
- **Skill Gap Analysis:** Identify matching skills and missing skills for a target job.
- **Semantic Resume Search:** Retrieve relevant resume content using text embeddings and similarity search.
- **Personalized Learning Roadmaps:** Generate learning recommendations based on missing skills.
- **AI Career Chat:** Interact with the career agent and ask questions about your resume, skills, and career development.
- **Agent Tool Integration:** Use specialized tools for role analysis, skill matching, learning-plan generation, and resume search.
- **Session-Based Interaction:** Maintain conversational context during a session.

## 🧠 Generative AI Concepts Implemented

### 1. Large Language Models (LLMs)
Uses Google's Gemini model to understand natural-language input, analyze job descriptions, explain skill gaps, and generate career recommendations.

### 2. Prompt Engineering
Uses instructions and structured prompts to guide the model toward relevant career analysis and useful responses.

### 3. AI Agents and Tool Calling
The CareerPilot agent coordinates specialized tools for skill analysis, role matching, learning-plan generation, and resume search.

### 4. Text Embeddings
Uses Google's `gemini-embedding-001` model to convert text into numerical vector representations.

### 5. Retrieval-Augmented Generation (RAG)
Processes resume documents into searchable chunks, creates embeddings, and retrieves relevant content to support resume-related queries.

### 6. Semantic Search
Uses embedding similarity and cosine similarity to find relevant information based on meaning, rather than relying exclusively on exact keyword matches.

### 7. Skill Matching and Gap Analysis
Combines skill extraction, skill normalization, and matching logic to identify relevant skills and areas for improvement.

> Note: CareerPilot uses existing pretrained Gemini models. Model fine-tuning is not part of the current implementation.

## 🛠️ Technology Stack

### Generative AI
- Google Gemini
- Large Language Models (LLMs)
- Prompt Engineering
- AI Agents and Tool Calling
- Text Embeddings
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Cosine Similarity

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn
- Python-dotenv

### Frontend
- React
- Vite
- JavaScript
- HTML5
- CSS3
- REST API integration

### Document Processing
- PDF text extraction
- Text chunking
- Resume section parsing
- Embedding generation and retrieval

## 🏗️ Project Structure

```text
careerpilot/
├── backend/
│   ├── api.py
│   ├── agent.py
│   ├── tools.py
│   ├── ingestion/
│   │   └── process_resume.py
│   ├── requirements.txt
│   ├── .env
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── README.md
└── .gitignore
```

*The structure above describes the main project components. Additional files and directories may exist in your local project.*

## ⚙️ Prerequisites

Install the following before running CareerPilot:

- Python 3.11
- Node.js and npm
- A Google Gemini API key

## 💻 Local Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd careerpilot
```

Replace the placeholder with your repository URL.

### 2. Configure the Backend

Open a terminal and navigate to the backend:

```bash
cd backend
```

Create and activate a Python virtual environment on Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

Install the dependencies:

```cmd
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own key. Never commit your `.env` file or expose your API key publicly.

### 3. Start the Backend

From the `backend` directory, run:

```cmd
uvicorn api:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation, when enabled by FastAPI, is available at:

```text
http://127.0.0.1:8000/docs
```

### 4. Start the Frontend

Open a second terminal:

```cmd
cd C:\Users\Ranji\OneDrive\Desktop\careerpilot\frontend
npm install
npm run dev
```

Open the local development URL displayed by Vite, typically:

```text
http://localhost:5173
```

Keep both the backend and frontend running while testing the application.

## 🔌 API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/resume/upload` | Upload and process a resume |
| `POST /api/analysis` | Run career or skill analysis |
| `POST /api/chat` | Interact with the CareerPilot agent |

The exact request bodies, response formats, and required fields should be checked in `backend/api.py`.

## 🔐 Environment Variables

Configure private credentials through environment variables.

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Authenticates requests to Google Gemini |

Never commit API keys, passwords, tokens, or other secrets to GitHub.

## 🧪 Testing

Test the application by checking the following workflows:

- Resume PDF upload and processing.
- Resume skill extraction.
- Job-role and skill-gap analysis.
- Missing-skill identification.
- Learning-plan generation.
- Semantic search over resume content.
- AI career chat and follow-up questions.
- Frontend-to-backend API communication.
- Error handling for invalid files and API failures.

## 🔮 Future Enhancements

- Support multiple resumes and job descriptions.
- Add job recommendations based on candidate skills.
- Integrate a dedicated vector database if needed.
- Add authentication and persistent user profiles.
- Track learning progress and completed skills.
- Improve evaluation of resume-to-job matching.
- Add automated backend and frontend tests.
- Deploy the frontend and backend with secure environment configuration.

## 🎯 Project Goal

CareerPilot aims to make career preparation more personalized and practical by combining Generative AI, resume intelligence, semantic retrieval, and skill-gap analysis in one application.

## 👨‍💻 Author

Developed as a Generative AI and full-stack development project.
