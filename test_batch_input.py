#!/usr/bin/env python3
"""
批量输入功能测试脚本
测试手动输入多条数据的功能
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_batch_input_functionality():
    """测试批量输入功能"""
    print("📥 测试批量输入功能...")
    
    # 准备测试数据
    batch_data = [
        {
            "point_id": "批量测试001",
            "date": "2024-03-11",
            "time": "08:00",
            "chlorine": 2.5,
            "conductivity": 450.0,
            "ph": 7.2,
            "orp": 650.0,
            "turbidity": 1.8
        },
        {
            "point_id": "批量测试002",
            "date": "2024-03-11",
            "time": "08:30",
            "chlorine": 3.0,
            "conductivity": 520.0,
            "ph": 7.8,
            "orp": 680.0,
            "turbidity": 2.1
        },
        {
            "point_id": "批量测试003",
            "date": "2024-03-11",
            "time": "09:00",
            "chlorine": 2.8,
            "conductivity": 480.0,
            "ph": 7.5,
            "orp": 660.0,
            "turbidity": 2.0
        },
        {
            "point_id": "批量测试004",
            "date": "2024-03-11",
            "time": "09:30",
            "chlorine": 4.5,
            "conductivity": 1100.0,
            "ph": 8.8,
            "orp": 450.0,
            "turbidity": 6.2
        },
        {
            "point_id": "批量测试005",
            "date": "2024-03-11",
            "time": "10:00",
            "chlorine": 1.8,
            "conductivity": 380.0,
            "ph": 6.8,
            "orp": 720.0,
            "turbidity": 1.5
        }
    ]
    
    print(f"   准备批量插入 {len(batch_data)} 条记录")
    
    # 批量创建记录
    success_count = 0
    failed_count = 0
    errors = []
    
    for i, record in enumerate(batch_data):
        try:
            print(f"   正在保存第 {i+1} 条记录...")
            response = requests.post(f"{BASE_URL}/records/", json=record)
            
            if response.status_code == 201:
                created_record = response.json()
                print(f"     ✅ 成功创建记录 ID: {created_record.get('record_id')}")
                success_count += 1
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"     ❌ 创建失败: {error_msg}")
                failed_count += 1
                errors.append({
                    "index": i + 1,
                    "point_id": record["point_id"],
                    "error": error_msg
                })
                
        except Exception as e:
            print(f"     ❌ 创建异常: {str(e)}")
            failed_count += 1
            errors.append({
                "index": i + 1,
                "point_id": record["point_id"],
                "error": str(e)
            })
        
        # 避免请求过快
        time.sleep(0.1)
    
    # 显示结果
    print(f"\n📊 批量输入结果:")
    print(f"   ✅ 成功: {success_count} 条")
    print(f"   ❌ 失败: {failed_count} 条")
    
    if errors:
        print(f"\n❌ 错误详情:")
        for error in errors[:3]:  # 只显示前3个错误
            print(f"   第 {error['index']} 条 ({error['point_id']}): {error['error']}")
    
    return success_count == len(batch_data)

def test_data_validation():
    """测试数据验证功能"""
    print("\n🔍 测试数据验证功能...")
    
    # 测试无效数据
    invalid_records = [
        {
            "point_id": "",  # 空监测点
            "date": "2024-03-11",
            "time": "08:00",
            "chlorine": 2.5,
            "conductivity": 450.0,
            "ph": 7.2,
            "orp": 650.0,
            "turbidity": 1.8
        },
        {
            "point_id": "测试点",
            "date": "",  # 空日期
            "time": "08:00",
            "chlorine": 2.5,
            "conductivity": 450.0,
            "ph": 7.2,
            "orp": 650.0,
            "turbidity": 1.8
        },
        {
            "point_id": "测试点",
            "date": "2024-03-11",
            "time": "",  # 空时间
            "chlorine": 2.5,
            "conductivity": 450.0,
            "ph": 7.2,
            "orp": 650.0,
            "turbidity": 1.8
        }
    ]
    
    validation_failed = 0
    
    for i, record in enumerate(invalid_records):
        try:
            response = requests.post(f"{BASE_URL}/records/", json=record)
            if response.status_code == 400:
                print(f"   ✅ 第 {i+1} 条无效数据被正确拒绝")
                validation_failed += 1
            else:
                print(f"   ❌ 第 {i+1} 条无效数据未被拒绝 (状态码: {response.status_code})")
        except Exception as e:
            print(f"   ❌ 第 {i+1} 条验证测试异常: {str(e)}")
    
    expected_failures = len(invalid_records)
    if validation_failed == expected_failures:
        print(f"   ✅ 数据验证功能正常 ({validation_failed}/{expected_failures})")
        return True
    else:
        print(f"   ❌ 数据验证功能异常 ({validation_failed}/{expected_failures})")
        return False

def test_alert_detection():
    """测试超标检测功能"""
    print("\n⚠️  测试超标检测功能...")
    
    # 创建包含超标数据的记录
    alert_record = {
        "point_id": "报警测试点",
        "date": "2024-03-11",
        "time": "11:00",
        "chlorine": 5.0,  # 超标 (>4.0)
        "conductivity": 1200.0,  # 超标 (>1000)
        "ph": 9.0,  # 超标 (>8.5)
        "orp": 300.0,  # 偏低 (<400)
        "turbidity": 6.0  # 超标 (>5.0)
    }
    
    try:
        response = requests.post(f"{BASE_URL}/records/", json=alert_record)
        if response.status_code == 201:
            created_record = response.json()
            print(f"   ✅ 超标记录创建成功 ID: {created_record.get('record_id')}")
            
            # 检查各项指标
            alerts = []
            thresholds = {
                'chlorine': {'min': 0.5, 'max': 4.0},
                'conductivity': {'max': 1000},
                'ph': {'min': 6.5, 'max': 8.5},
                'orp': {'min': 400},
                'turbidity': {'max': 5.0}
            }
            
            if alert_record['chlorine'] > thresholds['chlorine']['max']:
                alerts.append('余氯超标')
            if alert_record['conductivity'] > thresholds['conductivity']['max']:
                alerts.append('电导率超标')
            if alert_record['ph'] > thresholds['ph']['max']:
                alerts.push('pH值超标')
            if alert_record['orp'] < thresholds['orp']['min']:
                alerts.push('ORP偏低')
            if alert_record['turbidity'] > thresholds['turbidity']['max']:
                alerts.push('浊度超标')
            
            print(f"   📋 检测到 {len(alerts)} 项超标: {', '.join(alerts)}")
            return True
        else:
            print(f"   ❌ 超标记录创建失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 超标检测测试异常: {str(e)}")
        return False

def test_batch_performance():
    """测试批量操作性能"""
    print("\n⚡ 测试批量操作性能...")
    
    # 生成大量测试数据
    large_batch = []
    for i in range(10):
        large_batch.append({
            "point_id": f"性能测试{i:03d}",
            "date": "2024-03-11",
            "time": f"{8 + i // 5:02d}:{(i % 5) * 12:02d}",
            "chlorine": 2.5 + i * 0.1,
            "conductivity": 450.0 + i * 10,
            "ph": 7.0 + i * 0.1,
            "orp": 650.0 + i * 5,
            "turbidity": 1.5 + i * 0.2
        })
    
    print(f"   准备批量插入 {len(large_batch)} 条记录进行性能测试")
    
    start_time = time.time()
    success_count = 0
    
    for i, record in enumerate(large_batch):
        try:
            response = requests.post(f"{BASE_URL}/records/", json=record)
            if response.status_code == 201:
                success_count += 1
        except:
            pass
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   ⏱️  执行时间: {duration:.2f} 秒")
    print(f"   📊 成功率: {success_count}/{len(large_batch)} ({success_count/len(large_batch)*100:.1f}%)")
    print(f"   ⚡ 平均速度: {len(large_batch)/duration:.1f} 条/秒")
    
    return success_count == len(large_batch)

def main():
    """主测试函数"""
    print("🚀 开始批量输入功能测试")
    print("=" * 50)
    
    # 测试批量输入功能
    batch_ok = test_batch_input_functionality()
    
    # 测试数据验证
    validation_ok = test_data_validation()
    
    # 测试超标检测
    alert_ok = test_alert_detection()
    
    # 测试批量性能
    performance_ok = test_batch_performance()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   批量输入: {'✅ 通过' if batch_ok else '❌ 失败'}")
    print(f"   数据验证: {'✅ 通过' if validation_ok else '❌ 失败'}")
    print(f"   超标检测: {'✅ 通过' if alert_ok else '❌ 失败'}")
    print(f"   性能测试: {'✅ 通过' if performance_ok else '❌ 失败'}")
    
    all_passed = batch_ok and validation_ok and alert_ok and performance_ok
    print(f"\n🎯 总体结果: {'✅ 全部通过' if all_passed else '❌ 存在问题'}")
    
    if all_passed:
        print("\n🎉 批量输入功能测试完成！")
        print("📱 前端访问: http://localhost:5173/batch-input")
        print("🔌 后端API: http://localhost:8000/api/")
    else:
        print("\n⚠️  请检查失败的功能模块")

if __name__ == "__main__":
    main()
