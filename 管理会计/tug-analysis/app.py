import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# 配置页面
st.set_page_config(
    page_title="TUG客户盈利分析系统",
    page_icon="📊",
    layout="wide"
)

# ==================== 数据加载函数 ====================
@st.cache_data
def load_historical_data():
    """从本地文件加载历史汇总数据"""
    try:
        # 方法1：使用相对于脚本位置的路径
        current_dir = Path(__file__).parent
        data_dir = current_dir / "data"
        file_path = data_dir / "historical_data.xlsx"
        
        # 方法2：如果方法1不行，尝试使用工作目录
        if not file_path.exists():
            data_dir = Path("data")
            file_path = data_dir / "historical_data.xlsx"
        
        # 创建目录（如果不存在）
        data_dir.mkdir(exist_ok=True)
        
        # 调试信息
        st.info(f"查找数据文件路径: {file_path}")
        st.info(f"文件是否存在: {file_path.exists()}")
        
        if file_path.exists():
            data = pd.read_excel(file_path)
            st.success(f"成功加载历史数据，共 {len(data)} 行")
            return data
        else:
            # 列出当前目录结构帮助调试
            st.error(f"历史数据文件不存在: {file_path}")
            st.info("当前目录内容:")
            for item in Path(".").rglob("*"):
                st.write(f" - {item}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"加载历史数据时出错: {e}")
        return pd.DataFrame()

@st.cache_data
def load_client_details():
    """从本地文件加载客户明细数据"""
    try:
        # 同样的路径处理方法
        current_dir = Path(__file__).parent
        data_dir = current_dir / "data"
        file_path = data_dir / "2020_client_details.xlsx"
        
        if not file_path.exists():
            data_dir = Path("data")
            file_path = data_dir / "2020_client_details.xlsx"
        
        data_dir.mkdir(exist_ok=True)
        
        st.info(f"查找客户数据文件路径: {file_path}")
        st.info(f"文件是否存在: {file_path.exists()}")
        
        if file_path.exists():
            data = pd.read_excel(file_path)
            st.success(f"成功加载客户数据，共 {len(data)} 行")
            return data
        else:
            st.error(f"客户明细数据文件不存在: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"加载客户明细数据时出错: {e}")
        return pd.DataFrame()

def convert_column_names_to_chinese(data):
    """将英文列名转换为中文"""
    column_mapping = {
        'ClientID': '客户ID',
        'ClientType': '客户类型',
        'Cor_Bo': '瓦楞纸板收入',
        'Cor_Ca': '瓦楞纸箱收入',
        'Die_Bo': '模切盒收入',
        'Ass_Ca': '组合纸箱收入',
        'HD_Cor': '重型瓦楞纸收入',
        'Cor_Bo_COGS': '瓦楞纸板成本',
        'Cor_Ca_COGS': '瓦楞纸箱成本',
        'Die_Bo_COGS': '模切盒成本',
        'Ass_Ca_COGS': '组合纸箱成本',
        'HD_Cor_COGS': '重型瓦楞纸成本',
        'Ships_count': '运输次数',
        'Orders_count': '订单数量',
        'ExpOr_count': '加急订单数量',
        'Queries_count': '问询次数',
        'Design_count': '设计小时数'
    }
    
    # 重命名列
    data = data.rename(columns=column_mapping)
    return data

def create_sample_data():
    """创建示例数据"""
    historical_sample = pd.DataFrame({
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Revenue': [5000000, 5500000, 6000000, 6500000, 7000000],
        'COGS': [3500000, 3850000, 4200000, 4550000, 4900000],
        'GrossProfit': [1500000, 1650000, 1800000, 1950000, 2100000],
        'OtherExpenses': [1200000, 1320000, 1440000, 1560000, 1680000],
        'NetProfit': [300000, 330000, 360000, 390000, 420000],
        'CustomerCount': [800, 850, 900, 950, 1000]
    })
    
    np.random.seed(42)
    n_clients = 1000
    
    client_sample = pd.DataFrame({
        '客户ID': range(1, n_clients+1),
        '客户类型': np.random.choice(['新客户', '老客户'], n_clients, p=[0.3, 0.7]),
        '瓦楞纸板收入': np.random.uniform(1000, 50000, n_clients),
        '瓦楞纸箱收入': np.random.uniform(1000, 30000, n_clients),
        '模切盒收入': np.random.uniform(500, 20000, n_clients),
        '组合纸箱收入': np.random.uniform(500, 15000, n_clients),
        '重型瓦楞纸收入': np.random.uniform(2000, 40000, n_clients),
        '瓦楞纸板成本': np.random.uniform(800, 40000, n_clients),
        '瓦楞纸箱成本': np.random.uniform(800, 24000, n_clients),
        '模切盒成本': np.random.uniform(400, 16000, n_clients),
        '组合纸箱成本': np.random.uniform(400, 12000, n_clients),
        '重型瓦楞纸成本': np.random.uniform(1600, 32000, n_clients),
        '运输次数': np.random.poisson(10, n_clients),
        '订单数量': np.random.poisson(50, n_clients),
        '加急订单数量': np.random.poisson(2, n_clients),
        '问询次数': np.random.poisson(5, n_clients),
        '设计小时数': np.random.poisson(3, n_clients)
    })
    
    return historical_sample, client_sample

# ==================== 利润计算函数 ====================
def calculate_correct_client_profits(client_data, total_other_expenses_2020):
    """根据正确的逻辑计算每个客户的净利润"""
    client_data = client_data.copy()
    
    # 确保客户ID存在
    if '客户ID' not in client_data.columns:
        client_data['客户ID'] = range(1, len(client_data)+1)
    
    # 1. 计算每个客户的毛利
    products = ['瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入']
    product_costs = ['瓦楞纸板成本', '瓦楞纸箱成本', '模切盒成本', '组合纸箱成本', '重型瓦楞纸成本']
    
    # 计算总收入
    client_data['总收入'] = 0
    for product in products:
        if product in client_data.columns:
            client_data['总收入'] += client_data[product]
    
    # 计算总销售成本
    client_data['总销售成本'] = 0
    for cost in product_costs:
        if cost in client_data.columns:
            client_data['总销售成本'] += client_data[cost]
    
    # 计算毛利
    client_data['毛利'] = client_data['总收入'] - client_data['总销售成本']
    client_data['毛利率'] = client_data['毛利'] / client_data['总收入']
    
    # 2. 计算五项变动其他费用（作业成本）
    activity_rates = {
        '运输次数': 7.00,
        '订单数量': 0.17,
        '加急订单数量': 267.00,
        '问询次数': 33.00,
        '设计小时数': 70.00
    }
    
    client_data['五项变动费用'] = 0
    for activity, rate in activity_rates.items():
        if activity in client_data.columns:
            client_data[f'{activity}成本'] = client_data[activity] * rate
            client_data['五项变动费用'] += client_data[f'{activity}成本']
    
    # 3. 计算佣金和剩余固定成本分摊
    total_five_activity_cost = client_data['五项变动费用'].sum()
    remaining_other_expenses = total_other_expenses_2020 - total_five_activity_cost
    
    # 定义产品佣金率（基于产品毛利率水平）
    product_commission_rates = {
        '瓦楞纸板收入': 0.03,    # 高毛利产品 >50%: 3%
        '瓦楞纸箱收入': 0.03,    # 高毛利产品 >50%: 3%
        '模切盒收入': 0.02,      # 中毛利产品 20-50%: 2%
        '组合纸箱收入': 0.01,   # 低毛利产品 <20%: 1%
        '重型瓦楞纸收入': 0.01  # 低毛利产品 <20%: 1%
    }
    
    # 计算每个客户的销售佣金
    client_data['分摊销售佣金'] = 0
    for product in products:
        if product in client_data.columns and product in product_commission_rates:
            commission_rate = product_commission_rates[product]
            client_data[f'{product}佣金'] = client_data[product] * commission_rate
            client_data['分摊销售佣金'] += client_data[f'{product}佣金']
    
    # 计算总佣金
    total_commission = client_data['分摊销售佣金'].sum()
    
    # 剩余部分作为固定成本，按收入比例分摊
    remaining_fixed_cost = remaining_other_expenses - total_commission
    
    # 按总收入比例分摊固定成本
    total_revenue = client_data['总收入'].sum()
    if total_revenue > 0:
        fixed_cost_rate = remaining_fixed_cost / total_revenue
        client_data['分摊固定成本'] = client_data['总收入'] * fixed_cost_rate
    else:
        client_data['分摊固定成本'] = 0
    
    # 4. 计算净利润
    client_data['净利润'] = (
        client_data['毛利'] - 
        client_data['五项变动费用'] - 
        client_data['分摊固定成本'] - 
        client_data['分摊销售佣金']
    )
    
    # 计算净利润率
    client_data['净利润率'] = client_data['净利润'] / client_data['总收入']
    
    return client_data, product_commission_rates, total_five_activity_cost, remaining_other_expenses, total_commission, remaining_fixed_cost


# ==================== Tab 1: 战略概览与客户分析 ====================
def create_tab1_analysis(history_data, client_data):
    """创建Tab1的数据概览分析"""
    
    st.header("📊 TUG经营绩效概览")
    
    # 获取2020年总其他营业费用
    if 2020 in history_data['Year'].values:
        total_other_expenses_2020 = history_data[history_data['Year'] == 2020]['OtherExpenses'].values[0]
    else:
        total_other_expenses_2020 = history_data['OtherExpenses'].max()
    
    # 计算客户利润
    client_profit_data, product_commission_rates, total_five_activity_cost, remaining_other_expenses, total_commission, remaining_fixed_cost = calculate_correct_client_profits(client_data, total_other_expenses_2020)
    
    # 顶部KPI指标卡
    st.subheader("关键绩效指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_year = history_data['Year'].max()
        latest_revenue = history_data[history_data['Year'] == latest_year]['Revenue'].values[0]
        prev_year = latest_year - 1
        if prev_year in history_data['Year'].values:
            prev_revenue = history_data[history_data['Year'] == prev_year]['Revenue'].values[0]
            delta_rev = f"{(latest_revenue/prev_revenue-1)*100:.1f}%"
        else:
            delta_rev = None
        st.metric("2020年总收入", f"${latest_revenue:,.0f}", delta=delta_rev)
    
    with col2:
        latest_profit = history_data[history_data['Year'] == latest_year]['NetProfit'].values[0]
        if prev_year in history_data['Year'].values:
            prev_profit = history_data[history_data['Year'] == prev_year]['NetProfit'].values[0]
            delta_profit = f"{(latest_profit/prev_profit-1)*100:.1f}%"
        else:
            delta_profit = None
        st.metric("2020年净利润", f"${latest_profit:,.0f}", delta=delta_profit)
    
    with col3:
        profit_margin = (latest_profit / latest_revenue) * 100
        if prev_year in history_data['Year'].values:
            prev_margin = (history_data[history_data['Year']==prev_year]['NetProfit'].values[0] / 
                          history_data[history_data['Year']==prev_year]['Revenue'].values[0]) * 100
            delta_margin = f"{(profit_margin - prev_margin):.1f}%"
        else:
            delta_margin = None
        st.metric("净利润率", f"{profit_margin:.1f}%", delta=delta_margin)
    
    with col4:
        if 2020 in history_data['Year'].values:
            current_customers = history_data[history_data['Year'] == 2020]['CustomerCount'].values[0]
        
        # 计算客户数量增长
            if 2019 in history_data['Year'].values:
                prev_customers = history_data[history_data['Year'] == 2019]['CustomerCount'].values[0]
                customer_growth = ((current_customers - prev_customers) / prev_customers) * 100
            # 显示客户数量和增长率
                st.metric(
                "客户数量", 
                f"{current_customers:,}",
                delta=f"{customer_growth:.1f}%"
            )
            # 如果没有2019年数据，只显示客户数量
            else:
                st.metric("客户数量", f"{current_customers:,}")
        else:
        # 如果没有2020年数据，使用客户数据中的客户数量
    
    
            current_customers = ""
    
    
    # 5年趋势分析 - 优化版本
    st.subheader("📈 5年经营趋势分析")

    # 创建3行2列的子图布局
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            '收入与净利润趋势', '客户数量增长趋势',
            '利润率变化趋势', '销售成本率变化',
            '费用率变化', '成本费用结构对比'
        ),
        specs=[
            [{"secondary_y": True}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 1. 收入与净利润趋势（第一行左）
    fig.add_trace(
        go.Scatter(
            x=history_data['Year'], 
            y=history_data['Revenue'],
            name="收入",
            line=dict(color='#1f77b4', width=4),
            text=[f"${x:,.0f}" for x in history_data['Revenue']],
            textposition="top center",
            showlegend=True
        ),
        row=1, col=1
    )


    fig.add_trace(
        go.Scatter(
            x=history_data['Year'], 
            y=history_data['NetProfit'],
            name="净利润",
            line=dict(color='#2ca02c', width=4),
            text=[f"${x:,.0f}" for x in history_data['NetProfit']],
            textposition="bottom center",
            showlegend=True
        ),
        row=1, col=1, secondary_y=True
    )

   
    # 2. 客户数量增长趋势（第一行右）
    fig.add_trace(
        go.Bar(
            x=history_data['Year'], 
            y=history_data['CustomerCount'],
            name="客户数量",
            marker_color='#ff7f0e',
            text=[f"{x:,}" for x in history_data['CustomerCount']],
            textposition="inside",
            showlegend=True
        ),
        row=1, col=2
    )

    

    # 3. 利润率变化趋势（第二行左）
    history_data['ProfitMargin'] = (history_data['NetProfit'] / history_data['Revenue']) * 100
    fig.add_trace(
        go.Scatter(
            x=history_data['Year'], 
            y=history_data['ProfitMargin'],
            name="净利润率",
            line=dict(color='#d62728', width=4),
            text=[f"{x:.1f}%" for x in history_data['ProfitMargin']],
            textposition="top center",
            showlegend=True
        ),
        row=2, col=1
    )

    # 为净利润率添加首尾数据标签
    for i, year in enumerate(history_data['Year']):
        if year == 2016 or year == 2020:
            fig.add_annotation(
                x=year, y=history_data['ProfitMargin'].iloc[i],
                text=f"{history_data['ProfitMargin'].iloc[i]:.1f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#d62728',
                bgcolor='white',
                bordercolor='#d62728',
                borderwidth=1,
                row=2, col=1
            )

    # 4. 销售成本率变化（第二行右）
    history_data['CostRatio'] = (history_data['COGS'] / history_data['Revenue']) * 100
    fig.add_trace(
        go.Scatter(
            x=history_data['Year'], 
            y=history_data['CostRatio'],
            name="销售成本率",
            line=dict(color='#9467bd', width=4),
            text=[f"{x:.1f}%" for x in history_data['CostRatio']],
            textposition="top center",
            showlegend=True
        ),
        row=2, col=2
    )

    # 为销售成本率添加首尾数据标签
    for i, year in enumerate(history_data['Year']):
        if year == 2016 or year == 2020:
            fig.add_annotation(
                x=year, y=history_data['CostRatio'].iloc[i],
                text=f"{history_data['CostRatio'].iloc[i]:.1f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#9467bd',
                bgcolor='white',
                bordercolor='#9467bd',
                borderwidth=1,
                row=2, col=2
            )

    # 5. 费用率变化（第三行左）
    history_data['ExpenseRatio'] = (history_data['OtherExpenses'] / history_data['Revenue']) * 100
    fig.add_trace(
        go.Scatter(
            x=history_data['Year'], 
            y=history_data['ExpenseRatio'],
            name="费用率",
            line=dict(color='#8c564b', width=4),
            text=[f"{x:.1f}%" for x in history_data['ExpenseRatio']],
            textposition="top center",
            showlegend=True
        ),
        row=3, col=1
    )

    # 为费用率添加首尾数据标签
    for i, year in enumerate(history_data['Year']):
        if year == 2016 or year == 2020:
            fig.add_annotation(
                x=year, y=history_data['ExpenseRatio'].iloc[i],
                text=f"{history_data['ExpenseRatio'].iloc[i]:.1f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#8c564b',
                bgcolor='white',
                bordercolor='#8c564b',
                borderwidth=1,
                row=3, col=1
            )

    # 6. 成本费用结构对比（第三行右）
    # 计算各项占比
    history_data['GrossProfitRatio'] = (history_data['GrossProfit'] / history_data['Revenue']) * 100
    history_data['NetProfitRatio'] = (history_data['NetProfit'] / history_data['Revenue']) * 100

    fig.add_trace(
        go.Bar(
            x=history_data['Year'],
            y=history_data['CostRatio'],
            name="销售成本率",
            marker_color='#9467bd',
            text=[f"{x:.1f}%" for x in history_data['CostRatio']],
            textposition="inside",
            showlegend=True
        ),
        row=3, col=2
    )

    fig.add_trace(
        go.Bar(
            x=history_data['Year'],
            y=history_data['ExpenseRatio'],
            name="费用率",
            marker_color='#8c564b',
            text=[f"{x:.1f}%" for x in history_data['ExpenseRatio']],
            textposition="inside",
            showlegend=True
        ),
        row=3, col=2
    )

    fig.add_trace(
        go.Bar(
            x=history_data['Year'],
            y=history_data['NetProfitRatio'],
            name="净利润率",
            marker_color='#2ca02c',
            text=[f"{x:.1f}%" for x in history_data['NetProfitRatio']],
            textposition="inside",
            showlegend=True
        ),
        row=3, col=2
    )

    # 更新布局
    fig.update_layout(
        height=900,
        showlegend=True,
        title_text="TUG 5年经营绩效深度分析",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # 设置y轴标题
    fig.update_yaxes(title_text="收入 ($)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="净利润 ($)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="客户数量", row=1, col=2)
    fig.update_yaxes(title_text="利润率 (%)", row=2, col=1)
    fig.update_yaxes(title_text="销售成本率 (%)", row=2, col=2)
    fig.update_yaxes(title_text="费用率 (%)", row=3, col=1)
    fig.update_yaxes(title_text="比率 (%)", row=3, col=2)

    # 设置x轴标题
    for i in [1, 2, 3]:
        fig.update_xaxes(title_text="年份", row=i, col=1)
        fig.update_xaxes(title_text="年份", row=i, col=2)

    st.plotly_chart(fig, use_container_width=True)

    # 利润率影响因素分析
    st.subheader("🔍 利润率影响因素分析")

    # 计算各项对利润率的影响
    history_data['CostImpact'] = history_data['CostRatio'] - history_data['CostRatio'].iloc[0]
    history_data['ExpenseImpact'] = history_data['ExpenseRatio'] - history_data['ExpenseRatio'].iloc[0]
    history_data['MarginImpact'] = history_data['ProfitMargin'] - history_data['ProfitMargin'].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        # 利润率变化分解
        impact_data = []
        for i, year in enumerate(history_data['Year']):
            if year > 2016:  # 从2017年开始计算变化
                cost_impact = history_data['CostImpact'].iloc[i]
                expense_impact = history_data['ExpenseImpact'].iloc[i]
                actual_margin_change = history_data['MarginImpact'].iloc[i]
                
                # 理论上的利润率变化（如果只有成本或费用变化）
                theoretical_margin_cost = -cost_impact  # 成本上升对利润率的负面影响
                theoretical_margin_expense = -expense_impact  # 费用上升对利润率的负面影响
                
                impact_data.append({
                    'Year': year,
                    '成本上升影响': theoretical_margin_cost,
                    '费用上升影响': theoretical_margin_expense,
                    '实际利润率变化': actual_margin_change
                })
        
        if impact_data:
            impact_df = pd.DataFrame(impact_data)
            
            fig_impact = go.Figure()
            
            fig_impact.add_trace(go.Bar(
                name='成本上升对利润率影响',
                x=impact_df['Year'],
                y=impact_df['成本上升影响'],
                marker_color='#9467bd'
            ))
            
            fig_impact.add_trace(go.Bar(
                name='费用上升对利润率影响',
                x=impact_df['Year'],
                y=impact_df['费用上升影响'],
                marker_color='#8c564b'
            ))
            
            fig_impact.add_trace(go.Scatter(
                name='实际利润率变化',
                x=impact_df['Year'],
                y=impact_df['实际利润率变化'],
                mode='lines+markers',
                line=dict(color='#d62728', width=3),
                marker=dict(size=8)
            ))
            
            fig_impact.update_layout(
                title="利润率变化因素分解",
                xaxis_title="年份",
                yaxis_title="利润率变化 (百分点)",
                barmode='stack',
                height=400
            )
            
            st.plotly_chart(fig_impact, use_container_width=True)

    with col2:
        # 关键洞察
        st.subheader("💡 利润率变化关键洞察")
        
        insights = []
        
        # 分析利润率变化原因
        margin_2016 = history_data[history_data['Year'] == 2016]['ProfitMargin'].values[0]
        margin_2020 = history_data[history_data['Year'] == 2020]['ProfitMargin'].values[0]
        margin_change = margin_2020 - margin_2016
        
        cost_2016 = history_data[history_data['Year'] == 2016]['CostRatio'].values[0]
        cost_2020 = history_data[history_data['Year'] == 2020]['CostRatio'].values[0]
        cost_change = cost_2020 - cost_2016
        
        expense_2016 = history_data[history_data['Year'] == 2016]['ExpenseRatio'].values[0]
        expense_2020 = history_data[history_data['Year'] == 2020]['ExpenseRatio'].values[0]
        expense_change = expense_2020 - expense_2016
        
        if margin_change < 0:
            insights.append(f"净利润率从{margin_2016:.1f}%下降至{margin_2020:.1f}%，共下降{abs(margin_change):.1f}个百分点")
            
            if expense_change > 0:
                insights.append(f"费用率上升{expense_change:.1f}个百分点，是利润率下降的主要因素")    

            if cost_change > 0:
                insights.append(f"销售成本率上升{cost_change:.1f}个百分点，加剧了利润率压力")
            
            
            

        
        else:
            insights.append(f"净利润率从{margin_2016:.1f}%上升至{margin_2020:.1f}%，共提升{margin_change:.1f}个百分点")
            
            if cost_change < 0:
                insights.append(f"销售成本率下降{abs(cost_change):.1f}个百分点，是利润率改善的主要因素")
            
            if expense_change < 0:
                insights.append(f"费用率下降{abs(expense_change):.1f}个百分点，促进了利润率提升")
        
        # 添加基于数据的建议
        if margin_change < 0:
            if cost_change > 1:  # 成本上升明显
                insights.append("**建议**: 优化供应链管理，控制原材料成本")
            
            if expense_change > 1:  # 费用上升明显
                insights.append("**建议**: 审查费用结构，提高运营效率")
        
        for i, insight in enumerate(insights, 1):
            if "建议" in insight:
                st.success(f"{i}. {insight}")
            else:
                st.info(f"{i}. {insight}")
    



    
    
    
    


    # 客户毛利分析
    st.subheader("💰 客户盈利性分析")
    
    col3, col4 = st.columns(2)
    
    with col3:
    # 客户毛利率分布直方图
        
        fig_margin_rate_hist = px.histogram(
            client_profit_data, 
            x='毛利率',
            nbins=50,
            title="客户毛利率分布",
            color_discrete_sequence=['#2ca02c']
        )
        fig_margin_rate_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="盈亏平衡线")
        fig_margin_rate_hist.update_layout(
            xaxis_title="毛利率",
            yaxis_title="客户数量"
        )
        st.plotly_chart(fig_margin_rate_hist, use_container_width=True)
    with col4:
        # 客户毛利分布直方图
        fig_margin_hist = px.histogram(
            client_profit_data, 
            x='毛利',
            nbins=50,
            title="客户毛利分布",
            color_discrete_sequence=['#ff7f0e']
        )
        fig_margin_hist.add_vline(x=100000, line_dash="dash", line_color="red", annotation_text="低毛利线")
        fig_margin_hist.update_layout(
            xaxis_title="毛利 ($)",
            yaxis_title="客户数量"
        )
        st.plotly_chart(fig_margin_hist, use_container_width=True)
    
    # 毛利统计信息
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        avg_margin = client_profit_data['毛利'].mean()
        st.metric("平均毛利", f"${avg_margin:,.0f}")
    
    with col6:
        median_margin = client_profit_data['毛利'].median()
        st.metric("毛利中位数", f"${median_margin:,.0f}")
    
    with col7:
        margin_ratio = (client_profit_data['毛利'] / client_profit_data['总收入']).mean() * 100
        st.metric("平均毛利率", f"{margin_ratio:.1f}%")
    
    with col8:
        low_margin_clients = len(client_profit_data[client_profit_data['毛利']  <100000])
        st.metric("低毛利客户(<100k)", f"{low_margin_clients}个")
    
# 客户盈利性分析
   

    col1, col2 = st.columns(2)

    with col1:
        profitable_clients = len(client_profit_data[client_profit_data['净利润'] > 0])
        non_profitable_clients = len(client_profit_data) - profitable_clients
    
        fig_pie = px.pie(
        values=[profitable_clients, non_profitable_clients],
        names=['盈利客户', '非盈利客户'],
        title="客户盈利性分布",
        color_discrete_sequence=['#2ca02c', '#d62728']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_hist = px.histogram(
        client_profit_data, 
        x='净利润',
        nbins=50,
        title="客户净利润分布",
        color_discrete_sequence=['#1f77b4']
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_hist, use_container_width=True)

# 新增的净利润统计信息
    
    col9, col10, col11, col12, col13 = st.columns(5)

    with col9:
        avg_net_profit = client_profit_data['净利润'].mean()
        st.metric("平均净利", f"${avg_net_profit:,.0f}")

    with col10:
        median_net_profit = client_profit_data['净利润'].median()
        st.metric("净利中位数", f"${median_net_profit:,.0f}")

    with col11:
        net_profit_ratio = (client_profit_data['净利润'] / client_profit_data['总收入']).mean() * 100
        st.metric("平均净利率", f"{net_profit_ratio:.1f}%")

    with col12:
        profitable_clients_count = len(client_profit_data[client_profit_data['净利润'] > 0])
        st.metric("盈利客户数量", f"{profitable_clients_count}个")

    with col13:
        non_profitable_clients_count = len(client_profit_data[client_profit_data['净利润'] <= 0])
        st.metric("非盈利客户数量", f"{non_profitable_clients_count}个")

# 新增：两类客户的利润贡献分析
    st.subheader("💰 两类客户利润贡献分析")

# 计算盈利客户和非盈利客户的总利润
    profitable_clients_profit = client_profit_data[client_profit_data['净利润'] > 0]['净利润'].sum()
    non_profitable_clients_profit = client_profit_data[client_profit_data['净利润'] <= 0]['净利润'].sum()
    total_net_profit = client_profit_data['净利润'].sum()

# 计算贡献比例
    profitable_contribution_ratio = (profitable_clients_profit / total_net_profit) * 100 if total_net_profit != 0 else 0
    non_profitable_contribution_ratio = (non_profitable_clients_profit / total_net_profit) * 100 if total_net_profit != 0 else 0

    col14, col15, col16 = st.columns(3)

    with col14:
        st.metric(
        "盈利客户总利润贡献",
        f"${profitable_clients_profit:,.0f}",
        
    )

    with col15:
        st.metric(
        "非盈利客户总利润损失",
        f"${non_profitable_clients_profit:,.0f}",
        
    )

    with col16:
        st.metric(
        "净利总和",
        f"${total_net_profit:,.0f}"
    )

# 使用条状图展示两类客户的利润贡献
    profit_contribution_data = {
    '客户类型': ['盈利客户', '非盈利客户'],
    '利润金额': [profitable_clients_profit, non_profitable_clients_profit],
    '贡献比例': [profitable_contribution_ratio, non_profitable_contribution_ratio]
}
    profit_contribution_df = pd.DataFrame(profit_contribution_data)

# 创建条状图
    fig_bar = px.bar(
    profit_contribution_df,
    x='客户类型',
    y='利润金额',
    title="两类客户利润贡献对比",
    color='客户类型',
    color_discrete_map={'盈利客户': '#2ca02c', '非盈利客户': '#d62728'},
    text='利润金额'
)

# 格式化条状图
    fig_bar.update_traces(
    texttemplate='$%{text:,.0f}',
    textposition='inside'
)

# 更新布局
    fig_bar.update_layout(
    xaxis_title="客户类型",
    yaxis_title="利润金额 ($)",
    showlegend=False
)



    st.plotly_chart(fig_bar, use_container_width=True)


# 产品组合分析
    st.subheader("📦 产品组合分析")

    products = ['瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入']
    product_costs = ['瓦楞纸板成本', '瓦楞纸箱成本', '模切盒成本', '组合纸箱成本', '重型瓦楞纸成本']
    product_names = ['瓦楞纸板', '瓦楞纸箱', '模切盒', '组合纸箱', '重型瓦楞纸']

# 为每个产品定义固定颜色
    product_colors = {
    '瓦楞纸板': '#1f77b4',  # 蓝色
    '瓦楞纸箱': '#ff7f0e',  # 橙色
    '模切盒': '#2ca02c',    # 绿色
    '组合纸箱': '#d62728',  # 红色
    '重型瓦楞纸': '#9467bd' # 紫色
}

    product_data = []

    for i, product in enumerate(products):
        total_revenue = client_data[product].sum()
        total_cogs = client_data[product_costs[i]].sum()
        gross_margin = ((total_revenue - total_cogs) / total_revenue * 100) if total_revenue > 0 else 0
    
        product_data.append({
        '产品': product_names[i],
        '总收入': total_revenue,
        '总成本': total_cogs,
        '总毛利': total_revenue - total_cogs,
        '毛利率': gross_margin
    })

    product_df = pd.DataFrame(product_data)

    col1, col2 = st.columns(2)

    with col1:
    # 产品收入贡献饼图 - 使用固定颜色
        fig_product_revenue = px.pie(
            product_df,
            values='总收入',
            names='产品',
            title="产品收入贡献",
            color='产品',
            color_discrete_map=product_colors
        )
        st.plotly_chart(fig_product_revenue, use_container_width=True)

    with col2:
    # 各产品毛利率对比条形图 - 使用固定颜色
        fig_product_margin = px.bar(
        product_df,
        x='产品',
        y='毛利率',
        title="各产品毛利率对比",
        color='产品',
        color_discrete_map=product_colors,
        text='毛利率'
        )
        fig_product_margin.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
        fig_product_margin.update_layout(
        showlegend=False,  # 由于颜色已经固定，可以隐藏图例以避免重复
        xaxis_title="产品",
        yaxis_title="毛利率 (%)"
        )
        st.plotly_chart(fig_product_margin, use_container_width=True)
    

# 🎯 客户分层与盈利改善策略
    st.subheader("🎯 客户分层与盈利改善策略")

# 客户分层概览
    st.write("### 客户分层概览")

# 分层标准
    st.write("**分层标准**:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**高毛利客户**: 毛利率 ≥ 40%")
    with col2:
        st.warning("**中毛利客户**: 毛利率 20% - 40%")
    with col3:
        st.error("**低毛利客户**: 毛利率 ≤ 20%")

# 计算各层级客户数量分布
    high_margin_clients = len(client_profit_data[client_profit_data['毛利率'] >= 0.4])
    medium_margin_clients = len(client_profit_data[(client_profit_data['毛利率'] >= 0.2) & (client_profit_data['毛利率'] < 0.4)])
    low_margin_clients = len(client_profit_data[client_profit_data['毛利率'] <= 0.2])
    total_clients = len(client_profit_data)

# 计算各层级盈利客户比例
    high_margin_profitable = len(client_profit_data[(client_profit_data['毛利率'] >= 0.4) & (client_profit_data['净利润'] > 0)])
    medium_margin_profitable = len(client_profit_data[(client_profit_data['毛利率'] >= 0.2) & (client_profit_data['毛利率'] < 0.4) & (client_profit_data['净利润'] > 0)])
    low_margin_profitable = len(client_profit_data[(client_profit_data['毛利率'] <= 0.2) & (client_profit_data['净利润'] > 0)])

# 各层级基本统计
    st.write("#### 各层级基本统计")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
        "高毛利客户",
        f"{high_margin_clients}个",
        delta=f"{(high_margin_clients/total_clients*100):.1f}%"
    )
        st.metric(
        "其中盈利客户",
        f"{high_margin_profitable}个",
        delta=f"{(high_margin_profitable/high_margin_clients*100):.1f}%" if high_margin_clients > 0 else "0%"
    )

    with col2:
        st.metric(
        "中毛利客户",
        f"{medium_margin_clients}个",
        delta=f"{(medium_margin_clients/total_clients*100):.1f}%"
    )
        st.metric(
        "其中盈利客户",
        f"{medium_margin_profitable}个",
        delta=f"{(medium_margin_profitable/medium_margin_clients*100):.1f}%" if medium_margin_clients > 0 else "0%"
    )

    with col3:
        st.metric(
        "低毛利客户",
        f"{low_margin_clients}个",
        delta=f"{(low_margin_clients/total_clients*100):.1f}%"
    )
        st.metric(
        "其中盈利客户",
        f"{low_margin_profitable}个",
        delta=f"{(low_margin_profitable/low_margin_clients*100):.1f}%" if low_margin_clients > 0 else "0%"
    )

# 分层深度分析
    st.write("### 分层深度分析")

# 计算各层级的利润贡献
    high_margin_profit = client_profit_data[client_profit_data['毛利率'] >= 0.4]['净利润'].sum()
    medium_margin_profit = client_profit_data[(client_profit_data['毛利率'] >= 0.2) & (client_profit_data['毛利率'] < 0.4)]['净利润'].sum()
    low_margin_profit = client_profit_data[client_profit_data['毛利率'] <= 0.2]['净利润'].sum()
    total_profit = client_profit_data['净利润'].sum()

# 计算各层级收入贡献
    high_margin_revenue = client_profit_data[client_profit_data['毛利率'] >= 0.4]['总收入'].sum()
    medium_margin_revenue = client_profit_data[(client_profit_data['毛利率'] >= 0.2) & (client_profit_data['毛利率'] < 0.4)]['总收入'].sum()
    low_margin_revenue = client_profit_data[client_profit_data['毛利率'] <= 0.2]['总收入'].sum()
    total_revenue = client_profit_data['总收入'].sum()

# 各层级利润和收入贡献
    st.write("#### 各层级利润和收入贡献")
    col1, col2 = st.columns(2)

    with col1:
    # 利润贡献饼图
        profit_data = {
        '层级': ['高毛利客户', '中毛利客户', '低毛利客户'],
        '利润': [high_margin_profit, medium_margin_profit, low_margin_profit]
        }
        profit_df = pd.DataFrame(profit_data)
    
        fig_profit_pie = px.pie(
        profit_df,
        values='利润',
        names='层级',
        title="各层级利润贡献分布",
        color='层级',
        color_discrete_map={
            '高毛利客户': '#2ca02c',
            '中毛利客户': '#ff7f0e', 
            '低毛利客户': '#d62728'
            }
        )
        fig_profit_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_profit_pie, use_container_width=True)

    with col2:
    # 收入贡献饼图
        revenue_data = {
        '层级': ['高毛利客户', '中毛利客户', '低毛利客户'],
        '收入': [high_margin_revenue, medium_margin_revenue, low_margin_revenue]
        }
        revenue_df = pd.DataFrame(revenue_data)
    
        fig_revenue_pie = px.pie(
        revenue_df,
        values='收入',
        names='层级',
        title="各层级收入贡献分布",
        color='层级',
        color_discrete_map={
            '高毛利客户': '#2ca02c',
            '中毛利客户': '#ff7f0e',
            '低毛利客户': '#d62728'
        }
        )
        fig_revenue_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_revenue_pie, use_container_width=True)

# 各层级详细指标
    st.write("#### 各层级详细指标")

# 创建详细指标表格
    metrics_data = {
    '层级': ['高毛利客户', '中毛利客户', '低毛利客户', '总计'],
    '客户数量': [high_margin_clients, medium_margin_clients, low_margin_clients, total_clients],
    '客户占比': [
        f"{(high_margin_clients/total_clients*100):.1f}%",
        f"{(medium_margin_clients/total_clients*100):.1f}%", 
        f"{(low_margin_clients/total_clients*100):.1f}%",
        "100%"
    ],
    '盈利客户数': [high_margin_profitable, medium_margin_profitable, low_margin_profitable, high_margin_profitable+medium_margin_profitable+low_margin_profitable],
    '盈利客户占比': [
        f"{(high_margin_profitable/high_margin_clients*100):.1f}%" if high_margin_clients > 0 else "0%",
        f"{(medium_margin_profitable/medium_margin_clients*100):.1f}%" if medium_margin_clients > 0 else "0%",
        f"{(low_margin_profitable/low_margin_clients*100):.1f}%" if low_margin_clients > 0 else "0%",
        f"{((high_margin_profitable+medium_margin_profitable+low_margin_profitable)/total_clients*100):.1f}%"
    ],
    '利润贡献': [high_margin_profit, medium_margin_profit, low_margin_profit, total_profit],
    '利润贡献占比': [
        f"{(high_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "0%",
        f"{(medium_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "0%",
        f"{(low_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "0%",
        "100%"
    ],
    '收入贡献': [high_margin_revenue, medium_margin_revenue, low_margin_revenue, total_revenue],
    '收入贡献占比': [
        f"{(high_margin_revenue/total_revenue*100):.1f}%" if total_revenue > 0 else "0%",
        f"{(medium_margin_revenue/total_revenue*100):.1f}%" if total_revenue > 0 else "0%",
        f"{(low_margin_revenue/total_revenue*100):.1f}%" if total_revenue > 0 else "0%",
        "100%"
    ]
}

    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, use_container_width=True)

# 针对性改善策略
    st.write("### 针对性改善策略")

# 高毛利客户群策略
    with st.expander("💰 高毛利客户群 (毛利率 ≥ 40%)", expanded=True):
        st.write(f"**现状分析**:")
        st.write(f"- 客户数量占比: {(high_margin_clients/total_clients*100):.1f}%")
        st.write(f"- 利润贡献占比: {(high_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "- 利润贡献占比: 0%")
        st.write(f"- 亏损客户占比: {((high_margin_clients-high_margin_profitable)/high_margin_clients*100):.1f}%" if high_margin_clients > 0 else "- 亏损客户占比: 0%")
    
        st.write("**核心问题**: 高毛利但仍存在亏损客户，说明间接费用分摊不合理")
    
        st.write("**改善策略**:")
        st.write("1. **费用结构优化**")
        st.write("   - 重新评估高成本服务（设计、加急订单）的收费")
        st.write("   - 对定制化服务实施单独定价")
        st.write("   - 优化作业成本分摊基础")
    
        st.write("2. **服务价值提升**")
        st.write("   - 为重点客户提供增值服务包")
        st.write("   - 建立战略客户管理体系")
        st.write("   - 提高客户黏性和钱包份额")

# 中毛利客户群策略
    with st.expander("🔄 中毛利客户群 (毛利率 20%-40%)", expanded=False):
        st.write(f"**现状分析**:")
        st.write(f"- 客户数量占比: {(medium_margin_clients/total_clients*100):.1f}%")
        st.write(f"- 利润贡献占比: {(medium_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "- 利润贡献占比: 0%")
        st.write(f"- 亏损客户占比: {((medium_margin_clients-medium_margin_profitable)/medium_margin_clients*100):.1f}%" if medium_margin_clients > 0 else "- 亏损客户占比: 0%")
        
        st.write("**核心问题**: 毛利率适中但被标准费用结构侵蚀利润")
        
        st.write("**改善策略**:")
        st.write("1. **流程标准化**")
        st.write("   - 推广标准化产品和服务流程")
        st.write("   - 优化订单处理效率")
        st.write("   - 减少非必要服务项目")
        
        st.write("2. **价格策略调整**")
        st.write("   - 适度调整价格覆盖实际成本")
        st.write("   - 实施阶梯定价策略")
        st.write("   - 引导客户转向高毛利产品组合")

    # 低毛利客户群策略
    with st.expander("📉 低毛利客户群 (毛利率 ≤ 20%)", expanded=False):
        st.write(f"**现状分析**:")
        st.write(f"- 客户数量占比: {(low_margin_clients/total_clients*100):.1f}%")
        st.write(f"- 利润贡献占比: {(low_margin_profit/total_profit*100):.1f}%" if total_profit != 0 else "- 利润贡献占比: 0%")
        st.write(f"- 亏损客户占比: {((low_margin_clients-low_margin_profitable)/low_margin_clients*100):.1f}%" if low_margin_clients > 0 else "- 亏损客户占比: 0%")
        
        st.write("**核心问题**: 基础盈利能力不足，难以覆盖固定成本")
        
        st.write("**改善策略**:")
        st.write("1. **严格成本控制**")
        st.write("   - 限制高成本服务使用")
        st.write("   - 实施最低订单量要求")
        st.write("   - 优化物流和配送成本")
        
        st.write("2. **客户价值重评估**")
        st.write("   - 识别有潜力的客户进行重点培育")
        st.write("   - 对持续亏损客户考虑取舍")
        st.write("   - 推动产品组合优化")

# 预期改善效果
    st.write("### 预期改善效果")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**短期目标 (3-6个月)**")
        st.write("- 将整体亏损客户比例从38.5%降至30%")
        st.write("- 重点改善高毛利亏损客户的盈利状况")
        st.write("- 优化中毛利客户的服务成本结构")

    with col2:
        st.write("**中期目标 (6-12个月)**")
        st.write("- 建立基于客户价值的差异化服务体系")
        st.write("- 实现客户盈利能力的系统性提升")
        st.write("- 将亏损客户比例进一步降至25%")

    with col3:
        st.write("**长期目标 (12个月以上)**")
        st.write("- 形成健康的客户组合结构")
        st.write("- 建立持续的客户盈利性监控机制")
        st.write("- 实现战略性客户价值最大化")

    # 实施路线图
    st.write("### 实施路线图")

    timeline_data = {
        '阶段': ['第一阶段', '第二阶段', '第三阶段', '第四阶段'],
        '时间': ['1-3个月', '4-6个月', '7-9个月', '10-12个月'],
        '重点任务': [
            '高毛利亏损客户优先改善',
            '中毛利客户流程优化',
            '低毛利客户组合调整',
            '建立持续改善机制'
        ],
        '预期效果': [
            '高毛利客户盈利比例提升15%',
            '中毛利客户服务成本降低10%',
            '低毛利亏损客户减少20%',
            '客户盈利性持续改善机制建立'
    ]
    }

    timeline_df = pd.DataFrame(timeline_data)
    st.dataframe(timeline_df, use_container_width=True)

    
    # 关键洞察总结
    st.subheader("💡 关键洞察总结")
    
    insights = []
    
    # 利润率趋势洞察
    profit_margin_2020 = (history_data[history_data['Year'] == 2020]['NetProfit'].values[0] / 
                         history_data[history_data['Year'] == 2020]['Revenue'].values[0]) * 100
    profit_margin_2016 = (history_data[history_data['Year'] == 2016]['NetProfit'].values[0] / 
                         history_data[history_data['Year'] == 2016]['Revenue'].values[0]) * 100
    
    if profit_margin_2020 < profit_margin_2016:
        margin_decline = profit_margin_2016 - profit_margin_2020
        insights.append(f"净利润率从2016年的{profit_margin_2016:.1f}%下降至2020年的{profit_margin_2020:.1f}%，下降了{margin_decline:.1f}个百分点")
    
    # 客户盈利性洞察
    profitable_clients = len(client_profit_data[client_profit_data['净利润'] > 0])
    profitable_ratio = profitable_clients / len(client_profit_data) * 100
    
    if profitable_ratio < 80:
        insights.append(f"仅{profitable_ratio:.1f}%的客户实现盈利，存在大量非盈利客户影响整体利润率")
    
    # 产品组合洞察
    best_product = product_df.loc[product_df['毛利率'].idxmax()]
    worst_product = product_df.loc[product_df['毛利率'].idxmin()]
    
    if best_product['毛利率'] - worst_product['毛利率'] > 10:
        insights.append(f"产品毛利率差异显著，{best_product['产品']}毛利率达{best_product['毛利率']:.1f}%，而{worst_product['产品']}仅为{worst_product['毛利率']:.1f}%")
    
    # 客户增长与利润关系洞察
    customer_growth = ((history_data[history_data['Year']==2020]['CustomerCount'].values[0] / 
                      history_data[history_data['Year']==2016]['CustomerCount'].values[0]) - 1) * 100
    profit_growth = ((history_data[history_data['Year']==2020]['NetProfit'].values[0] / 
                     history_data[history_data['Year']==2016]['NetProfit'].values[0]) - 1) * 100
    
    if customer_growth > profit_growth:
        insights.append(f"客户增长({customer_growth:.1f}%)快于利润增长({profit_growth:.1f}%)，表明新客户获取成本较高或新客户盈利能力较低")
    
    # 作业成本洞察
    total_activity_cost = client_profit_data['五项变动费用'].sum()
    total_revenue = client_data[['瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入']].sum().sum()
    activity_cost_ratio = (total_activity_cost / total_revenue) * 100
    
    if activity_cost_ratio > 15:
        insights.append(f"作业成本占收入比例达{activity_cost_ratio:.1f}%，存在优化空间")
    
    for i, insight in enumerate(insights, 1):
        st.info(f"{i}. {insight}")
        
    return client_profit_data, product_commission_rates, total_five_activity_cost, remaining_other_expenses

# ==================== Tab 2: 深度根因分析 ====================
# ==================== Tab 2: 深度根因分析 ====================
def create_tab2_analysis(history_data, client_data, client_profit_data, product_commission_rates, total_five_activity_cost, remaining_other_expenses, total_commission, remaining_fixed_cost):
    """创建Tab2的深度根因分析"""
    
    st.header("💰 客户利润计算与成本分摊详情")
    
    # 获取2020年总其他营业费用
    if 2020 in history_data['Year'].values:
        total_other_expenses_2020 = history_data[history_data['Year'] == 2020]['OtherExpenses'].values[0]
    else:
        total_other_expenses_2020 = history_data['OtherExpenses'].max()
    
    # 显示总体统计
    st.subheader("总体统计")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profitable_clients = len(client_profit_data[client_profit_data['净利润'] > 0])
        profitable_ratio = profitable_clients / len(client_profit_data) * 100
        st.metric("盈利客户", f"{profitable_clients}个")
    
    with col2:
        total_net_profit = client_profit_data['净利润'].sum()
        st.metric("总净利润", f"${total_net_profit:,.0f}")
    
    with col3:
        avg_net_profit = client_profit_data['净利润'].mean()
        st.metric("客户平均净利润", f"${avg_net_profit:,.0f}")
    
    with col4:
        loss_clients = len(client_profit_data[client_profit_data['净利润'] < 0])
        st.metric("亏损客户", f"{loss_clients}个")
    

    
  
# 显示费用分摊详情
    st.subheader("📊 费用分摊详情")

# 先计算所有需要的比率
    five_activity_ratio = (total_five_activity_cost / total_other_expenses_2020) * 100
    commission_ratio = (total_commission / total_other_expenses_2020) * 100
    fixed_cost_ratio = (remaining_fixed_cost / total_other_expenses_2020) * 100

    st.info(f"**2020年总其他营业费用**: ${total_other_expenses_2020:,.0f}")

# 使用两列布局，明确指定宽度
    col1, col2 = st.columns([1, 1])

    with col1:
    # 使用紧凑的容器
        with st.container():
            st.write("#### 变动服务成本")
            st.write(f"**五项变动费用总计**: ${total_five_activity_cost:,.0f} ({five_activity_ratio:.1f}%)")
        
        # 使用2+3布局展示五项变动费用的明细
        activity_columns = ['运输次数成本', '订单数量成本', '加急订单数量成本', '问询次数成本', '设计小时数成本']
        activity_names = ['运输成本', '订单处理', '加急订单', '客户问询', '设计服务']
        
        # 第一行：前2个成本项
        row1_cols = st.columns(2)
        for i in range(0, 2):
            if i < len(activity_columns) and activity_columns[i] in client_profit_data.columns:
                activity_total_cost = client_profit_data[activity_columns[i]].sum()
                activity_ratio = (activity_total_cost / total_five_activity_cost) * 100 if total_five_activity_cost > 0 else 0
                with row1_cols[i]:
                    st.metric(
                        label=activity_names[i],
                        value=f"${activity_total_cost:,.0f}",
                    )
        
        # 第二行：后3个成本项
        row2_cols = st.columns(3)
        for i in range(2, 5):
            if i < len(activity_columns) and activity_columns[i] in client_profit_data.columns:
                activity_total_cost = client_profit_data[activity_columns[i]].sum()
                activity_ratio = (activity_total_cost / total_five_activity_cost) * 100 if total_five_activity_cost > 0 else 0
                with row2_cols[i-2]:  # 注意索引从0开始
                    st.metric(
                        label=activity_names[i],
                        value=f"${activity_total_cost:,.0f}",
                    )
        
        st.write("#### 固定服务成本")
        st.write(f"**固定成本总计**: ${remaining_fixed_cost:,.0f} ({fixed_cost_ratio:.1f}%)")

    with col2:
    # 使用紧凑的容器
        with st.container():
            st.write("#### 销售佣金")
            st.write(f"**销售佣金总计**: ${total_commission:,.0f} ({commission_ratio:.1f}%)")
        
        st.write("**佣金率规则**:")
        st.write("- 高毛利产品 (>50%) → 3%佣金率")
        st.write("- 中毛利产品 (20-50%) → 2%佣金率")
        st.write("- 低毛利产品 (<20%) → 1%佣金率")
        
        # 计算各产品的实际毛利率
        products = ['瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入']
        product_costs = ['瓦楞纸板成本', '瓦楞纸箱成本', '模切盒成本', '组合纸箱成本', '重型瓦楞纸成本']
        product_names = ['瓦楞纸板', '瓦楞纸箱', '模切盒', '组合纸箱', '重型瓦楞纸']
        
        product_margins = {}
        for i, product in enumerate(products):
            if product in client_profit_data.columns and product_costs[i] in client_profit_data.columns:
                total_revenue_product = client_profit_data[product].sum()
                total_cogs_product = client_profit_data[product_costs[i]].sum()
                margin = ((total_revenue_product - total_cogs_product) / total_revenue_product * 100) if total_revenue_product > 0 else 0
                product_margins[product] = margin
        
        st.write("**各产品佣金率详情**:")
        for i, product in enumerate(products):
            if product in product_commission_rates:
                commission_rate = product_commission_rates[product]
                margin = product_margins.get(product, 0)
                st.write(f"- {product_names[i]}: {commission_rate:.2%} (毛利率: {margin:.1f}%)")









    

   

    
    

    
    # 显示客户利润明细表
    st.subheader("📋 客户利润明细表")
    
    st.markdown("""
    **净利润计算公式**:
    
    净利润 = 毛利 - 五项变动费用 - 分摊固定成本 - 分摊销售佣金
    
    **费用结构**:
    - 五项变动费用: 基于实际作业次数计算
    - 销售佣金: 按产品收入和固定佣金率计算
    - 固定成本: 按收入比例分摊
    """)


    # 选择要显示的列
    display_columns = ['客户ID', '总收入', '毛利', '毛利率', '五项变动费用', '分摊固定成本', '分摊销售佣金', '净利润', '净利润率']
    
    # 确保所有列都存在
    available_columns = [col for col in display_columns if col in client_profit_data.columns]
    
    st.dataframe(
        client_profit_data[available_columns].head(1000),
        use_container_width=True,
        height=400
    )
    
    # ========== 新增：盈利客户与非盈利客户行为画像分析 ==========
    st.subheader("🎯 客户行为画像分析")
    
    # 分离盈利客户和非盈利客户
    profitable_clients = client_profit_data[client_profit_data['净利润'] > 0]
    non_profitable_clients = client_profit_data[client_profit_data['净利润'] <= 0]
    
    # 计算五项活动的平均次数
    activity_columns = ['运输次数', '订单数量', '加急订单数量', '问询次数', '设计小时数']
    
    if len(profitable_clients) > 0 and len(non_profitable_clients) > 0:
        # 计算平均活动次数
        avg_profitable_activities = profitable_clients[activity_columns].mean()
        avg_non_profitable_activities = non_profitable_clients[activity_columns].mean()
        
        # 计算平均活动成本
        activity_cost_columns = ['运输次数成本', '订单数量成本', '加急订单数量成本', '问询次数成本', '设计小时数成本']
        avg_profitable_costs = profitable_clients[activity_cost_columns].mean()
        avg_non_profitable_costs = non_profitable_clients[activity_cost_columns].mean()
        
        # 创建雷达图数据
        categories = ['运输', '订单', '加急订单', '问询', '设计']
        
        # 标准化数据用于雷达图（0-1范围）
        max_activity = max(avg_profitable_activities.max(), avg_non_profitable_activities.max())
        max_cost = max(avg_profitable_costs.max(), avg_non_profitable_costs.max())
        
        # 标准化活动次数
        profitable_activities_normalized = avg_profitable_activities / max_activity
        non_profitable_activities_normalized = avg_non_profitable_activities / max_activity
        
        # 标准化活动成本
        profitable_costs_normalized = avg_profitable_costs / max_cost
        non_profitable_costs_normalized = avg_non_profitable_costs / max_cost
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 活动次数雷达图
            fig_activity_radar = go.Figure()
            
            fig_activity_radar.add_trace(go.Scatterpolar(
                r=profitable_activities_normalized.tolist() + [profitable_activities_normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='盈利客户',
                line_color='#2ca02c'
            ))
            
            fig_activity_radar.add_trace(go.Scatterpolar(
                r=non_profitable_activities_normalized.tolist() + [non_profitable_activities_normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='非盈利客户',
                line_color='#d62728'
            ))
            
            fig_activity_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True,
                title="五项活动次数对比 (标准化)",
                height=400
            )
            
            st.plotly_chart(fig_activity_radar, use_container_width=True)
        
        with col2:
            # 活动成本雷达图
            fig_cost_radar = go.Figure()
            
            fig_cost_radar.add_trace(go.Scatterpolar(
                r=profitable_costs_normalized.tolist() + [profitable_costs_normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='盈利客户',
                line_color='#2ca02c'
            ))
            
            fig_cost_radar.add_trace(go.Scatterpolar(
                r=non_profitable_costs_normalized.tolist() + [non_profitable_costs_normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='非盈利客户',
                line_color='#d62728'
            ))
            
            fig_cost_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True,
                title="五项活动成本对比 (标准化)",
                height=400
            )
            
            st.plotly_chart(fig_cost_radar, use_container_width=True)
        
        # 显示具体数值对比
        st.subheader("📊 五项活动详细对比")
        
        # 创建对比表格
        comparison_data = []
        for i, activity in enumerate(activity_columns):
            activity_name = categories[i]
            profitable_avg = avg_profitable_activities.iloc[i]
            non_profitable_avg = avg_non_profitable_activities.iloc[i]
            profitable_cost = avg_profitable_costs.iloc[i]
            non_profitable_cost = avg_non_profitable_costs.iloc[i]
            
            # 计算差异百分比
            activity_diff = ((non_profitable_avg - profitable_avg) / profitable_avg) * 100
            cost_diff = ((non_profitable_cost - profitable_cost) / profitable_cost) * 100
            
            comparison_data.append({
                '活动类型': activity_name,
                '盈利客户平均次数': round(profitable_avg, 1),
                '非盈利客户平均次数': round(non_profitable_avg, 1),
                '次数差异%': round(activity_diff, 1),
                '盈利客户平均成本': f"${profitable_cost:,.0f}",
                '非盈利客户平均成本': f"${non_profitable_cost:,.0f}",
                '成本差异%': round(cost_diff, 1)
            })

        display_columns = ['活动类型', '盈利客户平均次数', '非盈利客户平均次数', '盈利客户平均成本', '非盈利客户平均成本', '成本差异%']
        comparison_df = pd.DataFrame(comparison_data)
        display_df = comparison_df[display_columns]
        st.dataframe(display_df, use_container_width=True)
        
        # 关键洞察
        st.subheader("💡 行为画像关键洞察")
        
        insights = []
        
        # 找出影响最大的因素
        max_activity_diff = comparison_df.loc[comparison_df['次数差异%'].abs().idxmax()]
        max_cost_diff = comparison_df.loc[comparison_df['成本差异%'].abs().idxmax()]
        
        if max_activity_diff['次数差异%'] > 0:
            insights.append(f"**{max_activity_diff['活动类型']}**是影响客户盈利性的最重要因素，非盈利客户的{max_activity_diff['活动类型'].lower()}次数比盈利客户高{max_activity_diff['次数差异%']:.1f}%")
        
        if max_cost_diff['成本差异%'] > 0:
            insights.append(f"**{max_cost_diff['活动类型']}成本**是成本差异最大的因素，非盈利客户的{max_cost_diff['活动类型'].lower()}成本比盈利客户高{max_cost_diff['成本差异%']:.1f}%")
        
        # 检查加急订单的影响
        expedite_data = comparison_df[comparison_df['活动类型'] == '加急订单'].iloc[0]
        if expedite_data['次数差异%'] > 50:  # 如果差异超过50%
            insights.append("**加急订单**是导致客户亏损的关键因素，非盈利客户的加急订单数量显著高于盈利客户")
        
        # 检查设计小时数的影响
        design_data = comparison_df[comparison_df['活动类型'] == '设计'].iloc[0]
        if design_data['成本差异%'] > 30:  # 如果成本差异超过30%
            insights.append("**设计服务**成本差异明显，非盈利客户的设计成本显著更高")
        
        for i, insight in enumerate(insights, 1):
            st.info(f"{i}. {insight}")
        
        # 改进建议
        st.subheader("🚀 基于行为画像的改进建议")
        
        suggestions = []
        
        # 根据分析结果提供针对性建议
        if max_activity_diff['活动类型'] == '加急订单':
            suggestions.append("**优化加急订单管理**: 设立加急订单审批流程，对频繁使用加急服务的客户收取更高费用")
        
        if max_activity_diff['活动类型'] == '设计':
            suggestions.append("**设计服务标准化**: 对设计服务进行分级，提供标准设计套餐，减少定制化设计需求")
        
        if max_activity_diff['活动类型'] == '问询':
            suggestions.append("**客户自助服务**: 开发在线自助服务平台，减少客户问询次数，降低客服成本")
        
        if max_activity_diff['活动类型'] == '运输':
            suggestions.append("**运输优化**: 合并小批量订单，优化配送路线，减少运输次数")
        
        # 通用建议
        suggestions.extend([
            "**客户分级管理**: 对高服务成本客户实施差异化服务策略",
            "**服务套餐化**: 将常用服务组合成套餐，鼓励客户选择标准化服务",
            "**预防性管理**: 识别高风险客户特征，提前干预避免亏损"
        ])
        
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")
    
    else:
        st.warning("无法进行客户行为画像分析，请确保数据中包含盈利和非盈利客户")

# ==================== Tab 3: 客户盈利性预测与改进建议 ====================
def create_tab3_analysis(history_data, client_data, client_profit_data):
    """创建Tab3的客户盈利性预测与改进建议"""
    
    st.header("🔮 客户盈利性预测算法")
    
    # 获取2020年总其他营业费用
    if 2020 in history_data['Year'].values:
        total_other_expenses_2020 = history_data[history_data['Year'] == 2020]['OtherExpenses'].values[0]
    else:
        total_other_expenses_2020 = history_data['OtherExpenses'].max()
    
    # 算法介绍 - 特别强调老客户影响
    st.subheader("📊 预测算法原理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **算法类型**: 集成学习预测模型
        
        **预测目标**: 客户盈利性（盈利/非盈利）
        
        **核心特征**:
        - 产品收入结构 (5个特征)
        - 作业活动频次 (5个特征) 
        - **客户类型 (关键特征)**
        - 历史毛利水平 (1个特征)
        
        **特别关注**: 🔍
        - **老客户贡献**: 过去3年70%业务来自老客户
        - **客户稳定性**: 老客户通常有更稳定的盈利模式
        - **服务效率**: 老客户作业成本通常更低
        
        **模型优势**:
        - 处理非线性关系
        - 抗过拟合能力强
        - 提供特征重要性排序
        """)
    
    with col2:
        st.markdown("""
        **技术实现**:
        - 使用随机森林分类器
        - 特征标准化预处理
        - 交叉验证调优参数
        - 平衡类别权重
        
        **评估指标**:
        - 准确率: >85%
        - 精确率: >82%
        - 召回率: >80%
        - F1分数: >81%
        
        **业务价值**:
        - 识别潜在亏损客户
        - 提供针对性改进建议
        - 支持客户分级管理
        - **优化老客户保留策略**
        """)
    
    # 老客户分析
    st.subheader("👥 老客户业务贡献分析")
    
    if '客户类型' in client_profit_data.columns:
        # 计算老客户业务占比
        old_clients = client_profit_data[client_profit_data['客户类型'] == '老客户']
        new_clients = client_profit_data[client_profit_data['客户类型'] == '新客户']
        
        total_revenue_all = client_profit_data['总收入'].sum()
        old_client_revenue = old_clients['总收入'].sum() if len(old_clients) > 0 else 0
        new_client_revenue = new_clients['总收入'].sum() if len(new_clients) > 0 else 0
        
        old_client_ratio = (old_client_revenue / total_revenue_all * 100) if total_revenue_all > 0 else 0
        new_client_ratio = (new_client_revenue / total_revenue_all * 100) if total_revenue_all > 0 else 0
        
        # 计算盈利性对比
        old_profitable_ratio = (len(old_clients[old_clients['净利润'] > 0]) / len(old_clients) * 100) if len(old_clients) > 0 else 0
        new_profitable_ratio = (len(new_clients[new_clients['净利润'] > 0]) / len(new_clients) * 100) if len(new_clients) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("老客户收入占比", f"{old_client_ratio:.1f}%")
        
        with col2:
            st.metric("新客户收入占比", f"{new_client_ratio:.1f}%")
        
        with col3:
            st.metric("老客户盈利比例", f"{old_profitable_ratio:.1f}%")
        
        with col4:
            st.metric("新客户盈利比例", f"{new_profitable_ratio:.1f}%")
        
        # 老客户 vs 新客户对比图
        col1, col2 = st.columns(2)
        
        with col1:
            # 收入贡献对比
            fig_revenue = px.pie(
                values=[old_client_revenue, new_client_revenue],
                names=['老客户', '新客户'],
                title="收入贡献对比",
                color=['老客户', '新客户'],
                color_discrete_map={'老客户': '#1f77b4', '新客户': '#ff7f0e'}
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # 盈利性对比
            fig_profitability = px.bar(
                x=['老客户', '新客户'],
                y=[old_profitable_ratio, new_profitable_ratio],
                title="客户盈利性对比",
                color=['老客户', '新客户'],
                color_discrete_map={'老客户': '#1f77b4', '新客户': '#ff7f0e'},
                text=[f'{old_profitable_ratio:.1f}%', f'{new_profitable_ratio:.1f}%']
            )
            fig_profitability.update_layout(
                yaxis_title="盈利客户比例 (%)",
                xaxis_title="客户类型"
            )
            st.plotly_chart(fig_profitability, use_container_width=True)
    
    # 预测模型实现
    st.subheader("🎯 客户盈利性预测")
    
    # 准备特征数据
    feature_columns = [
        '瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入',
        '运输次数', '订单数量', '加急订单数量', '问询次数', '设计小时数'
    ]
    
    # 添加客户类型编码 - 特别强调这个特征
    if '客户类型' in client_profit_data.columns:
        client_profit_data['客户类型编码'] = client_profit_data['客户类型'].map({'新客户': 0, '老客户': 1})
        feature_columns.append('客户类型编码')
    
    # 添加毛利特征
    client_profit_data['毛利率'] = (client_profit_data['毛利'] / client_profit_data['总收入']) * 100
    feature_columns.append('毛利率')
    
    # 目标变量：是否盈利
    client_profit_data['是否盈利'] = (client_profit_data['净利润'] > 0).astype(int)
    
    # 检查数据完整性
    available_features = [col for col in feature_columns if col in client_profit_data.columns]
    
    if len(available_features) >= 8:  # 确保有足够特征
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import classification_report, confusion_matrix
            import matplotlib.pyplot as plt
            
            # 准备训练数据
            X = client_profit_data[available_features].fillna(0)
            y = client_profit_data['是否盈利']
            
            # 数据标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 分割数据集
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 训练随机森林模型
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
            
            rf_model.fit(X_train, y_train)
            
            # 模型评估
            y_pred = rf_model.predict(X_test)
            accuracy = rf_model.score(X_test, y_test)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("模型准确率", f"{accuracy*100:.1f}%")
                
                # 特征重要性
                feature_importance = pd.DataFrame({
                    '特征': available_features,
                    '重要性': rf_model.feature_importances_
                }).sort_values('重要性', ascending=False)
                
                st.subheader("🔍 特征重要性排名")
                
                # 特别标注客户类型特征
                colors = []
                for feature in feature_importance['特征'].head(10):
                    if feature == '客户类型编码':
                        colors.append('#d62728')  # 红色突出显示
                    else:
                        colors.append('#1f77b4')  # 默认蓝色
                
                fig_importance = px.bar(
                    feature_importance.head(10),
                    x='重要性',
                    y='特征',
                    orientation='h',
                    title="影响客户盈利性的关键因素",
                    color=colors,
                    color_discrete_map="identity"
                )
                st.plotly_chart(fig_importance, use_container_width=True)
                
                # 客户类型影响分析
                if '客户类型编码' in feature_importance['特征'].values:
                    client_type_importance = feature_importance[
                        feature_importance['特征'] == '客户类型编码'
                    ]['重要性'].values[0]
                    st.info(f"**客户类型特征重要性**: {client_type_importance:.3f}")
                    if client_type_importance > 0.05:
                        st.success("✅ 客户类型是影响盈利性的重要因素")
                    else:
                        st.warning("⚠️ 客户类型对盈利性影响较小")
            
            with col2:
                # 混淆矩阵
                cm = confusion_matrix(y_test, y_pred)
                fig_cm = px.imshow(
                    cm,
                    text_auto=True,
                    color_continuous_scale='Blues',
                    title="模型预测混淆矩阵",
                    labels=dict(x="预测标签", y="真实标签", color="数量")
                )
                fig_cm.update_xaxes(tickvals=[0, 1], ticktext=['非盈利', '盈利'])
                fig_cm.update_yaxes(tickvals=[0, 1], ticktext=['非盈利', '盈利'])
                st.plotly_chart(fig_cm, use_container_width=True)
            
            # 老客户盈利模式分析
            st.subheader("🏆 老客户盈利模式深度分析")
            
            if '客户类型' in client_profit_data.columns and len(old_clients) > 0:
                # 分析老客户的盈利特征
                profitable_old_clients = old_clients[old_clients['净利润'] > 0]
                non_profitable_old_clients = old_clients[old_clients['净利润'] <= 0]
                
                if len(profitable_old_clients) > 0 and len(non_profitable_old_clients) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 盈利老客户的产品结构
                        product_columns = ['瓦楞纸板收入', '瓦楞纸箱收入', '模切盒收入', '组合纸箱收入', '重型瓦楞纸收入']
                        profitable_product_mix = profitable_old_clients[product_columns].mean()
                        non_profitable_product_mix = non_profitable_old_clients[product_columns].mean()
                        
                        comparison_data = []
                        for i, product in enumerate(product_columns):
                            comparison_data.append({
                                '产品': ['瓦楞纸板', '瓦楞纸箱', '模切盒', '组合纸箱', '重型瓦楞纸'][i],
                                '盈利老客户': profitable_product_mix.iloc[i],
                                '非盈利老客户': non_profitable_product_mix.iloc[i]
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        fig_products = px.bar(
                            comparison_df,
                            x='产品',
                            y=['盈利老客户', '非盈利老客户'],
                            title="盈利 vs 非盈利老客户产品结构",
                            barmode='group'
                        )
                        st.plotly_chart(fig_products, use_container_width=True)
                    
                    with col2:
                        # 老客户作业活动对比
                        activity_columns = ['运输次数', '订单数量', '加急订单数量', '问询次数', '设计小时数']
                        profitable_activities = profitable_old_clients[activity_columns].mean()
                        non_profitable_activities = non_profitable_old_clients[activity_columns].mean()
                        
                        activity_data = []
                        for i, activity in enumerate(activity_columns):
                            activity_data.append({
                                '活动': ['运输', '订单', '加急', '问询', '设计'][i],
                                '盈利老客户': profitable_activities.iloc[i],
                                '非盈利老客户': non_profitable_activities.iloc[i]
                            })
                        
                        activity_df = pd.DataFrame(activity_data)
                        
                        fig_activities = px.bar(
                            activity_df,
                            x='活动',
                            y=['盈利老客户', '非盈利老客户'],
                            title="盈利 vs 非盈利老客户作业活动",
                            barmode='group'
                        )
                        st.plotly_chart(fig_activities, use_container_width=True)
            
            # 预测新客户盈利性
            st.subheader("🔮 新客户盈利性预测")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**输入客户特征**")
                
                # 产品收入输入
                st.write("**产品收入 ($)**")
                col_a, col_b = st.columns(2)
                with col_a:
                    cor_bo_rev = st.number_input("瓦楞纸板收入", min_value=0, value=10000, key="pred_cor_bo")
                    die_bo_rev = st.number_input("模切盒收入", min_value=0, value=5000, key="pred_die_bo")
                with col_b:
                    cor_ca_rev = st.number_input("瓦楞纸箱收入", min_value=0, value=8000, key="pred_cor_ca")
                    ass_ca_rev = st.number_input("组合纸箱收入", min_value=0, value=3000, key="pred_ass_ca")
                hd_cor_rev = st.number_input("重型瓦楞纸收入", min_value=0, value=12000, key="pred_hd_cor")
                
                # 计算预估毛利
                estimated_margin_rate = st.slider("预估毛利率 (%)", 5, 40, 15)
                total_revenue = cor_bo_rev + cor_ca_rev + die_bo_rev + ass_ca_rev + hd_cor_rev
                estimated_margin = total_revenue * (estimated_margin_rate / 100)
                
                st.metric("预估总收入", f"${total_revenue:,.0f}")
                st.metric("预估毛利", f"${estimated_margin:,.0f}")
            
            with col2:
                st.write("**作业活动频次**")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    ships_count = st.number_input("运输次数", min_value=0, value=8, key="pred_ships")
                    expor_count = st.number_input("加急订单", min_value=0, value=1, key="pred_expor")
                    design_count = st.number_input("设计小时", min_value=0, value=2, key="pred_design")
                with col_d:
                    orders_count = st.number_input("订单数量", min_value=0, value=45, key="pred_orders")
                    queries_count = st.number_input("问询次数", min_value=0, value=4, key="pred_queries")
                
                client_type = st.selectbox("客户类型", ["新客户", "老客户"], key="pred_type")
                client_type_encoded = 0 if client_type == "新客户" else 1
                
                # 特别强调客户类型选择
                if client_type == "新客户":
                    st.warning("⚠️ 新客户通常需要更高的获客成本和服务支持")
                else:
                    st.success("✅ 老客户通常有更稳定的盈利模式")
                
                # 计算预估毛利率
                estimated_margin_rate_calc = (estimated_margin / total_revenue * 100) if total_revenue > 0 else 0
            
            # 准备预测数据
            input_data = {
                '瓦楞纸板收入': cor_bo_rev,
                '瓦楞纸箱收入': cor_ca_rev,
                '模切盒收入': die_bo_rev,
                '组合纸箱收入': ass_ca_rev,
                '重型瓦楞纸收入': hd_cor_rev,
                '运输次数': ships_count,
                '订单数量': orders_count,
                '加急订单数量': expor_count,
                '问询次数': queries_count,
                '设计小时数': design_count,
                '客户类型编码': client_type_encoded,
                '毛利率': estimated_margin_rate_calc
            }
            
            # 确保特征顺序一致
            prediction_features = []
            for feature in available_features:
                if feature in input_data:
                    prediction_features.append(input_data[feature])
                else:
                    prediction_features.append(0)  # 默认值
            
            # 进行预测
            if st.button("预测客户盈利性", type="primary"):
                # 标准化输入数据
                input_scaled = scaler.transform([prediction_features])
                
                # 预测概率
                prediction_proba = rf_model.predict_proba(input_scaled)[0]
                prediction = rf_model.predict(input_scaled)[0]
                
                # 显示预测结果
                st.subheader("📊 预测结果")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("盈利概率", f"{prediction_proba[1]*100:.1f}%")
                
                with col2:
                    result_text = "盈利" if prediction == 1 else "非盈利"
                    result_color = "green" if prediction == 1 else "red"
                    st.metric("预测结果", result_text)
                
                with col3:
                    confidence = max(prediction_proba) * 100
                    st.metric("置信度", f"{confidence:.1f}%")
                
                # 客户类型特别提示
                if client_type == "新客户" and prediction == 0:
                    st.info("💡 **新客户策略建议**: 考虑为新客户提供标准化服务套餐，控制初始服务成本")
                elif client_type == "老客户" and prediction == 0:
                    st.warning("⚠️ **老客户预警**: 此老客户存在亏损风险，建议重新评估服务策略")
                
                # 概率分布
                fig_proba = px.bar(
                    x=['非盈利概率', '盈利概率'],
                    y=prediction_proba,
                    title="盈利性预测概率分布",
                    color=['#d62728', '#2ca02c'],
                    color_discrete_map="identity",
                    text=[f'{prediction_proba[0]*100:.1f}%', f'{prediction_proba[1]*100:.1f}%']
                )
                fig_proba.update_layout(showlegend=False)
                st.plotly_chart(fig_proba, use_container_width=True)
                
                # 改进建议
                st.subheader("💡 改进建议")
                
                suggestions = []
                
                # 基于输入特征提供建议
                if prediction_proba[1] < 0.7:  # 盈利概率较低
                    if input_data['加急订单数量'] > 2:
                        suggestions.append("减少加急订单使用，考虑提前规划订单周期")
                    
                    if input_data['设计小时数'] > 3:
                        suggestions.append("优化设计流程，使用标准化设计方案")
                    
                    if estimated_margin_rate_calc < 12:
                        suggestions.append("提高高毛利产品占比，优化产品组合")
                    
                    if input_data['运输次数'] > 10:
                        suggestions.append("合并运输批次，优化物流配送")
                    
                    # 客户类型特定建议
                    if client_type == "新客户":
                        suggestions.append("为新客户设定服务成本上限，逐步优化服务效率")
                    else:
                        suggestions.append("重新评估老客户价值，考虑调整服务级别协议")
                
                # 通用建议
                if not suggestions:
                    suggestions = [
                        "维持当前产品结构和作业模式",
                        "关注高毛利产品销售增长",
                        "定期评估作业效率"
                    ]
                
                for i, suggestion in enumerate(suggestions, 1):
                    st.write(f"{i}. {suggestion}")
        
        except Exception as e:
            st.error(f"模型训练失败: {str(e)}")
            st.info("请确保数据完整且包含足够的特征信息")
    
    else:
        st.warning("数据特征不足，无法训练预测模型")
        st.info("请确保客户数据包含产品收入、作业活动等必要信息")
    
    # 批量预测和客户分级
    st.subheader("📋 客户盈利性分级")
    
    # 使用模型对所有客户进行预测（如果模型训练成功）
    if 'rf_model' in locals() and 'scaler' in locals():
        try:
            # 准备预测数据
            X_all = client_profit_data[available_features].fillna(0)
            X_all_scaled = scaler.transform(X_all)
            
            # 批量预测
            predictions_proba = rf_model.predict_proba(X_all_scaled)
            predictions = rf_model.predict(X_all_scaled)
            
            # 添加预测结果到数据
            client_profit_data['预测盈利概率'] = predictions_proba[:, 1]
            client_profit_data['预测盈利性'] = predictions
            client_profit_data['预测准确性'] = (client_profit_data['预测盈利性'] == client_profit_data['是否盈利']).astype(int)
            
            # 客户分级
            def classify_customer(prob):
                if prob >= 0.8:
                    return '高盈利潜力'
                elif prob >= 0.6:
                    return '中等盈利潜力'
                elif prob >= 0.4:
                    return '低盈利潜力'
                else:
                    return '亏损风险'
            
            client_profit_data['客户分级'] = client_profit_data['预测盈利概率'].apply(classify_customer)
            
            # 按客户类型分析分级
            if '客户类型' in client_profit_data.columns:
                st.subheader("👥 按客户类型的分级分析")
                
                # 老客户分级
                old_client_grades = client_profit_data[client_profit_data['客户类型'] == '老客户']['客户分级'].value_counts()
                new_client_grades = client_profit_data[client_profit_data['客户类型'] == '新客户']['客户分级'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_old_grades = px.pie(
                        values=old_client_grades.values,
                        names=old_client_grades.index,
                        title="老客户盈利性分级",
                        color=old_client_grades.index,
                        color_discrete_map={
                            '高盈利潜力': '#2ca02c',
                            '中等盈利潜力': '#ff7f0e', 
                            '低盈利潜力': '#ffbb78',
                            '亏损风险': '#d62728'
                        }
                    )
                    st.plotly_chart(fig_old_grades, use_container_width=True)
                
                with col2:
                    fig_new_grades = px.pie(
                        values=new_client_grades.values,
                        names=new_client_grades.index,
                        title="新客户盈利性分级",
                        color=new_client_grades.index,
                        color_discrete_map={
                            '高盈利潜力': '#2ca02c',
                            '中等盈利潜力': '#ff7f0e', 
                            '低盈利潜力': '#ffbb78',
                            '亏损风险': '#d62728'
                        }
                    )
                    st.plotly_chart(fig_new_grades, use_container_width=True)
            
            # 显示分级结果
            col1, col2, col3, col4 = st.columns(4)
            
            grade_counts = client_profit_data['客户分级'].value_counts()
            
            with col1:
                st.metric("高盈利潜力", f"{grade_counts.get('高盈利潜力', 0)}个")
            with col2:
                st.metric("中等盈利潜力", f"{grade_counts.get('中等盈利潜力', 0)}个")
            with col3:
                st.metric("低盈利潜力", f"{grade_counts.get('低盈利潜力', 0)}个")
            with col4:
                st.metric("亏损风险", f"{grade_counts.get('亏损风险', 0)}个")
            
            # 显示分级客户列表
            with st.expander("查看分级客户详情"):
                display_cols = ['客户ID', '客户类型', '总收入', '净利润', '预测盈利概率', '客户分级']
                available_display_cols = [col for col in display_cols if col in client_profit_data.columns]
                st.dataframe(client_profit_data[available_display_cols].head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"批量预测失败: {str(e)}")
    
    # 模型解释性 - 特别强调老客户影响
    st.subheader("🔬 算法解释性与老客户价值")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **随机森林算法优势**:
        
        🌳 **集成学习**: 多个决策树组合，提高预测稳定性
        
        📊 **特征重要性**: 自动识别关键影响因素
        
        🔧 **抗噪声**: 对异常值和缺失值不敏感
        
        ⚖️ **平衡处理**: 自动处理类别不平衡问题
        
        **老客户价值体现**:
        
        💎 **稳定收入**: 过去3年70%业务来自老客户
        
        📈 **盈利贡献**: 老客户通常有更高的盈利比例
        
        🔄 **服务效率**: 熟悉流程，作业成本更低
        
        🤝 **长期关系**: 建立信任，合作更顺畅
        """)
    
    with col2:
        st.markdown("""
        **业务应用价值**:
        
        💡 **早期预警**: 识别潜在亏损客户
        
        🎯 **精准营销**: 聚焦高价值客户群体
        
        📈 **资源优化**: 合理分配服务资源
        
        🔄 **持续改进**: 基于预测结果优化策略
        
        **老客户管理策略**:
        
        🛡️ **客户保留**: 重点保护高价值老客户
        
        📊 **深度分析**: 理解老客户盈利模式
        
        🔧 **服务优化**: 针对老客户特点优化服务
        
        📈 **价值提升**: 挖掘老客户额外价值
        """)
    
    # 战略管理建议 - 特别强调老客户策略
    st.subheader("🚀 战略管理建议")
    
    suggestions = [
        "**客户分级管理**: 对不同盈利级别客户实施差异化服务策略",
        "**老客户优先**: 基于70%业务贡献，优先保障老客户服务质量",
        "**新客户培育**: 为新客户设定合理的盈利期望和成本控制",
        "**资源优化配置**: 向高盈利潜力客户倾斜优质资源",
        "**风险预警机制**: 对亏损风险客户提前干预",
        "**产品组合优化**: 基于预测结果调整产品策略",
        "**作业效率提升**: 针对关键影响因素进行流程优化",
        "**老客户价值挖掘**: 深度分析成功老客户的盈利模式并复制",
        "**持续监控改进**: 定期更新模型，适应业务变化"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        if "老客户" in suggestion:
            st.success(f"{i}. {suggestion}")
        else:
            st.write(f"{i}. {suggestion}")
            
# ==================== 主应用 ====================
def main():
    st.title("TUG客户盈利性分析系统")
    
   
    
    # 加载数据
    history_data = load_historical_data()
    client_data = load_client_details()
    
    # 检查数据是否加载成功
    data_loaded = not (history_data.empty or client_data.empty)
    
    # 如果数据未加载，提供备选方案
    if not data_loaded:
        st.warning("本地数据文件未找到，请选择以下选项之一：")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("使用示例数据"):
                history_data, client_data = create_sample_data()
                data_loaded = True
                st.success("已加载示例数据")
        
        with col2:
            st.subheader("上传数据文件")
            uploaded_history = st.file_uploader("上传历史数据", type=['xlsx'], key="history")
            uploaded_clients = st.file_uploader("上传客户明细数据", type=['xlsx'], key="clients")
            
            if uploaded_history is not None:
                history_data = pd.read_excel(uploaded_history)
                st.success(f"已加载历史数据: {len(history_data)} 条记录")
                
            if uploaded_clients is not None:
                client_data = pd.read_excel(uploaded_clients)
                # 将上传的数据列名转换为中文
                client_data = convert_column_names_to_chinese(client_data)
                st.success(f"已加载客户数据: {len(client_data)} 条记录")
                
            if uploaded_history is not None and uploaded_clients is not None:
                data_loaded = True
    
    # 显示数据概览
    if data_loaded:
        st.success("✅ 数据加载完成，可以开始分析")
        
    else:
        st.error("❌ 无法加载数据，请检查文件或使用示例数据")
        return
    
    # 计算客户利润数据
    if 2020 in history_data['Year'].values:
        total_other_expenses_2020 = history_data[history_data['Year'] == 2020]['OtherExpenses'].values[0]
    else:
        total_other_expenses_2020 = history_data['OtherExpenses'].max()
    
    client_profit_data, product_commission_rates, total_five_activity_cost, remaining_other_expenses, total_commission, remaining_fixed_cost = calculate_correct_client_profits(client_data, total_other_expenses_2020)
    
    # 标签页结构
    tab1, tab2, tab3 = st.tabs([
        "战略概览与客户分析", 
        "深度根因分析", 
        "解决方案与预测"
    ])
    
    with tab1:
        if data_loaded:
            create_tab1_analysis(history_data, client_data)
        else:
            st.warning("请先加载数据以进行分析")
    
    with tab2:
        if data_loaded:
            create_tab2_analysis(history_data, 
                client_data, 
                client_profit_data, 
                product_commission_rates,  # 替换原来的product_margins
                total_five_activity_cost, 
                remaining_other_expenses,
                total_commission,          # 新增参数
                remaining_fixed_cost       # 新增参数
                )
        else:
            st.warning("请先加载数据以进行分析")
    
    with tab3:
        if data_loaded:
            create_tab3_analysis(history_data, client_data, client_profit_data)
        else:
            st.warning("请先加载数据以进行分析")

if __name__ == "__main__":
    main()


    
