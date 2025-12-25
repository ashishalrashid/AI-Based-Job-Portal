<template>
  <div class="shortlisted-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <div class="header-info">
          <h1 class="page-title">Shortlisted Candidates</h1>
          <p class="page-subtitle">Review and manage candidates who have been shortlisted</p>
        </div>
      </div>
    </div>

    <!-- FIXED Modal - NO STAGE + HR ID DEBUG -->
    <div v-if="showScheduleModal" class="popup-overlay" @click="showScheduleModal = false">
      <div class="popup" @click.stop>
        <h3>Schedule Interview for {{ selectedCandidate?.firstName }} {{ selectedCandidate?.lastName }}</h3>
        <form @submit.prevent="saveInterview" class="modal-form">
          <div class="form-group">
            <label for="interview-date">Interview Date</label>
            <input type="date" id="interview-date" v-model="newInterview.interview_date" required />
          </div>
          <div class="form-group">
            <label for="interview-time">Interview Time</label>
            <input type="time" id="interview-time" v-model="newInterview.interview_time" required />
          </div>
          <div class="form-group">
            <label for="duration">Duration (minutes)</label>
            <input type="number" id="duration" v-model="newInterview.duration" min="15" max="240" required />
          </div>
          <div class="popup-actions">
            <button type="button" class="cancel-btn" @click="showScheduleModal = false">Cancel</button>
            <button type="submit" class="confirm-btn" :disabled="!isFormValid">Schedule Interview</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="search-filter-card">
      <div class="search-input-wrapper">
        <input type="text" placeholder="Search candidate name or ID..." v-model="searchQuery" class="search-input" />
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path>
        </svg>
      </div>
      <div class="filter-section">
        <label>Filter by Status</label>
        <select v-model="selectedStatus" @change="handleStatusChange" class="filter-select">
          <option value="">All Status</option>
          <option value="Pending Interview">Pending Interview</option>
          <option value="Interview Done">Interview Done</option>
          <option value="Feedback Pending">Feedback Pending</option>
          <option value="Offer Sent">Offer Sent</option>
          <option value="Accepted">Accepted</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>
      <div class="filter-section">
        <label>Filter by Role</label>
        <select v-model="selectedRole" @change="handleRoleChange" class="filter-select">
          <option value="">All Roles</option>
          <option value="Frontend Developer">Frontend Developer</option>
          <option value="Backend Developer">Backend Developer</option>
          <option value="Full Stack">Full Stack</option>
          <option value="Designer">Designer</option>
          <option value="Manager">Manager</option>
        </select>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ totalShortlisted }}</div>
        <div class="stat-label">Total Shortlisted</div>
        <div class="stat-icon blue">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ pendingInterviews }}</div>
        <div class="stat-label">Pending Interviews</div>
        <div class="stat-icon purple">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ offersSent }}</div>
        <div class="stat-label">Offers Sent</div>
        <div class="stat-icon orange">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ acceptanceRate }}%</div>
        <div class="stat-label">Acceptance Rate</div>
        <div class="stat-icon green">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- Candidates Table -->
    <div class="candidates-container">
      <div class="candidates-header">
        <h2>Candidates List</h2>
        <span class="candidates-count">{{ filteredCandidates.length }} candidates</span>
      </div>
      <div class="table-wrapper">
        <table class="candidates-table">
          <thead>
            <tr>
              <th>SN</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Role</th>
              <th>AI Match Score</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(candidate, index) in paginatedCandidates" :key="candidate.id">
              <td>{{ (currentPage - 1) * itemsPerPage + index + 1 }}</td>
              <td>{{ candidate.firstName }}</td>
              <td>{{ candidate.lastName }}</td>
              <td>{{ candidate.role }}</td>
              <td>
                <span :class="['score-badge', candidate.matchScore >= 75 ? 'high' : candidate.matchScore >= 50 ? 'medium' : 'low']">
                  {{ candidate.matchScore }}%
                </span>
              </td>
              <td>
                <span :class="['status-badge', getStatusClass(candidate.status)]">{{ candidate.status }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view-btn" @click="viewCandidate(candidate.id)" title="View Profile">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button :class="['action-btn', 'schedule-btn', { disabled: candidate.status !== 'Pending Interview' }]" @click="candidate.status === 'Pending Interview' && scheduleInterview(candidate.id)" :disabled="candidate.status !== 'Pending Interview'" title="Schedule Interview">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                  </button>
                  <button :class="['action-btn', 'offer-btn', { disabled: !isEligibleForOffer(candidate) }]" @click="isEligibleForOffer(candidate) && sendOffer(candidate.id)" :disabled="!isEligibleForOffer(candidate)" title="Generate Offer">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22 6 12 13 2 6"></polyline>
                    </svg>
                  </button>
                  <button :class="['action-btn', 'reject-btn', { disabled: ['Accepted', 'Rejected'].includes(candidate.status) }]" @click="!['Accepted', 'Rejected'].includes(candidate.status) && rejectCandidate(candidate.id)" :disabled="['Accepted', 'Rejected'].includes(candidate.status)" title="Reject">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination-section">
        <div class="pagination-info">
          Showing <strong>{{ (currentPage - 1) * itemsPerPage + 1 }}</strong> to <strong>{{ Math.min(currentPage * itemsPerPage, filteredCandidates.length) }}</strong> of <strong>{{ filteredCandidates.length }}</strong> candidates
        </div>
        <div class="pagination-controls">
          <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="['pagination-btn', { active: currentPage === page }]">{{ page }}</button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredCandidates.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
        <circle cx="12" cy="12" r="10"></circle><path d="M12 6v6m0 4v.01"></path>
      </svg>
      <p>No candidates found matching your criteria</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = 12

// FIXED: Removed stage field
const showScheduleModal = ref(false)
const selectedCandidate = ref(null)
const newInterview = ref({
  interview_date: '',
  interview_time: '',
  duration: 30
})

const shortlisted = ref([])
const stats = ref({
  acceptance_rate: 0,
  offers_sent: 0,
  pending_interviews: 0,
  total_shortlisted: 0,
})

// FIXED: No stage validation
const isFormValid = computed(() => {
  return newInterview.value.interview_date && 
         newInterview.value.interview_time && 
         newInterview.value.duration >= 15
})

function normalizeStatus(raw) {
  if (!raw) return 'Pending Interview'
  const s = String(raw).toLowerCase().trim()
  // Map backend statuses to frontend display
  if (s === 'pending interview' || s === 'scheduled') return 'Pending Interview'
  if (s === 'interview done' || s === 'completed') return 'Interview Done'
  if (s === 'feedback pending' || s === 'feedback_pending') return 'Feedback Pending'
  if (s === 'offer sent' || s === 'sent') return 'Offer Sent'
  if (s === 'accepted') return 'Accepted'
  if (s === 'rejected') return 'Rejected'
  // Fallback for partial matches
  if (s.includes('pending') && s.includes('feedback')) return 'Feedback Pending'
  if (s.includes('pending')) return 'Pending Interview'
  if (s.includes('done') || s.includes('completed')) return 'Interview Done'
  if (s.includes('offer')) return 'Offer Sent'
  if (s.includes('accepted')) return 'Accepted'
  if (s.includes('reject')) return 'Rejected'
  return 'Pending Interview'
}

function normalizeCandidates(list = []) {
  return (list || []).map((c, i) => ({
    id: c.application_id ?? (c.applicant_id ? `a-${c.applicant_id}` : i + 1),
    applicationId: c.application_id ?? null,
    firstName: c.first_name ?? (c.candidate?.name ?? '') ?? '',
    lastName: c.last_name ?? '',
    role: c.role ?? (c.job_title ?? '') ?? '',
    matchScore: c.ai_match_score == null ? 0 : Number(c.ai_match_score),
    status: normalizeStatus(c.status),
    statusRaw: c.status ?? null,
    interviewResult: c.interview_result ?? null, // Include interview result for offer eligibility
  }))
}

async function loadStats(companyId) {
  try {
    const res = await store.dispatch('hr/fetchShortlistStats', companyId)
    stats.value = res ?? stats.value
  } catch (err) {
    console.error('loadStats failed', err)
  }
}

async function loadCandidates(companyId) {
  try {
    // Map frontend status to backend expected format
    let statusParam = selectedStatus.value || ''
    if (statusParam) {
      const statusMap = {
        'Pending Interview': 'pending interview',
        'Interview Done': 'interview done',
        'Feedback Pending': 'feedback pending',
        'Offer Sent': 'offer sent',
        'Accepted': 'accepted',
        'Rejected': 'rejected'
      }
      statusParam = statusMap[statusParam] || statusParam.toLowerCase()
    }
    
    const params = {
      status: statusParam,
      role: selectedRole.value || '',
      search: searchQuery.value || '',
    }
    const res = await store.dispatch('hr/fetchShortlistedCandidates', { companyId, params })
    shortlisted.value = normalizeCandidates(res)
    if (currentPage.value > Math.ceil(shortlisted.value.length / itemsPerPage)) {
      currentPage.value = 1
    }
  } catch (err) {
    console.error('loadCandidates failed', err)
    shortlisted.value = []
  }
}

// Explicit handlers to ensure filters work
function handleStatusChange() {
  const companyId = store.getters['auth/currentUser']?.company_id
  if (!companyId) return
  currentPage.value = 1
  loadCandidates(companyId)
}

function handleRoleChange() {
  const companyId = store.getters['auth/currentUser']?.company_id
  if (!companyId) return
  currentPage.value = 1
  loadCandidates(companyId)
}

onMounted(async () => {
  const companyId = store.getters['auth/currentUser']?.company_id
  if (!companyId) {
    console.error('company_id missing')
    return
  }
  await loadStats(companyId)
  await loadCandidates(companyId)
})

let refetchTimer = null
watch([searchQuery, selectedRole, selectedStatus], async () => {
  clearTimeout(refetchTimer)
  refetchTimer = setTimeout(async () => {
    const companyId = store.getters['auth/currentUser']?.company_id
    if (!companyId) return
    currentPage.value = 1
    await loadCandidates(companyId)
  }, 250)
})

const filteredCandidates = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return shortlisted.value.filter((c) => {
    const matchesSearch = !q || String(c.firstName || '').toLowerCase().includes(q) || String(c.lastName || '').toLowerCase().includes(q) || String(c.id || '').toLowerCase().includes(q) || String(c.applicationId || '').toLowerCase().includes(q)
    const matchesRole = !selectedRole.value || (c.role || '').toLowerCase() === selectedRole.value.toLowerCase()
    const matchesStatus = !selectedStatus.value || (c.status || '').toLowerCase() === selectedStatus.value.toLowerCase()
    return matchesSearch && matchesRole && matchesStatus
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredCandidates.value.length / itemsPerPage)))
const paginatedCandidates = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredCandidates.value.slice(start, start + itemsPerPage)
})

