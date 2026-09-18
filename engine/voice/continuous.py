from __future__ import annotations


class JelonVoiceRuntime:
    """Always-running local voice runtime: wake -> local STT -> agent -> TTS."""

    def __init__(self, wake_listener, command_capture, agent, tts=None, on_event=None):
        self.wake_listener = wake_listener
        self.command_capture = command_capture
        self.agent = agent
        self.tts = tts
        self.on_event = on_event or (lambda event: None)

    def handle_wake(self):
        self.on_event({"type": "wake", "phrase": "jelon"})
        command = self.command_capture().strip()
        if not command:
            self.on_event({"type": "empty_command"})
            return None
        self.on_event({"type": "command", "text": command})
        result = self.agent.run(command)
        response = getattr(result, "summary", str(result))
        if self.tts is not None:
            self.tts.speak(response)
        self.on_event({"type": "completed", "response": response})
        return result

    def run(self):
        self.wake_listener.on_wake = self.handle_wake
        self.wake_listener.run_forever()

    def stop(self):
        self.wake_listener.stop()
