# Human Rights Monitor - FastAPI Backend

This project is a RESTful backend service built using **FastAPI** for the **Human Rights Monitor** platform. It provides a structured, powerful, and scalable API to access and manage all related resources in an isolated and organized manner.

## 🔍 Project Description

The backend exposes a set of RESTful endpoints to interact with different resources related to human rights monitoring, such as:
- Incidents Reports
- Victims
- Cases
- Users

Each endpoint is designed to provide clean access to the corresponding data, supporting full CRUD operations, filtering, and validation where needed.

## 👥 User Roles

The system supports multiple user roles, each with different permissions and responsibilities:

- **User** – Regular user who can submit and track incidents.  
- **Lawyer** – Can provide legal follow-up and handle assigned cases.  
- **Organization** – Human rights organization with access to broader cases.  
- **Admin** – Full access to manage users, incidents, cases, and platform settings.

## 🧑‍💻 Tech Stack

- **FastAPI** for building high-performance APIs
- **MongoDB** as the primary NoSQL database
- **Pydantic** for data validation
- **Uvicorn** as the ASGI server

## ⚙️ Setup and Running the Project

 Frontend repository: [https://github.com/Amer-Daghlis/Front-we](https://github.com/Amer-Daghlis/Front-we)

To run the project locally, follow these steps:

1. **Clone the repository:**
```bash
git clone https://github.com/Mohammad-Zaben/Human_Rights_Monitor.git
cd Human_Rights_Monitor
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
uvicorn app.main:app --reload
```

The server will start at:  
**http://127.0.0.1:8000**

5. **Access the API documentation interfaces:**
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📁 Project Structure

```
project/
├── app/
│   ├── main.py
|   ├── auth/
│   ├── models/
│   ├── routes/
│   ├── services/
|   ├── config.py
│   └── database.py
├── requirements.txt
└── README.md
```

## 🛡️ Notes

- The backend is modular and easily extendable.

## 📞 Contact

For inquiries, suggestions, or contributions, feel free to contact me
