FMS Unsigned Final Package
==========================

Templates copied into backend/templates: trading_invoice_system.xlsx, Service_invoice_system.xlsx, Nomuntu_January_payslip.xlsx

What is included:
- backend/: FastAPI app with auth, logo upload, exports that produce PDF by default (reportlab) and XLSX option
- frontend/: React PWA with logo upload UI and export buttons
- Dockerfile + docker-compose for easy deployment to Azure
- GitHub Actions (.github/workflows/build_apk.yml) that builds an unsigned APK and uploads it as an artifact; optional upload to Azure Blob if AZURE_STORAGE_CONNECTION_STRING secret is set.
- init_db.py and backend/create_admin.py scripts

Quick local run:
1. Initialize DB:
   python init_db.py
2. Create admin:
   python backend/create_admin.py --email admin@example.com --password StrongPass123 --name Admin
3. Start backend:
   cd backend
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
4. Start frontend:
   cd frontend
   npm install
   npm start

GitHub Actions (APK build):
- Push to main branch. The workflow builds frontend, runs Capacitor steps, attempts Android build (unsigned debug), and uploads APK as an artifact.
- To enable Azure upload, set AZURE_STORAGE_CONNECTION_STRING secret in repo settings.

APK and PWA:
- Android/Huawei: download the APK from GitHub Actions artifact or Azure Blob and install (allow installing from unknown sources).
- iPhone/iOS: install via PWA (Safari -> Share -> Add to Home Screen).

Notes:
- This package produces unsigned debug APKs for testing. For production, generate a keystore and add signing steps to the workflow.
- PDFs are generated via reportlab and should be readable by any PDF reader on any device.

