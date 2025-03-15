import React from 'react';
import { Container, Typography, Button, Box, Grid, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import MapIcon from '@mui/icons-material/Map';

const HomePage: React.FC = () => {
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
        <Box sx={{ mt: 4 }}>
          <Button
            component={RouterLink}
            to="/new-crawl"
            variant="contained"
            color="primary"
            size="large"
            sx={{ mx: 1 }}
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
          <Grid item xs={12} md={4}>
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
          <Grid item xs={12} md={4}>
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
          <Grid item xs={12} md={4}>
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
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage; 