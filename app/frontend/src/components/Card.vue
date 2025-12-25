<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <button class="view-all-btn" @click="emit('viewAll')">View All</button>
    </div>
    <div :class="cardContentClass">
      <!-- Activity Items -->
      <template v-if="type === 'activity'">
        <div v-for="(item, i) in items" :key="i" class="activity-item">
          <div class="activity-icon" :class="item.type">
            <span v-html="item.icon"></span>
          </div>
          <div class="activity-details">
            <p class="activity-title">{{ item.title }}</p>
            <p class="activity-time">{{ item.time }}</p>
          </div>
        </div>
        <div v-if="items.length === 0" class="empty-state">
          <p>No activities yet</p>
        </div>
      </template>

      <!-- Leave Request Items -->
      <template v-if="type === 'leave'">
        <div v-for="(item, i) in items" :key="i" class="leave-item">
          <div class="leave-info">
            <p class="leave-name">{{ item.name }}</p>
            <p class="leave-dates">{{ item.dates }}</p>
          </div>
          <div class="leave-actions">
            <button class="action-btn approve" @click="emit('approve', i)">Approve</button>
            <button class="action-btn reject" @click="emit('reject', i)">Reject</button>
          </div>
        </div>
        <div v-if="items.length === 0" class="empty-state">
          <p>No leave requests</p>
        </div>
      </template>

      <!-- Notification Items (generic) -->
      <template v-if="type === 'notification'">
        <div v-for="(item, i) in items" :key="i" class="notification-item">
          <div class="notification-badge" :class="item.priority">
            {{ item.priority.charAt(0).toUpperCase() }}
          </div>
          <div class="notification-content">
            <p class="notification-title">{{ item.title }}</p>
            <p class="notification-desc">{{ item.description }}</p>
            <p class="notification-time">{{ item.time }}</p>
          </div>
          <button v-if="item.action" class="notification-action" @click="emit('action', i)">
            {{ item.action }}
          </button>
        </div>
        <div v-if="items.length === 0" class="empty-state">
          <p>No notifications</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
  type: {
    type: String,
    enum: ['activity', 'leave', 'notification'],
    default: 'activity',
  },
})

const emit = defineEmits(['viewAll', 'approve', 'reject', 'action'])

const cardContentClass = computed(() => {
  switch (props.type) {
    case 'activity':
      return 'activity-list'
    case 'leave':
      return 'leave-list'
    case 'notification':
      return 'notification-list'
    default:
      return ''
  }
})
</script>

<style scoped>
.card {
  background: #fff;
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

.view-all-btn {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  transition: color 0.2s;
}

.view-all-btn:hover {
  text-decoration: underline;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f9fafb;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.success {
  background: #dcfce7;
  color: #10b981;
}

.activity-icon.info {
  background: #dbeafe;
  color: #6366f1;
}

.activity-icon.warning {
  background: #fef3c7;
  color: #f59e0b;
}

.activity-icon.error {
  background: #fee2e2;
  color: #ef4444;
}

.activity-details {
  flex: 1;
}

.activity-title {
  font-size: 0.9rem;
  color: #1e3a5f;
  font-weight: 500;
  margin: 0 0 0.25rem 0;
}

.activity-time {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

/* Leave List */
.leave-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.leave-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  background: #f9fafb;
  transition: all 0.2s;
}

.leave-item:hover {
  background: #f1f5f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.leave-info {
  flex: 1;
}

.leave-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.leave-dates {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.leave-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.approve {
  background: #10b981;
  color: #fff;
}

.action-btn.approve:hover {
  background: #059669;
  transform: translateY(-1px);
}

.action-btn.reject {
  background: #ef4444;
  color: #fff;
}

.action-btn.reject:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Notification List */
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f9fafb;
  border-left: 4px solid #e5e7eb;
  transition: all 0.2s;
}

.notification-item:hover {
  background: #f1f5f9;
  border-left-color: #3b82f6;
}

.notification-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.notification-badge.high {
  background: #fee2e2;
  color: #dc2626;
}

.notification-badge.medium {
  background: #fef3c7;
  color: #d97706;
}

.notification-badge.low {
  background: #dbeafe;
  color: #2563eb;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0.25rem 0;
}

.notification-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.notification-action {
  padding: 0.35rem 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.notification-action:hover {
  background: #2563eb;
}

/* Empty State */
.empty-state {
  padding: 2rem 1rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .card {
    padding: 1rem;
  }

  .card-header {
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
  }

  .card-title {
    font-size: 1rem;
  }

  .action-btn {
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
  }

  .leave-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .leave-actions {
    width: 100%;
  }

  .leave-actions .action-btn {
    flex: 1;
  }

  .notification-item {
    gap: 0.75rem;
  }

  .notification-action {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 0.75rem;
  }

  .activity-item {
    padding: 0.5rem;
    gap: 0.75rem;
  }

  .activity-icon {
    width: 36px;
    height: 36px;
  }

  .activity-title {
    font-size: 0.85rem;
  }

  .notification-item {
    padding: 0.75rem;
  }

  .notification-badge {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
}
</style>
