# manim -pql scenes/agent_flow_animation.py AgentFlowAnimation

import json

from manim import *


Text.set_default(font="lato", t2f={" ": "Arial Expanded"})


class AgentFlowAnimation(Scene):
    def construct(self):
        # Load message flow data
        with open("langgraph_files/agent/workflow_with_args.json", "r") as f:
            data = json.load(f)

        messages = data["messages"]

        # Title
        title = Text(
            "AGENT FLOW IN `GUESS MY NUMBER` GAME",
            font_size=24,
            color=WHITE,
        ).to_corner(UL)
        self.add(title)

        # Define positions for nodes in a triangle layout
        positions = {
            "start": LEFT * 3 + DOWN * 2,  # Bottom left (Human)
            "assistant": UP * 1.2,  # Top center (AI)
            "tool": RIGHT * 3 + DOWN * 2,  # Bottom right (Tool)
        }

        # Create nodes with initial size
        node_size = 0.6
        active_size = 0.8  # Size when active

        start_node = Circle(radius=node_size, color=BLUE, fill_opacity=0.5).move_to(
            positions["start"]
        )
        ai_node = Circle(radius=node_size, color=GREEN, fill_opacity=0.5).move_to(
            positions["assistant"]
        )
        tool_node = Circle(radius=node_size, color=YELLOW, fill_opacity=0.5).move_to(
            positions["tool"]
        )

        # Labels for nodes
        start_label = Text("Human", font_size=20).next_to(start_node, UP)
        ai_label = Text("Assistant", font_size=20).next_to(ai_node, DOWN)
        tool_label = Text("Tools", font_size=20).next_to(tool_node, UP)

        # Display objects
        self.add(start_node, ai_node, tool_node, start_label, ai_label, tool_label)

        # Initialize counters
        llm_counter = 0
        llm_counter_text = Text(
            f"LLM REQUESTS: {llm_counter}", font_size=20, color=YELLOW
        ).to_corner(UR)
        self.add(llm_counter_text)

        # Define edges
        node_map = {"human": start_node, "ai": ai_node, "tool": tool_node}

        arrow_paths = {
            ("human", "ai"): (positions["start"], positions["assistant"]),
            ("ai", "human"): (positions["assistant"], positions["start"]),
            ("ai", "tool"): (positions["assistant"], positions["tool"]),
            ("tool", "ai"): (positions["tool"], positions["assistant"]),
            ("tool", "human"): (positions["tool"], positions["start"]),
            ("human", "tool"): (positions["start"], positions["tool"]),
        }

        # Actual messages animation code
        previous_node = None
        previous_msg_type = None
        prev_text = None

        for message in messages:
            msg_type = message["type"]
            target_node = node_map.get(msg_type)

            if msg_type == "tool":
                tool_name = message["name"]
                tool_args = message["content"]

                tool_text = Text(f"RESPONSE: {tool_name}", font_size=18, color=YELLOW)
                args_text = Text(tool_args, font_size=16).next_to(tool_text, DOWN)

                multi_text = VGroup(tool_text, args_text)
                multi_text.arrange(DOWN)

            elif msg_type == "ai":
                if len(message.get("tool_calls", [])) > 0:
                    for tool_call in message["tool_calls"]:
                        tool_name_ai = tool_call["name"]

                        tool_text_ai = Text(
                            f"CALL: {tool_name_ai}", font_size=18, color=YELLOW
                        )
                        multi_text = VGroup(tool_text_ai)

                else:
                    content = message["content"]
                    msg_text = Text(content, font_size=18)
                    multi_text = VGroup(msg_text)

            elif msg_type == "human":
                content = message["content"]
                msg_text = Text(content, font_size=18)
                multi_text = VGroup(msg_text)

            # play action below
            if previous_node:
                # compute arrow position
                start_pos, end_pos = arrow_paths[(previous_msg_type, msg_type)]
                direction = (end_pos - start_pos) / np.linalg.norm(end_pos - start_pos)
                start_point = start_pos + direction * previous_node.radius
                end_point = end_pos - direction * target_node.radius

                # arrow animation
                msg_arrow = Arrow(start_point, end_point, buff=0.1, color=WHITE)
                self.bring_to_front(msg_arrow)
                self.play(
                    Create(msg_arrow),
                )

                # fade out
                self.play(
                    FadeOut(msg_arrow),
                    FadeOut(prev_text),
                    target_node.animate.scale(active_size / node_size),
                )
            else:
                self.play(
                    target_node.animate.scale(active_size / node_size)  # Decrease size
                )

            # show message under the node
            if msg_type == "tool":
                self.add(multi_text.next_to(node_map.get("tool"), DOWN * 1.2))
            elif msg_type == "ai":
                self.add(multi_text.next_to(node_map.get("ai"), UP * 1.2))
            elif msg_type == "human":
                self.add(multi_text.next_to(node_map.get("human"), DOWN * 1.2))

            # Update automation counter if the message is from AI or Tool
            if msg_type in {"ai", "tool"}:
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

            previous_node = target_node
            previous_msg_type = msg_type
            prev_text = multi_text

        self.wait(0.1)

        # fade out all objects
        self.play(
            FadeOut(start_node),
            FadeOut(ai_node),
            FadeOut(tool_node),
            FadeOut(start_label),
            FadeOut(ai_label),
            FadeOut(tool_label),
            FadeOut(llm_counter_text),
            FadeOut(multi_text),
            FadeOut(title),
        )


if __name__ == "__main__":
    scene = AgentFlowAnimation()
    scene.render()
