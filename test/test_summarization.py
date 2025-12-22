"""
Test script to verify context summarization is working correctly.
This script simulates a long interview and checks token reduction.
"""

from agent.llm_helpers import _format_history_with_summarization
from agent.config import RECENT_HISTORY_FULL_DETAIL
import json


def create_mock_interview_history(num_questions: int):
    """Create mock interview history for testing"""
    history = []
    
    topics = ["React Hooks", "State Management", "API Design", "Database Optimization", 
              "System Architecture", "Security", "Performance", "Testing", "CI/CD", "Microservices"]
    
    for i in range(num_questions):
        turn = {
            "question": {
                "text": f"Question {i+1}: This is a detailed question about {topics[i % len(topics)]}. "
                        f"Please explain your understanding and provide examples from your experience. "
                        f"Consider best practices and potential edge cases in your answer.",
                "topic": topics[i % len(topics)],
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "id": f"q_{i+1}"
            },
            "response": f"This is the candidate's detailed response to question {i+1}. " * 10,  # Long response
            "evaluation": {
                "score": 6 + (i % 5),  # Scores between 6-10
                "relevance_judgment": "Relevant",
                "strengths": [
                    f"Good understanding of {topics[i % len(topics)]}",
                    "Clear explanation with examples"
                ],
                "areas_for_improvement": [
                    "Could provide more specific examples",
                    "Consider edge cases"
                ]
            }
        }
        history.append(turn)
    
    return history


def estimate_token_count(text_list: list) -> int:
    """Rough estimate: 1 token ≈ 4 characters"""
    total_chars = sum(len(str(item)) for item in text_list)
    return total_chars // 4


def format_without_summarization(history):
    """Old method - includes all questions in full detail"""
    summary = []
    summary.append(f"Previous {len(history)} question(s) and answers:")
    for i, turn in enumerate(history):
        summary.append(f"\nTurn {i + 1}:")
        if turn.get('question'):
            summary.append(f"  Q: {turn['question'].get('text', 'N/A')}")
        if turn.get('response'):
            summary.append(f"  A: {turn['response'][:200]}...")
        if turn.get('evaluation'):
            eval_details = turn['evaluation']
            score = eval_details.get('score', 'N/A')
            relevance = eval_details.get('relevance_judgment', 'N/A')
            summary.append(f"  Score: {score}/10, Relevance: {relevance}")
    return summary


def run_comparison_test():
    """Run comparison between old and new methods"""
    
    print("=" * 80)
    print("CONTEXT SUMMARIZATION TEST")
    print("=" * 80)
    print()
    
    test_cases = [5, 10, 20, 30]
    
    for num_questions in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Testing with {num_questions} questions:")
        print(f"{'─' * 80}")
        
        # Create mock history
        history = create_mock_interview_history(num_questions)
        
        # Old method (no summarization)
        old_format = format_without_summarization(history)
        old_tokens = estimate_token_count(old_format)
        
        # New method (with summarization)
        new_format = _format_history_with_summarization(history)
        new_tokens = estimate_token_count(new_format)
        
        # Calculate reduction
        reduction_pct = ((old_tokens - new_tokens) / old_tokens * 100) if old_tokens > 0 else 0
        
        print(f"  WITHOUT Summarization:")
        print(f"    - Total lines: {len(old_format)}")
        print(f"    - Estimated tokens: {old_tokens:,}")
        print()
        print(f"  WITH Summarization:")
        print(f"    - Total lines: {len(new_format)}")
        print(f"    - Estimated tokens: {new_tokens:,}")
        print(f"    - Recent questions (full detail): {min(num_questions, RECENT_HISTORY_FULL_DETAIL)}")
        print(f"    - Older questions (summarized): {max(0, num_questions - RECENT_HISTORY_FULL_DETAIL)}")
        print()
        print(f"  📊 RESULTS:")
        print(f"    - Token reduction: {old_tokens - new_tokens:,} tokens")
        print(f"    - Percentage saved: {reduction_pct:.1f}%")
        print(f"    - Status: {'✅ SAFE' if new_tokens < 8000 else '⚠️ WARNING' if new_tokens < 12000 else '❌ RISKY'}")
        
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print(f"Configuration: RECENT_HISTORY_FULL_DETAIL = {RECENT_HISTORY_FULL_DETAIL}")
    print()


def test_format_structure():
    """Test that the formatted output has correct structure"""
    
    print("\n" + "=" * 80)
    print("STRUCTURE VALIDATION TEST")
    print("=" * 80)
    print()
    
    # Test with 15 questions
    history = create_mock_interview_history(15)
    formatted = _format_history_with_summarization(history)
    
    # Check for expected sections
    text = "\n".join(formatted)
    
    checks = {
        "Has earlier summary section": "📚 Earlier Questions Summary" in text,
        "Has recent detail section": "🔍 Recent Questions" in text,
        "Contains topics": "Topics Covered:" in text,
        "Contains scores": "Score:" in text,
        "Contains strengths": "Strengths:" in text,
        "Contains improvements": "To Improve:" in text,
    }
    
    print("Structure Checks:")
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}: {result}")
    
    # Print sample output
    print("\n" + "─" * 80)
    print("SAMPLE OUTPUT (first 20 lines):")
    print("─" * 80)
    for line in formatted[:20]:
        print(line)
    print("...")
    
    print("\n" + "=" * 80)
    print()


if __name__ == "__main__":
    try:
        # Run tests
        run_comparison_test()
        test_format_structure()
        
        print("\n✅ All tests completed successfully!")
        print("\nTo use in production, the system will automatically apply summarization")
        print("when generating questions and final reports.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
