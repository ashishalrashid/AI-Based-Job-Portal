<template>
  <div class="control-bar" role="group" aria-label="Interview controls">
    <div class="control-group left">
      <button
        class="control-btn"
        :class="{ active: micEnabled }"
        @click="$emit('toggleMic')"
        :aria-label="micEnabled ? 'Mute microphone' : 'Unmute microphone'"
        title="Toggle Microphone"
      >
        <svg v-if="micEnabled" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
          <line x1="11" y1="11" x2="22" y2="22"/>
          <path d="M9 9v3a3 3 0 0 0 5.12 2.12"/>
        </svg>
      </button>

      <button
        class="control-btn"
        :class="{ active: videoEnabled }"
        @click="$emit('toggleVideo')"
        :aria-label="videoEnabled ? 'Stop video' : 'Start video'"
        title="Toggle Video"
      >
        <svg v-if="videoEnabled" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <polygon points="23 7 16 12 23 17 23 7"/>
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>
      </button>
    </div>

    <div class="control-group center">
      <button
        v-if="!isRecording"
        class="control-btn btn-speak"
        @click="$emit('startSpeaking')"
        :disabled="aiSpeaking || isProcessing"
        aria-label="Start speaking your answer"
      >
        Start Speaking
      </button>
      <button
        v-else
        class="control-btn btn-stop"
        @click="$emit('stopSpeaking')"
        :disabled="isProcessing || waitingForFinal"
        aria-label="Finish your answer"
      >
        Finish Answer
      </button>
    </div>

    <div class="control-group right">
      <button
        class="control-btn end-call-btn"
        @click="$emit('endInterview')"
        :disabled="isProcessing"
        :class="{ 'btn-disabled': isProcessing }"
        aria-label="End interview"
      >
        {{ isProcessing ? 'Finishing...' : 'End Interview' }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  micEnabled: Boolean,
  videoEnabled: Boolean,
  isRecording: Boolean,
  isProcessing: Boolean,
  aiSpeaking: Boolean,
  waitingForFinal: Boolean
})
defineEmits(['toggleMic', 'toggleVideo', 'startSpeaking', 'stopSpeaking', 'endInterview'])
</script>

<style scoped>
.control-bar {
  display: flex;
  justify-content: space-between;
  background: white;
  padding: 1rem 1.5rem;
  box-shadow: 0 -1px 6px rgb(0 0 0 / 0.1);
  border-top: 1px solid #e5e7eb;
}
.control-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.control-btn {
  cursor: pointer;
  border: none;
  background: none;
  font-weight: 600;
  padding: 0.5rem 1.2rem;
  border-radius: 8px;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}
.control-btn svg {
  width: 24px;
  height: 24px;
}
.control-btn.active {
  background-color: #4f46e5;
  color: white;
}
.control-btn:hover:not(:disabled) {
  background-color: #4338ca;
  color: white;
}
.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-speak {
  background-color: #2563eb;
  color: white;
  padding: 0.65rem 1.6rem;
}
.btn-stop {
  background-color: #dc2626;
  color: white;
  padding: 0.65rem 1.6rem;
}
.end-call-btn {
  background-color: #b91c1c;
  color: white;
  padding: 0.65rem 1.6rem;
}
.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none; /* Extra safety to prevent clicks */
}
</style>

