<template>
  <div class="applicant-dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">Welcome back, {{ userName }}! 👋</h1>
        <p class="welcome-subtitle">Here's your job application summary</p>
      </div>
      <div class="welcome-actions">
        <router-link to="/applicant/jobs" class="btn-primary">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          Browse Jobs
        </router-link>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- Left Column -->
      <div class="column-left">
        <!-- Recent Applications Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Recent Applications</h2>
            <router-link to="/applicant/review-applications" class="view-all-link"
              >View All</router-link
            >
          </div>
          <div class="applications-list">
            <div v-if="recentApplications.length > 0" class="applications-items">
              <div v-for="app in recentApplications" :key="app.id" class="app-item">
                <div class="app-header">
                  <div class="company-info">
                    <div class="company-logo">{{ app.company.substring(0, 2).toUpperCase() }}</div>
                    <div class="app-details">
                      <p class="app-position">{{ app.position }}</p>
                      <p class="app-company">{{ app.company }}</p>
                    </div>
                  </div>
                  <span :class="['status-badge', getStatusClass(app.status)]">{{
                    app.status
                  }}</span>
                </div>
                <div class="app-footer">
                  <span class="app-date">{{ formatDate(app.appliedDate) }}</span>
                  <button class="btn-small" @click="viewApplicationDetails(app.id)">View</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>No applications yet</p>
              <router-link to="/applicant/jobs" class="btn-small">Start Applying</router-link>
            </div>
          </div>
        </div>

        <!-- Upcoming Interviews Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Upcoming Interviews</h2>
            <router-link to="/applicant/interview-slots" class="view-all-link"
              >View All</router-link
            >
          </div>
          <div class="interviews-list">
            <div v-if="upcomingInterviews.length > 0" class="interview-items">
              <div
                v-for="interview in upcomingInterviews"
                :key="interview.id"
                class="interview-item"
              >
                <div class="interview-header">
                  <div class="interview-date">
                    <p class="date-text">{{ formatDateShort(interview.date) }}</p>
                    <p class="time-text">{{ interview.time }}</p>
                  </div>
                  <div class="interview-info">
                    <p class="interview-position">{{ interview.position }}</p>
                    <p class="interview-company">{{ interview.company }}</p>
                    <p class="interview-round">Round: {{ interview.round }}</p>
                  </div>
                </div>
                <div class="interview-actions">
                  <button
                    class="btn-small primary"
                    @click="handleJoinInterview(interview)"
                  >
                    Join
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>No upcoming interviews</p>
              <p class="empty-hint">Keep applying to get interview invites!</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="column-right">
        <!-- Application Status Overview -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Application Status</h2>
          </div>
          <div class="status-overview">
            <div class="status-item">
              <div class="status-dot applied"></div>
              <span class="status-name">Applied</span>
              <span class="status-count">{{ statusCounts.applied }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot shortlisted"></div>
              <span class="status-name">Shortlisted</span>
              <span class="status-count">{{ statusCounts.shortlisted }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot interview"></div>
              <span class="status-name">Interview</span>
              <span class="status-count">{{ statusCounts.interview }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot offer"></div>
              <span class="status-name">Offer</span>
              <span class="status-count">{{ statusCounts.offer }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot rejected"></div>
              <span class="status-name">Rejected</span>
              <span class="status-count">{{ statusCounts.rejected }}</span>
            </div>
          </div>
        </div>

        <!-- Profile Completeness Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Profile Completeness</h2>
          </div>
          <div class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: profileCompletion + '%' }"></div>
            </div>
            <p class="progress-text">{{ profileCompletion }}% Complete</p>
            <p class="progress-hint">Complete your profile to increase matching chances</p>
            <router-link to="/applicant/profile" class="btn-small primary"
              >Complete Profile</router-link
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useStore } from "vuex"

const router = useRouter()
const store = useStore()

// Loading state
const loading = ref(true)

// Authenticated user
const currentUser = computed(() => store.getters["auth/currentUser"])

// Username for welcome header
const userName = computed(() => {
  const user = store.getters["auth/currentUser"]
  return user?.name || "Applicant"
})

// Store getters (already fixed in applicant.js)
const profile = computed(() => store.getters["applicant/profile"])
const applications = computed(() => store.getters["applicant/applications"])
const applicationSummary = computed(() => store.getters["applicant/applicationSummary"])
const interviews = computed(() => store.getters["applicant/interviews"])
const interviewSummary = computed(() => store.getters["applicant/interviewSummary"])

// -----------------------------------------------------
// RECENT APPLICATIONS (CORRECT MAPPING FROM BACKEND)
// -----------------------------------------------------
const recentApplications = computed(() =>
  applications.value.slice(0, 3).map(a => ({
    id: a.application_id,
    jobId: a.jobId || a.job_id,
    position: a.job_title,
    company: a.company_name,
    status: a.status,
    appliedDate: a.applied_on
  }))
)

///-------------------undefined id--------------

function handleJoinInterview(interview) {
  console.log('🔍 Clicking join for interview:', interview)
  console.log('🔍 interview.id:', interview.id)
  router.push(`/applicant/video-interview/${interview.id}`)
}

// -----------------------------------------------------
// UPCOMING INTERVIEWS (CORRECT MAPPING FROM BACKEND)
// -----------------------------------------------------
const upcomingInterviews = computed(() => {
  console.log('🔍 Raw interviews from store:', interviews.value)

  const mapped = interviews.value.map(iv => {
    console.log('🔍 Single interview:', iv)
    console.log('🔍 iv.id:', iv.id)
    console.log('🔍 iv.interviewid:', iv.interviewid)
    console.log('🔍 iv.interview_id:', iv.interview_id)

    return {
      id: iv.id || iv.interviewid,
      applicationId: iv.application_id,
      position: iv.job_title,
      company: iv.company_name,
      date: iv.interview_date,
      time: iv.start_time + " - " + iv.end_time,
      round: iv.stage
    }
  })

  console.log('🔍 Final mapped interviews:', mapped)
  return mapped
})

// -----------------------------------------------------
// APPLICATION STATUS COUNTS
// -----------------------------------------------------
const statusCounts = computed(() => {
  const normalizeStatus = (s) => String(s || '').toLowerCase()
  return {
    applied: applications.value.filter(a => {
      const s = normalizeStatus(a.status)
      return s === "submitted" || s === "under_review"
    }).length,
    shortlisted: applications.value.filter(a =>
      normalizeStatus(a.status) === "shortlisted"
    ).length,
    interview: applications.value.filter(a => {
      const s = normalizeStatus(a.status)
      return s === "interview_scheduled" || s === "interview"
    }).length,
    offer: applications.value.filter(a =>
      normalizeStatus(a.status) === "offered"
    ).length,
    rejected: applications.value.filter(a =>
      normalizeStatus(a.status) === "rejected"
    ).length,
  }
})

// -----------------------------------------------------
// PROFILE COMPLETION (SAFE + SIMPLE)
// -----------------------------------------------------
const profileCompletion = computed(() => {
  if (!profile.value) return 0

  const fields = [
    "address",
    "highest_qualification",
    "skills",
    "linkedin_url",
    "github_url",
    "portfolio_url",
    "current_job_title",
    "current_company",
    "preferred_location",
  ]

  let filled = 0

  fields.forEach(f => {
    const val = profile.value[f]
    if (Array.isArray(val)) {
      if (val.length > 0) filled++
    } else if (val) {
      filled++
    }
  })

  return Math.round((filled / fields.length) * 100)
})

// -----------------------------------------------------
// HELPERS
// -----------------------------------------------------
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric"
  })
}

