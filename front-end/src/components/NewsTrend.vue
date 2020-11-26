<template>
  <div ref="line"></div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import echarts from 'echarts';
export default defineComponent({
  data() {
    return {
      chart: null as any,
    };
  },
  props: {
    data: {
      type: Array,
    },
  },
  mounted() {
    this.chart = echarts.init(this.$refs.line as HTMLDivElement);
  },
  methods: {
    updateView() {
      this.chart.setOption({
        tooltip: {
          formatter: (params: any) => {
            return `${params.name}: ${params.value}`;
          },
        },
        visualMap: [
          {
            type: 'piecewise',
            pieces: [
              { min: 0, max: 1, color: '#FFFF00' },
              { min: 1, max: 5, color: '#FFD700' },
              { min: 5, max: 10, color: '#FFA500' },
              { min: 10, max: 25, color: '#FF8C00' },
              { min: 25, max: 50, color: '#FF4500' },
              { min: 50, max: 100, color: '#DC143C' },
              { min: 100, max: 200, color: '#B22222' },
              { min: 200, max: 400, color: '#A52A2A' },
              { min: 400, color: '#8B0000' },
            ],
            dimension: 1,
            show: false,
          },
        ],
        xAxis: {
          axisTick: {
            show: false,
          },
          data: this.data!.map((item: any) => item.date),
        },
        yAxis: {
          type: 'value',
        },
        series: [{
          data: this.data!.map((item: any) => {
            return {
              value: item.count,
              symbolSize: 8,
            };
          }),
          type: 'line',
        }],
        grid: {
          left: 30,
          top: 20,
          right: 20,
          bottom: 20,
        },
      });
    },
  },
  watch: {
    data() {
      this.updateView();
    },
  },
});
</script>