const totalShortlisted = computed(() => stats.value.total_shortlisted ?? shortlisted.value.length)
const pendingInterviews = computed(() => stats.value.pending_interviews ?? shortlisted.value.filter(c => (c.status || '').toLowerCase().includes('pending')).length)
const offersSent = computed(() => stats.value.offers_sent ?? shortlisted.value.filter(c => (c.status || '').toLowerCase().includes('offer')).length)
const acceptanceRate = computed(() => stats.value.acceptance_rate ?? 0)

function isEligibleForOffer(candidate) {
  // Candidate is eligible if:
  // 1. Status is "Interview Done" (completed interview)
  // 2. Interview result is "selected"
  const statusMatch = candidate.status === 'Interview Done' || 
                      (candidate.statusRaw && candidate.statusRaw.toLowerCase() === 'interview done')
  const resultMatch = candidate.interviewResult && 
                      String(candidate.interviewResult).toLowerCase() === 'selected'
  return statusMatch && resultMatch
}

function getStatusClass(status) {
  if (!status) return 'pending'
  const s = String(status).toLowerCase()
  if (s.includes('pending interview') || (s.includes('pending') && !s.includes('feedback'))) return 'pending'
  if (s.includes('interview done') || s.includes('done') || s.includes('completed')) return 'done'
  if (s.includes('feedback pending') || s.includes('feedback_pending')) return 'feedback'
  if (s.includes('offer sent') || s.includes('offer')) return 'offer'
  if (s.includes('accepted')) return 'accepted'
  if (s.includes('rejected') || s.includes('reject')) return 'rejected'
  return 'pending'
}

