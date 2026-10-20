# PrediCare

PrediCare is a Windows-friendly IoT health-monitoring demonstration. It
provides a React dashboard, FastAPI/SQLite persistence, an explicit simulation
mode, a documented ESP32 JSON protocol, and an isolated AI model interface.
It is decision support only and does not diagnose disease or predict medical
emergencies.

## Run locally

### Backend

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; SQLite is created as
`backend/predicare.db`. Use `POST /api/measurements/simulate` for a reading.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Set
`VITE_API_URL` if the backend uses another host.

### Validation

```powershell
cd backend
python -m pytest
cd ..\frontend
npm run build
```

See [docs/serial_protocol.md](docs/serial_protocol.md) and
[firmware/README.md](firmware/README.md) for hardware integration.
