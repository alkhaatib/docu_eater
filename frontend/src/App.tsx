import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import NewCrawlPage from './pages/NewCrawlPage';
import TasksPage from './pages/TasksPage';
import TaskDetailPage from './pages/TaskDetailPage';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <Box component="main" sx={{ flexGrow: 1, py: 3 }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/new-crawl" element={<NewCrawlPage />} />
              <Route path="/tasks" element={<TasksPage />} />
              <Route path="/task/:taskId" element={<TaskDetailPage />} />
              {/* Redirect any unknown paths to homepage */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Box>
          <Box component="footer" sx={{ py: 3, textAlign: 'center', mt: 'auto', bgcolor: 'background.paper' }}>
            DocuEater &copy; {new Date().getFullYear()}
          </Box>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
