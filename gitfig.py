# 导入必要的库
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
from dash.exceptions import PreventUpdate

# 读取CSV数据文件
df = pd.read_csv('github_extract.csv')

# 初始化Dash应用实例
app = dash.Dash(__name__)

# 设置应用的页面布局
app.layout = html.Div([
    # 页面标题
    html.H1('GitHub 项目分析面板', style={'textAlign': 'center'}),
    
    # 顶部统计卡片区域：展示关键指标
    html.Div([
        # 总项目数统计卡片
        html.Div([
            html.H4('总项目数'),
            html.H2(f'{len(df)}')
        ], className='stat-card'),
        # 热门项目数统计卡片
        html.Div([
            html.H4('热门项目数'),
            html.H2(f'{df["is_hot"].sum()}')
        ], className='stat-card'),
        # 已认领项目数统计卡片
        html.Div([
            html.H4('已认领项目数'),
            html.H2(f'{df["is_claimed"].sum()}')
        ], className='stat-card'),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
    
    # 项目列表数据表格区域
    html.Div([
        html.H3('项目列表'),
        # 使用DataTable组件展示项目详细信息
        dash.dash_table.DataTable(
            id='project-table',
            columns=[
                {'name': '项目名称', 'id': 'title'},
                {'name': '点击量', 'id': 'clicks_total'},
                {'name': '项目描述', 'id': 'summary'}
            ],
            data=df.to_dict('records'),
            page_size=5,  # 每页显示5条记录
            style_cell={
                'textAlign': 'left',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            # 设置表格间隔行的背景色
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], style={'margin': '20px'}),
    
    # 项目点击量柱状图
    html.Div([
        dcc.Graph(
            id='clicks-bar-chart',
            figure=px.bar(
                df,
                x='title',
                y='clicks_total',
                title='项目点击量统计',
                # 添加颜色区分
                color=df.apply(lambda x: '热门已认领' if x['is_hot'] and x['is_claimed']
                             else '热门未认领' if x['is_hot'] and not x['is_claimed']
                             else '普通已认领' if not x['is_hot'] and x['is_claimed']
                             else '普通未认领', axis=1),
                color_discrete_map={
                    '热门已认领': '#FF6B6B',    # 红色
                    '热门未认领': '#4ECDC4',    # 青色
                    '普通已认领': '#45B7D1',    # 蓝色
                    '普通未认领': '#96CEB4'     # 绿色
                }
            ).update_layout(
                xaxis_tickangle=-45,
                height=500,
                legend_title='项目状态',
                showlegend=True
            )
        )
    ]),
    
    # 项目详情模态框
    html.Div(
        id='project-modal',
        style={'display': 'none', 'position': 'fixed', 'top': '50%', 'left': '50%',
               'transform': 'translate(-50%, -50%)', 'backgroundColor': 'white',
               'padding': '20px', 'borderRadius': '5px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
               'zIndex': 1000},
        children=[
            html.H3(id='modal-title'),  # 模态框标题
            html.P(id='modal-description'),  # 项目描述
            html.P(id='modal-stats'),  # 项目统计信息
            html.Button('关闭', id='close-modal', n_clicks=0)  # 关闭按钮
        ]
    )
])

# 处理图表点击事件的回调函数
@app.callback(
    [Output('project-modal', 'style'),  # 控制模态框显示样式
     Output('modal-title', 'children'),  # 更新模态框标题
     Output('modal-description', 'children'),  # 更新项目描述
     Output('modal-stats', 'children')],  # 更新项目统计信息
    [Input('clicks-bar-chart', 'clickData'),  # 监听图表点击事件
     Input('close-modal', 'n_clicks')]  # 监听关闭按钮点击事件
)
def display_click_data(clickData, close_clicks):
    # 获取触发回调的上下文
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # 获取触发回调的组件ID
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # 处理关闭按钮点击事件
    if triggered_id == 'close-modal':
        return {'display': 'none'}, '', '', ''
    
    # 处理图表点击事件
    if clickData is None:
        raise PreventUpdate
    
    # 获取点击的数据点对应的项目信息
    point_index = clickData['points'][0]['pointIndex']
    project = df.iloc[point_index]
    
    # 准备模态框展示的内容
    title = project['title']
    description = project['summary']
    stats = f"点击量: {project['clicks_total']} | 是否热门: {'是' if project['is_hot'] else '否'} | 是否已认领: {'是' if project['is_claimed'] else '否'}"
    
    # 返回更新后的模态框样式和内容
    return {'display': 'block', 'position': 'fixed', 'top': '50%', 'left': '50%',
            'transform': 'translate(-50%, -50%)', 'backgroundColor': 'white',
            'padding': '20px', 'borderRadius': '5px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'zIndex': 1000}, title, description, stats

# 启动应用
if __name__ == '__main__':
    app.run(debug=True)  # 以调试模式运行应用
