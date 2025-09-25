# LangChain Workflow

The LangChain workflow provides AI-powered orchestration with intelligent decision-making, error recovery, and natural language control for TrendBolt automation.

## 📋 Overview

**File**: `trendbolt_mcp/orchestrator/langchain_agent.py`  
**Type**: AI-orchestrated workflow  
**Dependencies**: LangChain, LangGraph, Azure OpenAI  

## 🧠 Key Features

- **Intelligent Orchestration**: AI-powered decision making at each step
- **Natural Language Control**: Execute workflows with natural language queries
- **State Management**: Persistent state tracking across workflow steps
- **Error Recovery**: Automatic retry logic and graceful error handling
- **Dynamic Tool Usage**: Intelligent tool selection and execution

## 🔄 Workflow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  LangGraph      │───▶│  Azure OpenAI   │───▶│  Tool Executor  │
│  State Manager  │    │  Decision Engine │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Workflow Steps │    │  Error Recovery │    │  Result Handler │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Available Tools

### **Reddit Tools**
- `reddit_trending`: Fetch trending posts from subreddits
- `reddit_post`: Get specific post details by ID

### **Content Generation**
- `generate_content`: Create social media content from topics

### **Canva Tools**
- `canva_create_design`: Create Canva design job
- `canva_get_design`: Check design job status and get results

### **LinkedIn Publishing**
- `post_to_linkedin`: Publish content to LinkedIn

## 🚀 Usage

### **1. Structured Workflow Execution**

```python
from trendbolt_mcp.orchestrator import TrendBoltLangChainAgent

# Initialize agent
agent = TrendBoltLangChainAgent()

# Execute structured workflow
result = await agent.execute_workflow(
    subreddits=["technology", "programming"],
    strategy="hot",
    min_score=150
)

if result["success"]:
    print(f"✅ Workflow completed!")
    print(f"Topic: {result['topic']['title']}")
    print(f"LinkedIn Post: {result['linkedin_post']['post_id']}")
else:
    print(f"❌ Workflow failed: {result['errors']}")
```

### **2. Natural Language Control**

```python
# Natural language workflow execution
result = await agent.execute_simple_pipeline(
    query="Find trending AI topics and create a professional LinkedIn post",
    subreddits=["artificial", "MachineLearning"]
)

print(f"Response: {result['response']}")
```

### **3. MCP Tool Integration**

#### **Structured Workflow**
```json
{
  "name": "langchain_workflow",
  "arguments": {
    "subreddits": ["technology", "programming"],
    "strategy": "hot",
    "min_score": 100
  }
}
```

#### **Natural Language Query**
```json
{
  "name": "langchain_agent_query",
  "arguments": {
    "query": "Find popular startup news and create engaging content",
    "subreddits": ["startups", "entrepreneur"]
  }
}
```

## 🎯 Workflow Steps

### **1. Discovery Phase**
```python
async def _discover_content(self, state: WorkflowState) -> WorkflowState:
    # Fetch trending topics from Reddit
    # Apply intelligent filtering
    # Update workflow state
```

### **2. Content Generation Phase**
```python
async def _generate_content(self, state: WorkflowState) -> WorkflowState:
    # Select best topic using AI
    # Generate engaging content
    # Apply brand guidelines
```

### **3. Design Creation Phase**
```python
async def _create_design(self, state: WorkflowState) -> WorkflowState:
    # Create Canva design job
    # Enhanced polling with retry logic
    # Validate thumbnail URL availability
```

### **4. Publishing Phase**
```python
async def _publish_content(self, state: WorkflowState) -> WorkflowState:
    # Publish to LinkedIn
    # Handle both image and text posts
    # Return post details
```

## 🔧 Enhanced Canva Integration

### **Separate Create and Get Methods**

The LangChain workflow uses separate Canva tools for better control:

```python
# Step 1: Create design job
def canva_create_design_tool(title: str, description: str, image_url: str = "") -> str:
    job = create_autofill_job_from_values(values=data, image_fields=image_fields)
    return json.dumps({"success": True, "job": job})

# Step 2: Poll for completion
def canva_get_design_tool(job_id: str) -> str:
    status = get_autofill_job(job_id)
    return json.dumps({"success": True, "status": status})
```

### **Enhanced Polling Logic**

```python
# Enhanced polling with better error handling
max_attempts = 20  # Increased from 10
poll_interval = 3   # Increased from 2 seconds

for attempt in range(max_attempts):
    await asyncio.sleep(poll_interval)
    
    status = get_autofill_job(job_id)
    job_status = status["job"]["status"]
    
    if job_status == "success":
        design = status["job"]["result"]["design"]
        # Ensure we have a valid thumbnail URL before proceeding
        if design.get("thumbnail", {}).get("url"):
            break
```

