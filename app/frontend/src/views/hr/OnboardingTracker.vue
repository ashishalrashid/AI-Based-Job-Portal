<template>
  <div class="onboarding-container">
    <div class="onboarding-card">
      <h1 class="title">Onboarding Tracker</h1>
      <p class="subtitle">
        <strong>Job Requisition ID:</strong> JR-1042 | <strong>Job Posting Name:</strong> Frontend
        Developer
      </p>

      <div v-if="loading" class="loading">Loading onboarding data...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="candidates.length === 0" class="empty-state">
        <p>No onboarding records found</p>
      </div>
      <table v-else class="tracker-table">
        <thead>
          <tr>
            <th>Candidate ID</th>
            <th>Candidate Details</th>
            <th>Offer Acceptance</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="candidate in candidates" :key="candidate.id">
            <td>{{ candidate.id }}</td>
            <td>{{ candidate.details }}</td>
            <td>
              <span
                class="status"
                :class="{
                  accepted: candidate.status === 'Accepted',
                  pending: candidate.status === 'Pending',
                  rejected: candidate.status === 'Rejected',
                }"
              >
                {{ candidate.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

const store = useStore()

// Get company_id from user context
const hrUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
const companyId = hrUser?.company_id

const candidates = ref([])
const loading = ref(true)
const error = ref(null)

const loadOnboardings = async () => {
  if (!companyId) {
    error.value = 'Company ID not found'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    const res = await api.get('/onboarding')
    const allOnboardings = Array.isArray(res.data) ? res.data : []
    
    // Filter by company_id and transform to match template
    candidates.value = allOnboardings
      .filter(ob => (ob.company_id || ob.companyId) === companyId)
      .map(ob => ({
        id: ob.id || ob.onboarding_id || `OB-${ob.candidate_id || 'N/A'}`,
        details: `${ob.candidate_name || 'Unknown'} – ${ob.contact_email || ob.email || 'N/A'}`,
        status: ob.status === 'accepted' ? 'Accepted' : 
                ob.status === 'rejected' ? 'Rejected' : 
                'Pending'
      }))
  } catch (err) {
    console.error('Failed to load onboardings:', err)
    error.value = 'Failed to load onboarding data'
    candidates.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadOnboardings)
</script>

<style scoped>
.onboarding-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding-top: 80px; /* avoids navbar overlap */
  background-color: var(--background);
  color: var(--text);
}

.onboarding-card {
  background-color: var(--surface);
  padding: 2rem;
  border-radius: 12px;
  width: 80%;
  max-width: 900px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 1.5rem;
}

.tracker-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  background-color: var(--surface);
  color: var(--text);
}

.tracker-table th,
.tracker-table td {
  border: 1px solid var(--primary);
  padding: 12px 16px;
}

.tracker-table th {
  background-color: var(--primary);
  color: white;
}

.status {
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
}

.accepted {
  background-color: #28a745;
  color: white;
}

.pending {
  background-color: #ffc107;
  color: black;
}

.rejected {
  background-color: #dc3545;
  color: white;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text);
}

.error {
  color: #dc3545;
}

.empty-state {
  color: #6c757d;
}
</style>
