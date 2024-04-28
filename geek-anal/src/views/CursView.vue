<template>
  <div class="fill-height d-flex flex-column justify-space-between">
    <v-layout class="flex-column">
      <v-container>
        <curs-filter :query="searchQuery" @updateSearchQuery="updateSearchQuery"></curs-filter>
      </v-container>
      <v-container class="d-flex ga-5 flex-wrap justify-center">
        <some-curs v-for="course in cursNames.course_names" :curs-title="course"/>
      </v-container>
    </v-layout>
    <v-pagination
        v-model="page"
        class="my-4"
    ></v-pagination>
  </div>
</template>

<script setup>
import SomeCurs from "@/components/CursView/SomeCurs.vue";
import {onBeforeMount, ref} from "vue";
import CursFilter from "@/components/CursFilter.vue";
import axios from "axios";
import router from "@/router/";
const page = ref(1)
const searchQuery = ref('333')
const updateSearchQuery = (Query) => {
  console.log(Query)
  searchQuery.value = Query
}
const cursNames = ref({course_names: [
  ]})

onBeforeMount(() => {
 axios.get('http://127.0.0.1:8000/courses/names?skip=0&limit=10000').then(res => {
   cursNames.value = res.data
 })
})
</script>

<style scoped>

</style>