<h1 align="center">🌟 StoryMood</h1>

<p align="center">
  <b>An AI-powered storytelling platform that generates personalized, mood-based stories with realistic voice narration.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS%20Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white" />
  <img src="https://img.shields.io/badge/ElevenLabs-000000?style=for-the-badge&logo=elevenlabs&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

---

## ✨ Overview

**StoryMood** crafts unique, emotionally resonant stories tailored to each user — from children to seniors. Pick a mood, choose your characters, select a language, and let AI generate a personalized story, then bring it to life with lifelike AI voice narration.

---

## 🎯 Features

- **🎭 Mood-Based Stories** — Generate stories based on different emotional tones (soothing, joyful, magical, intense, and more)
- **📚 Multiple Story Types** — Adventure, Fantasy, Moral, Comedy, Mystery, Sci-Fi, and more
- **👤 Custom Characters** — Add your own characters with names, ages, and personality traits
- **🎙️ AI Voice Narration** — Convert stories into spoken narration using realistic ElevenLabs voices
- **🌍 Multi-Language Support** — English, Hindi, Telugu, Tamil, and Malayalam
- **💾 Story Vault** — Save and retrieve your favorite generated stories
- **🎨 World-Class UI** — Gradients, glassmorphism, smooth animations, and a fully responsive design
- **♿ Accessibility** — WCAG 2.1 AA compliant with full keyboard navigation and screen reader support

---

## 🏗️ Architecture

```
StoryMood/
├── frontend/     # React + TypeScript web app (UI, story builder, playback)
└── storyarc/     # FastAPI backend (story generation, voice, vault, sessions)
```

### Frontend
React (TypeScript) single-page app with a polished, animated UI for composing and playing back stories.

### Backend (`storyarc`)
FastAPI service that orchestrates LLM story generation, voice synthesis, and persistence.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, CSS3 (glassmorphism, gradients) |
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **AI / LLM** | AWS Bedrock (Claude 3) |
| **Voice (TTS)** | ElevenLabs API |
| **Database** | Amazon DynamoDB |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.10+
- AWS account with Bedrock & DynamoDB access
- ElevenLabs API key

### 1️⃣ Backend Setup

```bash
cd storyarc
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

Create a `.env` file in `storyarc/` with your credentials:

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
STORIES_TABLE=StoryArc_Stories
USERS_TABLE=StoryArc_Users
TTS_VOICE_ID=your_default_voice_id
SECRET_KEY=your_secure_secret_key
APP_ENV=development
```

Run the backend:

```bash
python main.py
```

### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

Create a `.env` file in `frontend/`:

```env
REACT_APP_API_URL=http://localhost:8000
```

Then open **http://localhost:3000** 🎉

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/story/generate-story` | Generate a new story |
| `POST` | `/api/v1/voice/narrate` | Convert story text to speech |
| `POST` | `/api/v1/vault/save` | Save a story to the vault |
| `GET` | `/api/v1/vault/{user_id}` | Get all stories for a user |
| `GET` | `/api/v1/vault/story/{story_id}` | Get a specific story |
| `POST` | `/api/v1/session/create` | Create a user session |

📖 Interactive API docs available at `/docs` (Swagger) and `/redoc` once the backend is running.

---

## 🎨 Design Highlights

- **Gradient backgrounds** and **glassmorphism** frosted-glass effects
- **Mood-specific color schemes** that match the emotional tone of each story
- **Smooth micro-interactions**, loading states, and friendly error handling
- **Inter** typography for optimal readability

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

<p align="center">Built with ❤️ by <a href="https://www.linkedin.com/in/praneesha-martha/">Praneesha Martha</a></p>
