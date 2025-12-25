<template>
  <div class="dashboard-page">
    <div class="dashboard-content">
      <!-- Header Section -->
      <div class="header-section">
        <div class="company-info">
          <div class="company-icon">📊</div>
          <div class="company-text">
            <h1 class="company-name">{{ companyName }}</h1>
            <p class="company-subtitle">Statistics</p>
          </div>
        </div>
      </div>

      <!-- Stats Cards Grid -->
      <div class="stats-grid">
        <!-- Total Employees Card -->
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">{{ dashboardData.total_employees }}</h3>
            <div class="stat-icon employees-icon">👥</div>
          </div>
          <p class="stat-label">total Employees</p>
        </div>

        <!-- Onboarded Last Month Card -->
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">{{ dashboardData.onboarded_last_month }}</h3>
            <div class="stat-icon onboarded-icon">👨‍💼</div>
          </div>
          <p class="stat-label">Onboarded Last Month</p>
        </div>

        <!-- Total HRs Card -->
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">{{ dashboardData.total_hrs }}</h3>
            <div class="stat-icon hr-icon">👤</div>
          </div>
          <p class="stat-label">Total HRs</p>
        </div>

        <!-- Job Openings Card -->
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">{{ dashboardData.open_job_openings }}</h3>
            <div class="stat-icon openings-icon">📋</div>
          </div>
          <p class="stat-label">Job Openings available</p>
        </div>
      </div>

      <!-- Hiring Summary Chart Section -->
      <div class="chart-section">
        <div class="chart-card">
          <h2 class="chart-title">Hiring summary</h2>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-box openings"></span>
              <span>Openings</span>
            </div>
            <div class="legend-item">
              <span class="legend-box onboarded"></span>
              <span>Onboarded</span>
            </div>
            <div class="legend-item">
              <span class="legend-box interviewing"></span>
              <span>Interviewing</span>
            </div>
          </div>
          <div class="chart-placeholder">
            <svg viewBox="0 0 1000 300" xmlns="http://www.w3.org/2000/svg">
              <g>
                <template v-for="(month, index) in chartMonths" :key="month.key">
                  <!-- Calculate stacked positions -->
                  <!-- Openings bar (blue) - bottom -->
                  <rect 
                    :x="30 + index * 70" 
                    :y="270 - month.openingsScaled" 
                    width="50" 
                    :height="Math.max(month.openingsScaled, 0)" 
                    fill="#3b82f6"
                    :opacity="month.isFuture ? 0.5 : 1"
                  ></rect>
                  
                  <!-- Onboarded bar (orange) - middle -->
                  <rect 
                    :x="30 + index * 70" 
                    :y="270 - month.openingsScaled - month.onboardedScaled" 
                    width="50" 
                    :height="Math.max(month.onboardedScaled, 0)" 
                    fill="#f97316"
                    :opacity="month.isFuture ? 0.5 : 1"
                  ></rect>
                  
                  <!-- Interviewing bar (purple) - top -->
                  <rect 
                    :x="30 + index * 70" 
                    :y="270 - month.openingsScaled - month.onboardedScaled - month.interviewingScaled" 
                    width="50" 
                    :height="Math.max(month.interviewingScaled, 0)" 
                    fill="#a855f7"
                    :opacity="month.isFuture ? 0.5 : 1"
                  ></rect>
                  
                  <!-- Month label -->
                  <text 
                    :x="55 + index * 70" 
                    y="285" 
                    text-anchor="middle" 
                    font-size="12" 
                    :fill="month.isCurrent ? '#2563eb' : '#666'"
                    :font-weight="month.isCurrent ? 'bold' : 'normal'"
                  >{{ month.label }}</text>
                  
                  <!-- Current month indicator line -->
                  <line 
                    v-if="month.isCurrent"
                    :x1="30 + index * 70" 
                    :x2="80 + index * 70" 
                    y1="275" 
                    y2="275" 
                    stroke="#2563eb" 
                    stroke-width="2"
                    stroke-dasharray="3,3"
                  ></line>
                </template>
              </g>
            </svg>
          </div>
        </div>
      </div>

      <!-- Human Resources Section -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

