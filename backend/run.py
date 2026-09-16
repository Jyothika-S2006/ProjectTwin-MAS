"""
ProjectTwin: Intelligent Data Capture & Schedule-Linking Layer
Oil India Limited / SIH26122 - Team SentinelX3.0
"""
import os
import sys
import webbrowser
import uvicorn

def main():
    print("=" * 70)
    print("ProjectTwin: Real-Time Actual Progress Tracking & Schedule Linking")
    print("Smart India Hackathon 2026 - Problem Statement ID: SIH26122")
    print("Organization: Oil India Limited | Team: SentinelX3.0")
    print("=" * 70)
    print("\nStarting local FastAPI server at http://127.0.0.1:8000 ...")
    print("Opening web browser dashboard...")
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
