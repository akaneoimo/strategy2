<template>
  <div>
    <a-row :key="index" v-for="(strategy, index) in data" :style="{ margin: '10px auto' }">
      <a-col :span="3"><span :style="{ fontWeight: 'bold' }">{{ strategy.name }}</span></a-col>
      <a-col :span="21">{{ strategy.define }}</a-col>
    </a-row>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
export default defineComponent({
  props: {
    data: {
      type: Array,
    },
  },
});
</script>