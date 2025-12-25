<template>
  <div class="dashboard-page">
    <div class="dashboard-content">

      <!-- ===================== KPI SECTION ===================== -->
      <section class="overview-section">
        <div class="overview-header">
          <h3 class="overview-title">Key Performance Indicators</h3>
        </div>

        <div class="kpi-grid">
          <div
            v-for="stat in statCards"
            :key="stat.id"
            class="kpi-card"
            :class="`kpi-${stat.color}`"
          >
            <div class="kpi-icon-wrapper">
              <div class="kpi-icon" v-html="stat.icon"></div>
            </div>

            <div class="kpi-content">
              <div class="kpi-value">
                <span class="kpi-number">{{ stat.value }}</span>
                <span class="kpi-unit">{{ stat.unit }}</span>
              </div>
              <div class="kpi-label">{{ stat.label }}</div>
              <div
                v-if="stat.change !== 0 && stat.trend"
                class="kpi-trend"
                :class="{ up: stat.trend === 'up', down: stat.trend === 'down' }"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <polyline points="17 11 12 6 7 11 7 13 12 18 17 13" />
                </svg>
                <span>{{ stat.change }}% from last month</span>
              </div>
              <div v-else class="kpi-trend">
                <span style="color: #94a3b8; font-size: 0.85rem;">No historical data available</span>
              </div>
            </div>
          </div>
        </div>
      </section>


      <!-- ===================== REQUIRE ATTENTION ===================== -->
      <section class="require-attention">
        <h3 class="section-title">Require Attention</h3>

        <!-- Tabs -->
        <nav class="tabs-container" role="tablist">
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              :class="['tab-btn', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
              role="tab"
              type="button"
            >
              {{ tab.name }}
            </button>
          </div>
        </nav>

        <!-- Data Table -->
        <DataTable
          :columns="tableColumns"
          :data="activeTabData"
          row-key="job_id"
          :items-per-page="12"
        >

          <!-- JOB TITLE CELL -->
          <template #cell-job_title="{ row }">
            <div class="cell-content">
              <p class="role-name">{{ row.job_title }}</p>
            </div>
          </template>

          <!-- POSITIONS LEFT -->
          <template #cell-positions_left="{ row }">
            <span class="pending-badge">
              {{ row.positions_left }}
            </span>
          </template>

          <!-- OFFERED -->
          <template #cell-offered_count="{ row }">
            <span
              :class="[
                'score-badge',
                row.offered_count > 5 ? 'high' : row.offered_count > 0 ? 'medium' : 'low'
              ]"
            >
              {{ row.offered_count }}
            </span>
          </template>

          <!-- FEEDBACK PENDING -->
          <template #cell-feedback_pending_count="{ row }">
            <span class="pending-badge">
              {{ row.feedback_pending_count }}
            </span>
          </template>

        </DataTable>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { useStore } from "vuex"
import DataTable from "@/components/DataTable.vue"
import { useRouter } from "vue-router"
import api from "@/services/api"

const store = useStore()
const router = useRouter()

/* Tabs */
const activeTab = ref("jobs")

const tabs = [
  { id: "jobs", name: "Jobs" },
  { id: "candidates", name: "Candidates" },
  { id: "onboardings", name: "Onboardings" }
]

/* Simplified Table Columns (6 important stats only) */
const tableColumns = [
  { key: "job_title", label: "Job Title" },
  { key: "positions_left", label: "Positions Left" },
  { key: "applications_count", label: "Applications" },
  { key: "interviewed_count", label: "Interviewed" },
  { key: "feedback_pending_count", label: "Feedback Pending" },
  { key: "offered_count", label: "Offered" }
]

/* Logged-in HR */
const hrUser = JSON.parse(localStorage.getItem("currentUser"))
const companyId = hrUser?.company_id
const hrId = hrUser?.hr_id

/* Dashboard API Loader */
const loadDashboard = async () => {
  try {
    await store.dispatch("hr/getOfferAcceptanceRate", companyId)
  } catch (err) {}

  try {
    await store.dispatch("hr/getPendingOnboardings", companyId)
  } catch (err) {}

  try {
    await store.dispatch("hr/getPendingFeedbackCount", companyId)
  } catch (err) {}

  try {
    await store.dispatch("hr/getJobStats", companyId)
  } catch (err) {}
}

