# 🖼️ 占位符图片说明

## 当前状态
由于项目尚未部署，截图文件暂未生成。当前使用 GitHub 原始链接指向不存在的图片文件。

## 解决方案

### 方案一：使用在线占位符服务（推荐）
```markdown
![OMB Dashboard](https://via.placeholder.com/800x400/2D5BFF/FFFFFF?text=OMB+Dashboard)
![Performance Analytics](https://via.placeholder.com/800x400/4A90E2/FFFFFF?text=Performance+Analytics)
![AI Optimization](https://via.placeholder.com/800x400/00C853/FFFFFF?text=AI+Optimization)
```

### 方案二：创建本地占位符图片
1. 运行截图生成脚本
2. 上传截图到 GitHub
3. 更新 README 中的链接

### 方案三：使用 SVG 矢量图形
创建简单的 SVG 图形作为占位符。

## 实际部署后的操作

### 生成真实截图
1. 启动 OMB 系统
2. 访问管理界面
3. 截取关键界面
4. 优化图片大小和质量

### 上传截图到 GitHub
```bash
# 将截图文件复制到 docs/screenshots/
cp ~/Desktop/dashboard.png docs/screenshots/
cp ~/Desktop/analytics.png docs/screenshots/
cp ~/Desktop/optimization.png docs/screenshots/

# 提交到 Git
git add docs/screenshots/
git commit -m "📸 添加实际截图"
git push origin main
```

### 截图规范
- **格式**: PNG 或高质量 JPG
- **尺寸**: 1920x1080 或 1440x900
- **大小**: 每个文件 < 500KB
- **命名**: 使用英文小写和下划线

## 临时解决方案
在生成实际截图前，建议使用方案一的在线占位符服务，确保 README 显示正常。