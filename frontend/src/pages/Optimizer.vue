<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>命运 2 配装计算器</h1>
      <p class="app-subtitle">设置目标属性与模组选项，主要解决当前目标属性及已有装备下，还需刷取哪些属性装备</p>
    </header>

    <main class="app-main">
      <section class="panel">
        <h2 class="panel-title">目标属性与优先级</h2>
        <p class="field-hint">拖动调整优先级（左侧更高）。目标为 0 的属性不参与计算。</p>

        <div class="priority-list">
          <div
            v-for="(attrId, index) in priorityOrder"
            :key="attrId"
            class="priority-item"
            draggable="true"
            @dragstart="onDragStart(index)"
            @dragenter.prevent="onDragEnter(index)"
            @dragend="onDragEnd"
          >
            <span class="priority-rank">#{{ index + 1 }}</span>
            <span class="attr-name">{{ attrName(attrId) }}</span>
            <a-input-number
              v-model:value="targets[attrId]"
              :min="0"
              class="target-input"
              placeholder="目标"
            />
          </div>
        </div>
      </section>

      <section class="panel">
        <h2 class="panel-title">装备框架预设</h2>
        <p class="field-hint">至少锁定一个部位的框架与随机属性。勾选后可选择框架与随机属性。</p>

        <div
          v-for="(slot, idx) in armorSlots"
          :key="slot.id"
          class="slot-preset-row"
          :class="{ locked: slotLocks[idx].locked }"
        >
          <div class="slot-left">
            <a-switch
              v-model:checked="slotLocks[idx].locked"
              size="small"
              @change="onToggleLock(idx)"
            />
            <span class="slot-name">{{ slot.name }}</span>
          </div>

          <a-select
            v-model:value="slotLocks[idx].frameworkId"
            class="preset-select"
            :disabled="!slotLocks[idx].locked"
            placeholder="选择框架"
            allow-clear
            @change="onFrameworkChange(idx)"
          >
            <a-select-option v-for="fw in frameworks" :key="fw.id" :value="fw.id">
              {{ fw.name }}
            </a-select-option>
          </a-select>

          <a-select
            v-model:value="slotLocks[idx].randomAttr"
            class="preset-select"
            :disabled="!slotLocks[idx].locked || !slotLocks[idx].frameworkId"
            placeholder="随机属性（四选一）"
            allow-clear
          >
            <a-select-option
              v-for="opt in poolRandomOptions(slotLocks[idx].frameworkId)"
              :key="opt.attr"
              :value="opt.attr"
            >
              {{ attrName(opt.attr) }} +20
            </a-select-option>
          </a-select>
        </div>
      </section>

      <section class="panel">
        <h2 class="panel-title">属性模组选择</h2>
        <p class="field-hint">每件护甲的祝福模组与转换模组互斥，仅可择一。</p>

        <div class="switch-list">
          <label v-for="item in modSwitches" :key="item.key" class="switch-item">
            <a-switch v-model:checked="item.ref.value" />
            <span>{{ item.label }}</span>
          </label>
        </div>
      </section>

      <section class="calculate-section">
        <a-button
          type="primary"
          size="large"
          block
          :loading="calculating"
          :disabled="!canCalculate"
          @click="onCalculate"
        >
          开始计算
        </a-button>
        <p v-if="!canCalculate" class="hint-message">请至少锁定一个部位，并选择框架与随机属性</p>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </section>

      <section class="panel result-panel">
        <h2 class="panel-title">计算结果</h2>
        <p class="field-hint">以下为不同「框架套装」的推荐方案（五件框架种类相同仅换槽位不重复出现），详情见各槽位分配。</p>

        <a-empty v-if="!calculatedResults.length && !calculating" description="暂无结果，请先设置条件并计算" />

        <div v-else class="solution-card-list">
          <article
            v-for="(solution, idx) in calculatedResults"
            :key="solution.id"
            class="solution-card"
          >
            <div class="solution-head">
              <h3>
                推荐方案 {{ idx + 1 }}
                <span v-if="solution.allMet" class="badge good">全部达标</span>
                <span v-else-if="solution.isClosest" class="badge warn">最接近方案</span>
                <span v-if="solution.conversionCount === 0" class="badge good">无需转换模组</span>
                <span v-else class="badge">需 {{ solution.conversionCount }} 个转换模组</span>
              </h3>
              <p v-if="solution.frameworkCombo" class="framework-combo">
                框架组合：{{ solution.frameworkCombo }}
              </p>
            </div>

            <div v-if="solution.priorityResults?.length" class="priority-status">
              <span
                v-for="pr in solution.priorityResults"
                :key="pr.attr"
                class="pr-tag"
                :class="{ met: pr.met, unmet: !pr.met }"
              >
                #{{ pr.rank }} {{ pr.attrName }}：{{ pr.actual }}/≥{{ pr.target }}
                {{ pr.met ? "✓" : "✗" }}
              </span>
            </div>

            <a-table
              :columns="resultColumns"
              :data-source="solution.slots"
              :pagination="false"
              size="small"
              row-key="slotId"
              bordered
            />
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, h } from "vue";
import { message } from "ant-design-vue";
import { attributes, armorSlots, frameworks, randomOptions } from "../config/config.js";
import { solveBuild } from "../api/optimizer";

