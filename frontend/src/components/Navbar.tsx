import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuBookIcon from '@mui/icons-material/MenuBook';

const Navbar: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <MenuBookIcon sx={{ mr: 1 }} />
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            DocuEater
          </Typography>
        </Box>
        
        <Button
          color="inherit"
          component={RouterLink}
          to="/"
          sx={{ mx: 1 }}
        >
          Home
        </Button>
        
        <Button
          color="inherit"
          component={RouterLink}
          to="/new-crawl"
          sx={{ mx: 1 }}
        >
          New Crawl
        </Button>
        
        <Button
          color="inherit"
          component={RouterLink}
          to="/tasks"
          sx={{ mx: 1 }}
        >
          Tasks
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 