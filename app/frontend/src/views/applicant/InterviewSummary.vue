<template>
  <div class="summary-container">
    <div class="summary-card">
      <div class="icon-wrapper">
        <span class="icon">🎉</span>
      </div>

      <h1>Thank You, <span class="highlight">{{ candidateName }}</span>!</h1>

      <p class="message">
        Your interview has been submitted successfully.<br>
        We have received your responses and will get back to you shortly.
      </p>

      <div class="redirect-box">
        <p>Redirecting to Interview Slots in <strong>{{ countdown }}</strong> seconds...</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: (countdown / 5) * 100 + '%' }"></div>
        </div>
      </div>

      <button @click="redirectNow" class="btn-primary">
        Go to Slots Now
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const countdown = ref(5)
let timer = null

// Get candidate name from URL query or default
const candidateName = route.query.name || 'Candidate'

const redirectNow = () => {
  // Redirect to the slots page as requested
  router.push('/applicant/interview-slots')
}

onMounted(() => {
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      redirectNow()
    }
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.summary-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 1rem;
}

.summary-card {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  text-align: center;
  max-width: 500px;
  width: 100%;
  animation: slideUp 0.5s ease-out;
}

.icon-wrapper {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

h1 {
  color: #1e3a5f;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.highlight {
  color: #6366f1;
}

.message {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.redirect-box {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  color: #475569;
  font-size: 0.9rem;
}

.progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin-top: 0.75rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #6366f1;
  transition: width 1s linear;
}

.btn-primary {
  background: #6366f1;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes popIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}
</style>
