<template>
  <v-card style="width: 400px; height: 200px" color="blue" hover @click="router.push({name: 'curs', query: {
    cursName: cursTitle}})">
    <v-card-title>
      {{props.cursTitle}}
    </v-card-title>
    <v-card-item>
      Курс
    </v-card-item>
  </v-card>
</template>

<script setup>
import router from "@/router";
const props = defineProps({
  cursTitle: String
})
</script>

<style scoped>

</style>