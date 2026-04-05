import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Entity:
    name: str
    value: str
    start: int = 0
    end: int = 0


class EntityExtractor:
    DATE_PATTERNS = [
        (r"今天", "今天"),
        (r"明天", "明天"),
        (r"后天", "后天"),
        (r"大后天", "大后天"),
        (r"昨天", "昨天"),
        (r"前天", "前天"),
        (r"本周", "本周"),
        (r"下周", "下周"),
        (r"上个月", "上个月"),
        (r"下个月", "下个月"),
        (r"(\d{1,2})月(\d{1,2})[日号]", "specific_date"),
        (r"(\d{4})年(\d{1,2})月(\d{1,2})[日号]?", "full_date"),
        (r"周[一二三四五六日天]", None),
        (r"星期[一二三四五六日天]", None),
    ]

    TIME_PATTERNS = [
        (r"早上", "早上"),
        (r"上午", "上午"),
        (r"中午", "中午"),
        (r"下午", "下午"),
        (r"晚上", "晚上"),
        (r"傍晚", "傍晚"),
        (r"凌晨", "凌晨"),
        (r"(\d{1,2})点", "hour"),
        (r"(\d{1,2}):(\d{2})", "time"),
    ]

    LOCATION_STOPWORDS = ["的", "了", "吗", "呢", "吧", "啊", "呀"]

    MAJOR_CITIES = [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
        "重庆", "武汉", "西安", "天津", "青岛", "大连", "厦门", "长沙",
        "郑州", "济南", "福州", "哈尔滨", "沈阳", "长春", "昆明", "贵阳",
        "南宁", "海口", "三亚", "拉萨", "乌鲁木齐", "兰州", "银川", "西宁",
        "呼和浩特", "石家庄", "太原", "合肥", "南昌", "武汉", "珠海", "东莞"
    ]

    def __init__(self, default_city: str = "北京"):
        self.default_city = default_city

    def extract_date(self, text: str) -> Optional[str]:
        for pattern, label in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                if label == "specific_date":
                    return f"{match.group(1)}月{match.group(2)}日"
                elif label == "full_date":
                    return f"{match.group(1)}年{match.group(2)}月{match.group(3)}日"
                elif label is None:
                    return match.group(0)
                else:
                    return label
        return None

    def extract_time(self, text: str) -> Optional[str]:
        for pattern, label in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                if label == "hour":
                    return f"{match.group(1)}点"
                elif label == "time":
                    return f"{match.group(1)}:{match.group(2)}"
                else:
                    return label
        return None

    def extract_location(self, text: str) -> str:
        text_clean = text.replace(" ", "").replace("　", "")
        for city in self.MAJOR_CITIES:
            if city in text_clean:
                return city

        location_patterns = [
            r"(.{2,10})(?:的|今天|明天|后天|天气|气温|温度)",
            r"在(.{2,10})(?:的|今天|明天|后天|天气|气温|温度)",
            r"(.{2,10})天气",
            r"(.{2,10})气温",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                for stopword in self.LOCATION_STOPWORDS:
                    location = location.replace(stopword, "")
                location = location.strip()
                if location and len(location) >= 2:
                    return location

        return self.default_city

    def extract_all(self, text: str) -> Dict[str, str]:
        entities = {}

        date = self.extract_date(text)
        if date:
            entities["date"] = date

        time = self.extract_time(text)
        if time:
            entities["time"] = time

        entities["location"] = self.extract_location(text)

        return entities
