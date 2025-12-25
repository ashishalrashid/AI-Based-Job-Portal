<template>
  <div class="offer-letter-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Offer Letter Editor</h1>
      <p class="page-subtitle">Create and send offer letters to selected candidates</p>
    </div>

    <!-- Candidates Table (if not pre-selected) -->
    <div v-if="!candidateId" class="candidates-table-card">
      <h3>Selected Candidates - Ready for Offer Letters</h3>
      <div v-if="loadingCandidates" class="loading">Loading candidates...</div>
      <div v-else-if="candidatesError" class="error">{{ candidatesError }}</div>
      <div v-else-if="!eligibleCandidates.length" class="empty-state">
        <p>No candidates with selected interview results found</p>
        <p class="hint">Candidates who have completed interviews with "selected" status will appear here.</p>
      </div>
      <div v-else class="table-container">
        <table class="candidates-table">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Position</th>
              <th>Interview Date</th>
              <th>Salary</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="candidate in eligibleCandidates" :key="candidate.id">
              <td class="candidate-cell">
                <div class="candidate-info">
                  <strong>{{ candidate.firstName }} {{ candidate.lastName }}</strong>
                  <div class="candidate-email">{{ candidate.email }}</div>
                  <div class="candidate-id">ID: {{ candidate.id }}</div>
                </div>
              </td>
              <td>
                <div class="job-info">
                  <div>{{ candidate.role }}</div>
                </div>
              </td>
              <td>
                <div class="interview-date">
                  <div>Interview Completed</div>
                  <div class="status-badge">Selected</div>
                </div>
              </td>
              <td>
                <div class="salary-info">
                  {{ candidate.salary ? `₹${candidate.salary}` : 'Not specified' }}
                </div>
              </td>
              <td class="actions-cell">
                <button
                  @click="selectCandidate(candidate.id)"
                  class="create-offer-btn"
                >
                  📝 Create Offer
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Offer Letter Editor -->
    <div v-if="selectedCandidateId || candidateId" class="editor-card">
      <!-- Editor Content -->
      <div class="editor-header">
        <h3>Candidate: {{ currentCandidate.firstName }} {{ currentCandidate.lastName }}</h3>
        <span class="role-badge">{{ currentCandidate.role }}</span>
      </div>

      <!-- Offer Letter Form -->
      <div class="offer-form">
        <div class="form-group">
          <label>Position <span class="required">*</span></label>
          <input v-model="offerData.position" type="text" class="form-input" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Annual Salary <span class="required">*</span></label>
            <input v-model="offerData.salary" type="text" class="form-input" />
          </div>

          <div class="form-group">
            <label>Start Date <span class="required">*</span></label>
            <input v-model="offerData.startDate" type="date" class="form-input" />
          </div>
        </div>

        <div class="form-group">
          <label>Department</label>
          <input v-model="offerData.department" type="text" class="form-input" />
        </div>

        <div class="form-group">
          <label>Work Mode</label>
          <select v-model="offerData.workMode" class="form-input">
            <option>Remote</option>
            <option>Hybrid</option>
            <option>On-site</option>
          </select>
        </div>

        <div class="form-group">
          <label>Additional Benefits</label>
          <textarea v-model="offerData.benefits" rows="4" class="form-textarea"></textarea>
        </div>

        <div class="form-group">
          <label>Offer Validity</label>
          <input v-model="offerData.validUntil" type="date" class="form-input" />
        </div>
      </div>

      <!-- Preview Section -->
      <div class="offer-preview">
        <h3>Offer Letter Preview</h3>
        <div class="preview-content">
          <div class="letter-header">
            <h2>{{ companyName }}</h2>
            <p>{{ companyAddress }}</p>
          </div>

          <div class="letter-body">
            <p class="date">Date: {{ formatDate(new Date()) }}</p>

            <p class="greeting">Dear {{ currentCandidate.firstName }},</p>

            <p>
              We are pleased to offer you the position of
              <strong>{{ offerData.position }}</strong> at {{ companyName }}.
            </p>

            <h4>Position Details:</h4>
            <ul>
              <li><strong>Position:</strong> {{ offerData.position }}</li>
              <li><strong>Department:</strong> {{ offerData.department }}</li>
              <li><strong>Annual Salary:</strong> ₹{{ offerData.salary }} </li>
              <li><strong>Start Date:</strong> {{ formatDate(offerData.startDate) }}</li>
              <li><strong>Work Mode:</strong> {{ offerData.workMode }}</li>
            </ul>

            <h4>Benefits:</h4>
            <p>{{ offerData.benefits }}</p>

            <p class="validity">
              This offer is valid until {{ formatDate(offerData.validUntil) }}.
            </p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="goBack" class="btn-secondary">Cancel</button>
        <button @click="saveAsDraft" class="btn-outline">Save as Draft</button>
        <button @click="sendOffer" class="btn-primary">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
          Send Offer Letter
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getEligibleCandidates, sendOfferLetter } from '@/services/api'