function viewCandidate(applicationId) {
  router.push(`/hr/candidates/${applicationId}`)
}

function scheduleInterview(applicationId) {
  const candidate = shortlisted.value.find(c => c.applicationId === applicationId || c.id === applicationId)
  if (!candidate) {
    console.error('Candidate not found:', applicationId)
    return
  }
  selectedCandidate.value = candidate
  showScheduleModal.value = true
  newInterview.value = {
    interview_date: '',
    interview_time: '',
    duration: 30
  }
}

// FIXED: No stage + HR ID debug
async function saveInterview() {
  if (!selectedCandidate.value || !isFormValid.value) {
    alert('Please fill date and time')
    return
  }

  try {
    const authUser = store.getters['auth/currentUser']
    console.log('Full auth user:', authUser)
    
    const hrId = authUser?.hrid || authUser?.hrId || authUser?.id || null
    
    if (!hrId) {
      console.error('No HR ID found in auth user:', authUser)
      alert('HR ID not found. Check console for auth user structure.')
      return
    }

    const payload = {
      applicationId: selectedCandidate.value.applicationId || selectedCandidate.value.id,
      hrId: hrId,
      form: {
        interview_date: newInterview.value.interview_date,
        interview_time: newInterview.value.interview_time,
        duration: newInterview.value.duration
      }
    }

    console.log('Sending payload to backend:', payload)
    await store.dispatch('hr/scheduleInterview', payload)
    
    const idx = shortlisted.value.findIndex(c => c.applicationId === payload.applicationId || c.id === payload.applicationId)
    if (idx !== -1) {
      shortlisted.value[idx].status = 'Interview Scheduled'
    }
    
    showScheduleModal.value = false
    alert(`Interview scheduled for ${selectedCandidate.value.firstName}!`)
    
  } catch (err) {
    console.error('Schedule interview failed:', err)
    alert('Failed: ' + (err.message || err.response?.data?.message || 'Try again'))
  }
}

