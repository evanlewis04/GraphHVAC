CREATE TABLE IF NOT EXISTS trace_steps (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id     TEXT    NOT NULL,
    iteration    INTEGER NOT NULL,
    kind         TEXT    NOT NULL,  -- 'model_call' | 'tool_call' | 'tool_result' | 'final_answer'
    payload_json TEXT    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trace_steps_trace_id
    ON trace_steps(trace_id, iteration);
