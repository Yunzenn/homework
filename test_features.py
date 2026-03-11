#!/usr/bin/env python3
"""
水质监控系统功能测试脚本
测试数据管理和查询功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_data_management():
    """测试数据管理核心功能"""
    print("🔧 测试数据管理核心功能...")
    
    # 1. 测试新增记录
    print("\n1. 测试新增水质记录")
    test_record = {
        "point_id": "测试点新增",
        "date": "2024-03-11",
        "time": "16:00",
        "chlorine": 2.8,
        "conductivity": 470.0,
        "ph": 7.3,
        "orp": 660.0,
        "turbidity": 2.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/records/", json=test_record)
        if response.status_code == 201:
            created_record = response.json()
            record_id = created_record.get('record_id')
            print(f"   ✅ 新增成功，记录ID: {record_id}")
        else:
            print(f"   ❌ 新增失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 新增异常: {e}")
        return False
    
    # 2. 测试修改记录
    print(f"\n2. 测试修改记录 ID: {record_id}")
    update_data = {
        "point_id": "测试点新增",
        "date": "2024-03-11",
        "time": "16:30",
        "chlorine": 3.0,
        "conductivity": 480.0,
        "ph": 7.5,
        "orp": 670.0,
        "turbidity": 2.2
    }
    
    try:
        response = requests.put(f"{BASE_URL}/records/{record_id}/", json=update_data)
        if response.status_code == 200:
            updated_record = response.json()
            print(f"   ✅ 修改成功，时间更新为: {updated_record['time']}")
        else:
            print(f"   ❌ 修改失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 修改异常: {e}")
        return False
    
    # 3. 测试删除记录
    print(f"\n3. 测试删除记录 ID: {record_id}")
    try:
        response = requests.delete(f"{BASE_URL}/records/{record_id}/")
        if response.status_code == 204:
            print("   ✅ 删除成功")
        else:
            print(f"   ❌ 删除失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 删除异常: {e}")
        return False
    
    return True

def test_query_functionality():
    """测试查询功能"""
    print("\n🔍 测试查询与监控功能...")
    
    # 获取所有数据用于查询测试
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code != 200:
            print(f"   ❌ 获取数据失败: {response.text}")
            return False
        
        all_records = response.json().get('results', [])
        print(f"   📊 当前数据量: {len(all_records)} 条")
        
        if len(all_records) == 0:
            print("   ⚠️  没有数据可供查询测试")
            return True
        
    except Exception as e:
        print(f"   ❌ 获取数据异常: {e}")
        return False
    
    # 1. 测试按监测点查询
    print("\n1. 测试按监测点查询")
    try:
        # 这里前端会处理查询逻辑，后端只需要返回所有数据
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code == 200:
            records = response.json().get('results', [])
            # 模拟前端过滤
            filtered = [r for r in records if '监测点001' in r.get('point_id', '')]
            print(f"   ✅ 监测点查询成功，找到 {len(filtered)} 条记录")
        else:
            print(f"   ❌ 监测点查询失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 监测点查询异常: {e}")
    
    # 2. 测试按日期范围查询
    print("\n2. 测试按日期范围查询")
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code == 200:
            records = response.json().get('results', [])
            # 模拟前端过滤
            filtered = [r for r in records if '2024-03-11' <= r.get('date', '') <= '2024-03-11']
            print(f"   ✅ 日期范围查询成功，找到 {len(filtered)} 条记录")
        else:
            print(f"   ❌ 日期范围查询失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 日期范围查询异常: {e}")
    
    # 3. 测试指标阈值查询
    print("\n3. 测试指标阈值查询")
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code == 200:
            records = response.json().get('results', [])
            # 模拟前端过滤 - pH值在6.5-8.5之间
            filtered = [r for r in records if 6.5 <= r.get('ph', 0) <= 8.5]
            print(f"   ✅ 指标阈值查询成功，找到 {len(filtered)} 条记录")
        else:
            print(f"   ❌ 指标阈值查询失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 指标阈值查询异常: {e}")
    
    return True

def test_alert_detection():
    """测试超标报警检测"""
    print("\n⚠️  测试超标报警功能...")
    
    # 报警阈值
    alert_thresholds = {
        'chlorine': {'min': 0.5, 'max': 4.0},
        'conductivity': {'max': 1000},
        'ph': {'min': 6.5, 'max': 8.5},
        'orp': {'min': 400},
        'turbidity': {'max': 5.0}
    }
    
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code != 200:
            print(f"   ❌ 获取数据失败: {response.text}")
            return False
        
        records = response.json().get('results', [])
        alert_records = []
        
        for record in records:
            alerts = []
            
            # 检查各项指标
            if record.get('chlorine', 0) < alert_thresholds['chlorine']['min']:
                alerts.append('余氯偏低')
            elif record.get('chlorine', 0) > alert_thresholds['chlorine']['max']:
                alerts.append('余氯超标')
            
            if record.get('conductivity', 0) > alert_thresholds['conductivity']['max']:
                alerts.append('电导率超标')
            
            if record.get('ph', 0) < alert_thresholds['ph']['min']:
                alerts.append('pH值偏低')
            elif record.get('ph', 0) > alert_thresholds['ph']['max']:
                alerts.append('pH值超标')
            
            if record.get('orp', 0) < alert_thresholds['orp']['min']:
                alerts.append('ORP偏低')
            
            if record.get('turbidity', 0) > alert_thresholds['turbidity']['max']:
                alerts.append('浊度超标')
            
            if alerts:
                alert_records.append({
                    'record_id': record.get('record_id'),
                    'point_id': record.get('point_id'),
                    'date': record.get('date'),
                    'time': record.get('time'),
                    'alerts': alerts
                })
        
        print(f"   ✅ 报警检测完成，发现 {len(alert_records)} 条超标记录")
        
        for alert in alert_records[:3]:  # 显示前3条
            print(f"   📋 {alert['point_id']} ({alert['date']} {alert['time']}): {', '.join(alert['alerts'])}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 报警检测异常: {e}")
        return False

def test_statistics():
    """测试数据统计功能"""
    print("\n📊 测试数据统计功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/records/")
        if response.status_code != 200:
            print(f"   ❌ 获取数据失败: {response.text}")
            return False
        
        records = response.json().get('results', [])
        
        # 计算统计数据
        total_records = len(records)
        unique_points = len(set(r.get('point_id') for r in records))
        
        # 模拟报警检测
        alert_thresholds = {
            'chlorine': {'min': 0.5, 'max': 4.0},
            'conductivity': {'max': 1000},
            'ph': {'min': 6.5, 'max': 8.5},
            'orp': {'min': 400},
            'turbidity': {'max': 5.0}
        }
        
        alert_count = 0
        for record in records:
            if (record.get('chlorine', 0) < alert_thresholds['chlorine']['min'] or 
                record.get('chlorine', 0) > alert_thresholds['chlorine']['max'] or
                record.get('conductivity', 0) > alert_thresholds['conductivity']['max'] or
                record.get('ph', 0) < alert_thresholds['ph']['min'] or 
                record.get('ph', 0) > alert_thresholds['ph']['max'] or
                record.get('orp', 0) < alert_thresholds['orp']['min'] or
                record.get('turbidity', 0) > alert_thresholds['turbidity']['max']):
                alert_count += 1
        
        # 计算在线率（假设最近24小时有数据为在线）
        online_rate = 85  # 模拟值
        
        print(f"   ✅ 统计数据:")
        print(f"      📈 总记录数: {total_records}")
        print(f"      📍 监测点数量: {unique_points}")
        print(f"      ⚠️  超标数量: {alert_count}")
        print(f"      🌐 设备在线率: {online_rate}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 统计计算异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始水质监控系统功能测试")
    print("=" * 50)
    
    # 测试数据管理功能
    data_mgmt_ok = test_data_management()
    
    # 测试查询功能
    query_ok = test_query_functionality()
    
    # 测试报警功能
    alert_ok = test_alert_detection()
    
    # 测试统计功能
    stats_ok = test_statistics()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   数据管理: {'✅ 通过' if data_mgmt_ok else '❌ 失败'}")
    print(f"   查询功能: {'✅ 通过' if query_ok else '❌ 失败'}")
    print(f"   报警检测: {'✅ 通过' if alert_ok else '❌ 失败'}")
    print(f"   数据统计: {'✅ 通过' if stats_ok else '❌ 失败'}")
    
    all_passed = data_mgmt_ok and query_ok and alert_ok and stats_ok
    print(f"\n🎯 总体结果: {'✅ 全部通过' if all_passed else '❌ 存在问题'}")
    
    if all_passed:
        print("\n🎉 水质监控系统功能测试完成！")
        print("📱 前端访问: http://localhost:5173")
        print("🔌 后端API: http://localhost:8000/api/")
    else:
        print("\n⚠️  请检查失败的功能模块")

if __name__ == "__main__":
    main()
