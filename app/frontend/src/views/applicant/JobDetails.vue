<template>
  <div class="job-details-page" v-if="!loading">
    <!-- Header -->
    <div class="page-header" v-if="jobData">
      <button class="back-btn" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Back to Jobs
      </button>

      <div class="header-actions">
        <button class="btn-download" @click="downloadJD" :disabled="!jobData.jd_file_url">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Download JD
        </button>

        <button class="btn-apply" @click="applyForJob" :disabled="hasApplied">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          {{ hasApplied ? 'Already Applied' : 'Apply Now' }}
        </button>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="error" class="error-box">{{ error }}</div>

    <!-- Main Content -->
    <div class="content-grid" v-if="jobData">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Job Overview Card -->
        <div class="card job-overview-card">
          <div class="company-header">
            <div class="company-logo">
              {{ getCompanyInitials(jobData.company || '') }}
            </div>
            <div class="company-info">
              <h1 class="job-title">{{ jobData.position }}</h1>
              <p class="company-name">{{ jobData.company }}</p>

              <div class="job-meta">
                <span class="meta-item">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                  </svg>
                  {{ jobData.location }}
                </span>

                <span class="meta-divider">•</span>

                <span class="meta-item">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                  </svg>
                  {{ jobData.experience }}
                </span>

                <span class="meta-divider">•</span>

                <span class="meta-item">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                  {{ jobData.workMode }}
                </span>
              </div>

              <div class="salary-badge">{{ jobData.salary }}</div>
            </div>
          </div>

          <div class="posted-date">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Posted {{ jobData.postedDate }}
          </div>
        </div>

        <!-- Job Description -->
        <div class="card">
          <div class="card-header"><h2 class="card-title">Job Description</h2></div>
          <div class="job-description"><p>{{ jobData.description }}</p></div>
        </div>

        <!-- Responsibilities -->
        <div class="card" v-if="jobData.responsibilities?.length">
          <div class="card-header"><h2 class="card-title">Key Responsibilities</h2></div>
          <ul class="responsibilities-list">
            <li v-for="(r, i) in jobData.responsibilities" :key="i">{{ r }}</li>
          </ul>
        </div>

        <!-- Requirements -->
        <div class="card" v-if="jobData.requirements?.length">
          <div class="card-header"><h2 class="card-title">Requirements</h2></div>
          <ul class="requirements-list">
            <li v-for="(req, i) in jobData.requirements" :key="i">{{ req }}</li>
          </ul>
        </div>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Skills Match Card -->
        <div class="card skills-match-card">
          <div class="card-header"><h3 class="card-title">Skills Match</h3></div>

          <div class="match-score">
            <div class="score-circle">
              <svg class="score-progress" width="120" height="120">
                <circle cx="60" cy="60" r="54" class="score-bg"></circle>
                <circle cx="60" cy="60" r="54" class="score-fill" :style="{ strokeDashoffset: calculateOffset(matchPercentage) }"></circle>
              </svg>

              <div class="score-text">
                <span class="score-value">{{ matchPercentage }}%</span>
                <span class="score-label">Match</span>
              </div>
            </div>
          </div>

          <div class="matched-skills">
            <p class="skills-count">{{ jobData.skillsMatched }} of {{ jobData.totalSkills }} skills matched</p>

            <div class="skills-tags">
              <span v-for="skill in jobData.requiredSkills" :key="skill" class="skill-tag" :class="{ matched: isSkillMatched(skill) }">
                {{ skill }}
                <svg v-if="isSkillMatched(skill)" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </span>
            </div>
          </div>
        </div>

        <!-- Company Details -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">About Company</h3></div>
          <div class="company-details">
            <p>{{ jobData.companyAbout }}</p>

            <div class="company-stats">
              <div class="stat-item">
                <span class="stat-label">Industry</span>
                <span class="stat-value">{{ jobData.industry }}</span>
              </div>

              <div class="stat-item">
                <span class="stat-label">Company Size</span>
                <span class="stat-value">{{ jobData.companySize }}</span>
              </div>

              <div class="stat-item">
                <span class="stat-label">Website</span>
                <a :href="jobData.companyWebsite" target="_blank" class="stat-link">Visit Website</a>
              </div>
            </div>
          </div>
        </div>

        <!-- Job Details -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Job Details</h3></div>
          <div class="job-details-list">
            <div class="detail-row"><span class="detail-label">Job Type</span><span class="detail-value">{{ jobData.jobType }}</span></div>
            <div class="detail-row"><span class="detail-label">Work Mode</span><span class="detail-value">{{ jobData.workMode }}</span></div>
            <div class="detail-row"><span class="detail-label">Experience</span><span class="detail-value">{{ jobData.experience }}</span></div>
            <div class="detail-row"><span class="detail-label">Openings</span><span class="detail-value">{{ jobData.openings }}</span></div>
            <div class="detail-row"><span class="detail-label">Applicants</span><span class="detail-value">{{ jobData.applicants }}</span></div>
            <div class="detail-row"><span class="detail-label">Deadline</span><span class="detail-value">{{ jobData.deadline || '—' }}</span></div>
          </div>
        </div>

        <!-- Contact -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Contact Information</h3></div>
          <div class="contact-info">
            <div class="contact-item"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg><span>{{ jobData.contactEmail || '—' }}</span></div>

            <div class="contact-item"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg><span>{{ jobData.contactPhone || '—' }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Apply Modal -->
    <div v-if="showApplyModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Apply for {{ jobData.position }}</h2>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Select Resume</label>
            <select v-model="applicationData.resume_filename" class="form-select">
              <option value="">Choose a resume</option>
              <option v-for="r in candidateResumes" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <p v-if="candidateResumes.length === 0" class="note">No resume found in your profile. Upload one from your profile page first.</p>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">Cancel</button>
          <button class="btn-submit" @click="submitApplication">Submit Application</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Small loading fallback -->
  <div v-if="loading" class="loading-box">Loading job details...</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useStore } from "vuex"
