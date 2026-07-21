# run.py — 프로젝트 진입점. 터미널 러너로 회사를 돌린다.
#   실행: python run.py   (프로젝트 루트에서)
#
# 나중에 슬랙/디스코드로 돌리려면 이 한 줄만 바꾸면 된다:
#   from runners.slack_bot import main   (에이전트는 안 건드림)
from runners.console import main

if __name__ == "__main__":
    main()
