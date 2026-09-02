import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EmotionManager:
    """内部感情状態管理"""
    
    def __init__(self):
        self.state = {
            'affection': 0.5,
            'trust': 0.5,
            'mood': 0.5,
            'energy': 0.7,
            'loneliness': 0.3,
            'playfulness': 0.5,
            'curiosity': 0.6,
            'boredom': 0.2
        }
        self.last_update = datetime.now()
    
    def update(self, changes: Dict[str, float]):
        """感情を更新"""
        for key, value in changes.items():
            if key in self.state:
                self.state[key] = max(0.0, min(1.0, self.state[key] + value))
        self.last_update = datetime.now()
        logger.debug(f"Emotion updated: {self.state}")
    
    def set_state(self, key: str, value: float):
        """感情値を直接設定"""
        if key in self.state:
            self.state[key] = max(0.0, min(1.0, value))
            self.last_update = datetime.now()
    
    def get_state(self) -> Dict[str, float]:
        """現在の感情状態を取得"""
        return self.state.copy()
    
    def get_expression(self) -> Dict[str, Any]:
        """感情に基づいてアバター表情を決定"""
        mood = self.state['mood']
        energy = self.state['energy']
        
        if energy < 0.3:
            return {
                'name': 'tired',
                'brow_angle': -10,
                'eye_openness': 0.4,
                'mouth_shape': 0.2
            }
        elif mood > 0.8 and energy > 0.7:
            return {
                'name': 'happy',
                'brow_angle': 15,
                'eye_openness': 0.9,
                'mouth_shape': 0.7
            }
        elif mood < 0.3:
            return {
                'name': 'sad',
                'brow_angle': -20,
                'eye_openness': 0.7,
                'mouth_shape': -0.5
            }
        else:
            return {
                'name': 'neutral',
                'brow_angle': 0,
                'eye_openness': 1.0,
                'mouth_shape': 0.0
            }

emotion_manager = EmotionManager()
