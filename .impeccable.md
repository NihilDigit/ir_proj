## Design Context

### Users
- 大学生（课程设计作者）和答辩老师（评审者）
- 使用场景：课程设计答辩演示，展示信息检索系统的完整功能
- 核心任务：快速演示布尔检索、短语查询、查询扩展、倒排索引浏览等 IR 功能

### Brand Personality
- **精致、专业、现代** — 类似 Notion/Linear 的气质
- 给答辩老师留下"这不是随便糊的课设"的印象
- 界面应传达：技术扎实 + 审美在线

### Aesthetic Direction
- **视觉基调**: 现代精致型 — 圆角、微动画、细腻的阴影和层级
- **参考**: Notion, Linear, Vercel Dashboard
- **反参考**: 不要老旧的 Bootstrap 默认样式、不要花哨的渐变和3D效果
- **主题**: 仅 Light Mode
- **配色**: 蓝色主色调 (#2563eb)，保持当前 Tailwind Blue 色系
- **高亮色**: 黄色 (#fef08a) 用于搜索词匹配标记
- **字体**: 系统字体栈，monospace 用于技术数据（词项、位置列表）

### Design Tokens
```css
--primary: #2563eb;
--primary-hover: #1d4ed8;
--bg: #f8fafc;
--card-bg: #ffffff;
--text: #1e293b;
--text-secondary: #64748b;
--border: #e2e8f0;
--mark-bg: #fef08a;
--mark-text: #854d0e;
--radius: 8px;
```

### Design Principles
1. **清晰优先** — 信息层级分明，结果易扫读，数据表格清晰对齐
2. **精致细节** — 微妙的阴影、过渡动画、焦点状态，体现打磨感
3. **功能可见** — 核心操作（搜索、切换模式、查看详情）一目了然，不藏功能
4. **数据友好** — 倒排索引、位置列表等技术数据用 monospace 和表格清晰呈现
5. **答辩友好** — 界面在投影仪上也要清晰可读，对比度足够，字号不过小

### Tech Stack
- Vue 3 (Composition API) + Vite
- vue-router (4 pages: 布尔检索, 短语查询, 查询扩展, 词典浏览)
- axios for API calls
- 纯 CSS (CSS Variables, 无 UI 框架)
- FastAPI 后端 (Python)
