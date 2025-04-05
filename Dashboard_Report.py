import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px

# Đọc danh sách mã cổ phiếu
file_path1 = "C:/Users/LENOVO/Downloads/Data_CK/Merged_Data.csv"
df1 = pd.read_csv(file_path1)
stock_codes = df1['Code'].unique().tolist()  # Tránh trùng lặp mã cổ phiếu

def format_number(value):
    """
    Định dạng số đã chia cho 1 tỷ:
    - T (nghìn tỷ) nếu số >= 1_000_000
    - B (tỷ) nếu số >= 1_000
    - M (triệu) nếu số >= 1
    - Giữ nguyên nếu số < 1
    """
    abs_value = abs(value)  # Lấy giá trị tuyệt đối để so sánh

    if abs_value >= 1_000_000:
        formatted_value = f"{value / 1_000_000:.2f}T"  # Nghìn tỷ
    elif abs_value >= 1_000:
        formatted_value = f"{value / 1_000:.2f}B"  # Tỷ
    elif abs_value >= 1:
        formatted_value = f"{value:.2f}M"  # Triệu
    else:
        formatted_value = f"{value:.2f}"  # Giữ nguyên nếu nhỏ hơn 1 triệu

    return formatted_value  # Giữ nguyên dấu chấm



# Định nghĩa đường dẫn dữ liệu
DATA_PATH = "C:/Users/LENOVO/Downloads/Data_CK/"

# Hàm tải dữ liệu theo năm
def load_data(year):
    file_name = f"{year}_Filtered.csv"
    file_path = DATA_PATH + file_name
    try:
        return pd.read_csv(file_path, dtype=str, low_memory=False)
    except FileNotFoundError:
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu file không tồn tại

# Định nghĩa các chỉ số tài chính
metrics = {
    "LỢI NHUẬN SAU THUẾ": "KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp",
    "DÒNG TIỀN TỰ DO": [
        "LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)",
        "LCTT. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác (TT)"
    ],  # Trừ

    "TỔNG TÀI SẢN": "CĐKT. TỔNG CỘNG TÀI SẢN",
    "CHI PHÍ NGUYÊN LIỆU":"BCTCKH. Doanh thu kế hoạch",
    "NỢ PHẢI TRẢ":"CĐKT. NỢ PHẢI TRẢ",
    "VỐN CHỦ SỞ HỮU":"CĐKT. VỐN CHỦ SỞ HỮU",
    "DOANH THU THUẦN":"KQKD. Doanh thu thuần",
    "LỢI NHUẬN GỘP":"KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ",
    "LƯU CHUYỂN TIỀN TỆ RÒNG TỪ HĐSXKD":"LCTT. Lưu chuyển tiền tệ ròng từ hoạt động sản xuất kinh doanh (TT)",
    "TIỀN VÀ CÁC KHOẢN TƯƠNG ĐƯƠNG TIỀN":"LCTT. Tiền và tương đương tiền cuối kỳ (TT)",
    "CHI PHÍ TÀI CHÍNH":"KQKD. Chi phí tài chính",
    "NỢ NGẮN HẠN":"CĐKT. Nợ ngắn hạn",
    "TỔNG TIỀN MẶT": [
        "LCTT. Tiền và tương đương tiền cuối kỳ (TT)",
        "CĐKT. Đầu tư tài chính ngắn hạn"
    ],  # Cộng

    "Quick Ratio": {
        "numerator": ["CĐKT. TÀI SẢN NGẮN HẠN", "(-CĐKT. Hàng tồn kho, ròng)"],
        "denominator": "CĐKT. Nợ ngắn hạn"
    },  # Chia

    "Cash Ratio": {
        "numerator": ["CĐKT. Tiền và tương đương tiền"],
        "denominator": "CĐKT. Nợ ngắn hạn"
    },  # Chia

    "Inventory Turnover": {
        "numerator": ["KQKD. Chi phí bán hàng"],
        "denominator": "CĐKT. Hàng tồn kho,ròng"
    },

    "Accounts Payable Turnover": {
        "numerator": ["KQKD. Chi phí bán hàng"],
        "denominator": "CĐKT. Các khoản phải trả"
    },

    "ROA": {
        "numerator": ["KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp"],
        "denominator": "CĐKT. TỔNG CỘNG TÀI SẢN",
        "percentage": True
    },

    "ROE": {
        "numerator": ["KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp"],
        "denominator": "CĐKT. VỐN CHỦ SỞ HỮU",
        "percentage": True
    }
}


data_year=["2020","2021","2022","2023","2024"]

