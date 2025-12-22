import React, { useState, useEffect, useRef } from 'react';
import { useInterview } from '../context/InterviewContext';
import { submitAnswer } from '../api';
import {
  Container,
  TextField,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Paper,
  Grid,
  Avatar,
  IconButton,
  Chip,
  LinearProgress,
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

// Typing Indicator Component
const TypingIndicator = () => (
  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 2 }}>
    <Avatar sx={{ bgcolor: '#1976d2', width: 32, height: 32 }}>
      <SmartToyIcon sx={{ fontSize: 18 }} />
    </Avatar>
    <Box
      sx={{
        bgcolor: '#e3f2fd',
        borderRadius: '18px',
        px: 2,
        py: 1,
        display: 'flex',
        gap: 0.5,
        alignItems: 'center',
      }}
    >
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: '#1976d2',
          animation: 'bounce 1.4s infinite ease-in-out',
          animationDelay: '0s',
          '@keyframes bounce': {
            '0%, 80%, 100%': { transform: 'scale(0)' },
            '40%': { transform: 'scale(1)' },
          },
        }}
      />
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: '#1976d2',
          animation: 'bounce 1.4s infinite ease-in-out',
          animationDelay: '0.2s',
          '@keyframes bounce': {
            '0%, 80%, 100%': { transform: 'scale(0)' },
            '40%': { transform: 'scale(1)' },
          },
        }}
      />
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: '#1976d2',
          animation: 'bounce 1.4s infinite ease-in-out',
          animationDelay: '0.4s',
          '@keyframes bounce': {
            '0%, 80%, 100%': { transform: 'scale(0)' },
            '40%': { transform: 'scale(1)' },
          },
        }}
      />
    </Box>
  </Box>
);

