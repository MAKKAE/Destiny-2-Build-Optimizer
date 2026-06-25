import axios from "axios";

// Electron / Web 自动切换
const api = axios.create({
	baseURL: window.electronAPI?.isElectron
		? "http://127.0.0.1:8000"
		: "/api"
});

// 计算方案（新版）
export function solveBuild(payload) {
	return api.post("/solve", payload);
	// return {
	// 	success: true,
	// 	solutions: TEST_SOLUTIONS
	// }
}


const TEST_SOLUTIONS = [
	{
		id: 1,
		conversionCount: 1,
		priorityResults: [
			{ attr: 'mobility', attrName: '机动', rank: 1, actual: 90, target: 80, met: true },
			{ attr: 'resilience', attrName: '韧性', rank: 2, actual: 70, target: 80, met: false },
			{ attr: 'recovery', attrName: '恢复', rank: 3, actual: 100, target: 100, met: true }
		],

		slots: [
			{
				slotId: 'head',
				slotName: '头部',
				frameworkId: 'expert',
				frameworkName: '专家',
				randomPick: { attr: 'weapon', attrName: '武器', value: 20 },
				statMod: { attr: 'mobility', attrName: '机动', value: 10 },
				conversionMod: { from: 'grenade', fromName: '手雷', to: 'weapon', toName: '武器' }
			},
			{
				slotId: 'hands',
				slotName: '手部',
				frameworkId: 'assaulter',
				frameworkName: '突击手',
				randomPick: { attr: 'melee', attrName: '近战', value: 20 },
				statMod: { attr: 'recovery', attrName: '恢复', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'chest',
				slotName: '胸部',
				frameworkId: 'paragon',
				frameworkName: '楷模典范',
				randomPick: { attr: 'class', attrName: '职业', value: 20 },
				statMod: { attr: 'resilience', attrName: '韧性', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'legs',
				slotName: '腿部',
				frameworkId: 'guardian',
				frameworkName: '守护者',
				randomPick: { attr: 'grenade', attrName: '手雷', value: 20 },
				statMod: { attr: 'mobility', attrName: '机动', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'class',
				slotName: '职业',
				frameworkId: 'expert',
				frameworkName: '专家',
				randomPick: { attr: 'super', attrName: '超能', value: 20 },
				statMod: { attr: 'recovery', attrName: '恢复', value: 10 },
				conversionMod: null
			}
		]
	},

	{
		id: 2,
		conversionCount: 0,
		priorityResults: [
			{ attr: 'mobility', attrName: '机动', rank: 1, actual: 100, target: 80, met: true },
			{ attr: 'resilience', attrName: '韧性', rank: 2, actual: 90, target: 80, met: true },
			{ attr: 'recovery', attrName: '恢复', rank: 3, actual: 100, target: 100, met: true }
		],
		slots: [
			{
				slotId: 'head',
				slotName: '头部',
				frameworkId: 'assaulter',
				frameworkName: '突击手',
				randomPick: { attr: 'weapon', attrName: '武器', value: 20 },
				statMod: { attr: 'mobility', attrName: '机动', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'hands',
				slotName: '手部',
				frameworkId: 'guardian',
				frameworkName: '守护者',
				randomPick: { attr: 'class', attrName: '职业', value: 20 },
				statMod: { attr: 'recovery', attrName: '恢复', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'chest',
				slotName: '胸部',
				frameworkId: 'expert',
				frameworkName: '专家',
				randomPick: { attr: 'super', attrName: '超能', value: 20 },
				statMod: { attr: 'resilience', attrName: '韧性', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'legs',
				slotName: '腿部',
				frameworkId: 'paragon',
				frameworkName: '楷模典范',
				randomPick: { attr: 'melee', attrName: '近战', value: 20 },
				statMod: { attr: 'mobility', attrName: '机动', value: 10 },
				conversionMod: null
			},
			{
				slotId: 'class',
				slotName: '职业',
				frameworkId: 'assaulter',
				frameworkName: '突击手',
				randomPick: { attr: 'grenade', attrName: '手雷', value: 20 },
				statMod: { attr: 'recovery', attrName: '恢复', value: 10 },
				conversionMod: null
			}
		]
	}
]