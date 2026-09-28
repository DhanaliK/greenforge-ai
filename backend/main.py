"""
GreenForge AI backend — entry point
Run with: uvicorn main:app --reload
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
