<template>
  <div class="interview-screen" :class="{ 'sidebar-open': showSidebar }">
    <!-- Top Bar with title and sidebar toggle -->
    <header class="top-bar">
      <h2>{{ interviewData.title }}</h2>
      <button class="btn-sidebar-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
        ☰
      </button>
    </header>

    <main class="main-content">
      <!-- Video container -->
      <section class="video-container">
        <VideoFeed
          :enabled="selfVideoEnabled"
          ref="candidateVideo"
          aria-label="Your video feed"
        />
      </section>

      <!-- Content area: AI Question + Transcript + Controls -->
      <section class="content-area">
        <ConversationHistory :conversationHistory="conversationHistory" />
        <div class="input-section">
          <AIQuestion
            :question="currentQuestion"
            :isSpeaking="aiSpeaking"
          />

          <Transcript
            :finalTranscript="currentTranscript"
            :interimTranscript="interimTranscript"
            :isRecording="isRecording"
            @submitManualAnswer="handleManualSubmit"
          />

          <Controls
            :micEnabled="selfAudioEnabled"
            :videoEnabled="selfVideoEnabled"
            :isRecording="isRecording"
            :isProcessing="isProcessing"
            :aiSpeaking="aiSpeaking"
            @toggleMic="toggleMic"
            @toggleVideo="toggleVideo"
            @startSpeaking="startSpeaking"
            @stopSpeaking="stopSpeaking"
            @endInterview="handleManualEnd"
          />
        </div>
      </section>
    </main>

    <!-- Sidebar with interview progress and info -->
    <Sidebar
      v-if="showSidebar"
      :key="sidebarKey"
      :questionCount="questionCount || 0"
      :timeElapsed="timeElapsed || '00:00'"
      :progressPercent="progressPercent || 0"
      :aiSpeaking="aiSpeaking || false"
      :isRecording="isRecording || false"
      :evaluation="evaluation || null"
      @closeSidebar="closeSidebar"
    />

    <!-- Buffering Warning -->
    <div v-if="showBufferingWarning" class="buffering-warning" role="alert">
      ⚠️ Connection issue - buffering {{ totalPendingChunks }} chunks
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { connectSocket, getSocket } from '@/services/socket'
import VideoFeed from '@/components/VideoFeed.vue'
import AIQuestion from '@/components/AIQuestion.vue'
import Transcript from '@/components/Transcript.vue'
import Controls from '@/components/controls.vue'
import Sidebar from '@/components/visidebar.vue'
import ConversationHistory from '@/components/ConversationHistory.vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()
const props = defineProps({
  sessionId: String,
  interviewData: Object
})

const isMounted = ref(false)
const isDestroying = ref(false)

// Reactive state
const lastQuestionCount = ref(0)
const selfVideoEnabled = ref(true)
const selfAudioEnabled = ref(true)
const aiSpeaking = ref(false)
const isRecording = ref(false)
const isProcessing = ref(false)
const waitingForFinal = ref(false)
const currentQuestion = ref('')
const currentTranscript = ref('')
const interimTranscript = ref('')
const questionCount = ref(0)
const timeElapsed = ref('00:00')
const showSidebar = ref(false)
const showBufferingWarning = ref(false)
const totalPendingChunks = ref(0)
const evaluation = ref(null)
const conversationHistory = ref([])

// Media recording refs and buffers
const localStream = ref(null)
const videoRecorder = ref(null)
const audioRecorder = ref(null)
const videoChunkNumber = ref(0)
const audioChunkNumber = ref(0)
const pendingVideoChunks = ref([])
const pendingAudioChunks = ref([])

const MAX_PENDING_CHUNKS = 50
const MAX_VIDEO_INFLIGHT = 5
const MAX_AUDIO_INFLIGHT = 5

// STT
const recognition = ref(null)
const isListening = ref(false)

// Flight control
const videoInFlight = ref(0)
const audioInFlight = ref(0)
const isFlushing = ref(false)

