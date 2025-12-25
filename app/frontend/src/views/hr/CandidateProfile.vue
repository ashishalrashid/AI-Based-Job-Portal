<template>
  <div class="candidate-profile-page">

    <!-- Schedule Interview Modal -->
    <div v-if="showScheduleModal" class="modal-overlay" @click="showScheduleModal = false">
      <div class="modal-container" @click.stop>
        <!-- Modal Header -->
        <div class="modal-header">
          <div class="modal-header-content">
            <div class="modal-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <div>
              <h3 class="modal-title">Schedule Interview</h3>
              <p class="modal-subtitle">{{ candidate.firstName }} {{ candidate.lastName }}</p>
            </div>
          </div>
          <button class="modal-close" @click="showScheduleModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <form @submit.prevent="saveInterview" class="modal-body">
          <div class="form-row">
            <div class="input-group">
              <label for="date" class="input-label">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                Interview Date
              </label>
              <input
                type="date"
                id="date"
                v-model="newInterview.interview_date"
                class="input-field"
                :min="todayDate"
                required
              />
            </div>

            <div class="input-group">
              <label for="time" class="input-label">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Start Time
              </label>
              <input
                type="time"
                id="time"
                v-model="newInterview.interview_time"
                class="input-field"
                required
              />
            </div>
          </div>

          <div class="input-group">
            <label for="duration" class="input-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              Duration
            </label>
            <div class="duration-selector">
              <button
                type="button"
                v-for="duration in [15, 30, 45, 60, 90]"
                :key="duration"
                @click="newInterview.duration = duration"
                :class="['duration-btn', { active: newInterview.duration === duration }]"
              >
                {{ duration }} min
              </button>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showScheduleModal = false">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting || hasScheduledInterview">
              Schedule Interview
              <span v-if="isSubmitting" class="ml-2">...</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">

      <!-- Left Section -->
      <div class="left-section">

        <!-- Profile Card -->
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar">
              {{ candidate.firstName.charAt(0) }}{{ candidate.lastName.charAt(0) }}
            </div>

            <div class="profile-info">
              <h1 class="candidate-name">{{ candidate.firstName }} {{ candidate.lastName }}</h1>
              <span :class="['status-badge', getStatusClass(candidate.status)]">
                {{ candidate.status }}
              </span>
            </div>

            <div class="action-buttons">
              <button v-if="!hasScheduledInterview" class="schedule-interview-btn" :disabled="isSubmitting" @click="showScheduleModal = true">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
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
                Schedule Interview
              </button>
              <div v-else class="interview-scheduled-badge">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
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
                <div class="interview-info">
                  <span class="interview-status">Interview Scheduled</span>
                  <span v-if="interviewDetails" class="interview-date">
                    {{ formatInterviewDate(interviewDetails.interview_date) }}
                  </span>
                </div>
              </div>
              <button class="reject-btn" @click="showRejectPopup = true">
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
                Reject
              </button>
            </div>
          </div>

          <div class="profile-details">
            <p class="email">{{ candidate.email || 'Email not provided' }}</p>
            <p class="phone">{{ candidate.phone || 'Phone not provided' }}</p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            :class="['tab-btn', { active: activeTab === tab }]"
          >
            {{ tab }}
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">

          <!-- GENERAL TAB -->
          <div v-if="activeTab === 'General'" class="tab-panel">

            <!-- Resume Preview Section -->
            <div v-if="candidateFiles.length > 0" class="section">
              <div class="section-header">
                <h3 class="section-title">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  Resume Preview
                </h3>
                <a
                  v-if="resumeFile"
                  :href="resumeFile.url"
                  target="_blank"
                  class="download-btn"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download
                </a>
              </div>

              <!-- PDF Viewer -->
              <div v-if="resumeFile" class="pdf-viewer-container">
                <iframe
                  :src="`${resumeFile.url}#toolbar=1&navpanes=0&scrollbar=1`"
                  class="pdf-viewer"
                  frameborder="0"
                ></iframe>
                <div class="pdf-fallback">
                  <p>Can't view the PDF? <a :href="resumeFile.url" target="_blank">Click here to open in new tab</a></p>
                </div>
              </div>

              <!-- No PDF Available -->
              <div v-else class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <p>No resume uploaded yet.</p>
              </div>
            </div>

            <!-- Candidate Files List -->
            <div class="section">
              <div class="section-header">
                <h3 class="section-title">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  All Documents ({{ candidateFiles.length }})
                </h3>
              </div>

              <div v-if="candidateFiles.length > 0" class="files-list">
                <a
                  v-for="file in candidateFiles"
                  :key="file.name"
                  :href="file.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  :class="['file-item', file.type]"
                >
                  <div class="file-icon">
                    <svg
                      v-if="file.type === 'resume'"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <line x1="16" y1="13" x2="8" y2="13"></line>
                      <line x1="16" y1="17" x2="8" y2="17"></line>
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                  </div>
                  <div class="file-details">
                    <p class="file-name">{{ file.name }}</p>
                    <p class="file-meta">
                      <span class="file-type">{{ file.type.toUpperCase() }}</span>
                      <span v-if="file.date" class="file-date">• {{ formatDate(file.date) }}</span>
                    </p>
                  </div>
                  <div class="file-action">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                      <polyline points="15 3 21 3 21 9"></polyline>
                      <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                  </div>
                </a>
              </div>
              <p v-else class="empty-message">No documents uploaded.</p>
            </div>

          </div>

          <!-- EVALUATIONS TAB -->
          <div v-else-if="activeTab === 'Evaluations'" class="tab-panel">
            <div v-if="aiResults && aiResults.processed" class="evaluation-content">

              <!-- AI Score Banner -->
              <div class="eval-score-banner">
                <div class="eval-score-left">
                  <div class="eval-score-number">{{ aiResults.score }}%</div>
                  <div class="eval-score-label">Match Score</div>
                </div>
                <div class="eval-score-right">
                  <span v-if="aiResults.score >= 90" class="status-badge-large excellent">
                    🌟 Excellent Match
                  </span>
                  <span v-else-if="aiResults.score >= 75" class="status-badge-large good">
                    ✓ Good Match
                  </span>
                  <span v-else-if="aiResults.score >= 60" class="status-badge-large average">
                    ~ Average Match
                  </span>
                  <span v-else class="status-badge-large poor">
                    ✗ Below Average
                  </span>
                </div>
              </div>

              <!-- AI Feedback -->
              <div class="section">
                <div class="section-header">
                  <h3 class="section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    AI Analysis
                  </h3>
                </div>
                <div class="feedback-box">
                  <p class="feedback-text">{{ aiResults.feedback }}</p>
                </div>
              </div>

              <!-- Skills -->
              <div v-if="aiResults.metadata?.skills && aiResults.metadata.skills.length > 0" class="section">
                <div class="section-header">
                  <h3 class="section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="16 18 22 12 16 6"></polyline>
                      <polyline points="8 6 2 12 8 18"></polyline>
                    </svg>
                    Technical Skills ({{ aiResults.metadata.skills.length }})
                  </h3>
                </div>
                <div class="skills-grid">
                  <span v-for="skill in aiResults.metadata.skills" :key="skill" class="skill-badge">
                    {{ skill }}
                  </span>
                </div>
              </div>

              <!-- Projects -->
              <div v-if="aiResults.metadata?.projects && aiResults.metadata.projects.length > 0" class="section">
                <div class="section-header">
                  <h3 class="section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Projects
                  </h3>
                </div>
                <div v-for="(project, idx) in aiResults.metadata.projects" :key="idx" class="project-card">
                  <h4 class="project-title">{{ project.title }}</h4>
                  <p class="project-description">{{ project.description }}</p>
                  <div v-if="project.technologies && project.technologies.length > 0" class="tech-tags">
                    <span v-for="tech in project.technologies" :key="tech" class="tech-badge">
                      {{ tech }}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <div v-else-if="loadingAIResults" class="loading-state">
              <div class="loading-spinner"></div>
              <p>Loading AI evaluation...</p>
            </div>

            <div v-else class="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <p>Resume not yet analyzed by AI.</p>
              <p class="hint-text">Analysis happens automatically when the candidate applies.</p>
            </div>
          </div>

          <!-- EXPERIENCE TAB -->
          <div v-else-if="activeTab === 'Experience'" class="tab-panel">
            <div v-if="experience.length > 0" class="experience-list">
              <div v-for="(exp, idx) in experience" :key="idx" class="experience-card">
                <div class="exp-header">
                  <div class="exp-icon">💼</div>
                  <div class="exp-info">
                    <h4 class="exp-title">{{ exp.role }}</h4>
                    <p class="exp-company">{{ exp.company }}</p>
                  </div>
                  <div v-if="exp.duration" class="exp-duration">{{ exp.duration }}</div>
                </div>
                <div v-if="exp.responsibilities && exp.responsibilities.length > 0" class="exp-body">
                  <p class="exp-label">Key Responsibilities:</p>
                  <ul class="exp-list">
                    <li v-for="(task, i) in exp.responsibilities" :key="i">{{ task }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
              </svg>
              <p>No experience data available.</p>
            </div>
          </div>

          <!-- EDUCATION TAB -->
          <div v-else-if="activeTab === 'Education'" class="tab-panel">
            <div v-if="education.length > 0" class="education-list">
              <div v-for="(edu, idx) in education" :key="idx" class="education-card">
                <div class="edu-icon">🎓</div>
                <div class="edu-content">
                  <h4 class="edu-title">{{ edu.degree }}</h4>
                  <p class="edu-institution">{{ edu.institution }}</p>
                  <p v-if="edu.year" class="edu-year">Graduated: {{ edu.year }}</p>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
              </svg>
              <p>No education data available.</p>
            </div>
          </div>

          <!-- SKILLS TAB -->
          <div v-else-if="activeTab === 'Skills'" class="tab-panel">
            <div v-if="aiResults?.metadata?.skills && aiResults.metadata.skills.length > 0">
              <div class="section">
                <div class="skills-showcase">
                  <span v-for="skill in aiResults.metadata.skills" :key="skill" class="skill-badge-large">
                    {{ skill }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
              </svg>
              <p>No skills data available.</p>
            </div>
          </div>

        </div>
      </div>

      <!-- Right Section -->
      <div class="right-section">

        <!-- AI Score Card -->
        <div class="score-card">
          <h3 class="score-card-title">AI Match Score</h3>
          <div class="score-circle">
            <svg viewBox="0 0 120 120" class="circle-svg">
              <!-- Dynamic gradient based on score -->
              <defs>
                <linearGradient id="circleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" :style="`stop-color:${getScoreColor(candidate.aiMatchScore)};stop-opacity:1`" />
                  <stop offset="100%" :style="`stop-color:${getScoreColorDark(candidate.aiMatchScore)};stop-opacity:1`" />
                </linearGradient>
              </defs>

              <circle cx="60" cy="60" r="54" class="circle-bg"></circle>
              <circle
                cx="60"
                cy="60"
                r="54"
                class="circle-fill"
                :style="{ strokeDashoffset: 360 - (candidate.aiMatchScore * 3.6) }"
              ></circle>
            </svg>
            <div class="score-text">
              <p class="score-number" :style="{ color: getScoreColor(candidate.aiMatchScore) }">
                {{ candidate.aiMatchScore }}
              </p>
              <p class="score-label">Match</p>
            </div>
          </div>
          <p class="score-description">Based on resume analysis and job requirements</p>
        </div>



        <!-- Qualifications Match -->
        <div class="qualifications-card">
          <h3 class="qualifications-title">Quick Overview</h3>
          <div class="qualifications-list">
            <div
              v-for="(item, index) in qualifications"
              :key="index"
              :class="['qualification-item', item.match ? 'match' : 'no-match']"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline v-if="item.match" points="20 6 9 17 4 12"></polyline>
                <line v-else x1="18" y1="6" x2="6" y2="18"></line>
                <line v-if="!item.match" x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Reject Popup -->
    <div v-if="showRejectPopup" class="popup-overlay">
      <div class="popup">
        <h3>Reject Candidate</h3>
        <p>Do you really want to reject {{ candidate.firstName }} {{ candidate.lastName }}?</p>

        <div class="popup-actions">
          <button class="confirm-btn" @click="rejectCandidate">Yes, Reject</button>
          <button class="cancel-btn" @click="showRejectPopup = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "vuex";

const store = useStore();
const route = useRoute();
const applicationId = route.params.id;

const tabs = ref([
  "General",
  "Evaluations",
  "Experience",
  "Education",
  "Skills"
]);

const todayDate = new Date().toISOString().split("T")[0];
const hasScheduledInterview = ref(false);
const interviewDetails = ref(null);
const loadingInterview = ref(false);
const isSubmitting = ref(false);
const activeTab = ref("Evaluations"); // Start with Evaluations to showcase AI

const showRejectPopup = ref(false);
const showScheduleModal = ref(false);

const newInterview = ref({
  interview_date: "",
  interview_time: "",
  duration: 30,
});

const candidate = ref({
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  status: "",
  aiMatchScore: 0,
});

const candidateFiles = ref([]);
const experience = ref([]);
const education = ref([]);
const qualifications = ref([]);
const aiResults = ref(null);
const loadingAIResults = ref(false);


// ✅ ADD THIS FUNCTION
const checkInterviewStatus = async () => {
  if (loadingInterview.value) return;

  loadingInterview.value = true;
  try {
    const interviews = await store.dispatch("hr/fetchInterviewByApplication", applicationId);

    const list = Array.isArray(interviews) ? interviews : (interviews ? [interviews] : []);

    const scheduled = list.find(i =>
      String(i.application_id) === String(applicationId) &&
      ["scheduled", "completed", "in_progress"].includes(String(i.status).toLowerCase())
    );

    if (scheduled) {
      hasScheduledInterview.value = true;
      interviewDetails.value = scheduled;
    } else {
      hasScheduledInterview.value = false;
      interviewDetails.value = null;
    }
  } catch (err) {
    console.error("Failed to check interview status:", err);
    hasScheduledInterview.value = false;
  } finally {
    loadingInterview.value = false;
  }
};


const saveInterview = async () => {
  // ✅ Prevent double-click
  if (isSubmitting.value) return;

  // ✅ Disable button immediately
  isSubmitting.value = true;

  try {
    const { interview_date, interview_time } = newInterview.value;

    // Validation 1: Check inputs
    if (!interview_date || !interview_time) {
      alert("Please select both date and time.");
      return;
    }

    // Validation 2: Check date format
    let selectedDate;
    try {
      selectedDate = new Date(interview_date);
      if (isNaN(selectedDate.getTime())) {
        throw new Error("Invalid date");
      }
    } catch (err) {
      alert("Please enter a valid interview date.");
      return;
    }

    // Validation 3: Date not in past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const checkDate = new Date(interview_date);
    checkDate.setHours(0, 0, 0, 0);

    if (checkDate < today) {
      alert("Interview date cannot be in the past.");
      return;
    }

    // Validation 4: Time not in past
    const selectedDateTime = new Date(`${interview_date}T${interview_time}:00`);
    const now = new Date();
    if (selectedDateTime < now) {
      alert("Interview time must be in the future.");
      return;
    }

    // Validation 5: Duration
    const duration = newInterview.value.duration;
    if (!duration || duration < 15 || duration > 480) {
      alert("Interview duration must be between 15 and 480 minutes.");
      return;
    }

    // Validation 6: Frontend check
    if (hasScheduledInterview.value) {
      alert("An interview is already scheduled. Please refresh to see details.");
      return;
    }

    const authUser = store.getters["auth/currentUser"];

    // Attempt to schedule
    try {
      const result = await store.dispatch("hr/scheduleInterview", {
        applicationId,
        hrId: authUser?.hr_id,
        form: newInterview.value,
      });

      if (result.success) {
        console.log("✅ Interview scheduled successfully", result.interview);
        alert("Interview scheduled successfully!");

        showScheduleModal.value = false;
        newInterview.value = {
          interview_date: "",
          interview_time: "",
          duration: 30
        };

        await checkInterviewStatus();
      }

    } catch (error) {
      // ✅ Handle different error types

      if (error.type === 'CONFLICT') {
        // CASE: Interview already exists
        const existing = error.existingInterview;
        const dateStr = existing?.interview_date ?
          new Date(existing.interview_date).toLocaleDateString() : 'unknown date';
        const timeStr = existing?.interview_time || 'unknown time';

        alert(
          `Cannot schedule interview.\n\n` +
          `An interview is already ${existing?.status?.toLowerCase() || 'scheduled'} ` +
          `for this application.\n\n` +
          `Existing interview: ${dateStr} at ${timeStr}`
        );

        // 1. Update the UI to show the "Scheduled" badge
        await checkInterviewStatus();

        // 2. CLOSE THE MODAL (So they can't click submit again)
        showScheduleModal.value = false;

      } else {
        // CASE: Other errors (keep modal open to fix input)
        if (error.type === 'BAD_REQUEST') {
          alert(`Invalid input:\n${error.message}`);
        } else if (error.type === 'NOT_FOUND') {
          alert(`Cannot schedule interview:\n${error.message}`);
        } else {
          alert(`Failed to schedule interview:\n${error.message}`);
        }

        // Keep modal open for retries
        showScheduleModal.value = true;
      }
    }
  } catch (err) {
    console.error("Unexpected error:", err);
    alert("An unexpected error occurred. Please try again.");
  } finally {
    isSubmitting.value = false; // ✅ Re-enable button (CRITICAL)
  }
};
/* ✅ FIXED: Handle structured experience objects */
const buildExperienceFromMetadata = (metaExp) => {
  if (!Array.isArray(metaExp)) return [];

  return metaExp.map((e) => {
    let responsibilities = [];
    if (Array.isArray(e?.responsibilities)) {
      responsibilities = e.responsibilities.filter(Boolean);
    } else if (e?.responsibilities && typeof e.responsibilities === 'string') {
      responsibilities = e.responsibilities.split(". ").map(s => s.trim()).filter(Boolean);
    } else if (e?.description) {
      responsibilities = e.description.split(". ").map(s => s.trim()).filter(Boolean);
    }

    return {
      role: e?.role || e?.title || "Role not specified",
      company: e?.company || "Company not specified",
      duration: e?.duration || e?.dates || "",
      responsibilities,
    };
  });
};

/* ✅ FIXED: Handle structured education objects */
const buildEducationFromMetadata = (metaEdu) => {
  if (!Array.isArray(metaEdu)) return [];

  return metaEdu.map((edu) => {
    if (typeof edu === 'object' && edu !== null) {
      const year = edu.graduation_year || edu.graduationYear || edu.year || "";
      const institution = edu.university || edu.institution || "Institution not specified";
      const field = edu.field || edu.major || "";
      const degreeText = field && field !== "Not specified" && field !== "Field not specified"
        ? `${edu.degree} in ${field}`
        : edu.degree || "Education";

      return {
        degree: degreeText,
        institution: institution,
        year: year
      };
    }

    if (typeof edu === 'string') {
      const degreePart = edu.split(" - ")[0] || edu;
      const rest = edu.split(" - ")[1] || "";
      const yearMatch = edu.match(/\b(202\d|19\d{2})\b/);
      const year = yearMatch ? yearMatch[1] : "";

      return {
        degree: degreePart,
        institution: rest,
        year: year
      };
    }

    return {
      degree: "Education",
      institution: "",
      year: ""
    };
  });
};

const updateQualificationsFromMetadata = (metadata) => {
  if (!metadata) return;

  const hasEducation = Array.isArray(metadata.education) && metadata.education.length > 0;
  const hasSkills = Array.isArray(metadata.skills) && metadata.skills.length > 0;
  const hasExperience = Array.isArray(metadata.experience) && metadata.experience.length > 0;

  qualifications.value = [
    { label: "Education Verified", match: hasEducation },
    { label: "Skills Match", match: hasSkills },
    { label: "Experience Match", match: hasExperience },
  ];
};

const applyMetadataToCandidate = (metadata, score) => {
  if (!metadata) return;

  if (metadata.name && typeof metadata.name === "string") {
    const parts = metadata.name.trim().split(/\s+/);
    candidate.value.firstName = parts[0] || candidate.value.firstName;
    candidate.value.lastName = parts.slice(1).join(" ") || candidate.value.lastName;
  }

  if (metadata.email) {
    candidate.value.email = metadata.email;
  }
  if (metadata.phone) {
    candidate.value.phone = metadata.phone;
  }

  const numericScore = Number(score);
  if (!Number.isNaN(numericScore)) {
    candidate.value.aiMatchScore = Math.max(0, Math.min(100, numericScore));
  }
};

const getStatusClass = (status) => {
  const statusMap = {
    'pending': 'pending',
    'under review': 'review',
    'shortlisted': 'shortlisted',
    'interview': 'interview',
    'offered': 'offered',
    'rejected': 'rejected'
  };
  return statusMap[status?.toLowerCase()] || 'pending';
};

const getScoreColor = (score) => {
  if (score >= 90) return '#10b981'; // Green - Excellent
  if (score >= 75) return '#3b82f6'; // Blue - Good
  if (score >= 60) return '#f59e0b'; // Orange - Average
  return '#ef4444'; // Red - Below Average
};

const getScoreColorDark = (score) => {
  if (score >= 90) return '#059669'; // Dark Green
  if (score >= 75) return '#2563eb'; // Dark Blue
  if (score >= 60) return '#d97706'; // Dark Orange
  return '#dc2626'; // Dark Red
};

const loadAIResults = async () => {
  if (loadingAIResults.value) return;
  loadingAIResults.value = true;
  try {
    const results = await store.dispatch("hr/fetchApplicationAIResults", applicationId);
    aiResults.value = results;

    if (results && results.processed) {
      const metadata = results.metadata || {};

      experience.value = buildExperienceFromMetadata(metadata.experience);
      education.value = buildEducationFromMetadata(metadata.education);
      applyMetadataToCandidate(metadata, results.score);
      updateQualificationsFromMetadata(metadata);
    }
  } catch (err) {
    console.error("Failed to load AI results", err);
    aiResults.value = null;
  } finally {
    loadingAIResults.value = false;
  }
};

const convertToHttpUrl = (filePath) => {
  if (!filePath) return '';

  // If already an HTTP URL, return as-is
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath;
  }

  // Extract filename from file system path
  // Example: /home/devendra/.../uploads/resumes/560949be98b5438c8bd61d4e29fa4bc4.pdf
  // Should become: 560949be98b5438c8bd61d4e29fa4bc4.pdf
  const filename = filePath.split('/').pop();

  // Determine subfolder from path
  let folder = 'resumes'; // default
  if (filePath.includes('/cover_letters/') || filePath.includes('cover_letter')) {
    folder = 'cover_letters';
  } else if (filePath.includes('/jds/')) {
    folder = 'jds';
  }

  // Construct proper HTTP URL pointing to Flask backend
  return `http://localhost:8086/uploads/${folder}/${filename}`;
};


onMounted(async () => {
  try {
    const profile = await store.dispatch("hr/fetchCandidateProfile", applicationId);

    candidate.value.firstName = profile.name || "";
    candidate.value.lastName = profile.last_name || profile.lastName || "";
    candidate.value.email = profile.email || "";
    candidate.value.phone = profile.phone || "";
    candidate.value.status = profile.application_status || profile.status || "";
    candidate.value.aiMatchScore = profile.ai_match_score ?? 0;

    candidateFiles.value = [];

    if (profile.resume?.filename) {
      const resumePath = profile.resume.path || profile.resume.filename;
      candidateFiles.value.push({
        name: profile.resume.filename,
        url: convertToHttpUrl(resumePath),
        type: "resume",
        date: profile.resume.uploaded_at,
      });
    }

    if (profile.cover_letter?.filename) {
      const coverPath = profile.cover_letter.path || profile.cover_letter.filename;
      candidateFiles.value.push({
        name: profile.cover_letter.filename,
        url: convertToHttpUrl(coverPath),
        type: "cover",
        date: profile.cover_letter.uploaded_at,
      });
    }

    qualifications.value = [
      { label: "Education Verified", match: false },
      { label: "Skills Match", match: false },
      { label: "Experience Match", match: false },
    ];

    // ✅ Check interview status first, then load AI results
    await checkInterviewStatus();
    await loadAIResults();
  } catch (err) {
    console.error("Failed to load profile", err);
  }
});

const resumeFile = computed(() => {
  return candidateFiles.value.find(file => file.type === 'resume') || null;
});

// Add this helper function
const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
};


