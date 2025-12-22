"""
Simple test to demonstrate summarization without dependencies
Run: python test_summarization_simple.py
"""

def create_mock_turn(i, topic):
    """Create a mock interview turn"""
    return {
        "question": {
            "text": f"Q{i+1}: Detailed question about {topic}" + " (additional context here)" * 5,
            "topic": topic,
            "difficulty": ["Easy", "Medium", "Hard"][i % 3],
        },
        "response": f"Candidate's detailed answer to question {i+1}. " * 15,
        "evaluation": {
            "score": 6 + (i % 5),
            "relevance_judgment": "Relevant",
            "strengths": [f"Good grasp of {topic}", "Clear explanation"],
            "areas_for_improvement": ["More examples needed", "Consider edge cases"]
        }
    }


def format_old_way(history):
    """Old method - all questions in full detail"""
    lines = [f"Previous {len(history)} questions:"]
    for i, turn in enumerate(history):
        lines.append(f"\nTurn {i+1}:")
        lines.append(f"  Q: {turn['question']['text']}")
        lines.append(f"  A: {turn['response'][:200]}...")
        lines.append(f"  Score: {turn['evaluation']['score']}/10")
    return lines


def format_new_way(history, recent_count=5):
    """NEW method - with summarization"""
    lines = []
    total = len(history)
    
    # Split into older and recent
    older = history[:-recent_count] if total > recent_count else []
    recent = history[-recent_count:] if total >= recent_count else history
    
    # Summarize older questions
    if older:
        lines.append(f"\n📚 Earlier Questions Summary ({len(older)} questions):")
        lines.append("=" * 60)
        
        topics = list(set(t['question']['topic'] for t in older))
        avg_score = sum(t['evaluation']['score'] for t in older) / len(older)
        
        lines.append(f"  Topics: {', '.join(topics[:8])}")
        lines.append(f"  Avg Score: {avg_score:.1f}/10")
        lines.append("=" * 60)
    
    # Recent questions - full detail
    if recent:
        lines.append(f"\n🔍 Recent Questions (last {len(recent)}):")
        start_idx = len(older)
        
        for i, turn in enumerate(recent):
            lines.append(f"\n--- Turn {start_idx + i + 1} ---")
            lines.append(f"  Q: {turn['question']['text']}")
            lines.append(f"  A: {turn['response'][:150]}...")
            lines.append(f"  Score: {turn['evaluation']['score']}/10")
    
    return lines


def estimate_tokens(lines):
    """Rough token estimate: 1 token ≈ 4 chars"""
    return sum(len(line) for line in lines) // 4


def run_demo():
    """Run demonstration"""
    
    print("\n" + "=" * 80)
    print("CONTEXT SUMMARIZATION DEMO")
    print("=" * 80)
    
    topics = ["React", "State Mgmt", "APIs", "Database", "System Design", 
              "Security", "Performance", "Testing", "DevOps", "Architecture"]
    
    for num_questions in [5, 10, 20, 30]:
        print(f"\n{'─' * 80}")
        print(f"📝 Interview with {num_questions} questions")
        print(f"{'─' * 80}")
        
        # Create mock history
        history = [create_mock_turn(i, topics[i % len(topics)]) for i in range(num_questions)]
        
        # Compare formats
        old = format_old_way(history)
        new = format_new_way(history, recent_count=5)
        
        old_tokens = estimate_tokens(old)
        new_tokens = estimate_tokens(new)
        reduction = ((old_tokens - new_tokens) / old_tokens * 100) if old_tokens > 0 else 0
        
        print(f"\n  WITHOUT Summarization:")
        print(f"    Lines: {len(old)}")
        print(f"    Tokens: ~{old_tokens:,}")
        
        print(f"\n  WITH Summarization:")
        print(f"    Lines: {len(new)}")
        print(f"    Tokens: ~{new_tokens:,}")
        print(f"    Recent (full): {min(num_questions, 5)}")
        print(f"    Older (summary): {max(0, num_questions - 5)}")
        
        print(f"\n  📊 SAVINGS:")
        print(f"    Token reduction: {old_tokens - new_tokens:,} ({reduction:.1f}%)")
        
        status = "✅ SAFE" if new_tokens < 8000 else "⚠️ CAUTION" if new_tokens < 12000 else "❌ RISK"
        print(f"    Status: {status}")
    
    print("\n" + "=" * 80)
    print("SAMPLE OUTPUT - 20 Questions with Summarization")
    print("=" * 80)
    
    # Show actual output for 20 questions
    history = [create_mock_turn(i, topics[i % len(topics)]) for i in range(20)]
    formatted = format_new_way(history, recent_count=5)
    
    for line in formatted[:25]:
        print(line)
    print("...")
    
    print("\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\nKEY TAKEAWAY:")
    print("  • With 5 questions: Minimal impact (all in full detail)")
    print("  • With 20 questions: ~70% token reduction")
    print("  • With 30 questions: ~80% token reduction")
    print("\nThe system automatically applies this when generating questions!")
    print()


if __name__ == "__main__":
    run_demo()
