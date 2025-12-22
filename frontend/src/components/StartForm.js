import React, { useState } from 'react';
import { startInterview } from '../api';
import { useInterview } from '../context/InterviewContext';
import {
  Container,
  TextField,
  Typography,
  Box,
  AppBar,
  Toolbar,
  MenuItem,
  FormHelperText,
} from '@mui/material';
import { LoadingButton } from '@mui/lab';

export default function StartForm() {
  // BlackRock Full Stack Java Engineer - Pre-filled for testing
  const [jobRole, setJobRole] = useState('Full Stack Java Engineer');
  const [candidateId, setCandidateId] = useState('TEST_CANDIDATE_001');
  const [industry, setIndustry] = useState('Financial Technology / Investment Management');
  const [jobLevel, setJobLevel] = useState('Mid-level');
  const [employmentType, setEmploymentType] = useState('Full-time');
  const [salaryRange, setSalaryRange] = useState('$120,000 - $148,000');
  const [jobDescription, setJobDescription] = useState('Full Stack Developer for BlackRock Aladdin Engineering team. Responsible for designing and enhancing solutions for Alternatives Investments Business. Key technologies: Java, React, TypeScript, SQL Server. Requirements: 3+ years full stack development, microservices architecture, object-oriented programming, expertise in Java and React. Building scalable applications for investment management workflow, compliance, risk management, and trade processing.');
  const [numQuestions, setNumQuestions] = useState(5);  // Default to 5 questions
  const [loading, setLoading] = useState(false);
  const { updateInterviewData, setSessionId } = useInterview();

  const handleStart = async (e) => {
    e.preventDefault();
    if (!jobRole || !candidateId) {
      alert('Please enter both Job Role and Candidate ID.');
      return;
    }

    setLoading(true);
    try {
      const jobInfo = {
        industry: industry || null,
        job_level: jobLevel || null,
        employment_type: employmentType || null,
        salary_range: salaryRange || null,
        job_description: jobDescription || null,
      };
      const data = await startInterview(jobRole, candidateId, jobInfo, numQuestions);
      setSessionId(data.session_id);
      updateInterviewData(data);
    } catch (error) {
      console.error('Error starting interview:', error);
      alert('Failed to start interview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const jobRoles = [
    "Software Engineer",
    "Full Stack Java Engineer",
    "Product Manager",
    "Data Scientist",
    "Computer Vision Engineer"
  ];

  const jobLevels = [
    "Junior",
    "Mid-level",
    "Senior",
    "Lead",
    "Manager"
  ];

  const employmentTypes = [
    "Full-time",
    "Part-time",
    "Contract",
    "Freelance",
    "Internship"
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Interview Application
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Box component="form" onSubmit={handleStart} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Start New Interview
          </Typography>

          <TextField
            select
            label="Job Role"
            variant="outlined"
            fullWidth
            value={jobRole}
            onChange={(e) => setJobRole(e.target.value)}
            required
            disabled={loading}
          >
            {jobRoles.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Candidate ID"
            variant="outlined"
            fullWidth
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
            required
            disabled={loading}
          />

          <Typography variant="subtitle2" sx={{ mt: 2, mb: -2 }}>
            Job Information (Optional)
          </Typography>

          <TextField
            label="Industry"
            variant="outlined"
            fullWidth
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            disabled={loading}
            placeholder="e.g., Technology, Finance, Healthcare"
          />

          <TextField
            select
            label="Job Level"
            variant="outlined"
            fullWidth
            value={jobLevel}
            onChange={(e) => setJobLevel(e.target.value)}
            disabled={loading}
          >
            <MenuItem value="">None</MenuItem>
            {jobLevels.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Employment Type"
            variant="outlined"
            fullWidth
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            disabled={loading}
          >
            <MenuItem value="">None</MenuItem>
            {employmentTypes.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Salary Range"
            variant="outlined"
            fullWidth
            value={salaryRange}
            onChange={(e) => setSalaryRange(e.target.value)}
            disabled={loading}
            placeholder="e.g., $100k - $150k"
          />

          <TextField
            label="Job Description"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            disabled={loading}
            placeholder="Enter key responsibilities and requirements..."
          />

          <Typography variant="subtitle2" sx={{ mt: 2, mb: -2 }}>
            Interview Settings
          </Typography>

          <TextField
            select
            label="Number of Questions"
            variant="outlined"
            fullWidth
            value={numQuestions}
            onChange={(e) => setNumQuestions(parseInt(e.target.value))}
            disabled={loading}
            helperText="Select how many questions you want in this interview"
          >
            <MenuItem value={3}>3 Questions (Quick)</MenuItem>
            <MenuItem value={5}>5 Questions (Standard)</MenuItem>
            <MenuItem value={10}>10 Questions (Detailed)</MenuItem>
            <MenuItem value={20}>20 Questions (Comprehensive)</MenuItem>
          </TextField>

          <FormHelperText sx={{ mt: -2, mb: 2 }}>
            NB : Candidate ID can be anything. In deployment, this can be generated by the backend and can be used to block re-attempts to an interview
          </FormHelperText>

          <LoadingButton
            variant="contained"
            type="submit"
            size="large"
            loading={loading}
            loadingPosition="start"
          >
            Start Interview
          </LoadingButton>
        </Box>
      </Container>
    </Box>
  );
}