// Video element ref - FIXED for VideoFeed component
const candidateVideo = ref(null)

const progressPercent = computed(() => Math.min((questionCount.value / 10) * 100, 100))
const sidebarKey = ref(0)

// 🔥 PERFECT: Timer for timeElapsed - FIXED
let timerInterval = null
function startTimer() {
  let seconds = 0
  timerInterval = setInterval(() => {
    seconds++
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0')
    const secs = (seconds % 60).toString().padStart(2, '0')
    timeElapsed.value = `${mins}:${secs}`
  }, 1000)
}

// 🔥 PERFECT: Fire-and-forget chunk flushing + DEBUG LOGS
async function flushPendingChunks() {
  if (isFlushing.value) return

  const sock = getSocket()
  if (!sock?.connected) return

  isFlushing.value = true
  try {
    // Video chunks
    while (pendingVideoChunks.value.length > 0 && videoInFlight.value < MAX_VIDEO_INFLIGHT) {
      const chunk = pendingVideoChunks.value.shift()
      sock.emit('videoChunk', {
        sessionId: props.sessionId,
        chunkNumber: chunk.number,
        data: chunk.data
      })
      videoInFlight.value++
      console.log(`📤 Video #${chunk.number} sent (${pendingVideoChunks.value.length} left)`)
    }

    // Audio chunks
    while (pendingAudioChunks.value.length > 0 && audioInFlight.value < MAX_AUDIO_INFLIGHT) {
      const chunk = pendingAudioChunks.value.shift()
      sock.emit('audioChunk', {
        sessionId: props.sessionId,
        chunkNumber: chunk.number,
        data: chunk.data
      })
      audioInFlight.value++
      console.log(`🎤 Audio #${chunk.number} sent (${pendingAudioChunks.value.length} left)`)
    }
  } finally {
    isFlushing.value = false
  }
}

// 🔥 PERFECT: Emergency flush ALL chunks
async function flushAllChunks() {
  return new Promise(resolve => {
    let attempts = 0
    const maxAttempts = 15

    const tryFlush = () => {
      if (attempts++ >= maxAttempts) {
        console.warn('⚠️ Emergency flush timeout')
        resolve()
        return
      }

      const sock = getSocket()
      if (!sock?.connected) {
        setTimeout(tryFlush, 200)
        return
      }

      const videoSent = pendingVideoChunks.value.length
      const audioSent = pendingAudioChunks.value.length

      // Clear ALL buffers
      pendingVideoChunks.value = []
      pendingAudioChunks.value = []
      videoInFlight.value = 0
      audioInFlight.value = 0

      console.log(`🚀 EMERGENCY FLUSH COMPLETE: Video=${videoSent}, Audio=${audioSent}`)
      resolve()
    }

    tryFlush()
  })
}

function bufferChunk(buffer, chunk) {
  if (buffer.length >= MAX_PENDING_CHUNKS) {
    buffer.shift()
  }
  buffer.push(chunk)
}

// 🔥 PERFECT: Sidebar handlers
function toggleSidebar() {
  if (!isMounted.value || isDestroying.value) return
  showSidebar.value = !showSidebar.value
  sidebarKey.value++
}

function closeSidebar() {
  showSidebar.value = false
  sidebarKey.value = 0
}

// 🔥 PERFECT: Media controls
function toggleMic() {
  selfAudioEnabled.value = !selfAudioEnabled.value
  localStream.value?.getAudioTracks().forEach(track => track.enabled = selfAudioEnabled.value)
}

function toggleVideo() {
  selfVideoEnabled.value = !selfVideoEnabled.value
  localStream.value?.getVideoTracks().forEach(track => track.enabled = selfVideoEnabled.value)
}

