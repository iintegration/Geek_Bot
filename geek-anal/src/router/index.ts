import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/homepage',
      name: 'homepage',
      component: () => import('../views/CursView.vue')
    },
    {
      path: '/curs',
      name: 'curs',
      component: () => import('../views/CurrentCurs.vue')
    }
  ]
})

export default router