/* KPI Cards */
const statCards = computed(() => {
  const d = store.getters["hr/dashboard"]

  return [
    {
      id: 1,
      value: d.acceptanceRate || 0,
      unit: "%",
      label: "Offer Acceptance Rate",
      color: "orange",
      trend: null, // No trend data available - will show "No change" message
      change: 0, // No historical data to calculate change
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`
    },
    {
      id: 2,
      value: d.pendingOnboardings || 0,
      unit: "",
      label: "Onboarding Pending",
      color: "purple",
      trend: null, // No trend data available - will show "No change" message
      change: 0, // No historical data to calculate change
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"></circle></svg>`
    },
    {
      id: 3,
      value: d.pendingFeedback || 0,
      unit: "",
      label: "Interview Feedback Pending",
      color: "blue",
      trend: null, // No trend data available - will show "No change" message
      change: 0, // No historical data to calculate change
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`
    }
  ]
})

/* Job Statistics Data */
const jobsData = computed(() => store.getters["hr/jobStats"] || [])

/* Candidates Data */
const candidatesData = ref([])
const loadCandidates = async () => {
  try {
    const res = await store.dispatch("hr/fetchCandidates", {
      companyId,
      role: '',
      search: '',
      page: 1,
      perPage: 100
    })
    candidatesData.value = (res.candidates || []).map(c => ({
      job_title: c.role || 'N/A',
      positions_left: '-',
      applications_count: 1,
      interviewed_count: '-',
      feedback_pending_count: '-',
      offered_count: '-',
      candidate_name: `${c.first_name} ${c.last_name}`.trim(),
      candidate_id: c.action_url?.split('/').pop()
    }))
  } catch (err) {
    console.error('Failed to load candidates:', err)
    candidatesData.value = []
  }
}

/* Onboardings Data */
const onboardingsData = ref([])
const loadOnboardings = async () => {
  try {
    const res = await api.get(`/onboarding/${companyId}`)
    const allOnboardings = Array.isArray(res.data) ? res.data : []
    onboardingsData.value = allOnboardings.map(ob => ({
      job_id: ob.application_id || ob.id,
      job_title: ob.job_title || 'N/A',
      positions_left: '-',
      applications_count: 1,
      interviewed_count: '-',
      feedback_pending_count: '-',
      offered_count: ob.offer_accepted ? 1 : 0,
      candidate_name: ob.candidate_name || 'N/A',
      onboarding_id: ob.id || ob.onboarding_id
    }))
  } catch (err) {
    console.error('Failed to load onboardings:', err)
    onboardingsData.value = []
  }
}

const activeTabData = computed(() => {
  if (activeTab.value === "jobs") return jobsData.value
  if (activeTab.value === "candidates") return candidatesData.value
  if (activeTab.value === "onboardings") return onboardingsData.value
  return []
})

// Watch for tab changes to load data
watch(activeTab, (newTab) => {
  if (newTab === "candidates" && candidatesData.value.length === 0) {
    loadCandidates()
  } else if (newTab === "onboardings" && onboardingsData.value.length === 0) {
    loadOnboardings()
  }
})

/* Lifecycle */
onMounted(() => {
  if (!companyId) return
  loadDashboard()
})
</script>


<style scoped>
.dashboard-page {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* KPI Section */
.overview-section {
  background: transparent;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.overview-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1rem 0;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.kpi-card {
  background: #fff;
  border-radius: 18px;
  padding: 1.75rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.06);
  border: 1px solid #f0f0f5;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card:hover {
  box-shadow: 0 8px 24px rgb(0 0 0 / 0.12);
  transform: translateY(-4px);
  border-color: #6366f1;
}

.kpi-icon-wrapper {
  flex-shrink: 0;
}

.kpi-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: inherit;
}

.kpi-card.kpi-orange .kpi-icon {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
  color: #c2410c;
}

.kpi-card.kpi-blue .kpi-icon {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.kpi-card.kpi-purple .kpi-icon {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #6d28d9;
}

.kpi-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.kpi-number {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1e3a5f;
  line-height: 1;
  letter-spacing: -0.02em;
}

.kpi-unit {
  font-size: 1.5rem;
  font-weight: 700;
  color: #64748b;
}

.kpi-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #475569;
  line-height: 1.3;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.25rem;
}

.kpi-trend.up {
  color: #16a34a;
}

.kpi-trend.down {
  color: #dc2626;
}

.kpi-trend svg {
  flex-shrink: 0;
}

/* Require Attention Section */
.require-attention {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  padding: 2rem;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: #1e3a5f;
}

.section-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

/* Tabs */
.tabs-container {
  margin-bottom: 2.25rem;
  border-bottom: 2px solid #d1d5db;
}

.tabs {
  display: flex;
  gap: 2.5rem;
}

.tab-btn {
  background: transparent;
  border: none;
  font-size: 1.05rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.75rem 0;
  border-bottom: 3px solid transparent;
  transition:
    color 0.3s,
    border-color 0.3s;
}

.tab-btn:hover {
  color: #2563eb;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  font-weight: 700;
}

/* Badge Styling */
.score-badge {
  display: inline-block;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 700;
  user-select: none;
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

.cell-content {
  display: flex;
  flex-direction: column;
}

.role-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.role-time {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 400;
}

/* Responsive */
@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .require-attention {
    padding: 1.5rem;
  }
}
</style>
