from typing import Optional, Literal

class AgentExecutionException(Exception):
    """
    Exception raised when an agent fails to execute properly.
    
    Attributes:
        agent_type -- the type of agent that failed
        purpose -- the purpose the agent was trying to fulfill
        message -- explanation of the error
    """
    
    def __init__(
        self, 
        agent_type: Literal["main", "metadata_extractor", "searcher"], 
        purpose: Optional[str] = None, 
        message: Optional[str] = None
    ):
        self.agent_type = agent_type
        self.purpose = purpose
        self.message = message or f"🚫 [Agent Execution Error]: Failed to execute {agent_type}"
        
        if purpose:
            self.message += f" with purpose: {purpose}"
        
        super().__init__(self.message)
