"""
Transcription Service - Handles Azure Speech streaming transcription
"""
import logging
import time
import threading
from typing import Dict, Optional
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class StreamingRecognizer:
    """Manages streaming speech recognition for a single session with Azure Speech SDK"""
    
    def __init__(self, session_id: str, speech_config, socketio, room: Optional[str] = None):
        self.session_id = session_id
        self.speech_config = speech_config
        self.socketio = socketio
        self.room = room
        
        # Transcript accumulation
        self.transcript_parts = []
        self.interim_text = ""
        
        # State management
        self.running = False
        self.last_active = time.time()
        self.lock = threading.Lock()
        
        # Azure Speech SDK components
        self.push_stream = None
        self.audio_config = None
        self.speech_recognizer = None
        
    def start(self):
        """Initialize and start Azure Speech recognition"""
        try:
            logger.info(f"🎤 Starting Azure Speech recognizer for session {self.session_id}")
            
            # Create push stream for audio input
            stream_format = speechsdk.audio.AudioStreamFormat(
                samples_per_second=16000,
                bits_per_sample=16,
                channels=1
            )
            self.push_stream = speechsdk.audio.PushAudioInputStream(stream_format)
            
            # Create audio config from push stream
            self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)
            
            # Create speech recognizer
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )
            
            # Connect event handlers
            self.speech_recognizer.recognizing.connect(self._on_recognizing)
            self.speech_recognizer.recognized.connect(self._on_recognized)
            self.speech_recognizer.canceled.connect(self._on_canceled)
            self.speech_recognizer.session_stopped.connect(self._on_session_stopped)
            
            # Start continuous recognition
            self.speech_recognizer.start_continuous_recognition_async().get()
            
            self.running = True
            logger.info(f"✅ Azure Speech recognizer started for {self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start recognizer: {e}", exc_info=True)
            self.running = False
            raise
    
    def _on_recognizing(self, evt):
        """Handle interim recognition results"""
        with self.lock:
            self.interim_text = evt.result.text
            self.last_active = time.time()
        
        # Emit interim transcript to frontend
        if self.socketio and self.room:
            self.socketio.emit('transcription_interim', {
                'session_id': self.session_id,
                'text': evt.result.text,
                'is_final': False
            }, room=self.room)
        
        logger.debug(f"🗣️ Recognizing: {evt.result.text[:50]}...")
    
    def _on_recognized(self, evt):
        """Handle final recognition results"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            with self.lock:
                if evt.result.text:
                    self.transcript_parts.append(evt.result.text)
                    self.interim_text = ""
                    self.last_active = time.time()
            
            # Emit final transcript to frontend
            if self.socketio and self.room:
                self.socketio.emit('transcription_final', {
                    'session_id': self.session_id,
                    'text': evt.result.text,
                    'is_final': True
                }, room=self.room)
            
            logger.info(f"✅ Recognized: {evt.result.text}")
        
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            logger.debug(f"No speech recognized: {evt.result.no_match_details}")
    
    def _on_canceled(self, evt):
        """Handle recognition cancellation"""
        logger.warning(f"Recognition canceled: {evt.cancellation_details.reason}")
        
        if evt.cancellation_details.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {evt.cancellation_details.error_details}")
    
    def _on_session_stopped(self, evt):
        """Handle session stop"""
        logger.info(f"Recognition session stopped for {self.session_id}")
        self.running = False
    
    def push_audio(self, audio_bytes: bytes):
        """Push audio chunk to Azure Speech recognizer"""
        with self.lock:
            if not self.running:
                raise RuntimeError("Recognizer not started")
            
            try:
                if self.push_stream:
                    self.push_stream.write(audio_bytes)
                    self.last_active = time.time()
            except Exception as e:
                logger.error(f"Error pushing audio: {e}")
                raise
    
    def get_transcript(self) -> str:
        """Return current transcript as string"""
        with self.lock:
            full_text = " ".join(self.transcript_parts)
            if self.interim_text:
                full_text += " " + self.interim_text
            return full_text.strip()
    
    def stop(self):
        """Stop recognition and cleanup resources"""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            
            try:
                if self.speech_recognizer:
                    self.speech_recognizer.stop_continuous_recognition_async().get()
                    logger.info(f"🛑 Recognition stopped for {self.session_id}")
                
                if self.push_stream:
                    self.push_stream.close()
                    
            except Exception as e:
                logger.error(f"Error stopping recognizer: {e}")


class TranscriptionService:
    """Handles Azure Speech streaming transcription with concurrency and cleanup"""
    
    def __init__(self):
        from ..config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
        
        self.initialized = False
        self.active_streams: Dict[str, StreamingRecognizer] = {}
        self.lock = threading.Lock()
        self.last_active: Dict[str, float] = {}
        
        if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
            logger.warning("⚠️ Azure Speech credentials not configured")
            return
        
        try:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY,
                region=AZURE_SPEECH_REGION
            )
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.output_format = speechsdk.OutputFormat.Detailed
            
            self.initialized = True
            logger.info("✅ Azure Speech Streaming initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize transcription: {e}")
            self.initialized = False
    
    def start_streaming(self, session_id: str, socketio, room: Optional[str] = None) -> bool:
        """Start streaming recognition for a session"""
        with self.lock:
            if not self.initialized:
                logger.warning("Service not initialized")
                return False
            
            if session_id in self.active_streams:
                logger.warning(f"Stream already active for {session_id}")
                return False
            
            try:
                recognizer = StreamingRecognizer(
                    session_id, self.speech_config, socketio, room
                )
                recognizer.start()
                
                self.active_streams[session_id] = recognizer
                self.last_active[session_id] = time.time()
                
                logger.info(f"✅ Started streaming for {session_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start streaming: {e}")
                return False
    
    def push_audio_chunk(self, session_id: str, audio_bytes: bytes) -> bool:
        """Push audio chunk to active recognizer"""
        with self.lock:
            recognizer = self.active_streams.get(session_id)
            
            if not recognizer:
                logger.warning(f"No active stream for {session_id}")
                return False
            
            try:
                recognizer.push_audio(audio_bytes)
                self.last_active[session_id] = time.time()
                return True
                
            except Exception as e:
                logger.error(f"Error pushing audio for {session_id}: {e}")
                return False
    
    def stop_streaming(self, session_id: str) -> str:
        """Stop streaming and return final transcript"""
        with self.lock:
            recognizer = self.active_streams.pop(session_id, None)
            self.last_active.pop(session_id, None)
            
            if not recognizer:
                logger.warning(f"Tried to stop non-existing stream for {session_id}")
                return ""
            
            try:
                transcript = recognizer.get_transcript()
                recognizer.stop()
                
                logger.info(f"🛑 Stopped streaming for {session_id}")
                return transcript
                
            except Exception as e:
                logger.error(f"Error stopping stream {session_id}: {e}")
                return ""
    
    def cleanup_inactive_streams(self, max_idle_seconds: int = 300) -> int:
        """Cleanup streams idle for more than max_idle_seconds"""
        now = time.time()
        to_remove = []
        
        with self.lock:
            for session_id, last_active in list(self.last_active.items()):
                idle_time = now - last_active
                if idle_time > max_idle_seconds:
                    to_remove.append(session_id)
        
        for session_id in to_remove:
            try:
                self.stop_streaming(session_id)
                logger.info(f"🧹 Cleaned inactive stream: {session_id}")
            except Exception as e:
                logger.error(f"Error cleaning stream {session_id}: {e}")
        
        if to_remove:
            logger.info(f"🧹 Cleaned {len(to_remove)} inactive transcription streams")
        
        return len(to_remove)


# Singleton instance
_transcription_service = None

def get_transcription_service() -> TranscriptionService:
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service

