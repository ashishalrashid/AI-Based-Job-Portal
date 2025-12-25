<template>
  <div class="conversation-history" ref="scrollContainer">
    <!-- Past Q&A Messages -->
    <div
      v-for="(item, index) in conversationHistory"
      :key="index"
      class="message"
      :class="item.type"
    >
      <div class="message-header">
        <span class="sender">
          {{ item.type === 'question' ? '🤖 AI Interviewer' : '👤 You' }}
        </span>
        <span v-if="item.questionNumber" class="question-badge">
          Q{{ item.questionNumber }}
        </span>
      </div>
      <p class="message-text">{{ item.text }}</p>
      <span class="message-time">{{ formatTime(item.timestamp) }}</span>
    </div>

    <!-- Empty state -->
    <div v-if="conversationHistory.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <p>Your interview conversation will appear here</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  conversationHistory: {
    type: Array,
    default: () => []
  }
})

const scrollContainer = ref(null)

// Auto-scroll to bottom when new messages arrive
watch(() => props.conversationHistory.length, async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}, { flush: 'post' })

// Format time helper
function formatTime(date) {
  if (!date) return ''
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.conversation-history {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f9fafb;
}

.message {
  background: #fff;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.question {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-left: 4px solid #667eea;
}

.message.answer {
  background: #f0fdf4;
  border-left: 4px solid #22c55e;
  margin-left: 12px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.sender {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
}

.question-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #667eea;
  background: #667eea15;
  padding: 2px 8px;
  border-radius: 8px;
}

.message-text {
  margin: 0;
  color: #1e293b;
  line-height: 1.6;
  font-size: 0.95rem;
}

.message-time {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.5rem;
  display: block;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #94a3b8;
  text-align: center;
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

/* Scrollbar styling */
.conversation-history::-webkit-scrollbar {
  width: 6px;
}

.conversation-history::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-history::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

.conversation-history::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>

