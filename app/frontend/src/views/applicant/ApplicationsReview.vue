<template>
  <div class="applications-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">My Applications</h1>
        <p class="page-subtitle">Track and manage your job applications</p>
      </div>
      <div class="header-stats">
        <div class="stat-box">
          <p class="stat-number">{{ totalApplications }}</p>
          <p class="stat-label">Total Applications</p>
        </div>
        <div class="stat-box">
          <p class="stat-number">{{ statusCounts.shortlisted }}</p>
          <p class="stat-label">Shortlisted</p>
        </div>
        <div class="stat-box">
          <p class="stat-number">{{ statusCounts.rejected }}</p>
          <p class="stat-label">Rejected</p>
        </div>
      </div>
    </div>

    <!-- Search & Filter Section -->
    <div class="search-filter-section">
      <div class="search-box">
        <label class="filter-label">Search Applications</label>
        <div class="search-input-wrapper">
          <input
            type="text"
            placeholder="Search by position or company"
            v-model="searchQuery"
            class="search-input"
            @input="currentPage = 1"
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="search-icon"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
        </div>
      </div>

      <div class="filter-status">
        <label class="filter-label">Filter by Status</label>
        <select v-model="selectedStatus" class="filter-select" @change="currentPage = 1">
          <option value="">All Status</option>
          <option value="Applied">Applied</option>
          <option value="Shortlisted">Shortlisted</option>
          <option value="Interview Scheduled">Interview Scheduled</option>
          <option value="Rejected">Rejected</option>
          <option value="Offer Received">Offer Received</option>
        </select>
      </div>

      <div class="filter-sort">
        <label class="filter-label">Sort by</label>
        <select v-model="sortBy" class="filter-select" @change="currentPage = 1">
          <option value="recent">Most Recent</option>
          <option value="oldest">Oldest First</option>
          <option value="company">Company A-Z</option>
          <option value="status">Status</option>
        </select>
      </div>
    </div>

    <!-- Applications List -->
    <div class="applications-container">
      <div class="applications-header">
        <h2>Your Applications</h2>
        <span class="applications-count">{{ filteredApplications.length }} applications</span>
      </div>

      <div v-if="paginatedApplications.length > 0" class="applications-grid">
        <div v-for="app in paginatedApplications" :key="app.id" class="application-card">
          <div class="card-header">
            <div class="company-logo">{{ app.company.substring(0, 2).toUpperCase() }}</div>
            <div class="card-header-info">
              <h3 class="position-title">{{ app.position }}</h3>
              <p class="company-name">{{ app.company }}</p>
            </div>
            <span :class="['status-badge', getStatusClass(app.status)]">
              {{ app.status }}
            </span>
          </div>

          <div class="card-body">
            <div class="info-row">
              <span class="info-label">Location:</span>
              <span class="info-value">{{ app.location }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Applied on:</span>
              <span class="info-value">{{ formatDate(app.appliedDate) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Work Mode:</span>
              <span class="info-value work-mode">{{ app.workMode }}</span>
            </div>
            <div class="info-row" v-if="app.interviewDate">
              <span class="info-label">Interview Date:</span>
              <span class="info-value interview-date">{{ formatDate(app.interviewDate) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button class="action-btn view-btn" @click="viewJobDetails(app.jobId)">View Job</button>
            <button
              v-if="app.status === 'Interview Scheduled'"
              class="action-btn interview-btn"
              @click="viewInterview(app.id)"
            >
              Interview Details
            </button>
            <button
              v-if="app.status === 'Offer Received'"
              class="action-btn offer-btn"
              @click="viewOffer(app.id)"
            >
              View Offer
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <h3>No Applications Found</h3>
        <p>Try adjusting your search or filters</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="currentPage = page"
          :class="['pagination-btn', { active: currentPage === page }]"
        >
          {{ page }}
        </button>
      </div>
    </div>

    <!-- Interview Details Modal -->
    <div v-if="showInterviewModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content interview-modal" @click.stop>
        <div class="modal-header">
          <h3>Interview Details</h3>
          <button class="close-btn" @click="closeModal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="interview-header">
            <div class="company-badge">
              {{ selectedInterview?.company?.substring(0, 2).toUpperCase() }}
            </div>
            <div class="interview-info">
              <h4>{{ selectedInterview?.position }}</h4>
              <p>{{ selectedInterview?.company }}</p>
            </div>
          </div>

          <div class="interview-details-grid">
            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
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
              <div class="detail-content">
                <span class="detail-label">Date</span>
                <span class="detail-value">{{ formatDate(selectedInterview?.interviewDate) }}</span>
              </div>
            </div>

            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Time</span>
                <span class="detail-value">{{
                  selectedInterview?.interviewTime || '10:00 AM'
                }}</span>
              </div>
            </div>

            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Interviewer</span>
                <span class="detail-value">{{
                  selectedInterview?.interviewer || 'Sarah Johnson'
                }}</span>
              </div>
            </div>

            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Duration</span>
                <span class="detail-value">{{ selectedInterview?.duration || '45 minutes' }}</span>
              </div>
            </div>

            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Mode</span>
                <span class="detail-value">{{
                  selectedInterview?.interviewMode || 'Virtual'
                }}</span>
              </div>
            </div>

            <div class="detail-item">
              <div class="detail-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
                  ></path>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Round</span>
                <span class="detail-value">{{
                  selectedInterview?.round || 'Technical Round'
                }}</span>
              </div>
            </div>
          </div>

          <div v-if="selectedInterview?.notes" class="interview-notes">
            <h4>Notes</h4>
            <p>{{ selectedInterview.notes }}</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel-interview" @click="cancelInterview">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Cancel Interview
          </button>
          <button class="btn-secondary" @click="closeModal">Close</button>
          <button class="btn-join" @click="joinInterviewFromModal">
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
        </div>
      </div>
    </div>

    <!-- Offer Letter Modal -->
    <div v-if="showOfferModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content offer-modal" @click.stop>
        <div class="modal-header">
          <h3>Offer Letter</h3>
          <button class="close-btn" @click="closeModal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="modal-body offer-body">
          <div class="offer-header">
            <div class="company-logo-large">
              {{ selectedOffer?.company?.substring(0, 2).toUpperCase() }}
            </div>
            <div class="offer-company-info">
              <h2>{{ selectedOffer?.company }}</h2>
              <p>{{ selectedOffer?.location }}</p>
            </div>
          </div>

          <div class="offer-letter-content">
            <div class="offer-greeting">
              <p>Dear Candidate,</p>
            </div>

            <div class="offer-body-text">
              <p>
                We are pleased to offer you the position of
                <strong>{{ selectedOffer?.position }}</strong> at {{ selectedOffer?.company }}. We
                believe your skills and experience will be a valuable addition to our team.
              </p>
            </div>

            <div class="offer-details">
              <h4>Position Details</h4>
              <div class="offer-detail-item">
                <span class="label">Position:</span>
                <span class="value">{{ selectedOffer?.position }}</span>
              </div>
              <div class="offer-detail-item">
                <span class="label">Department:</span>
                <span class="value">{{ selectedOffer?.department || 'Engineering' }}</span>
              </div>
              <div class="offer-detail-item">
                <span class="label">Location:</span>
                <span class="value">{{ selectedOffer?.location }}</span>
              </div>
              <div class="offer-detail-item">
                <span class="label">Work Mode:</span>
                <span class="value">{{ selectedOffer?.workMode }}</span>
              </div>
              <div class="offer-detail-item">
                <span class="label">Start Date:</span>
                <span class="value">{{ selectedOffer?.startDate || 'January 1, 2026' }}</span>
              </div>
            </div>

            <div class="offer-compensation">
              <h4>Compensation & Benefits</h4>
              <div class="compensation-highlight">
                <span class="comp-label">Annual Salary:</span>
                <span class="comp-value">{{ selectedOffer?.salary || '₹12-15 LPA' }}</span>
              </div>
              <ul class="benefits-list">
                <li>Health insurance for you and your family</li>
                <li>Performance-based bonuses</li>
                <li>Flexible working hours</li>
                <li>Professional development opportunities</li>
                <li>Paid time off and holidays</li>
              </ul>
            </div>

            <div class="offer-footer-text">
              <p>
                Please review this offer carefully. If you accept, please respond by clicking the
                "Accept Offer" button below. We look forward to welcoming you to our team!
              </p>
              <p class="offer-validity">
                This offer is valid until
                <strong>{{ selectedOffer?.offerValidUntil || 'December 31, 2025' }}</strong
                >.
              </p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">Decline</button>
          <button class="btn-accept-offer" @click="acceptOffer" :disabled="offerAccepted">
            <svg
              v-if="!offerAccepted"
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {{ offerAccepted ? 'Offer Accepted ✓' : 'Accept Offer' }}
          </button>
        </div>
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

const searchQuery = ref('')
const selectedStatus = ref('')
const sortBy = ref('recent')
const currentPage = ref(1)
const itemsPerPage = 8

const showInterviewModal = ref(false)
const showOfferModal = ref(false)
const selectedInterview = ref(null)
const selectedOffer = ref(null)
const offerAccepted = ref(false)

// 👉 Replace hardcoded array — empty initially
const applications = ref([])

// Summary from backend (optional)
const summary = ref({
  rejected: 0,
  shortlisted: 0,
  total: 0
})

// Fetch real applications
onMounted(async () => {
  try {
    const data = await store.dispatch("applicant/fetchMyApplications")

    summary.value = data.summary

    // Transform backend → frontend format
    applications.value = data.applications.map(a => ({
      id: a.application_id,
      position: a.job_title,
      company: a.company_name,
       jobId: a.jobId,
      location: a.location,
      appliedDate: a.applied_on,
      status: a.status.charAt(0).toUpperCase() + a.status.slice(1),
      workMode: a.work_mode
    }))
  } catch (err) {
    console.error("Failed to load apps", err)
  }
})

const totalApplications = computed(() => applications.value.length)

const statusCounts = computed(() => ({
  shortlisted: applications.value.filter(a => a.status === 'Shortlisted').length,
  rejected: applications.value.filter(a => a.status === 'Rejected').length
}))

const filteredApplications = computed(() => {
  let filtered = applications.value

  if (searchQuery.value) {
    filtered = filtered.filter((app) =>
      app.position.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      app.company.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(app => app.status === selectedStatus.value)
  }

  if (sortBy.value === 'recent') {
    filtered = filtered.sort((a, b) => new Date(b.appliedDate) - new Date(a.appliedDate))
  } else if (sortBy.value === 'oldest') {
    filtered = filtered.sort((a, b) => new Date(a.appliedDate) - new Date(b.appliedDate))
  } else if (sortBy.value === 'company') {
    filtered = filtered.sort((a, b) => a.company.localeCompare(b.company))
  } else if (sortBy.value === 'status') {
    filtered = filtered.sort((a, b) => a.status.localeCompare(b.status))
  }

  return filtered
})

const totalPages = computed(() =>
  Math.ceil(filteredApplications.value.length / itemsPerPage)
)

const paginatedApplications = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredApplications.value.slice(start, end)
})

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return date.toLocaleDateString('en-US', options)
}

const getStatusClass = (status) => {
  const statusMap = {
    Applied: 'applied',
    Shortlisted: 'shortlisted',
    'Interview Scheduled': 'interview',
    Rejected: 'rejected',
    'Offer Received': 'offer',
  }
  return statusMap[status] || 'applied'
}

const viewJobDetails = (jobId) => {
  if (!jobId) return
  router.push({ name: 'job-details', params: { id: jobId } })
}

const viewInterview = (appId) => {
  const application = applications.value.find((app) => app.id === appId)
  if (application) {
    selectedInterview.value = application
    showInterviewModal.value = true
  }
}

const viewOffer = (appId) => {
  const application = applications.value.find((app) => app.id === appId)
  if (application) {
    selectedOffer.value = application
    showOfferModal.value = true
    offerAccepted.value = false
  }
}

const closeModal = () => {
  showInterviewModal.value = false
  showOfferModal.value = false
  selectedInterview.value = null
  selectedOffer.value = null
  offerAccepted.value = false
}

const cancelInterview = () => {
  if (confirm('Are you sure you want to cancel this interview? This action cannot be undone.')) {
    alert('Interview cancelled successfully. HR will be notified.')
    closeModal()
  }
}

const joinInterviewFromModal = () => {
  if (selectedInterview.value) {
    router.push(`/applicant/video-interview/${selectedInterview.value.id}`)
    closeModal()
  }
}

const acceptOffer = () => {
  offerAccepted.value = true
  setTimeout(() => {
    alert('Offer accepted successfully! HR will contact you shortly.')
    closeModal()
  }, 1000)
}
</script>


<style scoped>
.applications-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
  flex-wrap: wrap;
}

.header-content {
  flex: 1;
  min-width: 250px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-box {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-width: 120px;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #6366f1;
  margin: 0;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
  font-weight: 500;
}

/* Search & Filter */
.search-filter-section {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.search-box,
.filter-status,
.filter-sort {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a5f;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #1e3a5f;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-select:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Applications Container */
.applications-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.applications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.applications-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.applications-count {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

/* Applications Grid */
.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.application-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  background: #f9fafb;
  transition: all 0.2s;
}

.application-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #6366f1;
}

.card-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: start;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.company-logo {
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

.card-header-info {
  min-width: 0;
}

.position-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.company-name {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  align-self: start;
}

.status-badge.applied {
  background: #dbeafe;
  color: #0369a1;
}

.status-badge.shortlisted {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.interview {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.offer {
  background: #ede9fe;
  color: #7c3aed;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.info-label {
  color: #64748b;
  font-weight: 500;
}

.info-value {
  color: #1e3a5f;
  font-weight: 600;
}

.info-value.work-mode {
  background: #eff6ff;
  color: #0369a1;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.info-value.interview-date {
  color: #16a34a;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  flex: 1;
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn {
  background: #f1f5f9;
  color: #1e3a5f;
}

.view-btn:hover {
  background: #e2e8f0;
}

.interview-btn {
  background: #10b981;
  color: white;
}

.interview-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.offer-btn {
  background: #7c3aed;
  color: white;
}

.offer-btn:hover {
  background: #6d28d9;
  transform: translateY(-1px);
}

/* Empty State */
.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state svg {
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  font-size: 0.9rem;
  margin: 0;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  padding-top: 2rem;
}

.pagination-btn {
  min-width: 40px;
  height: 40px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #1e3a5f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.pagination-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.pagination-btn.active {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 650px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e3a5f;
}

.modal-body {
  padding: 2rem;
}

.interview-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.company-badge {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 700;
  flex-shrink: 0;
}

.interview-info h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.interview-info p {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.interview-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.detail-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #eff6ff;
  color: #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.detail-label {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 0.95rem;
  color: #1e3a5f;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.interview-notes {
  padding: 1.25rem;
  background: #fffbeb;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
}

.interview-notes h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #92400e;
  margin: 0 0 0.5rem 0;
}

.interview-notes p {
  font-size: 0.875rem;
  color: #78350f;
  line-height: 1.6;
  margin: 0;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-join,
.btn-accept-offer,
.btn-secondary,
.btn-cancel-interview {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-cancel,
.btn-secondary {
  background: #f1f5f9;
  color: #1e3a5f;
}

.btn-cancel:hover,
.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-cancel-interview {
  background: #ef4444;
  color: white;
}

.btn-cancel-interview:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-join {
  background: #10b981;
  color: white;
}

.btn-join:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-accept-offer {
  background: #7c3aed;
  color: white;
}

.btn-accept-offer:hover:not(:disabled) {
  background: #6d28d9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}

.btn-accept-offer:disabled {
  background: #10b981;
  cursor: not-allowed;
  opacity: 0.8;
}

/* Responsive styles omitted for brevity */
</style>
