# 🚀 BaseSPA: Your Project Foundation

Stop reinventing the wheel! **BaseSPA** is the perfect launchpad designed specifically to be the **base for all your future projects**. Dive straight into building unique business features instead of spending days configuring authentication, databases, and APIs.

Whether you're building a web platform or a cross-platform mobile app, BaseSPA provides a production-ready, highly opinionated, and modern architecture out of the box.

---

## ✨ What's Already Implemented?


### 💻 Frontends
- **Web App**: Server-rendered HTML via Django templates styled beautifully.
- **Mobile App**: A pre-configured Flutter project with API client, token refresh logic, and core screens ready to go.

### 🏗️ Architecture & Core
- **Backend-for-Frontend (BFF)**: A dedicated Service Layer processes all business logic—views just serve the frontends!
- **Database**: Robust PostgreSQL integration.

### 🔐 Complete Authentication System
- **Email & Password**: Registration, login, password resets, and change password flows. Email acts as the primary identifier.
- **Google OAuth**: Seamless Gmail login integration. (Link existing accounts automatically).
- **Dual Session Management**: Stateful session auth for Web (HTML/Templates) and JWT tokens for Mobile (via DRF & dj-rest-allauth).


---

## 🛠️ How to Setup Everything

### 1. Prerequisites (Mac, Windows, Linux)
* **Python**: Install [uv](https://astral.sh/uv) (Extremely fast Python package manager).
* **Docker**: 
  * *Mac*: Install [OrbStack](https://orbstack.dev/) (recommended) or Docker Desktop.
  * *Windows*: Install [Docker Desktop](https://www.docker.com/products/docker-desktop) and ensure WSL 2 is enabled.
  * *Linux*: Install **Docker Engine** and the **Docker Compose plugin** using your distribution's package manager. Ensure your user is added to the `docker` group (`sudo usermod -aG docker $USER`).
* **Mobile**: Install the [Flutter SDK](https://docs.flutter.dev/get-started/install).

### 2. Clone the Repository
Clone or download the project to your local machine:
```bash
git clone https://github.com/oliverm91/baseSPA.git
cd baseSPA
```

### 3. Initialize UV
uv will create a .venv folder and install all dependencies.
```bash
uv sync
```

### 4. Environment Configuration
Set up your `.env` file from the template:
```bash
# Mac/Linux/Windows PowerShell
cp .env.example .env
```
*(Windows CMD: `copy .env.example .env`)*

Configure your `.env` with a `SECRET_KEY`, database credentials (defaults match docker), and your `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` if using OAuth.

### 5. Start the Infrastructure (Database and Email server for development)
Spin up your PostgreSQL database and email server for development (UI client on 127.0.0.1:1080) using Docker:
```bash
docker-compose up -d
```

### 6. Setup the Backend
Apply migrations and start the Django development server:
```bash
uv run manage.py migrate
uv run manage.py runserver
```

### 7. Setup the Mobile App
In a new terminal window, navigate to the mobile app directory and install the packages:
```bash
cd mobileapp
flutter pub get
```

To run the app, use the specific command for your target platform (Note: **Web is not supported**):

*   **Windows:** `flutter run -d windows` (Requires [Visual Studio](https://visualstudio.microsoft.com/) with C++ workload)
*   **Android:** `flutter run` or select your emulator (Requires [Android Studio](https://developer.android.com/studio))
*   **iOS:** `flutter run` or select your simulator (Requires [Xcode](https://developer.apple.com/xcode/), macOS only)
*   **macOS:** `flutter run -d macos` (Requires [Xcode](https://developer.apple.com/xcode/), macOS only)
*   **Linux:** `flutter run -d linux` (Requires GTK and build essentials)

---

## 🎨 Branding (Where to rename BaseSPA)
If you are turning this into your own project, here are the main places you need to update the "BaseSPA" name:

### Backend (Django)
* **`core/settings.py`**: Look for the `APP_NAME` variable.
* **`core/context_processors.py`**: The `global_settings` processor provides the default name.
* **`templates/snippets/navbar.html`**: The web navigation bar has the logo split into two colors: `<span class="text-white">Base</span><span class="text-[#EF3E5C]">SPA</span>`.

### Frontend (Mobile - Flutter)
* **`mobileapp/lib/widgets/app_navbar.dart`**: The `Text` widget inside the `AppBar`'s title holds the app name.
* **`mobileapp/lib/core/constants.dart`**: The `AppConstants.appName` variable.