import api from "@/services/api" // uses axios instance; keep for fallback calls

const router = useRouter()
const route = useRoute()
const store = useStore()

const BASE_URL = "http://127.0.0.1:8086"
const jobId = route.params.id

const jobData = ref(null)
const loading = ref(true)
const error = ref(null)

const hasApplied = ref(false)
const showApplyModal = ref(false)

// application payload uses resume filename as backend expects
const applicationData = ref({
  resume_filename: "",
})

// candidate resumes derived from applicant profile in store
const candidateResumes = computed(() => {
  const profile = store.getters["applicant/profile"]
  if (!profile) return []
  // backend profile.resume might be object or null
  const list = []
  if (profile.resume && profile.resume.filename) {
    list.push(profile.resume.filename)
  }
  // if profile has multiple resumes stored in a custom array, include them (defensive)
  if (Array.isArray(profile.resumes)) {
    profile.resumes.forEach(r => { if (r && r.filename) list.push(r.filename) })
  }
  return list
})

// compute applicant skills array
const applicantSkills = computed(() => {
  const profile = store.getters["applicant/profile"]
  return Array.isArray(profile?.skills) ? profile.skills : []
})

// normalize backend response into fields expected by the template
function normalize(resp) {
  if (!resp) return null
  const data = resp

  return {
    position: data.job_title || data.position || "—",
    company: data.company || "—",
    location: data.location || "—",
    experience: data.experience_range || data.experience || "—",
    workMode: data.work_mode || data.workMode || data.work_mode || "—",
    salary: data.basic_salary ? formatSalary(data.basic_salary) : (data.salary || "—"),
    postedDate: typeof data.days_ago_posted !== "undefined" ? `${data.days_ago_posted} days ago` : (data.postedDate || "—"),
    description: data.job_description || data.description || "—",
    responsibilities: data.key_responsibilities || data.responsibilities || [],
    requirements: data.requirements || [],
    requiredSkills: data.required_skills || [],
    skillsMatched: (data.skills_match && typeof data.skills_match.matched !== "undefined") ? data.skills_match.matched : (data.skillsMatched || 0),
    totalSkills: (data.skills_match && typeof data.skills_match.total !== "undefined") ? data.skills_match.total : (data.totalSkills || (data.required_skills ? data.required_skills.length : 0)),
    companyAbout: data.company_info?.description || data.companyAbout || "",
    industry: data.company_info?.industry || data.industry || "",
    companySize: data.company_info?.company_size || data.companySize || "",
    companyWebsite: data.company_info?.website || data.companyWebsite || "",
    jobType: data.employment_type || data.jobType || "—",
    openings: data.num_positions || data.openings || 1,
    applicants: data.total_applicants || data.applicants || 0,
    deadline: data.deadline || null,
    jd_file_url: data.jd_file_url || data.jd_file_url || null,
    contactEmail: data.contact_email || data.contactEmail || null,
    contactPhone: data.contact_phone || data.contactPhone || null,
    raw: data,
  }
}

