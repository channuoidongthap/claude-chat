# Claude Web Chat

A modern web application for interacting with Claude AI, built with Flask and featuring dark mode UI, chat history, and SSH integration.

## Features

- 🤖 **Claude AI Integration** - Full access to Claude API (Sonnet, Opus, Haiku models)
- 🎨 **Dark Mode UI** - Modern, responsive dark interface
- 💬 **Chat History** - Auto-save and load previous conversations
- 🔌 **SSH Integration** - Execute remote commands via SSH
- 📱 **Mobile Responsive** - Works on phones, tablets, and desktops
- ⚡ **Python 3.6+ Compatible** - Works with older Python versions
- 🚀 **Railway Ready** - One-click deployment to Railway.app

## Quick Start (Local)

### Prerequisites
- Python 3.6+
- pip (Python package manager)
- API Key from [Anthropic Console](https://console.anthropic.com)

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/sunreaches-ai/claude-chat.git
   cd claude-chat
   ```

2. **Setup Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

   Access at: http://localhost:5000

## Deployment on Railway

### 1. Prepare Code
- Push code to GitHub: https://github.com/sunreaches-ai/claude-chat

### 2. Connect to Railway
1. Go to https://railway.app
2. Click "Start New Project"
3. Select "Deploy from GitHub"
4. Choose repository "claude-chat"
5. Railway auto-deploys

### 3. Add Environment Variables
In Railway Dashboard → Variables:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
SSH_HOST=your-host
SSH_PORT=22
SSH_USER=your-user
SSH_PASSWORD=your-password
```

### 4. Configure Custom Domain
1. Railway Dashboard → Settings
2. Add Custom Domain: `ai.sunreaches.com`
3. Update DNS records in domain registrar
4. Wait for DNS propagation (5-10 minutes)

## API Endpoints

### Chat
- **POST** `/api/chat`
  ```json
  {
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "claude-sonnet-4-20250514"
  }
  ```

### SSH
- **GET** `/api/ssh/test` - Test SSH connection
- **POST** `/api/ssh/execute` - Execute command
  ```json
  {
    "command": "whoami"
  }
  ```

### History
- **GET** `/api/history/list` - List all sessions
- **GET** `/api/history/load/<session_id>` - Load session
- **POST** `/api/history/save` - Save history
  ```json
  {
    "session_id": "default",
    "messages": [...]
  }
  ```

### Health
- **GET** `/api/health` - Health check

## File Structure

```
claude-chat/
├── app.py              # Flask backend
├── index.html          # Web UI
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
├── .env.example       # Example config
├── Procfile           # Railway deployment config
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Configuration

Edit `.env`:

```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional: SSH Configuration
SSH_HOST=your-server.com
SSH_PORT=22
SSH_USER=username
SSH_PASSWORD=password
SSH_KEY_PATH=/path/to/key.pem

# App Config
FLASK_ENV=production
DEBUG=False
```

## Troubleshooting

### "API Key not configured"
- Check `.env` file has `ANTHROPIC_API_KEY`
- Verify key format: `sk-ant-...`

### SSH Connection Failed
- Check SSH credentials in `.env`
- Verify host is reachable: `ping your-server.com`
- Ensure port is correct (default: 22)

### Port Already in Use
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Models Available

- **claude-opus-4-20250805** - Most powerful (slower)
- **claude-sonnet-4-20250514** - Balanced (recommended)
- **claude-haiku-4-20250507** - Fastest (less capable)

## Development

### Run in Development Mode
```bash
python app.py  # Debug mode on
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

MIT License - See LICENSE file

## Support

- Issues: [GitHub Issues](https://github.com/sunreaches-ai/claude-chat/issues)
- Docs: [Anthropic API Docs](https://docs.anthropic.com)

## Version

- **Current:** 1.0.0
- **Last Updated:** 2026-04-04

---

**Made with ❤️ by Sun Reaches**
