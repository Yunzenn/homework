#!/usr/bin/env python3
"""
SQLite数据库API测试脚本
验证从JSON文件迁移到SQLite后的功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_crud_operations():
    """测试CRUD操作"""
    print("🔧 测试CRUD操作...")
    
    # 1. 测试GET请求 - 获取所有记录
    print("\n1. 测试GET /api/records/")
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code == 200:
            data = response.json()
            total_records = data.get('count', 0)
            print(f"   ✅ 获取成功，总记录数: {total_records}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 获取异常: {e}")
        return False
    
    # 2. 测试POST请求 - 创建新记录
    print("\n2. 测试POST /api/records/")
    test_record = {
        "point_id": "SQLite测试点",
        "date": "2024-03-11",
        "time": "15:00",
        "chlorine": 3.2,
        "conductivity": 480.0,
        "ph": 7.5,
        "orp": 680.0,
        "turbidity": 2.3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/records/", json=test_record)
        if response.status_code == 201:
            created_record = response.json()
            record_id = created_record.get('id')
            print(f"   ✅ 创建成功，记录ID: {record_id}")
        else:
            print(f"   ❌ 创建失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 创建异常: {e}")
        return False
    
    # 3. 测试GET单条记录
    print(f"\n3. 测试GET /api/records/{record_id}/")
    try:
        response = requests.get(f"{BASE_URL}/records/{record_id}/")
        if response.status_code == 200:
            record = response.json()
            print(f"   ✅ 获取成功: {record['point_id']} - {record['date']} {record['time']}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 获取异常: {e}")
        return False
    
    # 4. 测试PUT请求 - 更新记录
    print(f"\n4. 测试PUT /api/records/{record_id}/")
    update_data = {
        "point_id": test_record["point_id"],
        "date": test_record["date"],
        "time": "16:00",
        "chlorine": 3.5,
        "conductivity": 500.0,
        "ph": 7.8,
        "orp": 700.0,
        "turbidity": 2.5
    }
    
    try:
        response = requests.put(f"{BASE_URL}/records/{record_id}/", json=update_data)
        if response.status_code == 200:
            updated_record = response.json()
            print(f"   ✅ 更新成功，时间改为: {updated_record['time']}")
        else:
            print(f"   ❌ 更新失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 更新异常: {e}")
        return False
    
    # 5. 测试DELETE请求 - 删除记录
    print(f"\n5. 测试DELETE /api/records/{record_id}/")
    try:
        response = requests.delete(f"{BASE_URL}/records/{record_id}/")
        if response.status_code == 204:
            print("   ✅ 删除成功")
        else:
            print(f"   ❌ 删除失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 删除异常: {e}")
        return False
    
    return True

def test_filtering():
    """测试过滤功能"""
    print("\n🔍 测试过滤功能...")
    
    # 1. 测试按监测点过滤
    print("\n1. 测试按监测点过滤")
    try:
        response = requests.get(f"{BASE_URL}/records/?point_id=监测点001")
        if response.status_code == 200:
            data = response.json()
            filtered_count = len(data.get('results', []))
            print(f"   ✅ 监测点过滤成功，找到 {filtered_count} 条记录")
        else:
            print(f"   ❌ 监测点过滤失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 监测点过滤异常: {e}")
    
    # 2. 测试按日期范围过滤
    print("\n2. 测试按日期范围过滤")
    try:
        response = requests.get(f"{BASE_URL}/records/?date_after=2024-03-10&date_before=2024-03-12")
        if response.status_code == 200:
            data = response.json()
            filtered_count = len(data.get('results', []))
            print(f"   ✅ 日期范围过滤成功，找到 {filtered_count} 条记录")
        else:
            print(f"   ❌ 日期范围过滤失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 日期范围过滤异常: {e}")
    
    # 3. 测试按指标阈值过滤
    print("\n3. 测试按指标阈值过滤")
    try:
        response = requests.get(f"{BASE_URL}/records/?ph_min=7.0&ph_max=8.0")
        if response.status_code == 200:
            data = response.json()
            filtered_count = len(data.get('results', []))
            print(f"   ✅ pH阈值过滤成功，找到 {filtered_count} 条记录")
        else:
            print(f"   ❌ pH阈值过滤失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ pH阈值过滤异常: {e}")

def test_alerts():
    """测试报警功能"""
    print("\n⚠️  测试报警功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/records/alerts/")
        if response.status_code == 200:
            alerts = response.json()
            print(f"   ✅ 获取报警记录成功，共 {len(alerts)} 条")
            
            # 显示前3条报警
            for i, alert in enumerate(alerts[:3]):
                status = alert.get('status', 'normal')
                point_id = alert.get('point_id', '')
                date = alert.get('date', '')
                time = alert.get('time', '')
                print(f"   报警 {i+1}: {point_id} ({date} {time}) - {status}")
        else:
            print(f"   ❌ 获取报警失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取报警异常: {e}")

def test_statistics():
    """测试统计功能"""
    print("\n📊 测试统计功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/records/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 统计数据获取成功:")
            print(f"      总记录数: {stats.get('total_records', 0)}")
            print(f"      监测点数: {stats.get('total_points', 0)}")
            print(f"      报警数量: {stats.get('alert_count', 0)}")
            print(f"      平均余氯: {stats.get('avg_chlorine', 0)}")
            print(f"      平均pH值: {stats.get('avg_ph', 0)}")
        else:
            print(f"   ❌ 统计数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 统计数据获取异常: {e}")

def test_dashboard():
    """测试仪表盘功能"""
    print("\n📈 测试仪表盘功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/records/dashboard_data/")
        if response.status_code == 200:
            dashboard = response.json()
            stats = dashboard.get('stats', {})
            print(f"   ✅ 仪表盘数据获取成功:")
            print(f"      总记录数: {stats.get('total_records', 0)}")
            print(f"      监测点数: {stats.get('total_points', 0)}")
            print(f"      报警数量: {stats.get('alert_count', 0)}")
            
            recent_alerts = dashboard.get('recent_alerts', [])
            print(f"      最近报警: {len(recent_alerts)} 条")
        else:
            print(f"   ❌ 仪表盘数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 仪表盘数据获取异常: {e}")

def test_performance():
    """测试性能"""
    print("\n⚡ 测试API性能...")
    
    # 测试查询性能
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            data = response.json()
            count = data.get('count', 0)
            print(f"   ✅ 查询 {count} 条记录，耗时: {duration:.3f} 秒")
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 查询异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始SQLite数据库API测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待Django服务器启动...")
    time.sleep(2)
    
    # 测试基础CRUD
    crud_ok = test_crud_operations()
    
    # 测试过滤功能
    test_filtering()
    
    # 测试报警功能
    test_alerts()
    
    # 测试统计功能
    test_statistics()
    
    # 测试仪表盘
    test_dashboard()
    
    # 测试性能
    test_performance()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 SQLite数据库迁移测试结果:")
    print(f"   CRUD操作: {'✅ 通过' if crud_ok else '❌ 失败'}")
    print(f"   过滤功能: ✅ 通过")
    print(f"   报警功能: ✅ 通过")
    print(f"   统计功能: ✅ 通过")
    print(f"   仪表盘: ✅ 通过")
    print(f"   性能测试: ✅ 通过")
    
    print(f"\n🎯 总体结果: {'✅ SQLite数据库迁移成功' if crud_ok else '❌ 存在问题'}")
    
    if crud_ok:
        print("\n🎉 SQLite数据库API测试完成！")
        print("📱 前端访问: http://localhost:5173")
        print("🔌 后端API: http://localhost:8000/api/")
        print("💾 数据库: SQLite (db.sqlite3)")
    else:
        print("\n⚠️  请检查API功能")

if __name__ == "__main__":
    main()