function formatSalary(value) {
  // backend supplies number string like "5000000.00" — show as "₹5,000,000"
  try {
    const n = Number(value)
    if (Number.isNaN(n)) return value
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n)
  } catch {
    return value
  }
}

// compute match percentage
const matchPercentage = computed(() => {
  if (!jobData.value) return 0
  // if backend included percentage, use it
  if (jobData.value.raw?.skills_match?.percentage !== undefined) {
    return Math.round(jobData.value.raw.skills_match.percentage)
  }
  const total = jobData.value.totalSkills || 0
  if (total === 0) return 0
  return Math.round((jobData.value.skillsMatched / total) * 100)
})

const calculateOffset = (percentage) => {
  const circumference = 2 * Math.PI * 54
  return circumference - (percentage / 100) * circumference
}

const getCompanyInitials = (company = "") => {
  if (!company) return "NA"
  return company.split(" ").map(s => s[0] || '').slice(0,2).join('').toUpperCase()
}

const isSkillMatched = (skill) => {
  return applicantSkills.value.includes(skill)
}

// fetch using store action if available, otherwise fallback to direct call
const fetchJobDetails = async () => {
  loading.value = true
  error.value = null
  try {
    // ensure profile exists — try to fetch if not present
    if (!store.getters["applicant/profile"]) {
      // don't await — but attempt to fetch profile for resumes/skills
      try { store.dispatch("applicant/fetchProfile") } catch (_) {}
    }

    // prefer store action
    if (store._actions && store._actions["applicant/fetchJobDetails"]) {
      const res = await store.dispatch("applicant/fetchJobDetails", jobId)
      jobData.value = normalize(res)
    } else {
      // fallback: direct API call
      const applicantId = store.state.applicant.applicant_id || store.state.auth?.currentUser?.applicant_id
      const resp = await api.get(`/job/detail/${jobId}/${applicantId}`)
      jobData.value = normalize(resp.data)
    }

    // check hasApplied flag from backend raw response (if present)
    if (jobData.value?.raw?.has_applied !== undefined) {
      hasApplied.value = !!jobData.value.raw.has_applied
    } else {
      hasApplied.value = false
    }
  } catch (err) {
    console.error("fetchJobDetails error:", err)
    error.value = err.response?.data?.message || "Failed to load job details"
  } finally {
    loading.value = false
  }
}

const downloadJD = () => {
  let href

  if (jobData.value?.jd_file_url) {
    href = jobData.value.jd_file_url.startsWith("http")
      ? jobData.value.jd_file_url
      : `${BASE_URL}${jobData.value.jd_file_url}`
  } else {
    // make fallback match backend
    href = `${BASE_URL}/jobs/download_jd/${jobId}`
  }

  const a = document.createElement("a")
  a.href = href
  a.setAttribute("download", "")
  document.body.appendChild(a)
  a.click()
  a.remove()
}

const applyForJob = () => {
  if (hasApplied.value) return
  showApplyModal.value = true
}

const closeModal = () => {
  showApplyModal.value = false
  applicationData.value.resume_filename = ""
}

