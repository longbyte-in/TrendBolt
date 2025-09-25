# How to Add MCP Server Logs to Claude Desktop

## Option 1: Use Your Current Config with Logging (Recommended)

Your current `claude_desktop_config.json` now has logging enabled. The logs will be saved to:
- **Console**: Visible in Claude Desktop's developer console
- **File**: `/Users/ikan/Projects/TrendBolt/trendbolt.log`

### To see logs:

1. **Watch the log file in real-time**:
   ```bash
   tail -f /Users/ikan/Projects/TrendBolt/trendbolt.log
   ```

2. **Check Claude Desktop's developer console**:
   - Open Claude Desktop
   - Go to Help → Show Developer Console
   - Look for TrendBolt logs

## Option 2: Use Enhanced Logging Script

If you want more detailed logs, use the alternative config:

1. **Replace your config** with `claude_desktop_config_with_logs.json`
2. **Restart Claude Desktop**
3. **Watch logs**:
   ```bash
   tail -f /Users/ikan/Projects/TrendBolt/trendbolt.log
   ```

## What You'll See in Logs

The logs will show:
- When tools are called
- Reddit API requests and responses
- LangChain agent processing
- Any errors that occur

## Example Log Output

```
2025-09-25 15:07:01,753 - INFO - Starting simple pipeline with query: Find trending technology topics
2025-09-25 15:07:03,887 - INFO - Fetching trending posts from subreddits: ['technology']
2025-09-25 15:07:05,481 - INFO - Found 10 posts from technology (score >= 1)
2025-09-25 15:07:14,229 - INFO - Agent execution completed. Messages: 4
```

## Quick Start

1. **Your config is already updated** with logging
2. **Restart Claude Desktop**
3. **Run this command** to watch logs:
   ```bash
   tail -f /Users/ikan/Projects/TrendBolt/trendbolt.log
   ```
4. **Use TrendBolt in Claude Desktop** and watch the logs!

## Troubleshooting

- **No logs appearing**: Check file permissions on the log file
- **Logs too verbose**: Change `TRENDBOLT_LOG_LEVEL` to `WARNING` or `ERROR`
- **Log file location**: Change `TRENDBOLT_LOG_FILE` to your preferred path
