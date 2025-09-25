"""
Workflow Configuration for TrendBolt LangChain Integration

This module provides configuration settings and templates for different
workflow scenarios in TrendBolt.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class WorkflowConfig:
    """Configuration for a TrendBolt workflow execution."""
    name: str
    description: str
    subreddits: List[str]
    strategy: str = "hot"
    min_score: int = 100
    max_posts: int = 10
    content_style: str = "engaging"
    target_platform: str = "linkedin"
    include_images: bool = True
    auto_publish: bool = False


# Predefined workflow configurations
WORKFLOW_CONFIGS = {
    "tech_news": WorkflowConfig(
        name="Technology News",
        description="Find trending technology news and create professional content",
        subreddits=["technology", "programming", "artificial", "MachineLearning"],
        strategy="hot",
        min_score=200,
        content_style="professional",
        include_images=True
    ),
    
    "ai_trends": WorkflowConfig(
        name="AI & ML Trends",
        description="Focus on AI and machine learning trending topics",
        subreddits=["artificial", "MachineLearning", "OpenAI", "ChatGPT"],
        strategy="hot",
        min_score=150,
        content_style="technical",
        include_images=True
    ),
    
    "startup_news": WorkflowConfig(
        name="Startup & Business",
        description="Startup and business trending content",
        subreddits=["startups", "entrepreneur", "business"],
        strategy="hot",
        min_score=100,
        content_style="business",
        include_images=True
    ),
    
    "dev_tools": WorkflowConfig(
        name="Developer Tools",
        description="Latest developer tools and programming resources",
        subreddits=["programming", "webdev", "javascript", "Python"],
        strategy="hot",
        min_score=100,
        content_style="technical",
        include_images=False
    ),
    
    "quick_viral": WorkflowConfig(
        name="Quick Viral Content",
        description="Fast turnaround viral content from multiple sources",
        subreddits=["technology", "todayilearned", "explainlikeimfive"],
        strategy="hot",
        min_score=500,
        max_posts=5,
        content_style="viral",
        include_images=True,
        auto_publish=True
    )
}


def get_workflow_config(name: str) -> WorkflowConfig:
    """Get a predefined workflow configuration."""
    return WORKFLOW_CONFIGS.get(name, WORKFLOW_CONFIGS["tech_news"])


def list_workflow_configs() -> List[str]:
    """List all available workflow configuration names."""
    return list(WORKFLOW_CONFIGS.keys())


def create_custom_config(
    name: str,
    subreddits: List[str],
    strategy: str = "hot",
    min_score: int = 100,
    content_style: str = "engaging"
) -> WorkflowConfig:
    """Create a custom workflow configuration."""
    return WorkflowConfig(
        name=name,
        description=f"Custom workflow: {name}",
        subreddits=subreddits,
        strategy=strategy,
        min_score=min_score,
        content_style=content_style
    )


# Content style templates
CONTENT_STYLES = {
    "professional": {
        "voice": "professional and authoritative",
        "tone": "informative",
        "cta": "Follow for professional insights",
        "hashtags": ["#TechNews", "#Business", "#Innovation"]
    },
    
    "technical": {
        "voice": "technical and precise",
        "tone": "educational",
        "cta": "Follow for technical updates",
        "hashtags": ["#Programming", "#Tech", "#Development"]
    },
    
    "business": {
        "voice": "business-focused and strategic",
        "tone": "actionable",
        "cta": "Follow for business insights",
        "hashtags": ["#Business", "#Startup", "#Strategy"]
    },
    
    "engaging": {
        "voice": "engaging and conversational",
        "tone": "approachable",
        "cta": "Follow TrendBolt for more",
        "hashtags": ["#TechTrends", "#Innovation", "#TechNews"]
    },
    
    "viral": {
        "voice": "catchy and shareable",
        "tone": "exciting",
        "cta": "Share if you agree!",
        "hashtags": ["#Viral", "#TechNews", "#MustRead"]
    }
}


def get_content_style(style_name: str) -> Dict[str, Any]:
    """Get content style configuration."""
    return CONTENT_STYLES.get(style_name, CONTENT_STYLES["engaging"])
