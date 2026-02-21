import time
import asyncio
from telegram import constants
from telegram.error import BadRequest

class TelegramRenderer:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = None
        self.buffer = []  # List of dicts: {'type': str, 'content': Any}
        self.last_update_time = 0
        self.update_interval = 2.0  # seconds
        self.is_finished = False

    async def start(self):
        """Send the initial 'Thinking...' message."""
        try:
            msg = await self.bot.send_message(
                chat_id=self.chat_id,
                text="Thinking...",
                parse_mode=constants.ParseMode.MARKDOWN
            )
            self.message_id = msg.message_id
        except Exception as e:
            print(f"Error starting renderer: {e}")

    async def update(self, status_type, content):
        """
        Update the renderer state.
        status_type: "thinking", "tool_use", "observation", "final_stream", "final"
        """
        if status_type == "final_stream":
            # Append to the last final_stream block if exists
            if not self.buffer or self.buffer[-1]['type'] != 'final_stream':
                self.buffer.append({'type': 'final_stream', 'content': content})
            else:
                self.buffer[-1]['content'] += content

        elif status_type == "final":
             # Replace the last stream block with the full final content if needed
             # or just mark finished
             if self.buffer and self.buffer[-1]['type'] == 'final_stream':
                 self.buffer[-1]['content'] = content # Overwrite with full content
             else:
                 self.buffer.append({'type': 'final_stream', 'content': content})
             self.is_finished = True
             await self.render(force=True)

        elif status_type == "tool_use":
            self.buffer.append({'type': 'tool_use', 'content': content})
            await self.render()

        elif status_type == "observation":
            # Find the last tool_use and attach result?
            # Or just append observation
            self.buffer.append({'type': 'observation', 'content': content})
            await self.render()

        elif status_type == "thinking":
            # Optional: Add thought log
            pass

        else:
            await self.render()

    async def render(self, force=False):
        """Render the current state to the Telegram message."""
        now = time.time()
        if not force and (now - self.last_update_time < self.update_interval):
            return

        text = self._format_text()
        if not text: return

        if not self.message_id:
            await self.start()
            if not self.message_id: return

        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=text,
                parse_mode=constants.ParseMode.MARKDOWN
            )
            self.last_update_time = now
        except BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            else:
                # If Markdown fails, retry without it or fallback
                try:
                    await self.bot.edit_message_text(
                        chat_id=self.chat_id,
                        message_id=self.message_id,
                        text=text # Retry plain
                    )
                except:
                    print(f"Failed to render message: {e}")
        except Exception as e:
            print(f"Render error: {e}")

    def _format_text(self):
        """Format the buffer into a CLI-style string."""
        display_text = ""

        # 1. Logs (Tools & Plans)
        logs = []
        for item in self.buffer:
            if item['type'] == 'tool_use':
                tool_name = item['content'].get('tool', 'Unknown')
                logs.append(f"🔧 Executing: {tool_name}...")
            elif item['type'] == 'observation':
                result = item['content'].replace("Tool '", "").replace("' output:", "") # Cleanup
                # Truncate
                if len(result) > 50: result = result[:50] + "..."
                logs.append(f"  ↳ Result: {result}")

        if logs:
            # Show last 8 lines
            visible_logs = logs[-8:]
            log_block = "\n".join(visible_logs)
            display_text += f"```\n{log_block}\n```\n"

        # 2. Main Content (Stream)
        # Find the final stream
        final_content = ""
        for item in self.buffer:
            if item['type'] == 'final_stream':
                final_content = item['content']

        if final_content:
            display_text += final_content
        else:
            if not logs:
                display_text = "Thinking..."

        # Truncate to Telegram limit (4096)
        if len(display_text) > 4000:
            display_text = display_text[:4000] + "..."

        return display_text
