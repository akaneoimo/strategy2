<template>
  <a-row>
    <span :style="{ float: 'right' }">
      <span :style="{ fontSize: '12px', marginRight: '5px' }">训练模型</span>
      <a-switch v-model:checked="isModelTraining" @change="handleTrain" :disabled="Boolean(modelTrainingStatus !== 0)">训练模型</a-switch>
    </span>
  </a-row>
  <a-row class="title">
    <a-col :span="2" class="title-header">议题</a-col>
    <a-col :span="18">{{ issue }}</a-col>
    <a-col><a-button @click="showIssues" type="primary" :style="{ float: 'right' }">切换议题</a-button></a-col>
  </a-row>
  <a-row class="title">
    <a-col :span="2" class="title-header">话题</a-col>
    <a-col :span="18">{{ topic }}</a-col>
    <a-col><a-button @click="showTopics" type="primary" :style="{ float: 'right' }">切换主题</a-button></a-col>
  </a-row>

  <a-row :style="{ height: '50px', lineHeight: '50px' }">
    <span class="title-header">新闻列表</span>
    <a-space :style="{ float: 'right' }">
      时间范围
      <a-range-picker v-model:value="range"/>
    </a-space>
  </a-row>

  <a-row>
    <List apiUrl="/api/news/" :columns="[{title: '标题', dataIndex: 'title', key: 'title'}]" :showHeader="false"
        :key="topicId + range.toString()"
        :extraQuery="{
          topic_id: topicId,
          start: range[0] && range[0].format('YYYYMMDD') || '',
          end: range[1] && range[1].format('YYYYMMDD') || '',
        }"
        @rowclick="handleNewsClick" />
  </a-row>

  <a-row>
    <a-col :span="12" class="wrapper">
      <a-card title="应对策略">
        <StrategyBar :style="{ height: '200px' }" :x="statisticData" :y="statisticDataY"/>
      </a-card>
    </a-col>
    <a-col :span="12" class="wrapper">
      <a-card title="策略应用">
        <StrategyDetail :style="{ height: '200px' }" :data="strategyDetailData"/>
      </a-card>
    </a-col>
  </a-row>
    
  <a-row>
    <a-col :span="12" class="wrapper">
      <a-card title="词云分析">
        <WordCloud :style="{ height: '200px' }" :list="wordcloudData"/>
      </a-card>
    </a-col>
    <a-col :span="12" class="wrapper">
      <a-card title="主题摘要">
        <Abstract :style="{ height: '200px' }" :data="abstractData" />
      </a-card>
    </a-col>
  </a-row>
  
  <a-row>
    <a-col :span="24" class="wrapper">
      <a-card title="新闻数量趋势变化">
        <NewsTrend :style="{width: '100%', height: '200px'}" :data="newsTrendData"/>
      </a-card>
    </a-col>
  </a-row>

  <a-modal key="news" :width="800" v-model:visible="isNewsModalVisible" :footer="null" :closable="false">
    <NewsDetail :key="newsId" :newsid="newsId" :strategyMap="strategyMap" />
  </a-modal>
  <a-modal key="issue" :width="800" v-model:visible="isIssueModalVisible" :footer="null" :closable="false">
    <List apiUrl="/api/issues/" :columns="[{title: '名称', dataIndex: 'name', key: 'name'}]" :showHeader="false" @rowclick="handleIssueClick"/>
  </a-modal>
  <a-modal key="topic" :width="800" v-model:visible="isTopicModalVisible" :footer="null" :closable="false">
    <List :key="issueId" apiUrl="/api/topics/" :columns="[{title: '话题', dataIndex: 'topic', key: 'topic'}]" :showHeader="false" @rowclick="handleTopicClick"
      :extraQuery="{
        issue_id: issueId
      }"/>
  </a-modal>

</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import _ from 'lodash';
import List from './List.vue';
import WordCloud from '../components/WordCloud.vue';
import StrategyBar from '../components/StrategyBar.vue';
import NewsDetail from '../components/NewsDetail.vue';
import StrategyDetail from '../components/StrategyDetail.vue';
import NewsTrend from '../components/NewsTrend.vue';
import Abstract from '../components/Abstract.vue';
import { Moment } from 'moment';
import { message } from 'ant-design-vue';

type Keyword = [string, number];

type Keysentence = [string, number];

type Statistic = {
  name: string;
  value: number;
};

type Strategy = {
  name: string;
  define: string;
};

type NewsTrend = {
  date: string;
  count: number;
}

type Data = {
  issue: string;
  topic: string;
  issueId: number;
  topicId: number;
  newsId: number;
  isIssueModalVisible: boolean;
  isTopicModalVisible: boolean;
  isNewsModalVisible: boolean;
  range: Moment[];
  strategyMap: {
    [strategyId: number]: {
      name: string;
      define: string;
    };
  };
  statisticData: Statistic[];
  wordcloudData: Keyword[];
  strategyDetailData: Strategy[];
  newsTrendData: NewsTrend[];
  abstractData: Keysentence[];
  modelTrainingStatus: number;
  isModelTraining: boolean;
};

type IssueRecord = {
  id: number;
  name: string;
};

