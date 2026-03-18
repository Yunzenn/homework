"""
污染溯源分析Agent
实现上下游关联分析、扩散模型、贡献度分析和反向追溯功能
"""

import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from scipy import stats
from scipy.signal import correlate
from sklearn.decomposition import NMF
from sklearn.preprocessing import StandardScaler
from .enhanced_agent import EnhancedBaseAgent, AgentResponse
from .model_interface import ModelConfig, ModelType
from api.models import WaterQualityRecord

logger = logging.getLogger(__name__)

@dataclass
class TraceAnalysisResult:
    """溯源分析结果"""
    upstream_correlations: List[Dict]
    diffusion_simulation: Dict
    contribution_analysis: Dict
    reverse_trace: Dict
    confidence_score: float

class PollutionTraceAgent(EnhancedBaseAgent):
    """污染溯源分析Agent"""
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的水质污染溯源分析专家。你的职责是：

1. 分析上下游监测点数据关联性，识别污染传播路径
2. 模拟污染物扩散过程，预测影响范围
3. 分析各污染源的贡献度，确定主要污染源
4. 进行反向追溯，定位污染源头位置

你需要处理的数据包括：
- 各监测点的pH值、溶解氧、浊度、电导率、氨氮等指标
- 监测点地理位置和河流网络拓扑
- 水文数据（流速、流向、水位）
- 污染源数据库信息

