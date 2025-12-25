<template>
  <div class="meet-container">
    <!-- Main Meeting Area -->
    <div class="meeting-wrapper">
      <!-- Video Section (Full Width with floating participants) -->
      <div class="video-main">
        <!-- Presentation/Screen Area -->
        <div class="video-presentation">
          <div class="video-placeholder">
            <div class="placeholder-content">
              <div class="icon">📹</div>
              <p>Waiting for {{ interview?.candidate }}...</p>
              <span class="subtext">They'll appear here when they join</span>
            </div>
          </div>
        </div>

        <!-- Floating Participant Cards -->
        <div class="participants-floating">
          <div class="participant-card participant-self">
            <div class="participant-avatar">
              <span class="initials">YOU</span>
            </div>
            <div class="participant-info">
              <span class="participant-name">You (Interviewer)</span>
              <span class="participant-status" v-if="isCallActive">🎤</span>
            </div>
          </div>

          <div class="participant-card participant-remote" v-if="interview?.candidate">
            <div class="participant-avatar remote">
              <span class="initials">{{ getInitials(interview?.candidate) }}</span>
            </div>
            <div class="participant-info">
              <span class="participant-name">{{ interview?.candidate }}</span>
              <span class="participant-status" v-if="isCallActive">🎤</span>
            </div>
          </div>
        </div>

        <!-- Info Overlay (Top Left) -->
        <div class="info-overlay">
          <div class="meeting-title">{{ interview?.title }}</div>
          <div class="meeting-time">{{ getCurrentTime() }}</div>
        </div>

        <!-- Controls Bar (Bottom) -->
        <div class="controls-bar">
          <div class="controls-group">
            <!-- Mic -->
            <button
              class="control-btn"
              :class="{ 'btn-off': !isMicOn }"
              @click="toggleMic"
              title="Turn microphone on/off (Ctrl + M)"
            >
              <span v-if="isMicOn" class="icon">🎤</span>
              <span v-else class="icon strikethrough">🎤</span>
              <span class="label">Mic</span>
            </button>

            <!-- Camera -->
            <button
              class="control-btn"
              :class="{ 'btn-off': !isCameraOn }"
              @click="toggleCamera"
              title="Turn camera on/off (Ctrl + E)"
            >
              <span v-if="isCameraOn" class="icon">📷</span>
              <span v-else class="icon strikethrough">📷</span>
              <span class="label">Camera</span>
            </button>

            <!-- Screen Share -->
            <button
              class="control-btn"
              :class="{ 'btn-active': isScreenSharing }"
              @click="toggleScreenShare"
              title="Share your screen"
            >
              <span class="icon">🖥️</span>
              <span class="label">Present</span>
            </button>
          </div>

          <!-- Center Actions -->
          <div class="controls-group center">
            <!-- Start/End Call -->
            <button
              v-if="!isCallActive"
              class="control-btn btn-start-call"
              @click="startCall"
              title="Start the interview call"
            >
              <span class="icon">☎️</span>
              <span class="label">Start Call</span>
            </button>
            <button
              v-else
              class="control-btn btn-end-call"
              @click="endCall"
              title="End the interview call"
            >
              <span class="icon">📞</span>
              <span class="label">End Call</span>
            </button>
          </div>

          <!-- Right Actions -->
          <div class="controls-group">
            <!-- Chat -->
            <button class="control-btn" @click="toggleChat" title="Open chat">
              <span class="icon">💬</span>
              <span class="label">Chat</span>
            </button>

            <!-- More Options -->
            <button class="control-btn" @click="toggleMoreOptions" title="More options">
              <span class="icon">⋮</span>
            </button>

            <!-- Exit -->
            <button class="control-btn btn-exit" @click="goBack" title="Exit meeting">
              <span class="icon">✕</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Side Panel (Info & Actions) -->
      <div class="side-panel" v-if="showSidePanel">
        <div class="panel-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'info' }"
            @click="activeTab = 'info'"
          >
            Info
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'notes' }"
            @click="activeTab = 'notes'"
          >
            Notes
          </button>
        </div>

        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="tab-content">
          <div class="info-section">
            <h3 class="section-title">Interview Details</h3>
            <div class="detail-item">
              <span class="detail-label">Position:</span>
              <span class="detail-value">{{ interview?.title }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Candidate:</span>
              <span class="detail-value">{{ interview?.candidate }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Round:</span>
              <span class="detail-value">{{ interview?.round || 'Screening' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Scheduled:</span>
              <span class="detail-value"
                >{{ formatDate(interview?.date) }} at {{ interview?.time }}</span
              >
            </div>
            <div class="detail-item">
              <span class="detail-label">Duration:</span>
              <span class="detail-value">60 minutes</span>
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">Status</h3>
            <div class="status-badge" :class="{ 'status-active': isCallActive }">
              <span class="status-dot"></span>
              {{ isCallActive ? 'Call In Progress' : 'Waiting to Start' }}
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">Actions</h3>
            <div class="action-grid">
              <button class="action-btn approve" @click="handleApprove">
                <span class="icon">✓</span>
                <span>Approve</span>
              </button>
              <button class="action-btn reject" @click="handleReject">
                <span class="icon">✕</span>
                <span>Reject</span>
              </button>
              <button class="action-btn hold">
                <span class="icon">⏸</span>
                <span>Hold</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Notes Tab -->
        <div v-if="activeTab === 'notes'" class="tab-content">
          <div class="info-section">
            <h3 class="section-title">Interview Notes</h3>
            <textarea
              v-model="interviewNotes"
              class="notes-input"
              placeholder="Add your notes about the interview here..."
            ></textarea>
            <button class="btn-save-notes" @click="saveNotes">Save Notes</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const route = useRoute()
const store = useStore()

const interview = ref(null)
const interviewNotes = ref('')
const isCallActive = ref(false)
const isMicOn = ref(true)
const isCameraOn = ref(true)
const isScreenSharing = ref(false)
const showSidePanel = ref(true)
const activeTab = ref('info')
const currentTime = ref('')

// Get initials from name
const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString('en-US', options)
}

// Get current time
const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

// Toggle Mic
const toggleMic = () => {
  isMicOn.value = !isMicOn.value
  console.log('Microphone:', isMicOn.value ? 'On' : 'Off')
}

// Toggle Camera
const toggleCamera = () => {
  isCameraOn.value = !isCameraOn.value
  console.log('Camera:', isCameraOn.value ? 'On' : 'Off')
}

// Toggle Screen Share
const toggleScreenShare = () => {
  isScreenSharing.value = !isScreenSharing.value
  console.log('Screen Sharing:', isScreenSharing.value ? 'Started' : 'Stopped')
}

// Toggle Chat
const toggleChat = () => {
  console.log('Chat opened')
}

// Toggle More Options
const toggleMoreOptions = () => {
  console.log('More options menu')
}

// Start call
const startCall = () => {
  isCallActive.value = true
  isMicOn.value = true
  isCameraOn.value = true
  console.log('Call started with:', interview.value?.candidate)
}

// End call
const endCall = () => {
  isCallActive.value = false
  console.log('Call ended')
}

// Go back
const goBack = () => {
  router.back()
}

// Handle approve
const handleApprove = () => {
  console.log('Candidate approved')
  alert('Candidate marked as approved')
}

// Handle reject
const handleReject = () => {
  console.log('Candidate rejected')
  alert('Candidate marked as rejected')
}

// Save notes
const saveNotes = () => {
  console.log('Notes saved:', interviewNotes.value)
  alert('Notes saved successfully')
}

// Load interview data from route params or API
onMounted(async () => {
  const interviewData = route.params.interview
  const interviewId = route.params.interviewId

  if (interviewData) {
    try {
      interview.value =
        typeof interviewData === 'string' ? JSON.parse(interviewData) : interviewData
    } catch (e) {
      interview.value = interviewData
    }
  } else if (interviewId) {
    // Fetch interview from API
    try {
      const hrUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
      const hrId = hrUser?.hr_id
      if (hrId) {
        const res = await store.dispatch('hr/fetchInterviewCards', hrUser.company_id)
        const found = res.find(i => i.interview_id === parseInt(interviewId))
        if (found) {
          interview.value = {
            id: found.interview_id,
            title: found.title || `${found.stage || found.round || 'Interview'} - ${found.job_title || ''}`,
            candidate: found.candidate_name || found.candidate || 'Unknown',
            time: found.start_time || found.time || '',
            round: found.stage || found.round || '',
            date: found.interview_date || found.date || ''
          }
        }
      }
    } catch (err) {
      console.error('Failed to load interview:', err)
    }
  }

  // Fallback to empty structure if no data found
  if (!interview.value) {
    interview.value = {
      id: null,
      title: 'Interview Details',
      candidate: 'Unknown',
      time: '',
      round: '',
      date: '',
    }
  }

  // Update time every second
  setInterval(() => {
    currentTime.value = getCurrentTime()
  }, 1000)
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.meet-container {
  width: 100%;
  height: 100vh;
  background: #202124;
  display: flex;
  font-family:
    'Roboto',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
  color: #fff;
}

.meeting-wrapper {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 0;
}

/* Main Video Section */
.video-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #000;
  overflow: hidden;
}

.video-presentation {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a1e 0%, #202124 100%);
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  color: #5f6368;
}

.placeholder-content .icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.placeholder-content p {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  color: #bdc1c6;
}

.subtext {
  font-size: 0.9rem;
  color: #5f6368;
}

/* Floating Participants */
.participants-floating {
  position: absolute;
  bottom: 80px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 10;
}

.participant-card {
  width: 200px;
  background: rgba(32, 33, 36, 0.95);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.participant-card:hover {
  background: rgba(32, 33, 36, 1);
  border-color: rgba(255, 255, 255, 0.2);
}

.participant-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5b9cf5 0%, #4284f3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-weight: 600;
  font-size: 0.85rem;
}

.participant-avatar.remote {
  background: linear-gradient(135deg, #34a853 0%, #2d8e47 100%);
}

.participant-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.participant-name {
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.participant-status {
  font-size: 0.8rem;
}

/* Info Overlay */
.info-overlay {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  padding: 12px 16px;
  border-radius: 8px;
  z-index: 10;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.meeting-title {
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.meeting-time {
  font-size: 0.85rem;
  color: #bdc1c6;
}

/* Controls Bar */
.controls-bar {
  height: 72px;
  background: rgba(32, 33, 36, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  gap: 16px;
  z-index: 20;
}

.controls-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.controls-group.center {
  margin: 0 auto;
}

/* Control Button */
.control-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 0.7rem;
  font-weight: 500;
  transition: all 0.2s ease;
  position: relative;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.control-btn .icon {
  font-size: 1.2rem;
}

.control-btn .label {
  font-size: 0.65rem;
  white-space: nowrap;
}

.control-btn.btn-off {
  background: rgba(244, 81, 30, 0.3);
}

.control-btn.btn-off:hover {
  background: rgba(244, 81, 30, 0.5);
}

.control-btn.btn-off .icon.strikethrough {
  position: relative;
}

.control-btn.btn-off .icon.strikethrough::after {
  content: '';
  position: absolute;
  width: 120%;
  height: 2px;
  background: #f4511e;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.control-btn.btn-active {
  background: rgba(52, 168, 83, 0.3);
}

.control-btn.btn-active:hover {
  background: rgba(52, 168, 83, 0.5);
}

.control-btn.btn-start-call {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #34a853 0%, #2d8e47 100%);
  box-shadow: 0 4px 12px rgba(52, 168, 83, 0.3);
}

.control-btn.btn-start-call:hover {
  background: linear-gradient(135deg, #2d8e47 0%, #1b6e36 100%);
  box-shadow: 0 6px 16px rgba(52, 168, 83, 0.4);
}

.control-btn.btn-end-call {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #f4511e 0%, #d33610 100%);
  box-shadow: 0 4px 12px rgba(244, 81, 30, 0.3);
}

.control-btn.btn-end-call:hover {
  background: linear-gradient(135deg, #d33610 0%, #a1280d 100%);
  box-shadow: 0 6px 16px rgba(244, 81, 30, 0.4);
}

.control-btn.btn-exit {
  background: rgba(255, 255, 255, 0.15);
}

.control-btn.btn-exit:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Side Panel */
.side-panel {
  width: 320px;
  background: #292a2d;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-tabs {
  display: flex;
  padding: 12px;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  color: #bdc1c6;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tab-btn.active {
  color: #fff;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 0;
  right: 0;
  height: 3px;
  background: #5b9cf5;
  border-radius: 2px;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.tab-content::-webkit-scrollbar {
  width: 6px;
}

.tab-content::-webkit-scrollbar-track {
  background: transparent;
}

.tab-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.tab-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Info Section */
.info-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #bdc1c6;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.9rem;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  color: #9aa0a6;
}

.detail-value {
  color: #fff;
  font-weight: 500;
  text-align: right;
  flex: 1;
  margin-left: 12px;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-badge.status-active {
  background: rgba(52, 168, 83, 0.2);
  border-color: rgba(52, 168, 83, 0.4);
  color: #81c995;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
}

.status-badge.status-active .status-dot {
  background: #34a853;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

/* Action Grid */
.action-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.action-btn .icon {
  font-size: 1.1rem;
}

.action-btn.approve {
  background: rgba(52, 168, 83, 0.2);
  color: #81c995;
  border: 1px solid rgba(52, 168, 83, 0.4);
}

.action-btn.approve:hover {
  background: rgba(52, 168, 83, 0.3);
  border-color: rgba(52, 168, 83, 0.6);
}

.action-btn.reject {
  background: rgba(244, 81, 30, 0.2);
  color: #f4a460;
  border: 1px solid rgba(244, 81, 30, 0.4);
}

.action-btn.reject:hover {
  background: rgba(244, 81, 30, 0.3);
  border-color: rgba(244, 81, 30, 0.6);
}

.action-btn.hold {
  background: rgba(251, 188, 4, 0.2);
  color: #fcc934;
  border: 1px solid rgba(251, 188, 4, 0.4);
}

.action-btn.hold:hover {
  background: rgba(251, 188, 4, 0.3);
  border-color: rgba(251, 188, 4, 0.6);
}

/* Notes Input */
.notes-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 120px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.notes-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.12);
  border-color: #5b9cf5;
  box-shadow: 0 0 0 3px rgba(91, 156, 245, 0.2);
}

.btn-save-notes {
  width: 100%;
  padding: 10px 16px;
  background: #5b9cf5;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-save-notes:hover {
  background: #4284f3;
  box-shadow: 0 2px 8px rgba(91, 156, 245, 0.3);
}

/* Responsive */
@media (max-width: 1200px) {
  .side-panel {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .meeting-wrapper {
    flex-direction: column;
  }

  .side-panel {
    width: 100%;
    height: 50%;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .controls-bar {
    height: 64px;
    padding: 0 12px;
  }

  .control-btn {
    width: 44px;
    height: 44px;
  }

  .control-btn.btn-start-call,
  .control-btn.btn-end-call {
    width: 48px;
    height: 48px;
  }

  .participants-floating {
    bottom: 68px;
    right: 12px;
    flex-direction: row;
    gap: 8px;
  }

  .participant-card {
    width: 160px;
  }
}

@media (max-width: 480px) {
  .controls-bar {
    height: auto;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px;
  }

  .control-btn {
    width: 40px;
    height: 40px;
    font-size: 0.6rem;
  }

  .info-overlay {
    font-size: 0.8rem;
    padding: 8px 12px;
  }

  .participants-floating {
    width: 100%;
    bottom: auto;
    top: 12px;
    right: auto;
    left: 12px;
    flex-direction: row;
  }

  .participant-card {
    width: 140px;
  }
}
</style>