const formatDateShort = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric"
  })
}

const getStatusClass = (status) => {
  const statusLower = String(status || '').toLowerCase()
  const classMap = {
    submitted: "applied",
    "under_review": "applied",
    shortlisted: "shortlisted",
    "interview_scheduled": "interview",
    interview: "interview",
    offered: "offer",
    rejected: "rejected"
  }
  return classMap[statusLower] || "applied"
}

const viewApplicationDetails = (applicationId) => {
  // Get the job_id from the application
  const application = recentApplications.value.find(app => app.id === applicationId)
  if (application && application.jobId) {
    router.push(`/applicant/job-details/${application.jobId}`)
  } else {
    // Fallback: try to get job_id from store
    const apps = store.getters['applicant/myApplications'] || []
    const app = apps.find(a => a.application_id === applicationId || a.id === applicationId)
    if (app && (app.jobId || app.job_id)) {
      router.push(`/applicant/job-details/${app.jobId || app.job_id}`)
    } else {
      // Last resort: go to review applications page
      router.push(`/applicant/review-applications?id=${applicationId}`)
    }
  }
}

// -----------------------------------------------------
// ON MOUNT — FETCH EVERYTHING
// -----------------------------------------------------
onMounted(async () => {
  loading.value = true

  await store.dispatch("applicant/fetchProfile")
  await store.dispatch("applicant/fetchMyApplications")
  await store.dispatch("applicant/fetchMyInterviews")

  loading.value = false
})
</script>



