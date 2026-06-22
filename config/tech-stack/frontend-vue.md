# Vue 3 + TypeScript + Element Plus + Vite 规范

## 技术栈
- 框架：Vue 3.4+ (Composition API)
- 语言：TypeScript 4.5+
- UI 库：Element Plus 2.4+
- 构建：Vite 4+
- 包管理：pnpm 8+ (推荐) / npm
- 路由：Vue Router 4
- 状态：Pinia 2

## 目录结构

```
src/
├── api/         # 接口请求
├── assets/      # 静态资源
├── components/  # 公共组件
│   └── business/  # 业务组件
├── composables/ # 组合式函数
├── router/      # 路由
├── stores/      # Pinia stores
├── types/       # TypeScript 类型
├── utils/       # 工具函数
├── views/       # 页面
└── App.vue
```

## 命名规范
- 组件文件：大驼峰（`UserProfile.vue`）
- 工具文件：kebab-case（`format-date.ts`）
- 路由 path：kebab-case（`/user-profile`）
- 接口：camelCase（`getUserList`）
- 常量：UPPER_SNAKE_CASE

## 关键约束

### 组件
- ✅ 使用 `<script setup lang="ts">` 语法
- ✅ Props 用 `defineProps<{}>()` 类型化
- ✅ Emits 用 `defineEmits<{}>()` 类型化
- ✅ 复杂逻辑用 `composables` 抽取
- ❌ 不要在 `<script setup>` 外用 Options API

### 表格
- ✅ el-table-column label 用中文业务含义（不是 DB 字段名）
- ✅ 状态列用 el-tag + 颜色映射
- ✅ 列表搜索优先，不预加载

### 状态管理
- Pinia 优先于 Vuex
- 按业务域拆分 store（不要一个 store 装所有）
- 避免在 store 里放 UI 临时状态

### TypeScript
- 严格模式开启
- 禁用 `any`（除非有充分理由）
- 公共类型放 `types/`

## 路由
- 动态路由 + 权限控制
- 路由懒加载：`component: () => import('@/views/...')`

## 构建
- `npm run build` 检查通过
- 路径别名 `@/` 配置
- 环境变量：`VITE_*` 前缀

## 国际化（如需要）
- vue-i18n 9+
- 中英文 key 完整
- 严禁硬编码中文到代码里
