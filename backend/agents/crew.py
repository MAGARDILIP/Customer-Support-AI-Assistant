"""
CrewAI-style Agent Orchestration — implemented directly with GROQ SDK.
Routes customer queries to the right agent (Research, Resolution, Escalation).
Each agent has specific tools and system prompts.
"""
import logging
from backend.config import settings
from backend.core.llm import get_llm_client
from backend.tools.order_lookup import order_lookup_fn
from backend.tools.refund_checker import refund_check_fn
from backend.tools.knowledge_search import knowledge_search_fn
from backend.tools.sentiment_analyzer import get_sentiment_score

logger = logging.getLogger(__name__)


# ============================================================
# Agent System Prompts (equivalent to CrewAI agent definitions)
# ============================================================

RESEARCH_AGENT_PROMPT = """You are the Research Agent for ShopEase, an e-commerce customer support AI.

Your Role: Search company policies, FAQs, and knowledge base to answer customer questions accurately.

Your Tools Available:
- Knowledge Base Search: You have access to company policies and FAQs

Instructions:
- Search the knowledge base for relevant information before answering
- Provide accurate, policy-based answers
- STRICT RULE: Do NOT answer questions using your general knowledge. If the answer is not in the knowledge base or is unrelated to ShopEase, you MUST politely say you cannot answer it as it is out of scope.
- Be friendly and professional
- Respond in the same language the customer used
"""

RESOLUTION_AGENT_PROMPT = """You are the Customer Resolution Agent for ShopEase, an e-commerce customer support AI.

Your Role: Handle order lookups, refund requests, and transaction-related queries.

Your Tools Available:
- Order Lookup: Find orders by order number, email, or phone
- Refund Eligibility Checker: Check if an order qualifies for a refund

Instructions:
- Use order details provided to look up specific information
- Check refund eligibility when customer asks about returns/refunds
- Provide clear status updates and next steps
- Be professional and solution-oriented
- Respond in the same language the customer used
"""

ESCALATION_AGENT_PROMPT = """You are the Escalation Agent for ShopEase, an e-commerce customer support AI.

Your Role: Handle frustrated, angry, or dissatisfied customers with empathy and authority.

Instructions:
- Acknowledge the customer's frustration sincerely
- Apologize for the inconvenience
- Show empathy and understanding
- Offer concrete solutions or alternatives
- Provide a sense of urgency and priority
- If needed, offer to connect with a human supervisor
- Never be defensive or dismissive
- Respond in the same language the customer used
"""


def classify_intent(message: str, sentiment_score: float) -> str:
    """
    Classify the customer's intent to route to the right agent.
    Returns one of: 'research', 'resolution', 'escalation'
    """
    message_lower = message.lower()

    # Escalation indicators (check first)
    if sentiment_score <= -0.4:
        return "escalation"

    escalation_keywords = [
        "furious", "terrible", "worst", "unacceptable", "disgusting",
        "scam", "fraud", "lawyer", "legal", "sue", "complaint",
        "manager", "supervisor", "never again", "horrible", "pathetic",
    ]
    if any(kw in message_lower for kw in escalation_keywords):
        return "escalation"

    # Resolution indicators (order/refund queries)
    resolution_keywords = [
        "order", "ord-", "tracking", "delivery", "delivered",
        "refund", "return", "cancel", "status", "shipped",
        "where is my", "track my", "money back", "exchange",
        "wrong item", "damaged", "missing", "lost package",
    ]
    if any(kw in message_lower for kw in resolution_keywords):
        return "resolution"

    # Default: Research (policy/FAQ queries)
    return "research"


