# web-crawler
A simple web crawler that retrieves links from any specified url

## Project Structure
- `backend/`: Python FastAPI server with async web crawler
- `frontend/`: Svelte-based web interface

## Prerequisites
- Python 3.7+
- Node.js and npm
- Git

## Setup and Installation

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will run on http://localhost:8000

### Frontend Setup
1. In a new terminal, navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:8080

## Usage
1. Open your browser and navigate to http://localhost:8080
2. Enter a URL in the input field
3. The crawler will start processing the URL and display results in real-time through WebSocket connection

## Features
- Asynchronous web crawling
- Real-time progress updates via WebSocket
- Configurable crawl depth and rate limiting
- Cross-origin resource sharing (CORS) enabled
- Single-page application (SPA) frontend

## Development
- Backend uses FastAPI with async support
- Frontend is built with Svelte
- WebSocket connection for real-time updates
- TypeScript support available (see frontend setup instructions)

## Notes
- The crawler is rate-limited to avoid overwhelming target servers
- Maximum crawl depth is set to 2 by default
- CORS is configured for localhost development