type TopicRecord = {
  id: number;
  topic: string;
  keywords?: Keyword[];
  keysentences?: Keysentence[];
};

type NewsRecord = {
  id: number;
  title: string;
  content: string;
}

export default defineComponent({
  data() {
    return {
      issue: '',
      topic: '',
      issueId: -1,
      topicId: -1,
      newsId: -1,
      isIssueModalVisible: false,
      isTopicModalVisible: false,
      isNewsModalVisible: false,
      range: [],
      strategyMap: {},
      statisticData: [],
      wordcloudData: [],
      strategyDetailData: [],
      newsTrendData: [],
      abstractData: [],
      modelTrainingStatus: -1,
      isModelTraining: false,
    } as Data;
  },
  async mounted() {
    const [
      { data: issueData },
      { data: strategyData },
      { data: trainStatusData },
    ] = await Promise.all([
      axios.get('/api/issues/'),
      axios.get(`/api/strategies/?limit=1000`),
      axios.get('/api/background/train-status'),
    ]);

    this.isModelTraining = Boolean(trainStatusData.data.value);
    this.modelTrainingStatus = trainStatusData.data.value;

    const issueId = issueData.data[0].id;
    const { data: topicData } = await axios.get(`/api/topics/?limit=1&skip=0&issue_id=${issueId}`);
    const topicId = topicData.data[0].id;

    this.issue = issueData.data[0].name;
    this.issueId = issueId;
    this.topic = topicData.data[0].topic;
    this.topicId = topicId;
    this.wordcloudData = topicData.data[0].keywords || [];
    this.abstractData = topicData.data[0].keysentences || [];

    this.strategyMap = strategyData.data.reduce((acc: {
      [strategyId: number]: Strategy;
    }, cur: Strategy & { id: number }) => {
      acc[cur.id] = { name: cur.name, define: cur.define };
      return acc;
    }, {});
  },
  components: {
    List,
    WordCloud,
    StrategyBar,
    NewsDetail,
    StrategyDetail,
    NewsTrend,
    Abstract,
  },
  methods: {
    showIssues() {
      this.isIssueModalVisible = true;
    },
    showTopics() {
      this.isTopicModalVisible = true;
    },
    async handleIssueClick(e: Event, record: IssueRecord) {
      this.issue = record.name;
      this.issueId = record.id;
      try {
        const { data } = await axios.get(`/api/topics/?limit=1&skip=0&issue_id=${record.id}`);
        this.topic = data.data[0].topic;
        this.topicId = data.data[0].id;
        this.wordcloudData = data.data[0].keywords || [];
        this.abstractData = data.data[0].keysentences || [];
      } finally {
        this.isIssueModalVisible = false;
      }
    },
    handleTopicClick(e: Event, record: TopicRecord) {
      this.topic = record.topic;
      this.topicId = record.id;
      this.wordcloudData = record.keywords || [];
      this.abstractData = record.keysentences || [];
      console.log(record);
      this.isTopicModalVisible = false;
    },
    handleNewsClick(e: Event, record: NewsRecord) {
      this.newsId = record.id;
      this.isNewsModalVisible = true;
    },
    async updateStatistic(topicId: number, topN = 5) {
      const { data: statisticData } = await axios.get(`/api/statistic/strategy/${topicId}?${new URLSearchParams({
        start: this.range[0] && this.range[0].format('YYYYMMDD') || '',
        end: this.range[1] && this.range[1].format('YYYYMMDD') || '',
      })}`);
      const slice = statisticData.data.slice(0, topN) as Array<{
        id: number;
        count: number;
      }>;
      const sum = _.sumBy(slice, (i) => i.count);
      this.statisticData = _.reverse(slice.map((item) => ({ name: this.strategyMap[item.id].name, value: item.count / sum })));
      this.strategyDetailData = slice.map((item) => ({ name: this.strategyMap[item.id].name, define: this.strategyMap[item.id].define }));
      const { data: newsTrendData } = await axios.get(`/api/statistic/newstrend/${topicId}?${new URLSearchParams({
        start: this.range[0] && this.range[0].format('YYYYMMDD') || '',
        end: this.range[1] && this.range[1].format('YYYYMMDD') || '',
      })}`);
      this.newsTrendData = newsTrendData.data;
    },
    async handleTrain(value: boolean) {
      this.modelTrainingStatus = Number(value);
      if (value) {
        try {
          const { data } = await axios.post('/api/background/train');
          if (data.code === 0) {
            message.success(data.data.message);
          } else {
            message.error(data.data.message);
          }
        } catch (err) {
          message.error(err.message);
        }
      }
    },
  },
  watch: {
    range() {
      this.updateStatistic(this.topicId);
    },
    topicId() {
      this.updateStatistic(this.topicId);
    },
  },
  computed: {
    statisticDataY(): string[] {
      return this.statisticData.map(item => item.name);
    },
  },
});
</script>

<style lang="scss" scoped>
.title {
  padding-top: 10px;
  padding-bottom: 10px;
}

.title-header {
  font-weight: bold;
}

.wrapper {
  padding: 20px 20px;
}
</style>