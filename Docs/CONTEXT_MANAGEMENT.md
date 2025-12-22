# Context Management & Summarization Strategy

## 📋 Overview

This document explains how the interview system manages conversation context to prevent token overflow when conducting interviews with many questions.

## ⚠️ The Problem

When generating interview questions dynamically, the system sends the entire interview history to the LLM (Gemini) as context. This causes issues:

- **Token Overflow**: With 20+ questions, the prompt can exceed Gemini's context window (~32K tokens)
- **Performance Degradation**: Longer prompts = slower responses and higher costs
- **Quality Issues**: Too much context can confuse the LLM

## ✅ The Solution: Summarization Strategy

We implement a **hybrid approach** that balances context retention with token efficiency:

### Strategy

1. **Recent Questions** (last 5 by default): Full details including:
   - Complete question text
   - Complete answer (truncated to 150 chars)
   - Evaluation scores
   - Strengths and weaknesses

2. **Older Questions**: Aggregated summary including:
   - Topics covered
   - Average performance score
   - Key strengths identified
   - Areas needing improvement

### Configuration

In `agent/config.py`:

```python
RECENT_HISTORY_FULL_DETAIL = 5  # Number of recent questions to keep in full detail
MAX_RESPONSE_CHARS_IN_SUMMARY = 150  # Max chars for answer text
```

### Token Savings

Example with 20 questions:

| Approach | Estimated Tokens | Status |
|----------|------------------|--------|
| **No Summarization** | ~12,000 tokens | ❌ Risk of overflow |
| **With Summarization** | ~3,500 tokens | ✅ Safe & efficient |

**Savings: ~70% reduction in context tokens**

## 🔧 Implementation Details

### Helper Function

`_format_history_with_summarization()` in `agent/llm_helpers.py`:

```python
def _format_history_with_summarization(
    interview_history: List[Dict[str, Any]],
    recent_count: int = RECENT_HISTORY_FULL_DETAIL,
) -> List[str]:
    """
    Returns formatted history with:
    - Older questions: Aggregated summary
    - Recent questions: Full details
    """
```

### Usage

The function is automatically used in:

1. **`call_llm_generate_question()`**: Uses default (5 recent questions)
2. **`call_llm_generate_final_report()`**: Uses 10 recent questions for comprehensive final report

## 📊 Example Output Format

### For Older Questions (Summarized)

```
📚 Earlier Questions Summary (15 questions):
============================================================
  Topics Covered: React Hooks, State Management, API Design, Database Optimization, System Architecture
  Average Score: 7.2/10
  Key Strengths: Strong understanding of async patterns; Good problem-solving approach
  Areas to Improve: Needs more depth in database indexing; System security best practices
============================================================
```

### For Recent Questions (Full Detail)

```
🔍 Recent Questions (last 5 - Full Detail):

--- Turn 16 ---
  Q: Explain how you would implement caching in a microservices architecture
  Topic: System Design
  Difficulty: Hard
  A: I would implement distributed caching using Redis at multiple levels. First, I'd add cache-aside pattern for database queries...
  Score: 8/10, Relevance: Relevant
  ✅ Strengths: Mentioned distributed systems, Considered scalability
  ⚠️ To Improve: Could expand on cache invalidation strategies
```

## 🎯 Benefits

1. **Scalability**: Support interviews with 30+ questions without context overflow
2. **Performance**: Faster LLM responses with shorter prompts
3. **Quality**: LLM receives relevant context without information overload
4. **Cost Efficiency**: Reduced token usage = lower API costs

## 🔄 Tuning Recommendations

Adjust `RECENT_HISTORY_FULL_DETAIL` based on your needs:

- **5 questions** (default): Good balance for most interviews
- **3 questions**: More aggressive summarization for very long interviews (30+)
- **10 questions**: Less summarization if you have shorter interviews (5-15 questions)

## 📝 Future Enhancements

Potential improvements:

1. **Adaptive Summarization**: Automatically adjust based on interview length
2. **Semantic Clustering**: Group similar topics in older questions
3. **LLM-Powered Summarization**: Use LLM to generate natural language summaries of older sections
4. **Persistent Summaries**: Cache summaries in database to avoid recalculation

## 🧪 Testing

To verify summarization is working:

1. Start an interview with `num_questions=20`
2. Check backend logs for prompt lengths
3. Compare token usage before/after implementation

Example log output:
```
Sending question generation prompt (15420 chars) to LLM...  # Before
Sending question generation prompt (4680 chars) to LLM...   # After ✅
```

## 📚 Related Files

- `agent/config.py`: Configuration constants
- `agent/llm_helpers.py`: Implementation of summarization logic
- `agent/nodes.py`: Nodes that call LLM helpers
- `agent/models.py`: InterviewState model that stores history

---

**Last Updated**: 2025-12-23
**Author**: AI Interview System
