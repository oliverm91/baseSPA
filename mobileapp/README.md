# 📱 BaseSPA: Mobile Application

This directory contains the cross-platform Flutter frontend for BaseSPA. 
While the main project `README.md` covers the architecture and high-level setup, this document provides a deeper dive into running the mobile application locally, configuring device emulators, and optimizing your developer experience.

## 🚀 1. Requirements & Setup

Before running the app, ensure you have:
1. Installed the [Flutter SDK](https://docs.flutter.dev/get-started/install).
2. Sourced your dependencies by running `flutter pub get` in this directory.
3. Started your Django backend (`uv run manage.py runserver` from the root directory) so the app has an API to connect to.

---

## 💻 2. Running on Desktop (Fastest Development)

Flutter allows you to run your "mobile" app as a native desktop window. This is **highly recommended** for building UI because it requires zero emulator overhead and hot-reloads instantly.

To run as a desktop app, you must install the native desktop build tools for your specific OS:
*   **Windows:** Install [Visual Studio](https://visualstudio.microsoft.com/) with the **"Desktop development with C++"** workload checked. Run `flutter run -d windows`.
*   **macOS:** Install [Xcode](https://developer.apple.com/xcode/). Run `flutter run -d macos`.
*   **Linux:** Install `clang`, `cmake`, `ninja-build`, `pkg-config`, and `libgtk-3-dev`. Run `flutter run -d linux`.

---

## 📱 3. Running on Phone Emulators (Final Testing)

When you are ready to test touch interactions, keyboards, and mobile-specific layouts, you need a simulator.

### Android Emulator Setup
1. Download and install [Android Studio](https://developer.android.com/studio). Use the default "Standard" installation.
2. Open Android Studio. Click on the **SDK Manager** (the cube with a down-arrow icon in the top right).
3. Select the **SDK Tools** tab in the middle of the window.
4. Check the box for **Android SDK Command-line Tools (latest)** and click **Apply**.
5. Open your terminal and run `flutter doctor --android-licenses`. Press `y` to accept all Google SDK licenses.
6. Back in Android Studio, open the **Virtual Device Manager** (Device icon).
7. Click **Create Device**. Select a generic modern phone (like **Pixel 8** or **Medium Phone**). 
   * *Note: Generic sizes are entirely fine for testing. You only need specific models if you are testing hardware notches or require the Google Play Store pre-installed.*
8. Download the latest Recommended System Image (e.g., API 34+) and click **Finish**.
9. Click the Play (▶) button next to your new device to boot it up.
10. Once the phone is on your screen, run `flutter run` in your terminal. Flutter will automatically detect the emulator and install the app.

*(Note: The first time you compile for Android, it will take several minutes to download the Gradle build tools and NDK. Subsequent runs will be extremely fast).*

### iOS Simulator Setup (macOS Only)
1. Install [Xcode](https://developer.apple.com/xcode/).
2. Run `sudo xcodebuild -license` in your terminal to accept the Apple developer licenses.
3. Open the **Simulator** app (you can find it via Spotlight Search).
4. Once the iPhone simulator boots up on your screen, run `flutter run` in your terminal.

---

## ⚡ 4. Developer Experience: VS Code Extensions

If you are using Visual Studio Code, you can drastically improve your workflow by installing these highly recommended extensions:

1. **Flutter** (`dart-code.flutter`): The official extension. It provides:
   * **Hot Reload on Save**: Instantly see your UI changes without typing `r` in the terminal.
   * **Device Selector**: A button in the bottom-right corner of VS Code to instantly boot up your Android/iOS emulators without opening Android Studio.
   * **Widget Inspector**: A visual tree to debug layouts and spacing.
2. **Dart** (`dart-code.dart`): Installed automatically with Flutter. Provides autocomplete, formatting, and linting.
