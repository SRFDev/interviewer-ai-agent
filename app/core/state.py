from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class InterviewState(TypedDict):
    """
    The memory state of the System Design Interviewer agent.
    """
    # Chat History: Appends new messages to the list
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Context: Tracks where we are in the interview
    candidate_level: str  # e.g., "Junior", "Senior", "Staff"
    current_topic: str    # e.g., "Load Balancing", "Database Sharding"
    interview_stage: str  # "intro", "questioning", "feedback", "end"
    
    # Assessment: Tracks performance
    feedback_log: List[str] # Running list of critiques
    question_count: int     # To limit the interview length

    # Internal Thought Process (The "Scratchpad")
    # This guides the generator on how to respond
    critique: str       # e.g., "User missed the trade-off on latency."
    decision: str       # "PASS", "FAIL", "PROBE"
    
    # Metrics
    question_count: int
    