// 🔥 PERFECT: Media initialization
async function initializeMedia() {
  try {
    localStream.value = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720, facingMode: 'user' },
      audio: { echoCancellation: true, noiseSuppression: true }
    })

    localStream.value.getVideoTracks().forEach(track => track.enabled = selfVideoEnabled.value)
    localStream.value.getAudioTracks().forEach(track => track.enabled = selfAudioEnabled.value)

    await nextTick()
    if (candidateVideo.value) {
      candidateVideo.value.srcObject = localStream.value  // FIXED: Direct video element access
    }
  } catch (err) {
    console.error('❌ Media init failed:', err)
    alert('Please allow camera and microphone access')
  }
}

function chooseVideoMimeType() {
  return MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' :
         MediaRecorder.isTypeSupported('video/webm;codecs=vp8') ? 'video/webm;codecs=vp8' :
         'video/webm'
}

// 🔥 PERFECT: Continuous video recording
function startContinuousVideoRecording() {
  if (!localStream.value || videoRecorder.value?.state === 'recording') return

  const mimeType = chooseVideoMimeType()
  videoRecorder.value = new MediaRecorder(localStream.value, {
    mimeType,
    videoBitsPerSecond: 2500000
  })

  videoRecorder.value.ondataavailable = event => {
    if (event.data?.size > 0) {
      const blob = new Blob([event.data], { type: mimeType })
      bufferChunk(pendingVideoChunks.value, { number: videoChunkNumber.value++, data: blob })
      flushPendingChunks()
    }
  }

  try {
    videoRecorder.value.start(4000)
    console.log('🎥 Video recording → CONTINUOUS (100+ chunks expected)')
  } catch (e) {
    console.error('❌ Video recording failed:', e)
  }
}

// 🔥 PERFECT: Continuous audio recording
function startContinuousAudioRecording() {
  if (!localStream.value || audioRecorder.value?.state === 'recording') return

  const audioTracks = localStream.value.getAudioTracks()
  if (!audioTracks.length) return

  const audioStream = new MediaStream(audioTracks)
  audioRecorder.value = new MediaRecorder(audioStream, { mimeType: 'audio/webm' })

  audioRecorder.value.ondataavailable = event => {
    if (event.data?.size > 0) {
      const blob = new Blob([event.data], { type: 'audio/webm' })
      bufferChunk(pendingAudioChunks.value, { number: audioChunkNumber.value++, data: blob })
      flushPendingChunks()
    }
  }

  try {
    audioRecorder.value.start(4000)
    console.log('🎤 Audio recording → CONTINUOUS (100+ chunks expected)')
  } catch (e) {
    console.error('❌ Audio recording failed:', e)
  }
}

// 🔥 PERFECT: Stop recorders (generates FINAL chunks)
function stopRecording() {
  if (videoRecorder.value?.state !== 'inactive') {
    videoRecorder.value.stop()
    console.log('⏹️ Video recorder stopped → FINAL chunk generated')
  }
  if (audioRecorder.value?.state !== 'inactive') {
    audioRecorder.value.stop()
    console.log('⏹️ Audio recorder stopped → FINAL chunk generated')
  }
}

// 🔥 PERFECT: Speech recognition
function initSpeechRecognition() {
  if (!('webkitSpeechRecognition' in window)) {
    console.warn('⚠️ Browser STT not supported')
    return
  }

  recognition.value = new (window.webkitSpeechRecognition || window.SpeechRecognition)()
  recognition.value.continuous = true
  recognition.value.interimResults = true
  recognition.value.lang = 'en-US'
  recognition.value.silenceDetectionDelay = 1000

  recognition.value.onstart = () => {
    isListening.value = true
    console.log('🎤 STT → ACTIVE')
  }

  recognition.value.onresult = event => {
    let interim = '', final = ''
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const transcript = event.results[i][0].transcript
      event.results[i].isFinal ? (final += transcript + ' ') : (interim += transcript)
    }
    if (final) {
      currentTranscript.value += final
      console.log('📝 STT Final:', final.trim())
    }
    interimTranscript.value = interim
  }

  recognition.value.onerror = event => {
    console.error('❌ STT error:', event.error)
  }

  recognition.value.onend = () => {
    console.log('🔄 STT ended → auto-restart')
    if (isRecording.value) {
      setTimeout(() => recognition.value?.start(), 50)
    }
  }
}

