# Sequential WhatsApp Message Sender 📲

A web-based Python application to **send WhatsApp messages sequentially** using the [TextMeBot API](https://textmebot.com/). This tool allows you to upload a CSV file with WhatsApp numbers, compose a custom message (with optional image), and send messages one by one — all through an intuitive interface with real-time logs and abort capability.

Ideal for small business owners, marketing teams, or support agents who need a lightweight tool to send personalized messages to multiple users while managing rate limits and monitoring delivery success.

---

## 🌟 Features

- ✅ Upload a CSV file of WhatsApp contacts
- 💬 Compose and send a custom message (with optional image link)
- 🕒 Adjustable delay between messages to avoid spam detection
- 📜 Real-time server logs using Server-Sent Events (SSE)
- 🛑 Abort message-sending mid-process
- 📁 Simple, no-database local app powered by Flask + Pandas

---

## 🧠 Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.6+
- Git (optional but recommended)
- A valid **TextMeBot** API key (https://textmebot.com/)
- Basic command-line familiarity

---

## ⚙️ Tech Stack & Libraries

| Technology | Purpose                  |
|------------|---------------------------|
| Flask      | Web server and routing    |
| Pandas     | CSV file parsing          |
| Requests   | API calls to TextMeBot    |
| HTML/CSS   | Frontend UI (in `templates/`) |
| JavaScript | Form submission, SSE log updates |

### 🔍 Python Packages Used

```bash
Flask
pandas
requests

```

## 🛠️ Installation & Setup

### Clone the repository
```bash
git clone https://github.com/yourusername/sequential-whatsapp-message-sender.git
cd sequential-whatsapp-message-sender
```
💡 Replace yourusername with your GitHub username or fork link.

### (Optional) Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies. Create and activate one using the following commands:

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
### Install Dependencies
Ensure you are in the project directory and install the required libraries:
```bash
pip install -r requirements.txt
```

### Run the Application
Start the Flask application by running:
```bash
python app.py
```
The app will start in debug mode. Open your browser and go to:
(http://127.0.0.1:5000)

## 🚀 How to Use





