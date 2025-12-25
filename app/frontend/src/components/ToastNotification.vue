<template>
  <transition-group name="toast" tag="div" class="toast-container" aria-live="polite" role="alert">
    <div v-for="toast in toasts" :key="toast.id" :class="['toast', `toast-${toast.type}`]" role="alert" aria-atomic="true">
      <span :class="['toast-icon', toast.icon]"></span>
      <span class="toast-message">{{ toast.message }}</span>
      <button class="toast-close-btn" @click="$emit('removeToast', toast.id)" aria-label="Close notification">&times;</button>
    </div>
  </transition-group>
</template>

<script setup>
const props = defineProps({
  toasts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['removeToast'])
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 10000;
  max-width: 300px;
}

.toast {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  font-size: 0.875rem;
  color: #1f2937;
  position: relative;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

.toast-success {
  border-left: 4px solid #22c55e;
}

.toast-warning {
  border-left: 4px solid #fbbf24;
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-icon {
  margin-right: 0.75rem;
  font-size: 1.25rem;
  user-select: none;
}

.toast-icon.success::before {
  content: '✔';
  color: #22c55e;
}

.toast-icon.error::before {
  content: '✖';
  color: #ef4444;
}

.toast-icon.warning::before {
  content: '⚠';
  color: #fbbf24;
}

.toast-icon.info::before {
  content: 'ℹ';
  color: #3b82f6;
}

.toast-message {
  flex: 1;
}

.toast-close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  margin-left: 0.5rem;
  user-select: none;
}

.toast-close-btn:hover {
  color: #374151;
}

/* Animations */
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
</style>