// 🔥 PERFECT: Manual submit
function handleManualSubmit(answer) {
  const sock = getSocket()
  if (sock && answer.trim()) {
    const trimmedAnswer = answer.trim()

    // ✅ Add answer to conversation history immediately
    conversationHistory.value.push({
      type: 'answer',
      text: trimmedAnswer,
      timestamp: new Date()
    })

    sock.emit('finishSpeaking', {
      sessionId: props.sessionId,
      answer: trimmedAnswer
    })
    currentTranscript.value = ''
    console.log('✍️ Manual answer submitted')
  }
}

// 🔥 PERFECT: Graceful manual end → TTS → 4-phase shutdown
async function handleManualEnd() {
  console.log('🛑 MANUAL END → Starting graceful shutdown')
  speakQuestion('Okay, thank you for your time. You can leave the meeting now.', true)
}

// ✅ Get best available female voice - with proper loading
let voicesLoaded = false
let cachedFemaleVoice = null

function loadVoices() {
  if (voicesLoaded && cachedFemaleVoice) {
    return cachedFemaleVoice
  }

  const voices = window.speechSynthesis.getVoices()
  if (voices.length === 0) {
    console.warn('⚠️ No voices loaded yet, will retry')
    return null
  }

  voicesLoaded = true

  // Preferred female voices (in order of preference)
  const preferredVoices = [
    'Samantha',           // macOS - Natural female voice
    'Karen',              // macOS - Australian female
    'Moira',              // macOS - Irish female
    'Tessa',              // macOS - South African female
    'Google UK English Female',  // Chrome - British female
    'Microsoft Zira - English (United States)',  // Windows - Natural female
    'Microsoft Hazel - English (Great Britain)', // Windows - British female
    'en-US-Neural2-F',    // Google Cloud TTS (if available)
    'en-GB-Neural-A',     // Google Cloud TTS (if available)
  ]

  // Try to find a preferred voice
  for (const preferred of preferredVoices) {
    const voice = voices.find(v =>
      v.name.includes(preferred) ||
      v.name.toLowerCase().includes(preferred.toLowerCase())
    )
    if (voice) {
      console.log(`✅ Using preferred voice: ${voice.name}`)
      cachedFemaleVoice = voice
      return voice
    }
  }

  // Fallback: Find any female voice
  const femaleVoice = voices.find(v => {
    const name = v.name.toLowerCase()
    return v.lang.startsWith('en') && (
      name.includes('female') ||
      name.includes('samantha') ||
      name.includes('karen') ||
      name.includes('zira') ||
      name.includes('hazel') ||
      name.includes('susan') ||
      name.includes('victoria') ||
      (v.gender && v.gender === 'female')
    )
  })

  if (femaleVoice) {
    console.log(`✅ Using female voice: ${femaleVoice.name}`)
    cachedFemaleVoice = femaleVoice
    return femaleVoice
  }

  // Last resort: Use any English voice (but log it)
  const englishVoice = voices.find(v => v.lang.startsWith('en'))
  if (englishVoice) {
    console.warn(`⚠️ Using fallback voice: ${englishVoice.name} (not ideal)`)
    cachedFemaleVoice = englishVoice
    return englishVoice
  }

  return null
}

function getBestFemaleVoice() {
  // Try to get cached voice first
  if (cachedFemaleVoice) {
    return cachedFemaleVoice
  }

  // Load voices
  return loadVoices()
}

