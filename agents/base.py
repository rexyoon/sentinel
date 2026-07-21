# agents/base.py — 모든 AI 직원(에이전트)이 지켜야 할 공통 계약(인터페이스).
from abc import ABC, abstractmethod


class Agent(ABC):
    name: str  # 직원 이름 (예: "기획자", "디자이너")

    @abstractmethod
    def run(self, task: str) -> str:
        """작업을 받아 처리하고, 산출물 경로(또는 결과 요약)를 돌려준다."""
        ...