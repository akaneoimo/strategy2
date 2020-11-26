import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import List from '../views/List.vue';
import Event from '../views/Event.vue';

const operation = {
  title: '操作',
  key: '_operation',
  fixed: 'right',
  width: 100,
  slots: { customRender: 'action' },
};

const topicColumns = [
  {
    title: '序号',
    dataIndex: 'id',
    key: 'id',
    width: 80,
  },
  {
    title: '地区',
    dataIndex: 'region',
    key: 'region',
    width: 150,
  },
  {
    title: '领域',
    dataIndex: 'field',
    key: 'field',
    width: 100,
  },
  {
    title: '议题',
    dataIndex: 'issue',
    key: 'issue',
  },
  {
    title: '话题',
    dataIndex: 'topic',
    key: 'topic',
  },
  {
    title: '主关键字',
    dataIndex: 'main_keywords',
    key: 'mainKeywords',
    ellipsis: true,
  },
  {
    title: '次关键字',
    dataIndex: 'submain_keywords',
    key: 'submainKeywords',
    ellipsis: true,
  },
  {
    title: '二级关键字',
    dataIndex: 'secondary_keywords',
    key: 'secondaryKeywords',
    ellipsis: true,
  },
  {...operation},
];

const strategyColumns = [
  {
    title: '序号',
    dataIndex: 'id',
    key: 'id',
    width: 80,
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
    width: 150,
  },
  {
    title: '定义',
    dataIndex: 'define',
    key: 'define',
    input: 'textarea',
  },
  {...operation},
];

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/admin/topic',
  },
  {
    path: '/admin/topic',
    name: 'Topic',
    component: List,
    props: {
      columns: topicColumns,
      apiUrl: '/api/topics/',
      editable: true,
    },
  },
  {
    path: '/admin/strategy',
    name: 'Strategy',
    component: List,
    props: {
      columns: strategyColumns,
      apiUrl: '/api/strategies/',
      editable: true,
    },
  },
  {
    path: '/event',
    name: 'Event',
    component: Event,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
