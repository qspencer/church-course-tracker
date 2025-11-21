# Accessing the Documentation Site Locally

## 🌐 Server Status

The MkDocs development server is running on **port 8000**.

## 📍 Access Methods

### Option 1: Direct Access (If on the same machine)

If you're accessing from the same machine where the server is running:

```
http://localhost:8000
```

or

```
http://127.0.0.1:8000
```

### Option 2: Remote Access via SSH Port Forwarding

If you're accessing from a remote machine (like your local computer), you'll need to set up SSH port forwarding:

**From your local machine, run:**

```bash
ssh -L 8000:localhost:8000 ubuntu@<your-server-ip>
```

Then in your local browser, go to:
```
http://localhost:8000
```

### Option 3: Public Access (Not Recommended for Development)

If you want to access it directly via the server's IP (requires firewall configuration):

1. Get the server's IP address
2. Configure security group/firewall to allow port 8000
3. Access via: `http://<server-ip>:8000`

**⚠️ Warning**: This exposes the development server publicly. Only use for testing.

## 🔍 Troubleshooting

### Connection Refused Error

**If you see "ERR_CONNECTION_REFUSED":**

1. **Check if server is running:**
   ```bash
   ps aux | grep "mkdocs serve"
   ```

2. **Check if port is listening:**
   ```bash
   ss -tuln | grep :8000
   ```

3. **Try restarting the server:**
   ```bash
   cd docs-site
   source venv/bin/activate
   mkdocs serve --dev-addr=0.0.0.0:8000
   ```

4. **Check firewall rules:**
   ```bash
   sudo ufw status
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
mkdocs serve --dev-addr=0.0.0.0:8001
```

Then access via port 8001.

## 🛑 Stopping the Server

To stop the server:

```bash
pkill -f "mkdocs serve"
```

Or press `Ctrl+C` in the terminal where it's running.

## ✅ Verify Server is Running

Check if the server is responding:

```bash
curl http://127.0.0.1:8000
```

You should see HTML output if the server is working.

