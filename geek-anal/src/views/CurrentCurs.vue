<template>
  <v-layout>
    <v-app-bar>
      <v-app-bar-title>
        {{ $route.query.cursName }}
      </v-app-bar-title>
    </v-app-bar>
    <v-main>
      <v-row>
        <v-col>
          <v-container>
            <Line
                aria-label="График"
                id="my-chart-id"
                :data="chartData"
            />
          </v-container>
        </v-col>
        <v-col>
          <v-container>
            <Doughnut
                class="w-50 h-50"
                id="my-doughnut-id"
                :data="chartData2"
            />
          </v-container>
        </v-col>
      </v-row>
      <v-container>
        <v-row v-for="answer in answers">
          <v-col>
            <v-row>
              <v-col>
                <v-card class="pa-2 bg-light-blue" elevation="4">
                  <v-row>
                    <v-col><v-card title="Оценка пользователя" :text="answer.question_1"/></v-col>
                    <v-col><v-card title="Вопрос 2" :text="answer.question_2"/></v-col>
                    <v-col><v-card title="Вопрос 3" :text="answer.question_3"/></v-col>
                    <v-col><v-card title="Вопрос 4" :text="answer.question_4"/></v-col>
                    <v-col><v-card title="Вопрос 5" :text="answer.question_5"/></v-col>
                    <v-col><v-card title="Вопрос 6" :text="answer.question_6"/></v-col>
                  </v-row>
                </v-card>
              </v-col>
              <v-col class="d-flex flex-column" cols="1">
                <v-tooltip text="Релевантность" >
                  <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" :icon="answer.randomRel ? 'mdi-trending-up' : 'mdi-trending-down'" />
                  </template>
                </v-tooltip>
                <v-tooltip text="Позитивный/Негативный">
                  <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" :icon="answer.random ? 'mdi-thumb-up' : 'mdi-thumb-down'" />
                  </template>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import {Line, Doughnut} from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import {onBeforeMount, ref} from "vue";
import router from "@/router";
import axios from "axios";
import * as qs from 'qs'
import {useRoute} from "vue-router";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
)
const chartData = ref({
  labels: ['26.04', '28.04', '29.04', '30.04', '1.05'],
  datasets: [
    {
      label: 'Соотношение позитивных отзывов',
      borderColor: 'lightblue',
      data: [Math.random(), Math.random(), Math.random(), Math.random(), Math.random()],
      borderWidth: 5,
      tension: 0.1,

    }
  ]
})
const chartData2 = ref({
  labels: ['Положительные отзывы', 'Отрицательные отзывы'],
  datasets: [
    {
      label: 'Текущее соотношение позитивных к негативным',
      backgroundColor: ['#47fa42', '#ff2626'],
      data: [chartData.value.datasets[0].data[4], chartData.value.datasets[0].data[2] - 1]
    }
  ]
})
const answers = ref({answers: [{
    user: String,
    question_1: Number,
    created_at: Date,
    course: String,
    question_2: String,
    question_3: String,
    question_4: String,
    question_5: String,
    question_6: String,
    randomRel: Boolean,
    random: Boolean
  }]})
onBeforeMount(() => {
  const route = useRoute();
  axios.get('http://127.0.0.1:8000/answers/course/',
      {
        params:
            {
              course: route.query.cursName, min: 0, limit: 100000
            }
      })
      .then(res => {
        const data = res.data.answers

        answers.value = data.map(item => {
          return {...item, ['randomRel']: Math.round(Math.random()) , ['random']: Math.round(Math.random())}
        })
        console.log(res.data)
      })
})


</script>

<style scoped>

</style>