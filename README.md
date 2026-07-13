# Velora AI - Local Hierarchical Multi-Agent System

Velora AI is a fully local, stateful, hierarchical multi-agent research system built on LangGraph 1.x and Ollama. The system operates without any external API keys or internet dependencies, enabling private and reproducible agentic workflows.

## System Architecture

The architecture follows a **hierarchical supervisor pattern**, where a central Supervisor agent orchestrates task execution by routing between specialized agents. All decision-making logic is centralized in the Supervisor, while subordinate agents execute specific tasks and return results to the supervisor for further routing.
User Query
↓
Supervisor (Decision Router)
↓
Researcher (Tool-augmented)
↓
Supervisor (Evaluation & Routing)
↓
[Writer / Critic] (Planned)
↓
Final Structured Output
text## Agent Design

### Supervisor Agent
- Acts as the single source of truth for workflow control.
- Analyzes current state and determines the next agent to invoke.
- Maintains global task context and enforces execution flow.
- Decision space is restricted to: `researcher`, `writer`, `critic`, `done`.

### Researcher Agent
- Responsible for information retrieval using external tools.
- Implements tool calling via `langchain_community` tools.
- Currently integrated with `WikipediaQueryRun` and `ArxivQueryRun`.
- Returns structured findings to the shared state under `research_findings`.

> Writer and Critic agents are defined in the architecture but remain unimplemented as of Phase 1.

## State Management

The system utilizes LangGraph’s `StateGraph` with a custom `AgentState` TypedDict for persistent context across agent executions.

```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_task: str
    research_findings: str
    draft_report: str
    critic_feedback: str
    final_report: str
    status: Literal["research", "write", "critic", "done"]
    next_agent: str
Key design decisions:

messages field accumulates reasoning traces and tool outputs.
status and next_agent fields enable explicit control flow from the Supervisor.
State is checkpointed using langgraph-checkpoint-sqlite for durability.

LangGraph Implementation
The workflow is modeled as a directed graph with conditional routing:

Entry Point: Supervisor node
Conditional Edges: Supervisor evaluates state and routes to appropriate agent
Cycle Pattern: Researcher → Supervisor loop until sufficient information is gathered
Termination: Supervisor emits done status

This design enables dynamic, state-dependent execution paths without hardcoded linear pipelines.
Tool Integration
Researcher agent utilizes the following tools:

WikipediaQueryRun — General knowledge retrieval
ArxivQueryRun — Academic and scientific literature search

Tools are bound to the LLM via bind_tools() and invoked through LangGraph’s ToolNode pattern. Tool outputs are parsed and injected back into the shared state.
LLM Integration
The system is designed around Ollama as the inference backend. The default model is qwen2.5:7b, selected for its strong tool-calling performance and reasoning capabilities within constrained hardware environments.
Model abstraction is handled through langchain_ollama.ChatOllama, allowing model swapping with minimal code changes.
Routing Logic
Routing decisions are made exclusively by the Supervisor agent through LLM-based classification. The prompt is engineered to constrain outputs to a predefined action space, reducing hallucinated routing decisions.
Current routing logic supports:

Information gathering loop (Researcher)
Future support for writing and critique loops

Current Limitations

Writer and Critic agents are not yet implemented.
Tool output quality is dependent on the underlying LLM’s summarization capability.
No self-correction or multi-turn reflection loop exists in Phase 1.
Long-context research tasks may hit model context window limitations.

Future Improvements

Implementation of Writer and Critic agents with structured output validation
Introduction of self-correction and retry mechanisms
Enhanced tool set including document parsing and structured data extraction
Persistent memory layer across sessions
Streaming support for real-time agent interaction

Technical Highlights

Fully local execution with zero external dependencies
Explicit state management via TypedDict and LangGraph checkpoints
Centralized control flow through Supervisor pattern
Tool-augmented reasoning with native LangChain integration
Modular agent and graph design for extensibility
