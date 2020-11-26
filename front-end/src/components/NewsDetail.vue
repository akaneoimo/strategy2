<template>
  <a-card :title="data.title">
    <p>{{ data.content }}</p>
  </a-card>
  <a-card>
    <p>
      <span>应对策略</span>
      <span :style="{ float: 'right' }">
        <span :style="{ fontSize: '12px', marginRight: '5px' }">编辑</span>
        <a-switch v-model:checked="editable"></a-switch>
      </span>
    </p>
    
    <div>专家库推荐</div>
    <a-button @click="() => handleRemovePredictStrategy(Number(strategy_id))" :key="index" v-for="(strategy_id, index) in data.predict_strategy_id">{{ strategyMap[strategy_id].name }}</a-button>
    <div>研判策略</div>
    <a-button @click="() => handleRemoveStrategy(Number(strategy_id))" :key="index" v-for="(strategy_id, index) in data.strategy_id">{{ strategyMap[strategy_id].name }}<DeleteOutlined :style="{fontSize: '20px', color: '#dc143c'}" /></a-button>
    
    <div v-if="editable">
      <div>策略库</div>
      <a-button :key="strategy_id" v-for="(strategy, strategy_id) in strategyMap"
        :disabled="data.strategy_id.indexOf(Number(strategy_id)) > -1"
        @click="() => handleAddStrategy(Number(strategy_id))">{{ strategy.name }}</a-button>
    </div>
  </a-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import { DeleteOutlined } from '@ant-design/icons-vue';

export default defineComponent({
  data() {
    return {
      data: {} as any,
      editable: false,
    };
  },
  props: {
    newsid: {
      type: Number,
    },
    strategyMap: {
      type: Object,
    },
  },
  async mounted() {
    const { data } = await axios.get(`/api/news/${this.newsid}`);
    this.data = data.data;
  },
  methods: {
    /* eslint-disable @typescript-eslint/camelcase */
    handleAddStrategy(strategyId: number) {
      this.data.strategy_id.push(strategyId);
      this.updateStrategy();
    },
    handleRemoveStrategy(strategyId: number) {
      const index = this.data.strategy_id.indexOf(strategyId);
      if (index > -1) {
        this.data.strategy_id.splice(index, 1);
        this.updateStrategy();
      }
    },
    handleRemovePredictStrategy(strategyId: number) {
      const index = this.data.predict_strategy_id.indexOf(strategyId);
      if (index > -1) {
        this.data.predict_strategy_id.splice(index, 1);
        this.updateStrategy();
      }
    },
    async updateStrategy() {
      const { data } = await axios.put(`/api/news/${this.newsid}`, this.data);
    },
  },
  components: {
    DeleteOutlined,
  },
});
</script>