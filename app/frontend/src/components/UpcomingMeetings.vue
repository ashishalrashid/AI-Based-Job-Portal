<template>
  <div class="upcoming-meetings">
    <div class="meetings-header">
      <h2 class="meetings-title">Upcoming Meetings</h2>
    </div>

    <div class="meetings-container">
      <!-- Today Meetings -->
      <div v-if="todayMeetings.length > 0" class="meetings-section">
        <h3 class="section-label">Today</h3>
        <div class="meetings-list">
          <div v-for="meeting in todayMeetings" :key="meeting.id" class="meeting-item">
            <div class="meeting-time">
              <span class="time-badge" :class="{ active: isCurrentTime(meeting.time) }">{{
                meeting.time
              }}</span>
            </div>
            <div class="meeting-info">
              <p class="meeting-title">{{ meeting.title }}</p>
              <p class="meeting-details">{{ meeting.candidate }} • {{ meeting.position }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tomorrow Meetings -->
      <div v-if="tomorrowMeetings.length > 0" class="meetings-section">
        <h3 class="section-label">Tomorrow</h3>
        <div class="meetings-list">
          <div v-for="meeting in tomorrowMeetings" :key="meeting.id" class="meeting-item">
            <div class="meeting-time">
              <span class="time-badge">{{ meeting.time }}</span>
            </div>
            <div class="meeting-info">
              <p class="meeting-title">{{ meeting.title }}</p>
              <p class="meeting-details">{{ meeting.candidate }} • {{ meeting.position }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- This Week Meetings -->
      <div v-if="thisWeekMeetings.length > 0" class="meetings-section">
        <h3 class="section-label">This Week</h3>
        <div class="meetings-list">
          <div v-for="meeting in thisWeekMeetings" :key="meeting.id" class="meeting-item">
            <div class="meeting-date">
              <span class="date-badge">{{ meeting.date }}</span>
            </div>
            <div class="meeting-info">
              <p class="meeting-title">{{ meeting.title }}</p>
              <p class="meeting-details">{{ meeting.candidate }} • {{ meeting.position }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="meetings.length === 0" class="empty-state">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          class="empty-icon"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <p class="empty-text">No upcoming meetings</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

const store = useStore()
const meetings = ref([])

const loadMeetings = async () => {
  try {
    const user = store.getters['auth/currentUser']
    const hrId = user?.hr_id || user?.id
    
    if (!hrId) {
      console.warn('HR ID not found, cannot load meetings')
      return
    }

    const res = await api.get(`/interview/sorted_by_date/${hrId}`)
    const interviews = res.data?.interviews || []
    
    // Transform interviews to meeting format
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const nextWeek = new Date(today)
    nextWeek.setDate(nextWeek.getDate() + 7)
    
    meetings.value = interviews.map(int => {
      const interviewDate = new Date(int.interview_date)
      const timeStr = int.slot_start_time || '00:00'
      const [hours, minutes] = timeStr.split(':')
      const time = `${hours}:${minutes}`
      
      let period = 'thisweek'
      if (interviewDate.toDateString() === today.toDateString()) {
        period = 'today'
      } else if (interviewDate.toDateString() === tomorrow.toDateString()) {
        period = 'tomorrow'
      }
      
      const candidateName = int.candidate_name || int.applicant_name || 'Candidate'
      const jobTitle = int.job_title || 'Position'
      
      return {
        id: int.interview_id || int.id,
        title: `${candidateName}: ${jobTitle}. Interview`,
        candidate: candidateName,
        position: jobTitle,
        time: time,
        date: interviewDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        period: period
      }
    })
  } catch (error) {
    console.error('Failed to load meetings:', error)
  }
}

onMounted(() => {
  loadMeetings()
})

// Filter meetings by period
const todayMeetings = computed(() => meetings.value.filter((m) => m.period === 'today'))

const tomorrowMeetings = computed(() => meetings.value.filter((m) => m.period === 'tomorrow'))

const thisWeekMeetings = computed(() => meetings.value.filter((m) => m.period === 'thisweek'))

// Check if time badge should be highlighted (for current time)
const isCurrentTime = (time) => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const currentTime = `${hours}:${minutes}`
  return time === currentTime
}

// Open create meeting modal
const openCreateMeeting = () => {
  console.log('Opening create meeting modal')
  // TODO: Implement modal opening
}
</script>

<style scoped>
.upcoming-meetings {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.meetings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.meetings-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.add-meeting-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-meeting-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.add-meeting-btn:active {
  transform: translateY(0);
}

.meetings-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.meetings-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.5rem 0;
}

.meetings-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.meeting-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.meeting-item:hover {
  background: #f1f5f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.meeting-time,
.meeting-date {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
}

.time-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  padding: 0.35rem 0.5rem;
  background: transparent;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.time-badge.active {
  background: #10b981;
  color: #fff;
}

.date-badge {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6366f1;
  padding: 0.35rem 0.5rem;
  background: #e0e7ff;
  border-radius: 6px;
}

.meeting-info {
  flex: 1;
  min-width: 0;
}

.meeting-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meeting-details {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #94a3b8;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 0.9rem;
  margin: 0;
}

/* Scrollbar styling */
.upcoming-meetings::-webkit-scrollbar,
.meetings-container::-webkit-scrollbar {
  width: 6px;
}

.upcoming-meetings::-webkit-scrollbar-track,
.meetings-container::-webkit-scrollbar-track {
  background: transparent;
}

.upcoming-meetings::-webkit-scrollbar-thumb,
.meetings-container::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

.upcoming-meetings::-webkit-scrollbar-thumb:hover,
.meetings-container::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

@media (max-width: 1024px) {
  .upcoming-meetings {
    max-height: 400px;
  }
}
</style>