export default function Interview() {
  const { sessionId, interviewData, updateInterviewData } = useInterview();
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [interviewData, loading]);

  useEffect(() => {
    // Focus input when not loading
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  // Debug logging
  useEffect(() => {
    console.log('Interview Data:', interviewData);
  }, [interviewData]);

  if (!sessionId) {
    return (
      <Box sx={{ flexGrow: 1, height: '100vh', bgcolor: '#f0f2f5' }}>
        <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
          <Toolbar>
            <SmartToyIcon sx={{ mr: 2 }} />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              AI Interview Assistant
            </Typography>
          </Toolbar>
        </AppBar>
        <Container sx={{ mt: 8, textAlign: 'center' }}>
          <SmartToyIcon sx={{ fontSize: 80, color: '#1976d2', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            No active interview session
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Please start a new interview to begin the conversation.
          </Typography>
        </Container>
      </Box>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) {
      return;
    }

    setLoading(true);
    try {
      const response = await submitAnswer(sessionId, answer);
      updateInterviewData(response);
      setAnswer('');
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const interviewHistory = interviewData?.interview_history_summary || [];
  const hasQuestion = interviewData && interviewData.current_question;
  const isInterviewOver = interviewData && ['completed', 'terminated'].includes(interviewData.status);
  const progress = interviewData?.total_questions_planned
    ? ((interviewHistory.length / interviewData.total_questions_planned) * 100)
    : 0;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#f0f2f5' }}>
      {/* Header */}
      <AppBar position="static" elevation={1} sx={{ bgcolor: '#fff', color: '#000' }}>
        <Toolbar>
          <Avatar sx={{ bgcolor: '#1976d2', mr: 2 }}>
            <SmartToyIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              AI Interviewer
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {isInterviewOver ? 'Interview Completed' : 'Active Session'}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Chip
              label={`Question ${interviewHistory.length + (hasQuestion && !isInterviewOver ? 1 : 0)} / ${interviewData?.total_questions_planned || '?'}`}
              color="primary"
              size="small"
              sx={{ mb: 0.5 }}
            />
            {isInterviewOver && (
              <Chip
                label={`Score: ${interviewData.overall_score?.toFixed(1)}/10`}
                color="success"
                size="small"
              />
            )}
          </Box>
        </Toolbar>
        {!isInterviewOver && (
          <LinearProgress variant="determinate" value={progress} sx={{ height: 3 }} />
        )}
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="md" sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 2, overflow: 'hidden' }}>
        {/* Messages */}
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            overflow: 'auto',
            mb: 2,
            bgcolor: 'transparent',
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              bgcolor: 'transparent',
            },
            '&::-webkit-scrollbar-thumb': {
              bgcolor: '#bbb',
              borderRadius: '4px',
            },
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pb: 2 }}>
            {/* Welcome Message */}
            {interviewHistory.length === 0 && !hasQuestion && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Avatar sx={{ bgcolor: '#1976d2', width: 64, height: 64, mx: 'auto', mb: 2 }}>
                  <SmartToyIcon sx={{ fontSize: 40 }} />
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  Welcome to your AI Interview
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  I'll ask you questions one at a time. Take your time to answer thoughtfully.
                </Typography>
              </Box>
            )}

            {/* Previous Q&A */}
            {interviewHistory.map((turn, idx) => (
              <Box key={idx}>
                {/* Question Bubble */}
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#1976d2', width: 36, height: 36 }}>
                    <SmartToyIcon sx={{ fontSize: 20 }} />
                  </Avatar>
                  <Box sx={{ flex: 1, maxWidth: '75%' }}>
                    <Typography variant="caption" sx={{ color: '#666', ml: 1, mb: 0.5, display: 'block' }}>
                      AI Interviewer
                    </Typography>
                    <Paper
                      elevation={1}
                      sx={{
                        bgcolor: '#e3f2fd',
                        p: 2,
                        borderRadius: '18px',
                        borderTopLeftRadius: '4px',
                      }}
                    >
                      <Typography variant="body1">
                        {turn.question?.text || 'N/A'}
                      </Typography>
                    </Paper>
                  </Box>
                </Box>

                {/* Answer Bubble */}
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', mb: 3 }}>
                  <Box sx={{ flex: 1, maxWidth: '75%', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Typography variant="caption" sx={{ color: '#666', mr: 1, mb: 0.5 }}>
                      You
                    </Typography>
                    <Paper
                      elevation={1}
                      sx={{
                        bgcolor: '#1976d2',
                        color: '#fff',
                        p: 2,
                        borderRadius: '18px',
                        borderTopRightRadius: '4px',
                      }}
                    >
                      <Typography variant="body1">
                        {turn.response || 'N/A'}
                      </Typography>
                      {turn.evaluation && (
                        <Chip
                          label={`Score: ${turn.evaluation.score}/10`}
                          size="small"
                          sx={{
                            mt: 1,
                            bgcolor: 'rgba(255,255,255,0.2)',
                            color: '#fff',
                            fontWeight: 'bold',
                          }}
                        />
                      )}
                    </Paper>
                  </Box>
                  <Avatar sx={{ bgcolor: '#7b1fa2', width: 36, height: 36 }}>
                    <PersonIcon sx={{ fontSize: 20 }} />
                  </Avatar>
                </Box>
              </Box>
            ))}

            {/* Current Question */}
            {hasQuestion && !isInterviewOver && (
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Avatar sx={{ bgcolor: '#1976d2', width: 36, height: 36 }}>
                  <SmartToyIcon sx={{ fontSize: 20 }} />
                </Avatar>
                <Box sx={{ flex: 1, maxWidth: '75%' }}>
                  <Typography variant="caption" sx={{ color: '#666', ml: 1, mb: 0.5, display: 'block' }}>
                    AI Interviewer
                  </Typography>
                  <Paper
                    elevation={2}
                    sx={{
                      bgcolor: '#e3f2fd',
                      p: 2,
                      borderRadius: '18px',
                      borderTopLeftRadius: '4px',
                      border: '2px solid #1976d2',
                    }}
                  >
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {interviewData.current_question.text}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            )}

            {/* Typing Indicator */}
            {loading && <TypingIndicator />}

            {/* Interview Complete Message */}
            {isInterviewOver && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Box
                  sx={{
                    bgcolor: '#e8f5e9',
                    borderRadius: '18px',
                    p: 3,
                    maxWidth: '400px',
                    mx: 'auto',
                    border: '2px solid #4caf50',
                  }}
                >
                  <Typography variant="h5" sx={{ color: '#2e7d32', fontWeight: 'bold', mb: 1 }}>
                    🎉 Interview Completed!
                  </Typography>
                  <Typography variant="h4" sx={{ color: '#1b5e20', fontWeight: 'bold', my: 2 }}>
                    {interviewData.overall_score?.toFixed(1)}/10
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Thank you for your time! Your responses have been recorded and evaluated.
                  </Typography>
                  {interviewData?.feedback && (
                    <Paper sx={{ mt: 2, p: 2, bgcolor: '#fff' }}>
                      <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#666' }}>
                        Final Feedback:
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {interviewData.feedback}
                      </Typography>
                    </Paper>
                  )}
                </Box>
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Box>
        </Paper>

        {/* Input Area */}
        {hasQuestion && !isInterviewOver && (
          <Paper
            component="form"
            onSubmit={handleSubmit}
            elevation={2}
            sx={{
              display: 'flex',
              alignItems: 'flex-end',
              p: 1.5,
              gap: 1,
              borderRadius: '24px',
              bgcolor: '#fff',
            }}
          >
            <TextField
              inputRef={inputRef}
              fullWidth
              multiline
              maxRows={4}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              placeholder="Type your answer..."
              variant="standard"
              InputProps={{
                disableUnderline: true,
                sx: { fontSize: '1rem', px: 1 },
              }}
            />
            <IconButton
              type="submit"
              disabled={!answer.trim() || loading}
              sx={{
                bgcolor: answer.trim() && !loading ? '#1976d2' : '#e0e0e0',
                color: '#fff',
                '&:hover': {
                  bgcolor: answer.trim() && !loading ? '#1565c0' : '#e0e0e0',
                },
                '&:disabled': {
                  bgcolor: '#e0e0e0',
                  color: '#9e9e9e',
                },
                width: 48,
                height: 48,
              }}
            >
              <SendIcon />
            </IconButton>
          </Paper>
        )}

        {/* Feedback Box */}
        {interviewData?.feedback && !isInterviewOver && (
          <Paper
            elevation={1}
            sx={{
              mt: 2,
              p: 2,
              bgcolor: '#fff3e0',
              borderRadius: '12px',
              border: '1px solid #ff9800',
            }}
          >
            <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#e65100' }}>
              💬 Latest Feedback:
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5, color: '#5d4037' }}>
              {interviewData.feedback}
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
}
