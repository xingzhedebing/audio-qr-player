# 🚀 EdgeOne Pages 部署指南

## 概述

EdgeOne Pages 是腾讯云推出的前端部署平台，相比Vercel在国内有更好的访问速度，完美解决微信扫码需要VPN的问题。

## 部署优势

✅ **国内访问速度快** - 无需VPN即可在微信中正常使用  
✅ **腾讯云生态整合** - 与现有COS存储完美配合  
✅ **边缘计算能力** - 支持Pages Functions和KV存储  
✅ **免费使用** - 公测期间完全免费  
✅ **自动部署** - GitHub集成，代码提交自动部署  

## 详细部署步骤

### 第一步：准备工作

1. **确认GitHub仓库**
   - 仓库地址：`https://github.com/xingzhedebing/audio-qr-player`
   - 确保包含 `edgeone.json` 配置文件
   - 确保包含 `wechat_player.html` 播放器文件

2. **登录腾讯云**
   - 访问：https://console.cloud.tencent.com/edgeone-pages
   - 使用您的腾讯云账号登录

### 第二步：创建项目

1. **点击"创建项目"**
   - 在EdgeOne Pages控制台点击创建项目按钮

2. **选择导入方式**
   - 选择 **"导入 Git 仓库"**
   - 如果未连接GitHub，需要先授权连接

3. **选择仓库**
   - 找到并选择 `xingzhedebing/audio-qr-player` 仓库
   - 选择 `main` 分支

### 第三步：配置构建设置

```
项目名称: audio-qr-player
框架预设: 其他 (Other)
构建命令: (留空)
输出目录: .
安装命令: (留空)
根目录: /
Node.js版本: 18.x (默认)
```

### 第四步：高级配置（可选）

**环境变量：**
- 暂时不需要设置环境变量

**构建缓存：**
- 保持默认设置即可

### 第五步：开始部署

1. **点击"部署"按钮**
2. **等待构建完成**
   - 通常需要1-3分钟
   - 可以在构建日志中查看进度

3. **获取部署地址**
   - 部署成功后会显示访问地址
   - 格式类似：`https://your-project-xxx.edgeone-pages.com`

### 第六步：测试部署

1. **测试主页**
   ```
   https://your-project-xxx.edgeone-pages.com/
   ```

2. **测试播放器**
   ```
   https://your-project-xxx.edgeone-pages.com/wechat_player.html
   ```

3. **测试音频播放**
   ```
   https://your-project-xxx.edgeone-pages.com/wechat_player.html?url=https://audio-qr-1361719303.cos.ap-chengdu.myqcloud.com/test.mp3
   ```

### 第七步：更新Python配置

1. **运行配置更新脚本**
   ```bash
   python edgeone_config_template.py
   ```

2. **输入EdgeOne域名**
   - 输入获得的EdgeOne Pages域名（不包含https://）
   - 例如：`your-project-xxx.edgeone-pages.com`

3. **验证更新**
   - 检查 `audio_qr_manager.py` 中的URL是否已更新
   - 重新运行Python程序测试

### 第八步：生成测试二维码

1. **运行Python程序**
   ```bash
   python audio_qr_manager.py
   ```

2. **生成二维码**
   - 选择一个音频文件
   - 点击"生成选中项"
   - 确认二维码模式为"微信适配"

3. **测试扫码**
   - 用微信扫描生成的二维码
   - 确认能够正常打开播放器页面
   - 确认音频能够正常播放

## 自定义域名配置（可选）

### 1. 添加自定义域名

1. **在EdgeOne Pages控制台**
   - 进入项目设置
   - 点击"域名管理"
   - 添加自定义域名

2. **配置DNS**
   - 在域名服务商处添加CNAME记录
   - 指向EdgeOne Pages提供的地址

### 2. 配置HTTPS证书

1. **自动证书**
   - EdgeOne Pages会自动申请Let's Encrypt证书

2. **自定义证书**
   - 也可以上传自己的SSL证书

## 性能优化配置

### 1. 缓存配置

在 `edgeone.json` 中已配置：
```json
{
  "routes": [
    {
      "src": "/wechat_player.html",
      "headers": {
        "Cache-Control": "public, max-age=3600"
      }
    }
  ]
}
```

### 2. 压缩优化

EdgeOne Pages自动启用：
- Gzip压缩
- Brotli压缩
- 图片优化

## 监控和日志

### 1. 访问统计

- 在EdgeOne Pages控制台查看访问统计
- 包括PV、UV、流量等数据

### 2. 错误监控

- 查看4xx、5xx错误统计
- 分析访问异常情况

### 3. 性能监控

- 查看页面加载时间
- 分析性能瓶颈

## 故障排除

### 1. 部署失败

**可能原因：**
- GitHub仓库权限问题
- 构建配置错误
- 文件路径问题

**解决方案：**
- 检查GitHub授权
- 确认构建配置
- 查看构建日志

### 2. 访问异常

**可能原因：**
- DNS解析问题
- 缓存问题
- 文件路径错误

**解决方案：**
- 清除浏览器缓存
- 检查文件路径
- 等待DNS生效

### 3. 音频播放问题

**可能原因：**
- CORS配置问题
- 音频文件格式问题
- 网络连接问题

**解决方案：**
- 检查COS的CORS配置
- 确认音频文件可访问
- 测试网络连接

## 成本说明

### 免费额度

EdgeOne Pages公测期间免费使用，包括：
- 无限制的构建次数
- 无限制的部署次数
- 全球CDN加速
- HTTPS证书

### 未来收费

公测结束后可能的收费项目：
- 超出免费额度的流量
- 高级功能（如Pages Functions）
- 自定义域名数量

## 与Vercel对比

| 功能 | EdgeOne Pages | Vercel |
|------|---------------|---------|
| 国内访问速度 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 微信兼容性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 部署速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 功能丰富度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 免费额度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 中文支持 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 总结

EdgeOne Pages是解决音频二维码项目国内访问问题的最佳方案：

✅ **完美解决VPN依赖** - 微信扫码无需VPN即可正常使用  
✅ **部署简单快速** - 几分钟即可完成部署  
✅ **与现有架构兼容** - 无需修改播放器代码  
✅ **成本低廉** - 公测期间完全免费  
✅ **性能优秀** - 国内访问速度显著提升  

推荐立即迁移到EdgeOne Pages，享受更好的用户体验！ 