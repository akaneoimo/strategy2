<template>
  <div class="header">事件应对智能决策系统</div>
  <div>
    <a-menu v-model:selectedKeys="current" mode="horizontal">
      <a-menu-item key="/admin/topic"><router-link to="/admin/topic">话题库</router-link></a-menu-item>
      <a-menu-item key="/admin/strategy"><router-link to="/admin/strategy">策略库</router-link></a-menu-item>
      <a-menu-item key="/event"><router-link to="/event">主题事件</router-link></a-menu-item>
    </a-menu>
  </div>
  <div class="main-content">
    <router-view :key="$route.fullPath"/>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      current: [''],
    };
  },
  mounted() {
    this.current = [this.$route.path || ''];
  },
  watch: {
    $route() {
      this.current = [this.$route.path || ''];
    },
  },
});
</script>

<style lang="scss">
.header {
  width: 100%;
  height: 50px;
  line-height: 50px;
  color: white;
  background-color: black;
  padding-left: 20px;
  font-size: 20px;
}

.main-content {
  padding-left: 20px;
  padding-right: 20px;
}
</style>