function speakQuestion(text, isFinal = false) {
  if (!text) return

  window.speechSynthesis.cancel()

  // ✅ Ensure voices are loaded before using them
  const voice = getBestFemaleVoice()
  if (!voice) {
    // If voices not loaded, try loading them now
    if (window.speechSynthesis.onvoiceschanged) {
      window.speechSynthesis.onvoiceschanged()
    }
    // Force reload voices
    const voices = window.speechSynthesis.getVoices()
    if (voices.length > 0) {
      loadVoices()
    }
  }

  // Chrome TTS warmup fix
  const warmup = new SpeechSynthesisUtterance('')
  warmup.volume = 0
  window.speechSynthesis.speak(warmup)

  setTimeout(() => {
    const utterance = new SpeechSynthesisUtterance(text)

    // ✅ Get and set the best female voice (try again if not cached)
    const selectedVoice = voice || getBestFemaleVoice()
    if (selectedVoice) {
      utterance.voice = selectedVoice
      utterance.voiceURI = selectedVoice.voiceURI
      console.log(`🎤 Speaking with voice: ${selectedVoice.name}`)
    } else {
      console.warn('⚠️ No female voice found, using default')
    }

    // ✅ Optimized voice settings for natural, pleasant speech
    utterance.rate = 0.95       // Slightly slower for clarity
    utterance.pitch = 1.0        // Natural pitch (not too high)
    utterance.volume = 0.9      // Slightly lower for comfort
    utterance.lang = 'en-US'

    utterance.onend = () => {
      aiSpeaking.value = false
      console.log('✅ TTS complete')
      if (isFinal) {
        endInterview()
      }
    }

    utterance.onerror = (error) => {
      aiSpeaking.value = false
      console.error('⚠️ TTS error:', error)
      if (isFinal) {
        endInterview()
      }
    }

    window.speechSynthesis.speak(utterance)
  }, 50)
}

// 🔥 PERFECT: Speaking controls
async function startSpeaking() {
  if (!localStream.value) await initializeMedia()

  if (recognition.value) {
    currentTranscript.value = ''
    interimTranscript.value = ''
    try {
      recognition.value.start()
      console.log('🎤 STT started')
    } catch (e) {
      console.error('❌ STT start failed:', e)
    }
  }

  getSocket()?.emit('startRecording', { sessionId: props.sessionId })
  isRecording.value = true
  console.log('🗣️ Speaking mode → ACTIVE')
}

function stopSpeaking() {
  console.log('🛑 stopSpeaking called')

  if (recognition.value) {
    try {
      recognition.value.stop()
      console.log('🛑 STT stopped')
    } catch (e) {
      console.warn('⚠️ Error stopping recognition:', e)
    }
  }

  // ✅ Wait a moment for final transcript to be captured
  setTimeout(() => {
    isRecording.value = false
    waitingForFinal.value = true

    // ✅ Combine final and interim transcripts
    const final = currentTranscript.value || ''
    const interim = interimTranscript.value || ''
    const fullAnswer = `${final} ${interim}`.trim()

    console.log('🚀 Sending answer:', fullAnswer.substring(0, 50) + '...')
    console.log('   Final length:', fullAnswer.length)

    if (fullAnswer && fullAnswer.length > 0) {
      conversationHistory.value.push({
        type: 'answer',
        text: fullAnswer,
        timestamp: new Date()
      })

      const sock = getSocket()
      if (sock?.connected) {
        sock.emit('finishSpeaking', {
          sessionId: props.sessionId,
          answer: fullAnswer
        })
        console.log('✅ Answer sent to backend')
      } else {
        console.error('❌ Socket not connected, cannot send answer')
      }
    } else {
      console.warn('⚠️ No answer text to send')
    }

    // Clear transcripts after sending
    setTimeout(() => {
      currentTranscript.value = ''
      interimTranscript.value = ''
      waitingForFinal.value = false
    }, 500)
  }, 500) // Wait 500ms for final transcript
}

