<template>
  <div class="interview-slots-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">📅 Interviews</h1>
        <p class="page-subtitle">You can see and evaluate interviews from here</p>
      </div>

      <div class="header-right">
        <!-- Filter Dropdown -->
        <select v-model="statusFilter" class="filter-select">
          <option value="all">All Interviews</option>
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
        </select>

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
            :class="['toggle-btn', { active: viewMode === 'cards' }]"
            @click="viewMode = 'cards'"
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
              <rect x="3" y="3" width="7" height="7" rx="1"></rect>
              <rect x="14" y="3" width="7" height="7" rx="1"></rect>
              <rect x="14" y="14" width="7" height="7" rx="1"></rect>
              <rect x="3" y="14" width="7" height="7" rx="1"></rect>
            </svg>
            Cards
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-badge">{{ interviewsScheduledMonth }}</div>
        <p class="stat-label">Scheduled Interviews this month</p>
        <div class="stat-icon" style="background: #dbeafe; color: #0369a1">📋</div>
      </div>
      <div class="stat-card">
        <div class="stat-badge">{{ interviewsScheduledWeek }}</div>
        <p class="stat-label">Scheduled Interviews this week</p>
        <div class="stat-icon" style="background: #fed7aa; color: #b45309">⏳</div>
      </div>
      <div class="stat-card">
        <div class="stat-badge">{{ completedCount }}</div>
        <p class="stat-label">Completed Interviews</p>
        <div class="stat-icon" style="background: #dcfce7; color: #15803d">✅</div>
      </div>
      <div class="stat-card">
        <div class="stat-badge">{{ totalPending }}</div>
        <p class="stat-label">Pending Interviews</p>
        <div class="stat-icon" style="background: #fef3c7; color: #d97706">📅</div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="viewMode === 'calendar'" class="main-content">
      <!-- Left Section: Calendar -->
      <div class="left-section">
        <div class="calendar-card">
          <div class="calendar-header">
            <button class="nav-btn" @click="previousMonth">‹</button>
            <h3 class="calendar-title">{{ monthYear }}</h3>
            <button class="nav-btn" @click="nextMonth">›</button>
          </div>
          <div class="calendar-grid">
            <div class="day-label">S</div>
            <div class="day-label">M</div>
            <div class="day-label">T</div>
            <div class="day-label">W</div>
            <div class="day-label">T</div>
            <div class="day-label">F</div>
            <div class="day-label">S</div>
            <div
              v-for="day in calendarDays"
              :key="`${day.year}-${day.month + 1}-${day.date}`"
              :class="[
                'day',
                {
                  'other-month': day.otherMonth,
                  today: day.isToday,
                  selected: day.isSelected,
                  'has-interview': day.hasInterview
                }
              ]"
              @click="selectDate(day)"
            >
              {{ day.date }}
              <span v-if="day.hasInterview" class="interview-dot"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Section: Scheduled Interviews -->
      <div class="right-section">
        <div class="interviews-card">
          <div class="card-header">
            <h2 class="section-title">Scheduled Interviews</h2>
          </div>
          <div class="date-label">{{ selectedDateFormatted }}</div>
          <div class="interviews-list">
            <div
              v-for="(interview, index) in filteredScheduledInterviews"
              :key="index"
              class="interview-item"
            >
              <div class="interview-number">{{ index + 1 }}</div>
              <div class="interview-info">
                <div class="interview-header-row">
                  <p class="interview-title">{{ interview.title }}</p>
                  <span :class="['status-label', interview.status.toLowerCase()]">
                    {{ interview.status }}
                  </span>
                </div>
                <p class="interview-candidate">
                  {{ interview.candidate }} • {{ interview.time }}
                </p>
              </div>
              <!-- BUTTON: only clickable when SCHEDULED; COMPLETED shows actual RESULT -->
              <button
                :class="['view-btn', { disabled: !interview.sessionid }]"
                @click="interview.sessionid && viewInterview(interview.sessionid || interview.id)"
                :disabled="!interview.sessionid"
              >
                {{
                  interview.status === 'scheduled'
                    ? 'View'
                    : formatResult(interview.result)
                }}
              </button>
            </div>

            <p v-if="filteredScheduledInterviews.length === 0" class="no-interviews">
              No interviews scheduled for this date
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Cards View -->
    <div v-if="viewMode === 'cards'" class="cards-view">
      <div class="cards-grid">
        <div
            v-for="interview in filteredInterviews"
            :key="interview.id"
            class="interview-card-item"
            @click="viewInterview(interview.id)"
        >
            <div class="card-header-section">
            <div class="candidate-initial">
              {{ getInitials(interview.candidate) }}
            </div>
            <div class="card-info">
              <h3 class="card-candidate-name">{{ interview.candidate }}</h3>
              <p class="card-title-text">{{ interview.title }}</p>
            </div>
            <span :class="['status-badge-card', interview.status.toLowerCase()]">
              {{ interview.status }}
            </span>
          </div>

          <div class="card-details-section">
            <div class="detail-row-item">
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
              <span>{{ formatDateCard(interview.date) }}</span>
            </div>
            <div class="detail-row-item">
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
          </div>

            <!-- BUTTON: only clickable when SCHEDULED; COMPLETED shows actual RESULT -->
          <button
            class="card-view-btn"
            @click.stop="viewInterview(interview.id)"
          >
            {{
              interview.status === 'scheduled'
                ? 'View Details'
                : formatResult(interview.result)
            }}
          </button>
        </div>
      </div>

      <p v-if="filteredInterviews.length === 0" class="no-interviews-cards">
        No {{ statusFilter === 'all' ? '' : statusFilter }} interviews found
      </p>
    </div>

    <!-- Schedule Modal (unchanged except logic around status/result not needed) -->
    <div v-if="showScheduleModal" class="modal-overlay" @click="showScheduleModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Schedule an Interview</h3>
          <button class="close-btn" @click="showScheduleModal = false">×</button>
        </div>
        <form class="modal-form" @submit.prevent="scheduleInterview">
          <div class="form-group">
            <label for="candidate">Select Candidate</label>
            <select id="candidate" v-model="newInterview.candidate" required>
              <option value="">Choose a candidate</option>
              <option
                v-for="candidate in availableCandidates"
                :key="candidate.id"
                :value="candidate.name"
              >
                {{ candidate.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="position">Position</label>
            <select id="position" v-model="newInterview.position" required>
              <option value="">Choose a position</option>
              <option value="SDE 1">SDE 1</option>
              <option value="SDE 2">SDE 2</option>
              <option value="SDE 3">SDE 3</option>
              <option value="Product Manager">Product Manager</option>
            </select>
          </div>
          <div class="form-group">
            <label for="round">Interview Round</label>
            <select id="round" v-model="newInterview.round" required>
              <option value="">Choose round</option>
              <option value="Screening">Screening</option>
              <option value="Technical">Technical</option>
              <option value="Final">Final</option>
            </select>
          </div>
          <div class="form-group">
            <label for="time">Interview Time</label>
            <input type="time" id="time" v-model="newInterview.time" required />
          </div>
          <div class="form-group">
            <label for="duration">Duration (minutes)</label>
            <input
              type="number"
              id="duration"
              v-model="newInterview.duration"
              min="15"
              required
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="showScheduleModal = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn">Schedule</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

/* ---------------------------------------------------------
   HR IDENTIFICATION
--------------------------------------------------------- */
const hrUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
const companyId = hrUser?.company_id

/* ---------------------------------------------------------
   VIEW / FILTER STATE
--------------------------------------------------------- */
const currentDate = ref(new Date())
const selectedDate = ref(new Date())
const showScheduleModal = ref(false)
const viewMode = ref('cards')
const statusFilter = ref('all')

/* ---------------------------------------------------------
   INTERVIEWS FROM BACKEND
--------------------------------------------------------- */
const rawCards = computed(() => store.getters['hr/interviewCards'] || [])

/* Map backend → template shape (now includes sessionid + result) */
const interviews = computed(() =>
  rawCards.value.map((it) => {
    const interviewId = it.interview_id ?? it.id ?? it.interviewId
    const sessionid = it.session_id || it.sessionid || it.sessionId || null

    const date =
      it.date ||
      it.scheduled_date ||
      it.interview_date ||
      it.scheduledDate ||
      null

    const time = it.time || it.scheduled_time || it.scheduledTime || null

    const candidate =
      it.name ||
      it.candidate_name ||
      it.candidate ||
      it.applicant_name ||
      'Candidate'

    const title = it.title || it.stage || it.round || 'Interview'

    const rawStatus = (it.status || it.interview_status || '').toLowerCase().trim()
    let status = 'scheduled'
    if (rawStatus === 'interview done' || rawStatus === 'completed') {
      status = 'completed'
    } else if (rawStatus === 'pending interview' || rawStatus === 'scheduled') {
      status = 'scheduled'
    }

    const result =
      it.result ||
      it.final_result ||
      it.outcome ||
      null

    return {
      id: interviewId,
      sessionid,
      date,
      candidate,
      title,
      time,
      status,
      result
    }
  })
)

/* ---------------------------------------------------------
   STATS (month/week/completed/pending)
--------------------------------------------------------- */
const interviewsScheduledMonth = computed(
  () => store.getters['hr/interviewsScheduledMonth'] ?? 0
)
const interviewsScheduledWeek = computed(
  () => store.getters['hr/interviewsScheduledWeek'] ?? 0
)
const completedCount = computed(
  () => store.getters['hr/interviewsCompleted'] ?? 0
)
const totalPending = computed(
  () => store.getters['hr/interviewsPendingFeedback'] ?? 0
)

const totalScheduled = computed(() => interviews.value.length)

/* ---------------------------------------------------------
   FILTERED CARD VIEW
--------------------------------------------------------- */
const filteredInterviews = computed(() => {
  let arr = [...interviews.value]

  arr.sort((a, b) => new Date(a.date) - new Date(b.date))

  if (statusFilter.value === 'scheduled')
    return arr.filter((i) => i.status === 'scheduled')

  if (statusFilter.value === 'completed')
    return arr.filter((i) => i.status === 'completed')

  return arr
})

/* ---------------------------------------------------------
   CALENDAR VIEW
--------------------------------------------------------- */
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

  const interviewDates = new Set(interviews.value.map((i) => i.date))

  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const dateStr = date.toISOString().split('T')[0]

    days.push({
      date: date.getDate(),
      month: date.getMonth(),
      year: date.getFullYear(),
      otherMonth: date.getMonth() !== month,
      isToday: date.toDateString() === today.toDateString(),
      isSelected: date.toDateString() === selectedDate.value.toDateString(),
      fullDate: date,
      hasInterview: interviewDates.has(dateStr)
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
  return interviews.value.filter((i) => i.date === dateStr)
})

const filteredScheduledInterviews = computed(() => {
  const dateStr = selectedDate.value.toISOString().split('T')[0]
  let arr = interviews.value.filter((i) => i.date === dateStr)

  if (statusFilter.value === 'scheduled')
    return arr.filter((i) => i.status === 'scheduled')

  if (statusFilter.value === 'completed')
    return arr.filter((i) => i.status === 'completed')

  return arr
})

const previousMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() - 1)
  currentDate.value = new Date(currentDate.value)
}

const nextMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() + 1)
  currentDate.value = new Date(currentDate.value)
}

const selectDate = (day) => {
  selectedDate.value = day.fullDate
}

/* ---------------------------------------------------------
   HELPERS
--------------------------------------------------------- */
const getInitials = (name = '') =>
  name
    .split(' ')
    .filter(Boolean)
    .map((n) => n[0])
    .join('')
    .toUpperCase() || 'A'

const formatDateCard = (dateStr) => {
  const date = new Date(dateStr)
  const options = { month: 'short', day: 'numeric', year: 'numeric' }
  return date.toLocaleDateString('en-US', options)
}

// Capitalize and fallback if result is missing
const formatResult = (res) => {
  if (!res) return 'Result'
  const s = String(res)
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/* ---------------------------------------------------------
   SCHEDULING (Frontend-only)
--------------------------------------------------------- */
const newInterview = ref({
  candidate: '',
  position: '',
  round: '',
  time: '',
  duration: 60
})

const scheduleInterview = () => {
  const dateStr = selectedDate.value.toISOString().split('T')[0]

  store.commit('hr/SET_INTERVIEW_CARDS', [
    ...rawCards.value,
    {
      id: Date.now(),
      date: dateStr,
      candidate: newInterview.value.candidate,
      title: `${newInterview.value.round} interview for ${newInterview.value.position}`,
      time: newInterview.value.time,
      status: 'scheduled',
      result: null
    }
  ])

  newInterview.value = {
    candidate: '',
    position: '',
    round: '',
    time: '',
    duration: 60
  }
  showScheduleModal.value = false
}

/* ---------------------------------------------------------
   OPEN INTERVIEW DETAIL PAGE
--------------------------------------------------------- */
const viewInterview = (sessionId) => {
  if (!sessionId) {
    console.error('viewInterview called without sessionId')
    return
  }
  router.push({
    name: 'interview-details',
    params: { interviewId: sessionId } // param name MUST be interviewId
  })
}

/* ---------------------------------------------------------
   AVAILABLE CANDIDATES FOR SCHEDULING
--------------------------------------------------------- */
const availableCandidates = ref([])

const loadAvailableCandidates = async () => {
  if (!companyId) return
  try {
    const res = await store.dispatch('hr/fetchShortlistedCandidates', {
      companyId,
      params: {
        status: '',
        role: '',
        search: ''
      }
    })
    availableCandidates.value = (res.candidates || []).map((c) => ({
      id: c.application_id || c.id,
      name:
        `${c.first_name || ''} ${c.last_name || ''}`.trim() ||
        c.candidate_name ||
        'Unknown'
    }))
  } catch (err) {
    console.error('Failed to load candidates for scheduling:', err)
    availableCandidates.value = []
  }
}

/* ---------------------------------------------------------
   LOAD BACKEND DATA
--------------------------------------------------------- */
async function loadData() {
  if (!companyId) return

  await store.dispatch('hr/getInterviewsScheduledThisMonth', companyId)
  await store.dispatch('hr/getInterviewsScheduledThisWeek', companyId)
  await store.dispatch('hr/getInterviewsCompletedCount', companyId)
  await store.dispatch('hr/getInterviewsPendingFeedback', companyId)
  await store.dispatch('hr/fetchInterviewCards', companyId)
  await loadAvailableCandidates()
}

onMounted(loadData)
</script>


<style scoped>
/* styles unchanged from your original */
.interview-slots-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  flex: 1;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Filter Select */
.filter-select {
  padding: 0.5rem 1rem;
  padding-right: 2.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #1e3a5f;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3a5f' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
}

.filter-select:hover {
  border-color: #6366f1;
  background-color: #f8fafc;
}

.filter-select:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background-color: white;
}

