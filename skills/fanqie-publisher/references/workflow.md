# 番茄小说发布详细流程

## 准备工作

### 文件结构
```
fanqie/
└── 2026-03-12/
    ├── 001/
    │   ├── 婆婆的拆迁款.txt
    │   └── t2i_1.png
    └── 002/
        ├── 老伴的退休金被儿子拿走了.txt
        └── t2i_1.png
```

### 封面准备
- 复制封面到临时目录：`cp xxx.png /tmp/openclaw/uploads/cover.png`

## 发布步骤详解

### 步骤1：打开发布页面
```bash
browser action=open url=https://fanqienovel.com/main/writer/publish-short
```

### 步骤2：输入标题
```bash
# 点击标题输入框
browser action=act kind=click ref=e51

# 输入标题
browser action=act kind=type ref=e51 text="故事标题"
```

### 步骤3：输入正文
```javascript
// 使用 JavaScript 注入
const content = `故事内容...`;
const html = content.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
document.querySelector('[contenteditable="true"]').innerHTML = '<p>' + html + '</p>';
```

**注意**：内容过长时分段注入，每次不超过5000字符

### 步骤4：设置AI使用
```bash
browser action=act kind=click ref=e73  # 点击"是"
```

### 步骤5：设置分类
```bash
# 点击分类选择器
browser action=act kind=click ref=e83

# 选择社会伦理
browser action=act kind=click ref=e200

# 关闭弹窗
browser action=act kind=press key=Escape
```

### 步骤6：设置试读比例
```bash
browser action=act kind=click ref=e164  # 点击"去设置"
```

### 步骤7：勾选发布协议
```bash
browser action=act kind=click ref=e107  # 勾选复选框
```

### 步骤8：点击下一步
```bash
browser action=act kind=click ref=e22
```

### 步骤9：处理弹窗
常见弹窗及处理：

1. **发布协议弹窗**
   - 点击"我已阅读并同意"：`ref=e393`

2. **发布提示弹窗**
   - 点击"继续发布"：`ref=e409`

3. **提交确认弹窗**
   - 点击"确定"：`ref=e431`

4. **标题重复**
   - 修改标题添加后缀（如"-新版"）

### 步骤10：封面设置（可选）

**方案A：封面模板**
```bash
# 点击封面制作
browser action=act kind=click ref=e66

# 选择模板
browser action=act kind=click ref=e271

# 完成制作
browser action=act kind=click ref=e293
```

**方案B：AI生成**
- 点击"封面制作" → 切换到"制作封面"标签 → 输入提示词生成

## 常见问题

### Q: 元素ref每次都变怎么办？
A: 使用 snapshot 获取最新页面结构，确认 ref 后再操作

### Q: 正文注入失败怎么办？
A: 
1. 检查内容是否包含特殊字符
2. 分段注入，每次<5000字
3. 让用户手动粘贴

### Q: 封面上传失败怎么办？
A: 使用番茄内置模板或AI生成功能

### Q: 弹窗关闭不了怎么办？
A: 多按几次 Escape，或使用截图确认弹窗位置后点击

## 发布结果

成功发布后显示：
- 提示："发布成功"
- 信息："已提交，预计1天内审核完成"