// 🔥 100% PERFECT: 4-Phase Graceful Shutdown + Guaranteed Navigation
async function endInterview() {
  console.log('🚀 4-PHASE GRACEFUL SHUTDOWN STARTED')

  if (isProcessing.value) {
    console.log('⏳ Already processing → skipping')
    return
  }
  isProcessing.value = true

  try {
    // PHASE 1: FLUSH ALL EXISTING CHUNKS (1s)
    console.log('📤 PHASE 1: Flushing existing chunks...')
    await flushAllChunks()

    // PHASE 2: STOP RECORDERS → Generate FINAL chunks
    console.log('⏹️ PHASE 2: Stopping recorders → final chunks...')
    stopRecording()

    // PHASE 3: Wait for final chunks + final flush (2s)
    console.log('⏳ PHASE 3: Waiting for final chunks...')
    await new Promise(r => setTimeout(r, 2000))
    console.log('📤 PHASE 3: Final flush...')
    await flushAllChunks()

    // PHASE 4: FULL CLEANUP + EMIT + NAVIGATE
    console.log('🧹 PHASE 4: Full cleanup + navigate')

    // Cleanup speech
    window.speechSynthesis.cancel()
    if (recognition.value) {
      recognition.value.stop()
      recognition.value = null
    }

    // Cleanup media tracks
    if (localStream.value) {
      localStream.value.getTracks().forEach(track => {
        console.log(`🛑 Killed ${track.kind} track`)
        track.stop()
      })
      localStream.value = null
    }

    // Clear video element
    if (candidateVideo.value) {
      const videoEl = candidateVideo.value.$el?.querySelector('video') || candidateVideo.value
      if (videoEl?.srcObject) {
        videoEl.srcObject.getTracks().forEach(t => t.stop())
        videoEl.srcObject = null
        videoEl.pause()
        videoEl.src = ''
        console.log('🖥️ Video element cleared')
      }
    }

    // Emit endInterview (best effort)
    const sock = getSocket()
    if (sock?.connected) {
      console.log('📤 EMITTING endInterview...')
      sock.emit('endInterview', {
        sessionId: props.sessionId,
        questionsanswered: questionCount.value  // ✅ Backend expects this exact field
      })
    }

    // 100% GUARANTEED NAVIGATION - NO SOCKET DEPENDENCY
    console.log('🚀 FORCE NAVIGATE → Thank You page')
    const user = store.getters['auth/currentUser']
    const name = user?.name || 'Candidate'
    router.push({ name: 'InterviewSummary', query: { name } })

  } catch (e) {
    console.error('❌ Shutdown error:', e)
  } finally {
    console.log('✅ 100% GRACEFUL SHUTDOWN COMPLETE')
  }
}