.filter-select option {
  background: white;
  color: #1e3a5f;
  padding: 0.5rem;
}

.filter-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f1f5f9;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.875rem;
  margin-bottom: 2rem;
}

.stat-card {
  position: relative;
  background: #fff;
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f5;
  transition: all 0.2s ease;
  cursor: pointer;
  min-height: 120px;
  text-align: center;
}

.stat-card:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.stat-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  border: 3px solid #fff;
}

.stat-label {
  font-size: 0.9rem;
  color: #475569;
  margin: 0;
  font-weight: 600;
  line-height: 1.3;
}

.stat-icon {
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  transition: all 0.2s ease;
  font-size: 2rem;
}

.stat-card:hover .stat-icon {
  opacity: 1;
}

.main-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
}

.left-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.calendar-card {
  background: white;
  padding: 1.2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.nav-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #1e3a5f;
  transition: all 0.2s;
  padding: 0.25rem 0.5rem;
  font-weight: 700;
}

.nav-btn:hover {
  color: #6366f1;
  transform: scale(1.2);
}

.calendar-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
  min-width: 130px;
  text-align: center;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.3rem;
}

.day-label {
  text-align: center;
  font-weight: 600;
  color: #94a3b8;
  font-size: 0.7rem;
  padding: 0.25rem;
}

