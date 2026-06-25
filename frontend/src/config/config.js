export const attributes = [
	{ id: 'hp', name: '生命' },
	{ id: 'melee', name: '近战' },
	{ id: 'grenade', name: '手雷' },
	{ id: 'super', name: '超能' },
	{ id: 'class', name: '职业' },
	{ id: 'weapon', name: '武器' }
]

/** 五件护甲槽位：头、手、胸、腿、职业；conversionTo 为转换模组可增加属性的限制 */
export const armorSlots = [
	{ id: 'head', name: '头部', conversionTo: null },
	{ id: 'hands', name: '手部', conversionTo: 'weapon' },
	{ id: 'chest', name: '胸部', conversionTo: 'grenade' },
	{ id: 'legs', name: '腿部', conversionTo: 'melee' },
	{ id: 'class', name: '职业', conversionTo: 'weapon' }
]

const attrIds = attributes.map((a) => a.id)

/** 根据固定属性自动生成随机属性候选（四选一，数值 20） */
export function randomOptions(fixed) {
	const fixedSet = new Set(fixed.map((f) => f.attr))
	return attrIds
		.filter((id) => !fixedSet.has(id))
		.map(attr => ({ attr, value: 20 }))
}

/** 12 种装备框架，固定属性数值为 30 或 25 */
export const frameworks = [
	{
		id: 'expert',
		name: '专家',
		fixed: [
			{ attr: 'class', value: 30 },
			{ attr: 'weapon', value: 25 }
		]
	},
	{
		id: 'assaulter',
		name: '突击手',
		fixed: [
			{ attr: 'melee', value: 30 },
			{ attr: 'weapon', value: 25 }
		]
	},
	{
		id: 'paragon',
		name: '楷模典范',
		fixed: [
			{ attr: 'melee', value: 25 },
			{ attr: 'super', value: 30 }
		]
	},
	{
		id: 'energizer',
		name: '高能者',
		fixed: [
			{ attr: 'super', value: 25 },
			{ attr: 'weapon', value: 30 }
		]
	},
	{
		id: 'gunslinger',
		name: '枪手',
		fixed: [
			{ attr: 'grenade', value: 25 },
			{ attr: 'weapon', value: 30 }
		]
	},
	{
		id: 'breacher',
		name: '突围者',
		fixed: [
			{ attr: 'hp', value: 30 },
			{ attr: 'grenade', value: 25 }
		]
	},
	{
		id: 'bastion',
		name: '堡垒',
		fixed: [
			{ attr: 'hp', value: 30 },
			{ attr: 'class', value: 25 }
		]
	},
	{
		id: 'fighter',
		name: '搏击手',
		fixed: [
			{ attr: 'hp', value: 25 },
			{ attr: 'melee', value: 30 }
		]
	},
	{
		id: 'grenadier',
		name: '掷雷手',
		fixed: [
			{ attr: 'grenade', value: 30 },
			{ attr: 'super', value: 25 }
		]
	},
	{
		id: 'demo_expert',
		name: '爆破专家',
		fixed: [
			{ attr: 'grenade', value: 30 },
			{ attr: 'class', value: 25 }
		]
	},
	{
		id: 'armored',
		name: '装甲兵',
		fixed: [
			{ attr: 'hp', value: 25 },
			{ attr: 'super', value: 30 }
		]
	},
	{
		id: 'marauder',
		name: '掠夺者',
		fixed: [
			{ attr: 'melee', value: 25 },
			{ attr: 'class', value: 30 }
		]
	}
]
