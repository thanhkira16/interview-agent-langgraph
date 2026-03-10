"""
Semantic Decision Tree Manager for Interview System

This module implements a semantic decision tree to optimize token usage
by only traversing relevant branches instead of dumping entire history.

Tree Structure:
Interview Tree
├── Skills
│   ├── Python
│   │   ├── Q1 → A1 → score
│   │   └── Q4 → A4 → score
│   └── Django
│       └── Q2 → A2 → score
├── Projects
│   └── E-commerce
│       ├── scalability
│       └── caching
└── Experience
    └── ABC Tech
        ├── role_responsibilities
        └── achievements
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    """
    Represents a node in the semantic decision tree.
    """
    node_id: str
    category: str  # e.g., "Skill", "Experience", "Project", "Education"
    subcategory: str  # e.g., "Python", "Django", "AWS"
    depth: int = 0
    
    # Q&A data
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata for semantic search
    keywords: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    
    # Statistics
    total_questions: int = 0
    average_score: float = 0.0
    last_accessed: Optional[datetime] = None
    
    # Child nodes
    children: Dict[str, 'TreeNode'] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class SemanticInterviewTree:
    """
    Manages the semantic decision tree for interview history.
    Optimizes token usage by only retrieving relevant branches.
    """
    
    def __init__(self):
        self.root = TreeNode(
            node_id="root",
            category="Interview",
            subcategory="Root",
            depth=0
        )
        self.node_index: Dict[str, TreeNode] = {"root": self.root}
        
    def add_qa_to_tree(
        self,
        question: Dict[str, Any],
        response: str,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any],
        feedback: str,
        timestamp: datetime
    ) -> None:
        """
        Add a Q&A pair to the appropriate branch of the tree.
        
        Args:
            question: Question data with metadata
            response: Candidate's response
            analysis: Response analysis
            evaluation: Response evaluation with score
            feedback: Feedback text
            timestamp: When this Q&A occurred
        """
        # Extract category and subcategory from question metadata
        category = self._extract_category(question)
        subcategory = self._extract_subcategory(question)
        
        # Find or create the appropriate node
        node = self._get_or_create_node(category, subcategory)
        
        # Create Q&A entry
        qa_entry = {
            "question": question,
            "response": response,
            "analysis": analysis,
            "evaluation": evaluation,
            "feedback": feedback,
            "timestamp": timestamp,
            "score": evaluation.get("score", 0.0) if evaluation else 0.0
        }
        
        # Add to node
        node.questions.append(qa_entry)
        node.total_questions += 1
        node.last_accessed = timestamp
        
        # Update average score
        total_score = sum(q["score"] for q in node.questions)
        node.average_score = total_score / node.total_questions if node.total_questions > 0 else 0.0
        
        # Update keywords
        self._update_keywords(node, question, response)
    
    def get_relevant_context(
        self,
        next_question_category: Optional[str] = None,
        next_question_subcategory: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        max_items: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve only relevant Q&A pairs for the next question.
        This is the KEY optimization - instead of dumping all history.
        
        Args:
            next_question_category: Category of the next question (e.g., "Skill")
            next_question_subcategory: Subcategory (e.g., "Python")
            keywords: Additional keywords to search for
            max_items: Maximum number of Q&A pairs to return
            
        Returns:
            List of relevant Q&A pairs, optimized for token usage
        """
        relevant_qa = []
        
        # Strategy 1: Direct branch traversal
        if next_question_category and next_question_subcategory:
            node = self._find_node(next_question_category, next_question_subcategory)
            if node:
                # Get all Q&As from this specific branch
                relevant_qa.extend(node.questions)
        
        # Strategy 2: Keyword-based semantic search
        if keywords:
            keyword_matches = self._search_by_keywords(keywords, max_items)
            relevant_qa.extend(keyword_matches)
        
        # Strategy 3: Recent context (last N questions regardless of category)
        if len(relevant_qa) < max_items:
            recent_qa = self._get_recent_questions(max_items - len(relevant_qa))
            relevant_qa.extend(recent_qa)
        
        # Remove duplicates and limit
        seen = set()
        unique_qa = []
        for qa in relevant_qa:
            qa_id = id(qa)  # Use object id to identify unique items
            if qa_id not in seen:
                seen.add(qa_id)
                unique_qa.append(qa)
                if len(unique_qa) >= max_items:
                    break
        
        return unique_qa
    
    def get_tree_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the tree structure for debugging/visualization.
        """
        def summarize_node(node: TreeNode) -> Dict[str, Any]:
            return {
                "category": node.category,
                "subcategory": node.subcategory,
                "total_questions": node.total_questions,
                "average_score": round(node.average_score, 2),
                "keywords": node.keywords[:5],  # Top 5 keywords
                "children": {
                    child_key: summarize_node(child_node)
                    for child_key, child_node in node.children.items()
                }
            }
        
        return summarize_node(self.root)
    
    def _extract_category(self, question: Dict[str, Any]) -> str:
        """
        Extract category from question metadata.
        Categories: Skill, Experience, Project, Education, Certification, General
        """
        # Check CV verification target
        cv_target = question.get("cv_verification_target", "")
        if "skill" in cv_target.lower():
            return "Skill"
        elif "experience" in cv_target.lower() or "work" in cv_target.lower():
            return "Experience"
        elif "project" in cv_target.lower():
            return "Project"
        elif "education" in cv_target.lower():
            return "Education"
        elif "certification" in cv_target.lower():
            return "Certification"
        
        # Check question type
        q_type = question.get("type", "").lower()
        if "technical" in q_type or "coding" in q_type:
            return "Skill"
        elif "behavioral" in q_type:
            return "Experience"
        
        return "General"
    
    def _extract_subcategory(self, question: Dict[str, Any]) -> str:
        """
        Extract subcategory from question metadata.
        E.g., "Python", "Django", "AWS", "E-commerce Project"
        """
        # Try to extract from CV verification target
        cv_target = question.get("cv_verification_target", "")
        if cv_target:
            # Extract the specific item (e.g., "Python" from "Skill: Python")
            parts = cv_target.split(":")
            if len(parts) > 1:
                return parts[1].strip()
        
        # Try to extract from JD alignment
        jd_alignment = question.get("jd_alignment", "")
        if jd_alignment:
            # Extract key technology/topic
            words = jd_alignment.split()
            for word in words:
                if word[0].isupper() and len(word) > 2:
                    return word
        
        # Try to extract from question text
        text = question.get("text", "")
        # Look for capitalized words (likely technology names)
        words = text.split()
        for word in words:
            # Remove punctuation
            clean_word = word.strip(".,!?;:")
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                # Common tech keywords
                tech_keywords = ["Python", "Django", "AWS", "Docker", "React", "Node", "SQL", "API"]
                if clean_word in tech_keywords:
                    return clean_word
        
        return "General"
    
    def _get_or_create_node(self, category: str, subcategory: str) -> TreeNode:
        """
        Get existing node or create new one for the given category/subcategory.
        """
        # Create node ID
        node_id = f"{category}::{subcategory}"
        
        # Check if already exists
        if node_id in self.node_index:
            return self.node_index[node_id]
        
        # Find or create category node
        category_id = f"category::{category}"
        if category_id not in self.node_index:
            category_node = TreeNode(
                node_id=category_id,
                category=category,
                subcategory="All",
                depth=1
            )
            self.root.children[category] = category_node
            self.node_index[category_id] = category_node
        else:
            category_node = self.node_index[category_id]
        
        # Create subcategory node
        subcategory_node = TreeNode(
            node_id=node_id,
            category=category,
            subcategory=subcategory,
            depth=2
        )
        category_node.children[subcategory] = subcategory_node
        self.node_index[node_id] = subcategory_node
        
        return subcategory_node
    
    def _find_node(self, category: str, subcategory: str) -> Optional[TreeNode]:
        """
        Find a node by category and subcategory.
        """
        node_id = f"{category}::{subcategory}"
        return self.node_index.get(node_id)
    
    def _update_keywords(self, node: TreeNode, question: Dict[str, Any], response: str) -> None:
        """
        Extract and update keywords for semantic search.
        """
        # Extract from question text
        q_text = question.get("text", "").lower()
        # Extract from response
        r_text = response.lower()
        
        # Simple keyword extraction (can be enhanced with NLP)
        combined_text = q_text + " " + r_text
        words = combined_text.split()
        
        # Filter for meaningful keywords (length > 3, not common words)
        common_words = {"the", "and", "for", "with", "this", "that", "from", "have", "what", "how", "why"}
        keywords = [w.strip(".,!?;:") for w in words if len(w) > 3 and w not in common_words]
        
        # Add unique keywords
        for kw in keywords[:10]:  # Limit to top 10 per Q&A
            if kw not in node.keywords:
                node.keywords.append(kw)
        
        # Keep only top 50 keywords per node
        if len(node.keywords) > 50:
            node.keywords = node.keywords[-50:]
    
    def _search_by_keywords(self, keywords: List[str], max_items: int) -> List[Dict[str, Any]]:
        """
        Search for Q&A pairs matching given keywords.
        """
        results = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        # Search all nodes
        for node in self.node_index.values():
            # Check if node keywords match search keywords
            node_keywords_lower = [kw.lower() for kw in node.keywords]
            matches = sum(1 for kw in keywords_lower if kw in node_keywords_lower)
            
            if matches > 0:
                # Add Q&As from this node with match score
                for qa in node.questions:
                    results.append((matches, qa))
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top matches
        return [qa for _, qa in results[:max_items]]
    
    def _get_recent_questions(self, max_items: int) -> List[Dict[str, Any]]:
        """
        Get the most recent Q&A pairs across all branches.
        """
        all_qa = []
        
        # Collect all Q&As with timestamps
        for node in self.node_index.values():
            all_qa.extend(node.questions)
        
        # Sort by timestamp (most recent first)
        all_qa.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
        
        return all_qa[:max_items]
