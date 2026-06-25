<template>
	<div class="calculator">
		<header class="header">
			<h1>配装计算器</h1>
		</header>

		<section class="panel-wrapper">
			<div class="panel-left">
				<h2>目标属性与优先级</h2>
				<p class="field-hint">拖动调整优先级（上方更高）。目标为 0 的属性不参与计算。</p>

				<div class="priority-list">
					<div v-for="(attrId, index) in priorityOrder" :key="attrId" class="priority-item" draggable="true"
						@dragstart="onDragStart(index)" @dragenter.prevent="onDragEnter(index)" @dragend="onDragEnd">
						<span class="priority-rank">#{{ index + 1 }}</span>
						<span class="attr-name">{{ attrName(attrId) }}</span>
						<a-input-number v-model:value="targets[attrId]" :min="0" class="target-input" placeholder="目标值" />
					</div>
				</div>
			</div>

			<div class="panel-right">
				<h2>属性模组选择</h2>
				<p class="field-hint">尽量不要同时使用祝福模组与转换模组。</p>

				<div class="switch-item">
					<a-switch v-model:checked="isMasterworked" />
					<span>大师护甲（三条最低属性 +5）</span>
				</div>
				<div class="switch-item">
					<a-switch v-model:checked="useMods" />
					<span>使用属性模组（+10）</span>
				</div>
				<div class="switch-item">
					<a-switch v-model:checked="useBlessing" />
					<span>使用祝福模组（三条最低属性 +1）</span>
				</div>
				<div class="switch-item">
					<a-switch v-model:checked="useArtifice" />
					<span>使用转换模组（+5 / -5）</span>
				</div>
			</div>
		</section>

		<section class="panel slot-presets-panel">
			<h2>装备框架预设</h2>
			<p class="field-hint">勾选后可选择框架与随机属性。</p>

			<div v-for="(slot, idx) in armorSlots" :key="slot.id" class="slot-preset-row"
				:class="{ locked: slotLocks[idx].locked }">
				<!-- 左侧：锁定开关 + 名称 -->
				<div class="slot-left">
					<a-switch v-model:checked="slotLocks[idx].locked" size="small" @change="onToggleLock(idx)" />
					<span class="slot-name">{{ slot.name }}</span>
				</div>

				<!-- 中间：框架选择 -->
				<select v-model="slotLocks[idx].frameworkId" class="preset-select" :disabled="!slotLocks[idx].locked"
					@change="onFrameworkChange(idx)">
					<option value="">选择框架</option>
					<option v-for="fw in frameworks" :key="fw.id" :value="fw.id">
						{{ fw.name }}
					</option>
				</select>

				<!-- 右侧：随机属性 -->
				<select v-model="slotLocks[idx].randomAttr" class="preset-select"
					:disabled="!slotLocks[idx].locked || !slotLocks[idx].frameworkId">
					<option value="">随机属性（四选一）</option>
					<option v-for="opt in poolRandomOptions(slotLocks[idx].frameworkId)" :key="opt.attr" :value="opt.attr">
						{{ attrName(opt.attr) }} +20
					</option>
				</select>
			</div>
		</section>

		<section class="calculate-divider">
			<a-button type="primary" size="large" block @click="onCalculate">
				开始计算
			</a-button>
		</section>

		<section class="panel result-panel">
			<h2>计算结果</h2>
			<p class="field-hint">以下为推荐方案，每张卡片代表一个完整搭配。</p>
			<div class="solution-card-list">
				<article v-for="(solution, idx) in calculatedResults" :key="solution.id" class="solution-card">
					<!-- 卡片头部 -->
					<div class="solution-head">
						<h3>
							推荐方案 {{ idx + 1 }}
							<span v-if="solution.conversionCount === 0" class="badge good">无需转换模组</span>
							<span v-else class="badge">需 {{ solution.conversionCount }} 个转换模组</span>
						</h3>
					</div>
					<!-- 优先级达成情况 -->
					<div class="priority-status" v-if="solution.priorityResults">
						<span v-for="pr in solution.priorityResults" :key="pr.attr" class="pr-tag"
							:class="{ met: pr.met, unmet: !pr.met }">
							#{{ pr.rank }} {{ pr.attrName }}：{{ pr.actual }}/≥{{ pr.target }}
							{{ pr.met ? '✓' : '✗' }}
						</span>
					</div>
					<table class="solution-table">
						<thead>
							<tr>
								<th>槽位</th>
								<th>装备框架</th>
								<th>随机属性</th>
								<th>属性模组</th>
								<th>祝福模组</th>
								<th>转换模组</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="slot in solution.slots" :key="slot.slotName">
								<td>{{ slot.slotName }}</td>
								<td>{{ slot.frameworkName }}</td>
								<td>{{ slot.randomAttrName }}</td>
								<!-- 属性模组 -->
								<td>
									<span v-if="slot.statMod">
										{{ slot.statMod.attrName }} +10
									</span>
									<span v-else>—</span>
								</td>
								<!-- 祝福模组 -->
								<td>
									<span v-if="slot.blessingMod">
										{{ slot.blessingMod.name }}
									</span>
									<span v-else>—</span>
								</td>
								<!-- 转换模组 -->
								<td>
									<span v-if="slot.conversionMod">
										{{ slot.conversionMod.fromName }} -5 → {{ slot.conversionMod.toName }} +5
									</span>
									<span v-else>—</span>
								</td>
							</tr>
						</tbody>
					</table>
				</article>
			</div>
		</section>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { attributes, armorSlots, frameworks, randomOptions } from '../config/config.js'