## 📊 State Management

### **WorkflowState Structure**

```python
class WorkflowState(TypedDict):
    messages: List[Any]              # Conversation history
    current_step: str                # Current workflow step
    reddit_topics: List[Dict]        # Discovered topics
    selected_topic: Optional[Dict]   # Selected topic for content
    generated_content: Optional[Dict] # Generated content
    canva_design: Optional[Dict]     # Created design assets
    linkedin_post: Optional[Dict]    # Published post details
    error_log: List[str]            # Error tracking
    metadata: Dict[str, Any]        # Execution metadata
```

### **State Transitions**

```
discover → generate → design → publish → completed
    ↓         ↓         ↓         ↓
  agent ← agent ← agent ← agent ← end
```

## ⚙️ Configuration

### **Predefined Workflow Configurations**

```python
from trendbolt_mcp.orchestrator.workflow_config import get_workflow_config

# Available configurations
configs = [
    "tech_news",      # Technology news and updates
    "ai_trends",      # AI and machine learning topics
    "startup_news",   # Startup and business content
    "dev_tools",      # Developer tools and programming
    "quick_viral"     # Fast viral content creation
]

# Use predefined configuration
config = get_workflow_config("tech_news")
result = await agent.execute_workflow(
    subreddits=config.subreddits,
    strategy=config.strategy,
    min_score=config.min_score
)
```

### **Content Styles**

```python
from trendbolt_mcp.orchestrator.workflow_config import get_content_style

# Available styles: professional, technical, business, engaging, viral
style = get_content_style("professional")
# Returns: voice, tone, cta, hashtags
```

## 🛡️ Error Handling

### **Multi-Level Error Recovery**

1. **Tool-Level Errors**: Individual tool failures with retry logic
2. **Step-Level Errors**: Workflow step failures with alternative paths
3. **Workflow-Level Errors**: Complete workflow failure handling
4. **Agent-Level Errors**: AI decision-making errors

### **Error Tracking**

```python
# Error log in workflow state
state["error_log"].append(error_msg)

# Final result includes all errors
return {
    "success": len(final_state.get("error_log", [])) == 0,
    "errors": final_state.get("error_log", []),
    "status": final_state.get("current_step", "unknown")
}
```

## 🎨 Natural Language Examples

### **Content Creation Queries**
- "Find trending AI topics and create a professional LinkedIn post"
- "Look for popular programming discussions and make engaging content"
- "Search for startup news and create a business-focused post with visuals"

### **Workflow Control Queries**
- "Create viral content from trending technology news"
- "Generate professional posts about machine learning breakthroughs"
- "Make engaging content about developer tools and frameworks"

## 📈 Performance Optimization

### **Intelligent Polling**
- **20 attempts** maximum (vs 10 in basic pipeline)
- **3-second intervals** (vs 2 seconds)
- **URL validation** before proceeding
- **Graceful timeout handling**

### **State Persistence**
- **Memory-based checkpoints** for workflow state
- **Recovery from interruptions**
- **Progress tracking and resumption**

## 🔄 Workflow Variations

### **Custom Workflow Configuration**

```python
from trendbolt_mcp.orchestrator.workflow_config import create_custom_config

custom_config = create_custom_config(
    name="DevOps Focus",
    subreddits=["devops", "kubernetes", "docker"],
    strategy="top",
    min_score=75,
    content_style="technical"
)
```

### **Multi-Step Natural Language**

```python
queries = [
    "First, find trending AI topics",
    "Then create professional content",
    "Finally, publish to LinkedIn with visuals"
]

for query in queries:
    result = await agent.execute_simple_pipeline(query=query)
```

## 🧪 Testing

### **Unit Tests**
```bash
pytest tests/test_langchain_workflow.py::TestTrendBoltLangChainAgent -v
```

### **Integration Tests**
```bash
pytest tests/test_langchain_workflow.py::TestWorkflowIntegration -v
```

### **Configuration Tests**
```bash
pytest tests/test_langchain_workflow.py::TestWorkflowConfig -v
```

## 🔗 Related Documentation

- [Basic Pipeline](./basic-pipeline.md) - Simple sequential workflow
- [MCP Tools](./mcp-tools.md) - Tool-based interface
- [Workflow Configuration](../configuration/workflow-config.md) - Configuration details
- [Azure OpenAI Integration](../integrations/azure-openai.md) - LLM setup
