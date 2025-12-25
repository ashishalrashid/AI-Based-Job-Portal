<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

onMounted(() => {
  // Safely dispatch theme init if available
  // This is already called in main.js, no need to call it twice.
  /*
  try {
    if (store) {
      store.dispatch('theme/initTheme')
    }
  } catch {
    // ignore any errors during startup
  }
  */
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

/* REMOVED the duplicate 'body' style block that was here.

  The correct 'body' styling (with theme variables)
  is already in frontend/src/assets/styles/global.css
  and will now be applied correctly.
*/

#app {
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>