const router = useRouter()
const route = useRoute()

// Props from route params
const candidateId = ref(route.params.candidateId || null)
const selectedCandidateId = ref(candidateId.value)

// Company Info
const companyName = ref('JobShalah')
const companyAddress = ref('Bangalore, Karnataka, India')

// Eligible candidates (fetched from API)
const eligibleCandidates = ref([])
const loadingCandidates = ref(false)
const candidatesError = ref(null)

// Offer Data
const offerData = ref({
  position: '',
  salary: '',
  startDate: '',
  department: 'Engineering',
  workMode: 'Hybrid',
  benefits: 'Health insurance, Performance bonuses, Flexible hours, Professional development',
  validUntil: '',
})

// Current candidate
const currentCandidate = computed(() => {
  const id = selectedCandidateId.value || candidateId.value
  return eligibleCandidates.value.find((c) => c.id == id) || {}
})

// Load candidate data and fetch eligible candidates
onMounted(async () => {
  await fetchEligibleCandidates()
  if (candidateId.value) {
    loadCandidateData(candidateId.value)
  }
})

// Fetch eligible candidates from API
const fetchEligibleCandidates = async () => {
  loadingCandidates.value = true
  candidatesError.value = null

  try {
    // Get company_id from user context
    const hrUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    const companyId = hrUser?.company_id

    if (!companyId) {
      candidatesError.value = 'Company ID not found. Please log in again.'
      return
    }

    const response = await getEligibleCandidates(companyId)
    const candidates = response.data

    // Transform API response to match component expectations
    eligibleCandidates.value = candidates.map(candidate => ({
      id: candidate.application_id,  // Use application_id as the unique identifier
      firstName: candidate.candidate_name ? candidate.candidate_name.split(' ')[0] || '' : '',
      lastName: candidate.candidate_name ? candidate.candidate_name.split(' ').slice(1).join(' ') || '' : '',
      role: candidate.job_title,
      status: 'Interview Done',
      email: candidate.email,
      location: candidate.location,
      salary: candidate.basic_salary
    }))
  } catch (error) {
    candidatesError.value = 'Failed to load candidates'
    console.error('Error fetching eligible candidates:', error)
  } finally {
    loadingCandidates.value = false
  }
}

const selectCandidate = (candidateId) => {
  selectedCandidateId.value = candidateId
  loadCandidateData(candidateId)
}

