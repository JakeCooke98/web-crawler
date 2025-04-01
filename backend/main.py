from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler import AsyncWebCrawler
import json

app = FastAPI()

# Define request body model
class CrawlRequest(BaseModel):
    url: str

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Receive the initial URL to crawl
        data = await websocket.receive_json()
        url = data.get("url")
        
        if not url:
            await websocket.close()
            return

        # Initialize crawler with a callback for sending updates
        async def send_update(page_url, links):
            await websocket.send_json({
                "page": page_url,
                "links": links
            })

        crawler = AsyncWebCrawler(
            start_url=url,
            max_depth=2,
            rate_limit=1.0,
            update_callback=send_update
        )
        
        await crawler.crawl()
        await websocket.send_json({"status": "completed"})
        
    except Exception as e:
        await websocket.send_json({
            "error": str(e)
        })
    finally:
        await websocket.close()
