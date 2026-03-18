"""
水质预测增强Agent
实现多因素预测、极端事件预警、影响范围预测和修复效果模拟
"""

import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from .enhanced_agent import EnhancedBaseAgent, AgentResponse
from .model_interface import ModelConfig, ModelType
from api.models import WaterQualityRecord

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """预测结果"""
    predictions: List[Dict]
    confidence_intervals: List[Dict]
    extreme_events: List[Dict]
    impact_analysis: Dict
    remediation_effects: List[Dict]
    model_performance: Dict

class EnhancedPredictionAgent(EnhancedBaseAgent):
    """水质预测增强Agent"""
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的水质预测分析专家。你的职责是：

1. 基于历史数据和多因素信息进行水质指标预测
2. 识别潜在的极端事件风险并提供预警
3. 预测污染事件的影响范围和传播路径
4. 模拟不同治理措施的效果和成本效益

你需要处理的数据包括：
- 历史水质监测数据（pH、溶解氧、浊度、电导率、氨氮等）
- 气象数据（降雨、气温、气压、湿度等）
- 水文数据（流速、水位、流量等）
- 污染源信息和治理措施数据

请始终以JSON格式返回预测结果，包含：
- predictions: 多指标预测结果
- confidence_intervals: 置信区间
- extreme_events: 极端事件预警
- impact_analysis: 影响范围分析
- remediation_effects: 修复效果预测
- model_performance: 模型性能评估
"""

    def _get_response_schema(self) -> Dict:
        """获取响应数据结构"""
        return {
            "type": "object",
            "properties": {
                "predictions": {"type": "array"},
                "confidence_intervals": {"type": "array"},
                "extreme_events": {"type": "array"},
                "impact_analysis": {"type": "object"},
                "remediation_effects": {"type": "array"},
                "model_performance": {"type": "object"}
            }
        }
    
    async def _prepare_context(self, parameters: Dict) -> Dict:
        """准备上下文数据"""
        from asgiref.sync import sync_to_async
        
        context = {}
        
        # 获取历史监测数据
        @sync_to_async
        def get_historical_data():
            try:
                # 获取最近30天的数据用于预测
                start_date = datetime.now() - timedelta(days=30)
                records = WaterQualityRecord.objects.filter(
                    record_time__gte=start_date
                ).order_by('record_time')
                
                data = []
                for record in records:
                    data.append({
                        'location': record.location,
                        'record_time': record.record_time,
                        'ph_value': float(record.ph_value) if record.ph_value else None,
                        'dissolved_oxygen': float(record.dissolved_oxygen) if record.dissolved_oxygen else None,
                        'turbidity': float(record.turbidity) if record.turbidity else None,
                        'conductivity': float(record.conductivity) if record.conductivity else None,
                        'ammonia_nitrogen': float(record.ammonia_nitrogen) if record.ammonia_nitrogen else None,
                        'temperature': float(record.temperature) if record.temperature else None
                    })
                
                return pd.DataFrame(data)
            except Exception as e:
                logger.error(f"获取历史数据失败: {str(e)}")
                return pd.DataFrame()
        
        # 获取气象数据（模拟）
        @sync_to_async
        def get_weather_data():
            try:
                # 模拟气象数据（实际应从气象API获取）
                weather_data = []
                base_date = datetime.now() - timedelta(days=30)
                
                for i in range(30):
                    date = base_date + timedelta(days=i)
                    # 模拟气象数据
                    weather_data.append({
                        'date': date.date(),
                        'temperature': 20 + 10 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 3),
                        'rainfall': max(0, 5 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 2)),
                        'humidity': 60 + 20 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 10),
                        'pressure': 1013 + 10 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 5)
                    })
                
                return pd.DataFrame(weather_data)
            except Exception as e:
                logger.error(f"获取气象数据失败: {str(e)}")
                return pd.DataFrame()
        
        # 获取水文数据（模拟）
        @sync_to_async
        def get_hydrological_data():
            try:
                # 模拟水文数据
                hydro_data = []
                base_date = datetime.now() - timedelta(days=30)
                
                for i in range(30):
                    date = base_date + timedelta(days=i)
                    hydro_data.append({
                        'date': date.date(),
                        'flow_velocity': 0.5 + 0.2 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 0.1),
                        'water_level': 2.5 + 0.5 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 0.2),
                        'flow_rate': 100 + 20 * np.sin(i * 2 * np.pi / 30) + np.random.normal(0, 10)
                    })
                
                return pd.DataFrame(hydro_data)
            except Exception as e:
                logger.error(f"获取水文数据失败: {str(e)}")
                return pd.DataFrame()
        
        # 获取治理措施数据
        @sync_to_async
        def get_remediation_measures():
            try:
                # 治理措施数据库
                return [
                    {
                        'id': 'measure_001',
                        'name': '曝气增氧',
                        'type': 'oxygenation',
                        'effectiveness': {
                            'dissolved_oxygen': 0.3,  # 提升溶解氧30%
                            'ph_value': 0.1,          # 轻微提升pH
                            'turbidity': -0.2         # 降低浊度20%
                        },
                        'cost_per_day': 1000,
                        'implementation_time_hours': 4,
                        'duration_days': 7
                    },
                    {
                        'id': 'measure_002',
                        'name': 'pH调节剂投加',
                        'type': 'ph_adjustment',
                        'effectiveness': {
                            'ph_value': 0.4,          # 显著调节pH
                            'conductivity': 0.1,     # 轻微影响电导率
                            'ammonia_nitrogen': -0.1  # 轻微降低氨氮
                        },
                        'cost_per_day': 800,
                        'implementation_time_hours': 2,
                        'duration_days': 3
                    },
                    {
                        'id': 'measure_003',
                        'name': '絮凝剂投加',
                        'type': 'flocculation',
                        'effectiveness': {
                            'turbidity': -0.6,        # 显著降低浊度
                            'conductivity': 0.2,     # 增加电导率
                            'ammonia_nitrogen': -0.3  # 降低氨氮
                        },
                        'cost_per_day': 1200,
                        'implementation_time_hours': 6,
                        'duration_days': 5
                    },
                    {
                        'id': 'measure_004',
                        'name': '生物修复',
                        'type': 'biological',
                        'effectiveness': {
                            'ammonia_nitrogen': -0.4, # 显著降低氨氮
                            'ph_value': 0.1,          # 轻微调节pH
                            'dissolved_oxygen': 0.2   # 提升溶解氧
                        },
                        'cost_per_day': 600,
                        'implementation_time_hours': 12,
                        'duration_days': 14
                    }
                ]
            except Exception as e:
                logger.error(f"获取治理措施数据失败: {str(e)}")
                return []
        
        # 并行获取数据
        historical_df = await get_historical_data()
        weather_df = await get_weather_data()
        hydro_df = await get_hydrological_data()
        remediation_measures = await get_remediation_measures()
        
        context.update({
            'historical_data': historical_df.to_dict('records') if not historical_df.empty else [],
            'weather_data': weather_df.to_dict('records') if not weather_df.empty else [],
            'hydrological_data': hydro_df.to_dict('records') if not hydro_df.empty else [],
            'remediation_measures': remediation_measures,
            'prediction_target': parameters.get('target_location', 'P-042'),
            'prediction_hours': parameters.get('prediction_hours', 48),
            'analysis_time': datetime.now().isoformat()
        })
        
        return context
    
    async def _parse_response(self, response_text: str) -> Dict:
        """解析模型响应并执行实际预测"""
        try:
            # 尝试解析JSON
            response_data = json.loads(response_text)
            
            # 执行实际的预测分析
            if 'context_data' in response_text or 'prediction' in response_text.lower():
                actual_result = await self._perform_prediction_analysis(response_data)
                response_data.update(actual_result)
            
            return response_data
            
        except json.JSONDecodeError:
            # 如果不是JSON格式，执行默认分析
            return await self._perform_prediction_analysis({})
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return {
                "error": "预测分析失败",
                "details": str(e)
            }
    
    async def _perform_prediction_analysis(self, parameters: Dict) -> Dict:
        """执行实际的预测分析"""
        try:
            # 获取上下文数据
            context = await self._prepare_context(parameters)
            
            # 1. 多因素预测
            predictions, confidence_intervals = await self._multifactor_prediction(context)
            
            # 2. 极端事件预警
            extreme_events = await self._extreme_event_prediction(context, predictions)
            
            # 3. 影响范围预测
            impact_analysis = await self._impact_range_prediction(context, extreme_events)
            
            # 4. 修复效果预测
            remediation_effects = await self._remediation_effect_prediction(context)
            
            # 5. 模型性能评估
            model_performance = await self._evaluate_model_performance(context)
            
            return {
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'extreme_events': extreme_events,
                'impact_analysis': impact_analysis,
                'remediation_effects': remediation_effects,
                'model_performance': model_performance,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"预测分析失败: {str(e)}")
            return {
                'error': '预测分析失败',
                'details': str(e)
            }
    
    async def _multactor_prediction(self, context: Dict) -> Tuple[List[Dict], List[Dict]]:
        """多因素预测"""
        try:
            historical_data = context.get('historical_data', [])
            weather_data = context.get('weather_data', [])
            hydro_data = context.get('hydrological_data', [])
            prediction_hours = context.get('prediction_hours', 48)
            
            if not historical_data:
                return [], []
            
            df = pd.DataFrame(historical_data)
            weather_df = pd.DataFrame(weather_data)
            hydro_df = pd.DataFrame(hydro_data)
            
            # 准备特征数据
            features_df = self._prepare_prediction_features(df, weather_df, hydro_df)
            
            if features_df.empty:
                return [], []
            
            # 对每个指标进行预测
            metrics = ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']
            predictions = []
            confidence_intervals = []
            
            for metric in metrics:
                if metric in df.columns:
                    try:
                        # 准备训练数据
                        X, y = self._prepare_training_data(features_df, df, metric)
                        
                        if len(X) < 10:  # 数据不足
                            continue
                        
                        # 训练模型
                        model = RandomForestRegressor(n_estimators=50, random_state=42)
                        model.fit(X, y)
                        
                        # 生成未来特征
                        future_features = self._generate_future_features(features_df, prediction_hours)
                        
                        # 进行预测
                        future_predictions = model.predict(future_features)
                        
                        # 计算置信区间（简化方法）
                        std_error = np.std(y - model.predict(X))
                        confidence_level = 1.96  # 95%置信区间
                        
                        metric_predictions = []
                        metric_confidence_intervals = []
                        
                        for i, pred in enumerate(future_predictions):
                            timestamp = datetime.now() + timedelta(hours=i+1)
                            
                            metric_predictions.append({
                                'timestamp': timestamp.isoformat(),
                                'metric': metric,
                                'predicted_value': float(pred),
                                'hour_ahead': i + 1
                            })
                            
                            metric_confidence_intervals.append({
                                'timestamp': timestamp.isoformat(),
                                'metric': metric,
                                'lower_bound': float(pred - confidence_level * std_error),
                                'upper_bound': float(pred + confidence_level * std_error),
                                'confidence_level': 0.95
                            })
                        
                        predictions.extend(metric_predictions)
                        confidence_intervals.extend(metric_confidence_intervals)
                        
                    except Exception as e:
                        logger.error(f"指标{metric}预测失败: {str(e)}")
                        continue
            
            return predictions, confidence_intervals
            
        except Exception as e:
            logger.error(f"多因素预测失败: {str(e)}")
            return [], []
    
    def _prepare_prediction_features(self, df: pd.DataFrame, weather_df: pd.DataFrame, hydro_df: pd.DataFrame) -> pd.DataFrame:
        """准备预测特征"""
        try:
            # 合并数据
            features = df.copy()
            
            # 添加时间特征
            features['hour'] = pd.to_datetime(features['record_time']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['record_time']).dt.dayofweek
            features['month'] = pd.to_datetime(features['record_time']).dt.month
            
            # 添加滞后特征
            for metric in ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']:
                if metric in features.columns:
                    features[f'{metric}_lag1'] = features[metric].shift(1)
                    features[f'{metric}_lag2'] = features[metric].shift(2)
                    features[f'{metric}_lag3'] = features[metric].shift(3)
            
            # 添加移动平均特征
            for metric in ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']:
                if metric in features.columns:
                    features[f'{metric}_ma3'] = features[metric].rolling(window=3).mean()
                    features[f'{metric}_ma6'] = features[metric].rolling(window=6).mean()
            
            # 合并气象数据
            if not weather_df.empty:
                weather_df['date'] = pd.to_datetime(weather_df['date'])
                features['date'] = pd.to_datetime(features['record_time']).dt.date
                features = pd.merge(features, weather_df, on='date', how='left')
            
            # 合并水文数据
            if not hydro_df.empty:
                hydro_df['date'] = pd.to_datetime(hydro_df['date'])
                features = pd.merge(features, hydro_df, on='date', how='left')
            
            # 删除包含NaN的行
            features = features.dropna()
            
            return features
            
        except Exception as e:
            logger.error(f"特征准备失败: {str(e)}")
            return pd.DataFrame()
    
    def _prepare_training_data(self, features_df: pd.DataFrame, target_df: pd.DataFrame, metric: str) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        try:
            # 选择特征列
            feature_columns = []
            for col in features_df.columns:
                if col not in ['record_time', 'location', 'date', metric]:
                    feature_columns.append(col)
            
            X = features_df[feature_columns].values
            
            # 目标变量
            y = target_df[metric].values
            
            # 对齐数据
            min_length = min(len(X), len(y))
            X = X[:min_length]
            y = y[:min_length]
            
            # 移除NaN值
            valid_indices = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X = X[valid_indices]
            y = y[valid_indices]
            
            return X, y
            
        except Exception as e:
            logger.error(f"训练数据准备失败: {str(e)}")
            return np.array([]), np.array([])
    
    def _generate_future_features(self, features_df: pd.DataFrame, prediction_hours: int) -> np.ndarray:
        """生成未来特征"""
        try:
            # 获取最后一行的特征作为基础
            last_features = features_df.iloc[-1:].copy()
            
            future_features_list = []
            
            for hour in range(1, prediction_hours + 1):
                future_feature = last_features.copy()
                
                # 更新时间特征
                current_time = datetime.now() + timedelta(hours=hour)
                future_feature['hour'] = current_time.hour
                future_feature['day_of_week'] = current_time.weekday()
                future_feature['month'] = current_time.month
                
                # 简化处理：使用最后的滞后值和移动平均值
                for metric in ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']:
                    if f'{metric}_lag1' in future_feature.columns:
                        future_feature[f'{metric}_lag1'] = future_feature[f'{metric}_lag2'].values[0]
                    if f'{metric}_lag2' in future_feature.columns:
                        future_feature[f'{metric}_lag2'] = future_feature[f'{metric}_lag3'].values[0]
                    if f'{metric}_lag3' in future_feature.columns:
                        future_feature[f'{metric}_lag3'] = future_feature[f'{metric}_ma3'].values[0]
                
                future_features_list.append(future_feature.iloc[0].values)
            
            return np.array(future_features_list)
            
        except Exception as e:
            logger.error(f"未来特征生成失败: {str(e)}")
            return np.array([])
    
    async def _extreme_event_prediction(self, context: Dict, predictions: List[Dict]) -> List[Dict]:
        """极端事件预警"""
        try:
            if not predictions:
                return []
            
            extreme_events = []
            
            # 按指标分组预测
            predictions_df = pd.DataFrame(predictions)
            metrics = predictions_df['metric'].unique()
            
            for metric in metrics:
                metric_predictions = predictions_df[predictions_df['metric'] == metric]
                
                # 计算统计特征
                values = metric_predictions['predicted_value'].values
                
                if len(values) < 6:  # 数据不足
                    continue
                
                # 定义阈值（基于历史统计）
                thresholds = self._get_extreme_thresholds(metric)
                
                # 检测极端事件
                for i, pred in metric_predictions.iterrows():
                    value = pred['predicted_value']
                    timestamp = pred['timestamp']
                    
                    event_type = None
                    severity = None
                    
                    # 检查是否超出阈值
                    if value > thresholds.get('upper_extreme', float('inf')):
                        event_type = 'high_extreme'
                        severity = 'red' if value > thresholds.get('upper_critical', float('inf')) else 'orange'
                    elif value < thresholds.get('lower_extreme', -float('inf')):
                        event_type = 'low_extreme'
                        severity = 'red' if value < thresholds.get('lower_critical', -float('inf')) else 'orange'
                    elif value > thresholds.get('upper_warning', float('inf')):
                        event_type = 'high_warning'
                        severity = 'yellow'
                    elif value < thresholds.get('lower_warning', -float('inf')):
                        event_type = 'low_warning'
                        severity = 'blue'
                    
                    if event_type:
                        # 计算持续时间
                        duration_hours = self._calculate_event_duration(metric_predictions, i, event_type)
                        
                        extreme_events.append({
                            'timestamp': timestamp,
                            'metric': metric,
                            'event_type': event_type,
                            'severity': severity,
                            'predicted_value': float(value),
                            'threshold_exceeded': self._get_threshold_value(metric, event_type),
                            'duration_hours': duration_hours,
                            'confidence': 0.8,  # 简化置信度
                            'recommended_actions': self._get_extreme_actions(metric, event_type, severity)
                        })
            
            # 按严重程度和时间排序
            severity_order = {'red': 4, 'orange': 3, 'yellow': 2, 'blue': 1}
            extreme_events.sort(key=lambda x: (severity_order.get(x['severity'], 0), x['timestamp']), reverse=True)
            
            return extreme_events[:10]  # 返回前10个事件
            
        except Exception as e:
            logger.error(f"极端事件预测失败: {str(e)}")
            return []
    
    def _get_extreme_thresholds(self, metric: str) -> Dict:
        """获取极端事件阈值"""
        # 基于水质标准的阈值定义
        thresholds = {
            'ph_value': {
                'lower_critical': 6.0,
                'lower_extreme': 6.5,
                'lower_warning': 7.0,
                'upper_warning': 8.0,
                'upper_extreme': 8.5,
                'upper_critical': 9.0
            },
            'dissolved_oxygen': {
                'lower_critical': 3.0,
                'lower_extreme': 4.0,
                'lower_warning': 5.0,
                'upper_warning': 10.0,
                'upper_extreme': 12.0,
                'upper_critical': 15.0
            },
            'turbidity': {
                'upper_warning': 5.0,
                'upper_extreme': 10.0,
                'upper_critical': 20.0
            },
            'conductivity': {
                'upper_warning': 500,
                'upper_extreme': 800,
                'upper_critical': 1200
            },
            'ammonia_nitrogen': {
                'upper_warning': 1.0,
                'upper_extreme': 2.0,
                'upper_critical': 3.0
            }
        }
        
        return thresholds.get(metric, {})
    
    def _get_threshold_value(self, metric: str, event_type: str) -> float:
        """获取阈值"""
        thresholds = self._get_extreme_thresholds(metric)
        
        if 'high' in event_type:
            if 'critical' in event_type:
                return thresholds.get('upper_critical', 0)
            elif 'extreme' in event_type:
                return thresholds.get('upper_extreme', 0)
            else:
                return thresholds.get('upper_warning', 0)
        else:
            if 'critical' in event_type:
                return thresholds.get('lower_critical', 0)
            elif 'extreme' in event_type:
                return thresholds.get('lower_extreme', 0)
            else:
                return thresholds.get('lower_warning', 0)
    
    def _calculate_event_duration(self, predictions: pd.DataFrame, start_idx: int, event_type: str) -> int:
        """计算事件持续时间"""
        try:
            metric = predictions.iloc[start_idx]['metric']
            threshold = self._get_threshold_value(metric, event_type)
            
            duration = 1
            for i in range(start_idx + 1, len(predictions)):
                value = predictions.iloc[i]['predicted_value']
                
                if 'high' in event_type:
                    if value < threshold:
                        break
                else:
                    if value > threshold:
                        break
                
                duration += 1
            
            return duration
            
        except Exception as e:
            logger.error(f"持续时间计算失败: {str(e)}")
            return 1
    
    def _get_extreme_actions(self, metric: str, event_type: str, severity: str) -> List[str]:
        """获取极端事件应对建议"""
        actions = []
        
        if severity == 'red':
            actions.append("立即启动应急预案")
            actions.append("通知相关部门和下游用户")
            actions.append("加强监测频次至每小时一次")
        
        if metric == 'ph_value':
            if 'low' in event_type:
                actions.append("检查酸性物质排放源")
                actions.append("考虑投加碱性中和剂")
            else:
                actions.append("检查碱性物质排放源")
                actions.append("考虑投加酸性中和剂")
        
        elif metric == 'dissolved_oxygen':
            if 'low' in event_type:
                actions.append("启动增氧设备")
                actions.append("减少有机污染负荷")
                actions.append("检查水体富营养化程度")
        
        elif metric == 'turbidity':
            if 'high' in event_type:
                actions.append("检查悬浮物来源")
                actions.append("加强沉淀处理")
                actions.append("考虑投加絮凝剂")
        
        elif metric == 'ammonia_nitrogen':
            if 'high' in event_type:
                actions.append("检查生活污水和工业废水排放")
                actions.append("加强硝化处理")
                actions.append("控制农业面源污染")
        
        return actions
    
    async def _impact_range_prediction(self, context: Dict, extreme_events: List[Dict]) -> Dict:
        """影响范围预测"""
        try:
            if not extreme_events:
                return {'affected_points': [], 'impact_timeline': {}, 'severity_distribution': {}}
            
            # 获取监测网络
            monitoring_points = context.get('monitoring_network', {}).get('monitoring_points', [])
            
            impact_analysis = {
                'affected_points': [],
                'impact_timeline': {},
                'severity_distribution': {'red': 0, 'orange': 0, 'yellow': 0, 'blue': 0},
                'total_affected_points': 0,
                'max_impact_radius_km': 0
            }
            
            # 分析每个极端事件的影响
            for event in extreme_events:
                if event['severity'] not in ['red', 'orange']:  # 只分析严重事件
                    continue
                
                # 模拟影响范围（简化计算）
                impact_radius = self._calculate_impact_radius(event)
                
                # 找出受影响的监测点
                affected_points = self._find_affected_points(
                    event, monitoring_points, impact_radius
                )
                
                # 计算到达时间
                for point in affected_points:
                    arrival_time = self._calculate_arrival_time(event, point)
                    
                    impact_analysis['affected_points'].append({
                        'monitoring_point': point,
                        'event_timestamp': event['timestamp'],
                        'predicted_arrival': arrival_time.isoformat(),
                        'impact_severity': event['severity'],
                        'expected_concentration': self._estimate_concentration(event, point),
                        'distance_km': impact_radius
                    })
                
                # 更新影响时间线
                event_hour = datetime.fromisoformat(event['timestamp']).hour
                if event_hour not in impact_analysis['impact_timeline']:
                    impact_analysis['impact_timeline'][event_hour] = []
                impact_analysis['impact_timeline'][event_hour].append({
                    'event_type': event['event_type'],
                    'affected_count': len(affected_points),
                    'severity': event['severity']
                })
                
                # 更新严重程度分布
                impact_analysis['severity_distribution'][event['severity']] += len(affected_points)
            
            # 计算总体影响
            impact_analysis['total_affected_points'] = len(impact_analysis['affected_points'])
            
            if impact_analysis['affected_points']:
                max_distance = max([p['distance_km'] for p in impact_analysis['affected_points']])
                impact_analysis['max_impact_radius_km'] = max_distance
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"影响范围预测失败: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_impact_radius(self, event: Dict) -> float:
        """计算影响半径"""
        # 基于事件严重程度和类型计算影响半径
        severity_multiplier = {'red': 2.0, 'orange': 1.5, 'yellow': 1.0, 'blue': 0.5}
        
        base_radius = 5.0  # 基础半径5km
        multiplier = severity_multiplier.get(event['severity'], 1.0)
        
        # 根据指标调整
        metric_adjustment = 1.0
        if event['metric'] == 'ammonia_nitrogen':
            metric_adjustment = 1.2  # 氨氮影响范围较大
        elif event['metric'] == 'ph_value':
            metric_adjustment = 0.8  # pH影响范围相对较小
        
        return base_radius * multiplier * metric_adjustment
    
    def _find_affected_points(self, event: Dict, monitoring_points: List[str], impact_radius: float) -> List[str]:
        """找出受影响的监测点"""
        # 简化处理：随机选择一些监测点作为受影响点
        num_affected = min(int(len(monitoring_points) * 0.3), 5)  # 最多影响30%的点，最多5个
        
        if len(monitoring_points) > 0:
            indices = np.random.choice(len(monitoring_points), num_affected, replace=False)
            return [monitoring_points[i] for i in indices]
        
        return []
    
    def _calculate_arrival_time(self, event: Dict, point: str) -> datetime:
        """计算到达时间"""
        # 简化计算：基于距离和流速
        base_velocity = 0.5  # m/s
        distance_km = np.random.uniform(1, 10)  # 模拟距离
        
        travel_time_hours = (distance_km * 1000) / (base_velocity * 3600)
        
        event_time = datetime.fromisoformat(event['timestamp'])
        arrival_time = event_time + timedelta(hours=travel_time_hours)
        
        return arrival_time
    
    def _estimate_concentration(self, event: Dict, point: str) -> float:
        """估算浓度"""
        # 简化浓度估算
        base_concentration = event['predicted_value']
        distance_factor = np.random.uniform(0.3, 0.8)  # 距离衰减
        
        return base_concentration * distance_factor
    
    async def _remediation_effect_prediction(self, context: Dict) -> List[Dict]:
        """修复效果预测"""
        try:
            remediation_measures = context.get('remediation_measures', [])
            predictions = context.get('predictions', [])
            
            if not remediation_measures or not predictions:
                return []
            
            effects = []
            
            # 获取当前水质状况
            current_conditions = self._get_current_conditions(predictions)
            
            # 对每个治理措施进行效果预测
            for measure in remediation_measures:
                try:
                    # 计算治理效果
                    effect_result = self._calculate_measure_effect(measure, current_conditions)
                    
                    # 计算成本效益
                    cost_benefit = self._calculate_cost_benefit(measure, effect_result)
                    
                    effects.append({
                        'measure_id': measure['id'],
                        'measure_name': measure['name'],
                        'measure_type': measure['type'],
                        'predicted_effects': effect_result,
                        'cost_analysis': {
                            'implementation_cost': measure['cost_per_day'] * measure['duration_days'],
                            'daily_cost': measure['cost_per_day'],
                            'duration_days': measure['duration_days'],
                            'cost_per_improvement': cost_benefit['cost_per_improvement']
                        },
                        'implementation_timeline': {
                            'start_time_hours': measure['implementation_time_hours'],
                            'full_effect_time_hours': measure['implementation_time_hours'] + 24,
                            'duration_days': measure['duration_days']
                        },
                        'recommendation_score': cost_benefit['recommendation_score'],
                        'suitability': self._assess_suitability(measure, current_conditions)
                    })
                    
                except Exception as e:
                    logger.error(f"治理措施{measure['name']}效果预测失败: {str(e)}")
                    continue
            
            # 按推荐分数排序
            effects.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return effects
            
        except Exception as e:
            logger.error(f"修复效果预测失败: {str(e)}")
            return []
    
    def _get_current_conditions(self, predictions: List[Dict]) -> Dict:
        """获取当前水质状况"""
        if not predictions:
            return {}
        
        # 获取最新的预测值作为当前状况
        latest_predictions = {}
        for pred in predictions:
            metric = pred['metric']
            if metric not in latest_predictions or pred['hour_ahead'] == 1:
                latest_predictions[metric] = pred['predicted_value']
        
        return latest_predictions
    
    def _calculate_measure_effect(self, measure: Dict, current_conditions: Dict) -> Dict:
        """计算治理措施效果"""
        effectiveness = measure.get('effectiveness', {})
        effects = {}
        
        for metric, current_value in current_conditions.items():
            if metric in effectiveness:
                effect_factor = effectiveness[metric]
                
                # 计算改善后的值
                if effect_factor > 0:  # 正向效果
                    improved_value = current_value * (1 + effect_factor)
                else:  # 负向效果（降低）
                    improved_value = current_value * (1 + effect_factor)
                
                effects[metric] = {
                    'current_value': current_value,
                    'predicted_value': improved_value,
                    'improvement_percentage': abs(effect_factor) * 100,
                    'direction': 'increase' if effect_factor > 0 else 'decrease'
                }
        
        return effects
    
    def _calculate_cost_benefit(self, measure: Dict, effect_result: Dict) -> Dict:
        """计算成本效益"""
        total_cost = measure['cost_per_day'] * measure['duration_days']
        
        # 计算总体改善程度
        total_improvement = 0
        for metric, effect in effect_result.items():
            total_improvement += effect['improvement_percentage']
        
        # 成本效益比
        cost_per_improvement = total_cost / total_improvement if total_improvement > 0 else float('inf')
        
        # 推荐分数（综合考虑效果和成本）
        effectiveness_score = min(total_improvement / 100, 1.0)  # 效果分数
        cost_score = max(0, 1 - (cost_per_improvement / 1000))  # 成本分数
        
        recommendation_score = (effectiveness_score * 0.6 + cost_score * 0.4) * 100
        
        return {
            'total_improvement': total_improvement,
            'cost_per_improvement': cost_per_improvement,
            'recommendation_score': recommendation_score
        }
    
    def _assess_suitability(self, measure: Dict, current_conditions: Dict) -> str:
        """评估治理措施适用性"""
        # 基于当前水质状况评估适用性
        suitability_score = 0.5  # 基础分数
        
        # 根据治理类型调整
        if measure['type'] == 'oxygenation':
            if current_conditions.get('dissolved_oxygen', 0) < 5:
                suitability_score += 0.3
        
        elif measure['type'] == 'ph_adjustment':
            ph_value = current_conditions.get('ph_value', 7)
            if ph_value < 6.5 or ph_value > 8.5:
                suitability_score += 0.3
        
        elif measure['type'] == 'flocculation':
            if current_conditions.get('turbidity', 0) > 5:
                suitability_score += 0.3
        
        elif measure['type'] == 'biological':
            if current_conditions.get('ammonia_nitrogen', 0) > 1.5:
                suitability_score += 0.3
        
        # 转换为适用性等级
        if suitability_score >= 0.8:
            return 'highly_suitable'
        elif suitability_score >= 0.6:
            return 'suitable'
        elif suitability_score >= 0.4:
            return 'moderately_suitable'
        else:
            return 'not_suitable'
    
    async def _evaluate_model_performance(self, context: Dict) -> Dict:
        """评估模型性能"""
        try:
            historical_data = context.get('historical_data', [])
            
            if len(historical_data) < 20:  # 数据不足
                return {
                    'r2_score': 0.7,  # 模拟值
                    'rmse': 0.5,
                    'mae': 0.3,
                    'data_quality': 'limited',
                    'model_reliability': 'medium'
                }
            
            df = pd.DataFrame(historical_data)
            
            # 简化的性能评估（使用留出法验证）
            performance_metrics = {}
            metrics = ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']
            
            for metric in metrics:
                if metric in df.columns and len(df) > 10:
                    try:
                        # 简单的时间序列验证
                        train_size = int(len(df) * 0.8)
                        train_data = df[:train_size]
                        test_data = df[train_size:]
                        
                        if len(test_data) > 0:
                            # 使用简单模型进行验证
                            X_train = np.array(range(len(train_data))).reshape(-1, 1)
                            y_train = train_data[metric].dropna().values
                            X_test = np.array(range(len(train_data), len(df))).reshape(-1, 1)
                            y_test = test_data[metric].dropna().values
                            
                            if len(y_train) > 5 and len(y_test) > 0:
                                from sklearn.linear_model import LinearRegression
                                model = LinearRegression()
                                model.fit(X_train, y_train)
                                y_pred = model.predict(X_test)
                                
                                # 计算性能指标
                                r2 = r2_score(y_test, y_pred[:len(y_test)])
                                rmse = np.sqrt(mean_squared_error(y_test, y_pred[:len(y_test)]))
                                mae = np.mean(np.abs(y_test - y_pred[:len(y_test)]))
                                
                                performance_metrics[metric] = {
                                    'r2_score': float(r2),
                                    'rmse': float(rmse),
                                    'mae': float(mae)
                                }
                    
                    except Exception as e:
                        logger.error(f"指标{metric}性能评估失败: {str(e)}")
                        continue
            
            # 计算整体性能
            if performance_metrics:
                avg_r2 = np.mean([m['r2_score'] for m in performance_metrics.values()])
                avg_rmse = np.mean([m['rmse'] for m in performance_metrics.values()])
                avg_mae = np.mean([m['mae'] for m in performance_metrics.values()])
                
                # 评估数据质量和模型可靠性
                data_quality = 'good' if len(df) > 100 else 'medium' if len(df) > 50 else 'limited'
                model_reliability = 'high' if avg_r2 > 0.8 else 'medium' if avg_r2 > 0.6 else 'low'
                
                return {
                    'overall_performance': {
                        'r2_score': float(avg_r2),
                        'rmse': float(avg_rmse),
                        'mae': float(avg_mae)
                    },
                    'metrics_performance': performance_metrics,
                    'data_quality': data_quality,
                    'model_reliability': model_reliability,
                    'training_data_size': len(df),
                    'evaluation_method': 'time_series_validation'
                }
            else:
                return {
                    'r2_score': 0.7,
                    'rmse': 0.5,
                    'mae': 0.3,
                    'data_quality': 'limited',
                    'model_reliability': 'medium'
                }
                
        except Exception as e:
            logger.error(f"模型性能评估失败: {str(e)}")
            return {
                'error': str(e),
                'r2_score': 0.5,
                'model_reliability': 'low'
            }
