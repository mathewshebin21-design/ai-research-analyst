 def analyze_question(self, query: str, persona: str = "Senior Strategy Consultant") -> StrategicAnalysis:
        # Inject the selected persona into the prompt
        system_prompt = (
            f"You are an elite {persona}. "
            "Analyze business opportunities with extreme rigor and adopt the tone, focus, and priorities of this persona. "
            "CRITICAL: The 'recommendation' field MUST strictly be one of: "
            "'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'."
        )

        user_prompt = f"Conduct a full strategic market assessment for the following inquiry:\n\n'{query}'"

        response = self.client.models.generate_content(
            model=self.selected_model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StrategicAnalysis,
            ),
        )

        return StrategicAnalysis.model_validate_json(response.text)