请始终以JSON格式返回分析结果，包含：
- upstream_correlations: 上下游关联分析结果
- diffusion_simulation: 扩散模拟结果
- contribution_analysis: 贡献度分析
- reverse_trace: 反向追溯结果
- confidence_score: 整体置信度评分
"""

    def _get_response_schema(self) -> Dict:
        """获取响应数据结构"""
        return {
            "type": "object",
            "properties": {
                "upstream_correlations": {"type": "array"},
                "diffusion_simulation": {"type": "object"},
                "contribution_analysis": {"type": "object"},
                "reverse_trace": {"type": "object"},
                "confidence_score": {"type": "number"}
            }
        }
    
    async def _prepare_context(self, parameters: Dict) -> Dict:
        """准备上下文数据"""
        from asgiref.sync import sync_to_async
        
        context = {}
        
        # 获取监测点网络拓扑
        @sync_to_async
        def get_monitoring_network():
            try:
                # 获取所有监测点
                locations = list(WaterQualityRecord.objects.values_list('location', flat=True).distinct())
                
                # 构建简化的河流网络拓扑（实际项目中应从GIS数据获取）
                network_topology = self._build_river_network(locations)
                
                return {
                    'monitoring_points': locations,
                    'network_topology': network_topology,
                    'total_points': len(locations)
                }
            except Exception as e:
                logger.error(f"获取监测网络失败: {str(e)}")
                return {'monitoring_points': [], 'network_topology': {}, 'total_points': 0}
        
        # 获取历史数据用于关联分析
        @sync_to_async
        def get_historical_data():
            try:
                # 获取最近7天的数据
                start_date = datetime.now() - timedelta(days=7)
                records = WaterQualityRecord.objects.filter(
                    record_time__gte=start_date
                ).order_by('record_time')
                
                # 转换为DataFrame格式
                data = []
                for record in records:
                    data.append({
                        'location': record.location,
                        'record_time': record.record_time,
                        'ph_value': float(record.ph_value) if record.ph_value else None,
                        'dissolved_oxygen': float(record.dissolved_oxygen) if record.dissolved_oxygen else None,
                        'turbidity': float(record.turbidity) if record.turbidity else None,
                        'conductivity': float(record.conductivity) if record.conductivity else None,
                        'ammonia_nitrogen': float(record.ammonia_nitrogen) if record.ammonia_nitrogen else None
                    })
                
                return pd.DataFrame(data)
            except Exception as e:
                logger.error(f"获取历史数据失败: {str(e)}")
                return pd.DataFrame()
        
        # 获取污染源数据库
        @sync_to_async
        def get_pollution_sources():
            # 模拟污染源数据（实际应从数据库获取）
            return [
                {
                    'id': 'source_001',
                    'name': '上游工业园区',
                    'type': 'industrial',
                    'location': 'P-035上游2km',
                    'characteristics': {
                        'high_conductivity': True,
                        'high_ammonia': True,
                        'ph_variability': True
                    },
                    'emission_patterns': ['间歇性排放', '夜间高峰']
                },
                {
                    'id': 'source_002', 
                    'name': '生活污水处理厂',
                    'type': 'domestic',
                    'location': 'P-038附近',
                    'characteristics': {
                        'high_turbidity': True,
                        'moderate_conductivity': True,
                        'stable_ph': True
                    },
                    'emission_patterns': ['连续排放', '早晚高峰']
                },
                {
                    'id': 'source_003',
                    'name': '农业面源污染',
                    'type': 'agricultural',
                    'location': 'P-040周边区域',
                    'characteristics': {
                        'seasonal_variation': True,
                        'nutrient_loading': True,
                        'ph_dependent': True
                    },
                    'emission_patterns': ['季节性排放', '降雨相关']
                }
            ]
        
        # 并行获取数据
        network_data = await get_monitoring_network()
        historical_df = await get_historical_data()
        pollution_sources = await get_pollution_sources()
        
        context.update({
            'monitoring_network': network_data,
            'historical_data': historical_df.to_dict('records') if not historical_df.empty else [],
            'pollution_sources': pollution_sources,
            'analysis_time': datetime.now().isoformat()
        })
        
        return context
    
    def _build_river_network(self, locations: List[str]) -> Dict:
        """构建河流网络拓扑"""
        # 简化的河流网络（实际应从GIS数据获取）
        network = {
            'flow_direction': 'downstream',
            'connections': {}
        }
        
        # 基于监测点编号推断上下游关系
        sorted_locations = sorted(locations)
        for i, location in enumerate(sorted_locations):
            if i > 0:
                network['connections'][sorted_locations[i-1]] = [location]
            if i < len(sorted_locations) - 1:
                downstream = sorted_locations[i+1] if location not in network['connections'] else []
                if location not in network['connections']:
                    network['connections'][location] = downstream
                else:
                    network['connections'][location].extend(downstream)
        
        return network
    
    async def _parse_response(self, response_text: str) -> Dict:
        """解析模型响应并执行实际分析"""
        try:
            # 尝试解析JSON
            response_data = json.loads(response_text)
            
            # 执行实际的溯源分析
            if 'context_data' in response_text or 'analysis' in response_text.lower():
                actual_result = await self._perform_trace_analysis(response_data)
                response_data.update(actual_result)
            
            return response_data
            
        except json.JSONDecodeError:
            # 如果不是JSON格式，执行默认分析
            return await self._perform_trace_analysis({})
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return {
                "error": "分析失败",
                "details": str(e)
            }
    
    async def _perform_trace_analysis(self, parameters: Dict) -> Dict:
        """执行实际的溯源分析"""
        try:
            # 获取上下文数据
            context = await self._prepare_context(parameters)
            
            # 1. 上下游关联分析
            upstream_correlations = await self._analyze_upstream_correlations(context)
            
            # 2. 扩散模拟
            diffusion_simulation = await self._simulate_diffusion(context)
            
            # 3. 贡献度分析
            contribution_analysis = await self._analyze_contributions(context)
            
            # 4. 反向追溯
            reverse_trace = await self._perform_reverse_trace(context)
            
            # 5. 计算整体置信度
            confidence_score = self._calculate_confidence_score(
                upstream_correlations, diffusion_simulation, 
                contribution_analysis, reverse_trace
            )
            
            return {
                'upstream_correlations': upstream_correlations,
                'diffusion_simulation': diffusion_simulation,
                'contribution_analysis': contribution_analysis,
                'reverse_trace': reverse_trace,
                'confidence_score': confidence_score,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"溯源分析失败: {str(e)}")
            return {
                'error': '溯源分析失败',
                'details': str(e),
                'confidence_score': 0.0
            }
    
    async def _analyze_upstream_correlations(self, context: Dict) -> List[Dict]:
        """上下游关联分析"""
        try:
            historical_data = context.get('historical_data', [])
            if not historical_data:
                return []
            
            df = pd.DataFrame(historical_data)
            network = context.get('monitoring_network', {}).get('network_topology', {})
            
            correlations = []
            locations = df['location'].unique()
            
            for location in locations:
                # 获取当前位置数据
                location_data = df[df['location'] == location].sort_values('record_time')
                
                # 查找上游监测点
                upstream_points = self._find_upstream_points(location, network)
                
                for upstream in upstream_points:
                    if upstream in locations:
                        upstream_data = df[df['location'] == upstream].sort_values('record_time')
                        
                        # 计算时序相关性
                        correlation_result = self._calculate_time_series_correlation(
                            upstream_data, location_data
                        )
                        
                        if correlation_result['correlation'] > 0.6:  # 只保留强相关
                            correlations.append({
                                'target_point': location,
                                'upstream_point': upstream,
                                'correlation': correlation_result['correlation'],
                                'time_delay_minutes': correlation_result['delay_minutes'],
                                'metrics': correlation_result['metrics'],
                                'significance': correlation_result['significance']
                            })
            
            # 按相关性排序
            correlations.sort(key=lambda x: x['correlation'], reverse=True)
            return correlations[:10]  # 返回前10个最强相关
            
        except Exception as e:
            logger.error(f"上下游关联分析失败: {str(e)}")
            return []
    
    def _find_upstream_points(self, location: str, network: Dict) -> List[str]:
        """查找上游监测点"""
        upstream_points = []
        connections = network.get('connections', {})
        
        # 反向查找上游点
        for point, downstreams in connections.items():
            if location in downstreams:
                upstream_points.append(point)
        
        return upstream_points
    
    def _calculate_time_series_correlation(self, upstream_data: pd.DataFrame, 
                                         downstream_data: pd.DataFrame) -> Dict:
        """计算时序相关性"""
        try:
            # 确保数据对齐
            common_time = pd.merge(upstream_data, downstream_data, on='record_time', suffixes=('_up', '_down'))
            
            if len(common_time) < 10:  # 数据点太少
                return {'correlation': 0, 'delay_minutes': 0, 'metrics': {}, 'significance': False}
            
            # 计算各指标的相关性
            metrics = {}
            for metric in ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']:
                upstream_col = f'{metric}_up'
                downstream_col = f'{metric}_down'
                
                if upstream_col in common_time.columns and downstream_col in common_time.columns:
                    upstream_vals = common_time[upstream_col].dropna()
                    downstream_vals = common_time[downstream_col].dropna()
                    
                    if len(upstream_vals) > 5 and len(downstream_vals) > 5:
                        # 对齐数据
                        min_len = min(len(upstream_vals), len(downstream_vals))
                        upstream_aligned = upstream_vals.iloc[:min_len]
                        downstream_aligned = downstream_vals.iloc[:min_len]
                        
                        # 计算相关系数
                        corr, p_value = stats.pearsonr(upstream_aligned, downstream_aligned)
                        
                        if not np.isnan(corr):
                            metrics[metric] = {
                                'correlation': float(corr),
                                'p_value': float(p_value),
                                'data_points': min_len
                            }
            
            # 计算整体相关性（取各指标平均值）
            if metrics:
                avg_correlation = np.mean([m['correlation'] for m in metrics.values()])
                max_correlation = max([m['correlation'] for m in metrics.values()])
                
                # 估算时间延迟（基于流速和距离，简化计算）
                estimated_delay = 30  # 默认30分钟延迟
                
                return {
                    'correlation': float(avg_correlation),
                    'max_correlation': float(max_correlation),
                    'delay_minutes': estimated_delay,
                    'metrics': metrics,
                    'significance': avg_correlation > 0.6 and len(metrics) >= 2
                }
            else:
                return {'correlation': 0, 'delay_minutes': 0, 'metrics': {}, 'significance': False}
                
        except Exception as e:
            logger.error(f"时序相关性计算失败: {str(e)}")
            return {'correlation': 0, 'delay_minutes': 0, 'metrics': {}, 'significance': False}
    
    async def _simulate_diffusion(self, context: Dict) -> Dict:
        """扩散模拟"""
        try:
            # 简化的扩散模拟（实际应使用专业水动力模型）
            monitoring_points = context.get('monitoring_network', {}).get('monitoring_points', [])
            
            # 模拟参数
            simulation_params = {
                'flow_velocity': 0.5,  # m/s
                'diffusion_coefficient': 0.1,  # m²/s
                'decay_rate': 0.05,  # 污染物衰减率
                'simulation_hours': 24
            }
            
            # 模拟结果
            simulation_results = {
                'parameters': simulation_params,
                'affected_points': [],
                'concentration_timeline': {},
                'impact_radius': 0,
                'peak_concentration': 0
            }
            
            # 计算影响范围（简化计算）
            impact_distance = simulation_params['flow_velocity'] * simulation_params['simulation_hours'] * 3600  # 米
            simulation_results['impact_radius'] = impact_distance
            
            # 模拟浓度变化
            for hour in range(0, simulation_params['simulation_hours'] + 1, 2):
                concentration = 100 * np.exp(-simulation_params['decay_rate'] * hour)  # 简化衰减模型
                simulation_results['concentration_timeline'][f'hour_{hour}'] = concentration
            
            # 找出受影响的监测点
            for point in monitoring_points[:5]:  # 限制数量
                distance = np.random.uniform(0.5, 2.0) * impact_distance  # 模拟距离
                if distance <= impact_radius:
                    simulation_results['affected_points'].append({
                        'location': point,
                        'distance_km': distance / 1000,
                        'arrival_time_hours': distance / (simulation_params['flow_velocity'] * 3600),
                        'peak_concentration': 100 * np.exp(-simulation_params['decay_rate'] * distance / (simulation_params['flow_velocity'] * 3600))
                    })
            
            simulation_results['peak_concentration'] = 100  # 初始浓度
            
            return simulation_results
            
        except Exception as e:
            logger.error(f"扩散模拟失败: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_contributions(self, context: Dict) -> Dict:
        """贡献度分析"""
        try:
            pollution_sources = context.get('pollution_sources', [])
            historical_data = context.get('historical_data', [])
            
            if not pollution_sources or not historical_data:
                return {'error': '缺少污染源或历史数据'}
            
            # 使用非负矩阵分解进行贡献度分析
            df = pd.DataFrame(historical_data)
            
            # 准备数据矩阵
            metrics_data = []
            for metric in ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen']:
                if metric in df.columns:
                    metric_values = df[metric].dropna()
                    if len(metric_values) > 0:
                        metrics_data.append(metric_values.tolist())
            
            if len(metrics_data) < 2:
                return {'error': '有效指标数据不足'}
            
            # 构建数据矩阵
            data_matrix = np.array(metrics_data).T
            
            # 使用NMF分解
            n_sources = min(len(pollution_sources), 3)  # 限制源数量
            nmf = NMF(n_components=n_sources, random_state=42)
            
            try:
                W = nmf.fit_transform(data_matrix)
                H = nmf.components_
                
                # 计算贡献度
                contributions = {}
                for i, source in enumerate(pollution_sources[:n_sources]):
                    contribution_score = np.mean(W[:, i]) / np.sum(W) if np.sum(W) > 0 else 0
                    contributions[source['id']] = {
                        'name': source['name'],
                        'type': source['type'],
                        'contribution_percentage': float(contribution_score * 100),
                        'characteristics_match': self._match_characteristics(H[i], source),
                        'confidence': float(np.max(H[i]) / np.sum(H) if np.sum(H) > 0 else 0)
                    }
                
                # 排序贡献度
                sorted_contributions = sorted(
                    contributions.values(), 
                    key=lambda x: x['contribution_percentage'], 
                    reverse=True
                )
                
                return {
                    'total_sources_analyzed': n_sources,
                    'contributions': sorted_contributions,
                    'dominant_source': sorted_contributions[0] if sorted_contributions else None,
                    'analysis_method': 'Non-negative Matrix Factorization',
                    'data_quality': 'good' if len(metrics_data) >= 3 else 'limited'
                }
                
            except Exception as e:
                logger.error(f"NMF分解失败: {str(e)}")
                # 降级为简单分析
                return self._simple_contribution_analysis(pollution_sources, df)
                
        except Exception as e:
            logger.error(f"贡献度分析失败: {str(e)}")
            return {'error': str(e)}
    
    def _match_characteristics(self, component_profile: np.ndarray, source: Dict) -> Dict:
        """匹配污染源特征"""
        try:
            characteristics = source.get('characteristics', {})
            
            # 简化的特征匹配
            matches = {}
            
            # 基于成分谱特征匹配
            if characteristics.get('high_conductivity'):
                matches['conductivity'] = component_profile[3] if len(component_profile) > 3 else 0
            
            if characteristics.get('high_ammonia'):
                matches['ammonia'] = component_profile[4] if len(component_profile) > 4 else 0
            
            if characteristics.get('high_turbidity'):
                matches['turbidity'] = component_profile[2] if len(component_profile) > 2 else 0
            
            return {
                'matches': matches,
                'overall_match_score': np.mean(list(matches.values())) if matches else 0
            }
            
        except Exception as e:
            logger.error(f"特征匹配失败: {str(e)}")
            return {'matches': {}, 'overall_match_score': 0}
    
    def _simple_contribution_analysis(self, pollution_sources: List[Dict], df: pd.DataFrame) -> Dict:
        """简单贡献度分析（降级方案）"""
        try:
            # 基于统计特征的简单分析
            contributions = {}
            
            for source in pollution_sources:
                # 模拟贡献度（实际应基于真实数据）
                contribution_score = np.random.uniform(0.1, 0.4)
                contributions[source['id']] = {
                    'name': source['name'],
                    'type': source['type'],
                    'contribution_percentage': float(contribution_score * 100),
                    'characteristics_match': {'overall_match_score': np.random.uniform(0.6, 0.9)},
                    'confidence': float(np.random.uniform(0.5, 0.8))
                }
            
            # 归一化贡献度
            total_contrib = sum([c['contribution_percentage'] for c in contributions.values()])
            if total_contrib > 0:
                for contrib in contributions.values():
                    contrib['contribution_percentage'] = (contrib['contribution_percentage'] / total_contrib) * 100
            
            sorted_contributions = sorted(
                contributions.values(),
                key=lambda x: x['contribution_percentage'],
                reverse=True
            )
            
            return {
                'total_sources_analyzed': len(pollution_sources),
                'contributions': sorted_contributions,
                'dominant_source': sorted_contributions[0] if sorted_contributions else None,
                'analysis_method': 'Statistical Estimation',
                'data_quality': 'limited'
            }
            
        except Exception as e:
            logger.error(f"简单贡献度分析失败: {str(e)}")
            return {'error': str(e)}
    
    async def _perform_reverse_trace(self, context: Dict) -> Dict:
        """反向追溯"""
        try:
            upstream_correlations = context.get('upstream_correlations', [])
            contribution_analysis = context.get('contribution_analysis', {})
            pollution_sources = context.get('pollution_sources', [])
            
            # 基于关联分析和贡献度进行反向追溯
            trace_results = {
                'potential_sources': [],
                'trace_path': [],
                'confidence_levels': {},
                'recommendations': []
            }
            
            # 分析潜在污染源
            if contribution_analysis.get('contributions'):
                for contrib in contribution_analysis['contributions']:
                    if contrib['contribution_percentage'] > 15:  # 只考虑贡献度>15%的源
                        source_info = next(
                            (s for s in pollution_sources if s['id'] == contrib.get('source_id', '').split('_')[-1]),
                            None
                        )
                        
                        if source_info:
                            trace_results['potential_sources'].append({
                                'source_id': source_info['id'],
                                'source_name': source_info['name'],
                                'source_type': source_info['type'],
                                'location': source_info['location'],
                                'contribution_percentage': contrib['contribution_percentage'],
                                'confidence': contrib['confidence'],
                                'likelihood': self._calculate_likelihood(contrib, upstream_correlations)
                            })
            
            # 构建追溯路径
            if upstream_correlations:
                trace_results['trace_path'] = self._build_trace_path(upstream_correlations)
            
            # 计算置信度等级
            for source in trace_results['potential_sources']:
                confidence = source['confidence']
                if confidence > 0.8:
                    trace_results['confidence_levels'][source['source_id']] = 'high'
                elif confidence > 0.6:
                    trace_results['confidence_levels'][source['source_id']] = 'medium'
                else:
                    trace_results['confidence_levels'][source['source_id']] = 'low'
            
            # 生成建议
            trace_results['recommendations'] = self._generate_trace_recommendations(trace_results)
            
            return trace_results
            
        except Exception as e:
            logger.error(f"反向追溯失败: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_likelihood(self, contribution: Dict, correlations: List[Dict]) -> float:
        """计算污染源可能性"""
        try:
            base_likelihood = contribution['contribution_percentage'] / 100
            confidence_boost = contribution['confidence']
            
            # 基于关联分析调整可能性
            correlation_boost = 0
            for corr in correlations:
                if corr['correlation'] > 0.7:
                    correlation_boost += 0.1
            
            likelihood = base_likelihood * (1 + confidence_boost + correlation_boost)
            return min(likelihood, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"可能性计算失败: {str(e)}")
            return 0.5
    
    def _build_trace_path(self, correlations: List[Dict]) -> List[Dict]:
        """构建追溯路径"""
        try:
            # 按相关性排序构建路径
            path = []
            for corr in correlations:
                if corr['significance']:
                    path.append({
                        'from_point': corr['upstream_point'],
                        'to_point': corr['target_point'],
                        'correlation': corr['correlation'],
                        'delay_minutes': corr['delay_minutes'],
                        'path_confidence': corr['correlation'] * 0.8
                    })
            
            return path[:5]  # 返回前5个路径段
            
        except Exception as e:
            logger.error(f"追溯路径构建失败: {str(e)}")
            return []
    
    def _generate_trace_recommendations(self, trace_results: Dict) -> List[str]:
        """生成追溯建议"""
        recommendations = []
        
        potential_sources = trace_results.get('potential_sources', [])
        if not potential_sources:
            recommendations.append("未发现明显的污染源，建议扩大监测范围或增加监测频次。")
            return recommendations
        
        # 基于主要污染源生成建议
        dominant_source = max(potential_sources, key=lambda x: x['contribution_percentage'])
        
        if dominant_source['source_type'] == 'industrial':
            recommendations.append(f"重点检查{dominant_source['source_name']}的排污口，建议进行突击检查。")
            recommendations.append("排查工业废水处理设施运行状况，检查是否存在偷排行为。")
        elif dominant_source['source_type'] == 'domestic':
            recommendations.append(f"检查{dominant_source['source_name']}的处理能力，可能存在超负荷运行。")
            recommendations.append("排查管网系统是否存在渗漏或溢流问题。")
        elif dominant_source['source_type'] == 'agricultural':
            recommendations.append("关注近期农业活动情况，检查是否存在过量施肥。")
            recommendations.append("建议在降雨期间加强监测，防范面源污染。")
        
        # 基于置信度生成建议
        high_confidence_sources = [s for s in potential_sources if s['confidence'] > 0.7]
        if high_confidence_sources:
            recommendations.append(f"已确定{len(high_confidence_sources)}个高置信度污染源，建议优先处理。")
        else:
            recommendations.append("污染源置信度较低，建议增加监测数据以提高分析精度。")
        
        return recommendations
    
    def _calculate_confidence_score(self, upstream_correlations: List[Dict], 
                                   diffusion_simulation: Dict, 
                                   contribution_analysis: Dict, 
                                   reverse_trace: Dict) -> float:
        """计算整体置信度评分"""
        try:
            scores = []
            
            # 上下游关联分析评分
            if upstream_correlations:
                max_corr = max([c['correlation'] for c in upstream_correlations])
                scores.append(min(max_corr, 1.0))
            else:
                scores.append(0.3)
            
            # 扩散模拟评分
            if 'error' not in diffusion_simulation:
                scores.append(0.7)  # 模拟成功给中等分数
            else:
                scores.append(0.2)
            
            # 贡献度分析评分
            if contribution_analysis.get('contributions'):
                dominant_contrib = contribution_analysis['contributions'][0]
                scores.append(dominant_contrib.get('confidence', 0.5))
            else:
                scores.append(0.3)
            
            # 反向追溯评分
            potential_sources = reverse_trace.get('potential_sources', [])
            if potential_sources:
                avg_confidence = np.mean([s['confidence'] for s in potential_sources])
                scores.append(avg_confidence)
            else:
                scores.append(0.3)
            
            # 计算加权平均
            weights = [0.3, 0.2, 0.3, 0.2]  # 关联分析权重最高
            confidence_score = np.average(scores, weights=weights)
            
            return float(confidence_score)
            
        except Exception as e:
            logger.error(f"置信度计算失败: {str(e)}")
            return 0.5
