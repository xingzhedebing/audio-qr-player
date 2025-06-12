# EdgeOne Pages 部署配置更新脚本
# 在EdgeOne Pages部署成功后，运行此脚本更新Python代码中的URL配置

import re

def update_edgeone_url(python_file_path, edgeone_url):
    """
    更新Python代码中的EdgeOne Pages URL
    
    Args:
        python_file_path: Python文件路径
        edgeone_url: EdgeOne Pages分配的域名（不包含协议）
    """
    
    # 读取文件内容
    with open(python_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换Vercel URL为EdgeOne URL
    pattern = r'https://audio-qr-player\.vercel\.app'
    replacement = f'https://{edgeone_url}'
    
    updated_content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open(python_file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ 已更新 {python_file_path}")
    print(f"   Vercel URL -> EdgeOne URL: {replacement}")

def main():
    """主函数"""
    print("🚀 EdgeOne Pages URL 配置更新工具")
    print("=" * 50)
    
    # 获取用户输入的EdgeOne Pages域名
    edgeone_domain = input("请输入EdgeOne Pages分配的域名（例如：your-project.edgeone-pages.com）: ").strip()
    
    if not edgeone_domain:
        print("❌ 域名不能为空！")
        return
    
    # 移除可能的协议前缀
    if edgeone_domain.startswith('https://'):
        edgeone_domain = edgeone_domain[8:]
    elif edgeone_domain.startswith('http://'):
        edgeone_domain = edgeone_domain[7:]
    
    # 更新Python文件
    try:
        update_edgeone_url('audio_qr_manager.py', edgeone_domain)
        print("\n✅ 配置更新完成！")
        print(f"现在二维码将使用EdgeOne Pages地址：https://{edgeone_domain}")
        print("\n📝 接下来的步骤：")
        print("1. 重新运行 audio_qr_manager.py")
        print("2. 生成新的二维码测试")
        print("3. 用微信扫码测试播放效果")
        
    except Exception as e:
        print(f"❌ 更新失败：{e}")

if __name__ == "__main__":
    main() 