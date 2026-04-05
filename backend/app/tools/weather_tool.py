from typing import Any, Dict
import requests
from .base import BaseTool


def weather_tool(date: str, location: str) -> Dict[str, Any]:
    """
    查询指定日期和地点的天气信息
    
    Args:
        date: 日期，如 "今天"、"明天"
        location: 地点，如 "北京"、"上海"
        
    Returns:
        天气信息字典
    """
    # 高德天气 API 配置
    api_key = "5aa7eda4eb4d7556c07fda20eb13907c"  # 高德 API Key
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    # 构建请求参数
    params = {
        "key": api_key,
        "city": location,
        "extensions": "base",  # base: 基础天气, all: 详细天气
        "output": "json"
    }
    
    try:
        # 发送请求
        print(f"请求天气 API: {base_url}")
        print(f"参数: {params}")
        response = requests.get(base_url, params=params, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        data = response.json()
        
        # 检查响应状态
        if data.get("status") != "1":
            print(f"API 错误: {data.get('info')}")
            return {
                "weather": "未知",
                "advice": "无建议",
                "date": date,
                "location": location
            }
        
        # 解析天气数据
        forecasts = data.get("lives", [])
        if not forecasts:
            print("未获取到天气数据")
            return {
                "weather": "未知",
                "advice": "无建议",
                "date": date,
                "location": location
            }
        
        weather_info = forecasts[0]
        weather = weather_info.get("weather", "未知")
        temperature = weather_info.get("temperature", "未知")
        
        print(f"天气数据: {weather_info}")
        
        # 生成建议
        advice = ""
        if "雨" in weather:
            advice = "建议带伞"
        elif temperature != "未知" and int(temperature) > 30:
            advice = "天气炎热，注意防暑"
        elif temperature != "未知" and int(temperature) < 10:
            advice = "天气寒冷，注意保暖"
        else:
            advice = "天气适宜，适合外出"
        
        return {
            "weather": weather,
            "advice": advice,
            "date": date,
            "location": location,
            "temperature": f"{temperature}°C"
        }
        
    except Exception as e:
        print(f"天气查询错误: {e}")
        import traceback
        traceback.print_exc()
        # 出错时返回默认值
        return {
            "weather": "未知",
            "advice": "无建议",
            "date": date,
            "location": location
        }


class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="weather_query",
            description="查询指定城市的天气信息"
        )

    def execute(self, date: str, location: str, **kwargs) -> Dict[str, Any]:
        return weather_tool(date, location)
