<template>
  <div class="video-feed">
    <video
      v-if="enabled"
      ref="videoElement"
      autoplay
      muted
      playsinline
      class="video-element mirror"
      aria-label="Your video feed"
    ></video>
    <div v-else class="video-placeholder" aria-label="Video disabled">
      <div class="avatar-large">YOU</div>
    </div>
  </div>
</template>

<script setup>
import { watch, onMounted, ref } from 'vue'

const props = defineProps({
  enabled: {
    type: Boolean,
    default: true
  }
})

const videoElement = ref(null)
let localStream = null

async function startVideo() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720, facingMode: 'user' },
      audio: false
    })
    if (videoElement.value) {
      videoElement.value.srcObject = localStream
    }
  } catch (error) {
    console.error('Error accessing webcam:', error)
  }
}

function stopVideo() {
  if (localStream) {
    localStream.getTracks().forEach(track => track.stop())
    localStream = null
  }
}

watch(
  () => props.enabled,
  (newVal) => {
    if (newVal) startVideo()
    else stopVideo()
  }
)

onMounted(() => {
  if (props.enabled) startVideo()
})
</script>

<style scoped>
.video-feed {
  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mirror {
  transform: scaleX(-1);
}

.video-placeholder {
  width: 100%;
  height: 100%;
  background: #ddd;
  color: #666;
  font-weight: 700;
  font-size: 3rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-large {
  border-radius: 50%;
  width: 120px;
  height: 120px;
  background: #bbb;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  user-select: none;
}
</style>

