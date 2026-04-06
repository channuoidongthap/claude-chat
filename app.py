#!/usr/bin/env python3
"""
Claude Web Chat - Backend Server (Python 3.6 Compatible)
Uses HTTP requests instead of Anthropic SDK
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import paramiko
import requests
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIG
# ============================================================================

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

API_KEY = os.getenv("ANTHROPIC_API_KEY")
SSH_HOST = os.getenv("SSH_HOST", "")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", "")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "")

HISTORY_DIR = Path("./chat_history")
HISTORY_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# ============================================================================
# CLAUDE CHAT HANDLER
# ============================================================================

class ClaudeChat:
    def __init__(self):
        self.ssh_client = None
    
    def get_system_prompt(self):
        return """Bạn là Claude - một AI assistant toàn năng.

KHẢ NĂNG:
- Lập trình (Python, JavaScript, Bash, SQL, etc.)
- Phân tích dữ liệu & tạo strategy
- Viết & chỉnh sửa tài liệu
- Thực thi lệnh qua SSH (nếu user yêu cầu)
- Dịch thuật & viết sáng tạo

KHI USER YÊU CẦU:
1. Lệnh code → cung cấp đầy đủ, executable
2. SSH execution → gợi ý lệnh, sau đó hỏi user có muốn thực thi không
3. Phân tích → cung cấp insights chi tiết + recommendations

STYLE:
- Trả lời tiếng Việt nếu user dùng tiếng Việt
- Chia output thành sections rõ ràng
- Cung cấp context & giải thích"""
    
    def chat(self, messages, model="claude-sonnet-4-20250514"):
        """Call Claude API via HTTP requests (Python 3.6 compatible)"""
        try:
            if not API_KEY:
                return "❌ Error: ANTHROPIC_API_KEY not configured"
            
            headers = {
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": model,
                "max_tokens": 4096,
                "system": self.get_system_prompt(),
                "messages": messages
            }
            
            response = requests.post(
                ANTHROPIC_API_URL,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = response.text[:200]
                return "❌ API Error: {}".format(error_msg)
            
            data = response.json()
            return data['content'][0]['text']
        
        except Exception as e:
            return "❌ Error: {}".format(str(e))
    
    def ssh_execute(self, command):
        """Execute command on remote server"""
        try:
            if not SSH_HOST or not SSH_USER:
                return "❌ SSH not configured"
            
            if not self.ssh_client:
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                if SSH_KEY_PATH and os.path.exists(SSH_KEY_PATH):
                    self.ssh_client.connect(
                        SSH_HOST, 
                        port=SSH_PORT,
                        username=SSH_USER, 
                        key_filename=SSH_KEY_PATH, 
                        timeout=10
                    )
                else:
                    self.ssh_client.connect(
                        SSH_HOST, 
                        port=SSH_PORT,
                        username=SSH_USER, 
                        password=SSH_PASSWORD, 
                        timeout=10
                    )
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            return output if output else error
        
        except Exception as e:
            return "❌ SSH Error: {}".format(str(e))
    
    def test_ssh(self):
        """Test SSH connection"""
        result = self.ssh_execute("whoami")
        if "❌" in result:
            return {"success": False, "message": "SSH failed: {}".format(result)}
        else:
            return {"success": True, "message": "SSH OK - User: {}".format(result.strip())}

claude_chat = ClaudeChat()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "api_configured": bool(API_KEY),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Chat endpoint - main API"""
    try:
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'claude-sonnet-4-20250514')
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        response = claude_chat.chat(messages, model)
        
        return jsonify({
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ssh/test', methods=['GET'])
def ssh_test():
    """Test SSH connection"""
    result = claude_chat.test_ssh()
    return jsonify(result)

@app.route('/api/ssh/execute', methods=['POST'])
def ssh_execute():
    """Execute SSH command"""
    try:
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({"error": "No command provided"}), 400
        
        result = claude_chat.ssh_execute(command)
        
        return jsonify({
            "success": True,
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/save', methods=['POST'])
def save_history():
    """Save chat history"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        messages = data.get('messages', [])
        
        history_file = HISTORY_DIR / "{}.json".format(session_id)
        
        with open(str(history_file), 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": session_id,
                "messages": messages,
                "saved_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "message": "History saved: {}".format(session_id)
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/load/<session_id>', methods=['GET'])
def load_history(session_id):
    """Load chat history"""
    try:
        history_file = HISTORY_DIR / "{}.json".format(session_id)
        
        if not history_file.exists():
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        with open(str(history_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            "success": True,
            "data": data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/list', methods=['GET'])
def list_histories():
    """List all chat histories"""
    try:
        histories = []
        for file in HISTORY_DIR.glob("*.json"):
            with open(str(file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                histories.append({
                    "session_id": data.get("session_id"),
                    "saved_at": data.get("saved_at"),
                    "message_count": len(data.get("messages", []))
                })
        
        return jsonify({
            "success": True,
            "histories": sorted(histories, key=lambda x: x['saved_at'], reverse=True)
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Claude Web Chat Server")
    print("="*70)
    print("📡 Server running at: http://localhost:5000")
    print("🌐 Web UI at: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
