"""
Single entry point to start both FastAPI backend and Streamlit frontend.
Usage: python run.py
"""
import subprocess
import sys
import os
import time
import signal
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def start_backend():
    """Start FastAPI backend server."""
    logger.info("Starting FastAPI backend on http://localhost:8000 ...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT_DIR,
        env={**os.environ},
    )


def start_frontend():
    """Start Streamlit frontend server."""
    logger.info("Starting Streamlit frontend on http://localhost:8501 ...")
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"],
        cwd=ROOT_DIR,
        env={**os.environ},
    )


def main():
    print("=" * 60)
    print("  ShopEase AI Customer Support Assistant")
    print("  Starting Backend (FastAPI) + Frontend (Streamlit)")
    print("=" * 60)

    processes = []

    try:
        # Start backend first
        backend = start_backend()
        processes.append(backend)

        # Wait a moment for backend to initialize
        time.sleep(3)

        # Start frontend
        frontend = start_frontend()
        processes.append(frontend)

        print("\n" + "=" * 60)
        print("  ✅ Both servers are running!")
        print("  📡 Backend API:  http://localhost:8000")
        print("  📡 API Docs:     http://localhost:8000/docs")
        print("  🌐 Frontend UI:  http://localhost:8501")
        print("  Press Ctrl+C to stop both servers")
        print("=" * 60 + "\n")

        # Wait for processes
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        for p in processes:
            try:
                p.terminate()
                p.wait(timeout=5)
            except Exception:
                p.kill()
        print("✅ All servers stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
