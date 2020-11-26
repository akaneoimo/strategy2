<template>
  <div ref="bar"></div>
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
    x: {
      type: Array,
    },
    y: {
      type: Array,
    },
  },
  mounted() {
    this.chart = echarts.init(this.$refs.bar as HTMLDivElement);
  },
  methods: {
    updateView() {
      const maxLen = 6;
      this.chart.setOption({
        tooltip: {
          position: 'right',
          formatter: (params: any) => {
            return `${Number(params.data.value).toFixed(4)}<br/>${params.data.name}`;
          },
          textStyle: {
            fontSize: 12,
          },
        },
        visualMap: [
          {
            type: 'piecewise',
            pieces: [
              { min: 0, max: 0.1, color: '#FFFF00' },
              { min: 0.1, max: 0.2, color: '#FFD700' },
              { min: 0.2, max: 0.3, color: '#FFA500' },
              { min: 0.3, max: 0.4, color: '#FF8C00' },
              { min: 0.4, max: 0.5, color: '#FF4500' },
              { min: 0.5, max: 0.6, color: '#DC143C' },
              { min: 0.6, max: 0.7, color: '#B22222' },
              { min: 0.7, max: 0.8, color: '#A52A2A' },
              { min: 0.8, max: 0.9, color: '#8B0000' },
              { min: 0.9, max: 1, color: '#800000' },
            ],
            dimension: 0,
            show: false,
          },
        ],
        xAxis: {
          type: 'value',
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          min: 0,
          max: 1,
        },
        yAxis: {
          type: 'category',
          data: this.y,
          axisLine: {
            show: false,
          },
          axisTick: {
            show: false,
          },
          axisLabel: {
            formatter: (value: string) => {
              return value;
            },
          },
        },
        series: [{
          data: this.x,
          type: 'bar',
          barMaxWidth: 20,
          barMinHeight: 3,
          itemStyle: {
            color: '#1E90FF',
          },
        }],
        grid: {
          left: maxLen * 14,
          top: 20,
          right: 20,
          bottom: 20,
        },
      });
    },
  },
  watch: {
    x() {
      this.updateView();
    },
  },
});
</script>