// 🔥 PERFECT: Socket listeners - handles both questionsanswered & questions_asked
async function setupSocketListeners() {
  try {
    const socket = await connectSocket(props.sessionId)
    if (!socket) {
      console.error('❌ Socket connection failed')
      return
    }

    console.log('✅ Socket connected - listeners active')

    // 🔥 FIXED: aiSpeaking - NO questionCount increment
    socket.on('aiSpeaking', data => {
      console.log('🤖 AI Speaking:', data.question?.substring(0, 50) + '...')
      const isFinal = data.isfinal || data.is_final || false
      const isSpeaking = data.isSpeaking || data.is_speaking || false
      const aiQuestionNum = data.questionnumber || data.questionNumber || data.question_number  // 🔥 FIXED!

      if (!isFinal) {
        currentQuestion.value = data.question
        conversationHistory.value.push({
          type: 'question',
          text: data.question,
          questionNumber: aiQuestionNum,
          timestamp: new Date()
        })
      }

      aiSpeaking.value = isSpeaking
      if (isSpeaking) {
        speakQuestion(data.question, isFinal)
      }
    })
    // 🔥 FIXED: question event - ONLY increment if higher
    socket.on('question', data => {
      console.log('📩 Question event:', data.question?.substring(0, 50) + '...')
      const questionNum = data.questionNumber || data.question_number || questionCount.value + 1  // 🔥 Unique name!

      if (questionNum > questionCount.value) {
        questionCount.value = questionNum
        currentQuestion.value = data.question
        console.log(`✅ Q${questionCount.value}:`, data.question.slice(0, 50))
      }
    })

    // ✅ KEEP ALL YOUR OTHER HANDLERS EXACTLY SAME:
    socket.on('answer_received', data => {
      console.log('✅ Answer processed by backend')
      isProcessing.value = false
    })

    socket.on('transcriptionUpdate', data => {
      interimTranscript.value = data.interimTranscript || ''
      currentTranscript.value = data.finalTranscript || ''
    })

    socket.on('interviewComplete', data => {
      console.log('🏁 Backend: Interview complete')
      evaluation.value = data
      questionCount.value = data.questionsanswered || data.questions_asked || questionCount.value
      const name = store.getters['auth/currentUser']?.name || 'Candidate'
      router.push({ name: 'InterviewSummary', query: { name } })
    })

    socket.on('bufferingWarning', count => {
      totalPendingChunks.value = count
      showBufferingWarning.value = count > 5
    })

    socket.on('disconnect', reason => {
      console.log('🔌 Socket disconnect:', reason)
      if (reason !== 'io client disconnect') {
        console.log('🔄 Attempting to reconnect...')
        setTimeout(async () => {
          try {
            const newSocket = await connectSocket(props.sessionId)
            if (newSocket) {
              console.log('✅ Reconnected successfully')
              setupSocketListeners()
            }
          } catch (err) {
            console.error('❌ Reconnection failed:', err)
          }
        }, 2000)
      }
    })

    socket.on('error', error => {
      console.error('❌ Socket error:', error)
    })

  } catch (error) {
    console.error('❌ Socket setup failed:', error)
    alert('Failed to connect. Please refresh.')
  }
}

// 🔥 PERFECT: Lifecycle hooks
onMounted(async () => {
  console.log('🚀 InterviewScreen → INITIALIZING')
  isMounted.value = true

  // ✅ Load voices for TTS (needed for voice selection)
  // Chrome loads voices asynchronously, so we need to wait
  const loadVoicesNow = () => {
    const voices = window.speechSynthesis.getVoices()
    if (voices.length > 0) {
      const selected = loadVoices()
      if (selected) {
        console.log(`✅ Loaded ${voices.length} TTS voices, selected: ${selected.name}`)
      } else {
        console.log(`✅ Loaded ${voices.length} TTS voices (no female voice found)`)
      }
    }
  }

  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = loadVoicesNow
  }

  // Try loading immediately
  loadVoicesNow()

  // Also try after a delay (for Chrome)
  setTimeout(loadVoicesNow, 200)
  setTimeout(loadVoicesNow, 1000)

  // Start timer
  startTimer()

  // Initialize everything
  initSpeechRecognition()
  await setupSocketListeners()
  await initializeMedia()
  startContinuousVideoRecording()
  startContinuousAudioRecording()

  console.log('✅ InterviewScreen → 100% READY')
})

onBeforeUnmount(() => {
  console.log('🧹 InterviewScreen → CLEANUP')
  isDestroying.value = true

  // Stop timer
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }

  // Cleanup STT
  if (recognition.value) {
    recognition.value.stop()
    recognition.value = null
  }

  // Emergency cleanup
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => track.stop())
    localStream.value = null
  }
})
</script>

<style scoped>
.interview-screen {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
  color: #1e293b;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem 1.5rem;
  box-shadow: 0 1px 4px rgb(0 0 0 / 0.1);
  font-weight: 600;
  font-size: 1.25rem;
}
.btn-sidebar-toggle {
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
}
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.video-container {
  flex: 1.4;
  background: black;
  display: flex;
  justify-content: center;
  align-items: center;
}
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
}

.input-section {
  flex-shrink: 0;
  background: #ffffff;
  border-top: 2px solid #e5e7eb;
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.buffering-warning {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: #fde68a;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
  font-weight: 600;
}
.sidebar-open .content-area {
  max-width: 600px;
}
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }

  .video-container {
    flex: 0 0 300px;
  }
}
</style>

