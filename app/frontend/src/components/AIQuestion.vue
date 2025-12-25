<template>
  <div class="ai-question" :class="{ speaking: isSpeaking }" role="region" aria-live="polite" aria-atomic="true">
    <h3>{{ question || 'Waiting for next question...' }}</h3>
    <p v-if="isSpeaking" class="speaking-indicator">
      <span class="dot" aria-hidden="true"></span> AI is speaking...
    </p>
  </div>
</template>

<script setup>
const props = defineProps({
  question: String,
  isSpeaking: Boolean
})
</script>

<style scoped>
.ai-question {
  background: #eef2ff;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  font-size: 1.1rem;
  color: #3730a3;
  min-height: 72px;
  transition: background-color 0.3s ease;
}

.ai-question.speaking {
  background: #c7d2fe;
}

.speaking-indicator {
  margin-top: 0.5rem;
  font-style: italic;
  color: #4f46e5;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dot {
  width: 0.8rem;
  height: 0.8rem;
  background: #4f46e5;
  border-radius: 50%;
  animation: pulse 1.2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>

