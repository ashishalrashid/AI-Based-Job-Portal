<template>
  <div class="resume-container">
    <div class="resume-card">
      <h2 class="page-title">Candidate Resume Review</h2>

      <div class="resume-grid">
        <!-- Left Box: Candidate Details -->
        <div class="details-box">
          <h3 class="box-title">Candidate Details</h3>
          <div class="details-content">
            <p><strong>CID:</strong> {{ candidate.cid }}</p>
            <p><strong>First Name:</strong> {{ candidate.firstName }}</p>
            <p><strong>Last Name:</strong> {{ candidate.lastName }}</p>
            <p><strong>Role:</strong> {{ candidate.role }}</p>
            <p><strong>Email:</strong> {{ candidate.email }}</p>
            <p><strong>Phone:</strong> {{ candidate.phone }}</p>
          </div>
        </div>

        <!-- Right Box: Overview + AI Score -->
        <div class="overview-box">
          <h3 class="box-title">Overview & AI Evaluation</h3>
          <div class="overview-content">
            <p class="overview-text">
              {{ candidate.overview }}
            </p>
            <div class="ai-score">
              <p class="ai-score-label">AI Match Score</p>
              <p class="ai-score-value">{{ candidate.aiScore }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="button-group">
        <button class="back-btn" @click="goBack">← Back to All Candidates</button>
        <button class="schedule-btn" @click="goToScheduleInterview">Schedule Interview</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'

const router = useRouter()
const route = useRoute()
const store = useStore()

// application_id coming from route like: /hr/candidate/5
const applicationId = route.params.id

const candidate = ref(null)
const loading = ref(true)

// Fetch candidate info from backend
onMounted(async () => {
  try {
    const data = await store.dispatch("hr/fetchCandidateProfile", applicationId)

    // Normalizing for UI
    candidate.value = {
      cid: data.applicant_id,
      firstName: data.name || "",
      lastName: "",
      role: data.role || "",
      email: data.email,
      phone: data.phone,
      aiScore: data.ai_match_score ? `${data.ai_match_score}%` : "-",
      overview: data.summary || "No overview available",
    }

  } catch (err) {
    console.error("Failed to load candidate:", err)
  } finally {
    loading.value = false
  }
})

// Navigation
function goBack() {
  router.push('/hr/shortlisted-candidates')
}

function goToScheduleInterview() {
  router.push({
    path: '/hr/interview-slots',
    query: {
      cid: candidate.value.cid,
      role: candidate.value.role,
      application_id: applicationId,
    },
  })
}
</script>


<style scoped>
.resume-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--background);
  color: var(--text);
  padding-top: 60px;
}

.resume-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 1100px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--primary);
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 2rem;
}

.resume-grid {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
}

.details-box,
.overview-box {
  flex: 1;
  min-width: 400px;
  background: var(--background);
  border: 1px solid var(--primary);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.box-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--secondary);
  margin-bottom: 1rem;
}

.details-content p {
  margin: 0.5rem 0;
  font-size: 1rem;
  color: var(--text);
}

.overview-content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  gap: 2rem;
}

.overview-text {
  flex: 3;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text);
  margin: 0;
}

.ai-score {
  flex: 1;
  text-align: right;
}

.ai-score-value {
  font-size: 4rem;
  font-weight: 800;
  color: var(--primary);
  margin: 0;
}

.ai-score-label {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text);
  opacity: 0.8;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
}

.back-btn,
.schedule-btn {
  background: var(--primary);
  color: var(--surface);
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover,
.schedule-btn:hover {
  background: var(--secondary);
  color: black;
}
</style>
