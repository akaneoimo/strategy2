<template>
  <a-row v-if="editable">
    <a-button type="primary" :style="{float: 'right'}" @click="handleAdd"><PlusCircleOutlined/>新增</a-button>
  </a-row>
  <a-table :customRow="customRow" :columns="columns" :dataSource="dataSource" :pagination="pagination" @change="handleTableChange" :loading="isLoading" :showHeader="showHeader">
    <template #action="{record}">
      <a @click="() => showEditModal(record)"><EditOutlined :style="{fontSize: '20px'}"/></a>
      <a @click="() => showDeleteModal(record)"><DeleteOutlined :style="{fontSize: '20px', color: '#dc143c'}" /></a>
    </template>
  </a-table>
  <a-modal v-model:visible="isModalVisible" :closable="false" :onOk="addNewData">
    <a-row v-for="(column, i) of editableColumns" :key="i">
      <a-input v-if="column.input !== 'textarea'" :addonBefore="column.title" v-model:value="newData[column.dataIndex]"></a-input>
      <a-textarea v-else :placeholder="column.title" v-model:value="newData[column.dataIndex]"></a-textarea>
    </a-row>
  </a-modal>
  <a-modal v-model:visible="isEditModalVisible" :closable="false" :onOk="editData">
    <a-row v-for="(column, i) of editableColumns" :key="i">
      <a-input v-if="column.input !== 'textarea'" :addonBefore="column.title" v-model:value="activeRecord[column.dataIndex]"></a-input>
      <a-textarea v-else :placeholder="column.title" v-model:value="activeRecord[column.dataIndex]"></a-textarea>
    </a-row>
  </a-modal>
  <a-modal v-model:visible="isDeleteModalVisible" :closable="false" :onOk="deleteData">
    确定要删除吗？
  </a-modal>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import { PlusCircleOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

type Item = {
  region: string;
  field: string;
  issue: string;
  topic: string;
  main_keywords: string;
  submain_keywords: string;
  secordary_keywords: string;
};

type PaginationOptions = {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  pageSizeOptions?: string[];
  showTotal?: (total: number) => string;
};

export default defineComponent({
  data() {
    return {
      dataSource: [],
      pagination: {
        current: 1,
        pageSize: 5,
        total: 0,
        showSizeChanger: true,
        pageSizeOptions: ['5', '10', '20'],
        showTotal(total: number) {
          return `共${total}项`;
        },
      },
      isLoading: true,
      isModalVisible: false,
      isEditModalVisible: false,
      isDeleteModalVisible: false,
      newData: {} as any,
      activeRecord: {id: 0},
    };
  },
  async mounted() {
    await this.fetchData();
  },
  props: {
    columns: Array,
    apiUrl: String,
    extraQuery: {
      type: Object,
      default: () => {
        return {};
      },
    },
    editable: {
      type: Boolean,
      default: false,
    },
    showHeader: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    async fetchData() {
      this.isLoading = true;
      try {
        const { pageSize, current } = this.pagination;
        const { data } = await axios.get(`${this.apiUrl}?limit=${pageSize}&skip=${(current - 1) * pageSize}&${new URLSearchParams(this.extraQuery).toString()}`);
        this.dataSource = data.data.map((item: Item, index: number) => {
          return {...item, key: index};
        });
        this.pagination.total = data.total;
      } catch (e) {
        console.log(e);
      } finally {
        this.isLoading = false;
      }
    },
    async handleTableChange(pagination: PaginationOptions) {
      const pager = { ...this.pagination };
      pager.current = pagination.current;
      pager.pageSize = pagination.pageSize;
      this.pagination = pager;
      this.fetchData();
    },
    handleAdd() {
      this.isModalVisible = true;
    },
    customRow(record: any, index: number) {
      return {
        click: (e: Event) => {
          this.$emit('rowclick', e, record, index);
        },
      };
    },
    async addNewData() {
      try {
        const { data } = await axios.post(`${this.apiUrl}`, this.newData);
        if (data.code === 0) {
          message.success(data.data.message);
        } else {
          message.error(data.data.message);
        }
      } catch (err) {
        message.error(err.message);
      } finally {
        this.resetNewData();
        this.isModalVisible = false;
        this.fetchData();
      }
    },
    showEditModal(record: any) {
      this.activeRecord = record;
      this.isEditModalVisible = true;
    },
    showDeleteModal(record: any) {
      this.activeRecord = record;
      this.isDeleteModalVisible = true;
    },
    async editData() {
      try {
        const { data } = await axios.put(`${this.apiUrl}${this.activeRecord.id}`, this.activeRecord);
        if (data.code === 0) {
          message.success(data.data.message);
        } else {
          message.error(data.data.message);
        }
      } catch (err) {
        message.error(err.message);
      } finally {
        this.isEditModalVisible = false;
        this.fetchData();
      }
    },
    async deleteData() {
      try {
        const { data } = await axios.delete(`${this.apiUrl}${this.activeRecord.id}`);
        if (data.code === 0) {
          message.success(data.data.message);
        } else {
          message.error(data.data.message);
        }
      } catch (err) {
        message.error(err.message);
      } finally {
        this.isDeleteModalVisible = false;
        this.fetchData();
      }
    },
    resetNewData() {
      this.editableColumns.forEach(column => {
        this.newData[column.dataIndex] = '';
      });
    },
  },
  components: {
    PlusCircleOutlined,
    EditOutlined,
    DeleteOutlined,
  },
  computed: {
    editableColumns(): any[] {
      return this.columns!.filter((column: any) => column.dataIndex && column.dataIndex !== 'id');
    },
  },
  emits: ['rowclick'],
});
</script>