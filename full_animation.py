# manim -pql full_animation.py FullAnimation
# manim -pqh full_animation.py FullAnimation --fps=120

from manim import *

from scenes.agent_flow_animation import AgentFlowAnimation
from scenes.workflow_animation import WorkflowAnimation


class FullAnimation(Scene):
    def construct(self):
        AgentFlowAnimation.construct(self)
        WorkflowAnimation.construct(self)
