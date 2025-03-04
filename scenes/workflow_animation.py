# manim -pql scenes/workflow_animation.py WorkflowAnimation

import json

from manim import *

Text.set_default(font="lato", t2f={" ": "Arial Expanded"})


class WorkflowAnimation(Scene):
    def construct(self):
        # Load message flow data
        with open("langgraph_files/workflow/workflow_simplified.json", "r") as f:
            data = json.load(f)

        messages = data["messages"]

        # Title
        title = Text(
            "LLM PIPELINE IN `GUESS MY NUMBER` GAME",
            font_size=24,
            color=WHITE,
        ).to_corner(UL)
        self.add(title)

        # Define positions for nodes in a hierarchical layout
        positions = {
            "human": LEFT * 3 + UP * 1.5,  # Top left,
            "get_range": LEFT * 2.5 + DOWN * 2,  # Bottom left
            "make_guess": RIGHT * 2.5 + DOWN * 2,  # Bottom right
            "get_feedback": RIGHT * 3 + UP * 1.5,  # Top right
            "adjust_range": LEFT * 0.1 + UP * 0.1,  # Middle center
        }

        # Create nodes with initial size
        node_size = 0.6
        active_size = 0.8  # Size when active

        nodes = {
            "human": Circle(radius=node_size, color=BLUE, fill_opacity=0.5),
            "get_range": Circle(radius=node_size, color=YELLOW, fill_opacity=0.5),
            "make_guess": Circle(radius=node_size, color=YELLOW, fill_opacity=0.5),
            "get_feedback": Circle(radius=node_size, color=YELLOW, fill_opacity=0.5),
            "adjust_range": Circle(radius=node_size, color=YELLOW, fill_opacity=0.5),
        }

        # Position nodes
        for key, node in nodes.items():
            node.move_to(positions[key])

        # Labels
        labels = {
            "human": Text("Human", font_size=20),
            "get_range": Text("get_range", font_size=20, color=YELLOW),
            "make_guess": Text("make_guess", font_size=20, color=YELLOW),
            "get_feedback": Text("get_feedback", font_size=20, color=YELLOW),
            "adjust_range": Text("adjust_range", font_size=20, color=YELLOW),
        }

        for key, label in labels.items():
            if key in ("human", "get_range"):
                label.next_to(nodes[key], LEFT)
            elif key in ("make_guess", "get_feedback"):
                label.next_to(nodes[key], RIGHT)
            else:
                label.next_to(nodes[key], UP)

        # Display nodes and labels
        self.add(*nodes.values(), *labels.values())

        # Define edges
        edges = {
            ("human", "get_range"),
            ("get_range", "make_guess"),
            ("make_guess", "get_feedback"),
            ("get_feedback", "human"),
            ("human", "get_feedback"),
            ("get_feedback", "adjust_range"),
            ("adjust_range", "make_guess"),
        }

        arrows = []
        for start, end in edges:
            start_pos = nodes[start].get_center()
            end_pos = nodes[end].get_center()

            # Compute direction vector
            direction = (end_pos - start_pos) / np.linalg.norm(end_pos - start_pos)

            # Adjust start and end points to be on the border
            start_point = start_pos + direction * nodes[start].radius * 1.3
            end_point = end_pos - direction * nodes[end].radius * 1.3

            # Create arrow with adjusted points
            arrow = Arrow(start_point, end_point, buff=0.1, color=DARK_GRAY)

            arrows.append(arrow)  # Store arrow reference
            self.add(arrow)
            self.bring_to_back(arrow)

        # Initialize counters
        llm_counter = 0
        llm_counter_text = Text(
            f"LLM REQUESTS: {llm_counter}", font_size=20, color=YELLOW
        ).to_corner(UR)
        self.add(llm_counter_text)

        # Actual messages animation code
        previous_node = None
        previous_msg_type = None
        prev_text = None

        for message in messages:
            msg_type = message["type"]
            msg_content = message["content"]
            target_node = nodes[msg_type]

            text = Text(msg_content, font_size=18, color=WHITE)

            if previous_node:
                # compute arrow position
                start_pos = nodes[previous_msg_type].get_center()
                end_pos = nodes[msg_type].get_center()
                direction = (end_pos - start_pos) / np.linalg.norm(end_pos - start_pos)
                start_point = (
                    start_pos + direction * nodes[previous_msg_type].radius * 1.3
                )
                end_point = end_pos - direction * nodes[msg_type].radius * 1.3

                # arrow animation
                msg_arrow = Arrow(start_point, end_point, buff=0.1, color=WHITE)
                self.bring_to_front(msg_arrow)
                self.play(Create(msg_arrow))

                # fade out
                self.play(
                    FadeOut(msg_arrow),
                    FadeOut(prev_text),
                    target_node.animate.scale(active_size / node_size),
                )
            else:
                self.play(
                    target_node.animate.scale(active_size / node_size)
                )  # Decrease size

            if msg_type in ("human", "get_feedback"):
                text.next_to(target_node, UP * 0.3)
            else:
                text.next_to(target_node, DOWN)

            self.add(text)

            # Update automation counter if the message is from AI or Tool
            if msg_type not in {"human"}:
                llm_counter += 1
                new_counter_text = Text(
                    f"LLM REQUESTS: {llm_counter}", font_size=20, color=YELLOW
                ).to_corner(UR)
                self.play(ReplacementTransform(llm_counter_text, new_counter_text))
                llm_counter_text = new_counter_text

            self.wait(0.3)
            self.play(
                target_node.animate.scale(node_size / active_size),  # Increase size
            )

            previous_node = msg_type
            previous_msg_type = msg_type
            prev_text = text

        self.wait(0.1)

        self.play(
            FadeOut(*nodes.values()),
            FadeOut(*labels.values()),
            FadeOut(*arrows),
            FadeOut(llm_counter_text),
            FadeOut(text),
            FadeOut(msg_arrow),
            FadeOut(target_node),
            FadeOut(title),
        )
