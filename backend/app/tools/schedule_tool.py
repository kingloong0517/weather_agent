from typing import Any, Dict
from .base import BaseTool


def schedule_tool(time: str, event: str) -> Dict[str, Any]:
    """
    设置日程提醒
    
    Args:
        time: 时间，如 "今天下午3点"、"明天早上9点"
        event: 事件，如 "开会"、"购物"
        
    Returns:
        提醒设置结果
    """
    # Mock 数据
    return {
        "status": "ok",
        "event": event,
        "time": time,
        "message": f"已成功设置{time}的{event}提醒"
    }


class ScheduleTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="schedule_reminder",
            description="设置日程提醒"
        )

    def execute(self, time: str, event: str, **kwargs) -> Dict[str, Any]:
        return schedule_tool(time, event)
