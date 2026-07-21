# How to Run the ShopEase AI Assistant

Follow these exact steps to start the servers yourself.

## Step 1: Open two terminals (Command Prompt or PowerShell)
You need two separate terminal windows open in your code editor (like VS Code) or on your computer. 
Make sure both terminals are inside the project folder: `C:\Projects\Customer_Support_Ecommerce_ai_assistant` (or your current OneDrive folder if you are still using that one).

## Step 2: Start the Backend Server (Terminal 1)
In the first terminal window, run this command:
```bash
.\venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*Wait a few seconds until you see `Uvicorn running on http://0.0.0.0:8000`*

## Step 3: Start the Frontend Application (Terminal 2)
In the second terminal window, run this command:
```bash
.\venv\Scripts\python -m streamlit run frontend/app.py --server.port 8501
```

## Step 4: Open your Browser
Once both are running, simply open your web browser and go to:
👉 **http://localhost:8501**

## To Stop the Servers
When you are done testing, go to each terminal window and press **`Ctrl + C`** on your keyboard to stop the servers.
