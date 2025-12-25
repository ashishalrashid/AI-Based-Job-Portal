<template>
  <div class="interview-offer-table">
    <div class="table-header">
      <h2>📋 Interview Results - Selected Candidates (Ready for Offer Letters)</h2>
      <div class="table-actions">
        <button
          @click="sendBulkOffers"
          :disabled="!selectedCandidates.length"
          class="bulk-send-btn"
        >
          📤 Send Selected Offers ({{ selectedCandidates.length }})
        </button>
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          🔄 Refresh
        </button>
        <a href="http://localhost:1080" target="_blank" class="maildev-link">
          📧 View MailDev
        </a>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading interview results...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <button @click="refreshData" class="retry-btn">Try Again</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="!interviewData.length" class="empty-state">
      <p>📭 No candidates with selected interview results found</p>
      <p class="hint">Candidates who have completed interviews with "selected" status will appear here.</p>
    </div>

    <!-- Interview Results Table -->
    <div v-else class="table-container">
      <table class="interview-table">
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                @change="toggleSelectAll"
                :checked="selectedCandidates.length === interviewData.length && interviewData.length > 0"
                :indeterminate="selectedCandidates.length > 0 && selectedCandidates.length < interviewData.length"
              />
              Candidate
            </th>
            <th>Position</th>
            <th>Interview Stage</th>
            <th>Interview Date</th>
            <th>Interviewer</th>
            <th>Result</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in interviewData"
            :key="item.interview_id"
            :class="{ 'sending': sendingId === item.application_id }"
          >
            <td class="candidate-cell">
              <div class="candidate-info">
                <input
                  type="checkbox"
                  :value="item.application_id"
                  v-model="selectedCandidates"
                  class="candidate-checkbox"
                />
                <strong>{{ item.candidate_name }}</strong>
                <div class="candidate-email">{{ item.email }}</div>
                <div class="candidate-id">ID: {{ item.candidate_id }}</div>
              </div>
            </td>

            <td>
              <div class="job-info">
                <div>{{ item.job_title }}</div>
                <div class="salary">{{ item.basic_salary }} LPA</div>
              </div>
            </td>

            <td>
              <span class="stage-badge" :class="item.interview_stage">
                {{ item.interview_stage || 'N/A' }}
              </span>
            </td>

            <td>
              <div class="interview-date">
                <div>{{ formatDate(item.interview_date) }}</div>
                <div class="time-slot" v-if="item.slot_start_time">
                  {{ item.slot_start_time }} - {{ item.slot_end_time }}
                </div>
              </div>
            </td>

            <td>{{ item.interviewer_name }}</td>

            <td>
              <span class="result-badge selected">
                ✅ Selected
              </span>
            </td>

            <td class="actions-cell">
              <button
                @click="sendOffer(item.application_id)"
                :disabled="sendingId === item.application_id"
                class="send-offer-btn"
                :class="{
                  'success': emailStatus[item.application_id] === 'success',
                  'error': emailStatus[item.application_id] === 'error'
                }"
              >
                <span v-if="sendingId === item.application_id">⏳ Sending...</span>
                <span v-else-if="emailStatus[item.application_id] === 'success'">✅ Sent</span>
                <span v-else-if="emailStatus[item.application_id] === 'error'">❌ Failed</span>
                <span v-else>📄 Send Offer</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Statistics -->
    <div v-if="interviewData.length" class="statistics">
      <div class="stat-item">
        <span class="stat-number">{{ interviewData.length }}</span>
        <span class="stat-label">Selected Candidates</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ sentCount }}</span>
        <span class="stat-label">Offers Sent</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ uniqueStages }}</span>
        <span class="stat-label">Interview Stages</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getEligibleCandidates, sendOfferLetter } from '../../services/api.js'

