from ApiClient import log_interaction
from Extensions import Extensions
import logging
import os


class voice_chat(Extensions):
    def __init__(self, **kwargs):
        self.ApiClient = kwargs["ApiClient"] if "ApiClient" in kwargs else None
        if "agent_name" in kwargs:
            self.agent_name = kwargs["agent_name"]
        else:
            self.agent_name = "gpt4free"
        self.voice_prompt = "Custom Input"
        self.tts_command = "Speak with TTS with Streamlabs Text to Speech"
        if "USE_STREAMLABS_TTS" in kwargs:
            if isinstance(kwargs["USE_STREAMLABS_TTS"], bool):
                if kwargs["USE_STREAMLABS_TTS"]:
                    self.tts_command = "Speak with TTS with Streamlabs Text to Speech"
            else:
                if kwargs["USE_STREAMLABS_TTS"].lower() == "true":
                    self.tts_command = "Speak with TTS with Streamlabs Text to Speech"
        if "USE_GTTS" in kwargs:
            if isinstance(kwargs["USE_GTTS"], bool):
                if kwargs["USE_GTTS"]:
                    self.tts_command = "Speak with GTTS"
            else:
                if kwargs["USE_GTTS"].lower() == "true":
                    self.tts_command = "Speak with GTTS"
        if "USE_HUGGINGFACE_TTS" in kwargs:
            if isinstance(kwargs["USE_HUGGINGFACE_TTS"], bool):
                if kwargs["USE_HUGGINGFACE_TTS"] and "HUGGINGFACE_API_KEY" in kwargs:
                    if kwargs["ELEVENLABS_API_KEY"] != "":
                        self.tts_command = "Read Audio with Huggingface"
            else:
                if (
                    kwargs["USE_HUGGINGFACE_TTS"].lower() == "true"
                    and "HUGGINGFACE_API_KEY" in kwargs
                ):
                    if kwargs["HUGGINGFACE_API_KEY"] != "":
                        self.tts_command = "Read Audio with Huggingface"
        if "ELEVENLABS_API_KEY" in kwargs:
            if kwargs["ELEVENLABS_API_KEY"] != "":
                self.tts_command = "Speak with TTS Using Elevenlabs"
        self.commands = {
            "Chat with Voice": self.chat_with_voice,
        }
        self.conversation_name = f"Voice Chat with {self.agent_name}"
        if "conversation_name" in kwargs:
            self.conversation_name = kwargs["conversation_name"]

    async def chat_with_voice(
        self,
        base64_audio,
        conversation_results=3,
        context_results=10,
    ):
        # Convert from M4A to WAV
        filename = "recording.wav"
        user_audio_path = self.ApiClient.execute_command(
            agent_name=self.agent_name,
            command_name="Convert M4A to WAV",
            command_args={
                "base64_audio": base64_audio,
                "filename": filename,
            },
        )
        # Get content of audio file.
        with open(user_audio_path, "rb") as f:
            user_audio = f.read()
        # Transcribe the audio to text.
        user_input = self.ApiClient.execute_command(
            agent_name=self.agent_name,
            command_name="Transcribe Audio from File",
            command_args={
                "filename": filename,
            },
        )
        user_message = f"{user_input}\n#GENERATED_AUDIO:{user_audio}"
        log_interaction(
            agent_name=self.agent_name,
            conversation_name=self.conversation_name,
            role="USER",
            message=user_message,
            user="USER",
        )
        logging.info(f"[Whisper]: Transcribed User Input: {user_input}")
        # Send the transcribed text to the agent.
        text_response = self.ApiClient.prompt_agent(
            agent_name=self.agent_name,
            prompt_name=self.voice_prompt,
            prompt_args={
                "user_input": user_input,
                "context_results": context_results,
            },
        )
        logging.info(f"[Whisper]: Text Response from LLM: {text_response}")
        # Get the audio response from the TTS engine and return it.
        audio_response = self.ApiClient.execute_command(
            agent_name=self.agent_name,
            command_name=self.tts_command,
            command_args={"text": text_response},
        )
        log_interaction(
            agent_name=self.agent_name,
            conversation_name=self.conversation_name,
            role=self.agent_name,
            message=audio_response,
            user="USER",
        )
        logging.info(f"[Whisper]: Audio Response from TTS: {audio_response}")
        return f"{audio_response}"
