# Quick Test Commands

## ✅ Correct Commands

```bash
# Test the server (with port 8000)
curl http://127.0.0.1:8000

# Or use localhost
curl http://localhost:8000

# Get just the headers
curl -I http://127.0.0.1:8000

# Get first 20 lines
curl http://127.0.0.1:8000 | head -20
```

## ❌ Common Mistakes

```bash
# WRONG - Missing port number (tries port 80)
curl http://127.0.0.1

# WRONG - Incomplete IP address
curl http://127.0.0.

# CORRECT - Include port 8000
curl http://127.0.0.1:8000
```

## 🌐 Accessing from Browser

Since you're on AWS, you need SSH port forwarding:

**On your local computer:**
```bash
ssh -L 8000:localhost:8000 ubuntu@<server-ip>
```

**Then in your browser:**
```
http://localhost:8000
```

## 🔍 Verify Server is Running

```bash
# Check if process is running
ps aux | grep "mkdocs serve"

# Check if port is listening
ss -tuln | grep :8000

# Test the connection
curl http://127.0.0.1:8000
```

