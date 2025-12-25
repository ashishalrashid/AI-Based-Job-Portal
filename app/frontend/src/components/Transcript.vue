<template>
  <section class="transcript-section" role="log" aria-live="polite" aria-atomic="true">
    <h4>Your Response Live Transcript</h4>

    <div class="transcript-box" :class="{ active: isRecording }" aria-label="Live transcript of your answers">
      <p v-if="!finalTranscript && !interimTranscript && !isRecording" class="placeholder">
        Click Start Speaking to answer...
      </p>
      <p v-else-if="isRecording" class="listening-text">
        Recording... <span class="final-transcript">{{ finalTranscript }}</span><span class="interim-transcript">{{ interimTranscript }}</span>
      </p>
      <p v-else>{{ finalTranscript }}</p>
    </div>

    <div v-if="!isRecording" class="manual-input">
      <p class="hint">Or type your answer manually</p>
      <textarea
        v-model="manualAnswer"
        placeholder="Type your answer here..."
        :disabled="isRecording || aiSpeaking"
        aria-label="Type your answer manually"
        class="manual-textarea"
      ></textarea>
      <button
        class="btn-submit-manual"
        :disabled="!manualAnswer.trim() || aiSpeaking"
        @click="submitManualAnswer"
        aria-label="Submit typed answer"
      >
        Submit Answer
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  finalTranscript: { type: String, default: '' },
  interimTranscript: { type: String, default: '' },
  isRecording: { type: Boolean, default: false },
  aiSpeaking: { type: Boolean, default: false }
})

const manualAnswer = ref('')

const emit = defineEmits(['submitManualAnswer'])

function submitManualAnswer() {
  if (manualAnswer.value.trim()) {
    emit('submitManualAnswer', manualAnswer.value.trim())
    manualAnswer.value = ''
  }
}
</script>

<style scoped>
.transcript-section {
  background: white;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 4px rgb(0 0 0 / 0.1);
  max-height: 180px;
  overflow-y: auto;
}

.transcript-box {
  min-height: 72px;
  font-size: 1rem;
  color: #333;
  padding: 0.5rem 0;
}

.transcript-box.active {
  background: #f3f4f6;
}

.placeholder {
  color: #9ca3af;
  font-style: italic;
}

.listening-text {
  font-weight: 600;
}

.final-transcript {
  color: #1f2937;
}

.interim-transcript {
  color: #6b7280;
  font-style: italic;
  margin-left: 0.4rem;
}

.manual-input {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hint {
  font-size: 0.875rem;
  color: #6b7280;
}

.manual-textarea {
  width: 100%;
  min-height: 70px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 0.5rem;
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
}

.btn-submit-manual {
  align-self: flex-end;
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-submit-manual:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

.btn-submit-manual:hover:not(:disabled) {
  background: #4338ca;
}
</style>

