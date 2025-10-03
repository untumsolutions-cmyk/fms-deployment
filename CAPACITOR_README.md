CAPACITOR / APK manual steps (backup):
1. cd frontend
2. npm install
3. npm run build
4. npm install -g @capacitor/cli
5. npx cap init fms com.example.fms --web-dir build
6. npx cap add android
7. npx cap open android
8. Build APK in Android Studio or run ./gradlew assembleDebug in frontend/android
