#!/usr/bin/env python3
"""
Django API测试脚本
用于验证水质监控系统的API接口
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_api():
    """测试所有API端点"""
    print("🚀 开始测试Django API...")
    
    # 1. 测试GET请求 - 获取记录列表
    print("\n1. 测试GET /api/records/")
    try:
        response = requests.get(f"{BASE_URL}/records/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   记录数量: {data['count']}")
            print("   ✅ GET请求成功")
        else:
            print(f"   ❌ GET请求失败: {response.text}")
    except Exception as e:
        print(f"   ❌ GET请求异常: {e}")
    
    # 2. 测试POST请求 - 创建新记录
    print("\n2. 测试POST /api/records/")
    test_data = {
        "point_id": "测试点002",
        "date": "2024-03-11",
        "time": "14:30",
        "chlorine": 3.2,
        "conductivity": 480.0,
        "ph": 7.5,
        "orp": 680.0,
        "turbidity": 2.1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/records/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 201:
            created_record = response.json()
            record_id = created_record.get('record_id')
            print(f"   创建成功，记录ID: {record_id}")
            print("   ✅ POST请求成功")
            
            # 3. 测试GET单条记录
            print(f"\n3. 测试GET /api/records/{record_id}/")
            try:
                response = requests.get(f"{BASE_URL}/records/{record_id}/")
                print(f"   状态码: {response.status_code}")
                if response.status_code == 200:
                    record = response.json()
                    print(f"   记录详情: {record['point_id']} - {record['date']} {record['time']}")
                    print("   ✅ 单条记录获取成功")
                    
                    # 4. 测试PUT请求 - 更新记录
                    print(f"\n4. 测试PUT /api/records/{record_id}/")
                    update_data = {
                        "point_id": record['point_id'],
                        "date": record['date'],
                        "time": "15:00",
                        "chlorine": 3.5,
                        "conductivity": 500.0,
                        "ph": 7.8,
                        "orp": 700.0,
                        "turbidity": 2.3
                    }
                    
                    try:
                        response = requests.put(
                            f"{BASE_URL}/records/{record_id}/",
                            json=update_data,
                            headers={"Content-Type": "application/json"}
                        )
                        print(f"   状态码: {response.status_code}")
                        if response.status_code == 200:
                            updated_record = response.json()
                            print(f"   更新成功，时间改为: {updated_record['time']}")
                            print("   ✅ PUT请求成功")
                            
                            # 5. 测试DELETE请求 - 删除记录
                            print(f"\n5. 测试DELETE /api/records/{record_id}/")
                            try:
                                response = requests.delete(f"{BASE_URL}/records/{record_id}/")
                                print(f"   状态码: {response.status_code}")
                                if response.status_code == 204:
                                    print("   ✅ DELETE请求成功")
                                else:
                                    print(f"   ❌ DELETE请求失败: {response.text}")
                            except Exception as e:
                                print(f"   ❌ DELETE请求异常: {e}")
                        else:
                            print(f"   ❌ PUT请求失败: {response.text}")
                    except Exception as e:
                        print(f"   ❌ PUT请求异常: {e}")
                else:
                    print(f"   ❌ 单条记录获取失败: {response.text}")
            except Exception as e:
                print(f"   ❌ 单条记录获取异常: {e}")
        else:
            print(f"   ❌ POST请求失败: {response.text}")
    except Exception as e:
        print(f"   ❌ POST请求异常: {e}")
    
    # 6. 测试统计数据
    print("\n6. 测试GET /api/stats/")
    try:
        response = requests.get(f"{BASE_URL}/stats/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   总记录数: {stats.get('total_records', 0)}")
            print("   ✅ 统计数据获取成功")
        else:
            print(f"   ❌ 统计数据获取失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 统计数据获取异常: {e}")
    
    print("\n🎉 API测试完成！")

if __name__ == "__main__":
    test_api()
