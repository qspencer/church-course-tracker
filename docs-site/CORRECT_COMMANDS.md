# Correct Commands for Testing the Server

## ✅ Working Commands

### Option 1: Follow Redirects (Recommended)
```bash
curl -L -s http://127.0.0.1:8000 | head -10
```

The `-L` flag tells curl to follow redirects, and `-s` silences the progress output.

### Option 2: Access the Redirected Path Directly
```bash
curl -s http://127.0.0.1:8000/churchcoursetracker/ | head -10
```

### Option 3: Get Just the Title
```bash
curl -L -s http://127.0.0.1:8000 | grep -o '<title>[^<]*</title>'
```

### Option 4: Check HTTP Status
```bash
curl -I -L http://127.0.0.1:8000
```

## ❌ Why Your Command Didn't Show Output

When you ran:
```bash
curl http://127.0.0.1:8000 | head -10
```

The issue was:
1. **No `-L` flag**: The server redirects from `/` to `/churchcoursetracker/`, but curl didn't follow the redirect
2. **Progress output**: Without `-s`, curl shows progress information that can interfere with `head`
3. **Empty response**: The redirect response (HTTP 302) has no body, so `head` had nothing to show

## 🌐 Accessing from Browser

The server is working! To access it from your browser:

1. **Set up SSH port forwarding** (on your local machine):
   ```bash
   ssh -L 8000:localhost:8000 ubuntu@<server-ip>
   ```

2. **Open in browser**:
   ```
   http://localhost:8000
   ```

The browser will automatically follow the redirect to `/churchcoursetracker/`.

## 🔍 Verify Server Status

```bash
# Check if server is running
ps aux | grep "mkdocs serve"

# Check if port is listening
ss -tuln | grep :8000

# Test with full output
curl -L -s http://127.0.0.1:8000 | head -20
```