font_awesome = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
meta_tags = [{"name": "viewport", "content": "width=device-width"}]
external_stylesheets = [meta_tags, font_awesome]

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# Giao diện Dash
app.layout = html.Div([
    html.Div([  # Logo và tiêu đề
        html.Div([
            html.Img(
                src=app.get_asset_url('statistics.png'),
                style={'height': '100px', 'marginLeft': '-10px', 'marginTop': '-11px'},
                className='title_image'
            ),
            html.H6(
                'Financial Dashboard',
                style={'color': '#cf3d3d','fontWeight': 'bold', 'marginTop': '2px'},
                className='title'
            ),
        ], className='logo_title'),  # Đổi từ 'logo_year' thành 'logo_title'
        
        html.Div([  # Dropdown chọn mã cổ phiếu
            html.P('Chọn mã cổ phiếu',
                   style={'color': '#0a5167','fontWeight': 'bold','marginTop': '17px'},
                   className='drop_down_list_title'),
            dcc.Dropdown(
                id='select_stock',
                options=[{'label': code, 'value': code} for code in stock_codes],
                placeholder='Select Stock',
                className='drop_down_list'
            )
        ], className='title_drop_down_list'),

        html.Div([  # Dropdown chọn năm X
            html.P('Chọn năm so sánh',
                style={'color': '#0a5167','fontWeight': 'bold','marginTop': '17px'},
                className='drop_down_list_title'),
            dcc.Dropdown(
                id='select_year_x',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display': True},
                value='2020',
                options=[{'label': str(year), 'value': str(year)} for year in range(2020, 2026)],
                placeholder='Select Year X',
                className='drop_down_list'),
        ], className='title_drop_down_list'),

        html.Div([  # Dropdown chọn năm Y
            html.P('Chọn năm hiện tại',
                style={'color': '#0a5167','fontWeight': 'bold','marginTop': '17px'},
                className='drop_down_list_title'),
            dcc.Dropdown(
                id='select_year_y',
                options=[{'label': str(year), 'value': str(year)} for year in range(2020, 2026)],
                placeholder='Select Year Y',
                className='drop_down_list'),
        ], className='title_drop_down_list'),
    ], className='title_and_drop_down_list'),

    html.Div([ 
        html.Div([ 
            html.Div([
                html.Div([
                    html.Div([
                        html.P("NỢ PHẢI TRẢ",
                                className='format_text')
                    ], className='accounts_receivable1'),
                    html.Div([
                        html.Div(id='accounts_receivable_value',
                                    className='numeric_value')
                    ], className='accounts_receivable2')
                ], className='accounts_receivable_column'),
                html.Div([ 
                    html.Div([
                        html.P("VỐN CHỦ SỞ HỮU",
                                className='format_text')
                    ], className='accounts_payable1'),
                    html.Div([
                        html.Div(id='accounts_payable_value',
                                    className='numeric_value')
                    ], className='accounts_payable2')
                ], className='accounts_payable_column'),
            ], className='receivable_payable_column'), 

            html.Div([
                html.Div([
                    html.Div([
                        html.P('DOANH THU THUẦN',
                                className='format_text')
                    ], className='income1'),
                    html.Div([
                        html.Div(id='income_value',
                                    className='numeric_value')
                    ], className='income2')
                ], className='income_column'),
                html.Div([
                    html.Div([
                        html.P('DOANH THU KẾ HOẠCH',
                                className='format_text')
                    ], className='expenses1'),
                    html.Div([
                        html.Div(id='expenses_value',
                                    className='numeric_value')
                    ], className='expenses2')
                ], className='expenses_column'),
            ], className='income_expenses_column'),
        ], className='first_row'),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                    ], className='first_left_circle'),
                    html.Div([
                        html.Div(id='second_left_circle'),
                    ], className='second_left_circle'),
                ], className='first_second_left_column'),
            ], className='left_circle_row'),
            dcc.Graph(id='chart1',
                        config={'displayModeBar': False},
                        className='donut_chart_size'),
        ], className='text_and_chart'),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                    ], className='first_right_circle'),
                    html.Div([
                        html.Div(id='second_right_circle'),
                    ], className='second_right_circle'),
                ], className='first_second_right_column'),
            ], className='right_circle_row'),
            dcc.Graph(id='chart2',
                        config={'displayModeBar': False},
                        className='donut_chart_size'),

            html.Div([
                html.Div([
                    html.Div([
                        html.P('CÁC CHỈ SỐ TÀI CHÍNH',
                                className='format_text')
                    ], className='income_statement'),

                    html.Div([
                        html.Div([
                            html.Div([
                                html.P('Quick Ratio',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement1',
                                            className='income_statement1'),
                            ], className='income_statement_indicator_row1'),
                            html.Div([
                                html.P('Cash Ratio',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement2',
                                            className='income_statement1')
                            ], className='income_statement_indicator_row2'),
                            html.Hr(className='bottom_border'),
                            html.Div([
                                html.P('D/E',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement3',
                                            className='income_statement1'),
                            ], className='income_statement_indicator_row3'),
                            html.Div([
                                html.P('DOH',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement4',
                                            className='income_statement1')
                            ], className='income_statement_indicator_row4'),
                            html.Hr(className='bottom_border'),
                            html.Div([
                                html.P('ROA',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement5',
                                            className='income_statement1'),
                            ], className='income_statement_indicator_row5'),
                            html.Div([
                                html.P('ROE',
                                        className='income_statement_title'
                                        ),
                                html.Div(id='income_statement6',
                                            className='income_statement1')
                            ], className='income_statement_indicator_row6'),
                        ], className='in_state_column')
                    ], className='income_statement_multiple_values'),
                ], className='income_statement_column1'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.P('',
                                   className='income_statement_title'
                                   ),
                            html.Div(id='income_statement7',
                                     className='income_statement1')
                        ], className='income_statement_indicator_row7'),
                    ], className='net_profit_column')
                ], className='net_profit'),
            ], className='net_profit1'),
        ], className='income_statement_row')
    ], className='f_row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.P('TIỀN RÒNG HĐSXKD',
                               className='format_text')
                    ], className='accounts_receivable1'),
                    html.Div([
                        html.Div(id='quick_ratio_value',
                                 className='numeric_value')
                    ], className='accounts_receivable2')
                ], className='accounts_receivable_column'),
                html.Div([
                    html.Div([
                        html.P('TIỀN & TƯƠNG ĐƯƠNG TIỀN',
                               className='format_text')
                    ], className='accounts_payable1'),
                    html.Div([
                        html.Div(id='current_ratio_value',
                                 className='numeric_value')
                    ], className='accounts_payable2')
                ], className='accounts_payable_column'),
            ], className='receivable_payable_column'),

            html.Div([
                html.Div([
                    html.Div([
                        html.P('CHI PHÍ TÀI CHÍNH',
                               className='format_text')
                    ], className='income1'),
                    html.Div([
                        html.Div(id='net_profit_value',
                                 className='numeric_value')
                    ], className='income2')
                ], className='income_column'),
                html.Div([
                    html.Div([
                        html.P('NỢ NGẮN HẠN',
                               className='format_text')
                    ], className='expenses1'),
                    html.Div([
                        html.Div(id='cash_at_eom_value',
                                 className='numeric_value')
                    ], className='expenses2')
                ], className='expenses_column'),
            ], className='income_expenses_column'),
        ], className='first_row'),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                    ], className='first_left_circle'),
                    html.Div([
                        html.Div(id='third_left_circle'),
                    ], className='second_left_circle'),
                ], className='first_second_left_column'),
            ], className='left_circle_row'),
            dcc.Graph(id='chart3',
                      config={'displayModeBar': False},
                      className='donut_chart_size'),
        ], className='text_and_chart'),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                    ], className='first_right_circle'),
                    html.Div([
                        html.Div(id='fourth_right_circle'),
                    ], className='second_right_circle'),
                ], className='first_second_right_column'),
            ], className='right_circle_row'),
            dcc.Graph(id='chart4',
                      config={'displayModeBar': False},
                      className='donut_chart_size'),

            html.Div([
                dcc.Graph(id='bar_chart',
                          config={'displayModeBar': False},
                          className='bar_chart_size'),
            ], className='net_profit2'),
        ], className='income_statement_row')
    ], className='f_row'),

    html.Div([
        dcc.Graph(id='line_chart',
                  config={'displayModeBar': False},
                  className='line_chart_size'),
        dcc.Graph(id='combination_chart',
                  config={'displayModeBar': False},
                  className='combination_chart_size'),
    ], className='last_row')
])

# Callback cập nhật biểu đồ
@app.callback( # số 1
    Output('accounts_receivable_value', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')])
def update_accounts_receivable(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Lấy giá trị cột "NỢ PHẢI TRẢ"
    column_name = metrics["NỢ PHẢI TRẢ"]  # "CĐKT. NỢ PHẢI TRẢ"
    accounts_receivable_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    accounts_receivable_y = df_y[column_name].iloc[0]

    # Tính % thay đổi
    pct_change = ((accounts_receivable_y - accounts_receivable_x) / abs(accounts_receivable_x)) * 100 if accounts_receivable_x != 0 else 0

    # Hiển thị kết quả với màu sắc tương ứng
    if pct_change > 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_receivable_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator1'),
                        html.Div([
                            html.I(className="fas fa-caret-up",  
                                style={"font-size": "25px", 'color': '#00B050'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_receivable_y)), 
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change),  
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down",
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'), 
         ] 
    else:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_receivable_y)),  
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change),  
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down", 
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]