<style scoped>
.applicant-dashboard {
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Welcome Section */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.welcome-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

.column-left,
.column-right {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Card Styles */
.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.view-all-link {
  color: #6366f1;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.view-all-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* Applications List */
.applications-list {
  display: flex;
  flex-direction: column;
}

.applications-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.app-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.app-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.company-info {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.company-logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.app-details {
  flex: 1;
}

.app-position {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.app-company {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.applied {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.shortlisted {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.interview {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.offer {
  background: #dcfce7;
  color: #166534;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.app-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-date {
  font-size: 0.8rem;
  color: #94a3b8;
}

.btn-small {
  padding: 0.4rem 1rem;
  background: none;
  color: #6366f1;
  border: 1px solid #6366f1;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-small:hover {
  background: #6366f1;
  color: white;
}

.btn-small.primary {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

.btn-small.primary:hover {
  background: #4f46e5;
  border-color: #4f46e5;
}

/* Interviews List */
.interviews-list {
  display: flex;
  flex-direction: column;
}

.interview-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.interview-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.interview-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.interview-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.interview-date {
  width: 70px;
  padding: 0.5rem;
  background: #eff6ff;
  border-radius: 8px;
  text-align: center;
  flex-shrink: 0;
}

.date-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e40af;
  margin: 0 0 0.25rem 0;
}

.time-text {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.interview-info {
  flex: 1;
}

.interview-position {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.interview-company {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 0.25rem 0;
}

.interview-round {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

.interview-actions {
  display: flex;
  gap: 0.5rem;
}

/* Status Overview */
.status-overview {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.applied {
  background: #3b82f6;
}

.status-dot.shortlisted {
  background: #10b981;
}

.status-dot.interview {
  background: #f59e0b;
}

.status-dot.offer {
  background: #22c55e;
}

.status-dot.rejected {
  background: #ef4444;
}

.status-name {
  flex: 1;
  font-size: 0.9rem;
  color: #475569;
  font-weight: 500;
}

.status-count {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a5f;
}

/* Profile Completeness */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.progress-hint {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

/* Empty State */
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state p {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.empty-hint {
  font-size: 0.85rem;
  color: #cbd5e1;
}

/* Responsive */
@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .column-right {
    grid-template-columns: repeat(2, 1fr);
    display: grid;
  }
}

@media (max-width: 768px) {
  .applicant-dashboard {
    padding: 1rem;
  }

  .welcome-title {
    font-size: 1.5rem;
  }

  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .column-right {
    grid-template-columns: 1fr;
  }

  .company-logo {
    width: 40px;
    height: 40px;
    font-size: 0.8rem;
  }

  .interview-date {
    width: 60px;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 1rem;
  }

  .card-title {
    font-size: 1rem;
  }

  .app-header {
    flex-direction: column;
    gap: 0.75rem;
  }

  .interview-header {
    flex-direction: column;
  }

  .interview-actions {
    flex-direction: column;
  }
}
</style>
