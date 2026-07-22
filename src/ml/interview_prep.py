import random
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


@dataclass
class InterviewQuestion:
    question: str
    category: str
    difficulty: str
    answer: str
    tips: List[str] = field(default_factory=list)
    expected_duration: str = "2-3 minutes"


class InterviewPrepModule:
    def __init__(self):
        self.questions_db = self._build_questions_database()

    def _build_questions_database(self) -> Dict[str, List[InterviewQuestion]]:
        return {
            "technical_python": [
                InterviewQuestion(
                    question="What is the difference between a list and a tuple in Python?",
                    category="Python",
                    difficulty="Easy",
                    answer=(
                        "Lists are mutable (can be modified after creation) while "
                        "tuples are immutable. Lists use square brackets [], tuples use (). "
                        "Lists are slower due to mutability overhead; tuples are faster. "
                        "Tuples can be used as dictionary keys; lists cannot."
                    ),
                    tips=["Give real-world examples", "Mention memory efficiency", "Discuss use cases"],
                ),
                InterviewQuestion(
                    question="Explain the difference between深copy and shallow copy.",
                    category="Python",
                    difficulty="Medium",
                    answer=(
                        "Shallow copy creates a new object but references the same inner objects. "
                        "Deep copy creates a new object and recursively copies all nested objects. "
                        "Use copy.copy() for shallow and copy.deepcopy() for deep copy."
                    ),
                    tips=["Draw diagrams", "Show examples with nested lists", "Mention common pitfalls"],
                ),
                InterviewQuestion(
                    question="What are decorators in Python?",
                    category="Python",
                    difficulty="Medium",
                    answer=(
                        "Decorators are functions that modify the behavior of other functions. "
                        "They use the @decorator syntax. They follow the Open/Closed principle. "
                        "Common uses: logging, authentication, caching, timing."
                    ),
                    tips=["Show a simple example", "Explain @ syntax sugar", "Mention real use cases"],
                ),
                InterviewQuestion(
                    question="What is the GIL in Python?",
                    category="Python",
                    difficulty="Hard",
                    answer=(
                        "The Global Interpreter Lock (GIL) is a mutex that allows only one thread "
                        "to execute Python bytecode at a time. It simplifies memory management "
                        "but limits true parallelism for CPU-bound tasks. Use multiprocessing "
                        "or C extensions for parallel processing."
                    ),
                    tips=["Explain why it exists", "Discuss workarounds", "Mention multiprocessing vs threading"],
                ),
                InterviewQuestion(
                    question="How does memory management work in Python?",
                    category="Python",
                    difficulty="Hard",
                    answer=(
                        "Python uses reference counting and a cyclic garbage collector. "
                        "Each object has a reference count; when it drops to zero, the object "
                        "is deallocated. The gc module handles cyclic references. "
                        "Python also uses memory pools (pymalloc) for small objects."
                    ),
                    tips=["Mention reference counting", "Discuss garbage collector", "Talk about memory pools"],
                ),
            ],
            "technical_java": [
                InterviewQuestion(
                    question="What is the difference between an interface and an abstract class?",
                    category="Java",
                    difficulty="Easy",
                    answer=(
                        "Abstract classes can have constructors, state (fields), and both "
                        "abstract and concrete methods. Interfaces (pre-Java 8) only had "
                        "abstract methods. Since Java 8, interfaces can have default and "
                        "static methods. A class can implement multiple interfaces but "
                        "extend only one abstract class."
                    ),
                    tips=["Give examples", "Mention multiple inheritance", "Discuss when to use each"],
                ),
                InterviewQuestion(
                    question="Explain the HashMap working mechanism in Java.",
                    category="Java",
                    difficulty="Medium",
                    answer=(
                        "HashMap uses an array of buckets. Key's hashCode() determines the bucket. "
                        "Collisions are handled by chaining (linked list, converts to tree for >8 entries). "
                        "Load factor (default 0.75) triggers resizing. "
                        "Time complexity: O(1) average, O(n) worst case."
                    ),
                    tips=["Draw the bucket structure", "Explain collision handling", "Discuss load factor"],
                ),
                InterviewQuestion(
                    question="What are the SOLID principles?",
                    category="Java",
                    difficulty="Medium",
                    answer=(
                        "S: Single Responsibility - one class, one job. "
                        "O: Open/Closed - open for extension, closed for modification. "
                        "L: Liskov Substitution - subtypes must be substitutable. "
                        "I: Interface Segregation - many specific interfaces over general. "
                        "D: Dependency Inversion - depend on abstractions, not concretions."
                    ),
                    tips=["Give a code example for each", "Explain real project usage", "Mention design patterns"],
                ),
            ],
            "technical_dsa": [
                InterviewQuestion(
                    question="Explain the difference between BFS and DFS.",
                    category="Data Structures",
                    difficulty="Easy",
                    answer=(
                        "BFS (Breadth-First Search) explores level by level using a queue. "
                        "DFS (Depth-First Search) explores as deep as possible using a stack/recursion. "
                        "BFS finds shortest path in unweighted graphs. DFS uses less memory. "
                        "BFS: O(V+E) time, O(V) space. DFS: O(V+E) time, O(V) space."
                    ),
                    tips=["Draw the traversal order", "Mention applications", "Discuss time/space complexity"],
                ),
                InterviewQuestion(
                    question="How does a Hash Table handle collisions?",
                    category="Data Structures",
                    difficulty="Medium",
                    answer=(
                        "Two main approaches: 1) Chaining - each bucket contains a linked list. "
                        "2) Open Addressing - linear probing, quadratic probing, or double hashing. "
                        "Chaining is simpler; open addressing has better cache performance. "
                        "Load factor management is crucial for performance."
                    ),
                    tips=["Compare approaches", "Discuss load factor", "Mention real implementations"],
                ),
                InterviewQuestion(
                    question="Explain the time complexity of common sorting algorithms.",
                    category="Data Structures",
                    difficulty="Medium",
                    answer=(
                        "Bubble Sort: O(n²), Selection Sort: O(n²), Insertion Sort: O(n²). "
                        "Merge Sort: O(n log n), Quick Sort: O(n log n) avg, O(n²) worst. "
                        "Heap Sort: O(n log n), Tim Sort: O(n log n). "
                        "Space: Merge O(n), Quick O(log n), Heap O(1)."
                    ),
                    tips=["Create a comparison table", "Discuss best/worst cases", "Mention when to use each"],
                ),
            ],
            "technical_system_design": [
                InterviewQuestion(
                    question="Design a URL shortener like bit.ly.",
                    category="System Design",
                    difficulty="Medium",
                    answer=(
                        "Components: 1) API Gateway for request handling. "
                        "2) Hash/encode function for URL shortening (base62 or MD5). "
                        "3) Database (NoSQL like DynamoDB for key-value pairs). "
                        "4) Cache (Redis) for frequent lookups. "
                        "5) Analytics service for click tracking. "
                        "Consider: custom aliases, expiration, rate limiting."
                    ),
                    tips=["Start with requirements", "Draw architecture diagram", "Discuss scalability"],
                ),
                InterviewQuestion(
                    question="Design a chat application like WhatsApp.",
                    category="System Design",
                    difficulty="Hard",
                    answer=(
                        "1) WebSocket connections for real-time messaging. "
                        "2) Message queue (Kafka/RabbitMQ) for message routing. "
                        "3) User service for authentication and contacts. "
                        "4) Message storage (Cassandra for write-heavy workload). "
                        "5) Push notifications via FCM/APNs. "
                        "6) End-to-end encryption. 7) Media storage (S3)."
                    ),
                    tips=["Discuss protocol choices", "Handle offline messages", "Scale considerations"],
                ),
            ],
            "aptitude_quantitative": [
                InterviewQuestion(
                    question="If a train travels 360 km in 4 hours, what is its speed? If it needs to cover 540 km, how long will it take?",
                    category="Quantitative Aptitude",
                    difficulty="Easy",
                    answer=(
                        "Speed = Distance/Time = 360/4 = 90 km/h. "
                        "Time = Distance/Speed = 540/90 = 6 hours. "
                        "Key concept: Speed = Distance/Time, Time = Distance/Speed, "
                        "Distance = Speed x Time."
                    ),
                    tips=["Write formulas clearly", "Show step-by-step", "Double-check units"],
                ),
                InterviewQuestion(
                    question="A is twice as efficient as B. Together they can complete a work in 12 days. How long will A take alone?",
                    category="Quantitative Aptitude",
                    difficulty="Medium",
                    answer=(
                        "Let B's work per day = x, then A's = 2x. "
                        "Together: 2x + x = 1/12. 3x = 1/12. x = 1/36. "
                        "A's rate = 2/36 = 1/18. A alone = 18 days."
                    ),
                    tips=["Use work rate approach", "Define variables clearly", "Verify the answer"],
                ),
            ],
            "aptitude_logical": [
                InterviewQuestion(
                    question="What comes next: 2, 6, 12, 20, 30, ?",
                    category="Logical Reasoning",
                    difficulty="Easy",
                    answer=(
                        "Pattern: n(n+1) where n = 1,2,3,4,5,6... "
                        "1*2=2, 2*3=6, 3*4=12, 4*5=20, 5*6=30, 6*7=42. "
                        "Answer: 42"
                    ),
                    tips=["Find the pattern", "Write as formula", "Verify with given numbers"],
                ),
                InterviewQuestion(
                    question="If all roses are flowers and some flowers fade quickly, can we conclude all roses fade quickly?",
                    category="Logical Reasoning",
                    difficulty="Medium",
                    answer=(
                        "No, we cannot conclude that. This is the fallacy of the undistributed middle. "
                        "The premise says 'some flowers' fade quickly, not all. "
                        "Roses are a subset of flowers, so roses might or might not be "
                        "among the flowers that fade quickly."
                    ),
                    tips=["Use Venn diagrams", "Identify logical structure", "Find counterexample"],
                ),
            ],
            "hr_behavioral": [
                InterviewQuestion(
                    question="Tell me about yourself.",
                    category="HR",
                    difficulty="Easy",
                    answer=(
                        "Use the Present-Past-Future framework: "
                        "Present: Current role/education and key strengths. "
                        "Past: Relevant experience, achievements, projects. "
                        "Future: Career goals and why this role fits. "
                        "Keep it under 2 minutes. Focus on relevance to the position."
                    ),
                    tips=["Keep it concise (2 min)", "Focus on achievements", "Relate to the job"],
                ),
                InterviewQuestion(
                    question="Why should we hire you?",
                    category="HR",
                    difficulty="Easy",
                    answer=(
                        "Structure: 1) Understand the role requirements. "
                        "2) Map your skills to those requirements. "
                        "3) Provide specific examples of relevant achievements. "
                        "4) Show enthusiasm for the company/role. "
                        "5) Mention what unique value you bring."
                    ),
                    tips=["Research the company", "Be specific with examples", "Show genuine interest"],
                ),
                InterviewQuestion(
                    question="Describe a challenging project and how you handled it.",
                    category="HR",
                    difficulty="Medium",
                    answer=(
                        "Use STAR method: "
                        "Situation: Set the context. "
                        "Task: Describe your responsibility. "
                        "Action: Explain what you did specifically. "
                        "Result: Share the measurable outcome. "
                        "Focus on your problem-solving approach and what you learned."
                    ),
                    tips=["Use STAR method", "Quantify results", "Show learning/growth"],
                ),
                InterviewQuestion(
                    question="Where do you see yourself in 5 years?",
                    category="HR",
                    difficulty="Easy",
                    answer=(
                        "Show ambition aligned with the company's growth path. "
                        "Example: 'In 5 years, I see myself as a senior engineer/tech lead, "
                        "having contributed to major projects, mentored junior developers, "
                        "and gained expertise in [relevant technology]. "
                        "I want to grow with [company] and take on increasing responsibility.'"
                    ),
                    tips=["Align with company growth", "Show ambition", "Be realistic"],
                ),
                InterviewQuestion(
                    question="What is your greatest weakness?",
                    category="HR",
                    difficulty="Medium",
                    answer=(
                        "Choose a real but non-critical weakness. "
                        "Example: 'I tend to over-detail in documentation, which can slow me down. "
                        "I've been working on balancing thoroughness with efficiency by setting "
                        "time limits for documentation tasks.' "
                        "Show self-awareness and active improvement."
                    ),
                    tips=["Be genuine", "Show improvement", "Don't say perfectionism"],
                ),
            ],
        }

    def get_all_categories(self) -> List[str]:
        return list(self.questions_db.keys())

    def get_questions_by_category(
        self, category: str, difficulty: str = None, count: int = 5
    ) -> List[InterviewQuestion]:
        questions = self.questions_db.get(category, [])
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        if count and len(questions) > count:
            questions = random.sample(questions, count)
        return questions

    def get_mixed_quiz(
        self, categories: List[str] = None, count: int = 10
    ) -> List[InterviewQuestion]:
        if not categories:
            categories = list(self.questions_db.keys())

        all_questions = []
        for cat in categories:
            all_questions.extend(self.questions_db.get(cat, []))

        if len(all_questions) > count:
            return random.sample(all_questions, count)
        return all_questions

    def get_difficulty_distribution(
        self, category: str = None
    ) -> Dict[str, int]:
        dist = {"Easy": 0, "Medium": 0, "Hard": 0}
        categories = [category] if category else self.questions_db.keys()
        for cat in categories:
            for q in self.questions_db.get(cat, []):
                dist[q.difficulty] = dist.get(q.difficulty, 0) + 1
        return dist

    def format_question(self, q: InterviewQuestion, index: int) -> str:
        return (
            f"Q{index}. [{q.difficulty}] {q.question}\n"
            f"   Category: {q.category}\n"
            f"   Expected Duration: {q.expected_duration}"
        )

    def format_answer(self, q: InterviewQuestion) -> str:
        tips_str = "\n".join(f"   - {t}" for t in q.tips)
        return (
            f"Answer:\n{q.answer}\n\n"
            f"Tips for answering:\n{tips_str}"
        )

    def get_interview_tips(self, role: str = "software_engineer") -> List[str]:
        tips = {
            "software_engineer": [
                "Practice coding problems daily on LeetCode/HackerRank",
                "Study data structures and algorithms thoroughly",
                "Prepare 3-5 projects you can explain in detail",
                "Practice system design basics (URL shortener, chat app)",
                "Review OOP concepts and design patterns",
                "Know your resume - every project, every skill",
                "Prepare questions to ask the interviewer",
                "Practice coding on a whiteboard/notepad",
                "Review the company's tech stack and products",
                "Get good sleep the night before",
            ],
            "data_scientist": [
                "Review statistics and probability fundamentals",
                "Practice ML model selection and evaluation metrics",
                "Prepare case studies from past projects",
                "Know SQL joins, aggregations, window functions",
                "Practice explaining complex models simply",
                "Review Python/R data manipulation libraries",
                "Study A/B testing methodology",
                "Prepare portfolio of data projects",
            ],
            "general": [
                "Research the company thoroughly",
                "Prepare STAR-format behavioral answers",
                "Dress professionally (business casual minimum)",
                "Arrive 10-15 minutes early",
                "Bring multiple copies of your resume",
                "Prepare thoughtful questions for the interviewer",
                "Send a thank-you email after the interview",
                "Follow up if you don't hear back in a week",
            ],
        }
        return tips.get(role, tips["general"])

    def get_question_count(self) -> Dict[str, int]:
        counts = {}
        for cat, questions in self.questions_db.items():
            counts[cat] = len(questions)
        return counts
