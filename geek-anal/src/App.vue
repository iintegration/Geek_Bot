<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import {ref} from "vue";
</script>

<template>
  <v-app class="fill-height">
      <RouterView />
  </v-app>
</template>

<style scoped>

</style>