const loadCandidateData = (id) => {
  // Pre-fill offer data based on candidate
  const candidate = eligibleCandidates.value.find((c) => c.id == id)
  if (candidate) {
    offerData.value.position = candidate.role
    offerData.value.salary = candidate.salary || ''
    // Set default validity to 15 days from now
    const validity = new Date()
    validity.setDate(validity.getDate() + 15)
    offerData.value.validUntil = validity.toISOString().split('T')[0]
  }
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const goBack = () => {
  if (candidateId.value) {
    // If we came from a specific candidate route, go back to candidates list
    router.push('/hr/eligible-candidates')
  } else {
    // If we were in the general editor, reset selection to show table again
    selectedCandidateId.value = null
    offerData.value = {
      position: '',
      salary: '',
      startDate: '',
      department: 'Engineering',
      workMode: 'Hybrid',
      benefits: 'Health insurance, Performance bonuses, Flexible hours, Professional development',
      validUntil: '',
    }
  }
}

const saveAsDraft = () => {
  alert('Offer letter saved as draft!')
  console.log('Draft saved:', offerData.value)
}

const sendOffer = async () => {
  // Validate required fields
  if (!offerData.value.position || !offerData.value.salary || !offerData.value.startDate) {
    alert('Please fill all required fields: Position, Salary, and Start Date!')
    return
  }

  const appId = selectedCandidateId.value || candidateId.value
  if (!appId) {
    alert('No candidate selected!')
    return
  }

  try {
    // Prepare data for API call
    const payload = {
      salary: offerData.value.salary,
      position: offerData.value.position,
      start_date: offerData.value.startDate,
      department: offerData.value.department,
      work_mode: offerData.value.workMode,
      benefits: offerData.value.benefits,
      valid_until: offerData.value.validUntil
    }

    // API call to send offer
    await sendOfferLetter(appId, payload)

    alert(`Offer letter sent to ${currentCandidate.value.firstName} ${currentCandidate.value.lastName}!`)
    router.push('/hr/shortlisted-candidates')
  } catch (error) {
    console.error('Error sending offer:', error)
    alert('Failed to send offer letter. Please try again.')
  }
}
</script>

<style scoped>
.offer-letter-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 2rem;
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

.candidates-table-card,
.candidate-selector-card,
.editor-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.candidates-table thead {
  background: #f8f9fa;
}

.candidates-table th {
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
}

.candidates-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: top;
}

.candidates-table tbody tr {
  transition: all 0.2s ease;
}

.candidates-table tbody tr:hover {
  background-color: #f8f9fa;
}

.candidate-cell {
  min-width: 200px;
}

.candidate-info strong {
  display: block;
  color: #2c3e50;
  font-size: 16px;
  margin-bottom: 4px;
}

.candidate-email {
  color: #6c757d;
  font-size: 13px;
  margin-bottom: 2px;
}

.candidate-id {
  font-size: 11px;
  color: #adb5bd;
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

.job-info div:first-child {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  background: #d4edda;
  color: #155724;
}

.salary-info {
  font-weight: 500;
  color: #2c3e50;
}

.create-offer-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #3498db;
  color: white;
}

.create-offer-btn:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  color: #6c757d;
  margin-bottom: 10px;
}

.empty-state .hint {
  color: #adb5bd;
  font-size: 14px;
}

.candidate-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  margin-top: 1rem;
}

.loading {
  color: #64748b;
  font-style: italic;
  padding: 1rem;
  text-align: center;
}

.error {
  color: #e74c3c;
  background: #fef2f2;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
  margin-top: 1rem;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.role-badge {
  padding: 0.5rem 1rem;
  background: #eff6ff;
  color: #0369a1;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.offer-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
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

.required {
  color: #e74c3c;
  font-weight: bold;
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.offer-preview {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.offer-preview h3 {
  margin-bottom: 1rem;
  color: #1e3a5f;
}

.preview-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
}

.letter-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #6366f1;
}

.letter-body {
  line-height: 1.8;
  color: #475569;
}

.letter-body h4 {
  margin-top: 1.5rem;
  color: #1e3a5f;
}

.letter-body ul {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary,
.btn-outline {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #6366f1;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: #f1f5f9;
  color: #64748b;
  border: none;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-outline {
  background: white;
  color: #6366f1;
  border: 1px solid #6366f1;
}

.btn-outline:hover {
  background: #eff6ff;
}

@media (max-width: 768px) {
  .offer-letter-page {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
