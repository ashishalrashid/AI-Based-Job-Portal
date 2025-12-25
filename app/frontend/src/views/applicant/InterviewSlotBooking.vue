<template>
  <div class="interview-slots-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        </div>
        <div class="header-info">
          <h1 class="page-title">My Interviews</h1>
          <p class="page-subtitle">View and manage your scheduled interviews</p>
        </div>
      </div>

      <!-- View Toggle -->
      <div class="view-toggle">
        <button
          :class="['toggle-btn', { active: viewMode === 'calendar' }]"
          @click="viewMode = 'calendar'"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          Calendar
        </button>
        <button
          :class="['toggle-btn', { active: viewMode === 'list' }]"
          @click="viewMode = 'list'"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
          List
        </button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-number">{{ totalScheduled }}</p>
          <p class="stat-label">Total Scheduled</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-number">{{ upcomingInterviews }}</p>
          <p class="stat-label">Upcoming</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon green">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-number">{{ completedInterviews }}</p>
          <p class="stat-label">Completed</p>
        </div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="viewMode === 'calendar'" class="calendar-layout">
      <div class="calendar-card card">
        <div class="calendar-header">
          <h2 class="calendar-title">{{ monthYear }}</h2>
          <div class="calendar-nav">
            <button class="nav-btn" @click="previousMonth">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
            <button class="nav-btn" @click="nextMonth">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>

        <div class="calendar-grid">
          <div class="calendar-weekdays">
            <div class="weekday">Sun</div>
            <div class="weekday">Mon</div>
            <div class="weekday">Tue</div>
            <div class="weekday">Wed</div>
            <div class="weekday">Thu</div>
            <div class="weekday">Fri</div>
            <div class="weekday">Sat</div>
          </div>
          <div class="calendar-days">
            <button
              v-for="(day, index) in calendarDays"
              :key="index"
              @click="selectDate(day)"
              :class="[
                'calendar-day',
                {
                  'other-month': day.otherMonth,
                  today: day.isToday,
                  selected: day.isSelected,
                  'has-interview': day.hasInterview,
                },
              ]"
            >
              {{ day.date }}
            </button>
          </div>
        </div>
      </div>

      <div class="interviews-panel card">
        <div class="panel-header">
          <h3 class="panel-title">{{ selectedDateFormatted }}</h3>
          <span class="interview-count">
            {{ scheduledInterviews.length }} interview{{ scheduledInterviews.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <div v-if="scheduledInterviews.length > 0" class="interview-list">
          <div
            v-for="interview in scheduledInterviews"
            :key="interview.interview_id"
            class="interview-item"
          >
            <div class="interview-time">{{ interview.time }}</div>
            <div class="interview-details">
              <h4 class="interview-title">{{ interview.title }}</h4>
              <p class="interview-company">{{ interview.company }}</p>
              <span class="interview-round">{{ interview.round }}</span>
            </div>
            <div class="interview-actions">
              <button class="btn-join" @click="joinInterview(interview)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Join Interview
              </button>
              <button class="btn-cancel" @click="cancelInterview(interview.interview_id)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
                Cancel Interview
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <p>No interviews scheduled</p>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-if="viewMode === 'list'" class="list-view card">
      <div v-if="interviews.length > 0" class="interviews-grid">
        <div
          v-for="interview in sortedInterviews"
          :key="interview.interview_id"
          class="interview-card"
        >
          <div class="card-header-section">
            <div class="company-badge">
              {{ getCompanyInitials(interview.company) }}
            </div>
            <div class="header-info">
              <h3 class="card-title">{{ interview.title }}</h3>
              <p class="card-company">{{ interview.company }}</p>
            </div>
          </div>

          <div class="card-details">
            <div class="detail-row">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>{{ formatDate(interview.date) }}</span>
            </div>
            <div class="detail-row">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>{{ interview.time }}</span>
            </div>
            <div class="detail-row">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>{{ interview.round }}</span>
            </div>
          </div>

          <button class="card-join-btn" @click="joinInterview(interview)">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Join Interview
          </button>
          <button class="btn-cancel" @click="cancelInterview(interview.interview_id)">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
            Cancel Interview
          </button>
        </div>
      </div>

      <div v-else class="empty-state-large">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <h3>No Interviews Scheduled</h3>
        <p>You don't have any upcoming interviews at the moment.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()

// View mode toggle
const viewMode = ref('calendar')

// Date management
const currentDate = ref(new Date())
const selectedDate = ref(new Date())

// Raw store data
const rawInterviews = computed(() => store.getters['applicant/interviews'])
const loading = computed(() => store.getters['applicant/loading'])
const error = computed(() => store.getters['applicant/error'])

// Normalize backend data → UI-friendly shape
const interviews = computed(() =>
  rawInterviews.value.map(int => {
    const date = int.interview_date // "YYYY-MM-DD"

    let time = ''
    if (int.start_time && int.end_time) {
      time = `${int.start_time.slice(0, 5)} - ${int.end_time.slice(0, 5)}`
    } else if (int.start_time) {
      time = int.start_time.slice(0, 5)
    }

    return {
      ...int,
      date,                           // used in filters, calendar, list view
      time,                           // show slot time
      title: int.job_title,
      company: int.company_name,
      round: int.stage,
    }
  })
)

// Stats
const totalScheduled = computed(() => interviews.value.length)

const upcomingInterviews = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return interviews.value.filter(i => i.date >= today).length
})

const completedInterviews = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return interviews.value.filter(i => i.date < today).length
})

const sortedInterviews = computed(() => {
  return [...interviews.value].sort((a, b) => new Date(a.date) - new Date(b.date))
})

