<template>
  <div class="overview-section">
    <!-- Header -->
    <div class="overview-header">
      <h3 class="overview-title">Key Performance Indicators</h3>
    </div>

    <!-- KPI Stats Grid -->
    <div class="kpi-grid">
      <div v-for="stat in statCards" :key="stat.id" class="kpi-card" :class="`kpi-${stat.color}`">
        <div class="kpi-icon-wrapper">
          <div class="kpi-icon" :class="stat.color">
            <span v-html="stat.icon"></span>
          </div>
        </div>

        <div class="kpi-content">
          <div class="kpi-value">
            <span class="kpi-number">{{ stat.value }}</span>
            <span class="kpi-unit">{{ stat.unit }}</span>
          </div>
          <div class="kpi-label">{{ stat.label }}</div>
          <div class="kpi-trend" :class="stat.trend">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <polyline
                :points="stat.trend === 'up' ? '17 11 12 6 7 11' : '7 13 12 18 17 13'"
              ></polyline>
            </svg>
            <span>{{ stat.change }}% from last month</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const statCards = ref([
  {
    id: 1,
    value: 85,
    unit: '%',
    label: 'Offer Acceptance Rate',
    color: 'orange',
    trend: 'up',
    change: 12,
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>`,
  },
  {
    id: 2,
    value: 12,
    unit: '',
    label: 'Onboarding Pending',
    color: 'purple',
    trend: 'down',
    change: 8,
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>`,
  },
  {
    id: 3,
    value: 15,
    unit: '%',
    label: 'Interview Feedback Pending',
    color: 'blue',
    trend: 'up',
    change: 5,
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>`,
  },
])
</script>

<style scoped>
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
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.kpi-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.75rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f5;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: currentColor;
  transition: width 0.3s ease;
}

.kpi-card.kpi-orange::before {
  background: linear-gradient(180deg, #f97316 0%, #ea580c 100%);
}

.kpi-card.kpi-purple::before {
  background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%);
}

.kpi-card.kpi-blue::before {
  background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
}

.kpi-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.kpi-card:hover::before {
  width: 6px;
}

/* KPI Icon */
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
}

.kpi-icon.orange {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
  color: #c2410c;
}

.kpi-icon.purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #6d28d9;
}

.kpi-icon.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.kpi-card:hover .kpi-icon {
  transform: scale(1.1) rotate(5deg);
}

/* KPI Content */
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

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
  }

  .kpi-card {
    padding: 1.5rem;
  }

  .kpi-icon {
    width: 56px;
    height: 56px;
  }

  .kpi-number {
    font-size: 2rem;
  }

  .kpi-unit {
    font-size: 1.25rem;
  }
}

@media (max-width: 1024px) {
  .kpi-grid {
    gap: 1rem;
  }

  .kpi-card {
    padding: 1.25rem;
    gap: 1rem;
  }

  .kpi-icon {
    width: 52px;
    height: 52px;
  }

  .kpi-number {
    font-size: 1.75rem;
  }

  .kpi-label {
    font-size: 0.875rem;
  }
}

@media (max-width: 768px) {
  .overview-title {
    font-size: 1.125rem;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .kpi-card {
    padding: 1.25rem;
  }

  .kpi-icon {
    width: 56px;
    height: 56px;
  }

  .kpi-number {
    font-size: 2rem;
  }

  .kpi-label {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .overview-section {
    gap: 1.25rem;
  }

  .overview-title {
    font-size: 1rem;
  }

  .kpi-card {
    padding: 1rem;
    gap: 0.875rem;
    flex-direction: column;
    text-align: center;
  }

  .kpi-icon {
    width: 52px;
    height: 52px;
  }

  .kpi-content {
    align-items: center;
  }

  .kpi-number {
    font-size: 1.75rem;
  }

  .kpi-unit {
    font-size: 1.125rem;
  }

  .kpi-label {
    font-size: 0.85rem;
  }

  .kpi-trend {
    font-size: 0.75rem;
  }
}
</style>
