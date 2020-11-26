<template>
  <div ref="cloud" ></div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import WordCloud from 'wordcloud';
import _ from 'lodash';

type WordCloudData = [[string, number]];
export default defineComponent({
  props: {
    list: {
      type: Array,
    },
  },
  mounted() {
    this.updateView();
  },
  methods: {
    updateView() {
      WordCloud(this.$refs.cloud as HTMLElement, {
        list: this.normalize(this.list as WordCloudData),
        // hover(item) {
        //   console.log(item);
        // },
        color: 'random-dark',
        // backgroundColor: '#f0f0f0',
        weightFactor: 15 * this.list!.length,
      });
    },
    normalize(data: WordCloudData) {
      const sum = _.sumBy(data, (i) => i[1]);
      return data.map((item) => [item[0], item[1] / sum]);
    },
  },
  watch: {
    list() {
      this.updateView();
    },
  },
});
</script>