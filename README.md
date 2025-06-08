# Human Rights Monitor - FastAPI Backend

This project is a RESTful backend service built using **FastAPI** for the **Human Rights Monitor** platform. It provides a structured, powerful, and scalable API to access and manage all related resources in an isolated and organized manner.

## 🔍 Project Description

The backend exposes a set of RESTful endpoints to interact with different resources related to human rights monitoring, such as:
- Incidents Reports
- Victims
- Cases
- Users

Each endpoint is designed to provide clean access to the corresponding data, supporting full CRUD operations, filtering, and validation where needed.

## ⚙️ Setup and Running the Project

To run the project locally, follow these steps:

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. **Create and activate a virtual environment:**

On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install the project dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the FastAPI app using Uvicorn:**
```bash
uvicorn main:app --reload
```

> ⚠️ Replace `main:app` with the actual import path to your FastAPI `app` instance if it's different.

The server will start at:  
**http://127.0.0.1:8000**

5. **Access the API documentation interfaces:**
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📁 Example Project Structure

```
project/
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── database.py
├── requirements.txt
└── README.md
```

## 🛡️ Notes

- Ensure any required environment variables (like database URLs, secrets) are configured properly.
- The backend is modular and easily extendable.

## 📞 Contact

For inquiries, suggestions, or contributions, feel free to contact the maintainer.