const defaultPriorityOrder = attributes.map((a) => a.id);
const priorityOrder = ref([...defaultPriorityOrder]);
const targets = ref(Object.fromEntries(attributes.map((a) => [a.id, 0])));
const draggingIndex = ref(null);

const isMasterworked = ref(false);
const useMods = ref(false);
const useBlessing = ref(false);
const useArtifice = ref(false);

const modSwitches = [
  { key: "masterwork", ref: isMasterworked, label: "大师护甲（三条最低属性 +5）" },
  { key: "mods", ref: useMods, label: "使用属性模组（+10）" },
  { key: "blessing", ref: useBlessing, label: "使用祝福模组（三条最低属性 +1）" },
  { key: "artifice", ref: useArtifice, label: "使用转换模组（+5 / -5）" },
];

const slotLocks = ref(
  armorSlots.map(() => ({
    locked: false,
    frameworkId: undefined,
    randomAttr: undefined,
  }))
);

const calculatedResults = ref([]);
const calculating = ref(false);
const errorMessage = ref("");

const finalTargets = computed(() =>
  priorityOrder.value.map((attrId, index) => ({
    id: attrId,
    target: targets.value[attrId] ?? 0,
    priority: index + 1,
  }))
);

const canCalculate = computed(() =>
  slotLocks.value.some(
    (s) => s.locked && s.frameworkId && s.randomAttr
  )
);

const resultColumns = [
  { title: "槽位", dataIndex: "slotName", key: "slotName", width: 80 },
  { title: "装备框架", dataIndex: "frameworkName", key: "frameworkName" },
  { title: "随机属性", dataIndex: "randomAttrName", key: "randomAttrName" },
  {
    title: "属性模组",
    key: "statMod",
    customRender: ({ record }) =>
      record.statMod
        ? h("span", `${record.statMod.attrName} +${record.statMod.value}`)
        : h("span", { class: "cell-empty" }, "—"),
  },
  {
    title: "祝福模组",
    key: "blessingMod",
    customRender: ({ record }) =>
      record.blessingMod
        ? h("span", record.blessingMod.name)
        : h("span", { class: "cell-empty" }, "—"),
  },
  {
    title: "转换模组",
    key: "conversionMod",
    customRender: ({ record }) =>
      record.conversionMod
        ? h(
            "span",
            `${record.conversionMod.fromName} -5 → ${record.conversionMod.toName} +5`
          )
        : h("span", { class: "cell-empty" }, "—"),
  },
];

function attrName(id) {
  return attributes.find((a) => a.id === id)?.name ?? id;
}

function onDragStart(index) {
  draggingIndex.value = index;
}

function onDragEnter(index) {
  const from = draggingIndex.value;
  if (from === null || from === index) return;
  const newOrder = [...priorityOrder.value];
  const moved = newOrder.splice(from, 1)[0];
  newOrder.splice(index, 0, moved);
  priorityOrder.value = newOrder;
  draggingIndex.value = index;
}

function onDragEnd() {
  draggingIndex.value = null;
}

function onToggleLock(idx) {
  if (!slotLocks.value[idx].locked) {
    slotLocks.value[idx].frameworkId = undefined;
    slotLocks.value[idx].randomAttr = undefined;
  }
}

function onFrameworkChange(idx) {
  slotLocks.value[idx].randomAttr = undefined;
}

