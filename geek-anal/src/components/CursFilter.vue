<template>
    <v-row align="stretch">
      <v-col class="v-col-lg-4 v-col-md-5">
        <v-combobox
            label="Поиск по"
            :items="['Названию курса', 'Промежутку времени']"
            v-model="searchType"
        ></v-combobox>
      </v-col>
      <v-col class="flex-row d-flex ga-3 justify-center" v-if="searchType == 'Названию курса'" cols="4">
        <v-text-field @keydown.enter="emit('updateSearchQuery', searchQuery)" v-model="searchQuery" label="Название курса"></v-text-field>
        <v-btn @click="emit('updateSearchQuery', searchQuery)" v-ripple rounded text="Поиск" stacked></v-btn>
      </v-col>
      <v-col class="flex-row d-flex ga-3 justify-center" v-if="searchType == 'Промежутку времени'">
        <v-overlay>
          <template v-slot:activator="{props: activatorProps}">
            <v-text-field
                v-model="firstDate"
                v-bind="activatorProps"
                readonly
                label="Выберите число"
            >
            </v-text-field>
          </template>
          <template v-slot:default="{ isActive }">
            <v-row justify="center" align="center">
              <v-col>
                <v-date-picker
                    min="2016-06-15"
                    v-model="firstDate"
                    hide-header
                >
                </v-date-picker>
              </v-col>
            </v-row>
          </template>
        </v-overlay>
      </v-col>
      <v-col class="flex-row d-flex ga-3 justify-center" v-if="searchType == 'Промежутку времени' && firstDate" cols="2">
        <v-overlay>
          <template v-slot:activator="{props: activatorProps}">
            <v-text-field
                v-bind="activatorProps"
                readonly
                label="Выберите число"
                v-model="secondDate"
            >
            </v-text-field>
          </template>
          <template v-slot:default="{ isActive }">
            <v-date-picker
                v-model="secondDate"
            >
            </v-date-picker>
          </template>
        </v-overlay>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-lg-3 v-col-md-4">
        <v-combobox
            label="Сортировка по"
            :items="['Релевантности', 'Дате создания', 'Дате изменения', 'Негативности','Позитивности']"
            v-model="filterType"
        ></v-combobox>
      </v-col>
    </v-row>
</template>

<script setup>

import {computed, ref} from "vue";
import {useDate} from "vuetify";
const searchType = ref('')
const filterType = ref('')
const firstDate = ref(null)
const secondDate = ref(null)
const props = defineProps({
  query: String
})
const searchQuery = ref(props.query)
const emit = defineEmits(['updateSearchQuery'])
const formatDate = (date) => {
  console.log(date)
}
</script>

<style scoped>

</style>