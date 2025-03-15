import React, { useEffect, useState } from 'react';
import { Container, Typography, Button, Box, Grid, Paper, CircularProgress, Alert } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import MapIcon from '@mui/icons-material/Map';
import ListAltIcon from '@mui/icons-material/ListAlt';
import { ApiService } from '../services/api';

const HomePage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');

  useEffect(() => {
    const checkApiConnection = async () => {
      try {
        const isConnected = await ApiService.testConnection();
        setApiStatus(isConnected ? 'connected' : 'error');
      } catch (error) {
        console.error('API connection error:', error);
        setApiStatus('error');
      }
    };

    checkApiConnection();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box 
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          py: 8
        }}
      >
        <MenuBookIcon color="primary" sx={{ fontSize: 80, mb: 3 }} />
        <Typography variant="h2" gutterBottom>
          Welcome to DocuEater
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Your intelligent documentation crawler and mapper
        </Typography>
        
        {apiStatus === 'loading' && (
          <Box sx={{ mt: 2, mb: 2 }}>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            <Typography variant="body2" component="span">
              Connecting to API...
            </Typography>
          </Box>
        )}
        
        {apiStatus === 'error' && (
          <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
            Cannot connect to the backend API. Please make sure the backend server is running.
          </Alert>
        )}
        
        <Box sx={{ mt: 4 }}>
          <Button
            component={RouterLink}
            to="/new-crawl"
            variant="contained"
            color="primary"
            size="large"
            sx={{ mx: 1 }}
            disabled={apiStatus === 'error'}
          >
            Start New Crawl
          </Button>
          <Button
            component={RouterLink}
            to="/tasks"
            variant="outlined"
            color="primary"
            size="large"
            sx={{ mx: 1 }}
            disabled={apiStatus === 'error'}
          >
            View Tasks
          </Button>
        </Box>
      </Box>

      <Box sx={{ py: 8 }}>
        <Typography variant="h4" align="center" gutterBottom>
          How It Works
        </Typography>
        <Grid container spacing={4} sx={{ mt: 2 }}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <TravelExploreIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  1. Crawl
                </Typography>
                <Typography align="center">
                  Provide a documentation URL and DocuEater will intelligently crawl the pages,
                  following links and gathering content.
                </Typography>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <MapIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  2. Map
                </Typography>
                <Typography align="center">
                  DocuEater analyzes the structure of the documentation and creates
                  a hierarchical map that organizes the content.
                </Typography>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <MenuBookIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  3. Explore
                </Typography>
                <Typography align="center">
                  Navigate through the documentation map to easily find and access
                  the information you need.
                </Typography>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <ListAltIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  4. Track
                </Typography>
                <Typography align="center">
                  Monitor your crawl tasks, check their status, and keep track of all
                  your documentation mapping projects.
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage; 