function sendOffer(applicationId) {
  router.push({ name: 'create-offer-letter', params: { candidateId: String(applicationId) } })
}

async function rejectCandidate(applicationId) {
  if (!confirm('Reject this candidate?')) return
  try {
    await store.dispatch('hr/rejectShortlisted', { applicationId })
    // Update status immediately
    const idx = shortlisted.value.findIndex(x => x.applicationId === applicationId || x.id === applicationId)
    if (idx !== -1) {
      shortlisted.value[idx].status = 'Rejected'
    }
    // Reload the list to ensure consistency with backend
    const companyId = store.getters['auth/currentUser']?.company_id
    if (companyId) {
      await loadCandidates(companyId)
    }
  } catch (err) {
    console.error('rejectShortlisted failed', err)
    alert('Failed to reject candidate. Please try again.')
  }
}
</script>
<style scoped>
.shortlisted-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* Modal Styles - NEW */
.popup-overlay {
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
  backdrop-filter: blur(4px);
}

.popup {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.popup h3 {
  margin: 0 0 1.5rem 0;
  color: #1e3a5f;
  font-size: 1.25rem;
  font-weight: 700;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
}

.form-group input,
.form-group select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.popup-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn,
.confirm-btn {
  flex: 1;
  padding: 0.875rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.cancel-btn {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.cancel-btn:hover {
  background: #f1f5f9;
}

.confirm-btn {
  background: #065eb5;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #054a8f;
}

.confirm-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
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

/* Search and Filter Card */
.search-filter-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  color: #1e3a5f;
  font-family: inherit;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.search-input::placeholder {
  color: #cbd5e1;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #64748b;
  pointer-events: none;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-section label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a5f;
}

.filter-select {
  padding: 0.75rem 1rem;
  padding-right: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  color: #1e3a5f;
  cursor: pointer;
  font-family: inherit;
  font-weight: 500;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3a5f' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
}

.filter-select:hover {
  border-color: #065eb5;
  background-color: #f8fafc;
}

.filter-select:focus {
  outline: none;
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
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

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
  border: 1px solid #f0f0f5;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #065eb5;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  transition: all 0.2s ease;
}

.stat-icon.blue {
  background: #dbeafe;
  color: #0369a1;
}

.stat-icon.purple {
  background: #ede9fe;
  color: #6d28d9;
}

.stat-icon.orange {
  background: #fed7aa;
  color: #b45309;
}

.stat-icon.green {
  background: #dcfce7;
  color: #15803d;
}

.stat-card:hover .stat-icon {
  opacity: 1;
}

/* Candidates Table */
.candidates-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.candidates-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.candidates-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.candidates-count {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
}

.candidates-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #e5e7eb;
}

.candidates-table th {
  padding: 1rem;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e3a5f;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.candidates-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s ease;
}

.candidates-table tbody tr:hover {
  background: #f8f9fa;
}

.candidates-table td {
  padding: 1rem;
  color: #1e3a5f;
  font-weight: 500;
  font-size: 0.9rem;
}

.score-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
}

.score-badge.low {
  background: #fee2e2;
  color: #dc2626;
}

.score-badge.medium {
  background: #fef3c7;
  color: #d97706;
}

.score-badge.high {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge {
  display: inline-block;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.done {
  background: #dbeafe;
  color: #0c4a6e;
}

.status-badge.feedback {
  background: #fce7f3;
  color: #9f1239;
}

.status-badge.offer {
  background: #c7d2fe;
  color: #312e81;
}

.status-badge.accepted {
  background: #dcfce7;
  color: #166534;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: #64748b;
}

.action-btn:hover:not(.disabled) {
  border-color: #065eb5;
  background: #f0f9ff;
  color: #065eb5;
}

.action-btn.schedule-btn:hover:not(.disabled) {
  border-color: #10b981;
  background: #ecfdf5;
  color: #10b981;
}

.action-btn.reject-btn:hover:not(.disabled) {
  border-color: #dc2626;
  background: #fef2f2;
  color: #dc2626;
}

.action-btn.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
}

.action-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Pagination */
.pagination-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  font-size: 0.9rem;
  color: #64748b;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

.pagination-btn {
  min-width: 40px;
  height: 40px;
  padding: 0 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: #1e3a5f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.pagination-btn:hover {
  border-color: #065eb5;
  color: #065eb5;
}

.pagination-btn.active {
  background: #065eb5;
  color: white;
  border-color: #065eb5;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: #94a3b8;
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .search-filter-card {
    grid-template-columns: 1fr 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

@media (max-width: 768px) {
  .shortlisted-page {
    padding: 1rem;
  }

  .search-filter-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .candidates-container {
    padding: 1.5rem;
  }

  .candidates-table th,
  .candidates-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.85rem;
  }

  .pagination-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .action-buttons {
    gap: 0.25rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }

  .action-btn svg {
    width: 14px;
    height: 14px;
  }
}

@media (max-width: 480px) {
  .shortlisted-page {
    padding: 0.75rem;
  }

  .candidates-table th,
  .candidates-table td {
    padding: 0.5rem 0.25rem;
    font-size: 0.8rem;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .stat-card {
    min-height: 90px;
  }

  .candidates-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
