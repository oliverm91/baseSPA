# BaseSPA

BaseSPA is a secure, scalable **Django-based foundation** for building modern applications with integrated **web and mobile frontends**. It provides a robust authentication system and a standardized architecture to accelerate development while ensuring best practices in security and cross-platform compatibility.

## Step 0: Prerequisites

### 1. Python & Package Management
- **All Platforms**: [uv](https://github.com/astral-sh/uv) (Extremely fast Python package manager)

### 2. Docker (Infrastructure)
You need Docker to run the database and email testing services locally.

#### **Windows**
- Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
- Ensure **WSL 2** is enabled in the Docker Desktop settings (General > Use the WSL 2 based engine).

#### **Mac**
- Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) or [OrbStack](https://orbstack.dev/) for better performance.

#### **Linux**
- Install **Docker Engine** and the **Docker Compose plugin** using your distribution's package manager (e.g., `sudo apt install docker-ce docker-compose-plugin`).
- Ensure your user is added to the `docker` group: `sudo usermod -aG docker $USER`.

---

## Step 1: Environment Configuration
Clone or download the project and create your local environment file. We use `.env.example` as a template that you copy to `.env` (which is ignored by git) so you can safely add your private keys.

**macOS / Linux / PowerShell:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```
Open `.env` and configure the following:
- **`SECRET_KEY`**: Set a unique cryptographic string.
- **`DEBUG`**: Set to `True` for development.
- **Database**: The defaults match the `docker-compose` settings.
- **Email**: Defaults set to work with the included testing services.

## Step 2: Google OAuth Setup
To enable Google Login:
1. **Google Cloud Console**:
   - Create a project at [Google Cloud Console](https://console.cloud.google.com/).
   - Configure **OAuth Consent Screen** and create **OAuth 2.0 Client IDs** (Web application).
   - Add Redirect URI: `http://localhost:8000/accounts/google/login/callback/`.
2. **Update `.env`**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
3. **Django Admin**:
   - Go to `http://localhost:8000/admin/` > **Social Accounts > Social Applications**.
   - Add a new application: Provider: `Google`, Name: `Google Auth`.
   - Select your site (e.g., `example.com`) and move it to "Chosen sites".

## Step 3: Run the Infrastructure
Start the database and background services:
```bash
docker-compose up -d
```

## Step 4: Install & Migrate
```bash
uv sync
uv run manage.py migrate
```

## Step 5: Start Development
```bash
uv run manage.py runserver
```

---

## Technical Stack
- **Backend**: Django 6 (Python 3.14+)
- **Database**: PostgreSQL
- **Auth**: django-allauth + dj-rest-auth
- **Frontend**: Tailwind CSS + Django Templates