.day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  color: #1e3a5f;
  font-weight: 500;
  transition: all 0.2s;
  border: 1px solid transparent;
  padding: 0.2rem;
  position: relative;
}

.day:hover {
  background: #f0f7ff;
}

.day.other-month {
  color: #cbd5e1;
}

.day.today {
  background: #6366f1;
  color: white;
  font-weight: 700;
}

.day.selected {
  background: #6366f1;
  color: white;
  border: 2px solid #6366f1;
  font-weight: 700;
}

.day.has-interview {
  background: #dbeafe;
  border: 1px solid #bfdbfe;
}

.day.has-interview:hover {
  background: #bfdbfe;
}

.interview-dot {
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #ef4444;
  border-radius: 50%;
  display: block;
}

.day.has-interview.selected {
  background: #6366f1;
  border-color: #6366f1;
}

.day.has-interview.selected .interview-dot {
  background: #ffffff;
}

.day.today.has-interview {
  background: #6366f1;
  border-color: #6366f1;
}

.day.today.has-interview .interview-dot {
  background: #ffffff;
}

.right-section {
  display: flex;
  flex-direction: column;
}

.interviews-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.date-label {
  padding: 0 1.5rem;
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
  padding-top: 1rem;
}

.interviews-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
  padding: 1rem 1.5rem 1.5rem;
  overflow-y: auto;
  max-height: 400px;
}