const router = useRouter()
const store = useStore()

const dashboardData = ref({
  total_employees: 0,
  total_hrs: 0,
  onboarded_last_month: 0,
  open_job_openings: 0,
  hiring_summary: {
    openings: {},
    onboarded: {},
    interviewing: {}
  }
})

const companyName = ref('')

// Generate last 6 months + current + next 6 months (12 months total, centered around current)
const chartMonths = computed(() => {
  const months = []
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() // 0-11
  
  // Get max value for scaling
  const summary = dashboardData.value.hiring_summary || {}
  let maxValue = 1 // Minimum 1 to avoid division by zero
  
  // Generate months: last 6 months (i=-6 to -1), current month (i=0), next 6 months (i=1 to 6)
  for (let i = -6; i <= 6; i++) {
    const date = new Date(currentYear, currentMonth + i, 1)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const key = `${year}-${String(month).padStart(2, '0')}`
    
    const openings = summary.openings?.[key] || 0
    const onboarded = summary.onboarded?.[key] || 0
    const interviewing = summary.interviewing?.[key] || 0
    
    maxValue = Math.max(maxValue, openings, onboarded, interviewing)
    
    // Format label: show month name, and year if it's different from current year or future
    let label = monthNames[date.getMonth()]
    if (date.getFullYear() !== currentYear) {
      label = `${label} '${String(date.getFullYear()).slice(-2)}`
    } else if (i > 0) {
      // Future months in current year - could add indicator if needed
      label = label
    }
    
    months.push({
      key,
      label,
      openings,
      onboarded,
      interviewing,
      isCurrent: i === 0, // Mark current month
      isFuture: i > 0 // Mark future months
    })
  }
  
  // Scale values to fit chart (max height 200px)
  const scale = 200 / maxValue
  months.forEach(month => {
    month.openingsScaled = month.openings * scale
    month.onboardedScaled = month.onboarded * scale
    month.interviewingScaled = month.interviewing * scale
  })
  
  return months
})

const loadDashboard = async () => {
  try {
    const user = store.getters['auth/currentUser']
    const companyId = user?.company_id
    
    if (!companyId) {
      console.error('Company ID not found')
      return
    }

    const res = await api.get(`/company/dashboard/${companyId}`)
    dashboardData.value = res.data
    
    // Get company name from API response
    if (res.data?.company_name) {
      companyName.value = res.data.company_name.toUpperCase()
    } else if (user?.company_name) {
      companyName.value = user.company_name.toUpperCase()
    }
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Header Section */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.company-icon {
  font-size: 2.5rem;
}

.company-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.company-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
  letter-spacing: 0.05em;
}

.company-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.add-new-btn {
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-new-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.stat-icon {
  font-size: 2.5rem;
  display: flex;
  align-items: center;
}

.stat-label {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 0.75rem 0;
  font-weight: 500;
}

.stat-change {
  font-size: 0.85rem;
  margin: 0;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.negative {
  color: #ef4444;
}

/* Chart Section */
.chart-section {
  margin-bottom: 1rem;
}

.chart-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1.5rem 0;
}

.chart-legend {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

.legend-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  display: inline-block;
}

.legend-box.openings {
  background: #3b82f6;
}

.legend-box.onboarded {
  background: #f97316;
}

.legend-box.interviewing {
  background: #a855f7;
}

.chart-placeholder {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 8px;
}

.chart-placeholder svg {
  width: 100%;
  height: 100%;
}

/* HR Section */
.hr-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.hr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.hr-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.add-new-hr-btn {
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-new-hr-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.view-more-link {
  color: #065eb5;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s;
}

.view-more-link:hover {
  color: #054a94;
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-legend {
    flex-direction: column;
    gap: 1rem;
  }

  .hr-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
