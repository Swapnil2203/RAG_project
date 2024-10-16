import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box, Paper, CircularProgress } from '@mui/material';

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const handleSubmit = async () => {
    if (!question) {
      setError('Please enter a question.');
      return;
    }
    setError('');
    setLoading(true);
    setResponse('');
    try {
      const result = await axios.get('https://rag-backend-app-bi.azurewebsites.net/query/', {
        params: { question: question },
      });
      if (result.data.response) {
        setResponse(result.data.response);
      } else {
        handleNoRelevantData();
      }
    } catch (err) {
      if (err.response && err.response.status === 404) {
        handleNoRelevantData();
      } else if (err.response && err.response.status === 500) {
        setError('An unexpected server error occurred. Please try again later.');
      } else {
        setError('An error occurred while fetching the response. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNoRelevantData = () => {
    setError(
      'No relevant information found for the provided question. Please try rephrasing the question or ensure the question pertains to the available datasets.'
    );
  };

  const handleClear = () => {
    setQuestion('');
    setResponse('');
    setError('');
  };

  return (
    <Container maxWidth="md" style={{ marginTop: '50px' }}>
      <Paper elevation={3} style={{ padding: '30px' }}>
        <Box my={4}>
          <Typography variant="h4" gutterBottom align="center">
            Retrieval-Augmented Generation (RAG) System
          </Typography>
          <TextField
            label="Enter your question"
            variant="outlined"
            fullWidth
            value={question}
            onChange={handleQuestionChange}
            multiline
            rows={3}
            margin="normal"
            style={{ marginBottom: '20px' }}
          />
          {error && (
            <Typography color="error" variant="body2" style={{ marginBottom: '20px' }}>
              {error}
            </Typography>
          )}
          <Box display="flex" justifyContent="center" style={{ marginBottom: '20px' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={loading}
              size="large"
              style={{ marginRight: '10px' }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Submit'}
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleClear}
              disabled={loading}
              size="large"
            >
              Clear
            </Button>
          </Box>
          {response && (
            <Paper style={{ padding: '20px', backgroundColor: '#f5f5f5' }}>
              <Typography variant="h6" style={{ marginBottom: '10px' }}>
                Response:
              </Typography>
              <Typography variant="body1">{response}</Typography>
            </Paper>
          )}
        </Box>
      </Paper>
    </Container>
  );
}

export default App;
