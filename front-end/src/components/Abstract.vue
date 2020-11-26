<template>
  <div>
    <a-row :key="index" v-for="(sentence, index) in data" :style="{ margin: '10px auto' }">
      {{ sentence[0] }}
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