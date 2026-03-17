# Architecture
* Sync Django
    * /login, /logout, /admin - DONE
    * /chat/new
        * GET: loads the initial UI with submit form containing HTMX logic and JS client
        * POST: initial chat message + selected provider, returns snippet replacing the chat history with a pre-loaded
            initial user message + assistant message placeholder, triggers URL push to /chat/<chat ID>, triggers JS
            client to connect to SSE endpoint /api/chat/<chat ID> and listen for changes, delays background task which
            connects to LLM and sends the request
    * /chat/<chat ID>
        * GET: Loads the chat state from the database and pre-render the chat panel, feed JS client with last consumed
            fragment ID so it knows how to reconnect to stream
        * POST: same as POST to /chat/new, but append message content instead of replacing the entire chat window
* Async Django Bolt
    * /api/chat/<chat id>?seq_id=xxx
        * Read from appropriate Redis Stream with a potential given offset, and stream back the SSE events
* Procrastinate
    * When user message is sent, trigger a job
    * Job sends request to provider API, receives response chunks, publishes them to appropriate Redis Stream, every X
      chunks flushes the content to database saving partial message + last seq ID