const submitApplication = async () => {
  if (!applicationData.value.resume_filename) {
    alert("Please select a resume")
    return
  }

  try {
    // use store action if present
    if (store._actions && store._actions["applicant/applyForJobCorrected"]) {
      await store.dispatch("applicant/applyForJobCorrected", {
        jobId: Number(jobId),
        resumeFilename: applicationData.value.resume_filename,
      })
    } else {
      const applicantId = store.state.applicant.applicant_id || store.state.auth?.currentUser?.applicant_id
      await api.post(`/applications/apply`, {
        applicant_id: applicantId,
        job_id: Number(jobId),
        resume_filename: applicationData.value.resume_filename,
      })
    }

    alert("Application submitted!")
    hasApplied.value = true
    closeModal()
  } catch (err) {
    console.error("submitApplication error:", err)
    alert(err.response?.data?.message || "Could not submit application")
  }
}

const goBack = () => router.push("/applicant/jobs")

onMounted(fetchJobDetails)
</script>



<style scoped>
.job-details-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #1e3a5f;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f9fafb;
  border-color: #6366f1;
  color: #6366f1;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-download,
.btn-apply {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-download {
  background: white;
  color: #6366f1;
  border: 1px solid #6366f1;
}

.btn-download:hover {
  background: #6366f1;
  color: white;
}

.btn-apply {
  background: #6366f1;
  color: white;
}

.btn-apply:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-apply:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Card */
.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
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

/* Job Overview */
.job-overview-card {
  padding: 2rem;
}

.company-header {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.company-logo {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.company-info {
  flex: 1;
}

.job-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.company-name {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0 0 1rem 0;
  font-weight: 500;
}

.job-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

.meta-divider {
  color: #cbd5e1;
}

.salary-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #dcfce7;
  color: #166534;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
}

.posted-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Job Description */
.job-description p {
  color: #475569;
  line-height: 1.8;
  margin: 0;
}

/* Lists */
.responsibilities-list,
.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.responsibilities-list li,
.requirements-list li {
  padding-left: 2rem;
  position: relative;
  color: #475569;
  line-height: 1.6;
}

.responsibilities-list li::before,
.requirements-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  width: 24px;
  height: 24px;
  background: #eff6ff;
  color: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

/* Skills Match */
.match-score {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.score-progress {
  transform: rotate(-90deg);
}

.score-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 8;
}

.score-fill {
  fill: none;
  stroke: #6366f1;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 339.292;
  transition: stroke-dashoffset 0.5s ease;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
}

.score-label {
  display: block;
  font-size: 0.85rem;
  color: #64748b;
}

.matched-skills {
  text-align: center;
}

.skills-count {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0 0 1rem 0;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.skill-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #e2e8f0;
}

.skill-tag.matched {
  background: #dcfce7;
  color: #166534;
  border-color: #10b981;
}

/* Company Details */
.company-details p {
  color: #475569;
  line-height: 1.8;
  margin: 0 0 1.5rem 0;
}

.company-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  font-size: 0.9rem;
  color: #1e3a5f;
  font-weight: 600;
}

.stat-link {
  font-size: 0.9rem;
  color: #6366f1;
  font-weight: 600;
  text-decoration: none;
}

.stat-link:hover {
  text-decoration: underline;
}

/* Job Details List */
.job-details-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 0.9rem;
  color: #1e3a5f;
  font-weight: 600;
}

/* Contact Info */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #475569;
  font-size: 0.9rem;
}

.contact-item svg {
  color: #6366f1;
  flex-shrink: 0;
}

/* Modal */
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
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
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e3a5f;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
  margin-bottom: 0.5rem;
}

.form-select,
.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  resize: vertical;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f1f5f9;
  color: #1e3a5f;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-submit {
  background: #6366f1;
  color: white;
}

.btn-submit:hover {
  background: #4f46e5;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .job-details-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-download,
  .btn-apply {
    width: 100%;
    justify-content: center;
  }

  .company-header {
    flex-direction: column;
    text-align: center;
  }

  .job-title {
    font-size: 1.5rem;
  }

  .job-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .card {
    padding: 1rem;
  }
}
</style>
