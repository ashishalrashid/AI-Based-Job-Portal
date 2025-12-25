<template>
  <div class="join-screen">
    <div class="card">
      <h2>AI Video Interview</h2>
      <p class="position-title">{{ interviewData.position }}</p>
      <div class="details">
        <p><strong>Company:</strong> {{ interviewData.company }}</p>
        <p><strong>Position:</strong> {{ interviewData.position }}</p>
      </div>
      <h3>Before you start</h3>
      <ul>
        <li>Ensure your camera and microphone are working</li>
        <li>Find a quiet, well-lit location</li>
        <li>The AI will ask adaptive questions based on your answers</li>
        <li>Speak clearly - your speech will be converted to text automatically</li>
        <li>Your interview will be recorded for review</li>
      </ul>
      <button class="btn-join" @click="joinInterview">Join Interview Room</button>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'
import api from '@/services/api'

const props = defineProps({
  interviewData: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['joined'])

async function joinInterview() {
  try {
    const interviewId = props.interviewData.id
    if (!interviewId) {
      alert('Interview ID is missing!')
      return
    }

    console.log('🔍 Starting interview for ID:', interviewId)

    const payload = {
      job_title: props.interviewData.position,
      job_description: props.interviewData.position,
      candidate_background: {}, // backend already builds rich background
    }

    // Call the existing video-interview route:
    // @interview_routes_bp.route('/start/<int:interview_id>', methods=['POST'])
    const response = await api.post(`/video-interview/start/${interviewId}`, payload)

    console.log('✅ Interview started:', response.data)

    const session =
      response.data.session_id ||
      response.data.sessionId ||
      response.data.sessionid

    if (!session) {
      alert('No session ID returned from server')
      return
    }

    emit('joined', session)
  } catch (err) {
    console.error('❌ Failed to start interview:', err)
    alert('Failed to start interview: ' + (err.response?.data?.error || err.message))
  }
}
</script>

<style scoped>
.join-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f4f8;
  padding: 1rem;
}
.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 8px 24px rgb(0 0 0 / 0.1);
  text-align: center;
}
.position-title {
  font-weight: 600;
  color: #4f46e5;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
}
.details p {
  margin: 0.3rem 0;
  font-size: 1rem;
  color: #555;
}
ul {
  text-align: left;
  margin: 1.5rem 0;
  padding-left: 1.2rem;
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}
.btn-join {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
}
.btn-join:hover {
  background-color: #4338ca;
}
</style>

