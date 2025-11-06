# Insider Threat Anomaly Detection (Logs)

A Flask web app that ingests access/log data, scores it with an **Isolation Forest** baseline, and visualizes anomalies in a dashboard.

---

## ✨ Highlights
- Web UI with upload + results views (Flask + Jinja2 templates)
- Baseline unsupervised model (Isolation Forest) for fast anomaly scoring
- Simple project layout: `app.py`, `models/`, `templates/`, `static/`, `data/`
- MIT licensed

---

## 🧱 Project Structure
```
.
├─ app.py                 # Flask entrypoint / routes
├─ models/                # detection & preprocessing modules
├─ templates/             # HTML templates
├─ static/                # CSS/JS assets
├─ data/                  # sample data / local artifacts (avoid committing PII)
├─ requirements.txt
├─ README.md
├─ ROADMAP.md
└─ LICENSE

````

---

## 🚀 Quickstart (macOS / Apple Silicon)

```bash
# 1) Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
python app.py

# 4) Open in browser
# http://localhost:5000

````

> 💡 Tip: Use a clean virtual environment and keep raw logs out of version control.

---

## 🧩 Typical Workflow

1. Upload access/log file in the UI.
2. App parses and preprocesses the data (see `models/` folder).
3. Isolation Forest scores events or entities.
4. Dashboard renders anomalies and supporting context.

---

## 🧪 Example Input Format

Example CSV layout:

```
timestamp,user,host,action,resource,bytes,success
2025-03-11T09:15:43Z,alice,laptop-01,LOGIN,Okta,0,true
```

You can modify the parser to match your specific log schema.

---

## ⚙️ Configuration

* Model and thresholds currently defined in code under `models/`.
* For larger datasets, you can batch processing or externalize config to YAML later.

---

## 🛡️ Security Notes

* Avoid uploading or committing real logs — use sanitized samples in `data/`.
* Hash usernames/IPs for demos when possible.
* Validate file types before processing user uploads.

---

## 📚 Additional Documentation

* [docs/USAGE.md](docs/USAGE.md): Detailed usage and troubleshooting guide
* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): System design and component overview
* [ROADMAP.md](ROADMAP.md): Planned improvements and milestones

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome!
Please open an issue first to discuss major changes.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

````
