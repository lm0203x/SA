"""
预警记录功能测试脚本
测试预警记录的各种API功能
"""

import requests
import json
import time
from datetime import datetime

# API基础地址
BASE_URL = "http://localhost:5000/api"

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get(f"{BASE_URL}/datasources", timeout=5)
        if response.status_code == 200:
            print("[OK] API连接成功")
            return True
        else:
            print(f"[ERROR] API连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] API连接异常: {e}")
        return False

def test_alert_options():
    """测试预警配置选项API"""
    try:
        response = requests.get(f"{BASE_URL}/alerts/options")
        if response.status_code == 200:
            data = response.json()
            print("[OK] 获取预警配置选项成功")
            print(f"  - 预警类型: {list(data['data']['alert_types'].keys())}")
            print(f"  - 预警级别: {list(data['data']['alert_levels'].keys())}")
            print(f"  - 预警状态: {list(data['data']['alert_statuses'].keys())}")
            return True
        else:
            print(f"[ERROR] 获取预警配置选项失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 获取预警配置选项异常: {e}")
        return False

def test_create_alert():
    """测试创建预警记录"""
    try:
        # 准备测试数据
        alert_data = {
            "ts_code": "000001.SZ",
            "alert_type": "price_threshold",
            "alert_level": "medium",
            "alert_message": "测试预警：平安银行价格超过15元",
            "risk_value": 15.50,
            "threshold_value": 15.00,
            "current_price": 15.50,
            "trigger_source": "manual",
            "extra_data": {
                "test": True,
                "created_by": "test_script"
            }
        }

        response = requests.post(
            f"{BASE_URL}/alerts",
            json=alert_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            data = response.json()
            print("[OK] 创建预警记录成功")
            print(f"  - 预警ID: {data['data']['id']}")
            print(f"  - 股票代码: {data['data']['ts_code']}")
            print(f"  - 预警类型: {data['data']['alert_type_name']}")
            print(f"  - 预警级别: {data['data']['alert_level_name']}")
            print(f"  - 预警状态: {data['data']['alert_status_name']}")
            return data['data']['id']
        else:
            print(f"[ERROR] 创建预警记录失败: {response.status_code}")
            print(f"  - 错误信息: {response.text}")
            return None

    except Exception as e:
        print(f"[ERROR] 创建预警记录异常: {e}")
        return None

def test_get_alerts():
    """测试获取预警记录列表"""
    try:
        response = requests.get(f"{BASE_URL}/alerts?per_page=5")
        if response.status_code == 200:
            data = response.json()
            print("[OK] 获取预警记录列表成功")
            print(f"  - 总记录数: {data['data']['pagination']['total']}")
            print(f"  - 当前页记录数: {len(data['data']['records'])}")

            for record in data['data']['records']:
                print(f"    * {record['ts_code']} - {record['alert_level_name']} - {record['alert_message'][:30]}...")

            return True
        else:
            print(f"[ERROR] 获取预警记录列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 获取预警记录列表异常: {e}")
        return False

def test_get_alert_stats():
    """测试获取预警统计信息"""
    try:
        response = requests.get(f"{BASE_URL}/alerts/stats?days=7")
        if response.status_code == 200:
            data = response.json()
            print("[OK] 获取预警统计信息成功")
            stats = data['data']
            print(f"  - 统计天数: {stats['period_days']}")
            print(f"  - 总预警数: {stats['total_alerts']}")
            print(f"  - 活跃预警: {stats['active_alerts']}")
            print(f"  - 已解决预警: {stats['resolved_alerts']}")
            print(f"  - 已忽略预警: {stats['ignored_alerts']}")

            print("  - 按级别统计:")
            for level, count in stats['by_level'].items():
                print(f"    * {level}: {count}")

            print("  - 按类型统计:")
            for alert_type, count in stats['by_type'].items():
                print(f"    * {alert_type}: {count}")

            return True
        else:
            print(f"[ERROR] 获取预警统计信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 获取预警统计信息异常: {e}")
        return False

def test_alert_operations(alert_id):
    """测试预警记录操作"""
    if not alert_id:
        print("[SKIP] 跳过预警操作测试（没有有效的预警ID）")
        return False

    try:
        # 测试获取单个预警记录
        response = requests.get(f"{BASE_URL}/alerts/{alert_id}")
        if response.status_code == 200:
            print("[OK] 获取单个预警记录成功")
        else:
            print(f"[ERROR] 获取单个预警记录失败: {response.status_code}")
            return False

        # 测试解决预警
        response = requests.post(
            f"{BASE_URL}/alerts/{alert_id}/resolve",
            json={"resolution_note": "测试解决"}
        )
        if response.status_code == 200:
            print("[OK] 解决预警记录成功")
        else:
            print(f"[ERROR] 解决预警记录失败: {response.status_code}")
            return False

        # 测试重新激活预警
        response = requests.post(f"{BASE_URL}/alerts/{alert_id}/reactivate")
        if response.status_code == 200:
            print("[OK] 重新激活预警记录成功")
        else:
            print(f"[ERROR] 重新激活预警记录失败: {response.status_code}")
            return False

        # 测试忽略预警
        response = requests.post(
            f"{BASE_URL}/alerts/{alert_id}/ignore",
            json={"ignore_note": "测试忽略"}
        )
        if response.status_code == 200:
            print("[OK] 忽略预警记录成功")
        else:
            print(f"[ERROR] 忽略预警记录失败: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] 预警记录操作异常: {e}")
        return False

def main():
    """主测试函数"""
    print("开始预警记录功能测试...")
    print("=" * 50)

    # 测试API连接
    if not test_api_connection():
        print("\n[ERROR] API连接失败，请确保Flask服务器正在运行")
        return

    print("\n" + "=" * 50)
    print("测试1: 获取预警配置选项")
    print("=" * 50)
    if not test_alert_options():
        return

    print("\n" + "=" * 50)
    print("测试2: 创建预警记录")
    print("=" * 50)
    alert_id = test_create_alert()

    print("\n" + "=" * 50)
    print("测试3: 获取预警记录列表")
    print("=" * 50)
    test_get_alerts()

    print("\n" + "=" * 50)
    print("测试4: 获取预警统计信息")
    print("=" * 50)
    test_get_alert_stats()

    print("\n" + "=" * 50)
    print("测试5: 预警记录操作")
    print("=" * 50)
    test_alert_operations(alert_id)

    print("\n" + "=" * 50)
    print("预警记录功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()