.interview-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  gap: 1rem;
  align-items: center;
  transition: all 0.2s;
  background: #f9fafb;
}

.interview-item:hover {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
}

.interview-number {
  font-weight: 700;
  color: #6366f1;
  flex-shrink: 0;
  font-size: 1.1rem;
}

.interview-info {
  flex: 1;
}

.interview-header-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.interview-title {
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
  font-size: 0.9rem;
  flex: 1;
}

.status-label {
  padding: 0.25rem 0.65rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-label.completed {
  background: #dcfce7;
  color: #16a34a;
}

.status-label.scheduled {
  background: #fef3c7;
  color: #d97706;
}

.interview-candidate {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
}

.view-btn {
  padding: 0.5rem 1.2rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.view-btn:hover:not(.disabled) {
  background: #4f46e5;
}

.view-btn.disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  opacity: 0.7;
}

.view-btn:disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  opacity: 0.7;
}

.no-interviews {
  text-align: center;
  color: #94a3b8;
  padding: 2rem 0;
  margin: 0;
  font-size: 0.9rem;
}

/* Cards View */
.cards-view {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.interview-card-item {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: all 0.2s;
  cursor: pointer;
}

.interview-card-item:hover:not(.disabled-card) {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.interview-card-item.disabled-card {
  cursor: not-allowed;
  opacity: 0.7;
}

.card-header-section {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: start;
  gap: 1rem;
}

.candidate-initial {
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

.card-info {
  min-width: 0;
}

.card-candidate-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-title-text {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge-card {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  align-self: start;
}

.status-badge-card.completed {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge-card.scheduled {
  background: #fef3c7;
  color: #d97706;
}

.card-details-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #64748b;
}

.detail-row-item svg {
  color: #6366f1;
  flex-shrink: 0;
}

.card-view-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.card-view-btn:hover:not(.disabled) {
  background: #4f46e5;
  transform: translateY(-1px);
}

.card-view-btn.disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
}

.card-view-btn:disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
}

.no-interviews-cards {
  text-align: center;
  color: #94a3b8;
  padding: 4rem 0;
  margin: 0;
  font-size: 1rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #1e3a5f;
}

.modal-form {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #1e3a5f;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #1e3a5f;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #1e3a5f;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f5f7fa;
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: #4f46e5;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-content {
    grid-template-columns: 1fr;
  }

  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .filter-select,
  .view-toggle {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .day {
    font-size: 0.7rem;
    padding: 0.15rem;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
