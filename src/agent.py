"""OpenAI function-calling agent with database tools and retry logic."""

import json
from openai import OpenAI

from src.data_manager import DataManager
from src.prompts import build_system_prompt

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute a read-only SQL SELECT query against the SQLite database and return results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A valid SQLite SELECT query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schema",
            "description": "Get the database schema including table names, column names, types, and sample data.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sample_data",
            "description": "Preview the first N rows of a table to understand actual data values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table (clients, invoices, or invoice_line_items).",
                    },
                    "n": {
                        "type": "integer",
                        "description": "Number of rows to preview (default 3).",
                        "default": 3,
                    },
                },
                "required": ["table_name"],
            },
        },
    },
]

MAX_ITERATIONS = 8


class Agent:
    """OpenAI function-calling agent that queries a database to answer questions."""

    def __init__(self, data_manager: DataManager, model: str = "gpt-5.1", api_key: str | None = None):
        self.dm = data_manager
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.system_prompt = build_system_prompt(data_manager.get_schema())

    def _handle_tool_call(self, tool_call) -> tuple[str, dict | None]:
        """Execute a tool call, return (result_str, metadata_or_none)."""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if name == "execute_sql":
            result = self.dm.execute_query(args["query"])
            return json.dumps(result, default=str), {
                "type": "sql",
                "query": args["query"],
                "result": result,
            }
        elif name == "get_schema":
            return self.dm.get_schema(), None
        elif name == "sample_data":
            result = self.dm.get_sample_data(args["table_name"], args.get("n", 3))
            return json.dumps(result, default=str), None
        else:
            return json.dumps({"error": f"Unknown tool: {name}"}), None

    def run(self, messages: list[dict]) -> dict:
        """Run the agent loop. Returns {answer, sql_queries, data_tables}."""
        agent_messages = [{"role": "system", "content": self.system_prompt}] + messages
        sql_queries: list[str] = []
        data_tables: list[dict] = []

        for _ in range(MAX_ITERATIONS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=agent_messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                return {
                    "answer": msg.content or "",
                    "sql_queries": sql_queries,
                    "data_tables": data_tables,
                }

            # Append the assistant message with tool calls
            agent_messages.append(msg)

            # Process each tool call
            for tc in msg.tool_calls:
                result_str, meta = self._handle_tool_call(tc)
                agent_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })
                if meta and meta["type"] == "sql":
                    sql_queries.append(meta["query"])
                    result = meta["result"]
                    if "columns" in result and "rows" in result:
                        data_tables.append(result)

        # If we hit max iterations, return whatever we have
        return {
            "answer": "I was unable to fully answer the question within the allowed number of steps. Here is what I found so far.",
            "sql_queries": sql_queries,
            "data_tables": data_tables,
        }
