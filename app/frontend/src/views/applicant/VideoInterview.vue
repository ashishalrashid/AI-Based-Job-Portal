<template>
  <div class="video-interview-page">
    <JoinScreen
      v-if="interviewStatus === 'waiting'"
      :interviewData="interviewData"
      @joined="handleJoined"
    />
    <InterviewScreen
      v-else-if="interviewStatus === 'active'"
      :sessionId="sessionId"
      :interviewData="interviewData"
      @endInterview="handleEndInterview"
    />
    <div v-else class="completion-screen">
      <h2>Thank you for your time!</h2>
      <p>Your interview is complete.</p>
    </div>
    <ToastNotification :toasts="toasts" @removeToast="removeToast" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'  // ← ADD THIS IMPORT
import JoinScreen from '@/components/JoinScreen.vue'
import InterviewScreen from '@/components/InterviewScreen.vue'
import ToastNotification from '@/components/ToastNotification.vue'

const route = useRoute()  // ← ADD THIS LINE
const interviewStatus = ref('waiting')
const sessionId = ref(null)

// ✅ FIXED: Add interview ID from route
const interviewData = ref({
  id: parseInt(route.params.id),  // ← ADD THIS LINE
  title: 'AI Video Interview',
  company: 'TechCorp',
  position: 'Software Engineer'
})

const toasts = ref([])

function handleJoined(session) {
  sessionId.value = session
  interviewStatus.value = 'active'
  showToast('Interview started successfully!', 'success')
}

function handleEndInterview() {
  interviewStatus.value = 'completed'
  showToast('Interview ended. Thank you!', 'info')
}

let toastId = 0
function showToast(message, type = 'info', duration = 3000) {
  const id = ++toastId
  toasts.value.push({ id, message, type, icon: type })
  setTimeout(() => removeToast(id), duration)
}

function removeToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}
</script>

<style scoped>
.video-interview-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

.completion-screen {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex: 1;
  font-size: 1.25rem;
  color: #374151;
  text-align: center;
  padding: 2rem;
}
</style>