def _use_tools(message: str, intent: str) -> str:
    """
    Run the appropriate tools based on intent and return context.
    The agent decides which tool to use — this is the tool execution layer.
    """
    tool_results = []
    tools_used = []

    if intent == "research":
        # Use Knowledge Base Search
        kb_result = knowledge_search_fn(message)
        if kb_result and "No relevant" not in kb_result:
            tool_results.append(f"[Knowledge Base Search Results]:\n{kb_result}")
            tools_used.append("Knowledge Base Search")
        else:
            tool_results.append("[Knowledge Base Search Results]:\nNo relevant information found in the knowledge base. This query is out of scope. Do not try to answer it using general knowledge.")
            tools_used.append("Knowledge Base Search")

    elif intent == "resolution":
        # Extract order number if present
        import re
        order_match = re.search(r'ORD-\d+', message.upper())

        if order_match:
            order_num = order_match.group()
            # Order Lookup
            order_result = order_lookup_fn(order_num)
            tool_results.append(f"[Order Lookup Result]:\n{order_result}")
            tools_used.append("Order Lookup")

            # Refund check if mentioned
            if any(kw in message.lower() for kw in ["refund", "return", "money back"]):
                refund_result = refund_check_fn(order_num)
                tool_results.append(f"[Refund Eligibility Check]:\n{refund_result}")
                tools_used.append("Refund Eligibility Checker")
        else:
            # Try knowledge base for general resolution queries
            kb_result = knowledge_search_fn(message)
            if kb_result and "No relevant" not in kb_result:
                tool_results.append(f"[Knowledge Base Search Results]:\n{kb_result}")
                tools_used.append("Knowledge Base Search")
            else:
                tool_results.append("[Knowledge Base Search Results]:\nNo relevant information found in the knowledge base. This query is out of scope. Do not try to answer it using general knowledge.")
                tools_used.append("Knowledge Base Search")

    elif intent == "escalation":
        # Use sentiment analysis + knowledge base
        tools_used.append("Sentiment Analyzer")
        kb_result = knowledge_search_fn(message)
        if kb_result and "No relevant" not in kb_result:
            tool_results.append(f"[Knowledge Base Search Results]:\n{kb_result}")
            tools_used.append("Knowledge Base Search")
        else:
            tool_results.append("[Knowledge Base Search Results]:\nNo relevant information found in the knowledge base. This query is out of scope. Do not try to answer it using general knowledge.")
            tools_used.append("Knowledge Base Search")

    context = "\n\n".join(tool_results) if tool_results else ""
    return context, tools_used


def run_crew(
    message: str,
    chat_history: list[dict] | None = None,
    sentiment_score: float = 0.0,
) -> dict:
    """
    Run the multi-agent system to handle a customer query.
    Routes to Research, Resolution, or Escalation agent based on intent.
    The agent decides which tool to use.
    """
    try:
        llm = get_llm_client()

        # Classify intent
        intent = classify_intent(message, sentiment_score)
        logger.info(f"Intent classified as: {intent} (sentiment: {sentiment_score:.2f})")

        # Select agent
        if intent == "escalation":
            system_prompt = ESCALATION_AGENT_PROMPT
            agent_name = "Escalation Agent"
        elif intent == "resolution":
            system_prompt = RESOLUTION_AGENT_PROMPT
            agent_name = "Resolution Agent"
        else:
            system_prompt = RESEARCH_AGENT_PROMPT
            agent_name = "Research Agent"

        # Run tools (agent decides which to use)
        tool_context, tools_used = _use_tools(message, intent)

        # Build conversation messages
        messages = []

        # Add chat history for context
        if chat_history:
            recent = chat_history[-6:]
            for msg in recent:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Build the user message with tool context
        user_content = message
        if tool_context:
            user_content = (
                f"Customer Message: {message}\n\n"
                f"--- Tool Results (use these to answer accurately) ---\n"
                f"{tool_context}\n\n"
                f"Use the tool results above to provide an accurate, helpful response. "
                f"Do NOT show raw tool output to the customer — summarize naturally."
            )

        messages.append({"role": "user", "content": user_content})

        # Get LLM response
        response = llm.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024,
        )

        return {
            "response": response,
            "agent_used": agent_name,
            "tools_used": tools_used,
            "intent": intent,
            "sentiment_score": sentiment_score,
        }

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return _fallback_response(message, str(e))


def _fallback_response(message: str, error: str) -> dict:
    """Fallback response when agents fail."""
    logger.warning(f"Using fallback response due to error: {error}")

    try:
        client = get_llm_client()
        response = client.chat_completion(
            messages=[{"role": "user", "content": message}],
            system_prompt=(
                "You are a friendly customer support agent for ShopEase, an e-commerce company. "
                "Help the customer with their query. Be professional and helpful."
            ),
        )
        return {
            "response": response,
            "agent_used": "Fallback Agent",
            "tools_used": [],
            "intent": "fallback",
            "sentiment_score": 0.0,
        }
    except Exception:
        return {
            "response": (
                "I apologize, but I'm experiencing technical difficulties. "
                "Please try again, or contact support@shopease.com for help."
            ),
            "agent_used": "System",
            "tools_used": [],
            "intent": "error",
            "sentiment_score": 0.0,
        }