@app.callback( #biểu đồ 2
    Output('accounts_payable_value', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def accounts_payable_receivable(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

   
    column_name = metrics["VỐN CHỦ SỞ HỮU"] 
    accounts_payable_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    accounts_payable_y = df_y[column_name].iloc[0]

    # Tính % thay đổi
    pct_change = ((accounts_payable_y - accounts_payable_x) / abs(accounts_payable_x)) * 100 if accounts_payable_x != 0 else 0

    # Hiển thị kết quả với màu sắc tương ứng
    if pct_change > 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_payable_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator1'),
                        html.Div([
                            html.I(className="fas fa-caret-up",  
                                style={"font-size": "25px", 'color': '#00B050'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_payable_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down",  
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    else:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(accounts_payable_y)),  
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change),  
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down", 
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]

@app.callback( #số 3
    Output('income_value', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def income_receivable(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

  
    column_name = metrics["DOANH THU THUẦN"] 
    income_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    income_y = df_y[column_name].iloc[0]

    # Tính % thay đổi
    pct_change = ((income_y - income_x) / abs(income_x)) * 100 if income_x != 0 else 0

    # Hiển thị kết quả với màu sắc tương ứng
    if pct_change > 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(income_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator1'),
                        html.Div([
                            html.I(className="fas fa-caret-up",  
                                style={"font-size": "25px", 'color': '#00B050'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(income_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down",  
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    else:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(income_y)),  
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change),  
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down", 
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    
@app.callback(#số4
    Output('expenses_value', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def expenses_receivable(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

  
    column_name = metrics["CHI PHÍ NGUYÊN LIỆU"] 
    expenses_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    expenses_y = df_y[column_name].iloc[0]

    # Tính % thay đổi
    pct_change = ((expenses_y - expenses_x) / abs(expenses_x)) * 100 if expenses_x != 0 else 0

    # Hiển thị kết quả với màu sắc tương ứng
    if pct_change > 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(expenses_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator1'),
                        html.Div([
                            html.I(className="fas fa-caret-up",  
                                style={"font-size": "25px", 'color': '#00B050'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(expenses_y)),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change), 
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down",  
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]
    else:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(expenses_y)),  
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_change),  
                                className='indicator2'),
                        html.Div([
                            html.I(className="fas fa-caret-down", 
                                style={"font-size": "25px", 'color': '#FF3399'}),
                        ], className='value_indicator'),
                    ], className='value_indicator_row'),
                ], className='vs_p_m_column')  
            ], className='indicator_column'),  
        ]


@app.callback(Output('second_left_circle', 'children'), #vòng tròn 1
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def first_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    column_name = metrics["LỢI NHUẬN SAU THUẾ"] 
    loinhuan_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    loinhuan_y = df_y[column_name].iloc[0]
    loinhuan_y_formatted=format_number(loinhuan_y)
    # Tính % thay đổi
    pct_net_profit_margin_percentage = ((loinhuan_y - loinhuan_x) / abs(loinhuan_x)) * 100 if loinhuan_x != 0 else 0

    if pct_net_profit_margin_percentage > 0:
        return [
            html.Div([
                html.Div([
                    html.P('LỢI NHUẬN SAU THUẾ',
                            className = 'donut_chart_title'
                            ),
                    html.P(loinhuan_y_formatted,
                            className = 'net_profit_margin_percentage'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}%'.format(pct_net_profit_margin_percentage),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_net_profit_margin_percentage < 0:
        return [
            html.Div([
                html.Div([
                    html.P('LỢI NHUẬN SAU THUẾ',
                            className = 'donut_chart_title'
                            ),
                    html.P(loinhuan_y_formatted,
                            className = 'net_profit_margin_percentage'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_net_profit_margin_percentage),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_net_profit_margin_percentage == 0:
        return [
            html.Div([
                html.Div([
                    html.P('LỢI NHUẬN SAU THUẾ',
                            className = 'donut_chart_title'
                            ),
                    html.P(loinhuan_y_formatted,
                            className = 'net_profit_margin_percentage'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_net_profit_margin_percentage),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous month',
                            className = 'vs_previous_month')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

@app.callback(Output('chart1', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def first_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    
    column_name = metrics["LỢI NHUẬN SAU THUẾ"] 
    loinhuan_x = df_x[column_name].iloc[0]  # Lấy giá trị đầu tiên
    loinhuan_y = df_y[column_name].iloc[0]
        # Tính tổng lợi nhuận của cả hai năm
    total_profit = loinhuan_x + loinhuan_y
    
    # Tính tỷ lệ phần trăm của từng năm
    if total_profit != 0:
        pct_loinhuan_x = (loinhuan_x / total_profit) * 100
        pct_loinhuan_y = (loinhuan_y / total_profit) * 100
    else:
        pct_loinhuan_x = 0
        pct_loinhuan_y = 0

    colors = ['#B258D3', '##FAF3C0']
    return {
        'data': [go.Pie(labels = ['', ''],
                        values = [pct_loinhuan_x, pct_loinhuan_y],
                        marker = dict(colors = colors,
                                      # line=dict(color='#DEB340', width=2)
                                      ),
                        hoverinfo = 'skip',
                        textinfo = 'text',
                        hole = .7,
                        rotation = 90
                        )],

        'layout': go.Layout(
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            margin = dict(t = 35, b = 0, r = 0, l = 0),
            showlegend = False,
            title = {'text': '',
                     'y': 0.95,
                     'x': 0.5,
                     'xanchor': 'center',
                     'yanchor': 'top'},
            titlefont = {'color': 'white',
                         'size': 15},
        ),

    }

# hàm tính dòng tiền tự do
def calculate_free_cash_flow(df):
    """Tính dòng tiền tự do = Lưu chuyển tiền từ HĐSXKD - Tiền chi cho TSCĐ"""
    operating_cash_flow = df["LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)"].iloc[0]
    capex = df["LCTT. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác (TT)"].iloc[0]
    return (operating_cash_flow-capex) if capex != 0 else 0

@app.callback(Output('second_right_circle', 'children'), # hình tròn 2
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def second_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
        # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    # 🔹 Tính toán DÒNG TIỀN TỰ DO trước khi lọc theo mã cổ phiếu

    free_cash_flow_x = calculate_free_cash_flow(df_x)
    free_cash_flow_y = calculate_free_cash_flow(df_y)
    free_cash_flow_y_formatted = format_number(free_cash_flow_y)
    # Tính % thay đổi
    pct_income_budget_percentage = ((free_cash_flow_y - free_cash_flow_x) / abs(free_cash_flow_x)) * 100 if free_cash_flow_x != 0 else 0

    if pct_income_budget_percentage > 0:
        return [
            html.Div([
                html.Div([
                    html.P('DÒNG TIỀN TỰ DO',
                            className = 'donut_chart_title'
                            ),
                    html.P(free_cash_flow_y_formatted,
                            className = 'net_profit_margin_percentage1'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}%'.format(pct_income_budget_percentage),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_income_budget_percentage < 0:
        return [
            html.Div([
                html.Div([
                    html.P('DÒNG TIỀN TỰ DO',
                            className = 'donut_chart_title'
                            ),
                    html.P(free_cash_flow_y_formatted,
                            className = 'net_profit_margin_percentage1'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_income_budget_percentage),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_income_budget_percentage == 0:
        return [
            html.Div([
                html.Div([
                    html.P('DÒNG TIỀN TỰ DO',
                            className = 'donut_chart_title'
                            ),
                    html.P(free_cash_flow_y_formatted,
                            className = 'net_profit_margin_percentage1'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_income_budget_percentage),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]


@app.callback(Output('chart2', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def second_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    
        # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    
        # 🔹 Tính toán DÒNG TIỀN TỰ DO trước khi lọc theo mã cổ phiếu

    free_cash_flow_x = calculate_free_cash_flow(df_x)
    free_cash_flow_y = calculate_free_cash_flow(df_y)

    # Tính % thay đổi
        # Tính tổng lợi nhuận của cả hai năm
    total_profit = free_cash_flow_x + free_cash_flow_y
    
    # Tính tỷ lệ phần trăm của từng năm
    if total_profit != 0:
        pct_cash_x = (free_cash_flow_x / total_profit) * 100
        pct_cash_y = (free_cash_flow_y/ total_profit) * 100
    else:
        pct_cash_x = 0
        pct_cash_y = 0
    colors = ['#63A0CC', '##FAF3C0']

    return {
        'data': [go.Pie(labels = ['', ''],
                        values = [pct_cash_x, pct_cash_y],
                        marker = dict(colors = colors,
                                      # line=dict(color='#DEB340', width=2)
                                      ),
                        hoverinfo = 'skip',
                        textinfo = 'text',
                        hole = .7,
                        rotation = 360
                        )],

        'layout': go.Layout(
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            autosize = True,
            margin = dict(t = 35, b = 0, r = 0, l = 0),
            showlegend = False,
            title = {'text': '',
                     'y': 0.95,
                     'x': 0.5,
                     'xanchor': 'center',
                     'yanchor': 'top'},
            titlefont = {'color': 'white',
                         'size': 15},
        ),

    }

# Hàm tính quick ratio
def calculate_quick_ratio(df):
    numerator_cols = ["CĐKT. TÀI SẢN NGẮN HẠN", "CĐKT. Hàng tồn kho, ròng"]
    denominator_col = "CĐKT. Nợ ngắn hạn"

    if denominator_col not in df.columns:
        return None

    # Kiểm tra từng cột numerator có trong dataframe không
    for col in numerator_cols:
        if col not in df.columns:
            return None

    # Tính Quick Ratio
    quick_ratio = (df[numerator_cols[0]] - df[numerator_cols[1]]) / df[denominator_col]

    return quick_ratio.iloc[0]  # Lấy giá trị đầu tiên





# Các hàm tính chỉ số
def calculate_cash_ratio(df):
    cash = "LCTT. Tiền và tương đương tiền cuối kỳ (TT)"
    denominator_col = "CĐKT. Nợ ngắn hạn"
    if cash not in df.columns or denominator_col not in df.columns:
        return None
    # Tính cash
    cash_ratio = df[cash] / df[denominator_col]
    return cash_ratio.iloc[0]  # Lấy giá trị đầu tiên

def calculate_inventory_turnover(df):
    tongtaisan = df["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]  # Lấy giá trị đầu tiên
    vcsh = df["CĐKT. VỐN CHỦ SỞ HỮU"].iloc[0]  # Lấy giá trị đầu tiên
    return (tongtaisan-vcsh) / vcsh if vcsh != 0 else 0

def calculate_accounts_payable_turnover(df):
    """Tính Accounts Payable Turnover = Giá vốn hàng bán / Phải trả người bán"""
    cogs = df["CĐKT. Hàng tồn kho, ròng"].iloc[0]  # Lấy giá trị đầu tiên
    cog1= df["KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ"].iloc[0]
    cog2= df["KQKD. Doanh thu thuần"].iloc[0]
    tru=cog2-cog1
    return (cogs/tru)*365 if tru!=0 else 0 

def calculate_roa(df):
    """Tính Return on Assets (ROA) = Lợi nhuận ròng / Tổng tài sản"""
    net_income = df["KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp"].iloc[0]
    total_assets = df["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]
    return net_income / total_assets if total_assets != 0 else 0

def calculate_roe(df):
    """Tính Return on Equity (ROE) = Lợi nhuận ròng / Vốn chủ sở hữu"""
    net_income = df["KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp"].iloc[0]  # Lấy giá trị đầu tiên
    equity = df["CĐKT. VỐN CHỦ SỞ HỮU"].iloc[0]  # Lấy giá trị đầu tiên
    return net_income / equity if equity != 0 else 0

def calculate_total_cash(df):
    """Tính tổng tiền mặt = Tiền và tương đương tiền + Các khoản đầu tư ngắn hạn"""
    cash = df[metrics["TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN"]].iloc[0]  # Lấy giá trị đầu tiên
    short_term_investments = df[metrics["CÁC KHOẢN ĐẦU TƯ NGẮN HẠN"]].iloc[0]  # Lấy giá trị đầu tiên
    return cash + short_term_investments


@app.callback(Output('income_statement1', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def quick_ratio(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Tính Quick Ratio
    quickratio_x = calculate_quick_ratio(df_x)
    quickratio_y = calculate_quick_ratio(df_y)

    if quickratio_x is None or quickratio_y is None:
        return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

    # Tính % thay đổi
    pct_income = ((quickratio_y - quickratio_x) / abs(quickratio_x)) * 100 if quickratio_x != 0 else 0

    if pct_income > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(quickratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_income),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_income < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(quickratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_income),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(quickratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_income),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]



# @app.callback(Output('income_statement2', 'children'),
#     [Input('select_stock', 'value'),
#      Input('select_year_x', 'value'),
#      Input('select_year_y', 'value')]
# )
# def cash_ratio(stock_code, select_year_x, select_year_y):
#     if stock_code is None or select_year_x is None or select_year_y is None:
#         raise dash.exceptions.PreventUpdate

#     # Đọc dữ liệu từ file của năm X và Y
#     file_x = f"{select_year_x}_Filtered.csv"
#     file_y = f"{select_year_y}_Filtered.csv"

#     try:
#         df_x = pd.read_csv(file_x)
#         df_y = pd.read_csv(file_y)
#     except FileNotFoundError:
#         return "File dữ liệu không tồn tại."

#     # Lọc theo mã cổ phiếu
#     df_x = df_x[df_x['Code'] == stock_code]
#     df_y = df_y[df_y['Code'] == stock_code]

#     if df_x.empty or df_y.empty:
#         return "Không có dữ liệu cho mã cổ phiếu này."

#     # Tính Quick Ratio
#     cashratio_x = calculate_cash_ratio(df_x)
#     cashratio_y = calculate_cash_ratio(df_y)

#     if cashratio_x is None or cashratio_y is None:
#         return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

#     # Tính % thay đổi
#     pct_cost_of_goods_sold = ((cashratio_y - cashratio_x) / abs(cashratio_x)) * 100 if cashratio_x != 0 else 0


#     if pct_cost_of_goods_sold > 0:
#         return [
#             html.Div([
#                 html.P('%{0:,.0f}'.format(cashratio_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('+{0:,.1f}%'.format(pct_cost_of_goods_sold),
#                            className = 'indicator1'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-up",
#                                style = {"font-size": "25px",
#                                         'color': '#00B050'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]
#     elif pct_cost_of_goods_sold < 0:
#         return [
#             html.Div([
#                 html.P('%{0:,.0f}'.format(cashratio_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_cost_of_goods_sold),
#                            className = 'indicator2'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-down",
#                                style = {"font-size": "25px",
#                                         'color': '#FF3399'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]

#     elif pct_cost_of_goods_sold == 0:
#         return [
#             html.Div([
#                 html.P('%{0:,.0f}'.format(cashratio_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_cost_of_goods_sold),
#                            className = 'indicator2'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]


# @app.callback(Output('income_statement3', 'children'),
#      [Input('select_stock', 'value'),
#      Input('select_year_x', 'value'),
#      Input('select_year_y', 'value')]
# )
# def inventory_turnover(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    inventory_x = calculate_inventory_turnover(df_x)
    inventory_y = calculate_inventory_turnover(df_y)

    if inventory_x is None or inventory_y is None:
        return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

    # Tính % thay đổi
    pct_gross_profit = ((inventory_y - inventory_x) / abs(inventory_x)) * 100 if inventory_x != 0 else 0



    if pct_gross_profit > 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(inventory_y),
                       className = 'monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_gross_profit),
                           className = 'indicator1'),
                    html.Div([
                        html.I(className = "fas fa-caret-up",
                               style = {"font-size": "25px",
                                        'color': '#00B050'},
                               ),
                    ], className = 'value_indicator'),
                ], className = 'value_indicator_row1'),
            ], className = 'income_statement_monthly_row'),
        ]
    elif pct_gross_profit < 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(inventory_y),
                       className = 'monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_gross_profit),
                           className = 'indicator2'),
                    html.Div([
                        html.I(className = "fas fa-caret-down",
                               style = {"font-size": "25px",
                                        'color': '#FF3399'},
                               ),
                    ], className = 'value_indicator'),
                ], className = 'value_indicator_row1'),
            ], className = 'income_statement_monthly_row'),
        ]

    elif pct_gross_profit == 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(inventory_y),
                       className = 'monthly_value'),

                html.Div([
                    html.P('{0:,.1f}%'.format(pct_gross_profit),
                           className = 'indicator2'),
                ], className = 'value_indicator_row1'),
            ], className = 'income_statement_monthly_row'),
        ]

@app.callback(Output('income_statement2', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def cash_ratio(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Tính Cash Ratio
    cashratio_x = calculate_cash_ratio(df_x)
    cashratio_y = calculate_cash_ratio(df_y)

    if cashratio_x is None or cashratio_y is None:
        return "Không thể tính toán Cash Ratio do thiếu dữ liệu."

    # Tính % thay đổi
    pct_change = ((cashratio_y - cashratio_x) / abs(cashratio_x)) * 100 if cashratio_x != 0 else 0

    if pct_change > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(cashratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_change),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(cashratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(cashratio_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
@app.callback(Output('income_statement3', 'children'),
     [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def inventory_turnover(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    inventory_x = calculate_inventory_turnover(df_x)
    inventory_y = calculate_inventory_turnover(df_y)

    if inventory_x is None or inventory_y is None:
        return "Không thể tính toán Inventory Turnover do thiếu dữ liệu."

    # Tính % thay đổi
    pct_change = ((inventory_y - inventory_x) / abs(inventory_x)) * 100 if inventory_x != 0 else 0

    if pct_change > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_change),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]

# @app.callback(Output('income_statement4', 'children'),
#      [Input('select_stock', 'value'),
#      Input('select_year_x', 'value'),
#      Input('select_year_y', 'value')]
# )
# def accounts_payable_turnover(stock_code, select_year_x, select_year_y):
#     if stock_code is None or select_year_x is None or select_year_y is None:
#         raise dash.exceptions.PreventUpdate

#     # Đọc dữ liệu từ file của năm X và Y
#     file_x = f"{select_year_x}_Filtered.csv"
#     file_y = f"{select_year_y}_Filtered.csv"

#     try:
#         df_x = pd.read_csv(file_x)
#         df_y = pd.read_csv(file_y)
#     except FileNotFoundError:
#         return "File dữ liệu không tồn tại."

#     # Lọc theo mã cổ phiếu
#     df_x = df_x[df_x['Code'] == stock_code]
#     df_y = df_y[df_y['Code'] == stock_code]

#     if df_x.empty or df_y.empty:
#         return "Không có dữ liệu cho mã cổ phiếu này."

#     # Tính Quick Ratio
#     payable_x = calculate_accounts_payable_turnover(df_x)
#     payable_y = calculate_accounts_payable_turnover(df_y)

#     if payable_x is None or payable_y is None:
#         return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

#     # Tính % thay đổi
#     pct_total_operating_expenses = ((payable_y - payable_x) / abs(payable_x)) * 100 if payable_x != 0 else 0


#     if pct_total_operating_expenses > 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(payable_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('+{0:,.1f}%'.format(pct_total_operating_expenses),
#                            className = 'indicator1'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-up",
#                                style = {"font-size": "25px",
#                                         'color': '#00B050'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]
#     elif pct_total_operating_expenses < 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(payable_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_total_operating_expenses),
#                            className = 'indicator2'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-down",
#                                style = {"font-size": "25px",
#                                         'color': '#FF3399'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]

#     elif pct_total_operating_expenses == 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(payable_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_total_operating_expenses),
#                            className = 'indicator2'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]


# @app.callback(Output('income_statement5', 'children'),
#      [Input('select_stock', 'value'),
#      Input('select_year_x', 'value'),
#      Input('select_year_y', 'value')]
# )
# def roa(stock_code, select_year_x, select_year_y):
#     if stock_code is None or select_year_x is None or select_year_y is None:
#         raise dash.exceptions.PreventUpdate

#     # Đọc dữ liệu từ file của năm X và Y
#     file_x = f"{select_year_x}_Filtered.csv"
#     file_y = f"{select_year_y}_Filtered.csv"

#     try:
#         df_x = pd.read_csv(file_x)
#         df_y = pd.read_csv(file_y)
#     except FileNotFoundError:
#         return "File dữ liệu không tồn tại."

#     # Lọc theo mã cổ phiếu
#     df_x = df_x[df_x['Code'] == stock_code]
#     df_y = df_y[df_y['Code'] == stock_code]

#     if df_x.empty or df_y.empty:
#         return "Không có dữ liệu cho mã cổ phiếu này."

#     # Tính Quick Ratio
#     roa_x = calculate_roa(df_x)
#     roa_y = calculate_roa(df_y)

#     if roa_x is None or roa_y is None:
#         return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

#     # Tính % thay đổi
#     pct_operating_profit_EBIT = ((roa_y - roa_x) / abs(roa_x)) * 100 if roa_x != 0 else 0
#     if pct_operating_profit_EBIT > 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roa_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('+{0:,.1f}%'.format(pct_operating_profit_EBIT),
#                            className = 'indicator1'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-up",
#                                style = {"font-size": "25px",
#                                         'color': '#00B050'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]
#     elif pct_operating_profit_EBIT < 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roa_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_operating_profit_EBIT),
#                            className = 'indicator2'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-down",
#                                style = {"font-size": "25px",
#                                         'color': '#FF3399'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]

#     elif pct_operating_profit_EBIT == 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roa_y),
#                        className = 'monthly_value'),

#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_operating_profit_EBIT),
#                            className = 'indicator2'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]


# @app.callback(Output('income_statement6', 'children'),
#      [Input('select_stock', 'value'),
#      Input('select_year_x', 'value'),
#      Input('select_year_y', 'value')]
# )
# def inventory_turnover(stock_code, select_year_x, select_year_y):
#     if stock_code is None or select_year_x is None or select_year_y is None:
#         raise dash.exceptions.PreventUpdate

#     # Đọc dữ liệu từ file của năm X và Y
#     file_x = f"{select_year_x}_Filtered.csv"
#     file_y = f"{select_year_y}_Filtered.csv"

#     try:
#         df_x = pd.read_csv(file_x)
#         df_y = pd.read_csv(file_y)
#     except FileNotFoundError:
#         return "File dữ liệu không tồn tại."

#     # Lọc theo mã cổ phiếu
#     df_x = df_x[df_x['Code'] == stock_code]
#     df_y = df_y[df_y['Code'] == stock_code]

#     if df_x.empty or df_y.empty:
#         return "Không có dữ liệu cho mã cổ phiếu này."

#     # Tính Quick Ratio
#     roe_x = calculate_roe(df_x)
#     roe_y = calculate_roe(df_y)

#     if roe_x is None or roe_y is None:
#         return "Không thể tính toán Quick Ratio do thiếu dữ liệu."

#     # Tính % thay đổi
#     pct_taxes= ((roe_y - roe_x) / abs(roe_x)) * 100 if roe_x != 0 else 0


#     if pct_taxes > 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roe_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('+{0:,.1f}%'.format(pct_taxes),
#                            className = 'indicator1'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-up",
#                                style = {"font-size": "25px",
#                                         'color': '#00B050'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]
#     elif pct_taxes < 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roe_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_taxes),
#                            className = 'indicator2'),
#                     html.Div([
#                         html.I(className = "fas fa-caret-down",
#                                style = {"font-size": "25px",
#                                         'color': '#FF3399'},
#                                ),
#                     ], className = 'value_indicator'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]

#     elif pct_taxes == 0:
#         return [
#             html.Div([
#                 html.P('${0:,.0f}'.format(roe_y),
#                        className = 'monthly_value'),
#                 html.Div([
#                     html.P('{0:,.1f}%'.format(pct_taxes),
#                            className = 'indicator2'),
#                 ], className = 'value_indicator_row1'),
#             ], className = 'income_statement_monthly_row'),
#         ]

@app.callback(Output('income_statement4', 'children'),
     [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def accounts_payable_turnover(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Tính Accounts Payable Turnover
    payable_x = calculate_accounts_payable_turnover(df_x)
    payable_y = calculate_accounts_payable_turnover(df_y)

    if payable_x is None or payable_y is None:
        return "Không thể tính toán Accounts Payable Turnover do thiếu dữ liệu."

    # Tính % thay đổi
    pct_change = ((payable_y - payable_x) / abs(payable_x)) * 100 if payable_x != 0 else 0

    if pct_change > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(payable_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_change),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(payable_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(payable_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
@app.callback(Output('income_statement5', 'children'),
     [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def roa(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Tính ROA
    roa_x = calculate_roa(df_x)
    roa_y = calculate_roa(df_y)

    if roa_x is None or roa_y is None:
        return "Không thể tính toán ROA do thiếu dữ liệu."

    # Tính % thay đổi
    pct_change = ((roa_y - roa_x) / abs(roa_x)) * 100 if roa_x != 0 else 0

    if pct_change > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(roa_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_change),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(roa_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(roa_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    
@app.callback(Output('income_statement6', 'children'),
     [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def inventory_turnover(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Tính Inventory Turnover
    inventory_x = calculate_inventory_turnover(df_x)
    inventory_y = calculate_inventory_turnover(df_y)

    if inventory_x is None or inventory_y is None:
        return "Không thể tính toán Inventory Turnover do thiếu dữ liệu."

    # Tính % thay đổi
    pct_change = ((inventory_y - inventory_x) / abs(inventory_x)) * 100 if inventory_x != 0 else 0

    if pct_change > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('+{0:,.1f}%'.format(pct_change),
                           className='indicator1'),
                    html.Div([
                        html.I(className="fas fa-caret-up",
                               style={"font-size": "25px", 'color': '#00B050'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    elif pct_change < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                    html.Div([
                        html.I(className="fas fa-caret-down",
                               style={"font-size": "25px", 'color': '#FF3399'}),
                    ], className='value_indicator'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(inventory_y),
                       className='monthly_value'),
                html.Div([
                    html.P('{0:,.1f}%'.format(pct_change),
                           className='indicator2'),
                ], className='value_indicator_row1'),
            ], className='income_statement_monthly_row'),
        ]

@app.callback(Output('quick_ratio_value', 'children'),  # số 5
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')])

def luuchuyentiente(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    # Kiểm tra xem cột có tồn tại không
    if "LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)" not in df_x.columns or "LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)" not in df_y.columns:
        return "Cột dữ liệu không tồn tại."

    accounts_sx_x = df_x["LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)"].iloc[0]  # Lấy giá trị đầu tiên
    accounts_sx_y = df_y["LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)"].iloc[0]

    # Tính % thay đổi
    pct_quick_ratio = ((accounts_sx_y - accounts_sx_x) / abs(accounts_sx_x)) * 100 if accounts_sx_x != 0 else 0

    # Hiển thị kết quả với màu sắc tương ứng
    if pct_quick_ratio > 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(accounts_sx_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_quick_ratio),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_quick_ratio < 0:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(accounts_sx_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('${0:,.1f}%'.format(pct_quick_ratio),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    else:
        return [
            html.Div([
                html.P('{0:,.2f}'.format(accounts_sx_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_quick_ratio),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
@app.callback(Output('current_ratio_value', 'children'), # số 6
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')])
def tuongduongtien(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    tuongduongtien_x = df_x["LCTT. Tiền và tương đương tiền cuối kỳ (TT)"].iloc[0]  # Lấy giá trị đầu tiên
    tuongduongtien_y = df_y["LCTT. Tiền và tương đương tiền cuối kỳ (TT)"].iloc[0]
    # Tính % thay đổi
    pct_current_ratio = ((tuongduongtien_y - tuongduongtien_x) / abs(tuongduongtien_x)) * 100 if tuongduongtien_x != 0 else 0
    if pct_current_ratio > 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(tuongduongtien_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_current_ratio),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_current_ratio < 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(tuongduongtien_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_current_ratio),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_current_ratio == 0:
        return [
            html.Div([
                html.P('${0:,.2f}'.format(tuongduongtien_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_current_ratio),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]


@app.callback(Output('net_profit_value', 'children'), # số 7
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')])
def chiphitaichinh(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    
    chiphi_x = -df_x["KQKD. Chi phí tài chính"].iloc[0]  # Lấy giá trị đầu tiên
    chiphi_y = -df_y["KQKD. Chi phí tài chính"].iloc[0]
    # Tính % thay đổi
    pct_net_profit = ((chiphi_y - (chiphi_x)) / abs((chiphi_x))) * 100 if chiphi_x != 0 else 0
    if pct_net_profit > 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(chiphi_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_net_profit),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_net_profit < 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(chiphi_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_net_profit),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_net_profit == 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(chiphi_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_net_profit),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]


@app.callback(Output('cash_at_eom_value', 'children'), # số 8
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')])
def nonganhan(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    nonganhan_x = df_x["CĐKT. Nợ ngắn hạn"].iloc[0]  # Lấy giá trị đầu tiên
    nonganhan_y = df_y["CĐKT. Nợ ngắn hạn"].iloc[0]
    # Tính % thay đổi
    pct_cash_at_eom = ((nonganhan_y - nonganhan_x) / abs(nonganhan_x)) * 100 if nonganhan_x != 0 else 0

    if pct_cash_at_eom > 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(nonganhan_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}%'.format(pct_cash_at_eom),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_cash_at_eom < 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(nonganhan_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_cash_at_eom),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]
    elif pct_cash_at_eom == 0:
        return [
            html.Div([
                html.P('${0:,.0f}'.format(nonganhan_y),
                        ),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_cash_at_eom),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                ], className = 'vs_p_m_column')
            ], className = 'indicator_column'),
        ]


#-----------------------------------

@app.callback(Output('third_left_circle', 'children'),  #vòng tròn ba
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def three_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    taisan_x = df_x["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]  # Lấy giá trị đầu tiên
    taisan_y = df_y["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]
    taisan_y_formatted=format_number(taisan_y)
    net_profit_margin_vs_target_margin = ((taisan_y - taisan_x) / abs(taisan_x)) * 100 if taisan_x != 0 else 0

    if net_profit_margin_vs_target_margin > 0:
        return [
            html.Div([
                html.Div([
                    html.P('TỔNG TÀI SẢN',
                            className = 'donut_chart_title'
                            ),
                    html.P(taisan_y_formatted,
                            className = 'net_profit_vs_target_margin'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}'.format(net_profit_margin_vs_target_margin),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if net_profit_margin_vs_target_margin < 0:
        return [
            html.Div([
                html.Div([
                    html.P('    TỔNG TÀI SẢN',
                            className = 'donut_chart_title'
                            ),
                    html.P(taisan_y_formatted,
                            className = 'net_profit_vs_target_margin'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}'.format(net_profit_margin_vs_target_margin),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if net_profit_margin_vs_target_margin == 0:
        return [
            html.Div([
                html.Div([
                    html.P('TỔNG TÀI SẢN',
                            className = 'donut_chart_title'
                            ),
                    html.P(taisan_y_formatted,
                            className = 'net_profit_vs_target_margin'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}'.format(net_profit_margin_vs_target_margin),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

@app.callback(Output('chart3', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def three_graph(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."
    
    taisan_x = df_x["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]  # Lấy giá trị đầu tiên
    taisan_y = df_y["CĐKT. TỔNG CỘNG TÀI SẢN"].iloc[0]
        # Tính tổng lợi nhuận của cả hai năm
    total_profit = taisan_x + taisan_y
    
    # Tính tỷ lệ phần trăm của từng năm
    if total_profit != 0:
        pct_taisan_x = (taisan_y / total_profit) * 100
        pct_taisan_y = (taisan_y / total_profit) * 100
    else:
        pct_loinhuan_x = 0
        pct_loinhuan_y = 0
    colors = ['#D35940', '##FAF3C0']

    return {
        'data': [go.Pie(labels = ['', ''],
                        values = [pct_taisan_x, pct_taisan_y],
                        marker = dict(colors = colors,
                                      # line=dict(color='#DEB340', width=2)
                                      ),
                        hoverinfo = 'skip',
                        textinfo = 'text',
                        hole = .7,
                        rotation = 90
                        )],

        'layout': go.Layout(
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            margin = dict(t = 35, b = 0, r = 0, l = 0),
            showlegend = False,
            title = {'text': '',
                     'y': 0.95,
                     'x': 0.5,
                     'xanchor': 'center',
                     'yanchor': 'top'},
            titlefont = {'color': 'white',
                         'size': 15},
        ),

    }

#hàm tính tổng tien mat
def tonng_tienmat(df):
    operating_cash_flow = df["LCTT. Tiền và tương đương tiền cuối kỳ (TT)"].iloc[0]
    capex = df["CĐKT. Đầu tư tài chính ngắn hạn"].iloc[0]
    return (operating_cash_flow+capex) if capex != 0 else 0

@app.callback(Output('fourth_right_circle', 'children'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def four_circle(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    tiemmat_x = tonng_tienmat(df_x)
    tiemmat_y = tonng_tienmat(df_y)
    tiemmat_y_formatted=format_number(tiemmat_y)
    # Tính % thay đổi
    pct_expense_budget_percentage = ((tiemmat_y - tiemmat_x) / abs(tiemmat_x)) * 100 if tiemmat_x != 0 else 0

    if pct_expense_budget_percentage > 0:
        return [
            html.Div([
                html.Div([
                    html.P('  TỔNG TIỀN MẶT',
                            className = 'donut_chart_title'
                            ),
                    html.P(tiemmat_y_formatted,
                            className = 'net_profit_margin_percentage2'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('+{0:,.1f}%'.format(pct_expense_budget_percentage),
                                className = 'indicator1'),
                        html.Div([
                            html.I(className = "fas fa-caret-up",
                                    style = {"font-size": "25px",
                                            'color': '#00B050'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_expense_budget_percentage < 0:
        return [
            html.Div([
                html.Div([
                    html.P('  TỔNG TIỀN MẶT',
                            className = 'donut_chart_title'
                            ),
                    html.P(tiemmat_y_formatted,
                            className = 'net_profit_margin_percentage2'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_expense_budget_percentage),
                                className = 'indicator2'),
                        html.Div([
                            html.I(className = "fas fa-caret-down",
                                    style = {"font-size": "25px",
                                            'color': '#FF3399'},
                                    ),
                        ], className = 'value_indicator'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]

    if pct_expense_budget_percentage == 0:
        return [
            html.Div([
                html.Div([
                    html.P('  TỔNG TIỀN MẶT',
                            className = 'donut_chart_title'
                            ),
                    html.P(tiemmat_y_formatted,
                            className = 'net_profit_margin_percentage2'),
                ], className = 'title_and_percentage'),
                html.Div([
                    html.Div([
                        html.P('{0:,.1f}%'.format(pct_expense_budget_percentage),
                                className = 'indicator2'),
                    ], className = 'value_indicator_row'),
                    html.P('vs previous year',
                            className = 'vs_previous_year')
                ], className = 'vs_p_m_column')
            ], className = 'inside_donut_chart_column'),
        ]


@app.callback(Output('chart4', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_x', 'value'),
     Input('select_year_y', 'value')]
)
def four_graph(stock_code, select_year_x, select_year_y):
    if stock_code is None or select_year_x is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm X và Y
    file_x = f"{select_year_x}_Filtered.csv"
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."
    # Lọc theo mã cổ phiếu
    df_x = df_x[df_x['Code'] == stock_code]
    df_y = df_y[df_y['Code'] == stock_code]

    if df_x.empty or df_y.empty:
        return "Không có dữ liệu cho mã cổ phiếu này."

    tiemmat_x = tonng_tienmat(df_x)
    tiemmat_y = tonng_tienmat(df_y)

        # Tính tổng lợi nhuận của cả hai năm
    total_profit = tiemmat_x + tiemmat_y
    
    # Tính tỷ lệ phần trăm của từng năm
    if total_profit != 0:
        pct_loinhuan_x = (tiemmat_x / total_profit) * 100
        pct_loinhuan_y = (tiemmat_y / total_profit) * 100
    else:
        pct_loinhuan_x = 0
        pct_loinhuan_y = 0

    colors = ['#8AC4A7', '##FAF3C0']

    return {
        'data': [go.Pie(labels = ['', ''],
                        values = [tiemmat_x, tiemmat_y],
                        marker = dict(colors = colors,
                                      # line=dict(color='#DEB340', width=2)
                                      ),
                        hoverinfo = 'skip',
                        textinfo = 'text',
                        hole = .7,
                        rotation = 360
                        )],

        'layout': go.Layout(
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            autosize = True,
            margin = dict(t = 35, b = 0, r = 0, l = 0),
            showlegend = False,
            title = {'text': '',
                     'y': 0.95,
                     'x': 0.5,
                     'xanchor': 'center',
                     'yanchor': 'top'},
            titlefont = {'color': 'white',
                         'size': 15},
        ),

    }


@app.callback(
    Output('bar_chart', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_y', 'value')]
)
def bckd(stock_code, select_year_y):
    if stock_code is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm Y
    file_y = f"{select_year_y}_Filtered.csv"

    try:
        df_y = pd.read_csv(file_y)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc và sắp xếp dữ liệu
    df_y = df_y.sort_values(by="KQKD. Doanh thu thuần", ascending=False)
    top_10 = df_y.head(10)

    # Tạo biểu đồ
    bar_color = '#e3117e'  # Màu của các cột

    return {
        'data': [go.Bar(
            x=top_10['Code'],  # Trục x là mã cổ phiếu (tên công ty)
            y=top_10['KQKD. Doanh thu thuần'],  # Trục y là giá trị lợi nhuận
            marker=dict(color=bar_color),
            width=0.5,
            orientation='v',
            hoverinfo='text',
            hovertext=
            'Mã: ' + top_10['Code'].astype(str) + '<br>' +
            'Lợi nhuận: T' + [f'{x:,.0f}' for x in top_10['KQKD. Doanh thu thuần']] + '<br>'
        )],

        'layout': go.Layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title={
                'text': f'Top 10 Công Ty Có Doanh Thu Thuần Cao Nhất {select_year_y}',
                'y': 0.97,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': '#404040',
                'size': 16,
                'family': 'Calibri',
            },
            margin=dict(r=20, t=50, b=50, l=70),
            xaxis=dict(
                title='<b></b>',
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=True,
                linecolor='white',
                linewidth=0,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='white'
                )
            ),
            yaxis=dict(
                title='<b></b>',
                tickformat='.3s',  # Định dạng số theo đơn vị B, M, T, f
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=True,
                linecolor='white',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Calibri',
                    size=15,
                    color='#404040'
                )
            ),
        )
    }


@app.callback(
    Output('combination_chart', 'figure'),
    [Input('select_stock', 'value'),
     Input('select_year_y', 'value')]
)
def bckd(stock_code, select_year_y):
    if stock_code is None or select_year_y is None:
        raise dash.exceptions.PreventUpdate

    # Đọc dữ liệu từ file của năm Y
    file_x = f"{select_year_y}_Filtered.csv"

    try:
        df_x = pd.read_csv(file_x)
    except FileNotFoundError:
        return "File dữ liệu không tồn tại."

    # Lọc và sắp xếp dữ liệu
    df_x = df_x.sort_values(by="KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ", ascending=False)
    top_10 = df_x.head(10)

    # Tạo biểu đồ
    bar_color = '#ebf761'  # Màu của các cột

    return {
        'data': [go.Bar(
            x=top_10['Code'],  # Trục x là mã cổ phiếu (tên công ty)
            y=top_10['KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'],  # Trục y là giá trị lợi nhuận
            marker=dict(color=bar_color),
            width=0.5,
            orientation='v',
            hoverinfo='text',
            hovertext=
            'Mã: ' + top_10['Code'].astype(str) + '<br>' +
            'Lợi nhuận: ' + [f'{x:,.0f}' for x in top_10['KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ']] + '<br>'
        )],

        'layout': go.Layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title={
                'text': f'Top 10 Công Ty Có Lợi Nhuận Gộp Cao Nhất {select_year_y}',
                'y': 0.97,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': '#404040',
                'size': 16,
                'family': 'Calibri',
            },
            margin=dict(r=20, t=50, b=50, l=70),
            xaxis=dict(
                title='<b></b>',
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=True,
                linecolor='white',
                linewidth=0,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='white'
                )
            ),
            yaxis=dict(
                title='<b></b>',
                tickprefix='$',
                tickformat='.3s',
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=True,
                linecolor='white',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Calibri',
                    size=15,
                    color='#404040'
                )
            ),
        )
    }



file_paths1 = {
    "2020": "C:/Users/LENOVO/Downloads/Data_CK/2020_Filtered.csv",
    "2021": "C:/Users/LENOVO/Downloads/Data_CK/2021_Filtered.csv",
    "2022": "C:/Users/LENOVO/Downloads/Data_CK/2022_Filtered.csv",
    "2023": "C:/Users/LENOVO/Downloads/Data_CK/2023_Filtered.csv",
    "2024": "C:/Users/LENOVO/Downloads/Data_CK/2024_Filtered.csv",
}
@app.callback(
    Output('line_chart', 'figure'),
    Input('select_stock', 'value')
)
def update_chart(select_stock):
    data = []
    
    # Lặp qua từng năm và đọc dữ liệu từ file CSV
    for year, file in file_paths1.items():
        df = pd.read_csv(file)
        
        # Kiểm tra xem cột 'Code' có tồn tại không
        if 'Code' in df.columns:
            df_filtered = df[df['Code'] == select_stock]
            
            # Kiểm tra xem có dữ liệu phù hợp không
            if not df_filtered.empty:
                revenue = df_filtered["KQKD. Doanh thu thuần"].values[0]
                # Thêm dữ liệu vào danh sách `data`
                data.append({"Năm": year, "Doanh thu thuần": revenue})
        else:
            print(f"Cột 'Code' không tồn tại trong file {file}")
            continue
    
    # Tạo DataFrame từ danh sách `data`
    df1_plot = pd.DataFrame(data)
    
    # Kiểm tra dữ liệu trong df_plot
    print("Dữ liệu trong df_plot:")
    print(df1_plot)
    
    # Vẽ biểu đồ nếu df_plot không trống
    if not df1_plot.empty:
        # Định dạng giá trị để hiển thị trên các điểm
        formatted_values = [format_number(value) for value in df1_plot["Doanh thu thuần"]]
        
        # Vẽ biểu đồ đường với giá trị hiển thị tại các điểm
        fig = px.line(df1_plot, x="Năm", y="Doanh thu thuần", title=f"Doanh thu thuần của {select_stock} (2020-2024)",
                      markers=True, text=formatted_values)
        
        # Cập nhật layout giống với mẫu của bạn
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title={
                'text': f"Doanh thu thuần của {select_stock} (2020-2024)",
                'y': 0.97,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'color': '#404040',
                    'size': 16,
                    'family': 'Calibri',
                }
            },
            margin=dict(r=20, t=20, b=30, l=70),
            xaxis=dict(
                title='<b></b>',
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=True,
                linecolor='white',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='#404040'
                )
            ),
            yaxis=dict(
                title='<b></b>',
                visible=True,
                color='white',
                showline=False,
                showgrid=False,
                showticklabels=False,  # Ẩn giá trị trên trục tung
                linecolor='white',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Calibri',
                    size=15,
                    color='#404040'
                )
            )
        )
        
        # Tùy chỉnh màu sắc của các điểm (dấu chấm) thành màu vàng
        fig.update_traces(
            marker=dict(color='#90c9ef', size=10),  # Màu vàng và kích thước điểm
            textposition='top center',  # Vị trí hiển thị giá trị
            line=dict(color='#d90ba9'))  # Màu đường line (nếu cần)
    else:
        # Nếu không có dữ liệu, hiển thị biểu đồ trống với thông báo
        fig = px.line(title=f"Doanh thu thuần của {select_stock} (2020-2024)")
    
    return fig

# Chạy ứng dụng
if __name__ == '__main__':
    app.run_server(debug=True)
