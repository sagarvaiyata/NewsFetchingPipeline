# 📰 Business Wire News Scraper API

A FastAPI-based service that scrapes press releases from [Business Wire](https://www.businesswire.com), extracts company tickers, publication dates, and article content, and stores them in MongoDB.

You can trigger this scraper by making a POST request with a list of stock ticker symbols — the API will fetch only matching news items.

---

## 🚀 Features

- Scrapes the Business Wire newsroom index page
- Extracts:
  - Article heading
  - URL
  - Ticker (e.g. `TDCB`)
  - Publication date
  - Main article content
- Filters news by specific tickers passed in the request
- Deduplicates using MongoDB before inserting
- Runs via `uvicorn` and integrates easily with Airflow or cron

---

## 📦 Project Structure

\`\`\`
news_scraper/
├── app/
│   ├── main.py              # FastAPI app setup
│   ├── config.py            # Environment configs (API keys, Mongo URI)
│   ├── models.py            # Request schema
│   ├── services/            # Logic for scraping & API calls
│   │   ├── firecrawl.py
│   │   ├── openai_client.py
│   │   └── mongo.py
│   └── routes/
│       └── scrape.py        # /run-scrape endpoint
├── run.py                   # Uvicorn launcher
├── requirements.txt         # Dependencies
└── .gitignore
\`\`\`

---

## 🛠️ Setup

### 1. Clone the repo

\`\`\`bash
git clone https://github.com/your-username/business-wire-scraper.git
cd business-wire-scraper
\`\`\`

### 2. Install dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Set environment variables

Create a \`.env\` file or set environment variables manually:

\`\`\`bash
export FIRECRAWL_API_KEY=your-firecrawl-key
export OPENAI_API_KEY=your-openai-key
export MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/
\`\`\`

---

## ▶️ Running the API

Simply run:

\`\`\`bash
python run.py
\`\`\`

This launches the FastAPI server via \`uvicorn\` on \`http://localhost:8000\`.

---

## 🔁 API Usage

### Endpoint

\`\`\`
POST /run-scrape
\`\`\`

### Request Body

\`\`\`json
{
  "ticker_codes": ["TDCB", "AAPL", "GOOG"]
}
\`\`\`

### Response

\`\`\`json
{
  "message": "Scrape complete",
  "new_documents_count": 2,
  "new_documents": [
    {
      "heading": "TDCB Reports Q2 Earnings",
      "url": "https://www.businesswire.com/news/home/20250717259715/en/",
      "ticker": "TDCB",
      "date": "Jul 15, 2025 5:00 PM Eastern Daylight Time",
      "content": "Full article text here..."
    }
  ]
}
\`\`\`

---

## 🧪 Testing

You can use [Postman](https://www.postman.com/) or \`curl\`:

\`\`\`bash
curl -X POST http://localhost:8000/run-scrape \
  -H "Content-Type: application/json" \
  -d '{"ticker_codes": ["TDCB"]}'
\`\`\`

---

## 📅 Scheduling with Airflow or Cron

This API is compatible with Astro or Apache Airflow. You can set up a DAG or cron job that calls \`POST /run-scrape\` every 10 minutes with your ticker list.

---

## 🧹 Ignored Files

Your \`.gitignore\` already excludes:

\`\`\`gitignore
__pycache__/
*.py[cod]
.venv/
.env
\`\`\`

---

## 📃 License

MIT License – use freely with attribution. Contributions welcome!

---

## 👨‍💻 Author

**Sagar Vaiyata**

Connect on [GitHub](https://github.com/sagarvaiyata) or [LinkedIn](https://linkedin.com/in/sagarvaiyata)
