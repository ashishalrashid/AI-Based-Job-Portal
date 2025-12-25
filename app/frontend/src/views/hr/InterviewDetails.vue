<template>
  <div class="interview-evaluation-page">
    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading evaluation...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <h2>⚠️ Error</h2>
      <p>{{ error }}</p>
      <button class="back-btn" @click="goBack">Back</button>
    </div>

    <!-- Main content -->
    <div v-else>
      <!-- Header -->
      <div class="page-header">
        <button class="back-btn" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
               viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Back
        </button>
        <div class="header-info">
          <h1 class="page-title">Interview Evaluation</h1>
          <div class="interview-meta">
            <span class="meta-item">{{ interviewData.position || 'Position' }}</span>
            <span class="meta-divider">•</span>
            <span class="meta-item">{{ interviewData.round || 'AI Video Interview Round' }}</span>
            <span class="meta-divider">•</span>
            <span class="meta-item">{{ interviewData.date || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Left Column -->
        <div class="left-column">
          <!-- Candidate Info Card -->
          <div class="card candidate-card">
            <div class="candidate-header">
              <div class="candidate-avatar">
                {{ getInitials(interviewData.candidateName) }}
              </div>
              <div class="candidate-info">
                <h2 class="candidate-name">
                  {{ interviewData.candidateName || 'Unknown Candidate' }}
                </h2>
                <p class="candidate-email" v-if="interviewData.candidateEmail">
                  {{ interviewData.candidateEmail }}
                </p>
                <p class="candidate-phone" v-if="interviewData.candidatePhone">
                  {{ interviewData.candidatePhone }}
                </p>
              </div>
            </div>
            <div class="candidate-details">
              <div class="detail-item">
                <span class="detail-label">Experience</span>
                <span class="detail-value">
                  {{ interviewData.experience || 'N/A' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Current Company</span>
                <span class="detail-value">
                  {{ interviewData.currentCompany || 'N/A' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Notice Period</span>
                <span class="detail-value">
                  {{ interviewData.noticePeriod || 'N/A' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Documents: Resume only -->
          <div class="card documents-card">
            <div class="card-header">
              <h3 class="card-title">Documents</h3>
            </div>
            <div class="documents-list">
              <div class="document-item" v-if="interviewData.resumeUrl">
                <div class="doc-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                       viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                </div>
                <span class="doc-name">{{ interviewData.resumeName || 'Resume' }}</span>
                <a
                  class="doc-download"
                  :href="interviewData.resumeUrl"
                  target="_blank"
                  rel="noopener"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                       viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                </a>
              </div>

              <p v-else class="empty-state">No resume attached.</p>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="right-column">
          <!-- Quick Decision Card -->
          <div class="card decision-card">
            <div class="card-header">
              <h3 class="card-title">Quick Decision</h3>
              <span
                :class="['status-badge', getStatusClass(interviewData.status)]"
              >
                {{ interviewData.status || 'Pending' }}
              </span>
            </div>
            <div class="decision-buttons">
              <button class="decision-btn approve-btn" @click="handleDecision('approved')">
                Approve
              </button>
              <button class="decision-btn reject-btn" @click="handleDecision('rejected')">
                Reject
              </button>
              <button class="decision-btn hold-btn" @click="handleDecision('on-hold')">
                On Hold
              </button>
            </div>
          </div>

          <!-- Evaluation Form -->
          <div class="card evaluation-card">
            <div class="card-header">
              <h3 class="card-title">Evaluation</h3>
            </div>
            <div class="evaluation-form">
              <!-- Technical Skills -->
              <div class="rating-section">
                <label class="rating-label">Technical Skills</label>
                <div class="rating-stars">
                  <button
                    v-for="star in 5"
                    :key="'tech-' + star"
                    class="star-btn"
                    :class="{ active: evaluation.technicalSkills >= star }"
                    @click="evaluation.technicalSkills = star"
                  >
                    ★
                  </button>
                </div>
              </div>

              <!-- Communication -->
              <div class="rating-section">
                <label class="rating-label">Communication</label>
                <div class="rating-stars">
                  <button
                    v-for="star in 5"
                    :key="'comm-' + star"
                    class="star-btn"
                    :class="{ active: evaluation.communication >= star }"
                    @click="evaluation.communication = star"
                  >
                    ★
                  </button>
                </div>
              </div>

              <!-- Problem Solving -->
              <div class="rating-section">
                <label class="rating-label">Problem Solving</label>
                <div class="rating-stars">
                  <button
                    v-for="star in 5"
                    :key="'prob-' + star"
                    class="star-btn"
                    :class="{ active: evaluation.problemSolving >= star }"
                    @click="evaluation.problemSolving = star"
                  >
                    ★
                  </button>
                </div>
              </div>

              <!-- Cultural Fit -->
              <div class="rating-section">
                <label class="rating-label">Cultural Fit</label>
                <div class="rating-stars">
                  <button
                    v-for="star in 5"
                    :key="'cult-' + star"
                    class="star-btn"
                    :class="{ active: evaluation.culturalFit >= star }"
                    @click="evaluation.culturalFit = star"
                  >
                    ★
                  </button>
                </div>
              </div>

              <!-- Overall Rating -->
              <div class="overall-rating">
                <span class="overall-label">Overall Rating</span>
                <span class="overall-score">{{ overallRating }}/5.0</span>
                <div class="rating-bar">
                  <div
                    class="rating-fill"
                    :style="{ width: (overallRating / 5) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Key Points to Consider -->
          <div class="card keypoints-card">
            <div class="card-header">
              <h3 class="card-title">Key Points to Consider</h3>
            </div>
            <div class="keypoints-list">
              <div class="keypoint-section">
                <h4 class="keypoint-title">Strengths</h4>
                <ul v-if="interviewData.Strengths && interviewData.Strengths.length">
                  <li v-for="(s, i) in interviewData.Strengths" :key="i">{{ s }}</li>
                </ul>
                <p v-else>No strengths identified</p>
              </div>
              <div class="keypoint-section">
                <h4 class="keypoint-title">Areas of Concern</h4>
                <ul v-if="interviewData.Areasofconcern && interviewData.Areasofconcern.length">
                  <li v-for="(c, i) in interviewData.Areasofconcern" :key="i">{{ c }}</li>
                </ul>
                <p v-else>No concerns identified</p>
              </div>
            </div>
          </div>

          <!-- Interviewer Notes -->
          <div class="card notes-card">
            <div class="card-header">
              <h3 class="card-title">Recommendations</h3>
              <span class="notes-author">By {{ interviewData.interviewer }}</span>
            </div>
            <p class="recommendation-text">
              {{ interviewData.Recommendation }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

const route = useRoute()
const router = useRouter()
const store = useStore()

const sessionId = ref(route.params.interviewId)
const loading = ref(true)
const error = ref(null)

const interviewData = ref({
  id: null,
  candidateName: '',
  candidateEmail: '',
  candidatePhone: '',
  experience: '',
  currentCompany: '',
  noticePeriod: '',
  position: '',
  round: '',
  date: '',
  time: '',
  status: '',
  videoUrl: '',
  documents: [],
  resumeUrl: '',
  resumeName: '',
  Strengths: [],
  Areasofconcern: [],
  Recommendation: '',
  interviewer: 'AI Interviewer'
})

const recordingDuration = ref('--:--')

const evaluation = ref({
  technicalSkills: 0,
  communication: 0,
  problemSolving: 0,
  culturalFit: 0,
  strengths: [],
  areasofconcern: [],
  recommendation: {}
})

const overallRating = computed(() => {
  const e = evaluation.value
  const total =
    (Number(e.technicalSkills) || 0) +
    (Number(e.communication) || 0) +
    (Number(e.problemSolving) || 0) +
    (Number(e.culturalFit) || 0)
  if (!total) return 0
  return Number((total / 4).toFixed(1))
})

const getStatusClass = (status) => {
  const map = {
    completed: 'status-approved',
    pending: 'status-pending',
    scheduled: 'status-pending',
    approved: 'status-approved',
    rejected: 'status-rejected',
    'on-hold': 'status-hold'
  }
  return map[status?.toLowerCase()] || 'status-pending'
}

import api, { getVideoInterviewSession, completeVideoInterview, getVideoInterviewData } from '@/services/api.js'

onMounted(async () => {
  loading.value = true
  try {
    const interviewId = route.params.interviewId
    console.log('🔍 Loading interview #', interviewId)

    // STEP 1: HR list → session_id (✅ PROVEN)
    const hrListRes = await api.get('/api/hr/interviews/1')
    const interview = hrListRes.data.find(i => i.interview_id == interviewId)

    if (!interview) {
      throw new Error(`Interview ${interviewId} not found`)
    }

    console.log('✅ Session found:', interview.session_id, interview.candidate_name)

    // STEP 2: Full data (✅ PROVEN)
    const dataRes = await api.get(`/video-interview/session/${interview.session_id}/data`)
    const data = dataRes.data

    console.log('🎉 FULL DATA:', {
      candidate: data.metadata?.candidate_name,
      rating: data.evaluation?.ratings?.technical_skills?.stars,
      strengths: data.evaluation?.strengths
    })

    // 🔥 FIXED: Populate BOTH evaluation + interviewData
    if (data.evaluation) {
      const evalData = data.evaluation

      // Stars for rating UI
      evaluation.value = {
        technicalSkills: Number(evalData.ratings?.technical_skills?.stars) || 3.0,
        communication: Number(evalData.ratings?.communication?.stars) || 3.0,
        problemSolving: Number(evalData.ratings?.problem_solving?.stars) || 3.0,
        culturalFit: Number(evalData.ratings?.cultural_fit?.stars) || 3.0,
        strengths: evalData.strengths || [],
        areasOfConcern: evalData.areas_of_concern || [],
        recommendation: evalData.recommendation?.decision || 'Review recommended'
      }

      // 🔥 TEMPLATE NEEDS THESE EXACT PROPERTIES:
      interviewData.value.Strengths = evalData.strengths || []
      interviewData.value.Areasofconcern = evalData.areas_of_concern || []
      interviewData.value.Recommendation = evalData.recommendation?.reasoning || 'Review recommended'
    }

    if (data.metadata) {
      // 🔥 MERGE - Keep Strengths/Areas/Rec from above + add metadata
      interviewData.value = {
        ...interviewData.value,  // Keep Strengths/Areas/Rec
        candidateName: data.metadata.candidate_name || interview.candidate_name || 'Candidate',
        position: data.metadata.job_title || interview.job_title || 'Position',
        date: interview.interview_date || 'NA',
        status: 'completed'
      }
    }

    console.log('✅ UI FULLY POPULATED!', {
      strengths: interviewData.value.Strengths,
      areas: interviewData.value.Areasofconcern,
      rec: interviewData.value.Recommendation
    })

  } catch (err) {
    console.error('❌ Error:', err)
    error.value = `Failed to load interview: ${err.message}`
  } finally {
    loading.value = false
  }
})




const getInitials = (name) =>
  name?.split(' ').map((n) => n[0]).join('').toUpperCase() || '?'

const handleDecision = async (decision) => {
  try {
    await store.dispatch('hr/updateInterviewDecision', {
      interviewId: sessionId.value,
      decision
    })
    interviewData.value.status = decision
    alert(`Interview marked as ${decision}`)
  } catch (err) {
    console.error('Failed to update decision:', err)
    alert('Could not update interview status.')
  }
}

const goBack = () => router.push('/hr/interview-slots')
</script>




<style scoped>
.interview-evaluation-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Loading / Error States */
.loading-overlay,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state h2 {
  color: #ef4444;
  margin: 0;
}

.error-state p {
  color: #64748b;
  margin: 0.5rem 0 1rem;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
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

.header-info {
  flex: 1;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.interview-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #64748b;
  font-size: 0.95rem;
}

.meta-item {
  font-weight: 500;
}

.meta-divider {
  color: #cbd5e1;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 450px 1fr;
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

/* Candidate Card */
.candidate-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.candidate-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.candidate-info {
  flex: 1;
}

.candidate-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.candidate-email,
.candidate-phone {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0.25rem 0;
}

.candidate-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
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
  font-size: 0.95rem;
  color: #1e3a5f;
  font-weight: 600;
}

/* Video Card */
.recording-duration {
  font-size: 0.9rem;
  color: #6366f1;
  font-weight: 600;
  background: #eff6ff;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
}

.video-container {
  border-radius: 8px;
  overflow: hidden;
  background: #000;
  aspect-ratio: 16 / 9;
}

.interview-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  gap: 1rem;
}

.video-placeholder p {
  margin: 0;
  font-size: 0.95rem;
}

/* Documents Card */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.document-item:hover {
  background: #f1f5f9;
}

.doc-icon {
  width: 40px;
  height: 40px;
  background: #eff6ff;
  color: #6366f1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-name {
  flex: 1;
  font-size: 0.9rem;
  color: #1e3a5f;
  font-weight: 500;
}

.doc-download {
  background: none;
  border: none;
  color: #6366f1;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.doc-download:hover {
  background: #eff6ff;
}

/* Decision Card */
.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-approved {
  background: #dcfce7;
  color: #166534;
}

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status-hold {
  background: #dbeafe;
  color: #1e40af;
}

.decision-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.decision-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 1rem;
  border: 2px solid;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.approve-btn {
  background: #dcfce7;
  border-color: #10b981;
  color: #166534;
}

.approve-btn:hover {
  background: #10b981;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.reject-btn {
  background: #fee2e2;
  border-color: #ef4444;
  color: #991b1b;
}

.reject-btn:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.hold-btn {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.hold-btn:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Evaluation Form */
.evaluation-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.rating-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rating-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
}

.rating-stars {
  display: flex;
  gap: 0.5rem;
}

.star-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
}

.star-btn:hover,
.star-btn.active {
  color: #fbbf24;
  transform: scale(1.1);
}

.overall-rating {
  margin-top: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
}

.overall-label {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 500;
}

.overall-score {
  font-size: 1.75rem;
  font-weight: 700;
  color: #6366f1;
  margin-left: 0.75rem;
}

.rating-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  margin-top: 1rem;
}

.rating-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
  transition: width 0.3s ease;
}

/* Key Points */
.keypoints-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.keypoint-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.keypoint-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

.keypoint-section ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin: 0;
  color: #475569;
}

.keypoint-section li {
  font-size: 0.9rem;
  margin: 0.25rem 0;
}

.keypoint-section p {
  font-size: 0.9rem;
  color: #94a3b8;
  margin: 0;
}

/* Notes Card */
.notes-author {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.recommendation-text {
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .decision-buttons {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .interview-evaluation-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .card {
    padding: 1rem;
  }
}
</style>