function poolRandomOptions(frameworkId) {
  if (!frameworkId) return [];
  const fw = frameworks.find((f) => f.id === frameworkId);
  if (!fw) return [];
  return randomOptions(fw.fixed);
}

async function onCalculate() {
  if (!canCalculate.value) {
    message.warning("请至少锁定一个部位，并选择框架与随机属性");
    return;
  }

  calculating.value = true;
  errorMessage.value = "";

  const payload = {
    targets: finalTargets.value,
    modSettings: {
      isMasterworked: isMasterworked.value,
      useMods: useMods.value,
      useBlessing: useBlessing.value,
      useArtifice: useArtifice.value,
    },
    slotLocks: slotLocks.value.map((s, idx) => ({
      slot: armorSlots[idx].id,
      locked: s.locked,
      frameworkId: s.frameworkId ?? "",
      randomAttr: s.randomAttr ?? "",
    })),
  };

  try {
    const data = await solveBuild(payload);
    if (!data.success) {
      calculatedResults.value = [];
      errorMessage.value = data.message || "未找到可行方案";
      message.warning(errorMessage.value);
      return;
    }
    calculatedResults.value = data.solutions ?? [];
    if (data.message) {
      message.info(data.message);
    } else if (!calculatedResults.value.length) {
      message.info("没有满足条件的方案");
    }
  } catch (err) {
    calculatedResults.value = [];
    errorMessage.value = "请求失败，请确认后端已启动（http://127.0.0.1:8000）";
    message.error(errorMessage.value);
    console.error(err);
  } finally {
    calculating.value = false;
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  padding: 24px 32px 40px;
}

.app-header {
  text-align: center;
  margin-bottom: 28px;
}

.app-header h1 {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
}

.app-subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel {
  padding: 20px 24px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--panel-radius);
  box-shadow: var(--panel-shadow);
}

.panel-title {
  margin: 0 0 4px;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary);
}

.field-hint {
  margin: 0 0 16px;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.priority-list {
  display: flex;
  flex-direction: row;
  gap: 10px;
}

.priority-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  background: #fafafa;
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  cursor: grab;
  transition: background 0.2s, border-color 0.2s;
}

.priority-item:active {
  cursor: grabbing;
  background: var(--primary-light);
  border-color: var(--primary);
}

.priority-rank {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.attr-name {
  font-weight: 600;
  font-size: 0.95rem;
  white-space: nowrap;
}

.target-input {
  width: 100%;
}

.switch-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 12px 24px;
}

.switch-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  color: var(--text-secondary);
  cursor: pointer;
}

@media (max-width: 768px) {
  .priority-list {
    flex-wrap: wrap;
  }

  .priority-item {
    flex: 1 1 calc(33.333% - 10px);
  }
}

.slot-preset-row {
  display: grid;
  grid-template-columns: 120px 1fr 1fr;
  gap: 16px;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: #fafafa;
  border: 1px solid var(--panel-border);
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.slot-preset-row.locked {
  background: var(--primary-light);
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(22, 119, 255, 0.12);
}

.slot-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.slot-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.preset-select {
  width: 100%;
}

.calculate-section {
  margin: 0;
}

.error-message {
  margin: 10px 0 0;
  font-size: 0.85rem;
  color: var(--error-text);
  text-align: center;
}

.hint-message {
  margin: 10px 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-align: center;
}

.result-panel {
  margin-top: 0;
}

.solution-card-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.solution-card {
  padding: 16px 20px;
  background: #fafafa;
  border: 1px solid var(--panel-border);
  border-radius: var(--panel-radius);
}

.solution-head h3 {
  margin: 0 0 8px;
  font-size: 1rem;
  font-weight: 600;
}

.framework-combo {
  margin: 0 0 12px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  margin-left: 8px;
  border-radius: 6px;
  background: var(--badge-neutral);
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.good {
  background: var(--badge-good);
  color: #fff;
}

.badge.warn {
  background: #faad14;
  color: #fff;
}

.priority-status {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.pr-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
}

.pr-tag.met {
  background: var(--success-bg);
  color: var(--success-text);
}

.pr-tag.unmet {
  background: var(--error-bg);
  color: var(--error-text);
}

:deep(.cell-empty) {
  color: var(--text-muted);
}
</style>
