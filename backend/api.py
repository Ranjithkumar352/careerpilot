
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, Field

from agent import CareerPilotAgent
from ingestion.process_resume import process_resume
from resume_ready import prepare_resume_for_careerpilot
from memory import ConversationMemory
from follow_up import handle_follow_up


# ======================================================
# CONFIGURATION
# ======================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="CareerPilot API",
    description="AI-powered career analysis and conversational career guidance",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://careerpilot-red.vercel.app",

    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ======================================================
# GEMINI CLIENT
# ======================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ======================================================
# SESSION STORAGE
# ======================================================

# Local development only. Sessions are lost on server restart.
sessions = {}


# ======================================================
# REQUEST MODELS
# ======================================================

class AnalyzeRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    role: str = Field(min_length=1, max_length=120)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=4000)


# ======================================================
# RESPONSE SERIALIZATION
# ======================================================

def to_json_safe(value):
    """Convert common Python containers and Pydantic models to JSON-safe data."""

    if hasattr(value, "model_dump"):
        return to_json_safe(value.model_dump())

    if hasattr(value, "dict") and callable(value.dict):
        return to_json_safe(value.dict())

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, Path):
        return str(value)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


# ======================================================
# SESSION HELPERS
# ======================================================

def get_session(session_id):
    session = sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload your resume again.",
        )

    return session


# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "CareerPilot API is running.",
    }


# ======================================================
# RESUME UPLOAD
# ======================================================

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume.",
        )

    session_id = uuid.uuid4().hex
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    resume_path = session_dir / "resume.pdf"
    index_path = session_dir / "resume_index.json"

    try:
        total_size = 0

        with resume_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Resume file must be 5 MB or smaller.",
                    )

                destination.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Process this resume and create its independent search index.
        process_resume(
            str(resume_path),
            store_path=str(index_path),
        )

        resume_data = prepare_resume_for_careerpilot(
            store_path=str(index_path),
        )

        suggested_roles = resume_data["suggested_roles"]

        # Create an agent linked to this resume.
        agent = CareerPilotAgent(
            resume_store_path=str(index_path),
            thread_id=f"careerpilot-{session_id}",
        )

        agent.state.resume_evidence = resume_data["resume_evidence"]
        agent.state.suggested_roles = suggested_roles
        agent.state.phase = "waiting_for_role"

        # Each uploaded resume gets its own agent and conversation memory.
        sessions[session_id] = {
            "agent": agent,
            "memory": ConversationMemory(),
            "index_path": str(index_path),
            "session_dir": str(session_dir),
        }

        return {
            "status": "success",
            "message": "Resume uploaded and processed successfully.",
            "session_id": session_id,
            "suggested_roles": to_json_safe(suggested_roles),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Resume upload failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Resume processing failed. Check the backend terminal.",
        ) from exc

    finally:
        await file.close()


# ======================================================
# ROLE ANALYSIS
# ======================================================

@app.post("/api/analysis")
def analyze_selected_role(request: AnalyzeRequest):
    session = get_session(request.session_id)
    agent = session["agent"]

    role = request.role.strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Please select a valid career role.",
        )

    # Only allow roles suggested for this uploaded resume.
    allowed_roles = {
        item if isinstance(item, str) else item.get("role", "")
        for item in agent.state.suggested_roles
    }

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Please select one of the suggested career roles.",
        )

    try:
        response = agent.process_role(role)

        if response is None:
            raise HTTPException(
                status_code=400,
                detail="CareerPilot could not select that role.",
            )

        if agent.state.phase == "error":
            raise HTTPException(
                status_code=422,
                detail="Career analysis failed because resume evidence was unavailable.",
            )

        session["agent"] = agent

        return {
            "status": "success",
            "session_id": request.session_id,
            "target_role": agent.state.target_role,
            "response": response,
            "role_analysis": to_json_safe(agent.state.role_analysis),
            "candidate_analysis": to_json_safe(agent.state.candidate_analysis),
            "match_result": to_json_safe(agent.state.match_result),
            "learning_plan": to_json_safe(agent.state.learning_plan),
            "resume_evidence": agent.state.resume_evidence,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Role analysis failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Role analysis failed. Check the backend terminal.",
        ) from exc


# ======================================================
# CONVERSATIONAL CHAT
# ======================================================

@app.post("/api/chat")
def chat(request: ChatRequest):
    session = get_session(request.session_id)

    agent = session["agent"]
    memory = session["memory"]

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    # Save the user's message before generating a response.
    memory.add_user_message(message)

    try:
        if agent.state.phase == "completed":
            # Reuse the existing follow-up logic and completed analysis.
            answer = handle_follow_up(
                user_message=message,
                state=agent.state,
                memory=memory,
            )

        else:
            # The resume has been processed, but the user may not
            # have selected a career role yet.
            history = memory.get_history()[:-1]

            prompt = f"""
You are CareerPilot, an AI career assistant.

The user's resume has been processed successfully.
They may ask questions before selecting a suggested role.

RESUME EVIDENCE:
{agent.state.resume_evidence}

SUGGESTED CAREER ROLES:
{to_json_safe(agent.state.suggested_roles)}

PREVIOUS CONVERSATION:
{to_json_safe(history)}

CURRENT USER QUESTION:
{message}

INSTRUCTIONS:
1. Answer using the supplied resume evidence where relevant.
2. Give practical, personalized career advice.
3. Do not invent skills, experience, projects, or qualifications.
4. If recommending projects, connect them to the user's existing skills
   and explain what the projects would demonstrate.
5. If asked about a specific career role, answer about that role even
   if the user has not selected it for formal analysis.
6. If resume evidence is insufficient, say so clearly.
7. Use readable headings and bullet points when useful.
8. Do not repeat the entire resume unnecessarily.
"""

            result = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )

            answer = (
                result.text.strip()
                if result.text
                else "I couldn't generate an answer. Please try again."
            )

        memory.add_assistant_message(answer)

        return {
            "status": "success",
            "session_id": request.session_id,
            "answer": answer,
            "target_role": agent.state.target_role,
        }

    except Exception as exc:
        # Remove the failed question so it isn't retained as an
        # unanswered message in the conversation history.
        history = memory.get_history()

        if history and history[-1].get("role") == "user":
            history.pop()

        print(f"Chat failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="CareerPilot could not answer your question. Check the backend terminal.",
        ) from exc
