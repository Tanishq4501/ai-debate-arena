import google.generativeai as genai
from memory_manager import save_to_memory
import random
from colorama import Fore, Style
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB7-jgzzXD-N_E0SPsqEcQkSWjt57xEe04") #replace with your key
genai.configure(api_key=API_KEY)

class DebateAgent:
    def __init__(self, name, role, persona_style, topic):
        self.name = name
        self.role = role  # "Pro" or "Con"
        self.persona_style = persona_style
        self.topic = topic
        self.goal = f"Defend the {role} side and win the debate on '{topic}'"
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.9,
                max_output_tokens=500,
                candidate_count=1
            )
        )
        self.history = []
        self.opponent_arguments = []
        self.score = 0
        self.color = self._assign_color()
        self.statement_count = 0
        self.retry_count = 0
        self.max_retries = 3

    def _assign_color(self):
        """Assign colors based on persona for better visualization"""
        colors = {
            "Formal Analyst": Fore.BLUE,
            "Emotional Activist": Fore.RED,
            "Sarcastic Rebel": Fore.YELLOW,
            "Curious Thinker": Fore.GREEN,
            "Strategic Debater": Fore.MAGENTA,
            "Evidence Expert": Fore.CYAN
        }
        return colors.get(self.name, Fore.WHITE)

    def track_arguments(self, debate_history):
        """Track and categorize opponent arguments for strategic responses"""
        try:
            self.opponent_arguments = []
            for entry in debate_history:
                if entry.get('agent') != self.name and 'text' in entry:
                    self.opponent_arguments.append({
                        'agent': entry['agent'],
                        'text': entry['text'],
                        'type': entry.get('type', 'unknown'),
                        'timestamp': entry.get('timestamp', None)
                    })
            logger.debug(f"Tracked {len(self.opponent_arguments)} opponent arguments for {self.name}")
            return self.opponent_arguments
        except Exception as e:
            logger.error(f"Error tracking arguments for {self.name}: {e}")
            return []

    def generate_strategic_question(self, debate_history):
        """Generate targeted questions based on debate flow"""
        try:
            recent_history = debate_history[-3:] if len(debate_history) > 3 else debate_history
            history_text = "\n".join([f"{entry.get('agent', 'Unknown')}: {entry.get('text', '')}" for entry in recent_history])
            
            prompt = f"""
            You are {self.name}, a {self.persona_style} debater arguing the {self.role} side of "{self.topic}".
            
            Recent debate exchange:
            {history_text}
            
            Generate a strategic question that:
            1. Targets a weakness in your opponent's recent argument
            2. Forces them to defend a vulnerable position
            3. Can be answered in 2-3 sentences
            4. Maintains your {self.persona_style} style
            5. Advances your {self.role} position on {self.topic}
            
            Keep it direct, challenging, and under 50 words.
            """
            return self._generate_response(prompt, stream=False)
        except Exception as e:
            logger.error(f"Error generating question for {self.name}: {e}")
            return f"Can you explain how your position on {self.topic} addresses the key concerns raised?"

    def answer_question(self, question):
        """Answer questions while maintaining persona and position"""
        try:
            prompt = f"""
            You are {self.name}, a {self.persona_style} debater arguing the {self.role} side of "{self.topic}".
            
            Answer this question directly and convincingly:
            "{question}"
            
            Requirements:
            1. Maintain your {self.persona_style} style
            2. Defend your {self.role} position strongly
            3. Be direct and substantive
            4. Keep response to 2-3 sentences (under 100 words)
            5. Avoid evasion - address the question head-on
            
            Provide a clear, confident answer.
            """
            return self._generate_response(prompt, stream=False)
        except Exception as e:
            logger.error(f"Error answering question for {self.name}: {e}")
            return f"From the {self.role} perspective on {self.topic}, the evidence clearly supports my position on this important question."

    def evaluate_answer(self, question, answer, debate_history):
        """Analyze if the answer properly addressed the question"""
        try:
            prompt = f"""
            Evaluate this debate exchange objectively:
            
            Question: {question}
            Answer: {answer}
            
            Rate on scale 1-5 and determine evasion:
            1. Directness: Did they answer the question directly? (1-5)
            2. Logic: Was the reasoning sound? (1-5)
            3. Evasion: Did they avoid addressing the core question? (Yes/No)
            
            Format exactly as: "Directness: X/5, Logic: X/5, Evasion: Yes/No"
            Then add one sentence analysis.
            """
            return self._generate_response(prompt, stream=False)
        except Exception as e:
            logger.error(f"Error evaluating answer for {self.name}: {e}")
            return "Directness: 3/5, Logic: 3/5, Evasion: No\nThe response addressed the question adequately."

    def generate_followup(self, question, answer, evaluation):
        """Generate follow-up based on answer quality"""
        try:
            prompt = f"""
            Previous exchange:
            Question: {question}
            Answer: {answer}
            Evaluation: {evaluation}
            
            As {self.name} ({self.persona_style}), generate either:
            - A clarifying follow-up if they were evasive or unclear
            - A counter-point if their answer was weak
            - Brief acknowledgment if they answered well
            
            Keep it under 30 words and maintain your persona.
            """
            return self._generate_response(prompt, stream=False)
        except Exception as e:
            logger.error(f"Error generating followup for {self.name}: {e}")
            return "That raises additional points worth exploring further."
            
    def get_opening_statement(self):
        """Generate compelling opening statement"""
        try:
            prompt = f"""
            You are {self.name}, a {self.persona_style} debater in a formal debate.
            
            Topic: {self.topic}
            Your Position: {self.role}
            Your Style: {self.persona_style}
            
            Create a compelling opening statement (4-5 sentences, under 150 words) that:
            1. Clearly states your {self.role} position
            2. Presents 2-3 main arguments
            3. Captures attention with your {self.persona_style} style
            4. Sets the tone for your debate strategy
            5. Is persuasive and memorable
            
            Be confident, engaging, and true to your persona.
            """
            response = self._generate_response(prompt, stream=False)
            self.statement_count += 1
            return response
        except Exception as e:
            logger.error(f"Error generating opening for {self.name}: {e}")
            return f"As {self.name}, I firmly support the {self.role} position on {self.topic}. The evidence and reasoning clearly demonstrate why this stance is correct, and I'll prove this through logical arguments and compelling evidence."
    
    def get_rebuttal(self, debate_history, current_round):
        """Generate strategic rebuttal based on debate flow"""
        try:
            # Get recent opponent statements
            opponent_points = []
            for entry in debate_history[-4:]:  # Last 4 entries
                if entry.get('agent') != self.name and entry.get('text'):
                    opponent_points.append(f"{entry['agent']}: {entry['text']}")
            
            recent_opponent_text = "\n".join(opponent_points) if opponent_points else "No recent opponent statements available"
            
            prompt = f"""
            Topic: {self.topic}
            Your Role: {self.role}
            Your Style: {self.persona_style}
            Round: {current_round}
            
            Recent opponent arguments:
            {recent_opponent_text}
            
            Generate a strategic rebuttal (4-5 sentences, under 150 words) that:
            1. Directly addresses at least one opponent point
            2. Strengthens your {self.role} position
            3. Maintains your {self.persona_style} style
            4. Introduces new evidence or reasoning
            5. Anticipates potential counter-arguments
            
            Be persuasive, focused, and strategic.
            """
            
            response = self._generate_response(prompt, stream=False)
            self.statement_count += 1
            return response
        except Exception as e:
            logger.error(f"Error generating rebuttal for {self.name}: {e}")
            return f"The arguments presented overlook key aspects of {self.topic}. From the {self.role} perspective, the evidence clearly points to a different conclusion that better addresses the core issues at stake."

    def get_closing_statement(self, debate_history):
        """Generate powerful closing statement"""
        try:
            # Summarize own key points
            own_statements = [entry.get('text', '') for entry in debate_history 
                            if entry.get('agent') == self.name and entry.get('text')]
            
            key_statements = "\n".join(own_statements[-3:]) if own_statements else "No previous statements available"
            
            prompt = f"""
            Topic: {self.topic}
            Your Role: {self.role}
            Your Style: {self.persona_style}
            
            Your key arguments in this debate:
            {key_statements}
            
            Generate a powerful closing statement (5-6 sentences, under 200 words) that:
            1. Summarizes your strongest arguments
            2. Reinforces your {self.role} position decisively
            3. Addresses key opponent weaknesses
            4. Leaves a lasting impression
            5. Maintains your {self.persona_style} style
            6. Calls for acceptance of your position
            
            This is your final chance - make it memorable and convincing.
            """
            
            response = self._generate_response(prompt, stream=False)
            self.statement_count += 1
            return response
        except Exception as e:
            logger.error(f"Error generating closing for {self.name}: {e}")
            return f"In conclusion, the {self.role} position on {self.topic} is clearly supported by the evidence and reasoning I've presented throughout this debate. The path forward is evident and compelling."
    
    def save_statement(self, session_id, statement_type, content):
        """Save statement to database with session context"""
        try:
            success = save_to_memory(session_id, self.name, statement_type, {
                "content": content,
                "role": self.role,
                "persona": self.persona_style,
                "statement_number": self.statement_count,
                "topic": self.topic
            })
            if success:
                logger.debug(f"Saved {statement_type} for {self.name}")
            else:
                logger.warning(f"Failed to save {statement_type} for {self.name}")
        except Exception as e:
            logger.error(f"Error saving statement for {self.name}: {e}")
    
    def remember_conversation(self, session_id, debate_history):
        """Store key debate points in memory"""
        try:
            # Extract key points from recent history
            key_points = []
            keywords = ['important', 'crucial', 'key', 'evidence', 'proof', 'shows', 'demonstrates', 'because', 'therefore']
            
            for entry in debate_history[-5:]:  # Last 5 entries
                text = entry.get('text', '').lower()
                if any(keyword in text for keyword in keywords):
                    key_points.append(entry.get('text', ''))
            
            if key_points:
                self.save_statement(session_id, "key_points", {
                    "points": key_points,
                    "summary": " | ".join(key_points)[:500],  # Limit summary length
                    "extracted_at": len(debate_history)
                })
                logger.debug(f"Remembered {len(key_points)} key points for {self.name}")
        except Exception as e:
            logger.error(f"Error remembering conversation for {self.name}: {e}")
        
    def _generate_response(self, prompt, stream=False, max_retries=3):
        """Generate response using Gemini API with robust error handling"""
        final_response = ""
        
        for attempt in range(max_retries):
            try:
                if stream:
                    print(f"{self.color}{self.name}: ", end="", flush=True)
                    response_stream = self.model.generate_content(prompt, stream=True)
                    for chunk in response_stream:
                        if hasattr(chunk, "text") and chunk.text:
                            print(chunk.text, end="", flush=True)
                            final_response += chunk.text
                    print(Style.RESET_ALL)
                    return final_response.strip()
                else:
                    response = self.model.generate_content(prompt)
                    if hasattr(response, 'text') and response.text:
                        return response.text.strip()
                    else:
                        raise ValueError("Empty response from API")
                        
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {self.name}: {e}")
                if attempt == max_retries - 1:
                    # Return fallback response based on role and topic
                    fallback = self._generate_fallback_response(prompt)
                    if stream:
                        print(f"{self.color}{fallback}{Style.RESET_ALL}")
                    return fallback
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt):
        """Generate fallback response when API fails"""
        fallback_responses = {
            "opening": f"As {self.name}, I strongly support the {self.role} position on {self.topic}. The evidence clearly demonstrates the validity of this stance, and I will present compelling arguments to support this view.",
            "rebuttal": f"The opposing arguments fail to address the core issues of {self.topic}. From the {self.role} perspective, the evidence points to a different conclusion.",
            "closing": f"In conclusion, the {self.role} position on {self.topic} is well-founded and supported by sound reasoning.",
            "question": f"How do you reconcile your position with the evidence regarding {self.topic}?",
            "answer": f"From the {self.role} standpoint, the answer is clear based on the evidence."
        }
        
        # Try to match prompt type
        for key, response in fallback_responses.items():
            if key in prompt.lower():
                return response
        
        return f"[{self.name}]: I maintain my {self.role} position on {self.topic} based on the evidence presented."

    def get_performance_metrics(self):
        """Get performance metrics for scoring"""
        return {
            "statements_made": self.statement_count,
            "arguments_tracked": len(self.opponent_arguments),
            "role": self.role,
            "persona": self.persona_style,
            "topic": self.topic,
            "retry_count": self.retry_count

        }