import { solveBuild } from "../api/optimizer";


// 默认顺序
const defaultPriorityOrder = attributes.map(a => a.id)
const priorityOrder = ref([...defaultPriorityOrder])

// 每个属性的目标值
const targets = ref(
	Object.fromEntries(attributes.map(a => [a.id, 0]))
)

// 拖动状态
const draggingIndex = ref(null)

function attrName(id) {
	return attributes.find(a => a.id === id)?.name ?? id
}

// 开始拖动
function onDragStart(index) {
	draggingIndex.value = index
}

// 拖动进入其他项
function onDragEnter(index) {
	const from = draggingIndex.value
	const to = index
	if (from === to) return

	const newOrder = [...priorityOrder.value]
	const moved = newOrder.splice(from, 1)[0]
	newOrder.splice(to, 0, moved)

	priorityOrder.value = newOrder
	draggingIndex.value = to
}

// 拖动结束
function onDragEnd() {
	draggingIndex.value = null
}

// 切换锁定
function onToggleLock(idx) {
	if (!slotLocks.value[idx].locked) {
		// 关闭时清空
		slotLocks.value[idx].frameworkId = ''
		slotLocks.value[idx].randomAttr = ''
	}
}

// 切换框架
function onFrameworkChange(idx) {
	slotLocks.value[idx].randomAttr = ''
}

// 随机属性候选
function poolRandomOptions(frameworkId) {
	if (!frameworkId) return []
	const fw = frameworks.find(f => f.id === frameworkId)
	if (!fw) return []
	return randomOptions(fw.fixed)
}

// 最终目标值
const finalTargets = computed(() => {
	return priorityOrder.value.map((attrId, index) => ({
		id: attrId,
		target: targets.value[attrId],
		priority: index + 1
	}))
})

// 属性模组开关
const isMasterworked = ref(false)
const useMods = ref(false)
const useBlessing = ref(false)
const useArtifice = ref(false)

// 槽位状态
const slotLocks = ref(
	armorSlots.map(() => ({
		locked: false,
		frameworkId: '',
		randomAttr: ''
	}))
)

const calculatedResults = ref([])

async function onCalculate() {
  const payload = {
    targets: finalTargets.value,
    modSettings: {
      isMasterworked: isMasterworked.value,
      useMods: useMods.value,
      useBlessing: useBlessing.value,
      useArtifice: useArtifice.value
    },
    slotLocks: slotLocks.value.map((s, idx) => ({
      slot: armorSlots[idx].id,
      locked: s.locked,
      frameworkId: s.frameworkId,
      randomAttr: s.randomAttr
    }))
  };

  const data = await solveBuild(payload);

  if (!data.success) {
    calculatedResults.value = [];
    return;
  }

  calculatedResults.value = data.solutions;
}
</script>

<style scoped>
.calculator {
	width: 100%;
	margin: 0;
	padding: 20px 30px;
	background: #f5f6fa;
	border-radius: 12px;
}

.header h1 {
	margin: 0 0 12px;
	font-size: 1.75rem;
	color: #1a1a2e;
	text-align: center;
}

.panel-wrapper {
	display: flex;
	gap: 20px;
	width: 100%;
}

.h2 {
	margin: 0;
	font-size: 1.1rem;
	color: #333;
}

