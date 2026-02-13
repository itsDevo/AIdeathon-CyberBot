from utils.ai_interact import set_ai_model, generate_questions, evaluate_response
import config

from json.decoder import JSONDecodeError


class Bot:
    def __init__(self, model=config.GROQ_LLAMA3_1_70B):
        # Initialize AI model, set by default to Llama 3.1 70B
        self.llm, self.settings, self.limits = set_ai_model(model=model)
        # Set message history, add welcome message
        self.message_history = [("llm", config.SYSTEM_MESSAGES["welcome"])]
        # Generate questions, set latest question
        while True:
            try:
                self.questions, self.limits = generate_questions(llm=self.llm, settings=self.settings,
                                                                 limits=self.limits)
                print("No error")
                break
            except JSONDecodeError as error:
                print("Error caught:", error)
                continue
        self.latest_question = None
        self.grade = 0

    def welcome_message(self):
        # To be used only once, at the beginning
        if self.latest_question is None:
            return self.message_history
        return None

    def next_question(self):
        # Get next question from the list, and add it to the message history
        if len(self.questions) != 0:
            self.latest_question = self.questions.pop(0)
            self.message_history.append(("llm", self.latest_question))
            return self.message_history
        else:
            return [("llm", "Thank you for participating in the quiz!")]

    def generate_feedback(self, user_response):
        # Evaluate user response, and add it to the message history
        self.message_history.append(("user", user_response))
        llm_feedback, self.limits, passed = evaluate_response(llm=self.llm,
                                                              settings=self.settings,
                                                              limits=self.limits,
                                                              question=self.latest_question,
                                                              user_response=user_response)
        if passed is True:
            self.grade += 1
        elif passed is None:
            self.grade += 0.5
        self.message_history.append(("llm", llm_feedback))
        return self.message_history

    def get_final_grade(self):
        return self.grade