const monthYear = computed(() => {
  const options = { year: 'numeric', month: 'long' }
  return currentDate.value.toLocaleDateString('en-US', options)
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())

  const days = []
  const today = new Date()
  const interviewDateSet = new Set(interviews.value.map(i => i.date))

  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const dateString = date.toISOString().split('T')[0]
    const hasInterview = interviewDateSet.has(dateString)

    days.push({
      date: date.getDate(),
      month: date.getMonth(),
      year: date.getFullYear(),
      otherMonth: date.getMonth() !== month,
      isToday: date.toDateString() === today.toDateString(),
      isSelected: date.toDateString() === selectedDate.value.toDateString(),
      fullDate: date,
      hasInterview,
    })
  }
  return days
})

const selectedDateFormatted = computed(() => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return selectedDate.value.toLocaleDateString('en-US', options)
})

const scheduledInterviews = computed(() => {
  const dateStr = selectedDate.value.toISOString().split('T')[0]
  return interviews.value.filter(i => i.date === dateStr)
})

// Methods
const previousMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() - 1)
  currentDate.value = new Date(currentDate.value)
}

const nextMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() + 1)
  currentDate.value = new Date(currentDate.value)
}

const selectDate = day => {
  selectedDate.value = day.fullDate
}

const joinInterview = (interview) => {
  console.log('🔍 Joining interview:', interview)
  console.log('🔍 interview.id:', interview.id)
  console.log('🔍 interview.interviewid:', interview.interviewid)

  const id = interview.id || interview.interviewid

  if (!id) {
    alert('Interview ID is missing!')
    return
  }

  router.push(`/applicant/video-interview/${id}`)
}


const getCompanyInitials = company => {
  if (!company) return 'NA'
  const trimmed = company.trim()
  if (!trimmed) return 'NA'
  return trimmed.substring(0, 2).toUpperCase()
}

const formatDate = dateStr => {
  const date = new Date(dateStr)
  const options = { month: 'short', day: 'numeric', year: 'numeric' }
  return date.toLocaleDateString('en-US', options)
}

onMounted(() => {
  store.dispatch('applicant/fetchMyInterviews')
})

const cancelInterview = async interviewId => {
  if (confirm('Are you sure you want to cancel this interview? This action cannot be undone.')) {
    try {
      await store.dispatch('applicant/cancelInterview', interviewId)
      store.dispatch('applicant/fetchMyInterviews')
    } catch (error) {
      alert('Failed to cancel interview. Please try again.')
    }
  }
}
</script>

<style scoped>
.interview-slots-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: #dbeafe;
  color: #0369a1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

/* View Toggle */
.view-toggle {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 0.35rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #f9fafb;
  color: #1e3a5f;
}

.toggle-btn.active {
  background: #6366f1;
  color: white;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.blue {
  background: #dbeafe;
  color: #0284c7;
}

.stat-icon.orange {
  background: #fed7aa;
  color: #d97706;
}

.stat-icon.green {
  background: #dcfce7;
  color: #16a34a;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}

/* Card */
.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Calendar Layout */
.calendar-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
}

/* Calendar Card */
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.calendar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.calendar-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
}

.nav-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.weekday {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  padding: 0.5rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.calendar-day {
  aspect-ratio: 1;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  color: #1e3a5f;
  font-size: 0.85rem;
  position: relative;
}

.calendar-day:hover {
  border-color: #6366f1;
  background: #f8f9fa;
}

.calendar-day.other-month {
  color: #cbd5e1;
}

.calendar-day.today {
  background: #eff6ff;
  border-color: #0284c7;
  color: #0284c7;
  font-weight: 700;
}

.calendar-day.selected {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

.calendar-day.has-interview::after {
  content: '';
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #ef4444;
  border-radius: 50%;
}

.calendar-day.selected.has-interview::after {
  background: white;
}

/* Interviews Panel */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.panel-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.interview-count {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
  background: #f9fafb;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
}

.interview-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.interview-item {
  display: grid;
  grid-template-columns: 80px 1fr auto;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  transition: all 0.2s;
}

.interview-item:hover {
  border-color: #6366f1;
  background: #f8f9fa;
}

.interview-time {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6366f1;
  background: #eff6ff;
  padding: 0.5rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.interview-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.interview-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.interview-company {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.interview-round {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.interview-actions {
  display: flex;
  align-items: center;
}

.btn-join {
  background-color: #10b981;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  margin-right: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-join:hover {
  background-color: #059669;
}

.btn-cancel {
  background-color: #ef4444;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-cancel:hover {
  background-color: #dc2626;
}

/* List View */
.list-view {
  padding: 2rem;
}

.interviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.interview-card {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: all 0.2s;
}

.interview-card:hover {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.company-badge {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-company {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #64748b;
}

.detail-row svg {
  color: #6366f1;
  flex-shrink: 0;
}

.card-join-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.card-join-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

/* Empty State */
.empty-state {
  padding: 2rem 1rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state svg {
  color: #cbd5e1;
  margin-bottom: 0.75rem;
}

.empty-state p {
  font-size: 0.85rem;
  margin: 0;
}

.empty-state-large {
  padding: 4rem 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state-large svg {
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state-large h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 0.5rem 0;
}

.empty-state-large p {
  font-size: 0.9rem;
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .calendar-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .interview-slots-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .interviews-grid {
    grid-template-columns: 1fr;
  }

  .interview-item {
    grid-template-columns: 1fr;
  }

  .btn-join,
  .card-join-btn {
    width: 100%;
  }
}
</style>
