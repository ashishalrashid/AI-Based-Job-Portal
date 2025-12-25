<template>
  <aside class="sidebar" role="complementary" aria-label="Interview progress and details">
    <header class="sidebar-header">
      <h3>Interview Progress</h3>
      <button class="close-sidebar-btn" @click="$emit('closeSidebar')" aria-label="Close sidebar">&times;</button>
    </header>

    <div class="sidebar-content">
      <div class="progress-info">
        <p><strong>Questions:</strong> {{ questionCount }}/10</p>
        <p><strong>Duration:</strong> {{ timeElapsed }}</p>
        <p><strong>Progress:</strong> <span>{{ progressPercent?.toFixed(1) || '0.0' }}%</span></p>
        <p>
          <strong>Status:</strong>
          <span v-if="aiSpeaking">AI Speaking</span>
          <span v-else-if="isRecording">Recording</span>
          <span v-else>Idle</span>
        </p>
      </div>

      <div class="progress-bar-container" role="progressbar" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100">
        <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>

      <div v-if="evaluation" class="evaluation-report" tabindex="0">
        <h4>Overall Rating</h4>
        <div class="overall-stars">
          <span v-for="star in 5" :key="star" class="star" :class="{ filled: star <= Math.round(evaluation.overallrating) }" aria-hidden="true">★</span>
          <div class="rating-number" :aria-label="'Rating ' + evaluation.overallrating + ' out of 5'">{{ evaluation.overallrating.toFixed(1) }}</div>
        </div>

        <h4>Key Points</h4>
        <div class="key-points-grid">
          <div class="points-column strengths">
            <h5>Strengths</h5>
            <ul>
              <li v-for="(strength, idx) in evaluation.strengths" :key="'strength' + idx">{{ strength }}</li>
            </ul>
          </div>
          <div class="points-column concerns">
            <h5>Areas of Concern</h5>
            <ul v-if="evaluation.areasofconcern && evaluation.areasofconcern.length > 0">
              <li v-for="(concern, idx) in evaluation.areasofconcern" :key="'concern' + idx">{{ concern }}</li>
            </ul>
            <p v-else>No major concerns identified</p>
          </div>
        </div>

        <h4>Recommendation</h4>
        <div :class="'recommendation-badge ' + (evaluation.recommendation.decision ? evaluation.recommendation.decision.toLowerCase().replace(' ', '-') : '')">
          {{ evaluation.recommendation.decision || 'N/A' }}
        </div>
        <p>{{ evaluation.recommendation.reasoning }}</p>
      </div>
    </div>
  </aside>
</template>

<script setup>

import { ref, computed } from 'vue'
const props = defineProps({
  questionCount: Number,
  timeElapsed: String,
  aiSpeaking: Boolean,
  isRecording: Boolean,
  progressPercent: Number,
  evaluation: Object
})


const safeQuestionCount = computed(() => questionCount || 0)
const safeTimeElapsed = computed(() => timeElapsed || '00:00')
const safeProgressPercent = computed(() => progressPercent || 0)
const safeEvaluation = computed(() => evaluation || null)

</script>

<style scoped>
.sidebar {
  width: 320px;
  background: #fff;
  box-shadow: -4px 0 12px rgb(0 0 0 / 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem 1.5rem;
  overflow-y: auto;
  font-size: 0.95rem;
  color: #334155;
  border-left: 1px solid #e2e8f0;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.close-sidebar-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
}
.progress-info p {
  margin: 0.25rem 0;
}
.progress-bar-container {
  height: 12px;
  background: #e0e7ff;
  border-radius: 8px;
  margin: 1rem 0 1.5rem;
  overflow: hidden;
}
.progress-bar-fill {
  height: 12px;
  background: #6366f1;
  transition: width 0.3s ease;
}
.evaluation-report {
  margin-top: 1rem;
  outline: none;
}

.overall-stars {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  color: #facc15;
}

.star {
  color: #ccc;
}

.star.filled {
  color: #f59e0b;
}

.rating-number {
  font-weight: 600;
  color: #334155;
  font-size: 1.2rem;
}

.key-points-grid {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.points-column {
  flex: 1;
}

.points-column h5 {
  margin-bottom: 0.5rem;
  color: #4b5563;
}

.points-column ul {
  list-style-type: disc;
  padding-left: 1.2rem;
}

.recommendation-badge {
  padding: 0.5rem 1rem;
  font-weight: 700;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 0.5rem;
  color: white;
  width: fit-content;
}
.recommendation-badge.strong-hire {
  background-color: #16a34a;
}
.recommendation-badge.hire {
  background-color: #22c55e;
}
.recommendation-badge.no-hire {
  background-color: #dc2626;
}
.recommendation-badge.maybe {
  background-color: #eab308;
}
</style>

