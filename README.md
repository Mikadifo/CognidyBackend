# Project Overview

![Project Banner](https://github.com/user-attachments/assets/9754d095-acc8-491f-a201-cc9e0286c043)

This project provides a backend service built with **Flask** and **MongoDB**, documented via **Swagger**.  
It follows a **branch-based workflow** to keep development organized and easy to test before merging.

---

## 🛠 Tech Stack

- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)
- **Database:** [MongoDB](https://www.mongodb.com/)
- **API Documentation:** [Swagger](https://swagger.io/)
- **AI API**: [Gemini API](https://aistudio.google.com/welcome)

---

## 🌱 Development Workflow

- Every task must be developed in a **new branch** based off the `dev` branch, based on naming conventions:

  - Features → `feature/<name>`  
    Example: `feature/user-authentication`

  - Bug fixes → `fix/<name>`  
    Example: `fix/input-validation`

  - Custom tasks can adapt the format if needed.

- Once a task is **completed**, create a **Pull Request (PR)**.

  - The rest of the team will **test it before merging** into `dev`.

- Once all tasks of the week are completed, we will merge into `master`.

> Do not push directly to `master` or `dev`

---

## ▶️ How to Run the Project

1. **Activate your virtual environment** (if not already active):

   ```bash
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies**: 

    ```bash
    pip install -r requirements.txt
    ```

3. **Add env variables:** (Ask a teammate for this)

    ```
    DB_USERNAME=<username>
    DB_PASSWORD=<password>
    DB_NAME=cognidy
    JWT_SECRET_KEY=<jwt_secret_key>
    GENAI_API_KEY=<genai_api_key>
    ```

4. **Start the Flask server**:

   ```bash
   flask run
   ```

5. **Access the API locally**:

   ```
   http://localhost:5000/
   ```

6. **Check API documentation (Swagger)**:
   ```
   http://localhost:5000/swagger
   ```

---

### 🧪 Running in Development Mode

If you want auto-reload on code changes, set the following environment variable:

```bash
# Linux/Mac
export FLASK_ENV=development

# Windows (PowerShell)
$env:FLASK_ENV="development"
```

Then run:

```bash
flask run
```

---

### 📦 Database

Make sure you have **MongoDB running remotely**. If not, then ask the team to turn the cluster on again.

Your `.env` file must have the correct `DB_USERNAME`, `DB_PASSWORD`, and `DB_NAME` set before running.

---

## 🚀 Available Features

- User authentication & validation (JWT)
- MongoDB integration with environment configs
- API endpoints documented via Swagger
- Error handling & structured responses
- Secure password hashing

_(This section will be updated as new features are added.)_

---

## ⚙️ Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mikadifo/CognidyBackend.git
cd CognidyBackend
```

### 2. Create and activate a virtual environment

```bash
# Create venv
python -m venv venv

# Activate venv
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you need to add a dependency that is not in the list, use the following command after installing it, so the rest of the team can install it too.

```bash
pip freeze > requirements.txt
```

> Remind the rest of the team to install the requirements.txt dependencies again after updating it.

### 4. Environment Variables

You need a `.env` file at the root of the project with the following values:

```ini
DB_USERNAME=<db_username>
DB_PASSWORD=<db_password>
DB_NAME=<db_name>
T_COL=<t_col>
```

⚠️ Ask a team member for the actual values or retrieve them from GitHub Secrets.

---

## 📖 API Documentation

Swagger will be available once you start the Flask server:

```
http://localhost:5000/swagger
```

---

## ✅ Contribution Guidelines

1. Always create a **new branch** for each task.
2. Follow the branch naming convention (`feature/*`, `fix/*`).
3. Push your changes and create a **Pull Request**.
4. Wait for teammates to test your PR before merging.
5. Keep commits **clear and descriptive**.

---

## ℹ️ Additional Notes

- Keep your virtual environment **out of version control** (ensure `.gitignore` includes `venv/`).
- Use **descriptive commit messages** to make history clear.
- Check the **Swagger docs** after each new endpoint to confirm correctness.
- If you add a new dependency, don’t forget to run:
  ```bash
  pip freeze > requirements.txt
  ```

---

👥 _Happy coding, and remember to keep branches clean and PRs small for easier review!_
