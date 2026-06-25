<template>
  <div style="padding: 24px">
    <a-card title="命运2 配装计算器">
      <a-form layout="inline">
        <a-form-item label="目标属性">
          <a-select v-model:value="target" style="width: 200px">
            <a-select-option v-for="a in attrs" :key="a" :value="a">
              {{ a }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-button type="primary" @click="onSolve">计算</a-button>
      </a-form>

      <a-divider />

      <a-spin :spinning="loading">
        <pre>{{ result }}</pre>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { fetchAttrs, solveBuild } from "../api/optimizer";

const attrs = ref([]);
const target = ref("");
const loading = ref(false);
const result = ref("");

onMounted(async () => {
  const res = await fetchAttrs();
  attrs.value = res.data.attrs;
  target.value = attrs.value[0];
});

async function onSolve() {
  loading.value = true;
  const res = await solveBuild(target.value);
  result.value = JSON.stringify(res.data, null, 2);
  loading.value = false;
}
</script>