.field-hint {
	margin: 4px 0 12px;
	font-size: 0.82rem;
	color: #999;
}

.panel-left {
	flex: 60%;
	margin-top: 24px;
	padding: 20px;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

	.priority-list {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.priority-item {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 12px;
		padding: 8px 14px;
		background: #ffffff;
		border-radius: 8px;
		border: 1px solid #e0e0e0;
		cursor: grab;
		transition: background 0.2s;
	}

	.priority-item:active {
		cursor: grabbing;
		background: #f0f0f0;
	}

	.priority-rank {
		font-weight: bold;
		width: 40px;
		text-align: center;
		color: #555;
	}

	.attr-name {
		font-size: 1rem;
		color: #333;
		width: 80px;
		text-align: center;
	}

	.target-input {
		flex: 1;
		padding: 4px 6px;
	}
}

.panel-right {
	flex: 40%;
	margin-top: 24px;
	padding: 20px 24px;
	background: #fff;
	border-radius: 10px;
	border: 1px solid #e5e5e5;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	display: flex;
	flex-direction: column;

	.switch-item {
		display: flex;
		align-items: center;
		gap: 10px;
		font-size: 0.95rem;
		padding: 12px 0;
	}
}

/* 整个装备框架预设 Panel */
.slot-presets-panel {
	margin-top: 24px;
	padding: 20px 24px;
	background: #fff;
	border-radius: 10px;
	border: 1px solid #e5e5e5;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	display: flex;
	flex-direction: column;

	.slot-preset-row {
		display: grid;
		grid-template-columns: 10% 1fr 1fr;
		gap: 24px;
		margin-bottom: 8px;
		align-items: center;
		padding: 12px 24px 12px 14px;
		border-radius: 10px;
		background: #fafafa;
		border: 1px solid #e3e3e3;
		transition: background 0.25s, border-color 0.25s, box-shadow 0.25s;
	}

	/* 激活状态 */
	.slot-preset-row.locked {
		background: #f0f5ff;
		border-color: #4a6cf7;
		box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.15);
	}

	/* 左侧区域 */
	.slot-left {
		display: flex;
		align-items: center;
		gap: 10px;
		justify-content: center;
	}

	.slot-name {
		font-weight: 600;
		color: #222;
		font-size: 0.9rem;
	}

	/* 下拉框 */
	.preset-select {
		width: 100%;
		padding: 7px 10px;
		border-radius: 6px;
		border: 1px solid #cfcfcf;
		background: #fff;
		font-size: 0.88rem;
		transition: background 0.2s, color 0.2s, border-color 0.2s;
	}

	/* hover */
	.preset-select:not(:disabled):hover {
		border-color: #4a6cf7;
	}

	/* 禁用状态 */
	.preset-select:disabled {
		background: #f2f2f2;
		color: #999;
		border-color: #d8d8d8;
		cursor: not-allowed;
		opacity: 0.9;
	}
}

.calculate-divider {
	margin: 12px 0;
	width: 100%;
}

.result-panel {
	margin-top: 24px;
	padding: 20px 24px;
	background: #fff;
	border-radius: 10px;
	border: 1px solid #e5e5e5;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	min-height: 200px;
	max-height: 600px;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
}

.solution-card-list {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.solution-card {
	padding: 20px 24px;
	background: #fafafa;
	border-radius: 12px;
	border: 1px solid #e3e3e3;
	box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.solution-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
}

.solution-head h3 {
	margin: 0;
	font-size: 1.1rem;
	font-weight: 600;
	color: #333;
}

.badge {
	padding: 2px 8px;
	border-radius: 6px;
	background: #ddd;
	font-size: 0.75rem;
	margin-left: 8px;
}

.badge.good {
	background: #4caf50;
	color: #fff;
}

.priority-status {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	margin-bottom: 16px;
}

.pr-tag {
	padding: 4px 8px;
	border-radius: 6px;
	font-size: 0.8rem;
}

.pr-tag.met {
	background: #e8f5e9;
	color: #2e7d32;
}

.pr-tag.unmet {
	background: #ffebee;
	color: #c62828;
}

.solution-table {
	width: 100%;
	border-collapse: collapse;
	margin-top: 12px;
}

.solution-table th,
.solution-table td {
	padding: 8px 10px;
	border-bottom: 1px solid #e0e0e0;
	text-align: left;
}

.solution-table th {
	background: #f5f5f5;
	font-weight: 600;
}
</style>