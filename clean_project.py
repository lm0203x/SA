#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本 - 删除冗余文件，精简项目结构
"""

import os
import shutil
from pathlib import Path

def clean_project():
    """清理项目冗余文件"""
    
    print("🧹 开始清理项目冗余文件...")
    
    # 需要删除的文件列表
    files_to_delete = [
        # 重复的启动脚本
        'quick_start.py',
        'complete_system_launcher.py', 
        'simple_working_system.py',
        'web_interface_v2.py',
        'start.bat',
        'start.sh',
        'start_web_server.py',  # 功能已集成到run.py
        
        # 重复的演示和测试文件
        'complete_demo.py',
        'demo_ml_factor_workflow.py',
        'demo_ml_model.py',
        'simple_factor_test.py',
        'quick_financial_test.py',
        'test_simple_chart.html',
        'working_demo_ml_model.py',
        'simple_complete_ml_model.py',
        'final_working_ml_model.py',
        'final_demo_ml_model.py',
        'complete_ml_model.py',
        'fix_working_demo_model.py',
        
        # 重复的配置文件
        'config_minimal.py',
        'requirements-base.txt',
        'requirements-dev.txt', 
        'requirements-ml.txt',
        'requirements-prod.txt',
        
        # 重复的系统文件
        'enhanced_multifactor_system.py',
        'enhanced_multifactor_system_v2.py',
        'advanced_factor_library.py',
        'enhanced_financial_factors.py',
        'app_minimal.py',
        
        # 临时和调试文件
        'database_explorer.py',
        'db_viewer.py',
        'run_database_explorer.py',
        'diagnose_training_data_issue.py',
        'fix_cache_issues.py',
        'fix_existing_models.py',
        'quick_fix_system.py',
        
        # 初始化脚本
        'init_ml_factor_system.py',
        'init_realtime_db.py',
        'init_realtime_indicators.py',
        'init_text2sql_db.py',
        'init_trading_signals.py',
    ]
    
    # 需要删除的报告和日志文件（通配符匹配）
    report_patterns = [
        'enhanced_multifactor_report_*.txt',
        'enhanced_multifactor_report_*.json', 
        'final_demo_ml_evaluation_report.txt',
        'final_demo_ml_evaluation_results.png',
        'system_fix_report_*.json',
        'system_report_*.txt',
    ]
    
    # 需要删除的目录
    dirs_to_delete = [
        'models',      # 空目录
        'static',      # 与app/static重复
        'templates',   # 与app/templates重复
        'migrations',  # 简单项目不需要
        'scripts',     # 功能已集成
        '__pycache__', # Python缓存
        '.idea',       # PyCharm配置
    ]
    
    deleted_files = 0
    deleted_dirs = 0
    
    # 删除文件
    for file_name in files_to_delete:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ 删除文件: {file_name}")
                deleted_files += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file_name} - {e}")
        else:
            print(f"  ⚠️ 文件不存在: {file_name}")
    
    # 删除匹配模式的文件
    import glob
    for pattern in report_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"  ✅ 删除报告文件: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file_path} - {e}")
    
    # 删除目录
    for dir_name in dirs_to_delete:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ 删除目录: {dir_name}")
                deleted_dirs += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {dir_name} - {e}")
        else:
            print(f"  ⚠️ 目录不存在: {dir_name}")
    
    # 清理Python缓存
    print("\n🧹 清理Python缓存...")
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # 使用切片复制避免修改正在迭代的列表
            if dir_name == '__pycache__':
                cache_path = Path(root) / dir_name
                try:
                    shutil.rmtree(cache_path)
                    print(f"  ✅ 删除缓存: {cache_path}")
                    dirs.remove(dir_name)  # 从迭代中移除
                except Exception as e:
                    print(f"  ❌ 删除缓存失败: {cache_path} - {e}")
    
    print(f"\n🎉 清理完成!")
    print(f"  📁 删除文件: {deleted_files} 个")
    print(f"  📂 删除目录: {deleted_dirs} 个")
    
    # 显示精简后的项目结构
    print(f"\n📊 精简后的项目结构:")
    print_project_structure()

def print_project_structure():
    """显示项目结构"""
    important_items = [
        'app/',
        'examples/',
        'docs/',
        'images/',
        'logs/',
        '.venv/',
        'config.py',
        'requirements.txt',
        'requirements_minimal.txt',
        'run.py',
        'quick_start_fixed.py',
        'run_system.py',
        'README.md',
        'Detail.md',
        '.gitignore'
    ]
    
    for item in important_items:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                print(f"  📁 {item}")
            else:
                print(f"  📄 {item}")
        else:
            print(f"  ❓ {item} (不存在)")

def backup_important_files():
    """备份重要文件"""
    print("💾 备份重要文件...")
    
    backup_files = [
        'config.py',
        'app/stock_analysis.db',
        '.env'
    ]
    
    backup_dir = Path('backup_before_clean')
    backup_dir.mkdir(exist_ok=True)
    
    for file_name in backup_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                print(f"  ✅ 备份: {file_name} -> {backup_path}")
            except Exception as e:
                print(f"  ❌ 备份失败: {file_name} - {e}")

def main():
    """主函数"""
    print("🧹 多因子选股系统 - 项目清理工具")
    print("=" * 50)
    
    # 确认清理
    response = input("⚠️ 此操作将删除大量文件，是否继续？(y/N): ").strip().lower()
    if response != 'y':
        print("❌ 取消清理操作")
        return
    
    # 备份重要文件
    backup_important_files()
    
    # 执行清理
    clean_project()
    
    print("\n💡 建议:")
    print("  1. 测试系统功能是否正常")
    print("  2. 提交Git更改")
    print("  3. 如有问题，可从backup_before_clean恢复文件")

if __name__ == "__main__":
    main()