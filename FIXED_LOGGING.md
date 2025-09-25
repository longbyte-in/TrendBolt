# Fixed: MCP Server Logs for Claude Desktop

## ✅ Issues Fixed

1. **JSON Parsing Error**: Fixed by removing stdout logging that interfered with MCP protocol
2. **Async/Await Error**: Fixed by properly handling coroutines
3. **Added stderr logging**: Logs now go to stderr (visible in Claude Desktop console) without breaking MCP communication

## 🔧 What's Been Updated

### Your `claude_desktop_config.json` now has:
- ✅ Logging environment variables
- ✅ Uses the original server (with added logging)
- ✅ Fixed min_score default to 1 (more generic)

### Server now logs to stderr:
- ✅ Tool calls and arguments
- ✅ Enhanced queries
- ✅ Pipeline execution status
- ✅ Error details with stack traces

## 📊 How to See Logs

### Option 1: Claude Desktop Developer Console (Recommended)
1. Open Claude Desktop
2. Go to **Help → Show Developer Console**
3. Look for `[TRENDBOLT]` messages

### Option 2: Terminal (if running from command line)
```bash
# The logs will appear in stderr, visible in terminal
python -m trendbolt_mcp.server
```

### Option 3: Log File
```bash
# Watch the log file
tail -f /Users/ikan/Projects/TrendBolt/trendbolt.log
```

## 🚀 Quick Start

1. **Your config is ready** - no changes needed!
2. **Restart Claude Desktop** to apply the fixes
3. **Open Developer Console** (Help → Show Developer Console)
4. **Use TrendBolt** and watch the `[TRENDBOLT]` logs appear!

## 📝 Example Log Output

```
[TRENDBOLT] Tool called: trendbolt
[TRENDBOLT] Arguments: {'query': 'Find trending tech topics', 'subreddits': ['technology']}
[TRENDBOLT] Enhanced query: Find trending tech topics Focus on these subreddits: technology
[TRENDBOLT] Executing pipeline...
[TRENDBOLT] Pipeline completed. Success: True
```

## 🔍 Troubleshooting

- **No logs in console**: Make sure Developer Console is open
- **Still getting JSON errors**: Restart Claude Desktop completely
- **Want more detailed logs**: Use `run_server_simple_logs.py` instead

The MCP server should now work properly with visible logging in Claude Desktop!