export default {
  name: 'EligibleCandidates',
  data() {
    return {
      interviewData: [], // Changed from candidates to interviewData
      loading: false,
      error: null,
      sendingId: null,
      emailStatus: {}, // { [applicationId]: 'success' | 'error' }
      companyId: null,
      selectedCandidates: [] // Array of selected application_ids
    }
  },
  computed: {
    sentCount() {
      return Object.values(this.emailStatus).filter(status => status === 'success').length
    },
    uniqueStages() {
      const stages = [...new Set(this.interviewData.map(item => item.interview_stage))];
      return stages.length;
    }
  },
  mounted() {
    this.loadCompanyId()
    this.refreshData()
  },
  methods: {
    async loadCompanyId() {
      // Get company ID from user session or props
      // For now, using a default or from localStorage
      this.companyId = localStorage.getItem('hr_company_id') || 1
    },

    async refreshData() { // Changed from refreshCandidates
      this.loading = true
      this.error = null

      try {
        const response = await getEligibleCandidates(this.companyId)
        this.interviewData = response.data || []
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to load interview data'
        console.error('Error loading interview data:', error)
      } finally {
        this.loading = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    async sendOffer(applicationId) {
      this.sendingId = applicationId

      try {
        const response = await sendOfferLetter(applicationId)

        if (response.status === 'success' || response.status === 200) {
          this.emailStatus[applicationId] = 'success'
          this.$emit('offer-sent', { applicationId, status: 'success' })
        } else {
          this.emailStatus[applicationId] = 'error'
          this.$emit('offer-sent', { applicationId, status: 'error' })
        }
      } catch (error) {
        console.error('Error sending offer:', error)
        this.emailStatus[applicationId] = 'error'
        this.$emit('offer-sent', {
          applicationId,
          status: 'error',
          error: error.response?.data?.message || 'Unknown error'
        })
      } finally {
        this.sendingId = null
      }
    },

    toggleSelectAll(event) {
      if (event.target.checked) {
        this.selectedCandidates = this.interviewData.map(item => item.application_id)
      } else {
        this.selectedCandidates = []
      }
    },

    async sendBulkOffers() {
      if (this.selectedCandidates.length === 0) {
        alert('Please select candidates to send offers to.')
        return
      }

      const confirmMessage = `Send offer letters to ${this.selectedCandidates.length} selected candidate(s)?`
      if (!confirm(confirmMessage)) {
        return
      }

      // Set all selected candidates as sending
      this.selectedCandidates.forEach(id => {
        this.emailStatus[id] = 'sending'
      })

      try {
        // For now, send offers individually. In the future, we could implement a bulk API
        const promises = this.selectedCandidates.map(id => this.sendOffer(id))
        await Promise.allSettled(promises)

        const successCount = this.selectedCandidates.filter(id => this.emailStatus[id] === 'success').length
        const errorCount = this.selectedCandidates.filter(id => this.emailStatus[id] === 'error').length

        alert(`Bulk send completed!\nSuccess: ${successCount}\nFailed: ${errorCount}`)
      } catch (error) {
        console.error('Error in bulk send:', error)
        alert('Error occurred during bulk send operation.')
      }
    }
  }
}
</script>

<style scoped>
.interview-offer-table {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8f9fa;
  min-height: 100vh;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 25px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.bulk-send-btn, .refresh-btn, .maildev-link {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  font-weight: 500;
}

.bulk-send-btn {
  background-color: #8e44ad;
  color: white;
}

.bulk-send-btn:hover:not(:disabled) {
  background-color: #732d91;
  transform: translateY(-2px);
}

.bulk-send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #bdc3c7;
}

.refresh-btn {
  background-color: #3498db;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.maildev-link {
  background-color: #27ae60;
  color: white;
}

.maildev-link:hover {
  background-color: #229954;
  transform: translateY(-2px);
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.interview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.interview-table thead {
  background: #f8f9fa;
}

.interview-table th {
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
  position: sticky;
  top: 0;
  background: #f8f9fa;
}

.interview-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: top;
}

.interview-table tbody tr {
  transition: all 0.2s ease;
}

.interview-table tbody tr:hover {
  background-color: #f8f9fa;
}

.interview-table tbody tr.sending {
  background-color: #fefbf3;
  border-left: 4px solid #f39c12;
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

.candidate-checkbox {
  margin-right: 8px;
  transform: scale(1.2);
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

.salary {
  color: #6c757d;
  font-size: 13px;
}

.stage-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.stage-badge.technical {
  background: #e3f2fd;
  color: #1976d2;
}

.stage-badge.hr {
  background: #f3e5f5;
  color: #7b1fa2;
}

.stage-badge.final {
  background: #fff3e0;
  color: #f57c00;
}

.interview-date div:first-child {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
}

.time-slot {
  color: #6c757d;
  font-size: 13px;
}

.result-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.result-badge.selected {
  background: #d4edda;
  color: #155724;
}

.actions-cell {
  text-align: center;
  min-width: 120px;
}

.send-offer-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
  white-space: nowrap;
}

.send-offer-btn:not(:disabled):hover {
  transform: translateY(-1px);
}

.send-offer-btn.success {
  background-color: #27ae60;
  color: white;
}

.send-offer-btn.error {
  background-color: #e74c3c;
  color: white;
}

.send-offer-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.statistics {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 30px;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .interview-table {
    font-size: 13px;
  }

  .interview-table th,
  .interview-table td {
    padding: 12px 8px;
  }
}

@media (max-width: 768px) {
  .interview-offer-table {
    padding: 15px;
  }

  .table-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
    padding: 20px;
  }

  .table-header h2 {
    font-size: 20px;
  }

  .table-actions {
    flex-direction: column;
    width: 100%;
  }

  .refresh-btn, .maildev-link {
    width: 100%;
    text-align: center;
  }

  .interview-table {
    font-size: 12px;
  }

  .candidate-cell {
    min-width: 150px;
  }

  .actions-cell {
    min-width: 100px;
  }

  .statistics {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .interview-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .interview-table th,
  .interview-table td {
    min-width: 120px;
  }
}
</style>