const rejectCandidate = async () => {
  try {
    await store.dispatch("hr/rejectInterview", applicationId);
    alert("Candidate rejected.");
    showRejectPopup.value = false;
    candidate.value.status = "rejected";
  } catch (err) {
    console.error(err);
    alert("Failed to reject candidate.");
  }
};
</script>

<style scoped>
/* ===== GLOBAL STYLES ===== */
.candidate-profile-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 2rem;
}

/* ===== POPUP STYLES ===== */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30, 58, 95, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popup {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 450px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popup h3 {
  margin-bottom: 1rem;
  color: #1e3a5f;
  font-size: 1.25rem;
}

.popup p {
  margin-bottom: 1.5rem;
  color: #64748b;
  font-size: 0.95rem;
}

.popup-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.confirm-btn {
  background: #dc2626;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.cancel-btn {
  background: #e5e7eb;
  color: #1e3a5f;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #cbd5e1;
}

/* ===== MAIN CONTENT ===== */
.main-content {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== LEFT SECTION ===== */
.left-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ===== PROFILE CARD ===== */
.profile-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  font-size: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.profile-info {
  flex: 1;
}

.candidate-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.status-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.review {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.shortlisted {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.interview {
  background: #e0f2fe;
  color: #0284c7;
}

.status-badge.offered {
  background: #dcfce7;
  color: #166534;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.schedule-interview-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.schedule-interview-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.reject-btn {
  padding: 0.75rem 1rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  color: #dc2626;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.reject-btn:hover {
  background: #fecaca;
  border-color: #f87171;
  transform: translateY(-1px);
}

.profile-details {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.email,
.phone {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0.5rem 0;
}

/* ===== TABS ===== */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e5e7eb;
  background: white;
  border-radius: 16px 16px 0 0;
  overflow-x: auto;
}

.tab-btn {
  padding: 1rem 1.75rem;
  background: none;
  border: none;
  color: #94a3b8;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
  font-size: 0.95rem;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-btn:hover {
  color: #1e3a5f;
  background: #f9fafb;
}

/* ===== TAB CONTENT ===== */
.tab-content {
  background: white;
  border-radius: 0 0 16px 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-height: 400px;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ===== EVALUATIONS TAB ===== */
.evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.eval-score-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2.5rem;
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.eval-score-left {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.eval-score-number {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1;
}

.eval-score-label {
  font-size: 1rem;
  opacity: 0.9;
  margin-top: 0.5rem;
  font-weight: 500;
}

.eval-score-right {
  font-size: 1.25rem;
  font-weight: 600;
}

.status-badge-large {
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  display: inline-block;
}

.status-badge-large.excellent {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-badge-large.good {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-badge-large.average {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.status-badge-large.poor {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title svg {
  color: #667eea;
}

.feedback-box {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-left: 4px solid #667eea;
  padding: 1.75rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.feedback-text {
  font-size: 1rem;
  line-height: 1.8;
  color: #334155;
  margin: 0;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
}

.skill-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 1rem;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #0284c7;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s;
  border: 1px solid #93c5fd;
}

.skill-badge:hover {
  background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
}

.skills-showcase {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.skill-badge-large {
  padding: 0.85rem 1.5rem;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #0284c7;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  border: 2px solid #93c5fd;
  transition: all 0.2s;
}

.skill-badge-large:hover {
  background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(2, 132, 199, 0.25);
}

.project-card {
  padding: 1.75rem;
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
  border-radius: 12px;
  border: 1px solid #e9d5ff;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.project-card:hover {
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.15);
  transform: translateY(-2px);
}

.project-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1rem 0;
}

.project-description {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.7;
  margin: 0 0 1.25rem 0;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-badge {
  display: inline-block;
  padding: 0.4rem 0.85rem;
  background: #f3e8ff;
  color: #7c3aed;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #e9d5ff;
}

/* ===== EXPERIENCE TAB ===== */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experience-card {
  padding: 1.75rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  border: 1px solid #fde047;
  transition: all 0.2s;
}

.experience-card:hover {
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.2);
  transform: translateY(-2px);
}

.exp-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.exp-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.exp-info {
  flex: 1;
}

.exp-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.exp-company {
  font-size: 0.9rem;
  color: #78350f;
  margin: 0;
  font-weight: 500;
}

.exp-duration {
  font-size: 0.85rem;
  color: #92400e;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-weight: 600;
}

.exp-body {
  border-top: 1px solid rgba(245, 158, 11, 0.2);
  padding-top: 1rem;
}

.exp-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.75rem 0;
}

.exp-list {
  font-size: 0.9rem;
  color: #475569;
  padding-left: 1.5rem;
  margin: 0;
  line-height: 1.7;
}

.exp-list li {
  margin-bottom: 0.5rem;
}

/* ===== EDUCATION TAB ===== */
.education-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.education-card {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  padding: 1.75rem;
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  border-radius: 12px;
  border: 1px solid #86efac;
  transition: all 0.2s;
}

.education-card:hover {
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.2);
  transform: translateY(-2px);
}

.edu-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.edu-content {
  flex: 1;
}

.edu-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.edu-institution {
  font-size: 0.95rem;
  color: #166534;
  margin: 0 0 0.25rem 0;
  font-weight: 500;
}

.edu-year {
  font-size: 0.85rem;
  color: #15803d;
  margin: 0;
  font-weight: 600;
}

/* ===== FILES ===== */
.files-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.file-card {
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f9fafb;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.file-card:hover {
  background: #f0f7ff;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.file-card.resume {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border-color: #93c5fd;
}

.file-card.resume:hover {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.file-card.cover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-color: #fca5a5;
}

.file-card.cover:hover {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.file-card svg {
  flex-shrink: 0;
  color: #0284c7;
}

.file-card.cover svg {
  color: #dc2626;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
  font-size: 0.95rem;
}

.file-date {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

/* ===== EMPTY STATE ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state svg {
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0.5rem 0;
  font-size: 1rem;
  color: #64748b;
}

.hint-text {
  font-size: 0.875rem;
  color: #94a3b8;
  font-style: italic;
}

.empty-message {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
  font-size: 0.95rem;
}

/* ===== LOADING STATE ===== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #64748b;
  font-size: 1rem;
}

/* ===== RIGHT SECTION ===== */
.right-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ===== SCORE CARD ===== */
.score-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.score-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1.5rem 0;
  text-align: center;
}

.score-circle {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 1.5rem;
}

.circle-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 8;
}

.circle-fill {
  fill: none;
  stroke: url(#circleGradient); /* ✅ Use the gradient */
  stroke-width: 8;
  stroke-dasharray: 360;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-number {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1;
}

.score-label {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0.5rem 0 0 0;
  font-weight: 600;
}

.score-description {
  font-size: 0.85rem;
  color: #94a3b8;
  text-align: center;
  line-height: 1.5;
  margin: 0;
}

/* ===== QUALIFICATIONS CARD ===== */
.qualifications-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.qualifications-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1.25rem 0;
}

.qualifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qualification-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  padding: 0.75rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.qualification-item.match {
  color: #10b981;
  background: #f0fdf4;
}

.qualification-item.match svg {
  stroke: #10b981;
}

.qualification-item.no-match {
  color: #dc2626;
  background: #fef2f2;
}

.qualification-item.no-match svg {
  stroke: #dc2626;
}

/* ===== FORM STYLES ===== */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-top: 1.5rem;
  text-align: left;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #1e3a5f;
  font-size: 0.95rem;
}

.form-group select,
.form-group input {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #1e3a5f;
  transition: all 0.2s;
}

.form-group select:focus,
.form-group input:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .files-grid {
    grid-template-columns: 1fr;
  }
}

/* ===== PDF VIEWER STYLES ===== */
.pdf-viewer-container {
  position: relative;
  width: 100%;
  height: 800px;
  background: #f9fafb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 2px solid #e5e7eb;
}

.pdf-viewer {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-fallback {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  padding: 1rem;
  text-align: center;
  color: white;
  font-size: 0.9rem;
}

.pdf-fallback a {
  color: #93c5fd;
  text-decoration: underline;
  font-weight: 600;
}

.pdf-fallback a:hover {
  color: #60a5fa;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* ===== FILES LIST STYLES ===== */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.file-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  transform: translateX(4px);
}

.file-item.resume {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-color: #93c5fd;
}

.file-item.resume:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
}

.file-item.cover {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #fca5a5;
}

.file-item.cover:hover {
  border-color: #ef4444;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
}

.file-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.file-item.resume .file-icon {
  background: #dbeafe;
}

.file-item.resume .file-icon svg {
  stroke: #2563eb;
}

.file-item.cover .file-icon {
  background: #fee2e2;
}

.file-item.cover .file-icon svg {
  stroke: #dc2626;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
  font-size: 0.95rem;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

.file-type {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.file-date {
  font-weight: 400;
}

.file-action {
  flex-shrink: 0;
  color: #94a3b8;
  transition: all 0.2s;
}

.file-item:hover .file-action {
  color: #667eea;
  transform: translateX(4px);
}

/* Responsive */
@media (max-width: 768px) {
  .pdf-viewer-container {
    height: 600px;
  }

  .file-item {
    padding: 1rem;
  }

  .file-icon {
    width: 40px;
    height: 40px;
  }
}

/* ===== MODERN MODAL STYLES ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.3s ease;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon svg {
  stroke: white;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: white;
}

.modal-subtitle {
  font-size: 0.95rem;
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  color: white;
}

.modal-close {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: white;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1e3a5f;
  font-size: 0.9rem;
}

.input-label svg {
  color: #667eea;
}

.input-field {
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #1e3a5f;
  transition: all 0.2s;
  font-family: inherit;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.input-field:hover {
  border-color: #cbd5e1;
}

.duration-selector {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.duration-btn {
  padding: 0.75rem 1.25rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.duration-btn:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}

.duration-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 0.5rem;
}

.btn-secondary {
  padding: 0.875rem 1.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e3a5f;
}

.btn-primary {
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

/* ===== INTERVIEW SCHEDULED BADGE ===== */
.interview-scheduled-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border: 2px solid #6ee7b7;
  border-radius: 10px;
  color: #065f46;
}

.interview-scheduled-badge svg {
  stroke: #059669;
  flex-shrink: 0;
}

.interview-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.interview-status {
  font-weight: 700;
  font-size: 0.9rem;
  color: #065f46;
}

.interview-date {
  font-size: 0.8rem;
  color: #047857;
  font-weight: 500;
}

/* Responsive for Modal */
@media (max-width: 640px) {
  .modal-container {
    width: 95%;
    max-width: none;
    margin: 1rem;
  }

  .modal-header {
    padding: 1.5rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .duration-selector {
    justify-content: space-between;
  }

  .duration-btn {
    flex: 1;
    min-width: fit-content;
  }
}

@media (max-width: 768px) {
  .candidate-profile-page {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .action-buttons {
    width: 100%;
    flex-direction: column;
  }

  .schedule-interview-btn,
  .reject-btn {
    width: 100%;
    justify-content: center;
  }

  .tabs {
    overflow-x: auto;
  }

  .skills-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }

  .eval-score-banner {
    flex-direction: column;
    gap: 1.5rem;
  }
}
</style>

