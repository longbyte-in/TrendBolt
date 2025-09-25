"""
LangChain Workflow Orchestrator for TrendBolt

This module implements a comprehensive LangChain-based workflow system that orchestrates
the entire TrendBolt pipeline: Reddit content discovery → LLM content generation → 
Canva design creation → LinkedIn publishing.

Features:
- Dynamic workflow planning and execution
- Error handling and retry logic
- State management across workflow steps
- Flexible tool integration
- Monitoring and logging
"""

from __future__ import annotations

import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from datetime import datetime

from langchain_core.tools import Tool, tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from ..config import get_settings
from ..tools.reddit import get_trending, get_post_by_id
from ..tools.llm import generate_canvas_post
from ..tools.canva_connect import (
    create_autofill_job_from_values,
    get_autofill_job,
    upload_image_from_url
)
from ..tools.linkedin import create_image_post, create_text_post

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State maintained throughout the workflow execution."""
    messages: Annotated[List[Any], add_messages]
    current_step: str
    reddit_topics: List[Dict[str, Any]]
    selected_topic: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    canva_design: Optional[Dict[str, Any]]
    linkedin_post: Optional[Dict[str, Any]]
    error_log: List[str]
    metadata: Dict[str, Any]


class TrendBoltLangChainAgent:
    """
    LangChain-powered workflow orchestrator for TrendBolt automation.
    
    This agent manages the complete pipeline from Reddit trending topics
    to LinkedIn post publication, with intelligent decision-making and
    error recovery capabilities.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logger
        self._setup_llm()
        self._create_tools()
        self._build_workflow()
        
    def _setup_llm(self):
        """Initialize Azure OpenAI language model."""
        from langchain_openai import AzureChatOpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            deployment_name=self.settings.azure_openai_deployment,
            api_version=getattr(self.settings, "azure_openai_api_version", "2024-06-01"),
            temperature=0.7,
        )
    
    def _create_tools(self):
        """Create LangChain tools for each service integration."""
        
        async def reddit_trending_tool(
            subreddits: str = "technology,programming,artificial",
            strategy: str = "hot",
            limit: int = 10,
            min_score: int = 100
        ) -> str:
            """Fetch trending posts from Reddit subreddits."""
            try:
                subreddit_list = [s.strip() for s in subreddits.split(",")]
                topics = await get_trending(
                    subreddits=subreddit_list,
                    strategy=strategy,
                    limit=limit,
                    min_score=min_score
                )
                return json.dumps({"success": True, "topics": topics})
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        async def reddit_post_tool(post_id: str) -> str:
            """Fetch a specific Reddit post by ID."""
            try:
                post = await get_post_by_id(post_id)
                return json.dumps({"success": True, "post": post})
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        @tool
        def content_generation_tool(
            topic_title: str,
            topic_url: str = "",
            brand_voice: str = "engaging and informative",
            cta: str = "Follow TrendBolt"
        ) -> str:
            """Generate social media content from a topic title and URL."""
            try:
                topic = {"title": topic_title, "url": topic_url}
                brand = {"voice": brand_voice, "cta": cta}
                content = generate_canvas_post(topic=topic, brand=brand)
                return json.dumps({"success": True, "content": content})
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        @tool
        def canva_create_design_tool(
            title: str,
            description: str,
            image_url: str = ""
        ) -> str:
            """Create a Canva design job with title, description, and optional image URL."""
            try:
                # Prepare autofill data
                data = {
                    "title": title,
                    "description": description,
                }
                if image_url:
                    data["image"] = image_url
                
                # Create autofill job using existing Canva tool
                job = create_autofill_job_from_values(
                    values=data,
                    image_fields={"image": "image"} if image_url else {}
                )
                
                return json.dumps({"success": True, "job": job})
                
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        @tool
        def canva_get_design_tool(job_id: str) -> str:
            """Get Canva design job status and result by job ID."""
            try:
                status = get_autofill_job(job_id)
                return json.dumps({"success": True, "status": status})
                
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        async def linkedin_post_tool(
            text: str,
            image_url: str = ""
        ) -> str:
            """Create a LinkedIn post."""
            try:
                if image_url:
                    result = create_image_post(image_url=image_url, text=text)
                else:
                    result = create_text_post(text=text)
                return json.dumps({"success": True, "post": result})
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        # Convert async functions to sync for LangChain compatibility
        @tool
        def sync_reddit_trending(
            subreddits: str = "technology,programming,artificial", 
            strategy: str = "hot", 
            limit: int = 10, 
            min_score: int = 5
        ) -> str:
            """Fetch trending posts from Reddit subreddits. Use comma-separated subreddit names."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, create a new task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, reddit_trending_tool(subreddits=subreddits, strategy=strategy, limit=limit, min_score=min_score))
                        return future.result()
                else:
                    return asyncio.run(reddit_trending_tool(subreddits=subreddits, strategy=strategy, limit=limit, min_score=min_score))
            except RuntimeError:
                # Fallback: run in new event loop
                return asyncio.run(reddit_trending_tool(subreddits=subreddits, strategy=strategy, limit=limit, min_score=min_score))
        
        @tool
        def sync_reddit_post(post_id: str) -> str:
            """Fetch a specific Reddit post by ID (e.g., t3_1ndjq1c)."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, reddit_post_tool(post_id=post_id))
                        return future.result()
                else:
                    return asyncio.run(reddit_post_tool(post_id=post_id))
            except RuntimeError:
                return asyncio.run(reddit_post_tool(post_id=post_id))
        
        @tool
        def sync_linkedin_post(text: str, image_url: str = "") -> str:
            """Create a LinkedIn post with text and optional image URL."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, linkedin_post_tool(text=text, image_url=image_url))
                        return future.result()
                else:
                    return asyncio.run(linkedin_post_tool(text=text, image_url=image_url))
            except RuntimeError:
                return asyncio.run(linkedin_post_tool(text=text, image_url=image_url))
        
        self.tools = [
            sync_reddit_trending,
            sync_reddit_post,
            content_generation_tool,
            canva_create_design_tool,
            canva_get_design_tool,
            sync_linkedin_post,
        ]
    
    def _build_workflow(self):
        """Build the LangGraph workflow."""
        
        # Create the agent with tools
        self.agent = create_react_agent(
            self.llm, 
            self.tools,
            checkpointer=MemorySaver()
        )
        
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("discover", self._discover_content)
        workflow.add_node("generate", self._generate_content)
        workflow.add_node("design", self._create_design)
        workflow.add_node("publish", self._publish_content)
        workflow.add_node("agent", self._run_agent)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._route_next_step,
            {
                "discover": "discover",
                "generate": "generate", 
                "design": "design",
                "publish": "publish",
                "end": END
            }
        )
        workflow.add_edge("discover", "agent")
        workflow.add_edge("generate", "agent")
        workflow.add_edge("design", "agent")
        workflow.add_edge("publish", END)
        
        self.workflow = workflow.compile(checkpointer=MemorySaver())
    
    async def _discover_content(self, state: WorkflowState) -> WorkflowState:
        """Discover trending content from Reddit."""
        try:
            subreddits = state.get("metadata", {}).get("subreddits", ["technology", "programming"])
            topics = await get_trending(
                subreddits=subreddits,
                strategy="hot",
                limit=10,
                min_score=5
            )
            
            state["reddit_topics"] = topics
            state["current_step"] = "generate"
            state["messages"].append(
                AIMessage(content=f"Found {len(topics)} trending topics from Reddit.")
            )
            
        except Exception as e:
            error_msg = f"Content discovery failed: {str(e)}"
            state["error_log"].append(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            
        return state
    
    async def _generate_content(self, state: WorkflowState) -> WorkflowState:
        """Generate content from selected topic."""
        try:
            if not state.get("reddit_topics"):
                raise ValueError("No topics available for content generation")
            
            # Select best topic (highest score)
            topic = max(state["reddit_topics"], key=lambda x: x.get("score", 0))
            state["selected_topic"] = topic
            
            # Generate content
            content = generate_canvas_post(
                topic=topic,
                brand={"voice": "engaging and informative", "cta": "Follow TrendBolt"}
            )
            
            state["generated_content"] = content
            state["current_step"] = "design"
            state["messages"].append(
                AIMessage(content=f"Generated content for: {topic.get('title', 'Unknown topic')}")
            )
            
        except Exception as e:
            error_msg = f"Content generation failed: {str(e)}"
            state["error_log"].append(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            
        return state
    
    async def _create_design(self, state: WorkflowState) -> WorkflowState:
        """Create visual design with Canva using separate create and get methods."""
        try:
            content = state.get("generated_content")
            if not content:
                raise ValueError("No content available for design creation")
            
            # Step 1: Create design job
            data = {
                "title": content.get("title", ""),
                "description": content.get("description", ""),
            }
            
            job = create_autofill_job_from_values(values=data, image_fields={})
            if not job.get("success"):
                raise Exception("Failed to create Canva design job")
            
            job_id = job["job"]["id"]
            state["metadata"]["canva_job_id"] = job_id
            
            # Step 2: Poll for completion with enhanced error handling
            max_attempts = 20
            poll_interval = 3
            
            for attempt in range(max_attempts):
                await asyncio.sleep(poll_interval)
                
                try:
                    status = get_autofill_job(job_id)
                    job_status = status["job"]["status"]
                    
                    if job_status == "success":
                        design = status["job"]["result"]["design"]
                        # Ensure we have a valid thumbnail URL before proceeding
                        if design.get("thumbnail", {}).get("url"):
                            state["canva_design"] = design
                            state["current_step"] = "publish"
                            state["messages"].append(
                                AIMessage(content=f"Design created successfully with Canva after {attempt + 1} attempts.")
                            )
                            break
                        else:
                            # Continue polling if no thumbnail URL yet
                            continue
                            
                    elif job_status == "failed":
                        error_msg = status["job"].get("error", "Unknown error")
                        raise Exception(f"Canva design job failed: {error_msg}")
                    elif job_status in ["pending", "processing"]:
                        # Continue polling
                        continue
                    else:
                        # Unknown status, continue polling
                        continue
                        
                except Exception as poll_error:
                    # Log polling error but continue trying
                    self.logger.warning(f"Design polling attempt {attempt + 1} failed: {poll_error}")
                    continue
            else:
                raise Exception(f"Canva design job timeout after {max_attempts} attempts")
                
        except Exception as e:
            error_msg = f"Design creation failed: {str(e)}"
            state["error_log"].append(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            
        return state
    
    async def _publish_content(self, state: WorkflowState) -> WorkflowState:
        """Publish content to LinkedIn."""
        try:
            content = state.get("generated_content")
            design = state.get("canva_design")
            
            if not content:
                raise ValueError("No content available for publishing")
            
            # Publish to LinkedIn
            text = content.get("description", "")
            image_url = design.get("thumbnail", {}).get("url") if design else ""
            
            if image_url:
                result = create_image_post(image_url=image_url, text=text)
            else:
                result = create_text_post(text=text)
            
            state["linkedin_post"] = result
            state["current_step"] = "completed"
            state["messages"].append(
                AIMessage(content="Content published successfully to LinkedIn!")
            )
            
        except Exception as e:
            error_msg = f"Publishing failed: {str(e)}"
            state["error_log"].append(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            
        return state
    
    async def _run_agent(self, state: WorkflowState) -> WorkflowState:
        """Run the LangChain agent to make decisions."""
        try:
            # Get the latest message to determine what to do
            if not state.get("messages"):
                # Initial state
                state["messages"] = [
                    HumanMessage(content="Execute the TrendBolt pipeline: discover trending content, generate posts, create designs, and publish to LinkedIn.")
                ]
                state["current_step"] = "discover"
            
            # Let the agent process the current state
            result = await self.agent.ainvoke(
                {"messages": state["messages"]},
                config={"configurable": {"thread_id": "trendbolt_workflow"}}
            )
            
            # Update messages with agent response
            if "messages" in result:
                state["messages"] = result["messages"]
                
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            state["error_log"].append(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            
        return state
    
    def _route_next_step(self, state: WorkflowState) -> str:
        """Route to the next step based on current state."""
        current_step = state.get("current_step", "discover")
        
        # Check if we have errors that should stop the workflow
        if state.get("error_log") and len(state["error_log"]) > 3:
            return "end"
        
        # Route based on current step and available data
        if current_step == "discover" and not state.get("reddit_topics"):
            return "discover"
        elif current_step == "generate" and not state.get("generated_content"):
            return "generate"
        elif current_step == "design" and not state.get("canva_design"):
            return "design"
        elif current_step == "publish" and not state.get("linkedin_post"):
            return "publish"
        elif current_step == "completed":
            return "end"
        else:
            # Continue with agent for decision making
            return "end"
    
    async def execute_workflow(
        self,
        subreddits: Optional[List[str]] = None,
        strategy: str = "hot",
        min_score: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the complete TrendBolt workflow.
        
        Args:
            subreddits: List of subreddits to search (default: ["technology", "programming"])
            strategy: Reddit search strategy ("hot", "top", "new")
            min_score: Minimum score threshold for posts
            
        Returns:
            Dictionary containing workflow results and status
        """
        initial_state = WorkflowState(
            messages=[],
            current_step="discover",
            reddit_topics=[],
            selected_topic=None,
            generated_content=None,
            canva_design=None,
            linkedin_post=None,
            error_log=[],
            metadata={
                "subreddits": subreddits or ["technology", "programming"],
                "strategy": strategy,
                "min_score": min_score,
                "started_at": datetime.now().isoformat()
            }
        )
        
        try:
            # Execute the workflow
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": f"workflow_{datetime.now().timestamp()}"}}
            )
            
            return {
                "success": len(final_state.get("error_log", [])) == 0,
                "status": final_state.get("current_step", "unknown"),
                "topic": final_state.get("selected_topic"),
                "content": final_state.get("generated_content"),
                "design": final_state.get("canva_design"),
                "linkedin_post": final_state.get("linkedin_post"),
                "errors": final_state.get("error_log", []),
                "metadata": final_state.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "metadata": initial_state["metadata"]
            }
    
    async def execute_simple_pipeline(
        self,
        query: str,
        subreddits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a simplified pipeline using the agent directly.
        
        Args:
            query: Natural language query describing what to do
            subreddits: Optional list of subreddits to focus on
            
        Returns:
            Dictionary containing the agent's response and actions taken
        """
        try:
            # Prepare context message
            context = f"User request: {query}"
            if subreddits:
                context += f"\nFocus on subreddits: {', '.join(subreddits)}"
            
            # Execute with the agent
            result = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=context)]},
                config={"configurable": {"thread_id": f"simple_{datetime.now().timestamp()}"}}
            )
            
            # Convert messages to serializable format
            serializable_messages = []
            for msg in result.get("messages", []):
                serializable_messages.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content
                })
            
            return {
                "success": True,
                "messages": serializable_messages,
                "response": result["messages"][-1].content if result.get("messages") else "No response"
            }
            
        except Exception as e:
            self.logger.error(f"Simple pipeline execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
