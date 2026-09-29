# GLM through the Coding Plan, with JSON mode and Pydantic validation

The coach calls GLM (GLM-5.3 for answers and interviews, GLM-5.3-Flash for graders, the simulated candidate and question generation) through the owner's GLM Coding Plan on its OpenAI-compatible coding endpoint, using LangChain's `ChatOpenAI`. GLM only accepts `tool_choice: auto` and has no `json_schema` response format, so LangChain's default structured output (and `create_agent(response_format=...)`) fails against it; structured output therefore uses JSON mode or unforced tool calls, validated with Pydantic and retried once with the validation error. The model sits behind one small factory function so moving to a pay-per-token key or a local model is a configuration change.

## Consequences

- The plan's usage policy limits it to officially supported tools; the owner accepted that risk for a learning project that does not run all the time.
- Plan quota is shared with other coding tools on the same account, so evaluation runs must read quota errors and stop rather than retry.
